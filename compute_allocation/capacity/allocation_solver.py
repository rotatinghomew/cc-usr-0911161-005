from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from compute_allocation.requests.application import DomainRecord, bounded, finite_number, normalized_text


@dataclass(frozen=True)
class PortfolioChoice:
    application_ids: tuple[str, ...]
    value: float
    capacity: float
    concentration: float
    feasible: bool


def application_profile(record: DomainRecord) -> dict[str, float]:
    proof = bounded(finite_number(record.payload.get("public_value_proof", 0.0)))
    gap = bounded(finite_number(record.payload.get("resource_gap", 0.0)))
    partner = bounded(finite_number(record.payload.get("partner_assurance", 0.0)))
    effort = max(0.0, finite_number(record.payload.get("localization_effort", 0.0)))
    capacity = max(0.0, finite_number(record.payload.get("delivery_capacity", 0.0)))
    revenue = max(0.0, finite_number(record.payload.get("requested_units", 0.0)))
    currency = bounded(finite_number(record.payload.get("continuity_risk", 0.0)))
    policy = bounded(finite_number(record.payload.get("policy_risk", 0.0)))
    support = max(0.0, finite_number(record.payload.get("operations_cost", 0.0)))
    dependencies = max(0.0, finite_number(record.payload.get("dependency_count", 0.0)))
    risk = bounded(currency * .3 + policy * .4 + gap * .2 + bounded(dependencies / 10.0) * .1)
    value = revenue * (proof * .35 + partner * .25 + (1.0 - risk) * .40) - effort - support
    return {"value": value, "capacity": capacity, "risk": risk, "readiness": bounded(proof * .4 + partner * .3 + (1.0 - gap) * .3)}


def evaluate_choice(records: Iterable[DomainRecord], capacity_limit: float, concentration_limit: float) -> PortfolioChoice:
    rows = list(records)
    profiles = [application_profile(row) for row in rows]
    capacity = sum(item["capacity"] for item in profiles)
    value = sum(item["value"] for item in profiles)
    countries = [normalized_text(row.payload.get("use_case", "unknown")) for row in rows]
    concentration = max((countries.count(country) / len(countries) for country in set(countries)), default=0.0)
    feasible = capacity <= capacity_limit and concentration <= concentration_limit and all(item["readiness"] >= .35 for item in profiles)
    return PortfolioChoice(tuple(row.record_id for row in rows), value, capacity, concentration, feasible)


