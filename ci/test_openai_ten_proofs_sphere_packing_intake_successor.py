#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "ci/validate_openai_ten_proofs_sphere_packing_intake_successor.py"
spec = importlib.util.spec_from_file_location("sphere_intake_validator", VALIDATOR_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

class SpherePackingIntakeSuccessorTests(unittest.TestCase):
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

    def test_target_substitution_fails_closed(self):
        self.reject(lambda d: d["target_scope"]["lean_theorems"].__setitem__(0, "Fake.target"))

    def test_packet_hash_mutation_fails_closed(self):
        self.reject(lambda d: d["authority"]["producer_packet"].__setitem__("digest", "0"*40))

    def test_composite_semantic_mutation_fails_closed(self):
        self.reject(lambda d: d["authority"]["forge_composite_semantic"].__setitem__("audit_blob", "0"*40))

    def test_bridge_semantic_mutation_fails_closed(self):
        self.reject(lambda d: d["authority"]["forge_bridge_semantic"].__setitem__("audit_blob", "0"*40))

    def test_formal_root_mutation_fails_closed(self):
        self.reject(lambda d: d["authority"]["official_subject"].__setitem__("commit", "0"*40))

    def test_source_digest_mutation_fails_closed(self):
        self.reject(lambda d: d["authority"]["source_pdf"].__setitem__("sha256", "0"*64))

    def test_decimal_source_authorship_inflation_fails_closed(self):
        self.reject(lambda d: d["target_scope"]["semantic_qualifications"].__setitem__(
            "binary_exponent_30_decimal_precision", "source_authored_exact_precision"))

    def test_normalization_erasure_fails_closed(self):
        self.reject(lambda d: d["target_scope"]["semantic_qualifications"].__setitem__(
            "sphere_packing_constant_relation", "definitionally_identical_to_source_delta_d"))

    def test_route_inflation_fails_closed(self):
        self.reject(lambda d: d["state"].__setitem__("route_registered", True))

    def test_adjudication_inflation_fails_closed(self):
        self.reject(lambda d: d["state"].__setitem__("may_adjudicate", True))

    def test_certificate_inflation_fails_closed(self):
        self.reject(lambda d: d["state"].__setitem__("cert_output", {"id":"invented"}))

    def test_proof_promotion_fails_closed(self):
        self.reject(lambda d: d["state"].__setitem__("mathematical_target_proved", True))

    def test_aggregate_authority_fails_closed(self):
        self.reject(lambda d: d["state"].__setitem__("aggregate_authority", True))

    def test_historical_namespace_mutation_fails_closed(self):
        self.reject(lambda d: d["mathcert_subject"].__setitem__("historical_intake_namespace_immutable", False))

    def test_schema_is_closed(self):
        schema = module.load_schema()
        self.assertIs(schema["additionalProperties"], False)
        candidate = copy.deepcopy(self.data)
        candidate["unexpected_authority"] = True
        with self.assertRaises(ValueError):
            module.validate_record(candidate)

if __name__ == "__main__":
    unittest.main()
