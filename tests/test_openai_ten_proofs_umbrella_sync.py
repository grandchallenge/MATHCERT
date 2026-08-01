from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "governance" / "pre_route_candidates" / "OPENAI_TEN_PROOFS_WP00_SYNC.json"
SCHEMA = ROOT / "schemas" / "openai_ten_proofs_umbrella_sync.schema.json"


class OpenAITenProofsUmbrellaSyncTests(unittest.TestCase):
    def setUp(self) -> None:
        self.record = json.loads(RECORD.read_text(encoding="utf-8"))
        self.validator = Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8")))

    def errors(self, record):
        return list(self.validator.iter_errors(record))

    def test_current_record_is_valid(self) -> None:
        self.assertEqual(self.errors(self.record), [])

    def test_current_root_cannot_be_replaced_by_historical_root(self) -> None:
        record = copy.deepcopy(self.record)
        record["subject"]["current_official"]["commit"] = record["subject"]["historical_disconnected"]["commit"]
        self.assertTrue(self.errors(record))

    def test_replay_and_source_acquisition_are_present(self) -> None:
        self.assertEqual(self.record["upstream_state"]["kernel_replay"], "clear_12_of_12_corrected_target_set")
        self.assertEqual(self.record["upstream_state"]["source_acquisition"], "present")

    def test_semantic_zero_forbids_handoff_and_adjudication(self) -> None:
        for path in (
            ("intake_controls", "solve_handoff_present"),
            ("intake_controls", "may_adjudicate"),
            ("route_controls", "may_accept_result_family_handoff"),
            ("route_controls", "may_adjudicate"),
            ("route_controls", "may_promote_claim"),
        ):
            with self.subTest(path=path):
                record = copy.deepcopy(self.record)
                record[path[0]][path[1]] = True
                self.assertTrue(self.errors(record))

    def test_cert_route_and_output_remain_null(self) -> None:
        for field in ("certification_route_registry_entry", "cert_output"):
            record = copy.deepcopy(self.record)
            record["route_controls"][field] = {"state": "certified"}
            self.assertTrue(self.errors(record))

    def test_aggregate_import_failure_cannot_create_route(self) -> None:
        record = copy.deepcopy(self.record)
        record["aggregate_integration"]["creates_cert_route"] = True
        self.assertTrue(self.errors(record))

    def test_aggregate_route_remains_prohibited(self) -> None:
        record = copy.deepcopy(self.record)
        record["route_controls"]["aggregate_route_prohibited"] = False
        self.assertTrue(self.errors(record))

    def test_authority_identity_is_closed(self) -> None:
        record = copy.deepcopy(self.record)
        record["authority"]["forge_evidence_merge"] = "0" * 40
        self.assertTrue(self.errors(record))

    def test_unexpected_field_is_rejected(self) -> None:
        record = copy.deepcopy(self.record)
        record["route_controls"]["aggregate_certified"] = True
        self.assertTrue(self.errors(record))


if __name__ == "__main__":
    unittest.main()
