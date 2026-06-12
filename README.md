# MATHCERT

Lean-first certification workspace for the Grand Challenge programme.

## Bootstrap

The package pins Lean in `lean-toolchain` and declares a matching mathlib release in
`lakefile.lean`. From this directory:

```powershell
lake update
lake exe cache get
.\ci\check_lean.ps1
```

On Linux or macOS:

```bash
lake update
lake exe cache get
./ci/check_lean.sh
```

The initial scaffold had Elan shims available but no pinned toolchain or mathlib
dependency, so `lake build` could stall while resolving the ambient `stable`
toolchain. The package-local pin makes that dependency explicit.

## Certification boundary

The full union-closed sets conjecture is stated but not proved. The checked local
lemmas and independently replayed `n <= 4` audit are bounded infrastructure.

## Algebraic certificate lane

MATHCERT now has an explicit algebraic-certificate lane for polynomial claims
whose proof burden can be reduced to exact symbolic algebra. The lane follows a
simple trust doctrine:

1. external CAS output is useful evidence but is not trusted;
2. exported certificates are durable artifacts but are not yet proof;
3. replay scripts may audit certificate shape and provenance;
4. Lean-checked lemmas are the certification boundary.

The lane is designed for polynomial identities, ideal membership and
non-membership, Gröbner-basis checking, ideal equality, radical membership,
remainder verification, and finite-truncation witnesses for families of algebraic
problems. See `docs/algebraic_certificate_lane.md`.

The lightweight JSON certificate validator is included in the standard CI path:

```bash
python3 ci/validate_algebraic_certificates.py
python3 ci/test_validate_algebraic_certificates.py
```
