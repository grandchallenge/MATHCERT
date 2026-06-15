# Pseudo-Boolean Certificate Lane

## Role

This lane checks pseudo-Boolean artifacts emitted by MATHSOLVE routes such as `SEMIRING-CONTRACTION/TCM`.

Doctrine:

> Search may be tropical; trust is certificate replay.

The initial checker is intentionally narrow: it validates TCM Fixture 006 assignment artifacts by replaying an integer primal witness and an integer dual upper-bound certificate.

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
