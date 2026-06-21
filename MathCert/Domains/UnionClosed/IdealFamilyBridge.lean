import MathCert.Domains.UnionClosed.Basic
import MathCert.Domains.UnionClosed.IdealFamilyPort
import Mathlib.Algebra.Order.Group.Unbundled.Basic
import Mathlib.Combinatorics.Enumerative.DoubleCounting

/-!
# Bridge from local finite families to the ideal-family port

The local public representation remains `Family α := Finset (Finset α)`.
This file constructs the ported predicate-style ideal-family structure from a
local finite family and proves the checked translation lemmas.
-/

namespace MathCert.UnionClosed

open Finset

variable {α : Type} [DecidableEq α]

/-- Local ideal-family hypotheses on a fixed ground set. -/
def IsIdealFamilyOn (F : Family α) (U : Finset α) : Prop :=
  (∀ S ∈ F, S ⊆ U) ∧
  (∅ : Finset α) ∈ F ∧
  U ∈ F ∧
  U.Nonempty ∧
  ∀ {A B : Finset α}, B ∈ F → B ≠ U → A ⊆ B → A ∈ F

/-- Local average-rarity/NDS nonpositivity statement in MATHCERT terms. -/
def IsAverageRareOn (F : Family α) (U : Finset α) : Prop :=
  2 * (F.sum fun S => S.card) ≤ U.card * F.card

/-- Every element of the ground set is rare. This is stronger than merely
having one rare element. -/
def IsEverywhereRareOn (F : Family α) (U : Finset α) : Prop :=
  ∀ x ∈ U, 2 * freq F x ≤ F.card

/-- Double-counting incidence: total set size equals the sum of local
frequencies over the chosen ground set. -/
theorem sum_card_eq_sum_freq_on
    {F : Family α} {U : Finset α} (hsub : ∀ S ∈ F, S ⊆ U) :
    F.sum (fun S => S.card) = U.sum (fun x => freq F x) := by
  classical
  let r : Finset α → α → Prop := fun S x => x ∈ S
  have hdc :
      (∑ S ∈ F, (U.bipartiteAbove r S).card) =
        ∑ x ∈ U, (F.bipartiteBelow r x).card :=
    Finset.sum_card_bipartiteAbove_eq_sum_card_bipartiteBelow
      (r := r) (s := F) (t := U)
  calc
    F.sum (fun S => S.card)
        = ∑ S ∈ F, (U.bipartiteAbove r S).card := by
          refine Finset.sum_congr rfl ?_
          intro S hS
          have hEq : U.bipartiteAbove r S = S := by
            apply Finset.ext
            intro x
            constructor
            · intro hx
              exact (Finset.mem_filter.mp hx).2
            · intro hx
              exact Finset.mem_filter.mpr ⟨hsub S hS hx, hx⟩
          rw [hEq]
    _ = ∑ x ∈ U, (F.bipartiteBelow r x).card := hdc
    _ = U.sum (fun x => freq F x) := by
          refine Finset.sum_congr rfl ?_
          intro x hx
          simp [Finset.bipartiteBelow, freq, r]

/-- Average rarity is exactly the corresponding bound on the sum of
frequencies over the ground set. -/
theorem isAverageRareOn_iff_sum_freq_on
    {F : Family α} {U : Finset α} (hsub : ∀ S ∈ F, S ⊆ U) :
    IsAverageRareOn F U ↔
      2 * (U.sum fun x => freq F x) ≤ U.card * F.card := by
  rw [IsAverageRareOn, sum_card_eq_sum_freq_on hsub]

/-- If every ground element is rare, then the family is average-rare. -/
theorem everywhereRare_averageRare
    {F : Family α} {U : Finset α}
    (hsub : ∀ S ∈ F, S ⊆ U)
    (hrare : IsEverywhereRareOn F U) :
    IsAverageRareOn F U := by
  rw [isAverageRareOn_iff_sum_freq_on hsub]
  calc
    2 * (U.sum fun x => freq F x)
        = U.sum (fun x => 2 * freq F x) := by
          rw [Finset.mul_sum]
    _ ≤ U.sum (fun _ => F.card) := by
          exact Finset.sum_le_sum hrare
    _ = U.card * F.card := by
          simp [Finset.sum_const]

