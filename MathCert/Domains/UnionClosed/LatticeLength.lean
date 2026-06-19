import MathCert.Domains.UnionClosed.LatticeMinimum
import Mathlib.Data.Fintype.Card
import Mathlib.Data.Finset.Max
import Mathlib.Data.Finset.Powerset
import Mathlib.Order.Preorder.Chain
import Mathlib.Order.Preorder.Finite

/-!
# Finite lattice length

This file provides the local length interface needed for Bouchard's Theorem
2.7.  Rival's external finite-lattice inequality is represented by the
subtraction-free predicate `RivalBound`; the theorem depending on it is kept
conditional.
-/

namespace MathCert.UnionClosed.Lattice

open Finset Set

universe u

variable {L : Type u} [Fintype L] [Lattice L] [BoundedOrder L]

/-- Cardinalities of all finite chain carriers in a finite bounded lattice. -/
noncomputable def chainCardinals
    (L : Type u) [Fintype L] [Lattice L] [BoundedOrder L] : Finset Nat := by
  classical
  exact ((Finset.univ : Finset L).powerset.filter
    (fun s : Finset L => IsChain (· ≤ ·) (s : Set L))).image
      (fun s : Finset L => s.card)

private theorem singleton_bot_card_mem_chainCardinals :
    1 ∈ chainCardinals L := by
  classical
  refine Finset.mem_image.mpr ?_
  refine ⟨({⊥} : Finset L), ?_, by simp⟩
  simp

theorem chainCardinals_nonempty : (chainCardinals L).Nonempty :=
  ⟨1, singleton_bot_card_mem_chainCardinals (L := L)⟩

/--
The finite lattice length used by Bouchard and Rival: one less than the maximum
cardinality of a finite chain.
-/
noncomputable def latticeLength
    (L : Type u) [Fintype L] [Lattice L] [BoundedOrder L] : Nat :=
  (chainCardinals L).max' (chainCardinals_nonempty (L := L)) - 1

theorem one_le_max_chainCardinals :
    1 ≤ (chainCardinals L).max' (chainCardinals_nonempty (L := L)) :=
  Finset.le_max' (chainCardinals L) 1 singleton_bot_card_mem_chainCardinals

theorem latticeLength_add_one_eq_max_chainCardinals :
    latticeLength L + 1 =
      (chainCardinals L).max' (chainCardinals_nonempty (L := L)) := by
  have hpos := one_le_max_chainCardinals (L := L)
  unfold latticeLength
  omega

theorem exists_chain_card_eq_latticeLength_add_one :
    ∃ s : Finset L, IsChain (· ≤ ·) (s : Set L) ∧
      s.card = latticeLength L + 1 := by
  classical
  have hmax_mem :
      (chainCardinals L).max' (chainCardinals_nonempty (L := L)) ∈ chainCardinals L :=
    Finset.max'_mem _ _
  unfold chainCardinals at hmax_mem
  rcases Finset.mem_image.mp hmax_mem with ⟨s, hs, hcard⟩
  refine ⟨s, (Finset.mem_filter.mp hs).2, ?_⟩
  rw [latticeLength_add_one_eq_max_chainCardinals (L := L)]
  exact hcard

theorem chain_card_le_latticeLength_add_one {s : Finset L}
    (hs : IsChain (· ≤ ·) (s : Set L)) :
    s.card ≤ latticeLength L + 1 := by
  classical
  rw [latticeLength_add_one_eq_max_chainCardinals (L := L)]
  apply Finset.le_max'
  refine Finset.mem_image.mpr ?_
  refine ⟨s, ?_, rfl⟩
  simp [hs]

omit [BoundedOrder L] in
/-- The finite carrier of the principal upper cone above `x`. -/
noncomputable def upperConeFinset (x : L) : Finset L := by
  classical
  exact Finset.univ.filter fun y : L => x ≤ y

omit [BoundedOrder L] in
theorem mem_upperConeFinset {x y : L} :
    y ∈ upperConeFinset x ↔ x ≤ y := by
  classical
  simp [upperConeFinset]

