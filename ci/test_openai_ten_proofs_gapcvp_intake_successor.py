#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "ci/validate_openai_ten_proofs_gapcvp_intake_successor.py"
spec = importlib.util.spec_from_file_location("gapcvp_intake_validator", VALIDATOR_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class GapCVPIntakeSuccessorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = module.load_record()

    def reject(self, mutate) -> None:
        candidate = copy.deepcopy(self.data)
        mutate(candidate)
        with self.assertRaises(ValueError):
            module.validate_record(candidate)

    def test_exact_record_validates(self):
        module.validate_record(self.data)
        module.validate_repository_guards()

    def test_historical_snapshot_route_inflation_fails_closed(self):
        historical = {"routes": [{"route_id": module.OWN_ROUTE_ID, "campaign_id": module.FAMILY_ID}]}
        with mock.patch.object(module, "load_historical_routes", return_value=historical):
            with self.assertRaises(ValueError):
                module.validate_repository_guards()

    def test_historical_snapshot_without_family_route_is_accepted(self):
        historical = {"routes": [{"route_id": "OTHER", "campaign_id": "OTHER"}]}
        with mock.patch.object(module, "load_historical_routes", return_value=historical):
            module.validate_repository_guards()

    def test_target_substitution_fails_closed(self):
        self.reject(lambda d: d["target_scope"]["lean_theorems"].__setitem__(0, "Fake.target"))

    def test_promise_substitution_fails_closed(self):
        self.reject(lambda d: d["target_scope"]["promise_interfaces"].__setitem__(0, "Fake.promise"))

    def test_packet_hash_mutation_fails_closed(self):
        self.reject(lambda d: d["authority"]["producer_packet"].__setitem__("digest", "0"*40))

    def test_semantic_audit_mutation_fails_closed(self):
        self.reject(lambda d: d["authority"]["forge_semantic"].__setitem__("audit_blob", "0"*40))

    def test_formal_root_mutation_fails_closed(self):
        self.reject(lambda d: d["authority"]["official_subject"].__setitem__("commit", "0"*40))

    def test_replay_job_mutation_fails_closed(self):
        self.reject(lambda d: d["authority"]["isolated_replay"].__setitem__("job_id", 0))

    def test_gap_factor_flattening_fails_closed(self):
        self.reject(lambda d: d["target_scope"]["gap_factors"].__setitem__(0, "400"))

    def test_integer_target_restriction_erasure_fails_closed(self):
        self.reject(lambda d: d["target_scope"]["classifications"].__setitem__(0, "source_faithful_whole_problem_identity"))

    def test_consistent_syndrome_restriction_erasure_fails_closed(self):
        self.reject(lambda d: d["target_scope"]["classifications"].__setitem__(2, "source_faithful_unrestricted_syndrome"))

    def test_nonvacuity_inflation_fails_closed(self):
        self.reject(lambda d: d["target_scope"]["nonvacuity"].__setitem__("state", "certifies_np_hardness"))

    def test_route_inflation_fails_closed(self):
        self.reject(lambda d: d["state"].__setitem__("route_registered", True))

    def test_adjudication_inflation_fails_closed(self):
        self.reject(lambda d: d["state"].__setitem__("may_adjudicate", True))

    def test_certificate_inflation_fails_closed(self):
        self.reject(lambda d: d["state"].__setitem__("cert_output", {"id": "invented"}))

    def test_proof_promotion_fails_closed(self):
        self.reject(lambda d: d["state"].__setitem__("mathematical_target_proved", True))

    def test_aggregate_authority_fails_closed(self):
        self.reject(lambda d: d["state"].__setitem__("aggregate_authority", True))

    def test_schema_is_closed(self):
        schema = module.load_schema()
        self.assertIs(schema["additionalProperties"], False)
        candidate = copy.deepcopy(self.data)
        candidate["unexpected_authority"] = True
        with self.assertRaises(ValueError):
            module.validate_record(candidate)


if __name__ == "__main__":
    unittest.main()
