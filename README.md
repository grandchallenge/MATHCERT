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
