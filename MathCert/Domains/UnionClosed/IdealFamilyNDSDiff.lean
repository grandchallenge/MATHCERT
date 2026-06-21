import MathCert.Domains.UnionClosed.IdealFamilyTrace
import MathCert.Domains.UnionClosed.IdealFamilyContraction
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Data.Finset.Card
import Mathlib.Data.Finset.Powerset
import Mathlib.Tactic.Ring
import Mathlib.Data.Int.Basic

/-!
# Exact NDS trace-difference formula

For an ideal family `F` and a vertex `v`, this file proves the exact
one-step NDS difference under the trace at `v`:

`nds(F) - nds(trace_v F) = normalizedDegreeAt v
  + sum_{t in contr ∩ del} (2 * |t| - (|ground| - 1))`.
-/

namespace IdealFamily
namespace Ideal

open Finset
open scoped BigOperators

noncomputable section

variable {α : Type*} [DecidableEq α]
variable (F : Ideal α) [DecidablePred F.sets]
variable (v : α)

private def sumZ (X : Finset (Finset α)) : ℤ :=
  ∑ s ∈ X, (s.card : ℤ)

/-- Carrier decomposition: members avoiding `v` union members containing `v`. -/
theorem carrier_eq_del_union_S :
    F.toSetFamily.carrier =
      F.toSetFamily.delCarrier v ∪ F.toSetFamily.S v := by
  classical
  apply Finset.ext
  intro t
  constructor
  · intro ht
    by_cases hv : v ∈ t
    · exact Finset.mem_union.mpr
        (Or.inr (Finset.mem_filter.mpr ⟨ht, hv⟩))
    · exact Finset.mem_union.mpr
        (Or.inl (Finset.mem_filter.mpr ⟨ht, hv⟩))
  · intro ht
    rcases Finset.mem_union.mp ht with hdel | hs
    · exact (Finset.mem_filter.mp hdel).1
    · exact (Finset.mem_filter.mp hs).1

/-- The deletion side and containing side are disjoint. -/
theorem disjoint_del_S :
    Disjoint (F.toSetFamily.delCarrier v) (F.toSetFamily.S v) := by
  classical
  refine Finset.disjoint_left.mpr ?_
  intro t hdel hs
  exact (Finset.mem_filter.mp hdel).2 (Finset.mem_filter.mp hs).2

/-- Edge count split on the original family. -/
theorem numEdges_split_F :
    F.toSetFamily.numEdges =
      ((F.toSetFamily.delCarrier v).card : ℤ) +
        ((F.toSetFamily.S v).card : ℤ) := by
  classical
  unfold SetFamily.numEdges SetFamily.numEdgesNat
  have hcarrier := carrier_eq_del_union_S (F := F) (v := v)
  have hdis := disjoint_del_S (F := F) (v := v)
  calc
    ((F.toSetFamily.carrier.card : ℕ) : ℤ)
        = (((F.toSetFamily.delCarrier v ∪ F.toSetFamily.S v).card : ℕ) : ℤ) := by
          rw [hcarrier]
    _ = ((((F.toSetFamily.delCarrier v).card + (F.toSetFamily.S v).card) : ℕ) : ℤ) := by
          rw [Finset.card_union_of_disjoint hdis]
    _ = ((F.toSetFamily.delCarrier v).card : ℤ) +
          ((F.toSetFamily.S v).card : ℤ) := by
          norm_num

/-- Total size split on the original family. -/
theorem totalSize_split_F :
    F.toSetFamily.totalSize =
      sumZ (F.toSetFamily.delCarrier v) + sumZ (F.toSetFamily.S v) := by
  classical
  unfold SetFamily.totalSize SetFamily.totalSizeNat sumZ
  rw [carrier_eq_del_union_S (F := F) (v := v)]
  rw [Finset.sum_union (disjoint_del_S (F := F) (v := v))]
  norm_cast

