# OM26-H1 independent Cert bootstrap

**Tracker:** `grandchallenge/MATHCERT#341`  
**Parent:** `grandchallenge/MATHCERT#339`  
**State:** `PENDING_FRESH_NON_AUTHORING_EXECUTOR`

## Exact subject

Certify or qualify only the two claims admitted in `INTAKE.json`:

1. `OM26-H1-THM-001`: the arrangement-edge / nondegenerate-3-cycle characterization of counted triangular faces.
2. `OM26-H1-CON-001`: the exact local candidate snapshot has 86 counted triangular faces for `n=18`.

## Independence firewall

The system that created the candidate and the existing Solve scorers/replay evidence must not issue the final Cert disposition. A fresh non-authoring executor must reconstruct the verification independently.

Do not import or execute the producer's `kobon_scorer.py`, `kobon_direct_oracle.py`, `search_tranche.py`, or producer tests. They may be inspected later as provenance or corroborating evidence only after the independent verification path exists.

## Required execution order

1. Bind to the exact Forge source lock and exact Solve protected commit recorded in `INTAKE.json`.
2. Verify the local candidate snapshot byte identity: upstream Git blob `17f8355b...` and SHA-256 `05a5f519...ad11d5`.
3. From the locked hill statement alone, independently define the counted-face predicate using exact rational/integer geometry.
4. Replay the candidate without executing any producer code. Export the exact count and the supporting-line triples.
5. Review `FACE_CRITERION.md` only after the independent predicate is fixed. Check both directions and the allowed degeneracies.
6. Record semantic-fidelity hazards and any counterexample found.
7. Issue separate dispositions for the construction claim and theorem claim. Do not collapse them.

## Stop conditions

Stop without certification if the candidate identity differs, the independent count is not 86, the theorem proof misses an allowed degeneracy, or the independent predicate depends on an unstated geometric tolerance.

## Claim boundary

Do not decide best-known status, optimality, novelty, priority, official AutoLab acceptance, or publication readiness.
