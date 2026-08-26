from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import audit_ci_reachability as module


class CiReachabilityTests(unittest.TestCase):
    def build_root(self) -> Path:
        temp = Path(tempfile.mkdtemp())
        (temp / "ci").mkdir()
        (temp / "governance").mkdir()
        (temp / ".github" / "workflows").mkdir(parents=True)
        data = json.loads(
            (module.ROOT / "governance" / "ci_control_registry.json").read_text(encoding="utf-8")
        )
        (temp / "governance" / "ci_control_registry.json").write_text(
            json.dumps(data, indent=2) + "\n", encoding="utf-8"
        )
        for record in data["controls"]:
            path = temp / record["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# fixture\n", encoding="utf-8")
        for orchestrator in data["orchestrators"]:
            text = "\n".join(
                record["path"] for record in data["controls"] if record["mode"] == "direct"
            )
            text += (
                "\ncheck_certification_platform_lane.py --certification-scope"
                "\nFULL_ESTATE\nMATHCERT_CONTEXT_SKIP\n"
            )
            path = temp / orchestrator
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")

        platform = json.loads(
            (module.ROOT / module.PLATFORM_MANIFEST).read_text(encoding="utf-8")
        )
        (temp / module.PLATFORM_MANIFEST).write_text(
            json.dumps(platform, indent=2) + "\n", encoding="utf-8"
        )
        workflow_controls = [
            path
            for path in platform["lane_support_paths"]
            if Path(path).name.startswith(module.CANONICAL_PREFIXES)
        ]
        for relative in workflow_controls:
            path = temp / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# platform fixture\n", encoding="utf-8")

        workflow_mentions = "\n".join(f"      - run: python3 {path}" for path in workflow_controls)
        (temp / ".github" / "workflows" / "ci.yml").write_text(
            """name: Cert checks
on:
  workflow_dispatch:
permissions:
  contents: read
concurrency:
  group: fixture
  cancel-in-progress: true
jobs:
  certify:
    runs-on: ubuntu-24.04
    timeout-minutes: 45
    steps:
      - uses: actions/checkout@3333333333333333333333333333333333333333
      - uses: actions/setup-python@4444444444444444444444444444444444444444
        with:
          python-version: "3.13"
      - run: python -m pip install -r requirements-ci.txt
"""
            + workflow_mentions
            + "\n",
            encoding="utf-8",
        )
        return temp

    def test_current_repository_passes(self) -> None:
        self.assertEqual([], module.errors())

    def test_unregistered_canonical_control_fails(self) -> None:
        root = self.build_root()
        (root / "ci" / "validate_orphan.py").write_text("# orphan\n", encoding="utf-8")
        self.assertTrue(any("unregistered CI control" in item for item in module.errors(root)))

    def test_declared_platform_workflow_control_is_accepted(self) -> None:
        root = self.build_root()
        self.assertFalse(any("check_certification_platform_lane" in item for item in module.errors(root)))

    def test_declared_platform_workflow_control_must_be_reached(self) -> None:
        root = self.build_root()
        workflow = root / ".github" / "workflows" / "ci.yml"
        workflow.write_text(
            workflow.read_text(encoding="utf-8").replace(
                "      - run: python3 ci/check_certification_platform_lane.py\n", ""
            ),
            encoding="utf-8",
        )
        self.assertTrue(
            any(
                "platform workflow control is not reached" in item
                and "check_certification_platform_lane.py" in item
                for item in module.errors(root)
            )
        )

    def test_unregistered_historical_builder_is_not_promoted(self) -> None:
        root = self.build_root()
        (root / "ci" / "build_historical_candidate.py").write_text("# non-control utility\n", encoding="utf-8")
        self.assertFalse(any("build_historical_candidate" in item for item in module.errors(root)))

    def test_registered_producer_missing_fails(self) -> None:
        root = self.build_root()
        path = root / "ci" / "build_otp_compactness_construction_evidence.py"
        path.unlink()
        self.assertTrue(any("registered CI control is missing" in item and "build_otp_compactness" in item for item in module.errors(root)))

    def test_registered_verifier_missing_fails(self) -> None:
        root = self.build_root()
        path = root / "ci" / "verify_otp_compactness_construction_evidence.py"
        path.unlink()
        self.assertTrue(any("registered CI control is missing" in item and "verify_otp_compactness" in item for item in module.errors(root)))

    def test_omitted_direct_control_fails(self) -> None:
        root = self.build_root()
        shell = root / "ci" / "check_lean.sh"
        shell.write_text("", encoding="utf-8")
        self.assertTrue(any("not reached" in item for item in module.errors(root)))

    def test_context_scope_must_remain_in_both_orchestrators(self) -> None:
        root = self.build_root()
        powershell = root / "ci" / "check_lean.ps1"
        powershell.write_text(
            powershell.read_text(encoding="utf-8").replace(module.SCOPE_TOKEN, "removed-scope"),
            encoding="utf-8",
        )
        self.assertTrue(
            any(
                "lacks context-aware certification scope" in item and "check_lean.ps1" in item
                for item in module.errors(root)
            )
        )

    def test_full_estate_marker_must_remain_in_orchestrator(self) -> None:
        root = self.build_root()
        shell = root / "ci" / "check_lean.sh"
        shell.write_text(shell.read_text(encoding="utf-8").replace("FULL_ESTATE", "REMOVED"), encoding="utf-8")
        self.assertTrue(any("lacks fail-closed full-estate" in item for item in module.errors(root)))

    def test_manual_full_estate_entry_must_remain(self) -> None:
        root = self.build_root()
        workflow = root / ".github" / "workflows" / "ci.yml"
        workflow.write_text(workflow.read_text(encoding="utf-8").replace("workflow_dispatch:", "removed_dispatch:"), encoding="utf-8")
        self.assertTrue(any("workflow_dispatch:" in item for item in module.errors(root)))

    def test_mutable_action_fails(self) -> None:
        root = self.build_root()
        workflow = root / ".github" / "workflows" / "ci.yml"
        workflow.write_text(
            workflow.read_text(encoding="utf-8").replace(
                "actions/checkout@3333333333333333333333333333333333333333",
                "actions/checkout@v7",
            ),
            encoding="utf-8",
        )
        self.assertTrue(any("not pinned" in item for item in module.errors(root)))


if __name__ == "__main__":
    unittest.main()
