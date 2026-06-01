# CERTIFICATION_LADDER.md

## Purpose

The certification ladder defines how claims move from idea to certified mathematical artifact. It prevents premature promotion and gives each Work Package a clear path from explanation to accountability.

## Levels

### Level 0: Intake and source status

The problem has been identified and source context is recorded. No new claim is made.

Artifacts:

- problem card;
- source map;
- status triage;
- risk notes.

### Level 1: Reproducible exploration

Computations or examples can be rerun, but they may be floating-point, heuristic, or limited. Useful for reconnaissance only.

Artifacts:

- scripts;
- environment notes;
- seeds;
- raw outputs;
- limitations.

### Level 2: Exact computation or exhaustive finite certificate

Claims over a finite domain are checked with exact arithmetic, exhaustive enumeration, or proof-producing search. This is certification for the finite domain only.

Artifacts:

- exact enumerator;
- output ledger;
- independent verifier;
- certificate schema;
- domain bound.

### Level 3: Formal statement scaffold

Definitions and theorem statements are expressed in Lean/equivalent systems. Proofs may be absent. This level exposes missing definitions and library gaps.

Artifacts:

- formal definitions;
- theorem statements;
- `sorry` or admitted placeholders clearly marked;
- dependency graph;
- informal-to-formal dictionary.

### Level 4: Machine-checked local lemmas or reductions

Important lemmas, reductions, finite verifiers, or algebraic identities are formally checked.

Artifacts:

- checked theorem prover files;
- CI run;
- proof dependency list;
- Work Package linkage.

### Level 5: Machine-checked theorem or replayable certificate theorem

The main claim is formally proved, or the informal theorem is reduced to checked proof artifacts and replayable certificates.

Artifacts:

- formal proof;
- exact certificate replay;
- theorem statement matched to informal theorem;
- no untracked assumptions;
- CI verification.

## Promotion policy

A claim cannot skip directly from Level 1 to Level 5. It may jump from Level 2 to Level 5 if the theorem is finite and the certificate verifier is itself checked.

A claim may be publicized as:

```text
candidate        Level 0-1
computed         Level 2
formalized       Level 3
partially checked Level 4
certified        Level 5
```

## Certification is domain-specific

For finite combinatorics, Level 2 may be very strong. For PDE or quantum chaos, Level 2 may only support toy models. For convex geometry with interval arithmetic, Level 2 can be strong if interval assumptions are complete and replayable.

## Lean-first but not Lean-only

Lean is the preferred formal target for Union-Closed Sets because finite sets and combinatorics are natural fits. Other domains may require Coq, Isabelle, HOL Light, Sage certificates, Arb interval ledgers, or specialized proof-producing solvers.

## Red flags

A claim must not be promoted if:

- it relies on unverified floating-point output;
- its formal theorem statement differs from the informal claim;
- it uses untracked assumptions;
- it treats a bounded computation as an unbounded theorem;
- it contains `sorry` while being described as proved;
- it relies on an unverifiable external script.

## Domain 01 target ladder

For Union-Closed Sets:

```text
Level 0: source/status audit of Frankl's conjecture.
Level 1: Python enumeration for small universes.
Level 2: exact finite-family certificates for n <= chosen bound.
Level 3: Lean definitions and Frankl statement.
Level 4: Lean-checked small lemmas and verifier semantics.
Level 5: not expected for the full conjecture; possible for restricted cases.
```
