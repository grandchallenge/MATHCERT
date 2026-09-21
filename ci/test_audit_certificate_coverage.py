from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import audit_certificate_coverage as module
import replay_certificates as replay


class CertificateCoverageTests(unittest.TestCase):
    def build_root(self) -> Path:
        root = Path(tempfile.mkdtemp())
        shutil.copytree(module.ROOT / "governance", root / "governance")
        shutil.copytree(module.ROOT / "certificates", root / "certificates")
        (root / "ci").mkdir()
        data = json.loads(
            (root / "governance" / "ci_control_registry.json").read_text(encoding="utf-8")
        )
        for family in data["certificate_families"]:
            checker = family.get("checker")
            if checker:
                path = root / checker
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("# fixture\n", encoding="utf-8")
        return root

    def test_current_repository_passes(self) -> None:
        self.assertEqual([], module.errors())

    def test_unknown_exact_certificate_fails(self) -> None:
        root = self.build_root()
        path = root / "certificates" / "exact" / "unknown.json"
        path.write_text("{}\n", encoding="utf-8")
        self.assertTrue(any("no replay implementation" in item for item in module.errors(root)))

    def test_blocked_family_artifact_fails(self) -> None:
        root = self.build_root()
        path = root / "certificates" / "interval" / "unregistered.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}\n", encoding="utf-8")
        self.assertTrue(any("blocked certificate family" in item for item in module.errors(root)))

    def test_rm_dio_004_committed_certificate_replays(self) -> None:
        certificate = json.loads(replay.RM_DIO_004_CERTIFICATE.read_text(encoding="utf-8"))
        self.assertEqual([], replay.rm_dio_004_errors(certificate))

    def test_rm_dio_004_rejects_missing_solution(self) -> None:
        certificate = json.loads(replay.RM_DIO_004_CERTIFICATE.read_text(encoding="utf-8"))
        certificate["solutions"].pop()
        certificate["solution_count"] -= 1
        self.assertTrue(replay.rm_dio_004_errors(certificate))

    def test_rm_dio_004_rejects_bound_inflation(self) -> None:
        certificate = json.loads(replay.RM_DIO_004_CERTIFICATE.read_text(encoding="utf-8"))
        certificate["domain"]["maximum"] += 1
        self.assertTrue(replay.rm_dio_004_errors(certificate))

    def test_rm_dio_004_rejects_upstream_drift(self) -> None:
        certificate = json.loads(replay.RM_DIO_004_CERTIFICATE.read_text(encoding="utf-8"))
        certificate["upstream"]["mathsolve_protected_commit"] = "0" * 40
        self.assertTrue(replay.rm_dio_004_errors(certificate))

    def test_rm_dio_004_rejects_unbounded_claim_inflation(self) -> None:
        certificate = json.loads(replay.RM_DIO_004_CERTIFICATE.read_text(encoding="utf-8"))
        certificate["excluded_claims"] = []
        self.assertTrue(replay.rm_dio_004_errors(certificate))


if __name__ == "__main__":
    unittest.main()
