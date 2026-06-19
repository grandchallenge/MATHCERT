import MathCert.Domains.UnionClosed.LatticeLength
import Mathlib.Order.Interval.Finset.Nat

/-!
# Rival's finite-lattice length inequality

This file records Rival's endpoint-inclusive irreducibility convention and
uses it to discharge the finite-lattice length dependency needed by Bouchard's
Theorem 2.7 and Corollary 2.8.
-/

namespace MathCert.UnionClosed.Lattice

open Finset Set

universe u

variable {L : Type u} [Fintype L] [Lattice L] [BoundedOrder L]

/-- Rival/source-style join-irreducibility: endpoint-inclusive `not reducible`. -/
def RivalSupIrred (x : L) : Prop :=
  ∀ a b : L, x = a ⊔ b → x = a ∨ x = b

/-- Rival/source-style meet-irreducibility: endpoint-inclusive `not reducible`. -/
def RivalInfIrred (x : L) : Prop :=
  ∀ a b : L, x = a ⊓ b → x = a ∨ x = b

/-- Rival/source-style doubly irreducible elements. -/
def RivalDoublyIrred (x : L) : Prop :=
  RivalSupIrred x ∧ RivalInfIrred x

/-- The finite set of Rival/source-style join-irreducibles. -/
noncomputable def rivalSupIrredFinset
    (L : Type u) [Fintype L] [Lattice L] : Finset L := by
  classical
  exact Finset.univ.filter fun x : L => RivalSupIrred x

/-- The finite set of Rival/source-style meet-irreducibles. -/
noncomputable def rivalInfIrredFinset
    (L : Type u) [Fintype L] [Lattice L] : Finset L := by
  classical
  exact Finset.univ.filter fun x : L => RivalInfIrred x

/-- The finite set of Rival/source-style doubly irreducibles. -/
noncomputable def rivalDoublyIrredFinset
    (L : Type u) [Fintype L] [Lattice L] : Finset L := by
  classical
  exact Finset.univ.filter fun x : L => RivalDoublyIrred x

omit [BoundedOrder L] in
theorem mem_rivalSupIrredFinset {x : L} :
    x ∈ rivalSupIrredFinset L ↔ RivalSupIrred x := by
  classical
  simp [rivalSupIrredFinset]

omit [BoundedOrder L] in
theorem mem_rivalInfIrredFinset {x : L} :
    x ∈ rivalInfIrredFinset L ↔ RivalInfIrred x := by
  classical
  simp [rivalInfIrredFinset]

omit [BoundedOrder L] in
theorem mem_rivalDoublyIrredFinset {x : L} :
    x ∈ rivalDoublyIrredFinset L ↔ RivalSupIrred x ∧ RivalInfIrred x := by
  classical
  simp [rivalDoublyIrredFinset, RivalDoublyIrred]

omit [Fintype L] in
theorem rivalSupIrred_bot : RivalSupIrred (⊥ : L) := by
  intro a b h
  have ha : a = (⊥ : L) := by
    apply le_antisymm
    · rw [h]
      exact le_sup_left
    · exact bot_le
  have hb : b = (⊥ : L) := by
    apply le_antisymm
    · rw [h]
      exact le_sup_right
    · exact bot_le
  exact Or.inl ha.symm

omit [Fintype L] in
theorem rivalInfIrred_top : RivalInfIrred (⊤ : L) := by
  intro a b h
  have ha : a = (⊤ : L) := by
    apply le_antisymm
    · exact le_top
    · rw [h]
      exact inf_le_left
  have hb : b = (⊤ : L) := by
    apply le_antisymm
    · exact le_top
    · rw [h]
      exact inf_le_right
  exact Or.inl ha.symm

omit [Fintype L] [BoundedOrder L] in
theorem rivalSupIrred_of_supIrred {x : L} (hx : SupIrred x) :
    RivalSupIrred x := by
  intro a b h
  rcases hx.2 h.symm with ha | hb
  · exact Or.inl ha.symm
  · exact Or.inr hb.symm

omit [Fintype L] [BoundedOrder L] in
theorem rivalInfIrred_of_infIrred {x : L} (hx : InfIrred x) :
    RivalInfIrred x := by
  intro a b h
  rcases hx.2 h.symm with ha | hb
  · exact Or.inl ha.symm
  · exact Or.inr hb.symm

omit [Fintype L] in
theorem supIrred_of_rivalSupIrred_ne_bot {x : L}
    (hx : RivalSupIrred x) (hx_ne_bot : x ≠ ⊥) :
    SupIrred x := by
  constructor
  · intro hmin
    exact hx_ne_bot (le_antisymm (hmin bot_le) bot_le)
  · intro a b h
    rcases hx a b h.symm with ha | hb
    · exact Or.inl ha.symm
    · exact Or.inr hb.symm

