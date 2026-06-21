import MathCert.Domains.UnionClosed.IdealFamilyPort.Core
import Mathlib.Data.Finset.Card
import Mathlib.Data.Finset.Image
import Mathlib.Data.Int.Basic

/-!
# Contraction numerics for the ideal-family port

The contraction carrier at `v` is the image of members containing `v` under
`erase v`.  This file proves that contraction preserves the number of such
members and lowers their total cardinality by one per member.
-/

namespace IdealFamily
namespace SetFamily

open Finset
open scoped BigOperators

noncomputable section

variable {α : Type*} [DecidableEq α]
variable (SF : SetFamily α) [DecidablePred SF.sets]
variable (v : α)

/-- Erasing `v` is injective on the members that contain `v`. -/
theorem erase_injective_on_S :
    ∀ {x} (_hx : x ∈ SF.S v) {y} (_hy : y ∈ SF.S v),
      x.erase v = y.erase v → x = y := by
  intro x hx y hy hxy
  have hvx : v ∈ x := (Finset.mem_filter.mp hx).2
  have hvy : v ∈ y := (Finset.mem_filter.mp hy).2
  calc
    x = insert v (x.erase v) := (Finset.insert_erase hvx).symm
    _ = insert v (y.erase v) := by rw [hxy]
    _ = y := Finset.insert_erase hvy

/-- The contraction carrier has the same cardinality as the containing side. -/
theorem card_contr_eq_cardS :
    (SF.contrCarrier v).card = (SF.S v).card := by
  classical
  rw [SetFamily.contrCarrier]
  exact Finset.card_image_iff.mpr
    (by
      intro x hx y hy hxy
      exact erase_injective_on_S (SF := SF) (v := v) hx hy hxy)

/-- Integer form of `card (s.erase v) = card s - 1` for `v ∈ s`. -/
theorem card_erase_z (s : Finset α) (hvs : v ∈ s) :
    ((s.erase v).card : ℤ) = (s.card : ℤ) - 1 := by
  have hNat : (s.erase v).card + 1 = s.card :=
    Finset.card_erase_add_one hvs
  have hInt : ((s.erase v).card : ℤ) + 1 = (s.card : ℤ) := by
    exact_mod_cast hNat
  omega

/-- The sum of set sizes over the contraction carrier equals the sum over the
containing side with one removed from each member. -/
theorem sum_card_contr_eq_sum_cardS_sub_one :
    (∑ t ∈ SF.contrCarrier v, (t.card : ℤ)) =
      ∑ s ∈ SF.S v, ((s.card : ℤ) - 1) := by
  classical
  have hsum :
      (∑ t ∈ SF.contrCarrier v, (t.card : ℤ)) =
        ∑ s ∈ SF.S v, (((s.erase v).card : ℤ)) := by
    let i : ∀ s, s ∈ SF.S v → Finset α := fun s _ => s.erase v
    have h_mem : ∀ s (hs : s ∈ SF.S v), i s hs ∈ SF.contrCarrier v := by
      intro s hs
      exact Finset.mem_image.mpr ⟨s, hs, rfl⟩
    have h_inj :
        ∀ s₁ (hs₁ : s₁ ∈ SF.S v) s₂ (hs₂ : s₂ ∈ SF.S v),
          i s₁ hs₁ = i s₂ hs₂ → s₁ = s₂ := by
      intro s₁ hs₁ s₂ hs₂ h
      exact erase_injective_on_S (SF := SF) (v := v) hs₁ hs₂ h
    have h_surj :
        ∀ t, t ∈ SF.contrCarrier v →
          ∃ s, ∃ hs : s ∈ SF.S v, i s hs = t := by
      intro t ht
      rcases Finset.mem_image.mp ht with ⟨s, hs, rfl⟩
      exact ⟨s, hs, rfl⟩
    have h_bij :=
      @Finset.sum_bij _ _ _ _ (SF.S v) (SF.contrCarrier v)
        (fun s => ((s.erase v).card : ℤ))
        (fun t => (t.card : ℤ))
        i h_mem h_inj h_surj
        (by intro s hs; rfl)
    exact h_bij.symm
  calc
    (∑ t ∈ SF.contrCarrier v, (t.card : ℤ))
        = ∑ s ∈ SF.S v, (((s.erase v).card : ℤ)) := hsum
    _ = ∑ s ∈ SF.S v, ((s.card : ℤ) - 1) := by
      refine Finset.sum_congr rfl ?_
      intro s hs
      exact card_erase_z (v := v) s ((Finset.mem_filter.mp hs).2)

end
end SetFamily

namespace Ideal

open Finset

noncomputable section

variable {α : Type*} [DecidableEq α]
variable (F : Ideal α) [DecidablePred F.sets]
variable (v : α)

/-- Contraction membership at a singleton vertex: a set `t` on
`ground.erase v` is present when `insert v t` was present in `F`. -/
def contrSets (t : Finset α) : Prop :=
  t ⊆ F.ground.erase v ∧ F.sets (insert v t)

