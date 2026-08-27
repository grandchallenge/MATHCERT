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


if __name__ == "__main__":
    unittest.main()
