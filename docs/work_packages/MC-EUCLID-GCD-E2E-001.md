# MC-EUCLID-GCD-E2E-001

## The concrete task

The protected Solve package proposes:

\[
\gcd(252,105)=21.
\]

It records three exact divisions:

\[
252=2\cdot105+42,\qquad
105=2\cdot42+21,\qquad
42=2\cdot21+0,
\]

and the integer witness:

\[
21=-2\cdot252+5\cdot105.
\]

## Independent certification surfaces

MATHCERT does not import or execute the Solve producer. Its independent checker reads the committed candidate snapshot and verifies the protected Forge and Solve identities, every division equation, trace linkage, strict descent, terminal zero, positive normalization, divisibility, the Bézout equality, and an independent `math.gcd` replay.

The Lean module defines an accepted-certificate predicate by positivity, common divisibility, and greatestness. It proves that every accepted predicate instance reports `Nat.gcd`, then proves the concrete trace, Bézout equality, gcd value, accepted predicate instance, and specialized soundness statement.

## Object, construction, witness, certificate

| Surface | Authoritative meaning |
|---|---|
| Object | the natural-number greatest common divisor |
| Construction | the Euclidean remainder trace |
| Witness | the integer coefficients `-2` and `5` |
| Certificate | the independently checked evidence package and Lean theorem set |

The Solve output remains candidate evidence. Certification authority arises only from the protected MATHCERT merge and its exact route output.

## GCL–Chaidez continuity

This work package begins with the approachable calculation, states exact quantifiers and input exclusions, and separates theorem, computation, witness, certificate, and nonclaim.

Historical attribution remains deferred. The later Book VII micro-edition must source-lock exact editions and propositions before constructing a historical-to-modern concordance. The modern extended-Euclidean, integer Bézout, and linear Diophantine statements are not presented here as verbatim Euclidean propositions.

Any later illuminated plates are pedagogical orientation only. The typeset theorem, exact trace, source and artifact identities, checker contract, Lean declarations, and technical records are authoritative.

## Claim boundary

This certification covers the admitted accepted-certificate soundness theorem and the exact `252,105` fixture. It does not prove correctness of every extended-Euclidean program, activate the linear Diophantine or Book VII stages, or establish novelty, priority, first formalization, or historical verbatim equivalence.
