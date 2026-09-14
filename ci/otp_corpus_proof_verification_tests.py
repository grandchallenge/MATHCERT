#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "ci/otp_corpus_proof_verification.py"
SPEC = importlib.util.spec_from_file_location("otp_corpus_validator", MODULE_PATH)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class CorpusVerificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(VALIDATOR.RECORD.read_text(encoding="utf-8"))

    def errors_for(self, mutate) -> list[str]:
        candidate = copy.deepcopy(self.record)
        mutate(candidate)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "candidate.json"
            path.write_text(json.dumps(candidate), encoding="utf-8")
            return VALIDATOR.validate(path)

    def test_protected_record_accepts(self) -> None:
        self.assertEqual(VALIDATOR.validate(), [])

    def test_false_proof_status_rejects(self) -> None:
        errors = self.errors_for(lambda r: r["conclusion"].__setitem__("supplied_lean_formalizations_verified", False))
        self.assertTrue(any("supplied_lean_formalizations_verified" in error or "weakened" in error for error in errors))

    def test_missing_result_rejects(self) -> None:
        errors = self.errors_for(lambda r: r["results"].pop())
        self.assertTrue(any("results" in error or "ordinals" in error or "coverage" in error for error in errors))

    def test_module_identity_drift_rejects(self) -> None:
        errors = self.errors_for(lambda r: r["results"][0].__setitem__("module_blob", "0" * 40))
        self.assertTrue(any("module identity drift" in error for error in errors))

    def test_pdf_equivalence_overclaim_rejects(self) -> None:
        errors = self.errors_for(lambda r: r["limitations"].__setitem__("pdf_exposition_line_by_line_equivalence", "established"))
        self.assertTrue(any("pdf_exposition" in error or "PDF exposition" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
