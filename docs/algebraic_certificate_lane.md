# Algebraic Certificate Lane

## Purpose

This lane codifies a narrow but important MATHCERT doctrine:

> Computation may suggest. Certificates may travel. Lean must check.

## Programme links

Read this certificate lane through the programme front door and the shared doctrine pages:

- [MATH-PROGRAMME Pages home](https://grandchallenge.github.io/MATH-PROGRAMME/)
- [Programme Atlas](https://grandchallenge.github.io/MATH-PROGRAMME/PROGRAMME_ATLAS/)
- [MATHCERT pillar doctrine](https://github.com/grandchallenge/MATH-PROGRAMME/blob/main/MATHCERT_SPEC.md)
- [Certification Ladder](https://github.com/grandchallenge/MATH-PROGRAMME/blob/main/CERTIFICATION_LADDER.md)
- [Cross-pillar lanes](https://grandchallenge.github.io/MATH-PROGRAMME/CROSS_PILLAR_LANES/)
- [Groebner and EXPSPACE doctrine](https://grandchallenge.github.io/MATH-PROGRAMME/GROEBNER_EXPSPACE_DOCTRINE/)
- [Reduction and Certificate Foundations](https://grandchallenge.github.io/MATH-PROGRAMME/REDUCTION_CERTIFICATE_FOUNDATIONS/)
- [Claim-boundary doctrine](https://grandchallenge.github.io/MATH-PROGRAMME/CLAIM_BOUNDARY_DOCTRINE/)

The lane is for proof obligations whose hard part is exact symbolic algebra:
polynomial identity checking, ideal membership, ideal equality, Gröbner-basis
checking, normal-form or remainder verification, radical membership, and
finite-truncation algebra for families of polynomial systems.

It is not intended to replace geometric, analytic, combinatorial, interval, or
human mathematical argument. It is a proof-carrying back-end for the algebraic
subclaims that appear inside those arguments.

## Paper-derived design notes

The February 2026 Lean Gröbner formalization develops the foundations directly
over Mathlib's `MvPolynomial` and monomial-order infrastructure. Its relevant
lessons for MATHCERT are:

- keep the mathematical vocabulary in Lean rather than in an external CAS;
- distinguish the zero polynomial from constants carefully when degree data is
  part of a certificate;
- support arbitrary variable index types, including infinite-variable settings;
- bridge finite truncations and infinite-variable statements using compatible
  embeddings and limit-style constructions.

Reference: <https://arxiv.org/pdf/2602.12772>.

The April 2026 automated polynomial-reasoning paper makes the operational lesson
even sharper:

- realistic Gröbner computation inside Lean is not the practical default;
- external systems such as SageMath or SymPy should perform heavy computation;
- returned certificates should be serialized, imported, and checked in Lean;
- supported tasks include remainder verification, Gröbner-basis checking, ideal
  equality, ideal membership, and radical membership.

Reference: <https://arxiv.org/pdf/2604.13514>.

## Trust ladder

MATHCERT records algebraic evidence at five levels.

| Level | Meaning | Trusted? |
| --- | --- | --- |
| `external_output_only` | A CAS printed a result. | No |
| `external_certificate_recorded` | A certificate artifact was exported and hashed. | No |
| `script_replayed` | MATHCERT replayed schema/provenance checks. | Audit only |
| `lean_kernel_checked` | A local Lean theorem checks the algebraic fact. | Yes |
| `integrated_checked_theorem` | A larger theorem depends on the checked local lemma. | Yes |

The first three levels are valuable engineering evidence. They are not the proof
boundary.

## Certificate payloads

A MATHCERT algebraic certificate should record:

- `certificate_id`;
- `claim_id`;
- certificate kind;
- coefficient domain;
- variable universe and variable names;
- monomial order;
- external backend and backend version;
- source polynomials;
- target polynomial or ideal statement;
- witness data, such as coefficients, remainders, normal forms, or bases;
- hash of the external output;
- Lean theorem name, once available;
- trust boundary.

The canonical schema lives at
`schemas/algebraic_certificate.schema.json`.

## Recommended use inside GCL

Use this lane when a certificate ledger contains phrases like:

- "after expansion, this expression vanishes";
- "this polynomial belongs to the generated ideal";
- "these two generated ideals are equal";
- "this branch is eliminated by the resulting normal form";
- "the finite truncations stabilize in a compatible way";
- "the equality manifold is obtained by eliminating auxiliary variables."

For the GCL open-problem programmes, this is most useful as local masonry:
small exact algebraic blocks supporting larger human, interval, or geometric
arguments.
