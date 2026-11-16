from __future__ import annotations

import unittest
from compute_allocation.requests.application import DomainRecord
from compute_allocation.capacity.allocation_solver import evaluate_choice, application_profile, optimize, shock


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
