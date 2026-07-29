from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import check_formal_trust as module


class FormalTrustTests(unittest.TestCase):
    def build_root(self, lean: str, declarations: list[dict] | None = None) -> Path:
        root = Path(tempfile.mkdtemp())
        (root / "MathCert").mkdir()
        (root / "governance").mkdir()
        (root / "MathCert" / "Fixture.lean").write_text(lean, encoding="utf-8")
        payload = {
            "schema_version": "1.0.0",
            "registry_id": "MC-FORMAL-TRUST-ALLOWLIST",
            "declarations": declarations or [],
        }
        (root / "governance" / "formal_trust_allowlist.json").write_text(
            json.dumps(payload, indent=2) + "\n", encoding="utf-8"
        )
        return root

    def test_current_repository_passes(self) -> None:
        self.assertEqual([], module.errors())

    def test_sorry_fails(self) -> None:
        root = self.build_root("theorem bad : True := by\n  sorry\n")
        self.assertTrue(any("proof placeholder" in item for item in module.errors(root)))

    def test_unregistered_axiom_fails(self) -> None:
        root = self.build_root("axiom ImportedFact : True\n")
        self.assertTrue(any("unregistered axiom" in item for item in module.errors(root)))

    def test_registered_axiom_passes(self) -> None:
        record = {
            "kind": "axiom",
            "name": "ImportedFact",
            "source_id": "SRC-001",
            "justification": "Visible imported theorem boundary.",
            "review_issue": "https://github.com/grandchallenge/MATHCERT/issues/31",
        }
        root = self.build_root("axiom ImportedFact : True\n", [record])
        self.assertEqual([], module.errors(root))


if __name__ == "__main__":
    unittest.main()
