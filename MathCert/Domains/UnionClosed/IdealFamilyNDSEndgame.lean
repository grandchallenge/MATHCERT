import MathCert.Domains.UnionClosed.IdealFamilyNDS
import MathCert.Domains.UnionClosed.IdealFamilyNDSDiff
import Mathlib.Tactic

/-!
# Ideal-family NDS endgame

This file closes the local NDS nonpositivity proof for the ported
ideal-family surface.  The proof uses the checked rare-vertex theorem, the
trace-difference formula, degree-one trace branches, and the singleton
contraction branch.
-/

namespace IdealFamily
namespace Ideal

open Finset
open scoped BigOperators

noncomputable section

variable {α : Type*} [DecidableEq α]

/-- Removing a member from a finite set of cardinal at least two leaves a
nonempty set. -/
theorem erase_nonempty_of_two_le_card
    {U : Finset α} {v : α} (hv : v ∈ U) (h2 : 2 ≤ U.card) :
    (U.erase v).Nonempty := by
  have hcard : 0 < (U.erase v).card := by
    rw [Finset.card_erase_of_mem hv]
    omega
  exact Finset.card_pos.mp hcard

variable (F : Ideal α) [DecidablePred F.sets]
variable (v : α)

/-- Any contraction member not already on the deletion side must be the
contracted top element `ground.erase v`. -/
theorem contr_sdiff_del_subset_groundErase
    : F.toSetFamily.contrCarrier v \ F.toSetFamily.delCarrier v ⊆
      {F.ground.erase v} := by
  classical
  intro t ht
  have htContr : t ∈ F.toSetFamily.contrCarrier v :=
    (Finset.mem_sdiff.mp ht).1
  have htNotDel : t ∉ F.toSetFamily.delCarrier v :=
    (Finset.mem_sdiff.mp ht).2
  rw [SetFamily.contrCarrier] at htContr
  rcases Finset.mem_image.mp htContr with ⟨s, hsS, hts⟩
  have hsCarrier : s ∈ F.toSetFamily.carrier :=
    (Finset.mem_filter.mp hsS).1
  have hvs : v ∈ s :=
    (Finset.mem_filter.mp hsS).2
  have hsInfo :=
    (SetFamily.mem_carrier_iff (SF := F.toSetFamily)).mp hsCarrier
  by_cases htop : s = F.ground
  · have htP : t = F.ground.erase v := by
      rw [← hts, htop]
    simp [htP]
  · have hEraseSet : F.sets (s.erase v) :=
      F.down_closed hsInfo.2 htop (Finset.erase_subset v s)
    have hEraseSub : s.erase v ⊆ F.ground := by
      intro x hx
      exact hsInfo.1 (Finset.mem_of_mem_erase hx)
    have hEraseCarrier : s.erase v ∈ F.toSetFamily.carrier :=
      (SetFamily.mem_carrier_iff (SF := F.toSetFamily)).mpr
        ⟨hEraseSub, hEraseSet⟩
    have hEraseDel : s.erase v ∈ F.toSetFamily.delCarrier v :=
      Finset.mem_filter.mpr ⟨hEraseCarrier, by simp⟩
    have htDel : t ∈ F.toSetFamily.delCarrier v := by
      simpa [hts] using hEraseDel
    exact False.elim (htNotDel htDel)