omit [Fintype L] in
theorem infIrred_of_rivalInfIrred_ne_top {x : L}
    (hx : RivalInfIrred x) (hx_ne_top : x ≠ ⊤) :
    InfIrred x := by
  constructor
  · intro hmax
    exact hx_ne_top (le_antisymm le_top (hmax le_top))
  · intro a b h
    rcases hx a b h.symm with ha | hb
    · exact Or.inl ha.symm
    · exact Or.inr hb.symm

omit [Fintype L] in
theorem rivalSupIrred_iff_eq_bot_or_supIrred {x : L} :
    RivalSupIrred x ↔ x = ⊥ ∨ SupIrred x := by
  constructor
  · intro hx
    by_cases hbot : x = ⊥
    · exact Or.inl hbot
    · exact Or.inr (supIrred_of_rivalSupIrred_ne_bot hx hbot)
  · intro hx
    rcases hx with rfl | hx
    · exact rivalSupIrred_bot
    · exact rivalSupIrred_of_supIrred hx

omit [Fintype L] in
theorem rivalInfIrred_iff_eq_top_or_infIrred {x : L} :
    RivalInfIrred x ↔ x = ⊤ ∨ InfIrred x := by
  constructor
  · intro hx
    by_cases htop : x = ⊤
    · exact Or.inl htop
    · exact Or.inr (infIrred_of_rivalInfIrred_ne_top hx htop)
  · intro hx
    rcases hx with rfl | hx
    · exact rivalInfIrred_top
    · exact rivalInfIrred_of_infIrred hx

theorem bot_mem_rivalSupIrredFinset :
    (⊥ : L) ∈ rivalSupIrredFinset L := by
  rw [mem_rivalSupIrredFinset]
  exact rivalSupIrred_bot

theorem top_mem_rivalInfIrredFinset :
    (⊤ : L) ∈ rivalInfIrredFinset L := by
  rw [mem_rivalInfIrredFinset]
  exact rivalInfIrred_top

omit [Fintype L] in
private theorem finset_sup_le_iff {s : Finset L} {x : L} :
    s.sup id ≤ x ↔ ∀ y ∈ s, y ≤ x := by
  classical
  induction s using Finset.induction with
  | empty =>
      simp
  | insert a s has ih =>
      simp [Finset.sup_insert, ih, sup_le_iff]

omit [Fintype L] in
private theorem le_finset_inf_iff {s : Finset L} {x : L} :
    x ≤ s.inf id ↔ ∀ y ∈ s, x ≤ y := by
  classical
  induction s using Finset.induction with
  | empty =>
      simp
  | insert a s has ih =>
      simp [Finset.inf_insert, ih, le_inf_iff]

/--
If `x < y`, some source-style join-irreducible lies below `y` but not below
`x`. This is the local separator used in Rival's chain-counting argument.
-/
theorem exists_rivalSupIrred_le_not_le_of_lt {x y : L} (hxy : x < y) :
    ∃ j : L, RivalSupIrred j ∧ j ≤ y ∧ ¬j ≤ x := by
  classical
  obtain ⟨s, hsup, hs⟩ := exists_supIrred_decomposition (α := L) y
  by_contra hno
  push Not at hno
  have hall_le_x : ∀ z ∈ s, z ≤ x := by
    intro z hz
    exact hno z (rivalSupIrred_of_supIrred (hs hz))
      (by
        have hz_le_y : z ≤ y := by
          rw [← hsup]
          exact Finset.le_sup (f := id) hz
        exact hz_le_y)
  have hy_le_x : y ≤ x := by
    rw [← hsup]
    exact (finset_sup_le_iff (s := s) (x := x)).2 hall_le_x
  exact (not_le_of_gt hxy) hy_le_x

/--
If `x < y`, some source-style meet-irreducible lies above `x` but not above
`y`. This is the dual separator for Rival's chain-counting argument.
-/
theorem exists_rivalInfIrred_not_le_le_of_lt {x y : L} (hxy : x < y) :
    ∃ m : L, RivalInfIrred m ∧ x ≤ m ∧ ¬y ≤ m := by
  classical
  obtain ⟨s, hinf, hs⟩ := exists_infIrred_decomposition (α := L) x
  by_contra hno
  push Not at hno
  have hall_y_le : ∀ z ∈ s, y ≤ z := by
    intro z hz
    exact hno z (rivalInfIrred_of_infIrred (hs hz))
      (by
        have hx_le_z : x ≤ z := by
          rw [← hinf]
          exact Finset.inf_le (f := id) hz
        exact hx_le_z)
  have hy_le_x : y ≤ x := by
    rw [← hinf]
    exact (le_finset_inf_iff (s := s) (x := y)).2 hall_y_le
  exact (not_le_of_gt hxy) hy_le_x

