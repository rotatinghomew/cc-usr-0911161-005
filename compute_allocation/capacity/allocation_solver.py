from __future__ import annotations

import itertools
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
    rows = list(records)
    best = PortfolioChoice((), 0.0, 0.0, 0.0, True)
    for size in range(1, len(rows) + 1):
        for combination in itertools.combinations(rows, size):
            choice = evaluate_choice(combination, capacity_limit, concentration_limit)
            if choice.feasible and choice.value > best.value:
                best = choice
    return best


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
