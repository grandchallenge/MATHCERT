from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from math import isqrt
from pathlib import Path

import audit_certificate_coverage as module

RM_DIO_004_CERTIFICATE = module.ROOT / "certificates" / "exact" / "RM-DIO-004-Y-ABS-1000000.json"


def replay_rm_dio_004(lower: int, upper: int) -> list[list[int]]:
    found: list[list[int]] = []
    for y in range(lower, upper + 1):
        rhs = y**5 - y
        discriminant = 4 * rhs + 1
        if discriminant < 0:
            continue
        z = isqrt(discriminant)
        if z**2 != discriminant:
            continue
        for x in {(1 - z) // 2, (1 + z) // 2}:
            if 2 * x in {1 - z, 1 + z} and x**2 - x == rhs:
                found.append([x, y])
    return sorted(found)


def rm_dio_004_errors(certificate: dict) -> list[str]:
    lower, upper = -1_000_000, 1_000_000
    domain, upstream = certificate.get("domain", {}), certificate.get("upstream", {})
    expected_blobs = {"source_binding_blob_sha1": "f2d0f1f06abf76fce6ce9dba4092e6f174180703", "exact_screen_blob_sha1": "a39c05ef411b4aeb66e845aefb65b67f1f78bacc", "handoff_blob_sha1": "92cd330bfd59e75ab85e3da4d7201c2482c1cb81", "claim_ledger_blob_sha1": "771935d883d6478485c96a39afcb39f91d9d1580", "validator_blob_sha1": "ecb52561ce0f77438357951e43e58a437786b40c"}
    checks = {
        "wrong certificate id": certificate.get("certificate_id") == "MC-RM-DIO-004-Y-ABS-1000000",
        "wrong certification level": certificate.get("certification_level") == 2,
        "lower bound drift": domain.get("minimum") == lower,
        "upper bound drift": domain.get("maximum") == upper,
        "domain not inclusive": domain.get("inclusive") is True,
        "x must remain unrestricted": domain.get("x_restriction") == "none",
        "MATHFORGE commit drift": upstream.get("mathforge_protected_commit") == "bab7ae57f54601b49ad9fc870051095ad487c64a",
        "MATHSOLVE commit drift": upstream.get("mathsolve_protected_commit") == "dc232d903be7647416bf1fcfc0bf4c415d95e245",
        "solution count drift": certificate.get("solution_count") == len(certificate.get("solutions", [])),
        "verdict inflation or drift": certificate.get("verdict") == "CERTIFIED_BOUNDED_EXACT_COMPUTATION",
    }
    errors = [message for message, ok in checks.items() if not ok]
    errors.extend(f"upstream blob drift: {field}" for field, expected in expected_blobs.items() if upstream.get(field) != expected)
    exclusions = " ".join(certificate.get("excluded_claims", [])).lower()
    if "unrestricted" not in exclusions or "not certified" not in exclusions:
        errors.append("unbounded nonclaim is missing")
    if not errors and certificate.get("solutions") != replay_rm_dio_004(lower, upper):
        errors.append("certificate solutions differ from independent exact replay")
    return errors


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
        certificate = json.loads(RM_DIO_004_CERTIFICATE.read_text(encoding="utf-8"))
        self.assertEqual([], rm_dio_004_errors(certificate))

    def test_rm_dio_004_rejects_missing_solution(self) -> None:
        certificate = json.loads(RM_DIO_004_CERTIFICATE.read_text(encoding="utf-8"))
        certificate["solutions"].pop()
        certificate["solution_count"] -= 1
        self.assertTrue(rm_dio_004_errors(certificate))

    def test_rm_dio_004_rejects_bound_inflation(self) -> None:
        certificate = json.loads(RM_DIO_004_CERTIFICATE.read_text(encoding="utf-8"))
        certificate["domain"]["maximum"] += 1
        self.assertTrue(rm_dio_004_errors(certificate))

    def test_rm_dio_004_rejects_upstream_drift(self) -> None:
        certificate = json.loads(RM_DIO_004_CERTIFICATE.read_text(encoding="utf-8"))
        certificate["upstream"]["mathsolve_protected_commit"] = "0" * 40
        self.assertTrue(rm_dio_004_errors(certificate))

    def test_rm_dio_004_rejects_unbounded_claim_inflation(self) -> None:
        certificate = json.loads(RM_DIO_004_CERTIFICATE.read_text(encoding="utf-8"))
        certificate["excluded_claims"] = []
        self.assertTrue(rm_dio_004_errors(certificate))


if __name__ == "__main__":
    unittest.main()
