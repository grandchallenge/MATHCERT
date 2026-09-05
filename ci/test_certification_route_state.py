#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import os
import stat
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

    def test_compactness_adjudication_uses_distinct_stage_epochs(self) -> None:
        expected_blob = "aa460c1310a7c81b64b88013b7aa4cfdc056f37b"
        expected = {
            "ci/otp_compactness_adjudication_input_control.py": "28db9aad66381ff4f8b68a48c18090fa5c5b843b",
            "ci/otp_compactness_adjudication_control.py": "17c081e6a1dbde9716e9e41e9960a90d37b31fb7",
        }
        for consumer, expected_commit in expected.items():
            row = state.classification_for(consumer)
            self.assertIsNotNone(row)
            assert row is not None
            self.assertEqual(row["classification"], "HISTORICAL_SNAPSHOT")
            self.assertEqual(row["snapshot_commit"], expected_commit)
            self.assertEqual(row["snapshot_blob"], expected_blob)
            self.assertEqual(state.source_route_blob_pins(consumer), {expected_blob})

    def test_j2_stages_are_bound_to_their_distinct_protected_epochs(self) -> None:
        expected = {
            "ci/validate_otp_j2_scope_repair.py": (
                "2106840fe2daf8b2492f52473465f531e7e2ef21",
                "bc4640661443f1b3de213aaa82a333a4fdb6849b",
            ),
            "ci/validate_otp_j2_source_faithful_evidence.py": (
                "491ea27cd93a6d403be3b9cab9e77f44fe0cf056",
                "bc4640661443f1b3de213aaa82a333a4fdb6849b",
            ),
            "ci/validate_otp_j2_adjudication_input.py": (
                "f7cd8ee65996b32c8b97ba15d67e663df3b31f01",
                "eb2ad35f73ec1f7a29c7432aa9e5ad299116dbfe",
            ),
            "ci/validate_otp_j2_adjudication.py": (
                "15559390e2489ae73d872f389a9601c7412b77ed",
                "2d17473b4731aa9d9c630b1e7777ad4bd794d993",
            ),
        }
        for consumer, (commit, blob) in expected.items():
            row = state.classification_for(consumer)
            self.assertIsNotNone(row)
            assert row is not None
            self.assertEqual(row["classification"], "HISTORICAL_SNAPSHOT")
            self.assertEqual(row["snapshot_commit"], commit)
            self.assertEqual(row["snapshot_blob"], blob)
            self.assertEqual(state.blob_at(commit), blob)
        wrapper = state.classification_for("ci/run_otp_j2_adjudication_replay.sh")
        assert wrapper is not None
        self.assertEqual(wrapper["classification"], "CURRENT_STATE")

    def test_j2_input_mutation_test_uses_governed_semantic_override(self) -> None:
        self.assertIsNone(state.classification_for("ci/test_otp_j2_adjudication_input.py"))
        override = state.semantic_override_for("ci/test_otp_j2_adjudication_input.py")
        self.assertIsNotNone(override)
        assert override is not None
        self.assertEqual(override["classification"], "CURRENT_STATE")
        effective = state.effective_classification_for("ci/test_otp_j2_adjudication_input.py")
        self.assertIsNotNone(effective)
        assert effective is not None
        self.assertEqual(effective["classification"], "CURRENT_STATE")
        self.assertTrue(effective.get("semantic_override"))

    def test_successor_aware_adjudication_design_uses_bounded_historical_override(self) -> None:
        consumer = "ci/validate_openai_ten_proofs_adjudication_design_with_successors.py"
        self.assertIsNone(state.classification_for(consumer))
        override = state.semantic_override_for(consumer)
        self.assertIsNotNone(override)
        assert override is not None
        self.assertEqual(override["classification"], "HISTORICAL_SNAPSHOT")
        self.assertEqual(override["snapshot_commit"], "0a24c03689734cac54d940c506ff4be02e200e65")
        self.assertEqual(override["snapshot_blob"], "4d5c8e3f2b33d5148d98e7057991e167938c75bb")
        effective = state.effective_classification_for(consumer)
        self.assertIsNotNone(effective)
        assert effective is not None
        self.assertEqual(effective["classification"], "HISTORICAL_SNAPSHOT")
        self.assertTrue(effective.get("semantic_override"))

    def test_a_stages_are_bound_to_exact_protected_epochs(self) -> None:
        expected = {
            "ci/run_openai_ten_proofs_sphere_packing_replay.sh": (
                "54b883bb5c6ffaf099efd7270df3519a45b13038",
                "2d17473b4731aa9d9c630b1e7777ad4bd794d993",
            ),
            "ci/run_openai_ten_proofs_sphere_packing_replay_with_registration_successor.sh": (
                "99cfde542cdb044145f6620190dfb6ee9cd7a959",
                "4d5c8e3f2b33d5148d98e7057991e167938c75bb",
            ),
            "ci/validate_otp_a_sphere_packing_adjudication_input.py": (
                "9fe7f8e26c201b304342e2b1158515f1845a971a",
                "b9bb0dc9e18856f50a88162df37c20c034327439",
            ),
            "ci/run_otp_a_sphere_packing_adjudication_replay.sh": (
                "5c35035aab713573c905eeb05abf07a62667a6a2",
                "b9bb0dc9e18856f50a88162df37c20c034327439",
            ),
            "ci/validate_otp_a_sphere_packing_adjudication.py": (
                "05f0bd517c11187e852aedc36a966bedc345e061",
                "b9bb0dc9e18856f50a88162df37c20c034327439",
            ),
        }
        for consumer, (commit, blob) in expected.items():
            row = state.classification_for(consumer)
            self.assertIsNotNone(row)
            assert row is not None
            self.assertEqual(row["classification"], "HISTORICAL_SNAPSHOT")
            self.assertEqual(row["snapshot_commit"], commit)
            self.assertEqual(row["snapshot_blob"], blob)
            self.assertEqual(state.blob_at(commit), blob)

    def test_h_gapcvp_registration_uses_its_own_completed_epoch(self) -> None:
        row = state.classification_for(
            "ci/validate_openai_ten_proofs_gapcvp_route_registration.py"
        )
        self.assertIsNotNone(row)
        assert row is not None
        self.assertEqual(row["classification"], "HISTORICAL_SNAPSHOT")
        self.assertEqual(row["snapshot_commit"], "7907fbdfe716e6a083b6772b9b3ce9f469d34389")
        self.assertEqual(row["snapshot_blob"], "ffc95950e571efebe1c90a3e6d1bf279b37b71b1")
        self.assertEqual(state.blob_at(row["snapshot_commit"]), row["snapshot_blob"])
        source = (ROOT / row["path"]).read_text(encoding="utf-8")
        self.assertIn(f'EXPECTED_ROUTES_BLOB = "{row["snapshot_blob"]}"', source)
        inherited = state.effective_classification_for("ci/test_openai_ten_proofs_gapcvp_route_registration.py")
        self.assertIsNotNone(inherited)
        self.assertEqual(inherited["snapshot_commit"], row["snapshot_commit"])

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

    def test_indirect_protected_object_pin_is_extracted(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "ci").mkdir()
            expected = "a" * 40
            (root / "ci/a.py").write_text(
                "EXPECTED={'record_blob':'" + expected + "'}\n"
                "OBJECTS={'governance/result.json':EXPECTED['record_blob']}\n",
                encoding="utf-8",
            )
            self.assertEqual(
                state.source_object_pins("ci/a.py", root=root),
                {"governance/result.json": expected},
            )

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

    def test_synthetic_historical_head_uses_protected_objects_and_absence(self) -> None:
        row = state.classification_for("ci/otp_compactness_adjudication_control.py")
        assert row is not None
        live_head, synthetic_head = state._synthetic_historical_head(row)
        self.assertEqual(state.blob_at(synthetic_head), row["snapshot_blob"])
        contract = "governance/result_family_adjudication_contracts/OTP-J1-COMPACTNESS.json"
        self.assertEqual(
            state._tree_entry(synthetic_head, contract)[1],
            "4288cf2199603ffc90d897062a575a5865326d70",
        )
        certificate = "certificates/formal_sources/MC-OTP-J1-COMPACTNESS-001.json"
        self.assertIsNotNone(state._tree_entry(live_head, certificate))
        self.assertIsNone(state._tree_entry(synthetic_head, certificate))
        record = "governance/result_family_adjudications/OTP-J1-COMPACTNESS.json"
        self.assertEqual(state._tree_entry(synthetic_head, record), state._tree_entry(live_head, record))

    def _init_temp_repository(self, root: Path) -> tuple[str, str]:
        def git(*args: str) -> str:
            return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.email", "ci@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.name", "CI Test"], check=True)
        (root / "governance").mkdir()
        (root / "ci").mkdir()
        (root / "governance/certification_routes.json").write_text('{"routes":[]}\n', encoding="utf-8")
        (root / "ci/replay.sh").write_text("#!/usr/bin/env bash\necho ok\n", encoding="utf-8")
        os.chmod(root / "ci/replay.sh", 0o600)
        subprocess.run(["git", "-C", str(root), "add", "."], check=True)
        subprocess.run(["git", "-C", str(root), "commit", "-q", "-m", "fixture"], check=True)
        return git("rev-parse", "HEAD"), git("rev-parse", "HEAD:governance/certification_routes.json")

    @unittest.skipIf(os.name == "nt", "Git executable-bit semantics are Unix-only")
    def test_route_view_preserves_incoming_mode_only_change(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            commit, route_blob = self._init_temp_repository(root)
            replay = root / "ci/replay.sh"
            os.chmod(replay, 0o700)
            entry = {
                "path": "ci/replay.sh",
                "classification": "HISTORICAL_SNAPSHOT",
                "snapshot_commit": commit,
                "snapshot_blob": route_blob,
            }
            with patch.object(state, "ROOT", root):
                self.assertEqual(state._capture_mode_only_changes(label="test"), {"ci/replay.sh": True})
                with state.route_view(entry):
                    self.assertTrue(bool(replay.stat().st_mode & stat.S_IXUSR))
                self.assertTrue(bool(replay.stat().st_mode & stat.S_IXUSR))
                self.assertEqual(state._git("hash-object", "--", "ci/replay.sh").stdout.strip(), state._tree_entry("HEAD", "ci/replay.sh")[1])

    @unittest.skipIf(os.name == "nt", "Git executable-bit semantics are Unix-only")
    def test_route_view_retains_current_ci_content_while_projecting_state(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            commit, route_blob = self._init_temp_repository(root)
            replay = root / "ci/replay.sh"
            replay.write_text("#!/usr/bin/env bash\necho changed\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "ci/replay.sh"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-q", "-m", "new replay"], check=True)
            live_head = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
            os.chmod(replay, 0o700)
            old_entry = {
                "path": "ci/replay.sh",
                "classification": "HISTORICAL_SNAPSHOT",
                "snapshot_commit": commit,
                "snapshot_blob": route_blob,
            }
            with patch.object(state, "ROOT", root):
                with state.route_view(old_entry):
                    self.assertTrue(bool(replay.stat().st_mode & stat.S_IXUSR))
                    self.assertEqual(replay.read_text(encoding="utf-8"), "#!/usr/bin/env bash\necho changed\n")
                self.assertTrue(bool(replay.stat().st_mode & stat.S_IXUSR))
                self.assertEqual(state._git("rev-parse", "HEAD").stdout.strip(), live_head)

    def test_route_view_rejects_content_mutation_and_restores_live_content(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            commit, route_blob = self._init_temp_repository(root)
            replay = root / "ci/replay.sh"
            entry = {
                "path": "ci/replay.sh",
                "classification": "HISTORICAL_SNAPSHOT",
                "snapshot_commit": commit,
                "snapshot_blob": route_blob,
            }
            with patch.object(state, "ROOT", root):
                with self.assertRaisesRegex(RuntimeError, "forbids tracked content changes"):
                    with state.route_view(entry):
                        replay.write_text("mutated\n", encoding="utf-8")
                self.assertEqual(replay.read_text(encoding="utf-8"), "#!/usr/bin/env bash\necho ok\n")
                self.assertEqual(state._git("rev-parse", "HEAD").stdout.strip(), commit)

    def test_unknown_consumer_is_unclassified(self) -> None:
        self.assertIsNone(state.effective_classification_for("ci/does_not_exist.py"))


if __name__ == "__main__":
    unittest.main()