omit [BoundedOrder L] in
theorem upperConeFinset_card_eq_upperConeCard (x : L) :
    (upperConeFinset x).card = upperConeCard x := by
  classical
  unfold upperConeFinset upperConeCard
  rw [Fintype.card_subtype]

/-- The upper cone with bottom adjoined. -/
noncomputable def botUpperConeFinset (x : L) : Finset L := by
  classical
  exact insert ⊥ (upperConeFinset x)

/--
If every non-top element in the principal upper cone above `x` is
meet-irreducible, then that upper cone is a chain.
-/
theorem upperCone_isChain_of_forall_infIrred {x : L}
    (hInf : ∀ y : L, x ≤ y → y ≠ ⊤ → InfIrred y) :
    IsChain (· ≤ ·) ({y : L | x ≤ y}) := by
  classical
  intro a ha b hb _
  by_cases hab : a ≤ b
  · exact Or.inl hab
  by_cases hba : b ≤ a
  · exact Or.inr hba
  exfalso
  have hxa : x ≤ a := ha
  have hxb : x ≤ b := hb
  have ha_ne_top : a ≠ ⊤ := by
    intro ha_top
    exact hba (by simp [ha_top])
  have hb_ne_top : b ≠ ⊤ := by
    intro hb_top
    exact hab (by simp [hb_top])
  let S : Finset L := Finset.univ.filter fun z : L => x ≤ z ∧ z ≤ a ∧ z ≤ b
  have hxS : x ∈ S := by
    simp [S, hxa, hxb]
  obtain ⟨m, hmmax⟩ := S.exists_maximal ⟨x, hxS⟩
  have hm_props : x ≤ m ∧ m ≤ a ∧ m ≤ b := by
    simpa [S] using hmmax.1
  have hm_ne_top : m ≠ ⊤ := by
    intro hm_top
    have htop_le_a : (⊤ : L) ≤ a := by
      simpa [hm_top] using hm_props.2.1
    exact ha_ne_top (le_antisymm le_top htop_le_a)
  have hmInf : InfIrred m := hInf m hm_props.1 hm_ne_top
  have hma : m < a := by
    refine lt_of_le_of_ne hm_props.2.1 ?_
    intro hma_eq
    exact hab (by simpa [hma_eq] using hm_props.2.2)
  have hmb : m < b := by
    refine lt_of_le_of_ne hm_props.2.2 ?_
    intro hmb_eq
    exact hba (by simpa [hmb_eq] using hm_props.2.1)
  have hmu : m < upperCover m := lt_upperCover hmInf
  have huS : upperCover m ∈ S := by
    simp [S, hm_props.1.trans hmu.le, upperCover_le_of_lt hma,
      upperCover_le_of_lt hmb]
  exact (not_le_of_gt hmu) (hmmax.2 huS hmu.le)

theorem botUpperConeFinset_isChain {x : L}
    (hchain : IsChain (· ≤ ·) ({y : L | x ≤ y})) :
    IsChain (· ≤ ·) (botUpperConeFinset x : Set L) := by
  classical
  intro a ha b hb hab
  simp [botUpperConeFinset, upperConeFinset] at ha hb
  rcases ha with rfl | ha
  · exact Or.inl bot_le
  rcases hb with rfl | hb
  · exact Or.inr bot_le
  exact hchain ha hb hab

/--
If the principal upper cone above a nonbottom element is a chain, then its
cardinality is at most the lattice length.
-/
theorem upperConeCard_le_latticeLength_of_upperCone_chain {x : L}
    (hx_bot : x ≠ ⊥)
    (hchain : IsChain (· ≤ ·) ({y : L | x ≤ y})) :
    upperConeCard x ≤ latticeLength L := by
  classical
  have hinsert := botUpperConeFinset_isChain (L := L) hchain
  have hle :=
    chain_card_le_latticeLength_add_one (L := L) (s := botUpperConeFinset x)
      hinsert
  have hbot_not : ⊥ ∉ upperConeFinset x := by
    rw [mem_upperConeFinset]
    intro hx
    exact hx_bot (le_antisymm hx bot_le)
  have hcard :
      (botUpperConeFinset x).card = upperConeCard x + 1 := by
    unfold botUpperConeFinset
    rw [Finset.card_insert_of_notMem hbot_not, upperConeFinset_card_eq_upperConeCard]
  rw [hcard] at hle
  omega

