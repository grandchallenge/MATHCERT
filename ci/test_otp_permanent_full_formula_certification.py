#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validator", ROOT / "ci/validate_otp_permanent_full_formula_certification.py")
validator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(validator)


class FullFormulaCertificationMutations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = validator.records_from_disk()
        baseline = validator.validation_errors(copy.deepcopy(cls.records), check_git=False)
        if baseline:
            raise AssertionError("baseline invalid: " + "; ".join(baseline))

    def errors(self, records):
        return validator.validation_errors(records, check_git=False)

    def test_target_inflation_rejected(self):
        r = copy.deepcopy(self.records)
        r["certificate"]["encoded_targets"].append("PermanentRollout.permanent_circuit_loglog_lower_bound")
        self.assertTrue(self.errors(r))

    def test_constant_drift_rejected(self):
        r = copy.deepcopy(self.records)
        r["intake"]["target_scope"]["source_projection"]["division_free"]["internal_gates"] = 255
        self.assertTrue(self.errors(r))

    def test_circuit_insertion_rejected(self):
        r = copy.deepcopy(self.records)
        r["proposal"]["route_contract"]["target_claim_ids"].append("PermanentRollout.permanent_circuit_loglog_lower_bound")
        self.assertTrue(self.errors(r))

    def test_source_substitution_rejected(self):
        r = copy.deepcopy(self.records)
        r["intake"]["authority"]["producer_packet"]["digest"] = "0" * 40
        self.assertTrue(self.errors(r))

    def test_overlay_substitution_rejected(self):
        r = copy.deepcopy(self.records)
        r["intake"]["authority"]["comparator_overlay"]["lean_digest"] = "0" * 40
        self.assertTrue(self.errors(r))

    def test_route_prepopulation_rejected(self):
        r = copy.deepcopy(self.records)
        r["route"]["route"]["intake_status"] = "qualified"
        self.assertTrue(self.errors(r))

    def test_route_output_prepopulation_rejected(self):
        r = copy.deepcopy(self.records)
        r["route"]["route"]["cert_output"] = {"fake": True}
        self.assertTrue(self.errors(r))

    def test_review_gate_removal_rejected(self):
        r = copy.deepcopy(self.records)
        r["contract"]["positive_gate"]["fresh_non_author_specialist_review_required"] = False
        self.assertTrue(self.errors(r))

    def test_replay_gate_removal_rejected(self):
        r = copy.deepcopy(self.records)
        r["adjudication"]["basis"]["fresh_exact_head_replay_required"] = False
        self.assertTrue(self.errors(r))

    def test_proof_promotion_rejected(self):
        r = copy.deepcopy(self.records)
        r["certificate"]["state"]["mathematical_target_proved"] = True
        self.assertTrue(self.errors(r))

    def test_aggregate_authority_rejected(self):
        r = copy.deepcopy(self.records)
        r["transition"]["post_transition"]["aggregate_output"] = True
        self.assertTrue(self.errors(r))

    def test_certificate_order_drift_rejected(self):
        r = copy.deepcopy(self.records)
        r["transition"]["certificate_content"]["content_commit"] = "0" * 40
        self.assertTrue(self.errors(r))

    def test_historical_pdf_inflation_rejected(self):
        r = copy.deepcopy(self.records)
        r["intake"]["target_scope"]["source_projection"]["historical_pdf_byte_equivalence"] = True
        self.assertTrue(self.errors(r))

    def test_adjudication_vocabulary_drift_rejected(self):
        r = copy.deepcopy(self.records)
        r["contract"]["admissible_dispositions"] = ["certified"]
        self.assertTrue(self.errors(r))


if __name__ == "__main__":
    unittest.main()
