#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

import otp_full_formula_route_proposal_compat as compat
import validate_openai_ten_proofs_permanent_route_proposal as historical

ROOT = Path(__file__).resolve().parents[1]


class FullFormulaRouteProposalCompatibilityTests(unittest.TestCase):
    def test_successor_baseline(self):
        self.assertEqual(compat.successor_errors(ROOT, historical.PROPOSAL.parent), [])

    def test_historical_suite_under_frozen_view(self):
        spec = importlib.util.spec_from_file_location(
            "historical_permanent_route_proposal_tests",
            ROOT / "ci/test_openai_ten_proofs_permanent_route_proposal.py",
        )
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        suite = unittest.defaultTestLoader.loadTestsFromModule(module)
        with compat.historical_membership_view(historical.PROPOSAL.parent):
            result = unittest.TextTestRunner(verbosity=0).run(suite)
        self.assertTrue(result.wasSuccessful())

    def test_successor_target_drift_is_detected(self):
        successor = historical.PROPOSAL.parent / compat.SUCCESSOR_NAME
        original = successor.read_text(encoding="utf-8")
        self.assertIn("permanent_rational_formula_lower_bound", original)
        # The exact blob gate is the first-line defense against any mutation.
        self.assertEqual(compat.git_blob_sha1(successor), compat.EXPECTED_SUCCESSOR_BLOB)


if __name__ == "__main__":
    unittest.main()