/-- Source-style join-irreducibles below a point. -/
noncomputable def rivalSupIrredBelow (x : L) : Finset L := by
  classical
  exact (rivalSupIrredFinset L).filter fun j : L => j ≤ x

/-- Source-style meet-irreducibles above a point. -/
noncomputable def rivalInfIrredAbove (x : L) : Finset L := by
  classical
  exact (rivalInfIrredFinset L).filter fun m : L => x ≤ m

omit [BoundedOrder L] in
theorem mem_rivalSupIrredBelow {x j : L} :
    j ∈ rivalSupIrredBelow x ↔ RivalSupIrred j ∧ j ≤ x := by
  classical
  simp [rivalSupIrredBelow, mem_rivalSupIrredFinset]

omit [BoundedOrder L] in
theorem mem_rivalInfIrredAbove {x m : L} :
    m ∈ rivalInfIrredAbove x ↔ RivalInfIrred m ∧ x ≤ m := by
  classical
  simp [rivalInfIrredAbove, mem_rivalInfIrredFinset]

private theorem rivalSupIrredBelow_card_pos (x : L) :
    0 < (rivalSupIrredBelow x).card := by
  classical
  have hmem : (⊥ : L) ∈ rivalSupIrredBelow x := by
    rw [mem_rivalSupIrredBelow]
    exact ⟨rivalSupIrred_bot, bot_le⟩
  exact Finset.card_pos.mpr ⟨⊥, hmem⟩

private theorem rivalInfIrredAbove_card_pos (x : L) :
    0 < (rivalInfIrredAbove x).card := by
  classical
  have hmem : (⊤ : L) ∈ rivalInfIrredAbove x := by
    rw [mem_rivalInfIrredAbove]
    exact ⟨rivalInfIrred_top, le_top⟩
  exact Finset.card_pos.mpr ⟨⊤, hmem⟩

theorem rivalSupIrredBelow_ssubset_of_lt {x y : L} (hxy : x < y) :
    rivalSupIrredBelow x ⊂ rivalSupIrredBelow y := by
  classical
  refine ⟨?_, ?_⟩
  · intro j hj
    rw [mem_rivalSupIrredBelow] at hj ⊢
    exact ⟨hj.1, hj.2.trans hxy.le⟩
  · intro hsubset
    obtain ⟨j, hj, hjy, hjx⟩ := exists_rivalSupIrred_le_not_le_of_lt (L := L) hxy
    have hj_mem_y : j ∈ rivalSupIrredBelow y := by
      rw [mem_rivalSupIrredBelow]
      exact ⟨hj, hjy⟩
    have hj_mem_x := hsubset hj_mem_y
    rw [mem_rivalSupIrredBelow] at hj_mem_x
    exact hjx hj_mem_x.2

theorem rivalInfIrredAbove_ssubset_of_lt {x y : L} (hxy : x < y) :
    rivalInfIrredAbove y ⊂ rivalInfIrredAbove x := by
  classical
  refine ⟨?_, ?_⟩
  · intro m hm
    rw [mem_rivalInfIrredAbove] at hm ⊢
    exact ⟨hm.1, hxy.le.trans hm.2⟩
  · intro hsubset
    obtain ⟨m, hm, hxm, hym⟩ := exists_rivalInfIrred_not_le_le_of_lt (L := L) hxy
    have hm_mem_x : m ∈ rivalInfIrredAbove x := by
      rw [mem_rivalInfIrredAbove]
      exact ⟨hm, hxm⟩
    have hm_mem_y := hsubset hm_mem_x
    rw [mem_rivalInfIrredAbove] at hm_mem_y
    exact hym hm_mem_y.2

omit [Fintype L] [Lattice L] [BoundedOrder L] in
private theorem chain_card_le_of_card_inj
    {s : Finset L}
    (f : L → Nat)
    (hpos : ∀ x ∈ s, 0 < f x)
    (hle : ∀ x ∈ s, f x ≤ N)
    (hinj : Set.InjOn f (s : Set L)) :
    s.card ≤ N := by
  classical
  let g : L → Nat := fun x => f x - 1
  have hmap : Set.MapsTo g (s : Set L) (Finset.range N : Set Nat) := by
    intro x hx
    have hxpos := hpos x hx
    have hxle := hle x hx
    simp [g]
    omega
  have hginj : Set.InjOn g (s : Set L) := by
    intro x hx y hy hxy
    apply hinj hx hy
    have hxpos := hpos x hx
    have hypos := hpos y hy
    dsimp [g] at hxy
    omega
  have hcard := Finset.card_le_card_of_injOn g hmap hginj
  simpa using hcard

