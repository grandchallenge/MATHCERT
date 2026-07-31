# MC-FC-WP00 — RH and NS-CI target replay

## Authority

- MATHCERT issue: `#36`
- MATHSOLVE provider issue: `grandchallenge/MATHSOLVE#80`
- MATHSOLVE merge: `916f3434abcce29098ba7508a3b457a461461193`
- MATHFORGE pilot merge: `b1cad1a9ed9256b863bb0a8658f06ea715db1230`
- upstream Formal Conjectures revision: `85f863718beeec7b58a3a1926ee92e3472bc2020`

## Independent kernel replay

MATHCERT imports the exact merged MATHSOLVE package as a pinned Lake dependency.
`MathCert/FormalSources/RHNSReplay.lean` defines three local wrapper theorems:

1. `RH.targetConcordance` replays the definitional equality between the
   Programme RH target and mathlib `RiemannHypothesis`.
2. `NS.targetInterface` replays the universal critical-integrability quantifier
   order and the time-first `L^4_t L^6_x` exponent carrier.
3. `NS.bridgeInterface` replays that the recorded bridge is one-way from the
   critical-integrability target to the positive Clay whole-space alternative.

The replay emits kernel axiom reports for all three wrappers.

## Dispositions

### RH-001

Disposition: `qualified_interface_only`.

The statement carrier, trivial-zero exclusion, pole exclusion, and
real-part-one-half conclusion elaborate in the Cert kernel environment. The
concordance theorem is kernel-checked. This is not a proof of RH.

### NS-CI-001

Disposition: `qualified_interface_only`.

The target interface and one-way bridge definition elaborate. The record
exposes the imported domain axioms for Leray–Hopf solutions, mixed-norm
finiteness, and the positive Clay alternative. No concordance theorem equating
the critical-integrability target with the upstream Clay-A declaration exists
or is claimed.

## Preserved debts

- `RH-T-000` is unproved.
- `NS-CI-T-000` is unproved.
- `NS-A2` is unproved.
- the one-way NS continuation bridge is unproved;
- no reverse Clay implication is stated;
- imported NS analytic predicates require later formalization or an accepted
  theory-interface disposition.

## Promotion boundary

`qualified` applies to exact target interfaces and correspondence boundaries.
It does not certify either open problem, a proof strategy, novelty, priority,
or a global regularity conclusion.
