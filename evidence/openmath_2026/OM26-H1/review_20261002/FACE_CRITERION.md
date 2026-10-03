# H1-02 — exact triangular-face criterion

**Status:** `SOLVE_PROOF_COMPLETE__BOUNDED_FALSIFICATION_PASS__MATHCERT_HANDOFF_PREPARED`

Let A be a finite set of distinct straight lines. An arrangement vertex is a point incident with at least two nonparallel lines. On a line, a bounded segment between consecutive distinct arrangement vertices is an arrangement edge.

For three distinct lines Li, Lj, Lk, write pij = Li ∩ Lj, and similarly.

## Criterion

The three lines support a counted Kobon triangular face iff:

1. all three pairwise intersections exist;
2. the three pairwise intersections are distinct and noncollinear; and
3. each of the three side segments joins consecutive arrangement vertices on its supporting line.

Equivalently, counted triangular faces are exactly the nondegenerate 3-cycles of the arrangement graph.

## Proof

Face ⇒ 3-cycle. A counted triangular face has three distinct nonparallel support lines and nonzero area. If a side contained another arrangement vertex in its relative interior, the distinct line creating that vertex would cross the side and one local branch would enter the triangular interior, contradicting the uncrossed-interior rule. Hence each side is an arrangement edge.

3-cycle ⇒ face. Suppose the three side segments are arrangement edges. If another line crossed the open triangular interior, convexity forces it to meet the boundary in two endpoints. A crossing through the relative interior of a side creates an arrangement vertex inside an alleged arrangement edge, contradiction. If it enters through a triangle vertex, it must leave through the relative interior of the opposite side; it cannot leave through a second triangle vertex because the unique line through two triangle vertices is already the corresponding support line. Therefore no other line crosses the open interior.

Parallel lines are harmless unless chosen as support pairs, concurrence collapses vertices and is rejected by the nonzero-area condition, and a non-support line may touch a triangle vertex without entering the open interior.

## Independent oracle

For another line M with affine form fM and triangle vertices v1,v2,v3, M meets the open triangle interior iff the exact values fM(v1), fM(v2), fM(v3) contain both a strict positive and a strict negative value. `kobon_direct_oracle.py` implements this direct sign test and shares no arrangement-graph logic with `kobon_scorer.py`.

This is a Solve-level proof object; MATHCERT certification is a separate disposition.

## Tranche disposition

The proof survived the bounded executable falsification campaign in GitHub Actions run `36356017300`, job `108723788668`: 210 exhaustive subsets of an explicit degeneracy pool, 360 seeded random exact arrangements across `n=3..8`, the baseline, and both H1-06 candidates agreed between the arrangement-graph scorer and the independent direct-interior oracle. This is supporting defect evidence, not a substitute for the proof or MATHCERT disposition.