/-- A single rare element does not, by itself, imply average rarity. -/
theorem existsRare_not_sufficient_for_averageRare :
    ¬ (∀ (F : Family Bool) (U : Finset Bool),
        (∃ x ∈ U, 2 * freq F x ≤ F.card) → IsAverageRareOn F U) := by
  intro h
  let U : Finset Bool := {true, false}
  let F : Family Bool := {({true} : Finset Bool), ({true, false} : Finset Bool)}
  have hrare : ∃ x ∈ U, 2 * freq F x ≤ F.card := by
    refine ⟨false, ?_, ?_⟩ <;> decide
  have hnot : ¬ IsAverageRareOn F U := by
    dsimp [IsAverageRareOn, F, U, freq]
    decide
  exact hnot (h F U hrare)

namespace IsIdealFamilyOn

theorem members_subset {F : Family α} {U : Finset α}
    (h : IsIdealFamilyOn F U) :
    ∀ S ∈ F, S ⊆ U :=
  h.1

theorem empty_mem {F : Family α} {U : Finset α}
    (h : IsIdealFamilyOn F U) :
    (∅ : Finset α) ∈ F :=
  h.2.1

theorem ground_mem {F : Family α} {U : Finset α}
    (h : IsIdealFamilyOn F U) :
    U ∈ F :=
  h.2.2.1

theorem ground_nonempty {F : Family α} {U : Finset α}
    (h : IsIdealFamilyOn F U) :
    U.Nonempty :=
  h.2.2.2.1

theorem down_closed {F : Family α} {U : Finset α}
    (h : IsIdealFamilyOn F U) :
    ∀ {A B : Finset α}, B ∈ F → B ≠ U → A ⊆ B → A ∈ F :=
  h.2.2.2.2

end IsIdealFamilyOn

/-- Convert a local finite family satisfying the local ideal hypotheses into
the predicate-style ideal-family structure used by the port. -/
noncomputable def toPortIdeal
    (F : Family α) (U : Finset α) (h : IsIdealFamilyOn F U) :
    _root_.IdealFamily.Ideal α :=
  { ground := U
    sets := fun S => S ∈ F
    inc_ground := by
      intro S hS
      exact h.members_subset S hS
    nonempty_ground := h.ground_nonempty
    has_empty := h.empty_mem
    has_ground := h.ground_mem
    down_closed := by
      intro A B hB hBne hAB
      exact h.down_closed hB hBne hAB }

noncomputable instance toPortIdeal_decidablePred
    (F : Family α) (U : Finset α) (h : IsIdealFamilyOn F U) :
    DecidablePred (toPortIdeal F U h).sets := by
  classical
  change DecidablePred (fun S : Finset α => S ∈ F)
  infer_instance

/-- The port carrier is exactly the local finite family. -/
theorem toPortIdeal_carrier_eq
    (F : Family α) (U : Finset α) (h : IsIdealFamilyOn F U) :
    (toPortIdeal F U h).toSetFamily.carrier = F := by
  classical
  apply Finset.ext
  intro S
  constructor
  · intro hS
    exact
      ((_root_.IdealFamily.SetFamily.mem_carrier_iff
        (SF := (toPortIdeal F U h).toSetFamily)).mp hS).2
  · intro hS
    exact
      (_root_.IdealFamily.SetFamily.mem_carrier_iff
        (SF := (toPortIdeal F U h).toSetFamily)).mpr
        ⟨h.members_subset S hS, hS⟩