/-- The intersection block in the singleton branch is bounded above by the
NDS of the singleton contraction ideal. -/
theorem inter_sum_le_contr_nds
    (hv : v ∈ F.ground)
    (hne : (F.ground.erase v).Nonempty)
    (hSing : F.sets ({v} : Finset α)) :
    (∑ t ∈ (F.toSetFamily.contrCarrier v ∩ F.toSetFamily.delCarrier v),
        ((2 : ℤ) * (t.card : ℤ) - ((F.ground.card : ℤ) - 1)))
      ≤ (F.contrIdeal v hv hne hSing).toSetFamily.nds := by
  classical
  let C : Finset (Finset α) := F.toSetFamily.contrCarrier v
  let D : Finset (Finset α) := F.toSetFamily.delCarrier v
  let I : Finset (Finset α) := C ∩ D
  let R : Finset (Finset α) := C \ D
  let g : Finset α → ℤ :=
    fun t => ((2 : ℤ) * (t.card : ℤ) - ((F.ground.card : ℤ) - 1))
  have hUnion : I ∪ R = C := by
    apply Finset.ext
    intro t
    by_cases htC : t ∈ C
    · by_cases htD : t ∈ D
      · simp [I, R, htC, htD]
      · simp [I, R, htC, htD]
    · simp [I, R, htC]
  have hDis : Disjoint I R := by
    refine Finset.disjoint_left.mpr ?_
    intro t htI htR
    exact (Finset.mem_sdiff.mp htR).2 (Finset.mem_inter.mp htI).2
  have hSplit :
      (∑ t ∈ C, g t) = (∑ t ∈ I, g t) + ∑ t ∈ R, g t := by
    calc
      (∑ t ∈ C, g t) = ∑ t ∈ I ∪ R, g t := by
          rw [hUnion]
      _ = (∑ t ∈ I, g t) + ∑ t ∈ R, g t := by
          rw [Finset.sum_union hDis]
  have hRestNonneg : 0 ≤ ∑ t ∈ R, g t := by
    refine Finset.sum_nonneg ?_
    intro t ht
    have htP : t = F.ground.erase v := by
      have hmem :
          t ∈ ({F.ground.erase v} : Finset (Finset α)) :=
        contr_sdiff_del_subset_groundErase (F := F) (v := v) (by simpa [C, D, R] using ht)
      simpa using hmem
    have hTerm : g t = ((F.ground.erase v).card : ℤ) := by
      rw [htP]
      unfold g
      have hPcard := card_ground_erase_z (F := F) (v := v) hv
      rw [hPcard]
      ring
    rw [hTerm]
    exact_mod_cast Nat.zero_le (F.ground.erase v).card
  have hSumI_le_SumC : (∑ t ∈ I, g t) ≤ ∑ t ∈ C, g t := by
    omega
  have hContrCarrier :
      (F.contrIdeal v hv hne hSing).toSetFamily.carrier = C := by
    simpa [C] using
      contrIdeal_carrier_eq_contrCarrier (F := F) (v := v) hv hne hSing
  have hContrNDS :
      (F.contrIdeal v hv hne hSing).toSetFamily.nds =
        ∑ t ∈ C, g t := by
    have hNDS :=
      SetFamily.nds_eq_sum_card_terms
        (SF := (F.contrIdeal v hv hne hSing).toSetFamily)
    have hPcard := card_ground_erase_z (F := F) (v := v) hv
    simpa [hContrCarrier, C, g, hPcard] using hNDS
  calc
    (∑ t ∈ (F.toSetFamily.contrCarrier v ∩ F.toSetFamily.delCarrier v),
        ((2 : ℤ) * (t.card : ℤ) - ((F.ground.card : ℤ) - 1)))
        = ∑ t ∈ I, g t := by
          rfl
    _ ≤ ∑ t ∈ C, g t := hSumI_le_SumC
    _ = (F.contrIdeal v hv hne hSing).toSetFamily.nds := hContrNDS.symm

/-- Singleton branch: if the contraction ideal has nonpositive NDS, then the
trace step at a rare singleton vertex is nonpositive. -/
theorem nds_diff_singleton_nonpos_of_contr_nds
    (hv : v ∈ F.ground)
    (hne : (F.ground.erase v).Nonempty)
    (hSing : F.sets ({v} : Finset α))
    (hRare : F.toSetFamily.normalizedDegreeAt v ≤ 0)
    (hContr :
      (F.contrIdeal v hv hne hSing).toSetFamily.nds ≤ 0) :
    F.toSetFamily.nds - (F.traceIdeal v hne).toSetFamily.nds ≤ 0 := by
  classical
  have hDiff :=
    nds_diff_trace_as_normdeg (F := F) (v := v) hv hne
  have hInterLe :=
    inter_sum_le_contr_nds (F := F) (v := v) hv hne hSing
  have hInterNonpos :
      (∑ t ∈ (F.toSetFamily.contrCarrier v ∩ F.toSetFamily.delCarrier v),
          ((2 : ℤ) * (t.card : ℤ) - ((F.ground.card : ℤ) - 1))) ≤ 0 :=
    le_trans hInterLe hContr
  rw [hDiff]
  exact add_nonpos hRare hInterNonpos

