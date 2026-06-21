import MathCert.Domains.UnionClosed.IdealFamilyBridge
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Tactic

/-!
# Checked NDS infrastructure for the ideal-family bridge

This file contains local, placeholder-free support lemmas for the intended
ideal-family NDS nonpositivity proof.  The final trace/contraction induction
is stated in `IdealFamilyNDSEndgame.lean`.
-/

namespace IdealFamily

open Finset
open scoped BigOperators

namespace SetFamily

variable {α : Type*} [DecidableEq α]
variable (SF : SetFamily α)
variable [DecidablePred SF.sets]

/-- Nat-level incidence double counting:
the sum of vertex degrees over the ground equals the sum of edge sizes. -/
theorem sum_degreeNat_over_ground_eq_totalSizeNat :
    ∑ v ∈ SF.ground, SF.degreeNat v =
      ∑ s ∈ SF.carrier, s.card := by
  classical
  let r : α → Finset α → Prop := fun v s => v ∈ s
  have hdc :
      (∑ v ∈ SF.ground, (SF.carrier.bipartiteAbove r v).card) =
        ∑ s ∈ SF.carrier, (SF.ground.bipartiteBelow r s).card :=
    Finset.sum_card_bipartiteAbove_eq_sum_card_bipartiteBelow
      (r := r) (s := SF.ground) (t := SF.carrier)
  calc
    ∑ v ∈ SF.ground, SF.degreeNat v
        = ∑ v ∈ SF.ground, (SF.carrier.bipartiteAbove r v).card := by
          refine Finset.sum_congr rfl ?_
          intro v hv
          apply congrArg Finset.card
          apply Finset.ext
          intro s
          simp [SetFamily.S, Finset.bipartiteAbove, r]
    _ = ∑ s ∈ SF.carrier, (SF.ground.bipartiteBelow r s).card := hdc
    _ = ∑ s ∈ SF.carrier, s.card := by
          refine Finset.sum_congr rfl ?_
          intro s hs
          have hsub : s ⊆ SF.ground :=
            ((SetFamily.mem_carrier_iff (SF := SF)).mp hs).1
          apply congrArg Finset.card
          apply Finset.ext
          intro v
          constructor
          · intro hv
            exact (Finset.mem_filter.mp hv).2
          · intro hv
            exact Finset.mem_filter.mpr ⟨hsub hv, hv⟩

/-- Integer-level incidence double counting. -/
theorem sum_degree_over_ground_eq_totalSize :
    ∑ v ∈ SF.ground, SF.degree v = SF.totalSize := by
  classical
  have hNat := sum_degreeNat_over_ground_eq_totalSizeNat (SF := SF)
  calc
    ∑ v ∈ SF.ground, SF.degree v
        = ∑ v ∈ SF.ground, ((SF.degreeNat v : ℕ) : ℤ) := by
          rfl
    _ = ((∑ v ∈ SF.ground, SF.degreeNat v : ℕ) : ℤ) := by
          norm_cast
    _ = ((∑ s ∈ SF.carrier, s.card : ℕ) : ℤ) := by
          exact congrArg (fun n : ℕ => (n : ℤ)) hNat
    _ = SF.totalSize := by
          rfl

/-- Frankl's normalized-degree sum identity. -/
theorem sum_normalizedDegree_over_ground_eq_nds :
    ∑ v ∈ SF.ground, SF.normalizedDegreeAt v = SF.nds := by
  classical
  have hDeg := sum_degree_over_ground_eq_totalSize (SF := SF)
  calc
    ∑ v ∈ SF.ground, SF.normalizedDegreeAt v
        = ∑ v ∈ SF.ground, ((2 : ℤ) * SF.degree v - SF.numEdges) := by
          rfl
    _ = (2 : ℤ) * (∑ v ∈ SF.ground, SF.degree v)
          - (SF.ground.card : ℤ) * SF.numEdges := by
          rw [Finset.sum_sub_distrib]
          rw [← Finset.mul_sum]
          simp [Finset.sum_const]
    _ = (2 : ℤ) * SF.totalSize
          - SF.numEdges * (SF.ground.card : ℤ) := by
          rw [hDeg]
          ring
    _ = SF.nds := by
          rfl

