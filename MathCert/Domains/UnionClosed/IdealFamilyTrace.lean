import MathCert.Domains.UnionClosed.IdealFamilyPort.Core
import Mathlib.Data.Finset.Card
import Mathlib.Data.Finset.Powerset

/-!
# Trace ideals for the ideal-family port

This file defines the trace of a ported ideal family at a vertex `v` and proves
the structural carrier identity used by the NDS proof:

`carrier(trace_v F) = delCarrier_v F ∪ contrCarrier_v F`.
-/

namespace IdealFamily
namespace Ideal

open Finset

noncomputable section

variable {α : Type*} [DecidableEq α]
variable (F : Ideal α) [DecidablePred F.sets]
variable (v : α)

omit [DecidablePred F.sets] in
private theorem subset_erase_of_subset_and_not_mem
    {t : Finset α} (htU : t ⊆ F.ground) (hvnot : v ∉ t) :
    t ⊆ F.ground.erase v := by
  intro x hx
  have hxU : x ∈ F.ground := htU hx
  have hxne : x ≠ v := by
    intro hxv
    exact hvnot (by simpa [hxv] using hx)
  exact Finset.mem_erase.mpr ⟨hxne, hxU⟩

/-- Trace membership at `v`: either a member already avoiding `v`, or the
erase-image of a member containing `v`. -/
def traceSets (t : Finset α) : Prop :=
  (F.sets t ∧ v ∉ t) ∨
    ∃ s : Finset α, F.sets s ∧ v ∈ s ∧ t = s.erase v

/-- The traced ideal at `v`, living on `ground.erase v`. -/
def traceIdeal (hne : (F.ground.erase v).Nonempty) : Ideal α :=
  { ground := F.ground.erase v
    sets := traceSets (F := F) v
    inc_ground := by
      intro t ht
      rcases ht with hleft | hright
      · exact subset_erase_of_subset_and_not_mem
          (F := F) (v := v) (F.inc_ground hleft.1) hleft.2
      · rcases hright with ⟨s, hsF, _hvs, ht⟩
        intro x hx
        have hxErase : x ∈ s.erase v := by
          rw [← ht]
          exact hx
        have hxPair := Finset.mem_erase.mp hxErase
        exact Finset.mem_erase.mpr ⟨hxPair.1, F.inc_ground hsF hxPair.2⟩
    nonempty_ground := hne
    has_empty := by
      left
      exact ⟨F.has_empty, by simp⟩
    has_ground := by
      by_cases hvU : v ∈ F.ground
      · right
        exact ⟨F.ground, F.has_ground, hvU, rfl⟩
      · left
        have hEq : F.ground.erase v = F.ground :=
          Finset.erase_eq_of_notMem hvU
        constructor
        · rw [hEq]
          exact F.has_ground
        · rw [hEq]
          exact hvU
    down_closed := by
      intro A B hB hBne hAB
      rcases hB with hleft | hright
      · have hBneU : B ≠ F.ground := by
          intro hBU
          by_cases hvU : v ∈ F.ground
          · exact hleft.2 (by simpa [hBU] using hvU)
          · have hErase : F.ground.erase v = F.ground :=
              Finset.erase_eq_of_notMem hvU
            exact hBne (by simp [hBU, hErase])
        have hAinF : F.sets A :=
          F.down_closed hleft.1 hBneU hAB
        have hvnotA : v ∉ A := by
          intro hvA
          exact hleft.2 (hAB hvA)
        exact Or.inl ⟨hAinF, hvnotA⟩
      · rcases hright with ⟨s, hsF, _hvs, hBdef⟩
        have hAsubS : A ⊆ s := by
          intro x hxA
          have hxB : x ∈ B := hAB hxA
          have hxErase : x ∈ s.erase v := by
            rw [← hBdef]
            exact hxB
          exact (Finset.mem_erase.mp hxErase).2
        have hvnotA : v ∉ A := by
          intro hvA
          have hvB : v ∈ B := hAB hvA
          have hvErase : v ∈ s.erase v := by
            rw [← hBdef]
            exact hvB
          exact (Finset.mem_erase.mp hvErase).1 rfl
        have hs_neU : s ≠ F.ground := by
          intro hsU
          exact hBne (by simpa [hsU] using hBdef)
        have hAinF : F.sets A :=
          F.down_closed hsF hs_neU hAsubS
        exact Or.inl ⟨hAinF, hvnotA⟩ }

omit [DecidablePred F.sets] in
@[simp] theorem traceIdeal_ground (hne : (F.ground.erase v).Nonempty) :
    (F.traceIdeal v hne).ground = F.ground.erase v := by
  rfl

