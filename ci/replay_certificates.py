#!/usr/bin/env python3
"""Independently replay exact finite certificates."""
from __future__ import annotations

import hashlib
import json
from itertools import permutations
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
COORDINATOR_ROOT = Path(__file__).resolve().parents[2]
UNION_CLOSED_CERTIFICATE = PACKAGE_ROOT / "certificates" / "exact" / "union_closed_n_le_4.json"
FINITE_LATTICE_CERTIFICATE = PACKAGE_ROOT / "certificates" / "exact" / "finite_lattices_4_to_7.json"
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


def main() -> int:
    validate_union_closed_certificate()
    validate_finite_lattice_certificate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