/-- Rewrite NDS as a sum of per-member centered cardinalities. -/
theorem nds_eq_sum_card_terms :
    SF.nds =
      ∑ s ∈ SF.carrier,
        ((2 : ℤ) * (s.card : ℤ) - (SF.ground.card : ℤ)) := by
  classical
  unfold SetFamily.nds SetFamily.totalSize SetFamily.totalSizeNat
    SetFamily.numEdges SetFamily.numEdgesNat
  calc
    (2 : ℤ) * (((SF.carrier.sum fun s => s.card) : ℕ) : ℤ) -
        (((SF.carrier.card : ℕ) : ℤ) * (SF.ground.card : ℤ))
        =
      (∑ s ∈ SF.carrier, (2 : ℤ) * (s.card : ℤ)) -
        ∑ _s ∈ SF.carrier, (SF.ground.card : ℤ) := by
          have hSumCast :
              (((SF.carrier.sum fun s => s.card) : ℕ) : ℤ) =
                ∑ s ∈ SF.carrier, (s.card : ℤ) := by
            norm_cast
          rw [hSumCast]
          rw [Finset.mul_sum]
          simp [Finset.sum_const]
    _ =
      ∑ s ∈ SF.carrier,
        ((2 : ℤ) * (s.card : ℤ) - (SF.ground.card : ℤ)) := by
          rw [← Finset.sum_sub_distrib]

end SetFamily

namespace Ideal

variable {α : Type*} [DecidableEq α]
variable (F : Ideal α)
variable [DecidablePred F.sets]

/-- Local rare-vertex predicate in source-style NDS notation. -/
def rare (v : α) : Prop :=
  F.toSetFamily.normalizedDegreeAt v ≤ 0

/-- If NDS is nonpositive, at least one ground element has nonpositive
normalized degree.  This direction is a pure double-counting consequence. -/
theorem exists_rare_of_nds_le_zero
    (hN : F.toSetFamily.nds ≤ 0) :
    ∃ v ∈ F.ground, F.rare v := by
  classical
  have hsum :
      ∑ v ∈ F.ground, F.toSetFamily.normalizedDegreeAt v =
        F.toSetFamily.nds :=
    SetFamily.sum_normalizedDegree_over_ground_eq_nds (SF := F.toSetFamily)
  by_contra hno
  have hpos :
      ∀ v ∈ F.ground, 0 < F.toSetFamily.normalizedDegreeAt v := by
    intro v hv
    have hnrare : ¬ F.rare v := by
      intro hvRare
      exact hno ⟨v, hv, hvRare⟩
    exact lt_of_not_ge hnrare
  have hone :
      ∀ v ∈ F.ground, (1 : ℤ) ≤ F.toSetFamily.normalizedDegreeAt v := by
    intro v hv
    exact Int.add_one_le_iff.mpr (hpos v hv)
  have hsum_ge :
      (F.ground.card : ℤ) ≤
        ∑ v ∈ F.ground, F.toSetFamily.normalizedDegreeAt v := by
    calc
      (F.ground.card : ℤ)
          = ∑ _v ∈ F.ground, (1 : ℤ) := by
            simp [Finset.sum_const]
      _ ≤ ∑ v ∈ F.ground, F.toSetFamily.normalizedDegreeAt v :=
            Finset.sum_le_sum hone
  have hcard_le_zero : (F.ground.card : ℤ) ≤ 0 := by
    exact le_trans (by simpa [hsum] using hsum_ge) hN
  have hcard_pos : 0 < (F.ground.card : ℤ) := by
    exact_mod_cast F.ground_card_pos
  omega

