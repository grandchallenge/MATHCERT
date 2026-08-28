#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "ci/certification_route_state.py"
spec = importlib.util.spec_from_file_location("certification_route_state", MODULE_PATH)
assert spec and spec.loader
state = importlib.util.module_from_spec(spec)
spec.loader.exec_module(state)


class CertificationRouteStateTests(unittest.TestCase):
    def test_manifest_validates(self) -> None:
        self.assertEqual(state.validate_manifest(), [])

    def test_required_classes_are_exact(self) -> None:
        manifest = state.load_manifest()
        self.assertEqual(set(manifest["allowed_classes"]), state.ALLOWED)

    def test_historical_snapshot_identity_is_exact(self) -> None:
        row = state.classification_for(
            "ci/validate_openai_ten_proofs_sphere_packing_intake_successor.py"
        )
        self.assertIsNotNone(row)
        assert row is not None
        self.assertEqual(row["classification"], "HISTORICAL_SNAPSHOT")
        self.assertEqual(row["snapshot_commit"], "0a24c03689734cac54d940c506ff4be02e200e65")
        self.assertEqual(row["snapshot_blob"], "4d5c8e3f2b33d5148d98e7057991e167938c75bb")
        self.assertEqual(state.blob_at(row["snapshot_commit"]), row["snapshot_blob"])

    def test_compactness_adjudication_uses_authorized_epoch(self) -> None:
        expected_commit = "28db9aad66381ff4f8b68a48c18090fa5c5b843b"
        expected_blob = "aa460c1310a7c81b64b88013b7aa4cfdc056f37b"
        for consumer in (
            "ci/otp_compactness_adjudication_input_control.py",
            "ci/otp_compactness_adjudication_control.py",
        ):
            row = state.classification_for(consumer)
            self.assertIsNotNone(row)
            assert row is not None
            self.assertEqual(row["classification"], "HISTORICAL_SNAPSHOT")
            self.assertEqual(row["snapshot_commit"], expected_commit)
            self.assertEqual(row["snapshot_blob"], expected_blob)
            self.assertEqual(state.source_route_blob_pins(consumer), {expected_blob})

    def test_h_gapcvp_is_not_forced_into_legacy_snapshot(self) -> None:
        row = state.classification_for(
            "ci/validate_openai_ten_proofs_gapcvp_route_registration.py"
        )
        self.assertIsNotNone(row)
        assert row is not None
        self.assertEqual(row["classification"], "TRANSITION_STATE")
        self.assertNotIn("snapshot_commit", row)

    def test_live_registry_validator_is_current_state(self) -> None:
        row = state.classification_for("ci/validate_certification_routes.py")
        self.assertIsNotNone(row)
        assert row is not None
        self.assertEqual(row["classification"], "CURRENT_STATE")

    def test_sphere_packing_test_inherits_historical_state(self) -> None:
        row = state.effective_classification_for(
            "ci/test_openai_ten_proofs_sphere_packing_intake_successor.py"
        )
        self.assertIsNotNone(row)
        assert row is not None
        self.assertEqual(row["classification"], "HISTORICAL_SNAPSHOT")
        self.assertTrue(row.get("inherited"))
        self.assertEqual(row["snapshot_commit"], "0a24c03689734cac54d940c506ff4be02e200e65")
        self.assertEqual(row["snapshot_blob"], "4d5c8e3f2b33d5148d98e7057991e167938c75bb")

    def test_transitive_ambiguity_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "ci").mkdir()
            (root / "ci/historical.py").write_text("VALUE = 1\n", encoding="utf-8")
            (root / "ci/current.py").write_text("VALUE = 2\n", encoding="utf-8")
            (root / "ci/test_mixed.py").write_text(
                "import historical\nimport current\n", encoding="utf-8"
            )
            manifest = {
                "consumers": [
                    {
                        "path": "ci/historical.py",
                        "classification": "HISTORICAL_SNAPSHOT",
                        "snapshot_commit": "a",
                        "snapshot_blob": "b",
                    },
                    {"path": "ci/current.py", "classification": "CURRENT_STATE"},
                ]
            }
            with self.assertRaisesRegex(ValueError, "ambiguous transitive certification state"):
                state.effective_classification_for(
                    "ci/test_mixed.py", manifest, root=root
                )

    def test_source_route_blob_pin_is_extracted_exactly(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "ci").mkdir()
            expected = "a" * 40
            (root / "ci/a.py").write_text(
                "PINS={'governance/certification_routes.json':'" + expected + "'}\n",
                encoding="utf-8",
            )
            self.assertEqual(state.source_route_blob_pins("ci/a.py", root=root), {expected})

    def test_missing_historical_commit_fetches_exact_sha(self) -> None:
        commit = "a" * 40
        missing = subprocess.CompletedProcess(["git"], 1, "", "missing")
        fetched = subprocess.CompletedProcess(["git"], 0, "", "")
        present = subprocess.CompletedProcess(["git"], 0, "", "")
        verified = subprocess.CompletedProcess(["git"], 0, commit + "\n", "")
        with patch.object(state, "_git", side_effect=[missing, fetched, present, verified]) as git:
            state.ensure_commit_available(commit)
        self.assertEqual(
            git.call_args_list[1].args,
            ("fetch", "--no-tags", "--depth=1", "origin", commit),
        )

    def test_missing_historical_commit_fetch_failure_fails_closed(self) -> None:
        commit = "b" * 40
        missing = subprocess.CompletedProcess(["git"], 1, "", "missing")
        failed = subprocess.CompletedProcess(["git"], 1, "", "not advertised")
        with patch.object(state, "_git", side_effect=[missing, failed]):
            with self.assertRaisesRegex(ValueError, "historical snapshot commit unavailable"):
                state.ensure_commit_available(commit)

    def test_bash_override_wins(self) -> None:
        with patch.dict(os.environ, {"MATHCERT_REAL_BASH": "/governed/bash"}):
            self.assertEqual(state._resolve_real_bash(), "/governed/bash")

    def test_bash_fallback_rejects_route_state_shim(self) -> None:
        with patch.dict(os.environ, {}, clear=True), patch.object(
            state.Path, "is_file", return_value=False
        ), patch.object(
            state.shutil,
            "which",
            return_value="/tmp/mathcert-route-state-bin/bash",
        ):
            with self.assertRaisesRegex(RuntimeError, "no non-shim Bash"):
                state._resolve_real_bash()

    def test_powershell_fallback_is_supported(self) -> None:
        with patch.dict(os.environ, {}, clear=True), patch.object(
            state.shutil, "which", side_effect=["/opt/pwsh", None]
        ):
            self.assertEqual(state._resolve_real_powershell(), "/opt/pwsh")
        self.assertEqual(state._script_consumer(["-File", "ci/a.ps1"], ".ps1"), "ci/a.ps1")

    def test_synthetic_historical_head_replaces_only_route_blob(self) -> None:
        row = state.classification_for(
            "ci/validate_openai_ten_proofs_sphere_packing_intake_successor.py"
        )
        assert row is not None
        live_head, synthetic_head = state._synthetic_historical_head(row)
        self.assertEqual(state.blob_at(synthetic_head), row["snapshot_blob"])
        live_manifest_blob = state._git(
            "rev-parse", f"{live_head}:governance/certification_platform_lane.json"
        ).stdout.strip()
        synthetic_manifest_blob = state._git(
            "rev-parse", f"{synthetic_head}:governance/certification_platform_lane.json"
        ).stdout.strip()
        self.assertEqual(live_manifest_blob, synthetic_manifest_blob)

    def test_unknown_consumer_is_unclassified(self) -> None:
        self.assertIsNone(state.effective_classification_for("ci/does_not_exist.py"))


if __name__ == "__main__":
    unittest.main()