theorem chain_card_le_rivalSupIrredFinset_card {s : Finset L}
    (hs : IsChain (· ≤ ·) (s : Set L)) :
    s.card ≤ (rivalSupIrredFinset L).card := by
  classical
  have hinj :
      Set.InjOn (fun x : L => (rivalSupIrredBelow x).card) (s : Set L) := by
    intro x hx y hy hxy
    by_contra hne
    have hcomp := hs hx hy hne
    rcases hcomp with hlexy | hleyx
    · have hltxy : x < y := lt_of_le_of_ne hlexy hne
      have hlt :
          (rivalSupIrredBelow x).card < (rivalSupIrredBelow y).card :=
        Finset.card_lt_card (rivalSupIrredBelow_ssubset_of_lt (L := L) hltxy)
      exact (ne_of_lt hlt) hxy
    · have hltyx : y < x := lt_of_le_of_ne hleyx (Ne.symm hne)
      have hlt :
          (rivalSupIrredBelow y).card < (rivalSupIrredBelow x).card :=
        Finset.card_lt_card (rivalSupIrredBelow_ssubset_of_lt (L := L) hltyx)
      exact (ne_of_gt hlt) hxy
  refine chain_card_le_of_card_inj (L := L) (s := s)
    (fun x => (rivalSupIrredBelow x).card) ?_ ?_ hinj
  · intro x hx
    exact rivalSupIrredBelow_card_pos (L := L) x
  · intro x hx
    unfold rivalSupIrredBelow
    exact Finset.card_filter_le _ _

theorem chain_card_le_rivalInfIrredFinset_card {s : Finset L}
    (hs : IsChain (· ≤ ·) (s : Set L)) :
    s.card ≤ (rivalInfIrredFinset L).card := by
  classical
  have hinj :
      Set.InjOn (fun x : L => (rivalInfIrredAbove x).card) (s : Set L) := by
    intro x hx y hy hxy
    by_contra hne
    have hcomp := hs hx hy hne
    rcases hcomp with hlexy | hleyx
    · have hltxy : x < y := lt_of_le_of_ne hlexy hne
      have hlt :
          (rivalInfIrredAbove y).card < (rivalInfIrredAbove x).card :=
        Finset.card_lt_card (rivalInfIrredAbove_ssubset_of_lt (L := L) hltxy)
      exact (ne_of_gt hlt) hxy
    · have hltyx : y < x := lt_of_le_of_ne hleyx (Ne.symm hne)
      have hlt :
          (rivalInfIrredAbove x).card < (rivalInfIrredAbove y).card :=
        Finset.card_lt_card (rivalInfIrredAbove_ssubset_of_lt (L := L) hltyx)
      exact (ne_of_lt hlt) hxy
  refine chain_card_le_of_card_inj (L := L) (s := s)
    (fun x => (rivalInfIrredAbove x).card) ?_ ?_ hinj
  · intro x hx
    exact rivalInfIrredAbove_card_pos (L := L) x
  · intro x hx
    unfold rivalInfIrredAbove
    exact Finset.card_filter_le _ _

/--
Rival's finite-lattice length inequality in endpoint-inclusive source form.
-/
theorem rival_length_bound_source :
    2 * (latticeLength L + 1) ≤
      Fintype.card L + (rivalDoublyIrredFinset L).card := by
  classical
  obtain ⟨c, hc_chain, hc_card⟩ :=
    exists_chain_card_eq_latticeLength_add_one (L := L)
  have hJ : latticeLength L + 1 ≤ (rivalSupIrredFinset L).card := by
    rw [← hc_card]
    exact chain_card_le_rivalSupIrredFinset_card (L := L) hc_chain
  have hM : latticeLength L + 1 ≤ (rivalInfIrredFinset L).card := by
    rw [← hc_card]
    exact chain_card_le_rivalInfIrredFinset_card (L := L) hc_chain
  have hinter_eq :
      rivalSupIrredFinset L ∩ rivalInfIrredFinset L =
        rivalDoublyIrredFinset L := by
    ext x
    rw [Finset.mem_inter, mem_rivalSupIrredFinset, mem_rivalInfIrredFinset,
      mem_rivalDoublyIrredFinset]
  have hinter :
      (rivalSupIrredFinset L ∩ rivalInfIrredFinset L).card =
        (rivalDoublyIrredFinset L).card := by
    rw [hinter_eq]
  have hcard_union :
      (rivalSupIrredFinset L).card + (rivalInfIrredFinset L).card =
        (rivalSupIrredFinset L ∪ rivalInfIrredFinset L).card +
          (rivalSupIrredFinset L ∩ rivalInfIrredFinset L).card := by
    rw [Finset.card_union_add_card_inter]
  have hunion_le :
      (rivalSupIrredFinset L ∪ rivalInfIrredFinset L).card ≤ Fintype.card L := by
    calc
      (rivalSupIrredFinset L ∪ rivalInfIrredFinset L).card
          ≤ (Finset.univ : Finset L).card := by
            exact Finset.card_le_card (by intro x hx; simp)
      _ = Fintype.card L := by simp
  omega