/-- Port-level NDS nonpositivity for finite ideal families. -/
theorem port_nds_nonpos
    (F : Ideal α) [DecidablePred F.sets] :
    F.toSetFamily.nds ≤ 0 := by
  classical
  let P : ℕ → Prop :=
    fun n => ∀ (G : Ideal α), [DecidablePred G.sets] →
      G.ground.card = n → G.toSetFamily.nds ≤ 0
  have hmain : ∀ n, P n := by
    intro n
    induction n using Nat.strong_induction_on with
    | h n IH =>
      intro G hDec hCard
      letI := hDec
      by_cases hOne : G.ground.card = 1
      · exact nds_nonpos_card_one (F := G) hOne
      have hPos : 0 < G.ground.card := G.ground_card_pos
      have hTwo : 2 ≤ G.ground.card := by
        omega
      obtain ⟨v, hv, hRarePort⟩ :=
        ideal_version_of_frankl_conjecture (F := G)
      have hRare : G.toSetFamily.normalizedDegreeAt v ≤ 0 := by
        simpa [
          SetFamily.isRare,
          SetFamily.normalizedDegreeAt
        ] using hRarePort
      have hne : (G.ground.erase v).Nonempty :=
        erase_nonempty_of_two_le_card (U := G.ground) (v := v) hv hTwo
      have hTraceLtN : (G.traceIdeal v hne).ground.card < n := by
        have hlt := trace_ground_card_lt (F := G) (v := v) hv hne
        omega
      have hTraceNDS : (G.traceIdeal v hne).toSetFamily.nds ≤ 0 :=
        IH (G.traceIdeal v hne).ground.card hTraceLtN
          (G := G.traceIdeal v hne) rfl
      by_cases hSing : G.sets ({v} : Finset α)
      · have hContrLtN : (G.contrIdeal v hv hne hSing).ground.card < n := by
          have hlt := contr_ground_card_lt (F := G) (v := v) hv hne hSing
          omega
        have hContrNDS : (G.contrIdeal v hv hne hSing).toSetFamily.nds ≤ 0 :=
          IH (G.contrIdeal v hv hne hSing).ground.card hContrLtN
            (G := G.contrIdeal v hv hne hSing) rfl
        have hDiff :=
          nds_diff_singleton_nonpos_of_contr_nds
            (F := G) (v := v) hv hne hSing hRare hContrNDS
        omega
      · have hDeg : G.toSetFamily.degreeNat v = 1 :=
          degreeNat_eq_one_of_not_singleton (F := G) hv hSing
        by_cases hTopMinus : G.sets (G.ground.erase v)
        · have hDiff :=
            nds_diff_deg1_groundErase_in_nonpos
              (F := G) (v := v) hv hDeg hne hTopMinus
          omega
        · have hDiffEq :=
            nds_diff_deg1_groundErase_notin
              (F := G) (v := v) hv hDeg hne hTopMinus
          have hDiff : G.toSetFamily.nds - (G.traceIdeal v hne).toSetFamily.nds ≤ 0 := by
            rw [hDiffEq]
            exact hRare
          omega
  exact hmain F.ground.card F rfl

end
end Ideal
end IdealFamily

namespace MathCert.UnionClosed

open Finset

variable {α : Type} [DecidableEq α]

/-- The local finite-family ideal bridge supplies port-level NDS
nonpositivity. -/
theorem localIdealFamily_port_nds_nonpos
    {F : Family α} {U : Finset α}
    (h : IsIdealFamilyOn F U) :
    (toPortIdeal F U h).toSetFamily.nds ≤ 0 := by
  classical
  exact _root_.IdealFamily.Ideal.port_nds_nonpos (F := toPortIdeal F U h)

/-- Unconditional local average-rarity theorem for finite ideal families. -/
theorem localIdealFamily_averageRare
    {F : Family α} {U : Finset α}
    (h : IsIdealFamilyOn F U) :
    IsAverageRareOn F U :=
  localIdealFamily_averageRare_of_port_nds_nonpos h
    (localIdealFamily_port_nds_nonpos h)

end MathCert.UnionClosed