/-- The locally relevant set of doubly irreducible elements. -/
noncomputable def doublyIrredFinset
    (L : Type u) [Fintype L] [Lattice L] [BoundedOrder L] : Finset L := by
  classical
  exact Finset.univ.filter fun x : L => SupIrred x ∧ InfIrred x

theorem mem_doublyIrredFinset {x : L} :
    x ∈ doublyIrredFinset L ↔ SupIrred x ∧ InfIrred x := by
  classical
  simp [doublyIrredFinset]

theorem doublyIrredFinset_card_le_one_of_minimum
    (hmin : IsMinimumCounterexample L) :
    (doublyIrredFinset L).card ≤ 1 := by
  classical
  rw [Finset.card_le_one]
  intro x hx y hy
  have hx' := (mem_doublyIrredFinset (L := L)).1 hx
  have hy' := (mem_doublyIrredFinset (L := L)).1 hy
  exact minimumCounterexample_doublyIrred_unique hmin x y hx'.1 hx'.2 hy'.1 hy'.2

/--
Rival's finite-lattice length inequality in a subtraction-free form:
`2 * (ell(L) + 1) <= |L| + |Irr(L)|`.
-/
def RivalBound
    (L : Type u) [Fintype L] [Lattice L] [BoundedOrder L] : Prop :=
  2 * (latticeLength L + 1) ≤ Fintype.card L + (doublyIrredFinset L).card

/--
UC-WP05-L017, conditional Bouchard Theorem 2.7:
assuming Rival's external length bound, every join-irreducible element in a
minimum counterexample has upper cone cardinality strictly greater than the
lattice length.
-/
theorem minimumCounterexample_upperConeCard_gt_latticeLength_of_rivalBound
    (hmin : IsMinimumCounterexample L)
    (hRival : RivalBound L)
    {j : L} (hj : SupIrred j) :
    latticeLength L < upperConeCard j := by
  have hIrr := doublyIrredFinset_card_le_one_of_minimum (L := L) hmin
  have hcounter : Fintype.card L < 2 * upperConeCard j := hmin.1.2 j hj
  unfold RivalBound at hRival
  omega

/--
UC-WP05-L018, conditional Bouchard Corollary 2.8:
assuming Rival's external length bound, every doubly irreducible element in a
minimum counterexample lies strictly below a non-top doubly reducible element.
-/
theorem minimumCounterexample_doublyIrred_lt_nonTop_doublyReducible_of_rivalBound
    (hmin : IsMinimumCounterexample L)
    (hRival : RivalBound L)
    {x : L} (hxSup : SupIrred x) (hxInf : InfIrred x) :
    ∃ y : L, x < y ∧ y ≠ ⊤ ∧ ¬SupIrred y ∧ ¬InfIrred y := by
  by_contra hno
  have hallInf : ∀ y : L, x ≤ y → y ≠ ⊤ → InfIrred y := by
    intro y hxy hy_top
    by_cases hyx : y = x
    · simpa [hyx] using hxInf
    have hxylt : x < y := lt_of_le_of_ne hxy (Ne.symm hyx)
    have hnotSup : ¬SupIrred y := by
      intro hySup
      exact minimumCounterexample_no_infIrred_lt_supIrred hmin x y hxInf hySup hxylt
    by_contra hnotInf
    exact hno ⟨y, hxylt, hy_top, hnotSup, hnotInf⟩
  have hchain : IsChain (· ≤ ·) ({y : L | x ≤ y}) :=
    upperCone_isChain_of_forall_infIrred (L := L) hallInf
  have hle : upperConeCard x ≤ latticeLength L :=
    upperConeCard_le_latticeLength_of_upperCone_chain (L := L) hxSup.ne_bot hchain
  have hgt : latticeLength L < upperConeCard x :=
    minimumCounterexample_upperConeCard_gt_latticeLength_of_rivalBound hmin hRival hxSup
  exact (not_lt_of_ge hle) hgt

end MathCert.UnionClosed.Lattice
