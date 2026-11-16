from __future__ import annotations

import itertools
import random
import time
import unittest
from compute_allocation.requests.application import DomainRecord
from compute_allocation.capacity.allocation_solver import (
    PortfolioChoice, derive_context, evaluate_choice, application_profile, optimize, shock)


def exhaustive_reference(records, capacity_limit, concentration_limit=.6):
    """修复前的全量穷举实现，作为等价性基准。"""
    rows = list(records)
    best = PortfolioChoice((), 0.0, 0.0, 0.0, True)
    for size in range(1, len(rows) + 1):
        for combination in itertools.combinations(rows, size):
            choice = evaluate_choice(combination, capacity_limit, concentration_limit)
            if choice.feasible and choice.value > best.value:
                best = choice
    return best


def random_record(rng, index):
    return DomainRecord(f"req-{index:03d}", {
        "requestor_country": f"country-{rng.randrange(4)}",
        "use_case": f"use-{rng.randrange(4)}",
        "public_value_proof": rng.random(),
        "resource_gap": rng.random(),
        "partner_assurance": rng.random(),
        "localization_effort": rng.uniform(0, 40),
        "delivery_capacity": rng.uniform(0, 30),
        "requested_units": rng.uniform(0, 60),
        "continuity_risk": rng.random(),
        "policy_risk": rng.random(),
        "operations_cost": rng.uniform(0, 40),
        "dependency_count": rng.uniform(0, 40),
    })


class StubRepository:
    def __init__(self, records):
        self._records = list(records)

    def list_records(self, state=None):
        return list(self._records)


class SelectionTests(unittest.TestCase):
    def record(self, key, country="th", revenue=100):
        return DomainRecord(key, {"requestor_country": "robot", "use_case": country, "public_value_proof": .8,
            "resource_gap": .2, "partner_assurance": .8, "localization_effort": 10, "delivery_capacity": 4,
            "requested_units": revenue, "continuity_risk": .2, "policy_risk": .2, "operations_cost": 5, "dependency_count": 2})

    def test_capacity_and_concentration_constraints(self):
        rows = [self.record("a", "th", 120), self.record("b", "vn", 100), self.record("c", "th", 80)]
        choice = optimize(rows, capacity_limit=8, concentration_limit=.6)
        self.assertTrue(choice.feasible)
        self.assertLessEqual(choice.capacity, 8)
        self.assertFalse(evaluate_choice(rows, 5, .5).feasible)

    def test_shock_reduces_value(self):
        result = shock(self.record("a"), .3, .3)
        self.assertLess(result["shocked_value"], result["base_value"])
        self.assertGreater(application_profile(self.record("a"))["readiness"], .5)


class OptimizeEquivalenceTests(unittest.TestCase):
    """分支定界必须与全量穷举逐位一致：同一最优组合、同一价值/容量/集中度。"""

    def check_equivalent(self, records, capacity_limit, concentration_limit):
        expected = exhaustive_reference(records, capacity_limit, concentration_limit)
        actual = optimize(records, capacity_limit, concentration_limit)
        self.assertEqual(actual.application_ids, expected.application_ids)
        self.assertEqual(actual.value, expected.value)
        self.assertEqual(actual.capacity, expected.capacity)
        self.assertEqual(actual.concentration, expected.concentration)
        self.assertEqual(actual.feasible, expected.feasible)

    def test_matches_exhaustive_search_on_random_batches(self):
        for seed in range(60):
            rng = random.Random(seed)
            records = [random_record(rng, index) for index in range(rng.randrange(1, 13))]
            total_capacity = sum(record.payload["delivery_capacity"] for record in records)
            capacity_limit = rng.uniform(-5.0, total_capacity * 1.2)
            concentration_limit = rng.choice([0.0, 0.4, 0.5, 0.6, 0.8, 1.0])
            with self.subTest(seed=seed):
                self.check_equivalent(records, capacity_limit, concentration_limit)

    def test_keeps_every_constraint_of_evaluate_choice(self):
        rng = random.Random(2026)
        records = [random_record(rng, index) for index in range(14)]
        choice = optimize(records, capacity_limit=50.0, concentration_limit=.55)
        self.assertTrue(choice.feasible)
        self.assertLessEqual(choice.capacity, 50.0)
        self.assertLessEqual(choice.concentration, .55)
        selected = [record for record in records if record.record_id in choice.application_ids]
        self.assertEqual(evaluate_choice(selected, 50.0, .55).application_ids, choice.application_ids)


class OptimizeScaleTests(unittest.TestCase):
    """较大批次必须在会议窗口内完成，且仍满足全部既有约束。"""

    def batch(self, count):
        records = []
        for index in range(count):
            records.append(DomainRecord(f"compute_request-{index + 1:03d}", {
                "requestor_country": f"requestor_country-{index % 5}",
                "use_case": f"use_case-{index % 7}",
                "public_value_proof": 0.25 + (index % 8) * 0.11,
                "resource_gap": 0.25 + ((index + 1) % 8) * 0.11,
                "partner_assurance": 0.25 + ((index + 2) % 8) * 0.11,
                "localization_effort": 21.5 + index * 3.7,
                "delivery_capacity": 23.4 + index * 3.7,
                "requested_units": 25.3 + index * 3.7,
                "continuity_risk": 0.25 + ((index + 3) % 8) * 0.11,
                "policy_risk": 0.25 + ((index + 4) % 8) * 0.11,
                "operations_cost": 31.0 + index * 3.7,
                "dependency_count": 32.9 + index * 3.7,
            }))
        return records

    def test_optimize_handles_dozen_plus_candidates(self):
        records = self.batch(26)
        capacity_limit = sum(application_profile(record)["capacity"] for record in records) * .75 + 1.0
        started = time.monotonic()
        choice = optimize(records, capacity_limit)
        elapsed = time.monotonic() - started
        self.assertLess(elapsed, 20.0)  # 穷举实现同规模需约一小时
        self.assertTrue(choice.feasible)
        self.assertLessEqual(choice.capacity, capacity_limit)
        self.assertLessEqual(choice.concentration, .6)

    def test_derive_context_stays_timely_for_full_batch(self):
        records = self.batch(18)
        repository = StubRepository(records)
        started = time.monotonic()
        for record in records:
            context = derive_context(record, repository)
        elapsed = time.monotonic() - started
        self.assertLess(elapsed, 20.0)  # 穷举实现同规模整批需约一分钟
        self.assertEqual(set(context), {"readiness_index_weight", "concentration_risk_weight",
                                        "capacity_fit_weight", "commercial_resilience_weight",
                                        "portfolio_value_weight"})
        self.assertTrue(all(0.0 <= value <= 2.0 for value in context.values()))
