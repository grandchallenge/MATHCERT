# MC-NS-CI-001 — Critical mixed-norm scaling certification plan

## Identity

- Parent programme tracker: `grandchallenge/MATH-PROGRAMME#55`
- MATHCERT issue: `#19`
- Campaign: `NS-CI-001`
- Owning pillar: MATHCERT
- State: certification plan only; no new theorem and no Lean implementation yet

## Certification target

For positive dilation `λ` and a sufficiently regular vector field `u`, define

```math
u_λ(x,t)=λu(λx,λ²t).
```

The first target is the exact identity

```math
∫₀ᵀ ‖u_λ(t)‖_{L⁶(ℝ³)}⁴dt
=∫₀^{λ²T} ‖u(s)‖_{L⁶(ℝ³)}⁴ds.
```

This certifies the scale-critical nature of the `(q,p)=(4,6)` mixed norm. It does not certify that the integral is finite for Navier–Stokes solutions.

## Trust boundary

### May be certified in the initial lane

- Euclidean `L^p` scaling for smooth compactly supported scalar or vector fields;
- time change of variables on finite intervals;
- exact exponent arithmetic in dimension three;
- composition of explicitly named assumptions into a logical implication theorem;
- the abstract energy-space non-embedding witness, only if represented faithfully.

### Must remain imported or open

- Leray–Hopf existence and energy inequality;
- the Ladyzhenskaya–Prodi–Serrin regularity theorem;
- local strong existence and maximal-time continuation;
- weak–strong uniqueness;
- universal `L⁴_tL⁶_x` integrability;
- global regularity.

An imported theorem must be visible as an imported assumption with provenance. It must not be hidden behind a name suggesting kernel-checked analytic content.

## Stage plan

### C0 — library reconnaissance

Audit the pinned Lean/mathlib environment for:

- `MeasureTheory.Lp` and vector-valued normed functions;
- Bochner integration and interval restrictions;
- linear equivalences and measure scaling under `x ↦ λx`;
- compactly supported smooth functions on Euclidean space;
- real powers with positive bases;
- Sobolev spaces and whole-space embeddings;
- divergence-free vector fields.

Output: `docs/ns_ci_library_audit.md` with exact imports, tested snippets, blockers, and actual command results.

### C1 — exponent arithmetic

Prove exact arithmetic lemmas for dimension `d=3`:

```text
1 - 3/6 = 1/2
4(1 - 3/6) = 2
2/4 + 3/6 = 1
```

These are small regression anchors for later generic theorems.

### C2 — spatial `L^p` scaling

Prove a theorem of the schematic form

```lean
-- Schematic. This file is a plan, not compiling code.
theorem lp_scale_dim3
    (λ : ℝ) (hλ : 0 < λ) (p : ℝ) (hp : 0 < p)
    (f : SmoothCompactSupportedVectorField) :
    lpNorm (fun x => λ • f (λ • x)) p
      = λ ^ (1 - 3 / p) * lpNorm f p := by
  ...
```

The actual theorem must use library-native exponents and `L^p` objects. Do not force this surface syntax if it obscures measure-theoretic assumptions.

### C3 — time rescaling and critical integral

Combine the `p=6` spatial theorem with `s=λ²t`. The theorem must state the transformed interval explicitly.

Required adversarial mutations:

1. replace dimension `3` by `2`;
2. omit the amplitude factor `λ`;
3. use `λt` instead of `λ²t`;
4. leave the upper integration limit as `T`;
5. change time exponent `4` to `2` while retaining an invariance claim.

Each mutation must fail either type checking, proof, or a dedicated property test.

### C4 — energy-space obstruction assessment

Assess whether the continuum witness

```math
v(t,x)=t^{-1/2}φ(t^{-1/3}x)
```

written equivalently as `λ(t)^{3/2}φ(λ(t)x)` with `λ(t)=t^{-1/3}`, can be represented without excessive semantic compromise.

The formal target is:

```text
exists divergence-free v,
  v ∈ L∞_t L2_x,
  grad v ∈ L2_t L2_x,
  v ∉ L4_t L6_x.
```

If the library cost is disproportionate, record an ADR and keep the human proof in MATH-PROGRAMME. Do not replace it with a finite-dimensional toy while preserving the same claim identifier.

### C5 — provenance-bearing implication interface

After MATHFORGE and MATHSOLVE supply audited theorem statements, define a structure such as:

```lean
structure NSCIImportedTheory where
  lps_regular_at_4_6 : L4L6 u T → Regular u T
  weak_strong_unique : Strong u T → LerayHopf v T → SameData u v → u = v
  local_continuation : ...
  provenance : ImportedTheoryProvenance
```

Then prove only the logical composition. The structure is not a substitute for formalizing its fields; documentation must call it an imported-theory interface.

## Repository layout proposal

```text
GrandChallengeMath/
  NSCI/
    Exponents.lean
    LpScaling.lean
    MixedNormScaling.lean
    ImportedTheory.lean
    ContinuationInterface.lean

test/
  NSCI/
    ScalingRegression.lean
    InvalidExponentFixtures.lean

docs/
  ns_ci_library_audit.md
  ns_ci_scaling_certification_plan.md
  ns_ci_claim_map.md
```

Implementation begins only after C0 confirms appropriate module names and representations.

## Claim map

| Formal target | Parent claim | Intended state |
|---|---|---|
| exponent arithmetic | `NS-CI-WP00-C003` | kernel checked |
| spatial scaling | `NS-CI-WP00-C003` | kernel checked |
| mixed-norm criticality | `NS-CI-WP00-C003` | kernel checked |
| energy-space obstruction | `NS-CI-WP00-C002` | optional kernel check; otherwise human audited |
| implication composition | `NS-CI-WP00-C005` | conditional theorem over explicit imports |
| universal integrability | none promoted | open; must not be introduced as an axiom |

## Acceptance criteria

- Lean and mathlib remain pinned.
- Every committed Lean file builds with the repository command.
- No `sorry`, hidden axiom, or untracked opaque declaration.
- Every imported mathematical assumption has a source identifier.
- Adversarial scaling fixtures fail as intended.
- Public text states exactly what is kernel checked and what remains imported.
- The formalization is not described as progress on universal regularity.

## First executable step

Run C0 and commit `docs/ns_ci_library_audit.md`. The audit must include at least one compiling prototype for scalar spatial scaling or a precise blocker with tested evidence.