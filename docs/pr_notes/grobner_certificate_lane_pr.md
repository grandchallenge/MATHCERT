# PR: Add algebraic Gröbner certificate lane

## Summary

This PR adds a first-class algebraic certificate lane to MATHCERT. The lane is
derived from the 2026 Lean Gröbner formalization and the 2026 Lean-CAS tactic
paper: exact symbolic computation may be delegated to external systems, but
MATHCERT only trusts replayed or Lean-kernel-checked certificates.

## Changes

- adds Lean vocabulary for algebraic certificate kinds, external backends, and
  trust boundaries;
- adds a Gröbner-lane doctrine module and a toy kernel-checked polynomial
  identity;
- adds a JSON schema for algebraic certificates;
- adds a sample certificate fixture and claim-ledger template;
- adds lightweight Python validation for algebraic certificate artifacts;
- adds documentation explaining how this lane fits the MATHCERT certification
  ladder.

## Testing

Run:

```bash
lake build
python3 ci/validate_ledgers.py
python3 ci/test_validate_ledgers.py
python3 ci/validate_algebraic_certificates.py
python3 ci/test_validate_algebraic_certificates.py
python3 ci/replay_certificates.py
python3 ci/check_sorries.py
```

## Notes

This PR deliberately does not implement a full Gröbner tactic or CAS bridge.
It establishes the MATHCERT-facing ledger/schema/trust-boundary layer so that
later work can plug in SageMath, SymPy, Singular, or a Lean-side Gröbner tactic
without changing claim-ledger semantics.
