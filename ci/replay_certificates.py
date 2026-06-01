#!/usr/bin/env python3
"""Independently replay the bounded union-closed audit certificate."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
COORDINATOR_ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = PACKAGE_ROOT / "certificates" / "exact" / "union_closed_n_le_4.json"
CONVENTION = (
    "raw union-closed counts include the empty family; Frankl-facing counts include "
    "only nontrivial families with nonempty support"
)


def is_union_closed(mask: int, subsets: range) -> bool:
    members = [value for value in subsets if mask & (1 << value)]
    return all(mask & (1 << (left | right)) for left in members for right in members)


def is_nontrivial(mask: int, subsets: range) -> bool:
    return any(value != 0 and mask & (1 << value) for value in subsets)


def frankl_holds(mask: int, n: int, subsets: range) -> bool:
    members = [value for value in subsets if mask & (1 << value)]
    return any(
        2 * sum(1 for value in members if value & (1 << element)) >= len(members)
        for element in range(n)
    )


def replay(n: int) -> dict[str, int]:
    subsets = range(1 << n)
    raw = nontrivial = violations = 0
    for mask in range(1 << (1 << n)):
        if not is_union_closed(mask, subsets):
            continue
        raw += 1
        if is_nontrivial(mask, subsets):
            nontrivial += 1
            if not frankl_holds(mask, n, subsets):
                violations += 1
    return {
        "universe_size": n,
        "raw_union_closed_families": raw,
        "nontrivial_union_closed_families": nontrivial,
        "frankl_violations": violations,
    }


def main() -> int:
    certificate = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    if certificate["counting_convention"] != CONVENTION:
        raise ValueError("certificate counting convention is not canonical")
    audit = COORDINATOR_ROOT / certificate["source_audit"]
    expected_digest = certificate["source_audit_sha256"]
    if not audit.exists():
        audit = PACKAGE_ROOT / certificate["source_audit_snapshot"]
        expected_digest = certificate["source_audit_snapshot_sha256"]
    digest = hashlib.sha256(audit.read_bytes()).hexdigest()
    if digest != expected_digest:
        raise ValueError("source audit hash does not match certificate")
    expected = [replay(n) for n in range(5)]
    if certificate["results"] != expected:
        raise ValueError(f"certificate mismatch\nexpected={expected}\nactual={certificate['results']}")
    if any(result["frankl_violations"] for result in expected):
        raise ValueError("Frankl violation found in bounded replay")
    print("Replayed union-closed certificate for n <= 4: no nontrivial violations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
