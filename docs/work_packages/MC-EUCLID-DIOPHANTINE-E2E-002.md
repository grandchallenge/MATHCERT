# MC-EUCLID-DIOPHANTINE-E2E-002

## Purpose

This work package independently certifies the admitted two-variable linear Diophantine theorem and two bounded exemplars. It consumes the protected Stage 1 GCD and Bézout result; it does not create a second GCD definition or execute the MATHSOLVE producer.

## Mathematical object

For integers `a`, `b`, and `c`, define the object of study as the equation

`a*x + b*y = c`

with integer unknowns `x` and `y` and a coefficient pair that is not simultaneously zero.

## Construction

The constructive direction scales a Bézout representation of the normalized gcd when that gcd divides the target. For the protected exemplar,

`-2*252 + 5*105 = 21`.

Since `84 = 4*21`, scaling gives

`-8*252 + 20*105 = 84`.

The construction is distinct from its witness and from the independent certificate that checks it.

## Constructive witness

The positive witness is the exact pair

`x = -8`, `y = 20`.

The checker verifies the scale factor, the protected Bézout identity, and the final integer equality.

## Divisibility obstruction

The negative exemplar is

`252*x + 105*y = 20`.

The protected normalized gcd is `21`. The exact division is

`20 = 0*21 + 20`, with `0 < 20 < 21`.

Every integer linear combination of `252` and `105` is divisible by `21`; the nonzero remainder therefore excludes an integer solution. A timeout or failed search is never accepted as an obstruction.

## Independent certificate

`work_packages/EUCLID_DIOPHANTINE_E2E_002/check_certificate.py` treats the Solve candidate as data. It does not import or execute `solve/euclid_diophantine.py`. It checks exact Forge, Stage 1, and Stage 2 identities; both evidence forms; authority boundaries; and the content-addressed route transition.

The checker is fail-closed and is accompanied by adversarial mutations for sign and input drift, false scale factors, changed witnesses, malformed remainders, identity substitution, timeout-as-unsatisfiability, and authority inflation.

## Formal theorem

`MathCert/Domains/NumberTheory/EuclidDiophantine.lean` proves the admitted modern theorem:

For integers `a`, `b`, and `c`, with `a != 0` or `b != 0`,

`(exists x y, a*x + b*y = c)` if and only if `gcd(a,b)` divides `|c|` under the normalized integer-gcd interface.

The file also proves the positive fixture, the exact obstruction statement, the negative no-solution theorem, and explicit zero-target solvability. Declaration-level axiom reports are emitted. `sorry` and local axioms are prohibited.

## Historical boundary

This is a modern integer formulation informed by the Euclidean algorithm and Bézout theory. It is not attributed verbatim to Euclid. Exact historical-modern concordance remains reserved for the source-locked Book VII micro-edition.

## GCL–Chaidez separation

The object, construction, witness, obstruction, independent certificate, and formal theorem are distinct authoritative surfaces. Any illustrated or illuminated presentation is pedagogical orientation only; the typeset theorem, exact arithmetic, checker contract, Lean declarations, and source identities govern.

## Excluded claims

This work package does not prove completeness for arbitrary Diophantine equations; accept timeout as unsatisfiability; establish novelty, priority, or first formalization; complete the Book VII micro-edition; or automatically activate Stage 3.

## Proposed protected disposition

`CERTIFIED_LINEAR_DIOPHANTINE_EQUIVALENCE_AND_BOUNDED_EXEMPLARS`