/-- Total size split on the traced family as `del ∪ (contr \ del)`. -/
theorem totalSize_split_trace
    (hne : (F.ground.erase v).Nonempty) :
    (F.traceIdeal v hne).toSetFamily.totalSize =
      sumZ (F.toSetFamily.delCarrier v) +
        sumZ (F.toSetFamily.contrCarrier v \ F.toSetFamily.delCarrier v) := by
  classical
  have hTrace :=
    trace_carrier_eq_del_union_contr (F := F) (v := v) hne
  have hUnion :
      F.toSetFamily.delCarrier v ∪ F.toSetFamily.contrCarrier v =
        F.toSetFamily.delCarrier v ∪
          (F.toSetFamily.contrCarrier v \ F.toSetFamily.delCarrier v) := by
    exact Eq.symm Finset.union_sdiff_self_eq_union
  have hdis :
      Disjoint (F.toSetFamily.delCarrier v)
        (F.toSetFamily.contrCarrier v \ F.toSetFamily.delCarrier v) := by
    exact Finset.disjoint_sdiff
  unfold SetFamily.totalSize SetFamily.totalSizeNat sumZ
  rw [hTrace, hUnion]
  rw [Finset.sum_union hdis]
  norm_cast

/-- Edge count on the trace: `|del| + |contr| - |contr ∩ del|`. -/
theorem numEdges_split_trace
    (hne : (F.ground.erase v).Nonempty) :
    (F.traceIdeal v hne).toSetFamily.numEdges =
      ((F.toSetFamily.delCarrier v).card : ℤ) +
        ((F.toSetFamily.contrCarrier v).card : ℤ) -
          ((F.toSetFamily.contrCarrier v ∩
            F.toSetFamily.delCarrier v).card : ℤ) := by
  classical
  have hTrace :=
    trace_carrier_eq_del_union_contr (F := F) (v := v) hne
  have hUnion :
      F.toSetFamily.delCarrier v ∪ F.toSetFamily.contrCarrier v =
        F.toSetFamily.delCarrier v ∪
          (F.toSetFamily.contrCarrier v \ F.toSetFamily.delCarrier v) := by
    exact Eq.symm Finset.union_sdiff_self_eq_union
  have hdis :
      Disjoint (F.toSetFamily.delCarrier v)
        (F.toSetFamily.contrCarrier v \ F.toSetFamily.delCarrier v) := by
    exact Finset.disjoint_sdiff
  have hinterSub :
      F.toSetFamily.contrCarrier v ∩ F.toSetFamily.delCarrier v ⊆
        F.toSetFamily.contrCarrier v := by
    intro t ht
    exact (Finset.mem_inter.mp ht).1
  unfold SetFamily.numEdges SetFamily.numEdgesNat
  calc
    (((F.traceIdeal v hne).toSetFamily.carrier.card : ℕ) : ℤ)
        =
      (((F.toSetFamily.delCarrier v ∪
          (F.toSetFamily.contrCarrier v \ F.toSetFamily.delCarrier v)).card : ℕ) : ℤ) := by
          rw [hTrace, hUnion]
    _ =
      ((((F.toSetFamily.delCarrier v).card +
          (F.toSetFamily.contrCarrier v \ F.toSetFamily.delCarrier v).card) : ℕ) : ℤ) := by
          rw [Finset.card_union_of_disjoint hdis]
    _ =
      ((F.toSetFamily.delCarrier v).card : ℤ) +
        ((F.toSetFamily.contrCarrier v \ F.toSetFamily.delCarrier v).card : ℤ) := by
          norm_num
    _ =
      ((F.toSetFamily.delCarrier v).card : ℤ) +
        (((F.toSetFamily.contrCarrier v).card : ℤ) -
          ((F.toSetFamily.contrCarrier v ∩
            F.toSetFamily.delCarrier v).card : ℤ)) := by
          have hNat :
              (F.toSetFamily.contrCarrier v \ F.toSetFamily.delCarrier v).card =
                (F.toSetFamily.contrCarrier v).card -
                  (F.toSetFamily.contrCarrier v ∩
                    F.toSetFamily.delCarrier v).card := by
            simpa [Finset.inter_comm] using
              (Finset.card_sdiff :
                #(F.toSetFamily.contrCarrier v \ F.toSetFamily.delCarrier v) =
                  #(F.toSetFamily.contrCarrier v) -
                    #(F.toSetFamily.delCarrier v ∩ F.toSetFamily.contrCarrier v))
          have hLe :
              (F.toSetFamily.contrCarrier v ∩
                F.toSetFamily.delCarrier v).card ≤
                  (F.toSetFamily.contrCarrier v).card :=
            Finset.card_le_card hinterSub
          rw [hNat]
          norm_num [Nat.cast_sub hLe]
    _ =
      ((F.toSetFamily.delCarrier v).card : ℤ) +
        ((F.toSetFamily.contrCarrier v).card : ℤ) -
          ((F.toSetFamily.contrCarrier v ∩
            F.toSetFamily.delCarrier v).card : ℤ) := by
          ring

/-- Contraction cardinality and total-size identities packaged together. -/
theorem contr_count_and_sum :
    (((F.toSetFamily.contrCarrier v).card : ℤ) =
        ((F.toSetFamily.S v).card : ℤ)) ∧
      ((∑ t ∈ F.toSetFamily.contrCarrier v, (t.card : ℤ)) =
        ∑ s ∈ F.toSetFamily.S v, ((s.card : ℤ) - 1)) := by
  classical
  constructor
  · exact congrArg (fun n : ℕ => (n : ℤ))
      (SetFamily.card_contr_eq_cardS (SF := F.toSetFamily) (v := v))
  · exact SetFamily.sum_card_contr_eq_sum_cardS_sub_one
      (SF := F.toSetFamily) (v := v)

/-- Delta of total sizes under trace. -/
theorem delta_total_size
    (hne : (F.ground.erase v).Nonempty) :
    F.toSetFamily.totalSize -
        (F.traceIdeal v hne).toSetFamily.totalSize =
      ((F.toSetFamily.S v).card : ℤ) +
        (∑ t ∈ (F.toSetFamily.contrCarrier v ∩ F.toSetFamily.delCarrier v),
          (t.card : ℤ)) := by
  classical
  let Sset := F.toSetFamily.S v
  let Dset := F.toSetFamily.delCarrier v
  let Cset := F.toSetFamily.contrCarrier v
  let Diff := Cset \ Dset
  let Inter := Cset ∩ Dset
  have hF := totalSize_split_F (F := F) (v := v)
  have hT := totalSize_split_trace (F := F) (v := v) hne
  have hsplitC : sumZ Cset = sumZ Diff + sumZ Inter := by
    have hunion : Diff ∪ Inter = Cset := by
      simp [Diff, Inter, Cset, Dset, Finset.sdiff_union_inter]
    have hdis : Disjoint Diff Inter := by
      simp [Diff, Inter, Cset, Dset]
      exact Finset.disjoint_sdiff_inter Cset Dset
    unfold sumZ
    rw [← hunion, Finset.sum_union hdis]
  have hContr := contr_count_and_sum (F := F) (v := v)
  have hSumC : sumZ Cset = ∑ s ∈ Sset, ((s.card : ℤ) - 1) := by
    simpa [Cset, Sset, sumZ] using hContr.right
  have hDelta0 :
      F.toSetFamily.totalSize -
          (F.traceIdeal v hne).toSetFamily.totalSize =
        sumZ Sset - sumZ Diff := by
    rw [hF, hT]
    simp [Sset, Dset, Cset, Diff, sumZ]
  have hDiff : sumZ Diff = sumZ Cset - sumZ Inter := by
    omega
  have hSumShift :
      sumZ Sset - ∑ s ∈ Sset, ((s.card : ℤ) - 1) =
        (Sset.card : ℤ) := by
    unfold sumZ
    calc
      (∑ s ∈ Sset, (s.card : ℤ)) -
          ∑ s ∈ Sset, ((s.card : ℤ) - 1)
          =
        ∑ s ∈ Sset, ((s.card : ℤ) - ((s.card : ℤ) - 1)) := by
          rw [← Finset.sum_sub_distrib]
      _ = ∑ _s ∈ Sset, (1 : ℤ) := by
          refine Finset.sum_congr rfl ?_
          intro s hs
          ring
      _ = (Sset.card : ℤ) := by
          simp [Finset.sum_const]
  calc
    F.toSetFamily.totalSize -
        (F.traceIdeal v hne).toSetFamily.totalSize
        = sumZ Sset - sumZ Diff := hDelta0
    _ = sumZ Sset - (sumZ Cset - sumZ Inter) := by
          rw [hDiff]
    _ = (sumZ Sset - ∑ s ∈ Sset, ((s.card : ℤ) - 1)) +
          sumZ Inter := by
          rw [hSumC]
          ring
    _ = ((F.toSetFamily.S v).card : ℤ) +
          (∑ t ∈ (F.toSetFamily.contrCarrier v ∩ F.toSetFamily.delCarrier v),
            (t.card : ℤ)) := by
          rw [hSumShift]
          rfl

/-- Edge-level combination under trace. -/
theorem edges_combo
    (hne : (F.ground.erase v).Nonempty) :
    - F.toSetFamily.numEdges * (F.ground.card : ℤ) +
        (F.traceIdeal v hne).toSetFamily.numEdges *
          ((F.ground.card : ℤ) - 1)
      =
    - (((F.toSetFamily.delCarrier v).card : ℤ) +
        ((F.toSetFamily.S v).card : ℤ)) -
      ((F.ground.card : ℤ) - 1) *
        ((F.toSetFamily.contrCarrier v ∩
          F.toSetFamily.delCarrier v).card : ℤ) := by
  classical
  have hF := numEdges_split_F (F := F) (v := v)
  have hT := numEdges_split_trace (F := F) (v := v) hne
  have hCard :
      ((F.toSetFamily.contrCarrier v).card : ℤ) =
        ((F.toSetFamily.S v).card : ℤ) :=
    (contr_count_and_sum (F := F) (v := v)).left
  rw [hF, hT, hCard]
  ring

omit [DecidablePred F.sets] in
/-- Cast `|ground.erase v|` to `ℤ` as `|ground| - 1`. -/
theorem card_ground_erase_z
    (hv : v ∈ F.ground) :
    ((F.ground.erase v).card : ℤ) = (F.ground.card : ℤ) - 1 := by
  have hNat : (F.ground.erase v).card + 1 = F.ground.card :=
    Finset.card_erase_add_one hv
  have hInt : ((F.ground.erase v).card : ℤ) + 1 =
      (F.ground.card : ℤ) := by
    exact_mod_cast hNat
  omega

/-- Rewrite the normalized-degree term into deletion/containing counts. -/
theorem degree_numEdges_combo :
    (2 : ℤ) * F.toSetFamily.degree v - F.toSetFamily.numEdges =
      (2 : ℤ) * ((F.toSetFamily.S v).card : ℤ) -
        (((F.toSetFamily.delCarrier v).card : ℤ) +
          ((F.toSetFamily.S v).card : ℤ)) := by
  classical
  have hEdges := numEdges_split_F (F := F) (v := v)
  rw [hEdges]
  rfl

/-- Linearize the intersection contribution. -/
theorem inter_sum_linear :
    (2 : ℤ) *
        (∑ t ∈ (F.toSetFamily.contrCarrier v ∩ F.toSetFamily.delCarrier v),
          (t.card : ℤ)) -
      ((F.ground.card : ℤ) - 1) *
        ((F.toSetFamily.contrCarrier v ∩
          F.toSetFamily.delCarrier v).card : ℤ)
      =
    (∑ t ∈ (F.toSetFamily.contrCarrier v ∩ F.toSetFamily.delCarrier v),
      ((2 : ℤ) * (t.card : ℤ))) -
      ∑ _t ∈ (F.toSetFamily.contrCarrier v ∩ F.toSetFamily.delCarrier v),
        ((F.ground.card : ℤ) - 1) := by
  classical
  rw [Finset.mul_sum]
  simp [Finset.sum_const]
  ring

/-- Pack the two intersection sums into a sum of pointwise differences. -/
theorem inter_sum_pack :
    (∑ t ∈ (F.toSetFamily.contrCarrier v ∩ F.toSetFamily.delCarrier v),
      ((2 : ℤ) * (t.card : ℤ))) -
      ∑ _t ∈ (F.toSetFamily.contrCarrier v ∩ F.toSetFamily.delCarrier v),
        ((F.ground.card : ℤ) - 1)
      =
    ∑ t ∈ (F.toSetFamily.contrCarrier v ∩ F.toSetFamily.delCarrier v),
      ((2 : ℤ) * (t.card : ℤ) - ((F.ground.card : ℤ) - 1)) := by
  classical
  rw [← Finset.sum_sub_distrib]

/-- Exact one-step difference formula under trace. -/
theorem nds_diff_trace_as_normdeg
    (hv : v ∈ F.ground)
    (hne : (F.ground.erase v).Nonempty) :
    F.toSetFamily.nds - (F.traceIdeal v hne).toSetFamily.nds =
      F.toSetFamily.normalizedDegreeAt v +
        ∑ t ∈ (F.toSetFamily.contrCarrier v ∩ F.toSetFamily.delCarrier v),
          ((2 : ℤ) * (t.card : ℤ) - ((F.ground.card : ℤ) - 1)) := by
  classical
  have hDelta := delta_total_size (F := F) (v := v) hne
  have hEdges := edges_combo (F := F) (v := v) hne
  have hGround := card_ground_erase_z (F := F) (v := v) hv
  have hDegEdges := degree_numEdges_combo (F := F) (v := v)
  have hInterLin := inter_sum_linear (F := F) (v := v)
  have hInterPack := inter_sum_pack (F := F) (v := v)
  unfold SetFamily.nds
  calc
    (2 : ℤ) * F.toSetFamily.totalSize -
          F.toSetFamily.numEdges * (F.ground.card : ℤ) -
        ((2 : ℤ) * (F.traceIdeal v hne).toSetFamily.totalSize -
          (F.traceIdeal v hne).toSetFamily.numEdges *
            (((F.ground.erase v).card : ℤ)))
        =
      (2 : ℤ) *
          (F.toSetFamily.totalSize -
            (F.traceIdeal v hne).toSetFamily.totalSize) +
        (- F.toSetFamily.numEdges * (F.ground.card : ℤ) +
          (F.traceIdeal v hne).toSetFamily.numEdges *
            (((F.ground.erase v).card : ℤ))) := by
          ring
    _ =
      (2 : ℤ) *
          (((F.toSetFamily.S v).card : ℤ) +
            (∑ t ∈
              (F.toSetFamily.contrCarrier v ∩ F.toSetFamily.delCarrier v),
              (t.card : ℤ))) +
        (- F.toSetFamily.numEdges * (F.ground.card : ℤ) +
          (F.traceIdeal v hne).toSetFamily.numEdges *
            (((F.ground.erase v).card : ℤ))) := by
          rw [hDelta]
    _ =
      (2 : ℤ) *
          (((F.toSetFamily.S v).card : ℤ) +
            (∑ t ∈
              (F.toSetFamily.contrCarrier v ∩ F.toSetFamily.delCarrier v),
              (t.card : ℤ))) +
        (- F.toSetFamily.numEdges * (F.ground.card : ℤ) +
          (F.traceIdeal v hne).toSetFamily.numEdges *
            ((F.ground.card : ℤ) - 1)) := by
          rw [hGround]
    _ =
      ((2 : ℤ) * ((F.toSetFamily.S v).card : ℤ) -
          (((F.toSetFamily.delCarrier v).card : ℤ) +
            ((F.toSetFamily.S v).card : ℤ))) +
        ((2 : ℤ) *
            (∑ t ∈
              (F.toSetFamily.contrCarrier v ∩ F.toSetFamily.delCarrier v),
              (t.card : ℤ)) -
          ((F.ground.card : ℤ) - 1) *
            ((F.toSetFamily.contrCarrier v ∩
              F.toSetFamily.delCarrier v).card : ℤ)) := by
          rw [hEdges]
          ring
    _ =
      ((2 : ℤ) * F.toSetFamily.degree v - F.toSetFamily.numEdges) +
        ((∑ t ∈
            (F.toSetFamily.contrCarrier v ∩ F.toSetFamily.delCarrier v),
            ((2 : ℤ) * (t.card : ℤ))) -
          ∑ _t ∈
            (F.toSetFamily.contrCarrier v ∩ F.toSetFamily.delCarrier v),
            ((F.ground.card : ℤ) - 1)) := by
          rw [← hDegEdges]
          rw [hInterLin]
    _ =
      F.toSetFamily.normalizedDegreeAt v +
        ∑ t ∈ (F.toSetFamily.contrCarrier v ∩ F.toSetFamily.delCarrier v),
          ((2 : ℤ) * (t.card : ℤ) - ((F.ground.card : ℤ) - 1)) := by
          rw [hInterPack]
          rfl

/-- If `degreeNat v = 1`, then the containing side consists only of the top
element. -/
theorem S_eq_singleton_ground_of_degreeNat_eq_one
    (hv : v ∈ F.ground)
    (hdeg : F.toSetFamily.degreeNat v = 1) :
    F.toSetFamily.S v = {F.ground} := by
  classical
  have hcard : (F.toSetFamily.S v).card = 1 := by
    simpa [SetFamily.degreeNat] using hdeg
  have hmem : F.ground ∈ F.toSetFamily.S v :=
    Finset.mem_filter.mpr ⟨F.ground_mem_carrier, hv⟩
  obtain ⟨s, hs⟩ := Finset.card_eq_one.mp hcard
  have hground : F.ground = s := by
    have : F.ground ∈ ({s} : Finset (Finset α)) := by
      simpa [hs] using hmem
    simpa using this
  rw [hs, hground]

/-- Degree-one specialization when `ground.erase v` is not a member: the
intersection block is empty, so the NDS drop is exactly the normalized degree. -/
theorem nds_diff_deg1_groundErase_notin
    (hv : v ∈ F.ground)
    (hdeg : F.toSetFamily.degreeNat v = 1)
    (hne : (F.ground.erase v).Nonempty)
    (hnot : ¬ F.sets (F.ground.erase v)) :
    F.toSetFamily.nds - (F.traceIdeal v hne).toSetFamily.nds =
      F.toSetFamily.normalizedDegreeAt v := by
  classical
  let P : Finset α := F.ground.erase v
  have hSsingle :
      F.toSetFamily.S v = {F.ground} :=
    S_eq_singleton_ground_of_degreeNat_eq_one
      (F := F) (v := v) hv hdeg
  have hContr :
      F.toSetFamily.contrCarrier v = {P} := by
    rw [SetFamily.contrCarrier, hSsingle]
    simp [P]
  have hP_not_del : P ∉ F.toSetFamily.delCarrier v := by
    intro hP
    have hCarrier : P ∈ F.toSetFamily.carrier :=
      (Finset.mem_filter.mp hP).1
    have hSet : F.sets P :=
      ((SetFamily.mem_carrier_iff (SF := F.toSetFamily)).mp hCarrier).2
    exact hnot (by simpa [P] using hSet)
  have hInter :
      F.toSetFamily.contrCarrier v ∩ F.toSetFamily.delCarrier v =
        (∅ : Finset (Finset α)) := by
    apply Finset.ext
    intro t
    constructor
    · intro ht
      have htContr : t ∈ F.toSetFamily.contrCarrier v :=
        (Finset.mem_inter.mp ht).1
      have htDel : t ∈ F.toSetFamily.delCarrier v :=
        (Finset.mem_inter.mp ht).2
      have htP : t = P := by
        simpa [hContr] using htContr
      rw [htP] at htDel
      exact False.elim (hP_not_del htDel)
    · intro ht
      exact False.elim (Finset.notMem_empty t ht)
  have hdiff :=
    nds_diff_trace_as_normdeg (F := F) (v := v) hv hne
  simpa [hInter] using hdiff

/-- Degree-one specialization when `ground.erase v` is a member: the NDS
drop to the trace is nonpositive. -/
theorem nds_diff_deg1_groundErase_in_nonpos
    (hv : v ∈ F.ground)
    (hdeg : F.toSetFamily.degreeNat v = 1)
    (hne : (F.ground.erase v).Nonempty)
    (hHave : F.sets (F.ground.erase v)) :
    F.toSetFamily.nds - (F.traceIdeal v hne).toSetFamily.nds ≤ 0 := by
  classical
  let P : Finset α := F.ground.erase v
  have hSsingle :
      F.toSetFamily.S v = {F.ground} :=
    S_eq_singleton_ground_of_degreeNat_eq_one
      (F := F) (v := v) hv hdeg
  have hContr :
      F.toSetFamily.contrCarrier v = {P} := by
    rw [SetFamily.contrCarrier, hSsingle]
    simp [P]
  have hP_in_del : P ∈ F.toSetFamily.delCarrier v := by
    have hP_sub : P ⊆ F.ground := by
      intro x hx
      exact Finset.mem_of_mem_erase hx
    have hP_carrier : P ∈ F.toSetFamily.carrier :=
      (SetFamily.mem_carrier_iff (SF := F.toSetFamily)).mpr
        ⟨hP_sub, by simpa [P] using hHave⟩
    exact Finset.mem_filter.mpr ⟨hP_carrier, by simp [P]⟩
  have hInter :
      F.toSetFamily.contrCarrier v ∩ F.toSetFamily.delCarrier v = {P} := by
    apply Finset.ext
    intro t
    constructor
    · intro ht
      have htContr : t ∈ F.toSetFamily.contrCarrier v :=
        (Finset.mem_inter.mp ht).1
      have htP : t = P := by
        simpa [hContr] using htContr
      simp [htP]
    · intro ht
      have htP : t = P := by
        simpa using ht
      rw [htP]
      exact Finset.mem_inter.mpr ⟨by simp [hContr], hP_in_del⟩
  have hTerm :
      (2 : ℤ) * (P.card : ℤ) - ((F.ground.card : ℤ) - 1) =
        (P.card : ℤ) := by
    have hErase := card_ground_erase_z (F := F) (v := v) hv
    have hPcard : (P.card : ℤ) = (F.ground.card : ℤ) - 1 := by
      simpa [P] using hErase
    rw [← hPcard]
    ring
  have hdiff :
      F.toSetFamily.nds - (F.traceIdeal v hne).toSetFamily.nds =
        F.toSetFamily.normalizedDegreeAt v + (P.card : ℤ) := by
    have hmain := nds_diff_trace_as_normdeg (F := F) (v := v) hv hne
    simpa [hInter, hTerm] using hmain
  have hNorm :
      F.toSetFamily.normalizedDegreeAt v =
        (2 : ℤ) - F.toSetFamily.numEdges := by
    have hdegZ : F.toSetFamily.degree v = (1 : ℤ) := by
      change ((F.toSetFamily.degreeNat v : ℕ) : ℤ) = 1
      exact_mod_cast hdeg
    simp [SetFamily.normalizedDegreeAt, hdegZ]

  have hP_ne_ground : P ≠ F.ground := by
    intro hPtop
    have hvP : v ∈ P := by
      simpa [hPtop] using hv
    exact (by simp [P] at hvP)

  let T : Finset (Finset α) :=
    insert F.ground (insert (∅ : Finset α) (P.image fun u => ({u} : Finset α)))
  have hT_sub : T ⊆ F.toSetFamily.carrier := by
    intro t ht
    rcases Finset.mem_insert.mp ht with htTop | htRest
    · rw [htTop]
      exact F.ground_mem_carrier
    · rcases Finset.mem_insert.mp htRest with htEmpty | htImage
      · rw [htEmpty]
        exact F.empty_mem_carrier
      · rcases Finset.mem_image.mp htImage with ⟨u, huP, rfl⟩
        have hsing_sub_P : ({u} : Finset α) ⊆ P := by
          intro x hx
          have hx_eq : x = u := by
            simpa using hx
          simpa [hx_eq] using huP
        have hsing_sets : F.sets ({u} : Finset α) := by
          exact F.down_closed
            (A := ({u} : Finset α)) (B := P)
            (by simpa [P] using hHave) hP_ne_ground hsing_sub_P
        have hsing_sub_ground : ({u} : Finset α) ⊆ F.ground := by
          intro x hx
          have hx_eq : x = u := by
            simpa using hx
          rw [hx_eq]
          exact Finset.mem_of_mem_erase huP
        exact (SetFamily.mem_carrier_iff (SF := F.toSetFamily)).mpr
          ⟨hsing_sub_ground, hsing_sets⟩
  have hImageCard :
      (P.image fun u => ({u} : Finset α)).card = P.card := by
    exact Finset.card_image_iff.mpr
      (by
        intro x hx y hy hxy
        simpa [Finset.ext_iff] using hxy)
  have hEmpty_not_image :
      (∅ : Finset α) ∉ P.image fun u => ({u} : Finset α) := by
    intro h
    rcases Finset.mem_image.mp h with ⟨u, hu, huEq⟩
    have hne : ({u} : Finset α).Nonempty := by
      exact ⟨u, by simp⟩
    rw [huEq] at hne
    exact Finset.not_nonempty_empty hne
  have hGround_not_rest :
      F.ground ∉ insert (∅ : Finset α) (P.image fun u => ({u} : Finset α)) := by
    intro h
    rcases Finset.mem_insert.mp h with hEmpty | hImage
    · have : v ∈ (∅ : Finset α) := by
        simp [hEmpty] at hv
      exact Finset.notMem_empty v this
    · rcases Finset.mem_image.mp hImage with ⟨u, huP, hUeq⟩
      have hvSingleton : v ∈ ({u} : Finset α) := by
        simpa [hUeq] using hv
      have hneq : u ≠ v := (Finset.mem_erase.mp huP).1
      have hvu : v = u := by
        simpa using hvSingleton
      exact hneq hvu.symm
  have hT_card : T.card = P.card + 2 := by
    have h1 :
        (insert (∅ : Finset α) (P.image fun u => ({u} : Finset α))).card =
          (P.image fun u => ({u} : Finset α)).card + 1 :=
      Finset.card_insert_of_notMem hEmpty_not_image
    have h2 :
        T.card =
          (insert (∅ : Finset α) (P.image fun u => ({u} : Finset α))).card + 1 :=
      Finset.card_insert_of_notMem hGround_not_rest
    calc
      T.card =
          (insert (∅ : Finset α) (P.image fun u => ({u} : Finset α))).card + 1 := h2
      _ = ((P.image fun u => ({u} : Finset α)).card + 1) + 1 := by
          rw [h1]
      _ = (P.card + 1) + 1 := by
          rw [hImageCard]
      _ = P.card + 2 := by
          omega
  have hEdges_ge_nat :
      P.card + 2 ≤ F.toSetFamily.carrier.card := by
    rw [← hT_card]
    exact Finset.card_le_card hT_sub
  have hEdges_ge_int :
      (P.card : ℤ) + 2 ≤ (F.toSetFamily.carrier.card : ℤ) := by
    exact_mod_cast hEdges_ge_nat
  have hdiff_rewrite :
      F.toSetFamily.nds - (F.traceIdeal v hne).toSetFamily.nds =
        ((P.card : ℤ) + 2) - (F.toSetFamily.carrier.card : ℤ) := by
    rw [hdiff, hNorm]
    simp [SetFamily.numEdges, SetFamily.numEdgesNat]
    ring
  rw [hdiff_rewrite]
  exact sub_nonpos.mpr hEdges_ge_int

end
end Ideal
end IdealFamily
