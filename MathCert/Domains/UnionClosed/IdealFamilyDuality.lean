import MathCert.Domains.UnionClosed.FranklStatement
import MathCert.Domains.UnionClosed.IdealFamilyNDSEndgame
import Mathlib.Tactic

/-!
# Complement duality for ideal families

This file turns the checked ideal-family rarity results into Frankl-facing
abundance statements for the complement family on a fixed finite ground.
-/

namespace MathCert.UnionClosed

open Finset
open scoped BigOperators

variable {α : Type} [DecidableEq α]

/-- The complement family of `F` inside the fixed ground `U`. -/
def complementFamilyOn (F : Family α) (U : Finset α) : Family α :=
  F.image fun S => U \ S

/-- Average abundance over a chosen ground, stated over integers to avoid
Nat-subtraction bookkeeping in complement identities. -/
def IsAverageAbundantOn (F : Family α) (U : Finset α) : Prop :=
  (U.card : ℤ) * (F.card : ℤ) ≤
    (2 : ℤ) * (((F.sum fun S => S.card) : ℕ) : ℤ)

/-- If `S ⊆ U`, complementing twice inside `U` returns `S`. -/
theorem sdiff_sdiff_eq_self_of_subset
    {S U : Finset α} (hS : S ⊆ U) :
    U \ (U \ S) = S := by
  ext x
  by_cases hxU : x ∈ U
  · by_cases hxS : x ∈ S
    · simp [hxU, hxS]
    · simp [hxU, hxS]
  · have hxS : x ∉ S := by
      intro hx
      exact hxU (hS hx)
    simp [hxU, hxS]

/-- Complementing inside `U` is injective on subsets of `U`. -/
theorem sdiff_left_inj_of_subset
    {S T U : Finset α} (hS : S ⊆ U) (hT : T ⊆ U)
    (hEq : U \ S = U \ T) :
    S = T := by
  calc
    S = U \ (U \ S) := (sdiff_sdiff_eq_self_of_subset hS).symm
    _ = U \ (U \ T) := by rw [hEq]
    _ = T := sdiff_sdiff_eq_self_of_subset hT

/-- The complement family has the same cardinality as the original family. -/
theorem complementFamilyOn_card
    {F : Family α} {U : Finset α}
    (hsub : ∀ S ∈ F, S ⊆ U) :
    (complementFamilyOn F U).card = F.card := by
  classical
  unfold complementFamilyOn
  exact Finset.card_image_iff.mpr
    (by
      intro S hS T hT hEq
      exact sdiff_left_inj_of_subset (hsub S hS) (hsub T hT) hEq)

/-- Sum of sizes in the complement family. -/
theorem sum_card_complementFamilyOn
    {F : Family α} {U : Finset α}
    (hsub : ∀ S ∈ F, S ⊆ U) :
    (complementFamilyOn F U).sum (fun S => S.card) =
      F.sum (fun S => U.card - S.card) := by
  classical
  unfold complementFamilyOn
  have hinj : Set.InjOn (fun S : Finset α => U \ S) ↑F := by
    intro S hS T hT hEq
    exact sdiff_left_inj_of_subset (hsub S hS) (hsub T hT) hEq
  calc
    (F.image fun S => U \ S).sum (fun S => S.card)
        = F.sum (fun S => (U \ S).card) := by
          rw [Finset.sum_image hinj]
    _ = F.sum (fun S => U.card - S.card) := by
          refine Finset.sum_congr rfl ?_
          intro S hS
          exact Finset.card_sdiff_of_subset (hsub S hS)