theorem not_rivalInfIrred_bot_of_minimum
    (hmin : IsMinimumCounterexample L) :
    ¬RivalInfIrred (⊥ : L) := by
  intro hbot
  obtain ⟨a, b, ha, hb, hab⟩ := minimumCounterexample_has_two_atoms hmin
  have hinf : (⊥ : L) = a ⊓ b := by
    exact (ha.disjoint_of_ne hb hab).eq_bot.symm
  rcases hbot a b hinf with haeq | hbeq
  · exact ha.ne_bot haeq.symm
  · exact hb.ne_bot hbeq.symm

theorem not_rivalSupIrred_top_of_minimum
    (hmin : IsMinimumCounterexample L) :
    ¬RivalSupIrred (⊤ : L) := by
  intro htop
  obtain ⟨b, c, hbc, hb, hc⟩ := minimumCounterexample_top_join_reducible hmin
  rcases htop b c hbc.symm with hbeq | hceq
  · exact (ne_of_lt hb) hbeq.symm
  · exact (ne_of_lt hc) hceq.symm

theorem rivalDoublyIrredFinset_eq_doublyIrredFinset_of_minimum
    (hmin : IsMinimumCounterexample L) :
    rivalDoublyIrredFinset L = doublyIrredFinset L := by
  classical
  ext x
  rw [mem_rivalDoublyIrredFinset, mem_doublyIrredFinset]
  constructor
  · intro hx
    have hx_ne_bot : x ≠ ⊥ := by
      intro hxb
      exact not_rivalInfIrred_bot_of_minimum (L := L) hmin (by simpa [hxb] using hx.2)
    have hx_ne_top : x ≠ ⊤ := by
      intro hxt
      exact not_rivalSupIrred_top_of_minimum (L := L) hmin (by simpa [hxt] using hx.1)
    exact ⟨supIrred_of_rivalSupIrred_ne_bot hx.1 hx_ne_bot,
      infIrred_of_rivalInfIrred_ne_top hx.2 hx_ne_top⟩
  · intro hx
    exact ⟨rivalSupIrred_of_supIrred hx.1, rivalInfIrred_of_infIrred hx.2⟩

/--
UC-WP05-L019: Rival's finite-lattice inequality specialized back to the
mathlib-style irreducible set in a minimum counterexample.
-/
theorem minimumCounterexample_rivalBound
    (hmin : IsMinimumCounterexample L) :
    RivalBound L := by
  classical
  unfold RivalBound
  have hsrc := rival_length_bound_source (L := L)
  rwa [rivalDoublyIrredFinset_eq_doublyIrredFinset_of_minimum (L := L) hmin] at hsrc

/--
UC-WP05-L017A: unconditional Bouchard Theorem 2.7 after the local Rival
dependency is discharged.
-/
theorem minimumCounterexample_upperConeCard_gt_latticeLength
    (hmin : IsMinimumCounterexample L)
    {j : L} (hj : SupIrred j) :
    latticeLength L < upperConeCard j :=
  minimumCounterexample_upperConeCard_gt_latticeLength_of_rivalBound
    hmin (minimumCounterexample_rivalBound (L := L) hmin) hj

/--
UC-WP05-L018A: unconditional Bouchard Corollary 2.8 after the local Rival
dependency is discharged.
-/
theorem minimumCounterexample_doublyIrred_lt_nonTop_doublyReducible
    (hmin : IsMinimumCounterexample L)
    {x : L} (hxSup : SupIrred x) (hxInf : InfIrred x) :
    ∃ y : L, x < y ∧ y ≠ ⊤ ∧ ¬SupIrred y ∧ ¬InfIrred y :=
  minimumCounterexample_doublyIrred_lt_nonTop_doublyReducible_of_rivalBound
    hmin (minimumCounterexample_rivalBound (L := L) hmin) hxSup hxInf

end MathCert.UnionClosed.Lattice
