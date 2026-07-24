# HC-WP00 claim schema and certification boundary

## Parent workflow

- Programme: `grandchallenge/MATH-PROGRAMME#65`
- Forge: `grandchallenge/MATHFORGE#21`
- Solve: `grandchallenge/MATHSOLVE#62`
- Cert: `grandchallenge/MATHCERT#23`
- Campaign: `HC-001`
- Audit date: 2026-07-24

## Purpose

The first certification task is semantic: prevent a theorem statement from changing its variety class, coefficient ring, cohomology theory, codimension, quantifier, or correspondence class while retaining the label “Hodge conjecture.”

Current formal-library infrastructure is not sufficient for an honest end-to-end formalization of the classical theorem. A bounded mathlib documentation audit found partial complex-manifold and singular infrastructure, but not a mature integrated stack for smooth projective varieties over `C`, Chow groups, rational equivalence, singular/de Rham comparison, polarizable Hodge structures, and algebraic cycle-class maps. This is a formalization boundary, not evidence about mathematical truth.

## Claim record

Every Hodge-related claim must instantiate `schemas/hc_claim_record.schema.json` and record:

- stable claim ID and campaign ID;
- base field;
- geometric category;
- smoothness and properness/projectivity;
- dimension and codimension;
- coefficient ring;
- cohomology theory and comparison map;
- input class predicate;
- cycle/correspondence object;
- cycle equivalence relation;
- quantifier scope;
- conclusion type;
- conditional dependencies;
- implication direction;
- source locator and audit state;
- proof/certification status;
- explicit claims not made.

## First formal model

The initial machine-checkable layer may abstract away geometry while preserving types and implications.

```lean
-- Schematic only.
structure GradedHodgeData where
  Hq : Nat -> Type
  Hc : Nat -> Type
  ratToComplex : {k : Nat} -> Hq k -> Hc k
  hodgePiece : Nat -> Nat -> Set (Hc (· + ·))

structure CycleClassInterface where
  Cycle : Nat -> Type
  ratCycle : Nat -> Type
  hodge : Nat -> Type
  cl : {p : Nat} -> ratCycle p -> hodge p

classicalHodgeAt (I : CycleClassInterface) (p : Nat) : Prop :=
  Function.Surjective (@I.cl p)
```

The actual definitions will differ. The certification objective is that a claim of surjectivity cannot silently become injectivity, integral surjectivity, Kahler surjectivity, effectivity, or a statement about a broader motivated correspondence class.

## Semantic replay fixtures

### Coefficient drift

Input:

```text
coefficient_ring = Q
```

Mutation:

```text
coefficient_ring = Z
```

Expected result: rejection as a different and false-in-general formulation.

### Rationality loss

Input predicate:

```text
alpha in H^(2p)(X,Q) and alpha_C in H^(p,p)
```

Mutation:

```text
alpha_C in H^(p,p)
```

Expected result: rejection; complex Hodge type alone does not imply rationality.

### Geometry drift

Input:

```text
smooth projective variety over C
```

Mutation:

```text
compact Kahler manifold
```

Expected result: rejection as a broader false-in-general analogue.

### Cycle-object drift

Input:

```text
CH^p(X) tensor Q
```

Mutation:

```text
motivated correspondences / topological K-theory / analytic coherent sheaf classes
```

Expected result: rejection unless an independently proved map from the mutated object to algebraic cycles is present.

### Effectivity drift

Input conclusion:

```text
finite rational linear combination of codimension-p subvarieties
```

Mutation:

```text
one effective irreducible subvariety
```

Expected result: rejection as an unrequested strengthening.

### Quantifier drift

Input:

```text
for every smooth projective X and every rational Hodge class alpha
```

Mutation:

```text
for a very general X / for sampled alpha
```

Expected result: rejection as a restricted claim.

### Implication reversal

Valid:

```text
algebraic -> Hodge
```

Mutation:

```text
Hodge -> algebraic
```

Expected result: label as the open target, not as a definition or imported theorem.

## Trust boundary for imported mathematics

The following remain named imports until formalized faithfully:

- Hodge decomposition for smooth projective complex varieties;
- Poincare duality;
- hard Lefschetz and compatibility with rational Hodge structures;
- Lefschetz `(1,1)`;
- Chow groups and rational equivalence;
- topological/algebraic cycle-class construction;
- Atiyah-Hirzebruch counterexample machinery;
- compact-Kahler counterexamples;
- Cattani-Deligne-Kaplan Hodge-locus theorem;
- comparison and specialization theorems used in Hodge-Tate arguments.

A formal implication theorem may accept these as provenance-bearing hypotheses. It may not conceal them as axioms and report the resulting term as a proof of the conjecture.

## Candidate certifiable slices

### C0 — schema validation

Validate claim records and reject coefficient, geometry, codimension, quantifier, and implication mutations.

### C1 — finite statement lattice

Represent formulation nodes and allowed relation labels:

```text
EQUIVALENT
IMPLIES
IMPLIED_BY
STRICTER
BROADER_FALSE_ANALOGUE
PARALLEL_REQUIRES_BRIDGE
NO_KNOWN_IMPLICATION
```

Check that no cycle in the relation graph yields `absolute -> algebraic`, `Tate -> Hodge`, or `Hodge locus -> algebraic class` without an explicit conjectural edge.

### C2 — boundary-case abstract proof

Under imported interfaces for Lefschetz `(1,1)` and hard Lefschetz as a rational Hodge-structure isomorphism, certify the logical reduction of codimension `n-1` to codimension one and the dimension-at-most-three case.

### C3 — cycle-generator equivalence

In an abstract free-module/quotient model, certify that surjectivity from `CH^p tensor Q` is equivalent to rational generation by irreducible subvariety classes, conditional on factorization of the cycle map.

### C4 — source-provenance checks

Every literature-derived theorem node must carry an audited source ID. A theorem with `THEOREM_BODY_PENDING` cannot be used to promote a more precise historical hypothesis than its record supports.

## Out of scope

- formal proof of universal cycle-class surjectivity;
- a surrogate finite-dimensional vector-space model presented as algebraic geometry;
- numerical period computations presented as certificates of algebraicity;
- declaring imported Hodge theory or Chow theory proved because it appears as a structure field;
- certification of a claimed new known case without exact geometric construction and source/prior-art review.

## Acceptance criteria

- JSON claim records validate against the committed schema.
- Negative fixtures fail for the intended reason.
- Every imported theorem is visible in the dependency output.
- No unchecked placeholder or axiom is included in a public proof-status count.
- Public wording remains `semantic substrate` or `conditional abstract certification`, never `formal proof of Hodge`.

## First executable MATHCERT task

Implement schema validation and semantic mutation fixtures for the canonical classical claim. This advances statement hygiene while remaining independent of the missing complex-algebraic-geometry library stack.