def optimize(records: Iterable[DomainRecord], capacity_limit: float, concentration_limit: float = .6) -> PortfolioChoice:
    """在既有约束下选出价值最大的组合，结果与全量穷举严格一致。

    约束与 evaluate_choice 相同：组合总容量不超过 capacity_limit、单一用途占比不超过
    concentration_limit、组合内每条申请 readiness 不低于 .35。原实现枚举全部 2^n 个子集，
    候选扩到十几件时耗时随规模指数膨胀，会议窗口内拿不到结果。这里改用分支定界：
    只剪掉「不可能可行」或「不可能更优」的分支，搜索空间与穷举等价，最优值与穷举相同，
    价值并列时也与穷举一样先取更小组合、再取原始顺序字典序靠前者。每次调用都基于当前
    输入完整重算，不跨批缓存任何评估结果，因此分配结论始终与当次输入批次一致。
    """
    rows = list(records)
    empty = PortfolioChoice((), 0.0, 0.0, 0.0, True)
    if not rows:
        return empty
    profiles = [application_profile(row) for row in rows]
    # 只剔除在任何可行组合中都不可能出现的记录：readiness 不达标会让包含它的组合直接
    # 不可行；容量均为非负，单条容量已超限的记录同理。这不是截断候选——穷举搜索也永远
    # 不会选中这些记录，最优解不受影响。
    eligible = [index for index, profile in enumerate(profiles)
                if profile["readiness"] >= .35 and profile["capacity"] <= capacity_limit]
    if not eligible:
        return empty
    row_value = [0.0] * len(rows)
    row_capacity = [0.0] * len(rows)
    row_group = [""] * len(rows)
    for index in eligible:
        profile = profiles[index]
        row_value[index] = profile["value"]
        row_capacity[index] = profile["capacity"]
        row_group[index] = normalized_text(rows[index].payload.get("use_case", "unknown"))
    # 搜索顺序按价值密度降序（并列按原始顺序），只影响收敛速度，不影响最终结果。
    def density(index: int) -> float:
        capacity = row_capacity[index]
        if capacity > 0.0:
            return row_value[index] / capacity
        return math.inf if row_value[index] > 0.0 else -math.inf

    ordered = sorted(eligible, key=lambda index: (-density(index), index))
    total = len(ordered)
    # suffix_counts[pos]：搜索序列 pos 及之后每个用途组的剩余条数，用于判断集中度是否还能稀释。
    suffix_counts: list[dict[str, int]] = [dict() for _ in range(total + 1)]
    for pos in range(total - 1, -1, -1):
        counts = dict(suffix_counts[pos + 1])
        group = row_group[ordered[pos]]
        counts[group] = counts.get(group, 0) + 1
        suffix_counts[pos] = counts
    best_value = 0.0
    best_choice: tuple[int, ...] = ()
    stack: list[tuple[int, tuple[int, ...]]] = [(0, ())]
    while stack:
        pos, selected = stack.pop()
        # 按与 evaluate_choice 相同的顺序和精度重算当前组合总量，保证判定与穷举零误差。
        capacity_total = 0.0
        value_total = 0.0
        counts: dict[str, int] = {}
        for index in selected:
            capacity_total += row_capacity[index]
            value_total += row_value[index]
            group = row_group[index]
            counts[group] = counts.get(group, 0) + 1
        if capacity_total > capacity_limit:
            continue  # 容量非负，子树不可能再回到限值以内
        remaining = total - pos
        dilutable = True
        for group, count in counts.items():
            others = remaining - suffix_counts[pos].get(group, 0)
            if count / (len(selected) + others) > concentration_limit:
                dilutable = False  # 即使选中其余全部用途的候选也无法稀释到限值以内
                break
        if not dilutable:
            continue
        if selected:
            concentration = max(count / len(selected) for count in counts.values())
            if concentration <= concentration_limit:
                if (value_total > best_value or
                        (value_total == best_value and best_choice and
                         (len(selected) < len(best_choice) or
                          (len(selected) == len(best_choice) and selected < best_choice)))):
                    best_value = value_total
                    best_choice = selected
        if pos >= total:
            continue
        # 上界：忽略集中度、容量可取分数的松弛解；上界已低于当前最优的分支不可能更优。
        bound = value_total
        room = capacity_limit - capacity_total
        for ahead in range(pos, total):
            value = row_value[ordered[ahead]]
            if value <= 0.0:
                continue
            capacity = row_capacity[ordered[ahead]]
            if capacity <= room:
                bound += value
                room -= capacity
            else:
                bound += value * (room / capacity)
                break
        if bound < best_value - 1e-12 * max(1.0, abs(best_value)):
            continue
        stack.append((pos + 1, selected))  # 先压入「不选」，让「选」的分支先被探索
        index = ordered[pos]
        stack.append((pos + 1, tuple(sorted(selected + (index,)))))
    if not best_choice:
        return empty
    return evaluate_choice([rows[index] for index in best_choice], capacity_limit, concentration_limit)


def shock(record: DomainRecord, currency_delta: float = 0.0, policy_delta: float = 0.0) -> dict[str, float]:
    base = application_profile(record)
    changed_payload = dict(record.payload)
    changed_payload["continuity_risk"] = bounded(finite_number(changed_payload.get("continuity_risk", 0.0)) + currency_delta)
    changed_payload["policy_risk"] = bounded(finite_number(changed_payload.get("policy_risk", 0.0)) + policy_delta)
    changed = application_profile(DomainRecord(record.record_id, changed_payload, record.state, record.version, record.occurred_at, record.source))
    return {"base_value": base["value"], "shocked_value": changed["value"], "value_delta": changed["value"] - base["value"],
            "risk_delta": changed["risk"] - base["risk"]}


def derive_context(record: DomainRecord, repository: Any) -> dict[str, float]:
    rows = repository.list_records() or [record]
    profile = application_profile(record)
    choice = optimize(rows, sum(application_profile(row)["capacity"] for row in rows) * .75 + 1.0)
    downside = shock(record, .15, .15)
    return {"readiness_index_weight": 0.6 + profile["readiness"] * 0.6,
            "concentration_risk_weight": 0.7 + choice.concentration * 0.7,
            "capacity_fit_weight": 1.1 - bounded(choice.capacity / max(1.0, profile["capacity"] * len(rows))) * 0.3,
            "commercial_resilience_weight": 0.8 + bounded(1.0 + downside["value_delta"] / max(1.0, abs(profile["value"]))) * 0.3,
            "portfolio_value_weight": 0.6 + bounded(choice.value / max(1.0, choice.value + 100.0)) * 0.6}
