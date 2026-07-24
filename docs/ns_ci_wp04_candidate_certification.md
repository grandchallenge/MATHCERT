# NS-CI-WP04 — Candidate certification feasibility

## Status

- Campaign: `NS-CI-001`
- Programme tracker: `grandchallenge/MATH-PROGRAMME#61`
- MATHCERT tracker: `grandchallenge/MATHCERT#21`
- MATHFORGE shortlist: `A2`, `D1`, `E1`
- State: `INITIAL_SHORTLIST_SCALING_AUDIT_COMPLETE`
- Open universal estimate: explicitly out of scope

MATHCERT certifies algebraic scaling, logical composition, and statement hygiene only. The decisive PDE estimates remain provenance-bearing imported interfaces.

## Common Navier–Stokes scaling

For

```math
u_\lambda(x,t)=\lambda u(\lambda x,\lambda^2t),
```

and a spatial derivative of order `k`,

```math
\|\nabla^ku_\lambda(t)\|_{L^p_x}
=
\lambda^{1+k-3/p}
\|\nabla^ku(\lambda^2t)\|_{L^p_x}.
```

Therefore

```math
\|u_\lambda(t)\|_6^4
=
\lambda^2\|u(\lambda^2t)\|_6^4,
```

and, after `s=lambda^2t`,

```math
I_T(u_\lambda)=I_{\lambda^2T}(u).
```

The mixed-norm convention is `(time,space)=(4,6)`. Reversing this order is a rejected fixture.

---

## A2 — Dissipation-wavenumber criterion

### Imported analytic definition

`Lambda(t)` is imported from the Cheskidov–Shvydkoy dissipation-wavenumber construction, including its dyadic decomposition, viscosity-dependent threshold, measurability, and convention for the lowest active shell. MATHCERT does not reprove these analytic properties in the initial slice.

### Scaling calculation

The required imported scaling interface is

```math
\Lambda_\lambda(t)=\lambda\Lambda(\lambda^2t).
```

For `p>0`,

```math
\int_0^T\Lambda_\lambda(t)^pdt
=
\lambda^{p-2}
\int_0^{\lambda^2T}\Lambda(s)^pds.
```

Consequently:

- `p<2` is subcritical with respect to concentration under this convention;
- `p=2` is invariant;
- `p>2` is stronger on the scaling orbit.

The proposed hypothesis `Lambda in L2_t` and conclusion `I_T<infinity` are therefore both scale-invariant.

### Minimal formal statement sketch

```text
structure DissipationWavenumberInterface where
  Lambda : Real -> ENNReal
  scales : for every lambda>0, Lambda_scaled(t)=lambda*Lambda(lambda^2*t)
  source : Provenance

theorem lambda_Lp_scaling
  (H : DissipationWavenumberInterface) (p : Real) ... :
  integral (Lambda_scaled^p) = lambda^(p-2) * integral (Lambda^p)

theorem A2_implication_shape
  (analytic_bridge : Integrable (Lambda^2) -> Finite CriticalIntegral) :
  Integrable (Lambda^2) -> Finite CriticalIntegral
```

The second theorem certifies logical composition only. It does not prove `analytic_bridge`.

### Adversarial fixtures

- replace exponent `2` by `2+delta` and verify non-invariance;
- reverse mixed-norm order and require rejection;
- rescale the time interval incorrectly and require rejection;
- omit the imported scaling field and require the theorem to remain unprovable;
- present the analytic bridge as an axiom and ensure generated claim text labels it imported.

### Formalizability score

`4/5` for scaling and statement hygiene. The decisive frequency estimate and the analytic definition of `Lambda` are substantial library gaps.

---

## D1 — Uniform shell-flux compensation

### Cutoff-covariant definitions

Let `P_{<=K}` denote a continuous-frequency cutoff, or use dyadic cutoffs with exact covariance restricted first to `lambda=2^m`. Define

```math
u^K=P_{\le K}u,
```

and

```math
\Pi_K(u)
=
\langle P_{\le K}((u\cdot\nabla)u),-\Delta u^K\rangle.
```

Under scaling, the cutoff must transform with frequency:

```math
K\mapsto \lambda K
```

or `N -> N+m` in the dyadic power-of-two model. Holding the cutoff index fixed while scaling the solution is an invalid fixture.

### Scaling calculation

Pointwise in rescaled time,

```math
\Pi_{\lambda K}(u_\lambda)(t)
=
\lambda^3\Pi_K(u)(\lambda^2t),
```

```math
\|\Delta u_\lambda^{\lambda K}(t)\|_2^2
=
\lambda^3\|\Delta u^K(\lambda^2t)\|_2^2,
```

and

```math
\|\nabla u_\lambda^{\lambda K}(t)\|_2^2
=
\lambda\|\nabla u^K(\lambda^2t)\|_2^2.
```

Thus the compensated inequality

```math
\Pi_K
\le
\theta\nu\|\Delta u^K\|_2^2
+a(t)\|\nabla u^K\|_2^2
```

is scale-covariant precisely when

```math
a_\lambda(t)=\lambda^2a(\lambda^2t).
```

Then

```math
\int_0^Ta_\lambda(t)dt
=
\int_0^{\lambda^2T}a(s)ds,
```