/-- Frequency duality: a ground element is present in exactly the complements
of original members that omitted it. -/
theorem freq_complementFamilyOn
    {F : Family α} {U : Finset α}
    (hsub : ∀ S ∈ F, S ⊆ U) {x : α} (hx : x ∈ U) :
    freq (complementFamilyOn F U) x = F.card - freq F x := by
  classical
  have hfilter :
      (complementFamilyOn F U).filter (fun A => x ∈ A) =
        (F.filter fun S => x ∉ S).image (fun S => U \ S) := by
    apply Finset.ext
    intro A
    constructor
    · intro hA
      have hAImage : A ∈ complementFamilyOn F U :=
        (Finset.mem_filter.mp hA).1
      have hxA : x ∈ A :=
        (Finset.mem_filter.mp hA).2
      rw [complementFamilyOn] at hAImage
      rcases Finset.mem_image.mp hAImage with ⟨S, hS, rfl⟩
      have hxNotS : x ∉ S := (Finset.mem_sdiff.mp hxA).2
      exact Finset.mem_image.mpr
        ⟨S, Finset.mem_filter.mpr ⟨hS, hxNotS⟩, rfl⟩
    · intro hA
      rcases Finset.mem_image.mp hA with ⟨S, hSf, rfl⟩
      have hS : S ∈ F := (Finset.mem_filter.mp hSf).1
      have hxNotS : x ∉ S := (Finset.mem_filter.mp hSf).2
      exact Finset.mem_filter.mpr
        ⟨by
            rw [complementFamilyOn]
            exact Finset.mem_image.mpr ⟨S, hS, rfl⟩,
          Finset.mem_sdiff.mpr ⟨hx, hxNotS⟩⟩
  unfold freq
  rw [hfilter]
  have hinj :
      Set.InjOn (fun S : Finset α => U \ S)
        ↑(F.filter fun S => x ∉ S) := by
    intro S hS T hT hEq
    exact sdiff_left_inj_of_subset
      (hsub S (Finset.mem_filter.mp hS).1)
      (hsub T (Finset.mem_filter.mp hT).1)
      hEq
  rw [Finset.card_image_iff.mpr hinj]
  have hsplit :=
    Finset.card_filter_add_card_filter_not
      (s := F) (p := fun S : Finset α => x ∈ S)
  omega

/-- The fixed ground belongs to the complement family when the original family
contains the empty set. -/
theorem ground_mem_complementFamilyOn
    {F : Family α} {U : Finset α}
    (hempty : (∅ : Finset α) ∈ F) :
    U ∈ complementFamilyOn F U := by
  classical
  rw [complementFamilyOn]
  exact Finset.mem_image.mpr ⟨∅, hempty, by simp⟩

/-- The complement of an ideal family is union-closed. -/
theorem complementFamilyOn_unionClosed_of_ideal
    {F : Family α} {U : Finset α}
    (h : IsIdealFamilyOn F U) :
    IsUnionClosed (complementFamilyOn F U) := by
  classical
  intro A hA B hB
  rw [complementFamilyOn] at hA hB
  rcases Finset.mem_image.mp hA with ⟨S, hS, rfl⟩
  rcases Finset.mem_image.mp hB with ⟨T, hT, rfl⟩
  have hInter : S ∩ T ∈ F := by
    by_cases hTop : S = U
    · have hTU : T ⊆ U := IsIdealFamilyOn.members_subset h T hT
      have hUT : U ∩ T = T := by
        apply Finset.ext
        intro x
        constructor
        · intro hx
          exact (Finset.mem_inter.mp hx).2
        · intro hx
          exact Finset.mem_inter.mpr ⟨hTU hx, hx⟩
      simpa [hTop, hUT] using hT
    · exact IsIdealFamilyOn.down_closed h hS hTop Finset.inter_subset_left
  rw [complementFamilyOn]
  refine Finset.mem_image.mpr ⟨S ∩ T, hInter, ?_⟩
  ext x
  by_cases hxU : x ∈ U
  · by_cases hxS : x ∈ S
    · by_cases hxT : x ∈ T <;> simp [hxU, hxS, hxT]
    · by_cases hxT : x ∈ T <;> simp [hxU, hxS, hxT]
  · simp [hxU]

