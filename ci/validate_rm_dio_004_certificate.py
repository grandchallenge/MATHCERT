#!/usr/bin/env python3
"""Independently replay the bounded RM-DIO-004 MATHCERT certificate."""
from __future__ import annotations
import json
from math import isqrt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CERTIFICATE_PATH = ROOT / "certificates" / "exact" / "RM-DIO-004-Y-ABS-1000000.json"
EXPECTED_MATHFORGE_COMMIT = "bab7ae57f54601b49ad9fc870051095ad487c64a"
EXPECTED_MATHSOLVE_COMMIT = "dc232d903be7647416bf1fcfc0bf4c415d95e245"
EXPECTED_BLOBS = {"source_binding_blob_sha1": "f2d0f1f06abf76fce6ce9dba4092e6f174180703", "exact_screen_blob_sha1": "a39c05ef411b4aeb66e845aefb65b67f1f78bacc", "handoff_blob_sha1": "92cd330bfd59e75ab85e3da4d7201c2482c1cb81", "claim_ledger_blob_sha1": "771935d883d6478485c96a39afcb39f91d9d1580", "validator_blob_sha1": "ecb52561ce0f77438357951e43e58a437786b40c"}
LOWER, UPPER = -1_000_000, 1_000_000

def independent_replay(lower: int, upper: int) -> list[list[int]]:
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

def certificate_errors(certificate: dict) -> list[str]:
    domain, upstream = certificate.get("domain", {}), certificate.get("upstream", {})
    checks = {
        "wrong certificate id": certificate.get("certificate_id") == "MC-RM-DIO-004-Y-ABS-1000000",
        "wrong certification level": certificate.get("certification_level") == 2,
        "lower bound drift": domain.get("minimum") == LOWER,
        "upper bound drift": domain.get("maximum") == UPPER,
        "domain not inclusive": domain.get("inclusive") is True,
        "x must remain unrestricted": domain.get("x_restriction") == "none",
        "MATHFORGE commit drift": upstream.get("mathforge_protected_commit") == EXPECTED_MATHFORGE_COMMIT,
        "MATHSOLVE commit drift": upstream.get("mathsolve_protected_commit") == EXPECTED_MATHSOLVE_COMMIT,
        "solution count drift": certificate.get("solution_count") == len(certificate.get("solutions", [])),
        "verdict inflation or drift": certificate.get("verdict") == "CERTIFIED_BOUNDED_EXACT_COMPUTATION",
    }
    errors = [message for message, ok in checks.items() if not ok]
    errors.extend(f"upstream blob drift: {field}" for field, expected in EXPECTED_BLOBS.items() if upstream.get(field) != expected)
    exclusions = " ".join(certificate.get("excluded_claims", [])).lower()
    if "unrestricted" not in exclusions or "not certified" not in exclusions:
        errors.append("unbounded nonclaim is missing")
    if not errors and certificate.get("solutions") != independent_replay(LOWER, UPPER):
        errors.append("certificate solutions differ from independent exact replay")
    return errors

def load_certificate() -> dict:
    return json.loads(CERTIFICATE_PATH.read_text(encoding="utf-8"))

def main() -> int:
    errors = certificate_errors(load_certificate())
    if errors:
        print("\n".join(errors)); return 1
    print("MATHCERT Level-2 RM-DIO-004 certificate replayed: 12 solutions for |y| <= 1000000; unrestricted claim excluded")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
