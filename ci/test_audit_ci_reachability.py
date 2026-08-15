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
            path = temp / orchestrator
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text + "\n", encoding="utf-8")
        (temp / ".github" / "workflows" / "ci.yml").write_text(
            """name: Cert checks
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
""",
            encoding="utf-8",
        )
        return temp

    def test_current_repository_passes(self) -> None:
        self.assertEqual([], module.errors())

    def test_unregistered_canonical_control_fails(self) -> None:
        root = self.build_root()
        (root / "ci" / "validate_orphan.py").write_text("# orphan\n", encoding="utf-8")
        self.assertTrue(any("unregistered CI control" in item for item in module.errors(root)))

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
