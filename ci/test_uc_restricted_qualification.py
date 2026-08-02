from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ci"))

from validate_uc_restricted_qualification import errors

FILES = [
    "certificates/union_closed/MC-UC-WP04-QUAL-001.json",
    "schemas/uc_restricted_qualification.schema.json",
    "governance/certification_routes.json",
    "MathCert/FormalSources/UCRestrictedReplay.lean",
    "MathCert/Domains/UnionClosed/SingletonCase.lean",
    "MathCert/Domains/UnionClosed/TwoElementCase.lean",
    "certificates/exact/union_closed_n_le_4.json",
    "ci/replay_certificates.py",
]


class UCRestrictedQualificationTests(unittest.TestCase):
    def copy(self) -> Path:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        for relative in FILES:
            source = ROOT / relative
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        return root

    @staticmethod
    def read(root: Path, relative: str) -> dict:
        return json.loads((root / relative).read_text(encoding="utf-8"))

    @staticmethod
    def write(root: Path, relative: str, value: dict) -> None:
        (root / relative).write_text(
            json.dumps(value, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def mutate_json(self, relative: str, mutator) -> list[str]:
        root = self.copy()
        value = self.read(root, relative)
        mutator(value)
        self.write(root, relative, value)
        return errors(root)

    def assert_error(self, found: list[str], fragment: str) -> None:
        self.assertTrue(any(fragment in item for item in found), found)

    def test_valid(self) -> None:
        self.assertEqual([], errors())

    def test_schema_must_remain_closed(self) -> None:
        found = self.mutate_json(
            "schemas/uc_restricted_qualification.schema.json",
            lambda value: value.update(additionalProperties=True),
        )
        self.assert_error(found, "schema must remain closed")

    def test_certificate_identity_drift(self) -> None:
        found = self.mutate_json(
            "certificates/union_closed/MC-UC-WP04-QUAL-001.json",
            lambda value: value.update(certificate_id="MC-UC-WP04-UNBOUNDED"),
        )
        self.assert_error(found, "qualification identity drift")

    def test_claim_omission(self) -> None:
        found = self.mutate_json(
            "certificates/union_closed/MC-UC-WP04-QUAL-001.json",
            lambda value: value.update(qualified_claims=value["qualified_claims"][:-1]),
        )
        self.assert_error(found, "exactly three claims")

    def test_universal_claim_insertion(self) -> None:
        def mutate(value: dict) -> None:
            value["qualified_claims"][0]["claim_id"] = "UC-FRANKL"
        found = self.mutate_json("certificates/union_closed/MC-UC-WP04-QUAL-001.json", mutate)
        self.assert_error(found, "universal Frankl claim")

    def test_claim_modality_drift(self) -> None:
        def mutate(value: dict) -> None:
            value["qualified_claims"][0]["modality"] = "EXACT_RATIONAL_CERTIFICATE"
        found = self.mutate_json("certificates/union_closed/MC-UC-WP04-QUAL-001.json", mutate)
        self.assert_error(found, "modality or disposition drift")

    def test_claim_evidence_drift(self) -> None:
        def mutate(value: dict) -> None:
            value["qualified_claims"][1]["evidence"]["digest"] = "0" * 40
        found = self.mutate_json("certificates/union_closed/MC-UC-WP04-QUAL-001.json", mutate)
        self.assert_error(found, "evidence identity drift")

    def test_local_theorem_blob_drift(self) -> None:
        root = self.copy()
        path = root / "MathCert/Domains/UnionClosed/SingletonCase.lean"
        path.write_text(path.read_text(encoding="utf-8") + "\n-- drift\n", encoding="utf-8")
        self.assert_error(errors(root), "local evidence blob mismatch")

    def test_replay_module_blob_drift(self) -> None:
        root = self.copy()
        path = root / "MathCert/FormalSources/UCRestrictedReplay.lean"
        path.write_text(path.read_text(encoding="utf-8") + "\n-- drift\n", encoding="utf-8")
        self.assert_error(errors(root), "Lean replay blob mismatch")

    def test_replay_placeholder_rejected(self) -> None:
        root = self.copy()
        path = root / "MathCert/FormalSources/UCRestrictedReplay.lean"
        path.write_text(path.read_text(encoding="utf-8") + "\n-- sorry\n", encoding="utf-8")
        self.assert_error(errors(root), "proof placeholder")

    def test_finite_certificate_range_drift(self) -> None:
        def mutate(value: dict) -> None:
            value["results"].pop()
        found = self.mutate_json("certificates/exact/union_closed_n_le_4.json", mutate)
        self.assert_error(found, "finite certificate range drift")

    def test_finite_violation_rejected(self) -> None:
        def mutate(value: dict) -> None:
            value["results"][-1]["frankl_violations"] = 1
        found = self.mutate_json("certificates/exact/union_closed_n_le_4.json", mutate)
        self.assert_error(found, "contains a violation")

    def test_finite_qualification_inflation(self) -> None:
        def mutate(value: dict) -> None:
            value["finite_range"]["max_universe_size"] = 5
        found = self.mutate_json("certificates/union_closed/MC-UC-WP04-QUAL-001.json", mutate)
        self.assert_error(found, "range inflation")

    def test_proof_promotion_rejected(self) -> None:
        found = self.mutate_json(
            "certificates/union_closed/MC-UC-WP04-QUAL-001.json",
            lambda value: value.update(mathematical_target_proved=True),
        )
        self.assert_error(found, "must remain unproved")

    def test_disposition_inflation_rejected(self) -> None:
        found = self.mutate_json(
            "certificates/union_closed/MC-UC-WP04-QUAL-001.json",
            lambda value: value.update(disposition="certified_universal_theorem"),
        )
        self.assert_error(found, "disposition inflation")

    def test_unresolved_obligation_removal(self) -> None:
        found = self.mutate_json(
            "certificates/union_closed/MC-UC-WP04-QUAL-001.json",
            lambda value: value.update(unresolved_obligations=["UC-FRANKL"]),
        )
        self.assert_error(found, "unresolved universal obligations drift")

    def test_claim_boundary_weakening(self) -> None:
        found = self.mutate_json(
            "certificates/union_closed/MC-UC-WP04-QUAL-001.json",
            lambda value: value.update(claim_boundary="Restricted qualification only."),
        )
        self.assert_error(found, "claim boundary missing token")

    def test_route_state_rollback(self) -> None:
        def mutate(value: dict) -> None:
            next(item for item in value["routes"] if item["campaign_id"] == "UC-001")["intake_status"] = "ready"
        found = self.mutate_json("governance/certification_routes.json", mutate)
        self.assert_error(found, "route is not qualified")

    def test_route_output_drift(self) -> None:
        def mutate(value: dict) -> None:
            next(item for item in value["routes"] if item["campaign_id"] == "UC-001")["cert_output"]["digest"] = "0" * 40
        found = self.mutate_json("governance/certification_routes.json", mutate)
        self.assert_error(found, "route output identity drift")

    def test_route_blocker_removal(self) -> None:
        def mutate(value: dict) -> None:
            next(item for item in value["routes"] if item["campaign_id"] == "UC-001")["blockers"] = ["None"]
        found = self.mutate_json("governance/certification_routes.json", mutate)
        self.assert_error(found, "route blockers missing token")


if __name__ == "__main__":
    unittest.main()
