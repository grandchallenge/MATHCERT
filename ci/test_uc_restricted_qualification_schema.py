from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import validate_uc_restricted_qualification_schema as module


class UCRestrictedQualificationSchemaTests(unittest.TestCase):
    def errors(self, mutator) -> list[str]:
        certificate = module.load(module.CERT_PATH)
        mutator(certificate)
        handle = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        with handle:
            json.dump(certificate, handle, indent=2)
            handle.write("\n")
        path = Path(handle.name)
        try:
            return module.errors(path)
        finally:
            path.unlink(missing_ok=True)

    def test_current_certificate_passes(self) -> None:
        self.assertEqual([], module.errors())

    def test_top_level_extension_rejected(self) -> None:
        found = self.errors(lambda value: value.update(extra=True))
        self.assertTrue(any("Additional properties" in item for item in found), found)

    def test_nested_extension_rejected(self) -> None:
        def mutate(value: dict) -> None:
            value["finite_range"]["extra"] = True
        found = self.errors(mutate)
        self.assertTrue(any("Additional properties" in item for item in found), found)

    def test_universal_proof_promotion_rejected(self) -> None:
        found = self.errors(lambda value: value.update(mathematical_target_proved=True))
        self.assertTrue(any("False was expected" in item for item in found), found)

    def test_finite_range_inflation_rejected(self) -> None:
        def mutate(value: dict) -> None:
            value["finite_range"]["max_universe_size"] = 5
        found = self.errors(mutate)
        self.assertTrue(any("4 was expected" in item for item in found), found)

    def test_unknown_claim_rejected(self) -> None:
        def mutate(value: dict) -> None:
            value["qualified_claims"][0]["claim_id"] = "UC-FRANKL"
        found = self.errors(mutate)
        self.assertTrue(any("is not one of" in item for item in found), found)


if __name__ == "__main__":
    unittest.main()
