# OpenAI Ten Proofs · corpus verification

**Status:** protected-main complete  
**Verified subject:** `openai/ten-proofs` commit `94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6`  
**MATHCERT record:** `MC-OPENAI-TEN-PROOFS-CORPUS-VERIFICATION-001`

## The result

MATHCERT independently rebuilt and Lean-kernel-checked the supplied
formalizations for all ten advertised results. The verification covered the
complete Lean dependency graph of each named headline declaration, not a
summary, route label, or prose-only surrogate.

| # | Advertised result | Exact module | Kernel-checked headline surface |
|---:|---|---|---|
| 1 | High-dimensional sphere packing | `SpherePacking.lean` | `PackingBounds.sharpFullCohnElkiesManuscriptConclusions` |
| 2 | Binary and spherical codes | `MetricCodes.lean` | `MetricCodes.Johnson.binaryRate_lt_mrrw`; `MetricCodes.Spherical.HigherHierarchy.strict_hierarchy` |
| 3 | Non-sofic groups | `NonSoficGroup.lean` | `SoficGroups.SourceTopLevelCompressionFinal.exists_finitelyPresented_nonsofic_group` |
| 4 | Connes rigidity counterexample | `ConnesRigidity.lean` | `ConnesRigidity.exists_infinite_pairwise_nonisomorphic_propertyT_icc_groups_with_isomorphic_factors` |
| 5 | Permanent circuit and formula lower bounds | `Permanent.lean` | `PermanentFormulaLowerBound.permanent_rational_formula_logarithmic_lower_bound` |
| 6 | Quantum parallel repetition | `QuantumParallelRepetition.lean` | `QuantumParallelRepetition.distributionUniformExponential` |
| 7 | Closest-vector and decoding hardness | `GapCVP.lean` | `GapCVP.Comparator.gapCVP400IsNPHard` |
| 8 | Sharp Ehrhart volume inequality | `EhrhartVolumeInequality.lean` | `Ehrhart.Volume.ehrhart_volume_inequality_for_sets` |
| 9 | Multicolor triangle Ramsey numbers | `MulticolorTriangleRamsey.lean` | `ErdosProblems.MulticolourTriangleRamsey.erdos_problem_183_explicit` |
| 10 | Extremal graph counterexamples | `CompactnessAndDegeneracy.lean` | `CompactnessConjecture.quantitativeCompactnessCounterexample`; `TwoDegenerateGraphs.twoDegenerateExtremalCounterexample` |

## What was checked

The protected workflow independently pinned and checked:

- upstream commit `94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6`;
- upstream tree `174289e4d4958cb0509874e6e53400e098213de7`;
- the exact Git blob of every source module;
- Lean `4.32.0` and mathlib commit `81a5d257c8e410db227a6665ed08f64fea08e997`;
- a clean build of each complete source module;
- kernel acceptance of all twelve headline declarations; and
- an axiom report permitting only `Classical.choice`, `Quot.sound`, and
  `propext`.

The final candidate head
`62a86d980679c9015a9c550d6441d3db185cd6b9` received a fresh independent
non-author approval before expected-head merge. Protected main then replayed
the corpus workflow successfully at merge commit
`2aeb5875532152310331662e18327cf9dc3c736e`.

## Evidence chain

| Evidence | Public record |
|---|---|
| Corpus verification | [`OPENAI-TEN-PROOFS-001.json`](../governance/corpus_verifications/OPENAI-TEN-PROOFS-001.json) |
| Protected integration | [MATHCERT PR #290](https://github.com/grandchallenge/MATHCERT/pull/290) |
| Protected-main replay | [Actions run 34838818609](https://github.com/grandchallenge/MATHCERT/actions/runs/34838818609) |
| Corrective tracker | [MATHCERT issue #289](https://github.com/grandchallenge/MATHCERT/issues/289) |
| Upstream formal source | [`openai/ten-proofs`](https://github.com/openai/ten-proofs/tree/94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6) |

## Claim boundary

The warranted public statement is:

> The exact supplied Lean formalizations for all ten advertised OpenAI Ten
> Proofs results were independently rebuilt and accepted by the Lean kernel on
> their recorded headline declarations, under the statement qualifications
> retained in the protected MATHCERT certificates.

This record does **not** establish literal line-by-line equivalence between the
Lean source and the accompanying PDF exposition. It makes no novelty,
publication-priority, authorship, or broader mathematical claim. The exact
family-level qualifications remain authoritative wherever a formal statement
is a restricted consequence, structured projection, or strengthening of its
source presentation.
