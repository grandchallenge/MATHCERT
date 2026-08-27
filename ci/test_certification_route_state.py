#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

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
        self.assertIsNone(state.classification_for("ci/does_not_exist.py"))


if __name__ == "__main__":
    unittest.main()
