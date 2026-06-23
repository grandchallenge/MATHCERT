# Tropical Initial-Ideal Certificates

## Purpose

This note extends the algebraic certificate lane with the narrow certificate kind needed by TROPIC-GROEBNER:

```text
tropical_initial_ideal
```

The certificate records a sampled weight, the declared valuation convention, the computed weighted initial generators, and the monomial-free or monomial-witness decision.

It is not a proof of a full tropical variety unless a separately certified fan traversal is provided.

## Certificate obligation

For a generator

```text
f = sum_a c_a x^a
```

and weight `w`, the replay checker must recompute the score

```text
nu(c_a) + w · a
```

for every term, keep the minimum-score terms, and compare the result with the certificate payload.

For a rejected weight, the certificate must include a monomial witness.

For a retained weight, the certificate must not include a monomial witness.

## Payload fields

The `certificate` object should contain:

```yaml
valuation: trivial | nontrivial | unspecified
weight: [[numerator, denominator], ...]
term_scores: {}
minimal_terms: []
initial_generators: []
contains_monomial: true | false
route_decision: retained | rejected
monomial_witness: null
```

The generic algebraic certificate fields still apply: coefficient domain, variables, monomial order, backend, source generators, target statement, trust boundary, and verification status.

## Trust boundary

`external_certificate_recorded` means the payload is stable and shaped. It is not yet proof.

`script_replayed` means MATHCERT has replayed the score and monomial-witness checks.

`lean_kernel_checked` means a Lean statement over the declared polynomial representation has checked.

## First fixture

`TROPIC-GROEBNER-001-TG001-B` records the retained weight `(1,0)` for

```text
I = <x + y + 1> in QQ[x, y]
```

with trivial valuation. The term scores are `(1,0,0)` for `(x,y,1)`, so the initial form is `y + 1`. The sampled route is retained because the displayed principal initial generator is not a monomial.

The fixture does not enumerate the tropical line. It proves only the sampled certificate path.
