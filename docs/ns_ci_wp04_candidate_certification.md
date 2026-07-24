# NS-CI-WP04 — Candidate certification feasibility

## Status

- Campaign: `NS-CI-001`
- Programme tracker: `grandchallenge/MATH-PROGRAMME#61`
- MATHCERT tracker: `grandchallenge/MATHCERT#21`
- State: `CANDIDATE_SCALING_AUDIT_ACTIVE`
- Open universal estimate: explicitly out of scope

## Purpose

Audit the scaling, statement hygiene, and formalization feasibility of each restricted-target candidate. MATHCERT certifies algebraic and logical substrate only; imported PDE theorems remain visible provenance-bearing interfaces.

## Required checks per candidate

1. exact Navier–Stokes scaling of every field, norm, and added hypothesis;
2. mixed-norm exponent order and interval rescaling;
3. whether constants are uniform under cutoff, smoothing, or approximation parameters;
4. whether the hypothesis is independently stated or hides the desired regularity;
5. exact imported theorem fields and source identifiers;
6. separation of kernel-checkable algebra from continuum analysis;
7. required Lean/mathlib infrastructure;
8. minimal formal theorem statement;
9. adversarial fixtures rejecting exponent, quantifier, domain, and assumption drift;
10. formalizability score from 0 to 5 with rationale.

## Imported-interface rule

A formal theorem may have the form

```text
(imported analytic hypotheses with provenance)
  -> (kernel-checked scaling or implication conclusion),
```

but it may not be described as a proof of the imported analytic hypotheses.

## Candidate families

The audit follows `NS-CI-R014-A` through `NS-CI-R014-F` in the Programme scorecard. Candidates rejected by MATHFORGE need only a concise certification-disposition record.

## Deliverables

- candidate scaling table;
- formal statement sketches;
- adversarial exponent and assumption fixtures;
- library-gap ledger;
- formalizability scores;
- certification recommendation for the final shortlist.

## Boundary

No theorem in this lane may formalize, assume opaquely, or claim progress on universal `L^4_tL^6_x` integrability without displaying that premise and its provenance.