/-- When the ground has one element, the carrier is exactly `{∅, ground}`. -/
theorem carrier_eq_pair_card_one
    (h1 : F.ground.card = 1) :
    F.toSetFamily.carrier = {∅, F.ground} := by
  classical
  apply Finset.ext
  intro s
  constructor
  · intro hs
    have hsub : s ⊆ F.ground :=
      ((SetFamily.mem_carrier_iff (SF := F.toSetFamily)).mp hs).1
    have hcard_le : s.card ≤ 1 := by
      simpa [h1] using Finset.card_le_card hsub
    interval_cases hcard : s.card
    · have hs_empty : s = ∅ := Finset.card_eq_zero.mp hcard
      simp [hs_empty]
    · have hs_ground : s = F.ground := by
        apply Finset.eq_of_subset_of_card_le hsub
        simp [h1, hcard]
      simp [hs_ground]
  · intro hs
    rcases Finset.mem_insert.mp hs with hs_empty | hs_ground
    · rw [hs_empty]
      exact F.empty_mem_carrier
    · rw [Finset.mem_singleton.mp hs_ground]
      exact F.ground_mem_carrier

/-- The NDS value is zero for a one-point ground. -/
theorem nds_eq_zero_card_one
    (h1 : F.ground.card = 1) :
    F.toSetFamily.nds = 0 := by
  classical
  have hCarrier := carrier_eq_pair_card_one (F := F) h1
  have hGround_ne_empty : F.ground ≠ (∅ : Finset α) := by
    intro h
    have : F.ground.card = 0 := by simp [h]
    omega
  have hEmpty_not_ground : (∅ : Finset α) ≠ F.ground := by
    exact hGround_ne_empty.symm
  have hTotal :
      F.toSetFamily.totalSize = (1 : ℤ) := by
    simp [
      SetFamily.totalSize,
      SetFamily.totalSizeNat,
      hCarrier,
      hEmpty_not_ground,
      h1
    ]
  have hEdges :
      F.toSetFamily.numEdges = (2 : ℤ) := by
    simp [
      SetFamily.numEdges,
      SetFamily.numEdgesNat,
      hCarrier,
      hEmpty_not_ground
    ]
  simp [SetFamily.nds, hTotal, hEdges, h1]

/-- The one-point ground base case as an inequality. -/
theorem nds_nonpos_card_one
    (h1 : F.ground.card = 1) :
    F.toSetFamily.nds ≤ 0 := by
  rw [nds_eq_zero_card_one (F := F) h1]

/-- If `v ∈ ground` and `{v}` is not a member of the ideal family, then the
only member containing `v` is the top element, so `degreeNat v = 1`. -/
theorem degreeNat_eq_one_of_not_singleton
    {v : α} (hv : v ∈ F.ground) (hnot : ¬ F.sets ({v} : Finset α)) :
    F.toSetFamily.degreeNat v = 1 := by
  classical
  have hS : F.toSetFamily.S v = {F.ground} := by
    apply Finset.ext
    intro s
    constructor
    · intro hs
      have hsCarrier : s ∈ F.toSetFamily.carrier := (Finset.mem_filter.mp hs).1
      have hvs : v ∈ s := (Finset.mem_filter.mp hs).2
      have hsSet : F.sets s :=
        ((SetFamily.mem_carrier_iff (SF := F.toSetFamily)).mp hsCarrier).2
      by_cases htop : s = F.ground
      · simp [htop]
      · have hsing : F.sets ({v} : Finset α) := by
          exact F.down_closed hsSet htop (Finset.singleton_subset_iff.mpr hvs)
        exact False.elim (hnot hsing)
    · intro hs
      have htop : s = F.ground := by
        simpa using hs
      rw [htop]
      exact Finset.mem_filter.mpr ⟨F.ground_mem_carrier, hv⟩
  calc
    F.toSetFamily.degreeNat v = (F.toSetFamily.S v).card := by
      rfl
    _ = 1 := by
      simp [hS]

end Ideal
end IdealFamily

namespace MathCert.UnionClosed

open Finset

variable {α : Type} [DecidableEq α]

/-- Checked local wrapper from port-level NDS nonpositivity to local average rarity. -/
theorem localIdealFamily_averageRare_of_port_nds_nonpos
    {F : Family α} {U : Finset α} (h : IsIdealFamilyOn F U)
    (hnds : (toPortIdeal F U h).toSetFamily.nds ≤ 0) :
    IsAverageRareOn F U :=
  localIdealFamily_averageRare_of_port_nds h hnds

end MathCert.UnionClosed
