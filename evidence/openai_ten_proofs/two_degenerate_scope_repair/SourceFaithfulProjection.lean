import CompactnessAndDegeneracy

namespace TwoDegenerateGraphs

open Filter Finset SimpleGraph
open scoped Topology

/--
MATHCERT source-faithful projection for Chapter 10, Theorem 1.2.

The upstream theorem `twoDegenerateExtremalCounterexample` is intentionally stronger:
it also proves a coloring-side maximum-degree property.  That conjunct is discarded here
and is not part of this projection's source attribution.
-/
open Classical in
theorem mathcert_sourceFaithfulTwoDegenerateExtremalCounterexample :
    ∃ (q : ℕ) (H : SimpleGraph (Fin q)),
      H.Connected ∧
      H.IsBipartite ∧
      IsTwoDegenerate H ∧
      ∃ c ε : ℝ, 0 < c ∧ 0 < ε ∧
        ∀ᶠ n : ℕ in atTop,
          c * (n : ℝ) ^ ((3 : ℝ) / 2 + ε) ≤
            (SimpleGraph.extremalNumber n H : ℝ) := by
  obtain ⟨q, H, hconnected, hbipartite, hdegenerate, _hdegree,
    c, ε, hc, hε, hlower⟩ := twoDegenerateExtremalCounterexample
  exact ⟨q, H, hconnected, hbipartite, hdegenerate,
    c, ε, hc, hε, hlower⟩

/--
Dependency-separation witness for the Erdős refutation.  This proof assumes only the
source-faithful core proposition above; it does not assume or recover the stronger
coloring-side maximum-degree conjunct.
-/
theorem mathcert_not_erdos_146_from_sourceFaithfulCore
    (hcore :
      ∃ (q : ℕ) (H : SimpleGraph (Fin q)),
        H.Connected ∧
        H.IsBipartite ∧
        IsTwoDegenerate H ∧
        ∃ c ε : ℝ, 0 < c ∧ 0 < ε ∧
          ∀ᶠ n : ℕ in atTop,
            c * (n : ℝ) ^ ((3 : ℝ) / 2 + ε) ≤
              (SimpleGraph.extremalNumber n H : ℝ)) :
    ¬ DegeneracyConjectureStatement := by
  intro hconjecture
  obtain ⟨q, H, _hconnected, hbipartite, hdegenerate,
    c, ε, hc, hε, hlower⟩ := hcore
  have hbigO := hconjecture 2 q H (by norm_num)
    hbipartite hdegenerate
  obtain ⟨C, hupper⟩ := Asymptotics.isBigO_iff.mp hbigO
  have hupper' :
      ∀ᶠ n : ℕ in Filter.atTop,
        (SimpleGraph.extremalNumber n H : ℝ) ≤
          C * (n : ℝ) ^ ((3 : ℝ) / 2) := by
    filter_upwards [hupper] with n hn
    have hnnonneg : (0 : ℝ) ≤ (n : ℝ) := Nat.cast_nonneg _
    have hextremal_nonneg :
        (0 : ℝ) ≤ (SimpleGraph.extremalNumber n H : ℝ) :=
      Nat.cast_nonneg _
    have hnormalized :
        (SimpleGraph.extremalNumber n H : ℝ) ≤
          C * (n : ℝ) ^ ((2 : ℝ) - 1 / (2 : ℝ)) := by
      simpa only [Real.norm_eq_abs, abs_of_nonneg hextremal_nonneg,
        abs_of_nonneg (Real.rpow_nonneg hnnonneg _), Nat.cast_ofNat] using hn
    convert hnormalized using 1
    norm_num
  have hlarge :=
    CompactnessConjecture.eventually_constant_le_positive_nat_rpow
      (C + 1) c ε hc hε
  have himpossible : ∀ᶠ n : ℕ in Filter.atTop, False := by
    filter_upwards [hlower, hupper', hlarge,
      Filter.eventually_gt_atTop 0] with n hlow hupp hlarge_n hn
    have hnreal : (0 : ℝ) < (n : ℝ) := by exact_mod_cast hn
    have hscale : 0 < (n : ℝ) ^ ((3 : ℝ) / 2) :=
      Real.rpow_pos_of_pos hnreal _
    have hdecompose :
        c * (n : ℝ) ^ ((3 : ℝ) / 2 + ε) =
          (c * (n : ℝ) ^ ε) * (n : ℝ) ^ ((3 : ℝ) / 2) := by
      rw [Real.rpow_add hnreal]
      ring
    rw [hdecompose] at hlow
    have hscaled := mul_le_mul_of_nonneg_right hlarge_n hscale.le
    nlinarith
  exact himpossible.exists.elim (fun _ h => h)

/-- The source-faithful core suffices for the registered Erdős refutation statement. -/
theorem mathcert_sourceFaithfulNotErdos146 :
    ¬ DegeneracyConjectureStatement :=
  mathcert_not_erdos_146_from_sourceFaithfulCore
    mathcert_sourceFaithfulTwoDegenerateExtremalCounterexample

end TwoDegenerateGraphs