omit [DecidablePred F.sets] in
@[simp] theorem traceIdeal_toSetFamily_ground
    (hne : (F.ground.erase v).Nonempty) :
    (F.traceIdeal v hne).toSetFamily.ground = F.ground.erase v := by
  rfl

omit [DecidablePred F.sets] in
theorem trace_ground_card_lt
    (hv : v ∈ F.ground) (hne : (F.ground.erase v).Nonempty) :
    (F.traceIdeal v hne).ground.card < F.ground.card := by
  rw [traceIdeal_ground]
  exact Finset.card_erase_lt_of_mem hv

omit [DecidablePred F.sets] in
theorem trace_ground_card_eq_pred
    (hv : v ∈ F.ground) (hne : (F.ground.erase v).Nonempty) :
    (F.traceIdeal v hne).ground.card = F.ground.card - 1 := by
  rw [traceIdeal_ground]
  exact Finset.card_erase_of_mem hv

instance traceIdeal_sets_decidable (hne : (F.ground.erase v).Nonempty) :
    DecidablePred ((F.traceIdeal v hne).sets) := by
  classical
  intro t
  exact Classical.dec _

/-- The trace carrier is the union of the deletion carrier and the contraction
carrier. -/
theorem trace_carrier_eq_del_union_contr
    (hne : (F.ground.erase v).Nonempty) :
    (F.traceIdeal v hne).toSetFamily.carrier =
      (F.toSetFamily.delCarrier v) ∪ (F.toSetFamily.contrCarrier v) := by
  classical
  apply Finset.ext
  intro t
  constructor
  · intro ht
    have hTrace :
        traceSets (F := F) v t :=
      ((SetFamily.mem_carrier_iff
        (SF := (F.traceIdeal v hne).toSetFamily)).mp ht).2
    rcases hTrace with hleft | hright
    · have hMemCarrier : t ∈ F.toSetFamily.carrier :=
        (SetFamily.mem_carrier_iff (SF := F.toSetFamily)).mpr
          ⟨F.inc_ground hleft.1, hleft.1⟩
      exact Finset.mem_union.mpr
        (Or.inl (Finset.mem_filter.mpr ⟨hMemCarrier, hleft.2⟩))
    · rcases hright with ⟨s, hsF, hvs, htdef⟩
      have hsCarrier : s ∈ F.toSetFamily.carrier :=
        (SetFamily.mem_carrier_iff (SF := F.toSetFamily)).mpr
          ⟨F.inc_ground hsF, hsF⟩
      have hsS : s ∈ F.toSetFamily.S v :=
        Finset.mem_filter.mpr ⟨hsCarrier, hvs⟩
      have htContr : t ∈ F.toSetFamily.contrCarrier v := by
        rw [SetFamily.contrCarrier]
        exact Finset.mem_image.mpr ⟨s, hsS, htdef.symm⟩
      exact Finset.mem_union.mpr (Or.inr htContr)
  · intro ht
    rcases Finset.mem_union.mp ht with hdel | hcontr
    · have htCarrier : t ∈ F.toSetFamily.carrier :=
        (Finset.mem_filter.mp hdel).1
      have hvnot : v ∉ t :=
        (Finset.mem_filter.mp hdel).2
      have htInfo :=
        (SetFamily.mem_carrier_iff (SF := F.toSetFamily)).mp htCarrier
      have htSubErase :
          t ⊆ F.ground.erase v :=
        subset_erase_of_subset_and_not_mem (F := F) (v := v)
          htInfo.1 hvnot
      exact
        (SetFamily.mem_carrier_iff
          (SF := (F.traceIdeal v hne).toSetFamily)).mpr
          ⟨htSubErase, Or.inl ⟨htInfo.2, hvnot⟩⟩
    · rcases Finset.mem_image.mp hcontr with ⟨s, hsS, htdef⟩
      have hsCarrier : s ∈ F.toSetFamily.carrier :=
        (Finset.mem_filter.mp hsS).1
      have hvs : v ∈ s :=
        (Finset.mem_filter.mp hsS).2
      have hsInfo :=
        (SetFamily.mem_carrier_iff (SF := F.toSetFamily)).mp hsCarrier
      have htSubErase :
          t ⊆ F.ground.erase v := by
        intro x hx
        have hxErase : x ∈ s.erase v := by
          rw [htdef]
          exact hx
        have hxPair := Finset.mem_erase.mp hxErase
        exact Finset.mem_erase.mpr ⟨hxPair.1, hsInfo.1 hxPair.2⟩
      exact
        (SetFamily.mem_carrier_iff
          (SF := (F.traceIdeal v hne).toSetFamily)).mpr
          ⟨htSubErase, Or.inr ⟨s, hsInfo.2, hvs, htdef.symm⟩⟩

end
end Ideal
end IdealFamily
