from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ci"))
from validate_hc_wp00_qualification import errors

FILES = [
    "certificates/hodge/MC-HC-WP00-QUAL-001.json",
    "certificates/hodge/claim_records/HC-C001.json",
    "certificates/hodge/claim_records/HC-C002.json",
    "certificates/hodge/claim_records/HC-C003.json",
    "schemas/hc_claim_record.schema.json",
    "schemas/hc_wp00_qualification.schema.json",
    "governance/certification_routes.json",
]


class HCQualificationTests(unittest.TestCase):
    def copy(self) -> Path:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        for relative in FILES:
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)
        return root

    def mutate(self, relative: str, action) -> list[str]:
        root = self.copy()
        path = root / relative
        value = json.loads(path.read_text(encoding="utf-8"))
        action(value)
        path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
        return errors(root)

    def assert_error(self, found: list[str], fragment: str) -> None:
        self.assertTrue(any(fragment in item for item in found), found)

    def test_valid(self) -> None:
        self.assertEqual([], errors())

    def test_coefficient_mutation_rejected(self) -> None:
        found = self.mutate("certificates/hodge/claim_records/HC-C001.json", lambda v: v.update(coefficient_ring="Z"))
        self.assert_error(found, "semantic coefficient_ring drift")

    def test_geometry_mutation_rejected(self) -> None:
        found = self.mutate("certificates/hodge/claim_records/HC-C001.json", lambda v: v.update(geometric_category="compact_kahler_manifold"))
        self.assert_error(found, "semantic geometric_category drift")

    def test_rationality_loss_rejected(self) -> None:
        found = self.mutate("certificates/hodge/claim_records/HC-C001.json", lambda v: v.update(input_class_predicate="alpha has Hodge type (p,p)"))
        self.assert_error(found, "rationality predicate drift")

    def test_quantifier_weakening_rejected(self) -> None:
        found = self.mutate("certificates/hodge/claim_records/HC-C001.json", lambda v: v.update(quantifier_scope="sampled_classes"))
        self.assert_error(found, "universal quantifier drift")

    def test_implication_reversal_rejected(self) -> None:
        found = self.mutate("certificates/hodge/claim_records/HC-C002.json", lambda v: v.update(implication_direction="algebraic_to_Hodge"))
        self.assert_error(found, "equivalence direction drift")

    def test_effectivity_inflation_rejected(self) -> None:
        found = self.mutate("certificates/hodge/claim_records/HC-C002.json", lambda v: v.update(claims_not_made=["uniqueness of a cycle"]))
        self.assert_error(found, "effectivity boundary removed")

    def test_dimension_inflation_rejected(self) -> None:
        found = self.mutate("certificates/hodge/claim_records/HC-C003.json", lambda v: v.update(dimension_scope="dim X <= 4"))
        self.assert_error(found, "conditional dimension boundary drift")

    def test_universal_proof_promotion_rejected(self) -> None:
        found = self.mutate("certificates/hodge/MC-HC-WP00-QUAL-001.json", lambda v: v.update(full_hodge_conjecture_proved=True))
        self.assert_error(found, "must remain false")

    def test_kernel_claim_insertion_rejected(self) -> None:
        def change(value: dict) -> None:
            value["replay"]["lean_formalization_available"] = True
            value["replay"]["kernel_checked_claims"] = ["HC-C003"]
        found = self.mutate("certificates/hodge/MC-HC-WP00-QUAL-001.json", change)
        self.assert_error(found, "formalization boundary inflated")

    def test_specialist_boundary_removal_rejected(self) -> None:
        def change(value: dict) -> None:
            value["unresolved_obligations"] = [item for item in value["unresolved_obligations"] if "specialist" not in item]
        found = self.mutate("certificates/hodge/MC-HC-WP00-QUAL-001.json", change)
        self.assert_error(found, "missing token: specialist")

    def test_route_rollback_rejected(self) -> None:
        def change(value: dict) -> None:
            next(item for item in value["routes"] if item["campaign_id"] == "HC-001")["intake_status"] = "ready"
        found = self.mutate("governance/certification_routes.json", change)
        self.assert_error(found, "route state or target set drift")

    def test_route_output_drift_rejected(self) -> None:
        def change(value: dict) -> None:
            next(item for item in value["routes"] if item["campaign_id"] == "HC-001")["cert_output"]["digest"] = "0" * 40
        found = self.mutate("governance/certification_routes.json", change)
        self.assert_error(found, "route output identity drift")


if __name__ == "__main__":
    unittest.main()
