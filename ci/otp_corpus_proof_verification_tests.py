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

    def test_protected_push_is_path_scoped_with_weekly_full_replay(self) -> None:
        workflow = (ROOT / ".github/workflows/otp-corpus-proof-verification.yml").read_text(
            encoding="utf-8"
        )
        push_block = workflow.split("  push:\n", 1)[1].split("  schedule:\n", 1)[0]
        self.assertIn("    paths:", push_block)
        self.assertIn('"ci/otp_corpus_proof_verification.py"', push_block)
        self.assertIn('cron: "43 3 * * 0"', workflow)
        self.assertIn("  workflow_dispatch:", workflow)
        routing = json.loads((ROOT / ".ghos-routing/workflows.json").read_text(encoding="utf-8"))
        entry = next(
            item
            for item in routing["workflows"]
            if item["path"] == ".github/workflows/otp-corpus-proof-verification.yml"
        )
        self.assertEqual(
            entry["observed_features"],
            ["AUTONOMOUS_WAKE", "OPAQUE_EXECUTION", "SCHEDULED"],
        )

    def test_shared_registry_does_not_directly_trigger_specialized_workflows(self) -> None:
        specialized = (
            "otp-h-gapcvp-cert-work-package.yml",
            "vgse-route-registration.yml",
        )
        offenders = []
        for name in specialized:
            path = ROOT / ".github/workflows" / name
            if '"governance/ci_control_registry.json"' in path.read_text(encoding="utf-8"):
                offenders.append(name)
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
