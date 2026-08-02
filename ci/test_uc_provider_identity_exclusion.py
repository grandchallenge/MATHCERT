from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import validate_uc_provider_identity_exclusion as module


class UCProviderIdentityExclusionTests(unittest.TestCase):
    def errors(self, mutator) -> list[str]:
        record = module.load(module.RECORD_PATH)
        mutator(record)
        handle = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        with handle:
            json.dump(record, handle, indent=2)
            handle.write("\n")
        path = Path(handle.name)
        try:
            return module.errors(path)
        finally:
            path.unlink(missing_ok=True)

    def test_current_record_passes(self) -> None:
        self.assertEqual([], module.errors())

    def test_extension_rejected(self) -> None:
        found = self.errors(lambda value: value.update(extra=True))
        self.assertTrue(any("Additional properties" in item for item in found), found)

    def test_digest_mismatch_cannot_be_erased(self) -> None:
        def mutate(value: dict) -> None:
            value["excluded_artifact"]["observed_digest"] = value["excluded_artifact"]["recorded_digest"]
        found = self.errors(mutate)
        self.assertTrue(any("real identity mismatch" in item or "607e494" in item for item in found), found)

    def test_exclusion_path_cannot_drift(self) -> None:
        def mutate(value: dict) -> None:
            value["excluded_artifact"]["path"] = "README.md"
        found = self.errors(mutate)
        self.assertTrue(any("was expected" in item for item in found), found)

    def test_correction_history_cannot_be_removed(self) -> None:
        found = self.errors(lambda value: value.pop("correction_history"))
        self.assertTrue(any("required property" in item for item in found), found)

    def test_corrected_recorded_digest_must_match_live_value(self) -> None:
        def mutate(value: dict) -> None:
            value["correction_history"]["corrected_recorded_digest"] = "0" * 40
        found = self.errors(mutate)
        self.assertTrue(any("corrected recorded digest" in item or "was expected" in item for item in found), found)

    def test_corrected_observed_digest_must_match_live_value(self) -> None:
        def mutate(value: dict) -> None:
            value["correction_history"]["corrected_observed_digest"] = "0" * 40
        found = self.errors(mutate)
        self.assertTrue(any("corrected observed digest" in item or "was expected" in item for item in found), found)

    def test_superseded_recorded_digest_must_differ(self) -> None:
        def mutate(value: dict) -> None:
            value["correction_history"]["superseded_recorded_digest"] = value["excluded_artifact"]["recorded_digest"]
        found = self.errors(mutate)
        self.assertTrue(any("superseded recorded digest" in item or "was expected" in item for item in found), found)

    def test_superseded_observed_digest_must_differ(self) -> None:
        def mutate(value: dict) -> None:
            value["correction_history"]["superseded_observed_digest"] = value["excluded_artifact"]["observed_digest"]
        found = self.errors(mutate)
        self.assertTrue(any("superseded observed digest" in item or "was expected" in item for item in found), found)

    def test_qualification_cannot_change(self) -> None:
        def mutate(value: dict) -> None:
            value["correction_history"]["qualification_unchanged"] = False
        found = self.errors(mutate)
        self.assertTrue(any("cannot alter the qualification" in item or "True was expected" in item for item in found), found)

    def test_repair_cannot_be_optional(self) -> None:
        def mutate(value: dict) -> None:
            value["downstream_repair"]["required"] = False
        found = self.errors(mutate)
        self.assertTrue(any("True was expected" in item or "must remain mandatory" in item for item in found), found)

    def test_closure_gate_cannot_be_removed(self) -> None:
        def mutate(value: dict) -> None:
            value["downstream_repair"]["closure_blocked_until_repair"] = False
        found = self.errors(mutate)
        self.assertTrue(any("True was expected" in item or "closure-blocking" in item for item in found), found)

    def test_repair_target_cannot_drift(self) -> None:
        def mutate(value: dict) -> None:
            value["downstream_repair"]["issue"] = 2
        found = self.errors(mutate)
        self.assertTrue(any("1 was expected" in item or "repair target drift" in item for item in found), found)

    def test_record_cannot_close_early(self) -> None:
        found = self.errors(lambda value: value.update(status="repaired"))
        self.assertTrue(any("open_repair_required" in item or "cannot close" in item for item in found), found)

    def test_boundary_cannot_be_weakened(self) -> None:
        found = self.errors(lambda value: value.update(claim_boundary="No effect."))
        self.assertTrue(any("boundary missing token" in item for item in found), found)


if __name__ == "__main__":
    unittest.main()
