#!/usr/bin/env python3
"""Independently replay exact finite certificates."""
from __future__ import annotations

import hashlib
import json
from itertools import permutations
from math import isqrt
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
COORDINATOR_ROOT = Path(__file__).resolve().parents[2]
UNION_CLOSED_CERTIFICATE = PACKAGE_ROOT / "certificates" / "exact" / "union_closed_n_le_4.json"
FINITE_LATTICE_CERTIFICATE = PACKAGE_ROOT / "certificates" / "exact" / "finite_lattices_4_to_7.json"
RM_DIO_004_CERTIFICATE = PACKAGE_ROOT / "certificates" / "exact" / "RM-DIO-004-Y-ABS-1000000.json"
UNION_CLOSED_CONVENTION = (
    "raw union-closed counts include the empty family; Frankl-facing counts include "
    "only nontrivial families with nonempty support"
)
FINITE_LATTICE_ENUMERATION = (
    "strict partial orders on {0,...,n-1} whose numeric labels form a linear extension; "
    "unlabeled counts are recovered by canonicalizing the reflexive order under all relabelings"
)
FINITE_LATTICE_IRREDUCIBILITY = (
    "doubly irreducible means exactly one lower cover and exactly one upper cover"
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


def validate_union_closed_certificate() -> None:
    certificate = json.loads(UNION_CLOSED_CERTIFICATE.read_text(encoding="utf-8"))
    if certificate["counting_convention"] != UNION_CLOSED_CONVENTION:
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


def relation_pairs(n: int) -> list[tuple[int, int]]:
    return [(i, j) for i in range(n) for j in range(i + 1, n)]


def relation_from_mask(n: int, pairs: list[tuple[int, int]], mask: int) -> list[int]:
    leq = [1 << i for i in range(n)]
    for bit, (i, j) in enumerate(pairs):
        if mask & (1 << bit):
            leq[i] |= 1 << j
    return leq


def is_transitive(leq: list[int]) -> bool:
    for i, upper_i in enumerate(leq):
        strict_upper = upper_i & ~(1 << i)
        while strict_upper:
            bit = strict_upper & -strict_upper
            j = bit.bit_length() - 1
            strict_upper -= bit
            if leq[j] & ~upper_i:
                return False
    return True


def lower_sets(n: int, leq: list[int]) -> list[int]:
    down = [0] * n
    for i, upper_i in enumerate(leq):
        bits = upper_i
        while bits:
            bit = bits & -bits
            j = bit.bit_length() - 1
            bits -= bit
            down[j] |= 1 << i
    return down


def is_lattice(n: int, leq: list[int], down: list[int]) -> bool:
    for a in range(n):
        for b in range(a, n):
            common_upper = leq[a] & leq[b]
            minimal_upper_count = 0
            bits = common_upper
            while bits:
                bit = bits & -bits
                u = bit.bit_length() - 1
                bits -= bit
                if down[u] & common_upper & ~(1 << u) == 0:
                    minimal_upper_count += 1
                    if minimal_upper_count > 1:
                        return False
            if minimal_upper_count != 1:
                return False

            common_lower = down[a] & down[b]
            maximal_lower_count = 0
            bits = common_lower
            while bits:
                bit = bits & -bits
                u = bit.bit_length() - 1
                bits -= bit
                if leq[u] & common_lower & ~(1 << u) == 0:
                    maximal_lower_count += 1
                    if maximal_lower_count > 1:
                        return False
            if maximal_lower_count != 1:
                return False
    return True


def doubly_irreducible_count(n: int, leq: list[int], down: list[int]) -> int:
    total = 0
    for x in range(n):
        lower_covers = 0
        lower = down[x] & ~(1 << x)
        bits = lower
        while bits:
            bit = bits & -bits
            y = bit.bit_length() - 1
            bits -= bit
            if leq[y] & lower & ~(1 << y) == 0:
                lower_covers += 1

        upper_covers = 0
        upper = leq[x] & ~(1 << x)
        bits = upper
        while bits:
            bit = bits & -bits
            y = bit.bit_length() - 1
            bits -= bit
            if down[y] & upper & ~(1 << y) == 0:
                upper_covers += 1

        if lower_covers == 1 and upper_covers == 1:
            total += 1
    return total


def canonical_relation(n: int, leq: list[int]) -> tuple[int, ...]:
    best: tuple[int, ...] | None = None
    for relabel in permutations(range(n)):
        rows = [0] * n
        for old_i, upper_i in enumerate(leq):
            new_i = relabel[old_i]
            row = 0
            bits = upper_i
            while bits:
                bit = bits & -bits
                old_j = bit.bit_length() - 1
                bits -= bit
                row |= 1 << relabel[old_j]
            rows[new_i] = row
        candidate = tuple(rows)
        if best is None or candidate < best:
            best = candidate
    assert best is not None
    return best


def replay_finite_lattices(n: int) -> dict[str, int]:
    pairs = relation_pairs(n)
    candidate_relation_masks = 1 << len(pairs)
    lattice_presentations = 0
    canonical_lattices: set[tuple[int, ...]] = set()
    minimum_doubly_irreducible = n
    violations = 0

    for mask in range(candidate_relation_masks):
        leq = relation_from_mask(n, pairs, mask)
        if not is_transitive(leq):
            continue
        down = lower_sets(n, leq)
        if not is_lattice(n, leq, down):
            continue

        lattice_presentations += 1
        canonical_lattices.add(canonical_relation(n, leq))
        doubly_irreducible = doubly_irreducible_count(n, leq, down)
        minimum_doubly_irreducible = min(minimum_doubly_irreducible, doubly_irreducible)
        if doubly_irreducible < 2:
            violations += 1

    return {
        "size": n,
        "candidate_relation_masks": candidate_relation_masks,
        "linear_extension_lattice_presentations": lattice_presentations,
        "unlabeled_lattice_count": len(canonical_lattices),
        "minimum_doubly_irreducible_elements": minimum_doubly_irreducible,
        "violating_lattice_presentations": violations,
    }


def validate_finite_lattice_certificate() -> None:
    certificate = json.loads(FINITE_LATTICE_CERTIFICATE.read_text(encoding="utf-8"))
    if certificate["enumeration_convention"] != FINITE_LATTICE_ENUMERATION:
        raise ValueError("finite-lattice enumeration convention is not canonical")
    if certificate["irreducibility_convention"] != FINITE_LATTICE_IRREDUCIBILITY:
        raise ValueError("finite-lattice irreducibility convention is not canonical")
    expected = [replay_finite_lattices(n) for n in range(4, 8)]
    if certificate["results"] != expected:
        raise ValueError(
            "finite-lattice certificate mismatch\n"
            f"expected={expected}\nactual={certificate['results']}"
        )
    if any(result["violating_lattice_presentations"] for result in expected):
        raise ValueError("finite lattice with fewer than two doubly irreducible elements found")
    print("Replayed finite-lattice certificate for sizes 4..7: no branch (i) violations")


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
    domain = certificate.get("domain", {})
    upstream = certificate.get("upstream", {})
    expected_blobs = {
        "source_binding_blob_sha1": "f2d0f1f06abf76fce6ce9dba4092e6f174180703",
        "exact_screen_blob_sha1": "a39c05ef411b4aeb66e845aefb65b67f1f78bacc",
        "handoff_blob_sha1": "92cd330bfd59e75ab85e3da4d7201c2482c1cb81",
        "claim_ledger_blob_sha1": "771935d883d6478485c96a39afcb39f91d9d1580",
        "validator_blob_sha1": "ecb52561ce0f77438357951e43e58a437786b40c",
    }
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


def validate_rm_dio_004_certificate() -> None:
    certificate = json.loads(RM_DIO_004_CERTIFICATE.read_text(encoding="utf-8"))
    errors = rm_dio_004_errors(certificate)
    if errors:
        raise ValueError("RM-DIO-004 certificate rejection: " + "; ".join(errors))
    print("Replayed RM-DIO-004 Level-2 certificate: 12 solutions for |y| <= 1000000; unrestricted claim excluded")


def main() -> int:
    validate_union_closed_certificate()
    validate_finite_lattice_certificate()
    validate_rm_dio_004_certificate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
