# Pseudo-Boolean Certificate Lane

## Role

This lane checks pseudo-Boolean artifacts emitted by MATHSOLVE routes such as `SEMIRING-CONTRACTION/TCM`.

Doctrine:

> Search may be tropical; trust is certificate replay.

The initial checker is intentionally narrow: it validates TCM Fixture 006 assignment artifacts by replaying an integer primal witness and an integer dual upper-bound certificate.

## Programme links

This certificate lane should be read through the programme's finite-obligation and claim-boundary doctrine:

- [MATH-PROGRAMME Pages home](https://grandchallenge.github.io/MATH-PROGRAMME/)
- [Programme Atlas](https://grandchallenge.github.io/MATH-PROGRAMME/PROGRAMME_ATLAS/)
- [MATHCERT pillar doctrine](https://github.com/grandchallenge/MATH-PROGRAMME/blob/main/MATHCERT_SPEC.md)
- [Certification Ladder](https://github.com/grandchallenge/MATH-PROGRAMME/blob/main/CERTIFICATION_LADDER.md)
- [Cross-pillar lanes](https://grandchallenge.github.io/MATH-PROGRAMME/CROSS_PILLAR_LANES/)
- [Claim-boundary doctrine](https://grandchallenge.github.io/MATH-PROGRAMME/CLAIM_BOUNDARY_DOCTRINE/)
- [Resource Budget Policy](https://grandchallenge.github.io/MATH-PROGRAMME/RESOURCE_BUDGET_POLICY/)
- [TCM semiring-contraction route doctrine](https://github.com/grandchallenge/MATH-PROGRAMME/blob/main/docs/routes/TCM_SEMIRING_CONTRACTION_ROUTE.md)

## Fixture 006 checker

```bash
python3 ci/validate_pb_certificate.py path/to/artifacts/fixture006
python3 ci/test_validate_pb_certificate.py
```

The checker expects:

```text
instance.opb
primal_witness.json
pb_dual_certificate.json
result_card.json
```

It accepts only when:

1. the OPB objective parses as a square assignment instance;
2. the witness selects exactly one distinct column per row;
3. the declared witness objective equals the replayed objective;
4. every dual inequality `row_dual_i + col_dual_j >= W_ij` holds;
5. the primal lower bound and dual upper bound meet;
6. the result-card optimum agrees with the replayed optimum.

## Boundary

This is not a full VeriPB implementation. It is a compact replay checker for the Fixture 006 certificate shape and a stepping stone toward external PB/VeriPB/Lean import.