/-- Ported degree equals local frequency. -/
theorem toPortIdeal_degreeNat_eq_freq
    (F : Family α) (U : Finset α) (h : IsIdealFamilyOn F U) (x : α) :
    (toPortIdeal F U h).toSetFamily.degreeNat x = freq F x := by
  classical
  simp [
    _root_.IdealFamily.SetFamily.degreeNat,
    _root_.IdealFamily.SetFamily.S,
    freq,
    toPortIdeal_carrier_eq
  ]

/-- Ported NDS is the local average-rarity deficit over integers. -/
theorem toPortIdeal_nds_eq
    (F : Family α) (U : Finset α) (h : IsIdealFamilyOn F U) :
    (toPortIdeal F U h).toSetFamily.nds =
      (2 : ℤ) * (((F.sum fun S => S.card) : ℕ) : ℤ)
        - (F.card : ℤ) * (U.card : ℤ) := by
  classical
  let I := toPortIdeal F U h
  have hCarrier : I.toSetFamily.carrier = F := by
    simpa [I] using toPortIdeal_carrier_eq F U h
  have hGround : I.toSetFamily.ground = U := by
    rfl
  change
    (2 : ℤ) * (((I.toSetFamily.carrier.sum fun S => S.card) : ℕ) : ℤ)
      - (I.toSetFamily.carrier.card : ℤ) * (I.toSetFamily.ground.card : ℤ)
      =
    (2 : ℤ) * (((F.sum fun S => S.card) : ℕ) : ℤ)
      - (F.card : ℤ) * (U.card : ℤ)
  rw [hCarrier, hGround]

/-- If the port supplies NDS nonpositivity, the local family is average-rare.

This conditional bridge is reused by the checked local NDS endgame theorem. -/
theorem localIdealFamily_averageRare_of_port_nds
    {F : Family α} {U : Finset α} (h : IsIdealFamilyOn F U)
    (hnds : (toPortIdeal F U h).toSetFamily.nds ≤ 0) :
    IsAverageRareOn F U := by
  classical
  have hndsLocal :
      (2 : ℤ) * (((F.sum fun S => S.card) : ℕ) : ℤ)
        - (F.card : ℤ) * (U.card : ℤ) ≤ 0 := by
    simpa [toPortIdeal_nds_eq] using hnds
  have hIntLe :
      (2 : ℤ) * (((F.sum fun S => S.card) : ℕ) : ℤ)
        ≤ (F.card : ℤ) * (U.card : ℤ) :=
    le_of_sub_nonpos hndsLocal
  dsimp [IsAverageRareOn]
  rw [Nat.mul_comm U.card F.card]
  exact_mod_cast hIntLe

/-- A checked local rare-vertex bridge from the completed rare-vertex port. -/
theorem localIdealFamily_exists_rare
    {F : Family α} {U : Finset α} (h : IsIdealFamilyOn F U) :
    ∃ x ∈ U, 2 * freq F x ≤ F.card := by
  classical
  let I := toPortIdeal F U h
  obtain ⟨x, hxU, hxRare⟩ :=
    _root_.IdealFamily.Ideal.ideal_version_of_frankl_conjecture (F := I)
  refine ⟨x, hxU, ?_⟩
  have hDegree : I.toSetFamily.degreeNat x = freq F x := by
    simpa [I] using toPortIdeal_degreeNat_eq_freq F U h x
  have hCarrier : I.toSetFamily.carrier = F := by
    simpa [I] using toPortIdeal_carrier_eq F U h
  have hRareLocal :
      (2 : ℤ) * (freq F x : ℤ) - (F.card : ℤ) ≤ 0 := by
    simpa [
      _root_.IdealFamily.SetFamily.isRare,
      _root_.IdealFamily.SetFamily.degree,
      _root_.IdealFamily.SetFamily.numEdges,
      _root_.IdealFamily.SetFamily.numEdgesNat,
      hDegree,
      hCarrier,
      I
    ] using hxRare
  have hIntLe : (2 : ℤ) * (freq F x : ℤ) ≤ (F.card : ℤ) :=
    le_of_sub_nonpos hRareLocal
  exact_mod_cast hIntLe

end MathCert.UnionClosed
