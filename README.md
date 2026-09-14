# MATHCERT

Lean-first certification workspace for the Grand Challenge programme.

## Verified corpus · OpenAI Ten Proofs

MATHCERT has independently kernel-verified the exact supplied Lean
formalizations for all ten results advertised by
[`openai/ten-proofs`](https://github.com/openai/ten-proofs) at commit
[`94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6`](https://github.com/openai/ten-proofs/commit/94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6).

| Verification surface | Protected result |
|---|---|
| Source modules | 10 of 10 built from the pinned upstream tree |
| Advertised headline declarations | 12 of 12 accepted by the Lean kernel |
| Axiom boundary | `Classical.choice`, `Quot.sound`, and `propext` only |
| MATHCERT family routes | 12 of 12 qualified with their statement qualifications retained |
| Protected-main replay | [Passed](https://github.com/grandchallenge/MATHCERT/actions/runs/34838818609) |

This verifies the supplied Lean proofs and their complete Lean dependency
graphs. It does not assert literal line-by-line identity with the accompanying
PDF exposition, novelty, priority, or any broader paraphrase. Read the
[public verification note](docs/OPENAI_TEN_PROOFS_VERIFICATION.md) or inspect
the [machine-readable corpus record](governance/corpus_verifications/OPENAI-TEN-PROOFS-001.json).

## Programme links

MATH-PROGRAMME is the front door and policy source for this pillar.

- [MATH-PROGRAMME Pages home](https://grandchallenge.github.io/MATH-PROGRAMME/)
- [Programme Atlas](https://grandchallenge.github.io/MATH-PROGRAMME/PROGRAMME_ATLAS/)
- [Three-pillar architecture overview](https://github.com/grandchallenge/MATH-PROGRAMME/blob/main/ARCHITECTURE_OVERVIEW.md)
- [MATHCERT pillar doctrine](https://github.com/grandchallenge/MATH-PROGRAMME/blob/main/MATHCERT_SPEC.md)
- [Certification Ladder](https://github.com/grandchallenge/MATH-PROGRAMME/blob/main/CERTIFICATION_LADDER.md)
- [Cross-pillar lanes](https://grandchallenge.github.io/MATH-PROGRAMME/CROSS_PILLAR_LANES/)
- [Groebner and EXPSPACE doctrine](https://grandchallenge.github.io/MATH-PROGRAMME/GROEBNER_EXPSPACE_DOCTRINE/)
- [Claim-boundary doctrine](https://grandchallenge.github.io/MATH-PROGRAMME/CLAIM_BOUNDARY_DOCTRINE/)
- [Exact adopted taxonomy reference](contracts/programme_taxonomy_adoption.json)

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
lemmas, the independently replayed `n <= 4` audit, the checked
minimum-lattice-counterexample theorem spine, and the independently replayed
finite-lattice certificate for sizes `4..7` are restricted infrastructure.

Knowledge graph and classification references are provenance links only.
Certification remains determined by checked proofs, replayable certificates, and
the claim ledger policy.

## Algebraic certificate lane

MATHCERT now has an explicit algebraic-certificate lane for polynomial claims
whose proof burden can be reduced to exact symbolic algebra. The lane follows a
simple trust doctrine:

1. external CAS output is useful evidence but is not trusted;
2. exported certificates are durable artifacts but are not yet proof;
3. replay scripts may audit certificate shape and provenance;
4. Lean-checked lemmas are the certification boundary.

The lane is designed for polynomial identities, ideal membership and
non-membership, Groebner-basis checking, ideal equality, radical membership,
remainder verification, finite-truncation witnesses for families of algebraic
problems, and tropical initial-ideal records. See `docs/algebraic_certificate_lane.md`.

The TROPIC-GROEBNER extension is documented in `docs/tropical_initial_ideal_certificates.md`.

The lightweight JSON certificate validator is included in the standard CI path:

```bash
python3 ci/validate_algebraic_certificates.py
python3 ci/test_validate_algebraic_certificates.py
```

## Tropical ReLU certificate fixture

MATHCERT includes a first tropical-neural extraction fixture:

```text
2D ReLU MLP -> tropical rational certificate -> independent replay checker
```

Fixture 001 records a tiny two-hidden-unit ReLU classifier, expands its logits
into max-plus affine pieces, prunes only a domain-dominated affine probe, and
certifies a logit margin over the box `[-1, 1]^2`. The checker is independent of
PyTorch and uses exact rational arithmetic.

```bash
python3 ci/validate_tropic_relu_certificates.py
python3 ci/test_validate_tropic_relu_certificates.py
```

See `docs/tropic_relu_fixture_001.md` and
`certificates/tropic_relu/fixture_001_relu_mlp_margin.json`.