/-- The singleton contraction ideal on `ground.erase v`. -/
def contrIdeal
    (hv : v ∈ F.ground)
    (hne : (F.ground.erase v).Nonempty)
    (hSing : F.sets ({v} : Finset α)) : Ideal α :=
  { ground := F.ground.erase v
    sets := contrSets (F := F) v
    inc_ground := by
      intro t ht
      exact ht.1
    nonempty_ground := hne
    has_empty := by
      constructor
      · intro x hx
        exact False.elim (Finset.notMem_empty x hx)
      · simpa using hSing
    has_ground := by
      constructor
      · exact subset_refl _
      · have htop : insert v (F.ground.erase v) = F.ground :=
          Finset.insert_erase hv
        simpa [htop] using F.has_ground
    down_closed := by
      intro A B hB hBne hAB
      constructor
      · exact subset_trans hAB hB.1
      · have hvnotB : v ∉ B := by
          intro hvB
          exact (Finset.mem_erase.mp (hB.1 hvB)).1 rfl
        have hBtop : insert v B ≠ F.ground := by
          intro htop
          have hErase : (insert v B).erase v = F.ground.erase v := by
            rw [htop]
          have hLeft : (insert v B).erase v = B := by
            simp [hvnotB]
          have hBground : B = F.ground.erase v := by
            rw [← hLeft, hErase]
          exact hBne hBground
        have hInsertSub : insert v A ⊆ insert v B := by
          intro x hx
          rw [Finset.mem_insert] at hx
          rw [Finset.mem_insert]
          rcases hx with hxv | hxA
          · exact Or.inl hxv
          · exact Or.inr (hAB hxA)
        exact F.down_closed hB.2 hBtop hInsertSub }

omit [DecidablePred F.sets] in
@[simp] theorem contrIdeal_ground
    (hv : v ∈ F.ground)
    (hne : (F.ground.erase v).Nonempty)
    (hSing : F.sets ({v} : Finset α)) :
    (F.contrIdeal v hv hne hSing).ground = F.ground.erase v := by
  rfl

instance contrIdeal_sets_decidable
    (hv : v ∈ F.ground)
    (hne : (F.ground.erase v).Nonempty)
    (hSing : F.sets ({v} : Finset α)) :
    DecidablePred ((F.contrIdeal v hv hne hSing).sets) := by
  classical
  intro t
  exact Classical.dec _

omit [DecidablePred F.sets] in
theorem contr_ground_card_lt
    (hv : v ∈ F.ground)
    (hne : (F.ground.erase v).Nonempty)
    (hSing : F.sets ({v} : Finset α)) :
    (F.contrIdeal v hv hne hSing).ground.card < F.ground.card := by
  rw [contrIdeal_ground]
  exact Finset.card_erase_lt_of_mem hv

/-- The carrier of the singleton contraction ideal is the existing
contraction carrier. -/
theorem contrIdeal_carrier_eq_contrCarrier
    (hv : v ∈ F.ground)
    (hne : (F.ground.erase v).Nonempty)
    (hSing : F.sets ({v} : Finset α)) :
    (F.contrIdeal v hv hne hSing).toSetFamily.carrier =
      F.toSetFamily.contrCarrier v := by
  classical
  apply Finset.ext
  intro t
  constructor
  · intro ht
    have htInfo :=
      (SetFamily.mem_carrier_iff
        (SF := (F.contrIdeal v hv hne hSing).toSetFamily)).mp ht
    have htSub : t ⊆ F.ground.erase v := htInfo.2.1
    have htSet : F.sets (insert v t) := htInfo.2.2
    have hvnot : v ∉ t := by
      intro hvt
      exact (Finset.mem_erase.mp (htSub hvt)).1 rfl
    have hInsertSub : insert v t ⊆ F.ground := by
      intro x hx
      rw [Finset.mem_insert] at hx
      rcases hx with hxv | hxt
      · simpa [hxv] using hv
      · exact Finset.mem_of_mem_erase (htSub hxt)
    have hInsertCarrier : insert v t ∈ F.toSetFamily.carrier :=
      (SetFamily.mem_carrier_iff (SF := F.toSetFamily)).mpr
        ⟨hInsertSub, htSet⟩
    have hInsertS : insert v t ∈ F.toSetFamily.S v :=
      Finset.mem_filter.mpr ⟨hInsertCarrier, by simp⟩
    rw [SetFamily.contrCarrier]
    exact Finset.mem_image.mpr
      ⟨insert v t, hInsertS, by simp [hvnot]⟩
  · intro ht
    rw [SetFamily.contrCarrier] at ht
    rcases Finset.mem_image.mp ht with ⟨s, hsS, rfl⟩
    have hsCarrier : s ∈ F.toSetFamily.carrier :=
      (Finset.mem_filter.mp hsS).1
    have hvs : v ∈ s :=
      (Finset.mem_filter.mp hsS).2
    have hsInfo :=
      (SetFamily.mem_carrier_iff (SF := F.toSetFamily)).mp hsCarrier
    have hEraseSub : s.erase v ⊆ F.ground.erase v := by
      intro x hx
      have hxPair := Finset.mem_erase.mp hx
      exact Finset.mem_erase.mpr ⟨hxPair.1, hsInfo.1 hxPair.2⟩
    have hSet : F.sets (insert v (s.erase v)) := by
      have hInsert : insert v (s.erase v) = s :=
        Finset.insert_erase hvs
      rw [hInsert]
      exact hsInfo.2
    exact
      (SetFamily.mem_carrier_iff
        (SF := (F.contrIdeal v hv hne hSing).toSetFamily)).mpr
        ⟨hEraseSub, ⟨hEraseSub, hSet⟩⟩

end
end Ideal
end IdealFamily