so `a in L1_t` is a critical coefficient condition.

### Tautology boundary

The compensated inequality is an imported analytic interface, not an admissible independent hypothesis. A candidate formalization must expose a separate observable `H_D` and an imported theorem

```text
H_D -> compensated_interface.
```

The following definitions are forbidden because they hide the conclusion:

```text
H_D := compensated_interface
H_D := a(t)=C*||u(t)||_6^4 is integrable
H_D := uniform H1 control
```

### Minimal formal statement sketch

```text
structure ShellFluxInterface where
  flux : Cutoff -> Time -> Real
  cutoff_covariance : ...
  scaling : flux_scaled(lambda*K,t)=lambda^3*flux(K,lambda^2*t)
  compensation : IndependentHypothesis -> CompensatedInequality
  source : Provenance

theorem compensated_gronwall
  (theta_lt_one : theta<1)
  (ha : Integrable a)
  (uniform_in_cutoff : ... ) :
  UniformEnstrophyBound
```

The Grönwall and exponent algebra are certifiable. The independent commutator mechanism and continuum limit are imported.

### Adversarial fixtures

- keep `K` fixed under scaling and require failure;
- use `a_lambda=lambda*a(lambda^2t)` and require failure;
- permit cutoff-dependent `a_K` without a uniform integrable majorant and require rejection;
- define `a` through the target critical norm and classify the theorem as circular;
- infer continuum regularity from a single finite cutoff and require rejection.

### Formalizability score

`3/5`. The algebraic interface is clean, but D1 is not theorem-grade until `H_D` is independently defined.

---

## E1 — Compact-support-to-Schwartz bridge

### Logical statement profile

E1 is primarily a quantifier and compactness bridge. Its safe logical skeleton is:

```text
for a fixed Schwartz datum u0,
there exists a divergence-free compactly supported approximating sequence u0_n,
for every finite T there exists K_T independent of n,
all associated strong solutions satisfy ||u_n||_(L4_t L6_x)^4 <= K_T,
compactness produces one Leray-Hopf limit u,
lower semicontinuity gives the same bound for u,
LPS makes u strong,
weak-strong uniqueness identifies every Leray-Hopf solution from u0 with u.
```

The order of quantifiers is essential. The invalid weaker statement

```text
for every n there exists K_(T,n)<infinity
```

does not provide the uniform passage to the limit.

### Scaling disposition

E1 is not primarily a new scaling criterion. If the approximation topology and bounds are rescaled consistently, the critical norm bound is invariant. The key certification burden is quantifier preservation, not a new exponent identity.

### Minimal formal statement sketch

```text
structure CompactApproximationInterface where
  approximants : Nat -> InitialDatum
  compact_support : ...
  converges_to_target : ...
  uniform_critical_bound : for every T, exists K_T, forall n, Bound n T K_T
  compactness : ProvenanceBearingImportedTheorem
  lower_semicontinuity : ProvenanceBearingImportedTheorem
  lps_regularization : ProvenanceBearingImportedTheorem
  weak_strong_uniqueness : ProvenanceBearingImportedTheorem

theorem E1_logical_bridge
  (H : CompactApproximationInterface) :
  forall leray_solution_from_target, Finite CriticalIntegral
```

### Adversarial fixtures

- swap `exists K_T, forall n` with `forall n, exists K_(T,n)`;
- prove existence of one regular limit but omit universal identification;
- change Schwartz data to compactly supported data in the conclusion;
- omit lower semicontinuity;
- treat local compactness as automatic global strong convergence;
- use weak–strong uniqueness before proving that the limit is in the strong class.

### Formalizability score

`4/5` for the implication skeleton. The compactness and PDE uniqueness fields remain imported.

---

## Rejected generic families

- generic geometric depletion: no separate certification target until a statement distinct from established vorticity-direction criteria is supplied;
- generic concentration/sparsity: no separate certification target until a statement beyond established sparseness criteria and the documented scaling gap is supplied;
- generic symmetry class: classical cases are not certification targets; recent axisymmetric-swirl claims require claimed-proof audit rather than formal adoption.

## Initial certification recommendation

1. **A2:** admissible and exactly scale-critical; best candidate for a first kernel-checked scaling slice.
2. **D1:** algebraically coherent, but blocked on an independent non-tautological hypothesis.
3. **E1:** logically clean and formalizable as a conditional bridge; substantive analytic work remains imported.

MATHCERT recommends provisional priority `A2 > E1 > D1` for statement certification. This is not a mathematical target selection or novelty judgment.

## Library-gap ledger

| Component | Initial status |
|---|---|
| scalar exponent and interval scaling | directly formalizable |
| mixed-norm order fixtures | directly formalizable |
| abstract cutoff covariance | formalizable with a simplified cutoff model |
| Grönwall implication | likely available or locally formalizable |
| quantifier-order fixtures | directly formalizable |
| Littlewood–Paley decomposition on `R3` | substantial library gap |
| dissipation-wavenumber analytic definition | imported interface initially |
| nonlinear commutator estimates | imported interface initially |
| Leray compactness and weak–strong uniqueness | imported interfaces initially |

## Claim boundary

The scaling audit does not prove A2, supply D1's missing mechanism, prove E1's imported compactness fields, or formalize the universal critical-integrability estimate.