/-- Average rarity of a family is average abundance of its complement. -/
theorem complementFamilyOn_averageAbundant_of_averageRare
    {F : Family α} {U : Finset α}
    (hsub : ∀ S ∈ F, S ⊆ U)
    (hrare : IsAverageRareOn F U) :
    IsAverageAbundantOn (complementFamilyOn F U) U := by
  classical
  let total : ℤ := (U.card : ℤ) * (F.card : ℤ)
  let sizeF : ℤ := (((F.sum fun S => S.card) : ℕ) : ℤ)
  have hAvg : (2 : ℤ) * sizeF ≤ total := by
    dsimp [total, sizeF]
    exact_mod_cast hrare
  have hsumZ :
      ((((complementFamilyOn F U).sum fun S => S.card) : ℕ) : ℤ) =
        total - sizeF := by
    rw [sum_card_complementFamilyOn hsub]
    dsimp [total, sizeF]
    calc
      (((F.sum fun S => U.card - S.card) : ℕ) : ℤ)
          = ∑ S ∈ F, (((U.card - S.card) : ℕ) : ℤ) := by
            norm_cast
      _ = ∑ S ∈ F, ((U.card : ℤ) - (S.card : ℤ)) := by
            refine Finset.sum_congr rfl ?_
            intro S hS
            have hcard : S.card ≤ U.card := Finset.card_le_card (hsub S hS)
            rw [Nat.cast_sub hcard]
      _ = (F.card : ℤ) * (U.card : ℤ) -
            ∑ S ∈ F, (S.card : ℤ) := by
            rw [Finset.sum_sub_distrib]
            simp [Finset.sum_const]
      _ = (U.card : ℤ) * (F.card : ℤ) -
            (((F.sum fun S => S.card) : ℕ) : ℤ) := by
            norm_cast
            ring_nf
  dsimp [IsAverageAbundantOn]
  rw [complementFamilyOn_card hsub, hsumZ]
  omega

/-- Rare vertices become abundant vertices after complementing. -/
theorem complementFamilyOn_abundant_of_exists_rare
    {F : Family α} {U : Finset α}
    (hsub : ∀ S ∈ F, S ⊆ U)
    (hempty : (∅ : Finset α) ∈ F)
    (hrare : ∃ x ∈ U, 2 * freq F x ≤ F.card) :
    IsFranklAbundant (complementFamilyOn F U) := by
  classical
  rcases hrare with ⟨x, hxU, hxRare⟩
  refine ⟨x, ?_, ?_⟩
  · exact (mem_support_iff (complementFamilyOn F U) x).mpr
      ⟨U, ground_mem_complementFamilyOn (F := F) (U := U) hempty, hxU⟩
  · have hfreq_le : freq F x ≤ F.card := by
      unfold freq
      exact Finset.card_le_card (Finset.filter_subset _ _)
    rw [
      freq_complementFamilyOn (F := F) (U := U) hsub hxU,
      complementFamilyOn_card (F := F) (U := U) hsub
    ]
    omega

/-- The complement of a local ideal family is union-closed, nontrivial, and
Frankl-abundant. -/
theorem localIdealFamily_complement_frankl
    {F : Family α} {U : Finset α}
    (h : IsIdealFamilyOn F U) :
    IsUnionClosed (complementFamilyOn F U) ∧
      IsNontrivial (complementFamilyOn F U) ∧
      IsFranklAbundant (complementFamilyOn F U) := by
  classical
  have hAbundant : IsFranklAbundant (complementFamilyOn F U) :=
    complementFamilyOn_abundant_of_exists_rare
      (F := F) (U := U)
      (IsIdealFamilyOn.members_subset h)
      (IsIdealFamilyOn.empty_mem h)
      (localIdealFamily_exists_rare h)
  refine ⟨complementFamilyOn_unionClosed_of_ideal h, ?_, hAbundant⟩
  rcases hAbundant with ⟨x, hxSupport, _⟩
  exact ⟨x, hxSupport⟩

/-- Families explicitly represented as complements of local ideal families
inherit the checked Frankl-facing conclusion. -/
theorem complementOfLocalIdealFamily_frankl
    {G : Family α}
    (hG : ∃ F U, IsIdealFamilyOn F U ∧ G = complementFamilyOn F U) :
    IsUnionClosed G ∧ IsNontrivial G ∧ IsFranklAbundant G := by
  classical
  rcases hG with ⟨F, U, hIdeal, hEq⟩
  rw [hEq]
  exact localIdealFamily_complement_frankl hIdeal

/-- The checked average-rarity theorem for local ideal families dualizes to
average abundance of the complement family. -/
theorem localIdealFamily_complement_averageAbundant
    {F : Family α} {U : Finset α}
    (h : IsIdealFamilyOn F U) :
    IsAverageAbundantOn (complementFamilyOn F U) U :=
  complementFamilyOn_averageAbundant_of_averageRare
    (IsIdealFamilyOn.members_subset h)
    (localIdealFamily_averageRare h)

end MathCert.UnionClosed
