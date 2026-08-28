#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "ci/check_certification_route_state_consumers.py"
spec = importlib.util.spec_from_file_location("check_certification_route_state_consumers", MODULE_PATH)
assert spec and spec.loader
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class CertificationRouteConsumerGateTests(unittest.TestCase):
    def test_repository_baseline(self) -> None:
        self.assertEqual(gate.validation_errors(), [])

    def test_unclassified_direct_consumer_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "ci").mkdir()
            (root / "governance").mkdir()
            (root / "ci/a.py").write_text('PATH = "governance/certification_routes.json"\n', encoding="utf-8")
            mp = root / "governance/certification_route_state_consumers.json"
            mp.write_text(json.dumps({"consumers": []}), encoding="utf-8")
            errors = gate.validation_errors(root, mp, check_git=False)
            self.assertTrue(any("unclassified direct" in e for e in errors))

    def test_transitive_consumer_inherits_one_state(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "ci").mkdir()
            (root / "governance").mkdir()
            (root / "ci/a.py").write_text('PATH = "governance/certification_routes.json"\n', encoding="utf-8")
            (root / "ci/test_a.py").write_text("import a\n", encoding="utf-8")
            mp = root / "governance/certification_route_state_consumers.json"
            mp.write_text(
                json.dumps(
                    {
                        "consumers": [
                            {"path": "ci/a.py", "classification": "CURRENT_STATE"}
                        ]
                    }
                ),
                encoding="utf-8",
            )
            self.assertEqual(gate.validation_errors(root, mp, check_git=False), [])
            direct, closure, workflow = gate.coverage_counts(root, mp)
            self.assertEqual(direct, 1)
            self.assertEqual(closure, 2)
            self.assertEqual(workflow, 0)

    def test_ambiguous_transitive_consumer_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "ci").mkdir()
            (root / "governance").mkdir()
            (root / "ci/a.py").write_text('PATH = "governance/certification_routes.json"\n', encoding="utf-8")
            (root / "ci/b.py").write_text('PATH = "governance/certification_routes.json"\n', encoding="utf-8")
            (root / "ci/test_ab.py").write_text("import a\nimport b\n", encoding="utf-8")
            mp = root / "governance/certification_route_state_consumers.json"
            mp.write_text(
                json.dumps(
                    {
                        "consumers": [
                            {
                                "path": "ci/a.py",
                                "classification": "HISTORICAL_SNAPSHOT",
                                "snapshot_commit": "a",
                                "snapshot_blob": "b",
                            },
                            {"path": "ci/b.py", "classification": "CURRENT_STATE"},
                        ]
                    }
                ),
                encoding="utf-8",
            )
            errors = gate.validation_errors(root, mp, check_git=False)
            self.assertTrue(any("ambiguous transitive certification state" in e for e in errors))

    def test_stale_classification_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "ci").mkdir()
            (root / "governance").mkdir()
            (root / "ci/a.py").write_text("print('x')\n", encoding="utf-8")
            mp = root / "governance/certification_route_state_consumers.json"
            mp.write_text(json.dumps({"consumers": [{"path":"ci/a.py","classification":"INVARIANT"}]}), encoding="utf-8")
            errors = gate.validation_errors(root, mp, check_git=False)
            self.assertTrue(any("stale classification" in e for e in errors))

    def test_historical_consumer_requires_snapshot_identity(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "ci").mkdir()
            (root / "governance").mkdir()
            (root / "ci/a.py").write_text('PATH = "governance/certification_routes.json"\n', encoding="utf-8")
            mp = root / "governance/certification_route_state_consumers.json"
            mp.write_text(json.dumps({"consumers": [{"path":"ci/a.py","classification":"HISTORICAL_SNAPSHOT"}]}), encoding="utf-8")
            errors = gate.validation_errors(root, mp, check_git=False)
            self.assertTrue(any("missing snapshot_commit" in e for e in errors))
            self.assertTrue(any("missing snapshot_blob" in e for e in errors))

    def test_unknown_class_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "ci").mkdir()
            (root / "governance").mkdir()
            (root / "ci/a.py").write_text('PATH = "governance/certification_routes.json"\n', encoding="utf-8")
            mp = root / "governance/certification_route_state_consumers.json"
            mp.write_text(json.dumps({"consumers": [{"path":"ci/a.py","classification":"MAGIC"}]}), encoding="utf-8")
            errors = gate.validation_errors(root, mp, check_git=False)
            self.assertTrue(any("unknown classification" in e for e in errors))

    def _workflow_fixture(self, td: str, run: str) -> tuple[Path, Path]:
        root = Path(td)
        (root / "ci").mkdir()
        (root / "governance").mkdir()
        (root / ".github/workflows").mkdir(parents=True)
        (root / "ci/a.py").write_text(
            'PATH = "governance/certification_routes.json"\n', encoding="utf-8"
        )
        (root / ".github/workflows/test.yml").write_text(
            "jobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n"
            f"      - run: {run}\n",
            encoding="utf-8",
        )
        mp = root / "governance/certification_route_state_consumers.json"
        mp.write_text(
            json.dumps(
                {
                    "consumers": [
                        {
                            "path": "ci/a.py",
                            "classification": "HISTORICAL_SNAPSHOT",
                            "snapshot_commit": "a",
                            "snapshot_blob": "b",
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        return root, mp

    def _script_workflow_fixture(
        self, td: str, *, suffix: str, run: str
    ) -> tuple[Path, Path]:
        root = Path(td)
        (root / "ci").mkdir()
        (root / "governance").mkdir()
        (root / ".github/workflows").mkdir(parents=True)
        consumer = f"ci/a{suffix}"
        (root / consumer).write_text(
            'PATH="governance/certification_routes.json"\n', encoding="utf-8"
        )
        (root / ".github/workflows/test.yml").write_text(
            "jobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n"
            f"      - run: {run}\n",
            encoding="utf-8",
        )
        mp = root / "governance/certification_route_state_consumers.json"
        mp.write_text(
            json.dumps(
                {
                    "consumers": [
                        {
                            "path": consumer,
                            "classification": "HISTORICAL_SNAPSHOT",
                            "snapshot_commit": "a",
                            "snapshot_blob": "b",
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        return root, mp

    def test_direct_historical_workflow_invocation_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root, mp = self._workflow_fixture(td, "python ci/a.py")
            errors = gate.validation_errors(root, mp, check_git=False)
            self.assertIn(
                "workflow historical certification-route consumer bypasses state executor: "
                ".github/workflows/test.yml: ci/a.py",
                errors,
            )

    def test_unittest_historical_workflow_invocation_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root, mp = self._workflow_fixture(td, "python -m unittest ci/a.py -v")
            errors = gate.validation_errors(root, mp, check_git=False)
            self.assertIn(
                "workflow historical certification-route consumer bypasses state executor: "
                ".github/workflows/test.yml: ci/a.py",
                errors,
            )

    def test_wrapped_historical_workflow_invocation_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root, mp = self._workflow_fixture(
                td, "python ci/certification_route_state.py exec ci/a.py"
            )
            self.assertEqual(gate.validation_errors(root, mp, check_git=False), [])
            direct, closure, workflow = gate.coverage_counts(root, mp)
            self.assertEqual((direct, closure, workflow), (1, 1, 1))

    def test_direct_historical_shell_workflow_invocation_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root, mp = self._script_workflow_fixture(td, suffix=".sh", run="ci/a.sh")
            errors = gate.validation_errors(root, mp, check_git=False)
            self.assertTrue(any(".github/workflows/test.yml: ci/a.sh" in e for e in errors))

    def test_bash_historical_shell_workflow_invocation_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root, mp = self._script_workflow_fixture(td, suffix=".sh", run="bash ci/a.sh")
            errors = gate.validation_errors(root, mp, check_git=False)
            self.assertTrue(any(".github/workflows/test.yml: ci/a.sh" in e for e in errors))

    def test_wrapped_historical_shell_workflow_invocation_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root, mp = self._script_workflow_fixture(
                td,
                suffix=".sh",
                run="python ci/certification_route_state.py exec-bash ci/a.sh",
            )
            self.assertEqual(gate.validation_errors(root, mp, check_git=False), [])

    def test_direct_historical_powershell_workflow_invocation_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root, mp = self._script_workflow_fixture(
                td, suffix=".ps1", run="pwsh -File ci/a.ps1"
            )
            errors = gate.validation_errors(root, mp, check_git=False)
            self.assertTrue(any(".github/workflows/test.yml: ci/a.ps1" in e for e in errors))

    def test_current_state_workflow_invocation_may_run_live(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root, mp = self._workflow_fixture(td, "python ci/a.py")
            payload = json.loads(mp.read_text(encoding="utf-8"))
            payload["consumers"][0] = {
                "path": "ci/a.py",
                "classification": "CURRENT_STATE",
            }
            mp.write_text(json.dumps(payload), encoding="utf-8")
            self.assertEqual(gate.validation_errors(root, mp, check_git=False), [])

    def test_yaml_extension_is_covered(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root, mp = self._workflow_fixture(td, "python ci/a.py")
            source = root / ".github/workflows/test.yml"
            target = root / ".github/workflows/test.yaml"
            source.rename(target)
            errors = gate.validation_errors(root, mp, check_git=False)
            self.assertTrue(any(".github/workflows/test.yaml: ci/a.py" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
