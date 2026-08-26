#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import shutil
import tempfile
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

    def test_independent_a_proposal_is_exact_pinned(self):
        proposal = historical.PROPOSAL.parent / compat.A_SPHERE_PACKING_NAME
        self.assertTrue(proposal.is_file())
        self.assertEqual(
            compat.git_blob_sha1(proposal),
            compat.EXPECTED_A_SPHERE_PACKING_BLOB,
        )

    def test_historical_view_hides_all_successors(self):
        with compat.historical_membership_view(historical.PROPOSAL.parent):
            members = sorted(p.name for p in historical.PROPOSAL.parent.glob("*.json"))
        self.assertEqual(members, ["OTP-C-PERMANENT.json"])

    def _copy_owned_surface(self, destination: Path) -> None:
        for name in [
            compat.A_SPHERE_PACKING_NAME,
            compat.HISTORICAL_PERMANENT_NAME,
            compat.FULL_FORMULA_NAME,
            compat.CIRCUIT_NAME,
        ]:
            shutil.copy2(historical.PROPOSAL.parent / name, destination / name)

    def test_unrelated_family_successor_is_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            proposal_dir = Path(tmp)
            self._copy_owned_surface(proposal_dir)
            (proposal_dir / "OTP-H-GAPCVP.json").write_text("{}\n", encoding="utf-8")
            self.assertEqual(compat.successor_errors(ROOT, proposal_dir), [])

    def test_unknown_permanent_successor_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            proposal_dir = Path(tmp)
            self._copy_owned_surface(proposal_dir)
            (proposal_dir / "OTP-C-PERMANENT-UNAUTHORIZED.json").write_text("{}\n", encoding="utf-8")
            errors = compat.successor_errors(ROOT, proposal_dir)
            self.assertTrue(any("unknown Permanent successor membership" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
