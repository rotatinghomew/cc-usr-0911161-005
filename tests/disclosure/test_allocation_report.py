from __future__ import annotations

import csv
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from compute_allocation.requests.application import ContractError, Decision, DomainRecord, records_from_fixture, stable_hash
from compute_allocation.ledger.allocation_log import Repository
from compute_allocation.lifecycle.reservation_flow import STATES, advance_for_outcome, allowed_targets, apply_transition, decide, guard_report, plan_transition
from compute_allocation.disclosure.allocation_report import export_bundle, verify_bundle
from compute_allocation.allocation_office import Application, load_fixture, run, verify


FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "acceptance.json"


def load_records() -> list[DomainRecord]:
    return records_from_fixture(json.loads(FIXTURE.read_text(encoding="utf-8")))


class RepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.database = Path(self.temp.name) / "state.sqlite3"
        self.repository = Repository(self.database)
        self.record = load_records()[0]

    def test_initialize_creates_expected_tables(self):
        with sqlite3.connect(self.database) as connection:
            tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertTrue({"records", "record_versions", "decisions", "events", "runs"}.issubset(tables))

    def test_save_and_load_record_round_trip(self):
        fingerprint = self.repository.save_record(self.record)
        loaded = self.repository.get_record(self.record.record_id)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.fingerprint, fingerprint)
        self.assertEqual(loaded.payload, self.record.payload)

    def test_identical_record_replay_is_idempotent(self):
        first = self.repository.save_record(self.record)
        second = self.repository.save_record(self.record)
        self.assertEqual(first, second)
        self.assertEqual(self.repository.snapshot()["counts"]["records"], 1)
        self.assertEqual(self.repository.snapshot()["counts"]["record_versions"], 1)

    def test_conflicting_version_is_rejected(self):
        self.repository.save_record(self.record)
        changed = self.record.with_payload({'requestor_country': 999})
        with self.assertRaisesRegex(ContractError, "version conflict"):
            self.repository.save_record(changed, expected_version=99)

    def test_version_must_advance(self):
        self.repository.save_record(self.record)
        changed = DomainRecord(self.record.record_id, dict(self.record.payload) | {'use_case': "changed"},
                               self.record.state, self.record.version, self.record.occurred_at, self.record.source)
        with self.assertRaisesRegex(ContractError, "version must advance"):
            self.repository.save_record(changed)

    def test_decision_requires_existing_record(self):
        decision = decide(self.record)
        with self.assertRaisesRegex(ContractError, "does not exist"):
            self.repository.save_decision(decision)

    def test_decision_replay_is_idempotent(self):
        self.repository.save_record(self.record)
        decision = decide(self.record)
        first = self.repository.save_decision(decision)
        second = self.repository.save_decision(decision)
        self.assertEqual(first, second)
        self.assertEqual(self.repository.snapshot()["counts"]["decisions"], 1)

    def test_audit_chain_detects_payload_tampering(self):
        self.repository.save_record(self.record)
        self.assertEqual(self.repository.verify_chain(), [])
        with sqlite3.connect(self.database) as connection:
            connection.execute("UPDATE events SET payload_json='{}' WHERE event_id=1")
        self.assertTrue(self.repository.verify_chain())

    def test_run_lifecycle_is_recorded(self):
        run_id = self.repository.begin_run("a" * 64, 3)
        self.repository.finish_run(run_id, {"ok": True})
        snapshot = self.repository.snapshot()
        self.assertEqual(snapshot["counts"]["runs"], 1)
        self.assertGreaterEqual(snapshot["counts"]["events"], 1)

    def test_list_records_filters_state(self):
        self.repository.save_record(self.record)
        advanced = self.record.with_state(STATES[1])
        self.repository.save_record(advanced, expected_version=1)
        self.assertEqual(len(self.repository.list_records(STATES[1])), 1)
        self.assertEqual(self.repository.list_records(STATES[1])[0].version, 2)


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.record = load_records()[0]

    def test_allowed_targets_are_forward_only(self):
        targets = allowed_targets(STATES[0])
        self.assertTrue(targets)
        self.assertNotIn(STATES[0], targets)

    def test_unknown_state_is_rejected(self):
        with self.assertRaisesRegex(ContractError, "unknown workflow"):
            allowed_targets("unknown")

    def test_non_adjacent_transition_is_blocked(self):
        plan = plan_transition(self.record, STATES[-1], {"transition_threshold": 0.0})
        self.assertFalse(plan.allowed)
        self.assertTrue(any("not adjacent" in reason for reason in plan.reasons))

    def test_adjacent_transition_can_be_applied(self):
        plan = plan_transition(self.record, STATES[1], {"transition_threshold": 0.0})
        self.assertTrue(plan.allowed)
        changed = apply_transition(self.record, STATES[1], {"transition_threshold": 0.0})
        self.assertEqual(changed.state, STATES[1])
        self.assertEqual(changed.version, 2)

    def test_decision_contains_full_rule_evidence(self):
        decision = decide(self.record)
        self.assertEqual(decision.record_id, self.record.record_id)
        self.assertGreater(len(decision.rule_results), 100)
        self.assertEqual(set(decision.metrics), {'policy_exposure', 'commercial_resilience', 'capacity_fit', 'readiness_index', 'concentration_risk', 'evidence_diversity', 'portfolio_value', 'dependency_fragility'})

    def test_guard_report_counts_every_guard(self):
        result = guard_report(self.record)
        self.assertEqual(result["passed"] + result["failed"], len(result["messages"]))
        self.assertGreater(len(result["messages"]), 50)

    def test_outcome_advancement_is_deterministic(self):
        decision = decide(self.record)
        first = advance_for_outcome(self.record, decision)
        second = advance_for_outcome(self.record, decision)
        self.assertEqual(first, second)


class EndToEndTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.database = self.root / "run.sqlite3"
        self.output = self.root / "output"

    def test_acceptance_run_writes_verified_bundle(self):
        result = run(FIXTURE, self.database, self.output)
        self.assertEqual(result["records"], len(load_records()))
        self.assertTrue((self.output / "manifest.json").is_file())
        self.assertEqual(verify_bundle(self.output), [])
        self.assertTrue(verify(self.database, self.output)["ok"])

    def test_repeated_run_preserves_record_count(self):
        first = run(FIXTURE, self.database, self.output)
        second = run(FIXTURE, self.database, self.output)
        self.assertEqual(first["records"], second["records"])
        self.assertEqual(Repository(self.database).snapshot()["counts"]["records"], len(load_records()))

    def test_manifest_lists_all_json_artifacts(self):
        run(FIXTURE, self.database, self.output)
        manifest = json.loads((self.output / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(set(manifest["files"]), {"summary.json", "decisions.json", "audit-events.json"})
        self.assertGreater(manifest["rule_rows"], 500)

    def test_records_csv_has_one_row_per_record(self):
        run(FIXTURE, self.database, self.output)
        with (self.output / "records.csv").open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), len(load_records()))
        self.assertTrue(all(row["fingerprint"] for row in rows))

    def test_rules_csv_contains_business_evidence(self):
        run(FIXTURE, self.database, self.output)
        with (self.output / "rules.csv").open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertGreater(len(rows), 500)
        self.assertTrue(all(row["code"] and row["message"] for row in rows))

    def test_bundle_tampering_is_detected(self):
        run(FIXTURE, self.database, self.output)
        summary = json.loads((self.output / "summary.json").read_text(encoding="utf-8"))
        summary["record_count"] = 999
        (self.output / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
        self.assertIn("summary.json hash mismatch", verify_bundle(self.output))

    def test_load_fixture_rejects_non_object(self):
        path = self.root / "invalid.json"
        path.write_text("[]", encoding="utf-8")
        with self.assertRaisesRegex(ContractError, "root must be an object"):
            load_fixture(path)

    def test_application_inspect_returns_decisions(self):
        application = Application(self.database)
        application.run_fixture(json.loads(FIXTURE.read_text(encoding="utf-8")), self.output)
        result = application.inspect()
        self.assertEqual(len(result["records"]), len(load_records()))
        self.assertEqual(len(result["decisions"]), len(load_records()))


class ScenarioVariationTests(unittest.TestCase):
    def setUp(self):
        self.records = load_records()

    def test_scenario_01_requestor_country(self):
        base = self.records[0]
        changed = base.with_payload({'requestor_country': 3.25})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('requestor_country', changed.payload)

    def test_scenario_02_use_case(self):
        base = self.records[1]
        changed = base.with_payload({'use_case': 6.5})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('use_case', changed.payload)

    def test_scenario_03_public_value_proof(self):
        base = self.records[2]
        changed = base.with_payload({'public_value_proof': 9.75})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('public_value_proof', changed.payload)

    def test_scenario_04_resource_gap(self):
        base = self.records[3]
        changed = base.with_payload({'resource_gap': 13.0})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('resource_gap', changed.payload)

    def test_scenario_05_partner_assurance(self):
        base = self.records[4]
        changed = base.with_payload({'partner_assurance': 16.25})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('partner_assurance', changed.payload)

    def test_scenario_06_localization_effort(self):
        base = self.records[5]
        changed = base.with_payload({'localization_effort': 19.5})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('localization_effort', changed.payload)

    def test_scenario_07_delivery_capacity(self):
        base = self.records[6]
        changed = base.with_payload({'delivery_capacity': 22.75})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('delivery_capacity', changed.payload)

    def test_scenario_08_requested_units(self):
        base = self.records[7]
        changed = base.with_payload({'requested_units': 26.0})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('requested_units', changed.payload)

    def test_scenario_09_continuity_risk(self):
        base = self.records[0]
        changed = base.with_payload({'continuity_risk': 29.25})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('continuity_risk', changed.payload)

    def test_scenario_10_policy_risk(self):
        base = self.records[1]
        changed = base.with_payload({'policy_risk': 32.5})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('policy_risk', changed.payload)

    def test_scenario_11_operations_cost(self):
        base = self.records[2]
        changed = base.with_payload({'operations_cost': 35.75})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('operations_cost', changed.payload)

    def test_scenario_12_dependency_count(self):
        base = self.records[3]
        changed = base.with_payload({'dependency_count': 39.0})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('dependency_count', changed.payload)

    def test_scenario_13_requestor_country(self):
        base = self.records[4]
        changed = base.with_payload({'requestor_country': 42.25})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('requestor_country', changed.payload)

    def test_scenario_14_use_case(self):
        base = self.records[5]
        changed = base.with_payload({'use_case': 45.5})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('use_case', changed.payload)

    def test_scenario_15_public_value_proof(self):
        base = self.records[6]
        changed = base.with_payload({'public_value_proof': 48.75})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('public_value_proof', changed.payload)

    def test_scenario_16_resource_gap(self):
        base = self.records[7]
        changed = base.with_payload({'resource_gap': 52.0})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('resource_gap', changed.payload)

    def test_scenario_17_partner_assurance(self):
        base = self.records[0]
        changed = base.with_payload({'partner_assurance': 55.25})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('partner_assurance', changed.payload)

    def test_scenario_18_localization_effort(self):
        base = self.records[1]
        changed = base.with_payload({'localization_effort': 58.5})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('localization_effort', changed.payload)

    def test_scenario_19_delivery_capacity(self):
        base = self.records[2]
        changed = base.with_payload({'delivery_capacity': 61.75})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('delivery_capacity', changed.payload)

    def test_scenario_20_requested_units(self):
        base = self.records[3]
        changed = base.with_payload({'requested_units': 65.0})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('requested_units', changed.payload)

    def test_scenario_21_continuity_risk(self):
        base = self.records[4]
        changed = base.with_payload({'continuity_risk': 68.25})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('continuity_risk', changed.payload)

    def test_scenario_22_policy_risk(self):
        base = self.records[5]
        changed = base.with_payload({'policy_risk': 71.5})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('policy_risk', changed.payload)

    def test_scenario_23_operations_cost(self):
        base = self.records[6]
        changed = base.with_payload({'operations_cost': 74.75})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('operations_cost', changed.payload)

    def test_scenario_24_dependency_count(self):
        base = self.records[7]
        changed = base.with_payload({'dependency_count': 78.0})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('dependency_count', changed.payload)

    def test_scenario_25_requestor_country(self):
        base = self.records[0]
        changed = base.with_payload({'requestor_country': 81.25})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('requestor_country', changed.payload)

    def test_scenario_26_use_case(self):
        base = self.records[1]
        changed = base.with_payload({'use_case': 84.5})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('use_case', changed.payload)

    def test_scenario_27_public_value_proof(self):
        base = self.records[2]
        changed = base.with_payload({'public_value_proof': 87.75})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('public_value_proof', changed.payload)

    def test_scenario_28_resource_gap(self):
        base = self.records[3]
        changed = base.with_payload({'resource_gap': 91.0})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('resource_gap', changed.payload)

    def test_scenario_29_partner_assurance(self):
        base = self.records[4]
        changed = base.with_payload({'partner_assurance': 94.25})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('partner_assurance', changed.payload)

    def test_scenario_30_localization_effort(self):
        base = self.records[5]
        changed = base.with_payload({'localization_effort': 97.5})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('localization_effort', changed.payload)

    def test_scenario_31_delivery_capacity(self):
        base = self.records[6]
        changed = base.with_payload({'delivery_capacity': 100.75})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('delivery_capacity', changed.payload)

    def test_scenario_32_requested_units(self):
        base = self.records[7]
        changed = base.with_payload({'requested_units': 104.0})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('requested_units', changed.payload)

    def test_scenario_33_continuity_risk(self):
        base = self.records[0]
        changed = base.with_payload({'continuity_risk': 107.25})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('continuity_risk', changed.payload)

    def test_scenario_34_policy_risk(self):
        base = self.records[1]
        changed = base.with_payload({'policy_risk': 110.5})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('policy_risk', changed.payload)

    def test_scenario_35_operations_cost(self):
        base = self.records[2]
        changed = base.with_payload({'operations_cost': 113.75})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('operations_cost', changed.payload)

    def test_scenario_36_dependency_count(self):
        base = self.records[3]
        changed = base.with_payload({'dependency_count': 117.0})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('dependency_count', changed.payload)

    def test_scenario_37_requestor_country(self):
        base = self.records[4]
        changed = base.with_payload({'requestor_country': 120.25})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('requestor_country', changed.payload)

    def test_scenario_38_use_case(self):
        base = self.records[5]
        changed = base.with_payload({'use_case': 123.5})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('use_case', changed.payload)

    def test_scenario_39_public_value_proof(self):
        base = self.records[6]
        changed = base.with_payload({'public_value_proof': 126.75})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('public_value_proof', changed.payload)

    def test_scenario_40_resource_gap(self):
        base = self.records[7]
        changed = base.with_payload({'resource_gap': 130.0})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('resource_gap', changed.payload)

    def test_scenario_41_partner_assurance(self):
        base = self.records[0]
        changed = base.with_payload({'partner_assurance': 133.25})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('partner_assurance', changed.payload)

    def test_scenario_42_localization_effort(self):
        base = self.records[1]
        changed = base.with_payload({'localization_effort': 136.5})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('localization_effort', changed.payload)

    def test_scenario_43_delivery_capacity(self):
        base = self.records[2]
        changed = base.with_payload({'delivery_capacity': 139.75})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('delivery_capacity', changed.payload)

    def test_scenario_44_requested_units(self):
        base = self.records[3]
        changed = base.with_payload({'requested_units': 143.0})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('requested_units', changed.payload)

    def test_scenario_45_continuity_risk(self):
        base = self.records[4]
        changed = base.with_payload({'continuity_risk': 146.25})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('continuity_risk', changed.payload)

    def test_scenario_46_policy_risk(self):
        base = self.records[5]
        changed = base.with_payload({'policy_risk': 149.5})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('policy_risk', changed.payload)

    def test_scenario_47_operations_cost(self):
        base = self.records[6]
        changed = base.with_payload({'operations_cost': 152.75})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('operations_cost', changed.payload)

    def test_scenario_48_dependency_count(self):
        base = self.records[7]
        changed = base.with_payload({'dependency_count': 156.0})
        original_decision = decide(base)
        changed_decision = decide(changed)
        self.assertEqual(original_decision.record_id, changed_decision.record_id)
        self.assertNotEqual(original_decision.fingerprint, changed_decision.fingerprint)
        self.assertTrue(0.0 <= changed_decision.score <= 1.0)
        self.assertIn('dependency_count', changed.payload)

if __name__ == '__main__':
    unittest.main()
