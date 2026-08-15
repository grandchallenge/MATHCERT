#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validator", ROOT / "ci/validate_otp_compactness_adjudication_execution_input.py"
)
validator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(validator)
BASE = json.loads((ROOT / "governance/result_family_adjudication_execution_inputs/OTP-J1-COMPACTNESS.json").read_text(encoding="utf-8"))


class CompactnessAdjudicationInputMutationTests(unittest.TestCase):
    def assert_rejected(self, mutate):
        record = copy.deepcopy(BASE)
        mutate(record)
        with self.assertRaises(Exception):
            validator.validate_record(record, check_repository=False)

    def test_baseline(self):
        validator.validate_record(copy.deepcopy(BASE), check_repository=True)

    def test_target_omission_rejected(self):
        self.assert_rejected(lambda r: r["encoded_targets"].pop())

    def test_another_family_target_rejected(self):
        self.assert_rejected(lambda r: r["encoded_targets"].append("TwoDegenerateGraphs.not_erdos_146"))

    def test_source_substitution_rejected(self):
        self.assert_rejected(lambda r: r["current_source"].__setitem__("expected_sha256", "0" * 64))

    def test_source_byte_drift_rejected(self):
        self.assert_rejected(lambda r: r["current_source"].__setitem__("expected_bytes", 1))

    def test_whole_document_equivalence_inflation_rejected(self):
        self.assert_rejected(lambda r: r["current_source"].__setitem__("whole_document_equivalence_between_revisions", "established"))

    def test_contract_substitution_rejected(self):
        self.assert_rejected(lambda r: r["contract"].__setitem__("contract_id", "OTHER"))

    def test_evidence_substitution_rejected(self):
        self.assert_rejected(lambda r: r["protected_evidence"].__setitem__("record_git_blob_sha1", "0" * 40))

    def test_disposition_insertion_rejected(self):
        self.assert_rejected(lambda r: r["decision_contract"].__setitem__("disposition_at_input_stage", "adjudication_clear_encoded_targets_only"))

    def test_disposition_set_inflation_rejected(self):
        self.assert_rejected(lambda r: r["decision_contract"]["admissible_dispositions"].append("qualified"))

    def test_authorization_prepopulation_rejected(self):
        def mutate(r):
            r["execution_recipe"]["execution_authorized"] = True
            r["execution_recipe"]["authorization"] = {"comment_id": 1}
        self.assert_rejected(mutate)

    def test_exact_head_gate_weakening_rejected(self):
        self.assert_rejected(lambda r: r["execution_recipe"].__setitem__("authorization_must_name_contract_and_exact_head", False))

    def test_fresh_replay_gate_weakening_rejected(self):
        self.assert_rejected(lambda r: r["execution_recipe"].__setitem__("fresh_isolated_replay_required", False))

    def test_route_transition_rejected(self):
        self.assert_rejected(lambda r: r["required_state"].__setitem__("route_state", "qualified"))

    def test_output_insertion_rejected(self):
        self.assert_rejected(lambda r: r["required_state"].__setitem__("cert_output", {}))

    def test_proof_promotion_rejected(self):
        self.assert_rejected(lambda r: r["required_state"].__setitem__("mathematical_target_proved", True))

    def test_aggregate_adjudication_rejected(self):
        self.assert_rejected(lambda r: r["required_state"].__setitem__("aggregate_adjudication", True))

    def test_review_prepopulation_rejected(self):
        self.assert_rejected(lambda r: r["review_gate"].__setitem__("recorded_review", {"state": "APPROVED"}))

    def test_proof_body_inflation_rejected(self):
        self.assert_rejected(lambda r: r["preserved_limitations"].__setitem__("proof_body_compared_in_full", True))

    def test_schema_opening_by_extra_top_level_field_rejected(self):
        self.assert_rejected(lambda r: r.__setitem__("unexpected", True))


if __name__ == "__main__":
    unittest.main()
