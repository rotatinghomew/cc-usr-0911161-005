from __future__ import annotations
import unittest
from compute_allocation.allocation_signal.allocation_pressure import allocation_pressure, peer_distribution
class Record:
    def __init__(self, payload): self.payload = payload
class SignalTests(unittest.TestCase):
    def setUp(self): self.payload = {'requestor_country': 'country-a', 'use_case': 'public-health', 'public_value_proof': 0.9, 'resource_gap': 0.8, 'partner_assurance': 0.78, 'localization_effort': 20, 'delivery_capacity': 0.75, 'requested_units': 60, 'continuity_risk': 0.2, 'policy_risk': 0.25, 'operations_cost': 12, 'dependency_count': 3}
    def test_signal_is_bounded_and_explainable(self):
        signal = allocation_pressure(self.payload)
        self.assertGreaterEqual(signal.score, 0.0)
        self.assertLessEqual(signal.score, 1.0)
        self.assertIn(signal.severity, {'info', 'warning', 'critical'})
        self.assertTrue({'capacity_fit', 'risk_total', 'burden'}.issubset(signal.evidence))
    def test_peer_distribution_uses_business_group(self):
        other = dict(self.payload); other['requestor_country'] = 'group-b'
        result = peer_distribution([Record(self.payload), Record(other)])
        self.assertEqual(result['count'], 2)
        self.assertIn('country_units', result)
    def test_material_business_change_is_observable(self):
        changed = dict(self.payload); changed['continuity_risk'] = 0.95
        self.assertNotEqual(allocation_pressure(changed).score, allocation_pressure(self.payload).score)
    def test_business_variant_1(self):
        changed = dict(self.payload)
        changed['public_value_proof'] = self.payload['public_value_proof']
        signal = allocation_pressure(changed)
        self.assertGreaterEqual(signal.score, 0.0)
        self.assertLessEqual(signal.score, 1.0)

    def test_business_variant_2(self):
        changed = dict(self.payload)
        changed['resource_gap'] = self.payload['resource_gap']
        signal = allocation_pressure(changed)
        self.assertGreaterEqual(signal.score, 0.0)
        self.assertLessEqual(signal.score, 1.0)

    def test_business_variant_3(self):
        changed = dict(self.payload)
        changed['partner_assurance'] = self.payload['partner_assurance']
        signal = allocation_pressure(changed)
        self.assertGreaterEqual(signal.score, 0.0)
        self.assertLessEqual(signal.score, 1.0)

    def test_business_variant_4(self):
        changed = dict(self.payload)
        changed['localization_effort'] = self.payload['localization_effort']
        signal = allocation_pressure(changed)
        self.assertGreaterEqual(signal.score, 0.0)
        self.assertLessEqual(signal.score, 1.0)

    def test_business_variant_5(self):
        changed = dict(self.payload)
        changed['delivery_capacity'] = self.payload['delivery_capacity']
        signal = allocation_pressure(changed)
        self.assertGreaterEqual(signal.score, 0.0)
        self.assertLessEqual(signal.score, 1.0)

    def test_business_variant_6(self):
        changed = dict(self.payload)
        changed['requested_units'] = self.payload['requested_units']
        signal = allocation_pressure(changed)
        self.assertGreaterEqual(signal.score, 0.0)
        self.assertLessEqual(signal.score, 1.0)

    def test_business_variant_7(self):
        changed = dict(self.payload)
        changed['continuity_risk'] = self.payload['continuity_risk']
        signal = allocation_pressure(changed)
        self.assertGreaterEqual(signal.score, 0.0)
        self.assertLessEqual(signal.score, 1.0)

if __name__ == '__main__': unittest.main()
