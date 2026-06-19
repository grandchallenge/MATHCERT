import Mathlib.Data.Fintype.Order
import Mathlib.Order.Atoms.Finite
import Mathlib.Order.Bounds.Basic
import Mathlib.Order.Hom.Lattice
import Mathlib.Order.Irreducible

/-!
# Deleting an irreducible element from a finite lattice

This file supplies the deletion construction used in Bouchard's
minimum-counterexample arguments. If `a` is sup-irreducible, deleting `a`
preserves joins. A meet that was equal to `a` is replaced by the greatest
element strictly below `a`.
-/

namespace MathCert.UnionClosed.Lattice

open Finset Set

variable {L : Type*} [Fintype L] [Lattice L] [BoundedOrder L]

/-- The induced ordered subtype obtained by deleting one element. -/
abbrev Deleted (a : L) := {x : L // x ≠ a}

/-- The supremum of all elements strictly below `a`. -/
noncomputable def lowerCover (a : L) : L := by
  classical
  exact (Finset.univ.filter fun x => x < a).sup id

theorem lowerCover_le (a : L) : lowerCover a ≤ a := by
  classical
  apply Finset.sup_le
  intro x hx
  simp only [Finset.mem_filter, Finset.mem_univ, true_and] at hx
  exact hx.le

theorem lowerCover_lt {a : L} (ha : SupIrred a) : lowerCover a < a := by
  classical
  have hle := lowerCover_le a
  refine lt_of_le_of_ne hle ?_
  intro hEq
  have hmember :=
    ha.finset_sup_eq
      (s := Finset.univ.filter fun x => x < a)
      (f := id)
      (by simpa [lowerCover] using hEq)
  obtain ⟨x, hx, hxa⟩ := hmember
  simp only [Finset.mem_filter, Finset.mem_univ, true_and] at hx
  simp only [id_eq] at hxa
  subst x
  exact (lt_irrefl a) hx

theorem le_lowerCover_of_lt {a x : L} (hx : x < a) : x ≤ lowerCover a := by
  classical
  apply Finset.le_sup (f := id)
  simp [hx]

/-- Join in the lattice obtained by deleting a sup-irreducible element. -/
noncomputable def deletedSup {a : L} (ha : SupIrred a)
    (x y : Deleted a) : Deleted a :=
  ⟨x.1 ⊔ y.1, by
    intro h
    rcases ha.2 h with hx | hy
    · exact x.2 hx
    · exact y.2 hy⟩

/-- Meet in the lattice obtained by deleting a sup-irreducible element. -/
noncomputable def deletedInf {a : L} (ha : SupIrred a)
    (x y : Deleted a) : Deleted a := by
  classical
  exact if h : x.1 ⊓ y.1 = a then
    ⟨lowerCover a, ne_of_lt (lowerCover_lt ha)⟩
  else
    ⟨x.1 ⊓ y.1, h⟩

omit [Fintype L] [BoundedOrder L] in
private theorem isLUB_deletedSup {a : L} (ha : SupIrred a)
    (x y : Deleted a) :
    IsLUB {x, y} (deletedSup ha x y) := by
  constructor
  · intro z hz
    rcases hz with rfl | hz
    · exact le_sup_left
    · rw [Set.mem_singleton_iff] at hz
      subst z
      exact le_sup_right
  · intro z hz
    exact sup_le (hz (by simp)) (hz (by simp))

private theorem isGLB_deletedInf {a : L} (ha : SupIrred a)
    (x y : Deleted a) :
    IsGLB {x, y} (deletedInf ha x y) := by
  by_cases hxy : x.1 ⊓ y.1 = a
  · rw [deletedInf, dif_pos hxy]
    constructor
    · intro z hz
      rcases hz with rfl | hz
      · exact (lowerCover_le a).trans (hxy.ge.trans inf_le_left)
      · rw [Set.mem_singleton_iff] at hz
        subst z
        exact (lowerCover_le a).trans (hxy.ge.trans inf_le_right)
    · intro z hz
      have hza : z.1 ≤ a := by
        exact (le_inf (hz (by simp)) (hz (by simp))).trans hxy.le
      exact le_lowerCover_of_lt (lt_of_le_of_ne hza z.2)
  · rw [deletedInf, dif_neg hxy]
    constructor
    · intro z hz
      rcases hz with rfl | hz
      · exact inf_le_left
      · rw [Set.mem_singleton_iff] at hz
        subst z
        exact inf_le_right
    · intro z hz
      exact le_inf (hz (by simp)) (hz (by simp))

/--
UC-WP05-L002, Bouchard deletion lemma, sup-irreducible direction: removing a
sup-irreducible element from a finite bounded lattice leaves a lattice.
-/
@[implicit_reducible]
noncomputable def deletedSupIrredLattice {a : L} (ha : SupIrred a) :
    Lattice (Deleted a) :=
  Lattice.ofIsLUBofIsGLB (deletedSup ha) (deletedInf ha)
    (isLUB_deletedSup ha) (isGLB_deletedInf ha)

/-- The infimum of all elements strictly above `a`. -/
noncomputable def upperCover (a : L) : L := by
  classical
  exact (Finset.univ.filter fun x => a < x).inf id

theorem le_upperCover (a : L) : a ≤ upperCover a := by
  classical
  apply Finset.le_inf
  intro x hx
  simp only [Finset.mem_filter, Finset.mem_univ, true_and] at hx
  exact hx.le

theorem lt_upperCover {a : L} (ha : InfIrred a) : a < upperCover a := by
  classical
  have hle := le_upperCover a
  refine lt_of_le_of_ne hle ?_
  intro hEq
  have hmember :=
    ha.finset_inf_eq
      (s := Finset.univ.filter fun x => a < x)
      (f := id)
      (by simpa [upperCover] using hEq.symm)
  obtain ⟨x, hx, hxa⟩ := hmember
  simp only [Finset.mem_filter, Finset.mem_univ, true_and] at hx
  simp only [id_eq] at hxa
  subst x
  exact (lt_irrefl a) hx

theorem upperCover_le_of_lt {a x : L} (hx : a < x) : upperCover a ≤ x := by
  classical
  apply Finset.inf_le (f := id)
  simp [hx]

/-- Meet in the lattice obtained by deleting an inf-irreducible element. -/
noncomputable def deletedInfOfInfIrred {a : L} (ha : InfIrred a)
    (x y : Deleted a) : Deleted a :=
  ⟨x.1 ⊓ y.1, by
    intro h
    rcases ha.2 h with hx | hy
    · exact x.2 hx
    · exact y.2 hy⟩

/-- Join in the lattice obtained by deleting an inf-irreducible element. -/
noncomputable def deletedSupOfInfIrred {a : L} (ha : InfIrred a)
    (x y : Deleted a) : Deleted a := by
  classical
  exact if h : x.1 ⊔ y.1 = a then
    ⟨upperCover a, ne_of_gt (lt_upperCover ha)⟩
  else
    ⟨x.1 ⊔ y.1, h⟩

omit [Fintype L] [BoundedOrder L] in
private theorem isGLB_deletedInfOfInfIrred {a : L} (ha : InfIrred a)
    (x y : Deleted a) :
    IsGLB {x, y} (deletedInfOfInfIrred ha x y) := by
  constructor
  · intro z hz
    rcases hz with rfl | hz
    · exact inf_le_left
    · rw [Set.mem_singleton_iff] at hz
      subst z
      exact inf_le_right
  · intro z hz
    exact le_inf (hz (by simp)) (hz (by simp))

private theorem isLUB_deletedSupOfInfIrred {a : L} (ha : InfIrred a)
    (x y : Deleted a) :
    IsLUB {x, y} (deletedSupOfInfIrred ha x y) := by
  by_cases hxy : x.1 ⊔ y.1 = a
  · rw [deletedSupOfInfIrred, dif_pos hxy]
    constructor
    · intro z hz
      rcases hz with rfl | hz
      · exact (le_sup_left.trans hxy.le).trans (le_upperCover a)
      · rw [Set.mem_singleton_iff] at hz
        subst z
        exact (le_sup_right.trans hxy.le).trans (le_upperCover a)
    · intro z hz
      have haz : a ≤ z.1 := by
        exact hxy.ge.trans (sup_le (hz (by simp)) (hz (by simp)))
      exact upperCover_le_of_lt (lt_of_le_of_ne haz (Ne.symm z.2))
  · rw [deletedSupOfInfIrred, dif_neg hxy]
    constructor
    · intro z hz
      rcases hz with rfl | hz
      · exact le_sup_left
      · rw [Set.mem_singleton_iff] at hz
        subst z
        exact le_sup_right
    · intro z hz
      exact sup_le (hz (by simp)) (hz (by simp))

/--
UC-WP05-L003, Bouchard deletion lemma, inf-irreducible direction: removing an
inf-irreducible element from a finite bounded lattice leaves a lattice.
-/
@[implicit_reducible]
noncomputable def deletedInfIrredLattice {a : L} (ha : InfIrred a) :
    Lattice (Deleted a) :=
  Lattice.ofIsLUBofIsGLB (deletedSupOfInfIrred ha) (deletedInfOfInfIrred ha)
    (isLUB_deletedSupOfInfIrred ha) (isGLB_deletedInfOfInfIrred ha)

/-- The induced ordered subtype obtained by deleting a finite set. -/
abbrev DeletedFinset (s : Finset L) := {x : L // x ∉ s}

/-- Surviving common lower bounds of two elements after deleting `s`. -/
noncomputable def remainingLowerBounds (s : Finset L) (x y : L) : Finset L := by
  classical
  exact Finset.univ.filter fun z => z ∉ s ∧ z ≤ x ∧ z ≤ y

/-- Surviving common upper bounds of two elements after deleting `s`. -/
noncomputable def remainingUpperBounds (s : Finset L) (x y : L) : Finset L := by
  classical
  exact Finset.univ.filter fun z => z ∉ s ∧ x ≤ z ∧ y ≤ z

/-- Join after deleting a finite set of sup-irreducible elements. -/
noncomputable def deletedFinsetSupOfSupIrred
    {s : Finset L} (hs : ∀ a ∈ s, SupIrred a)
    (x y : DeletedFinset s) : DeletedFinset s :=
  ⟨x.1 ⊔ y.1, by
    intro hmem
    rcases (hs _ hmem).2 rfl with hx | hy
    · exact x.2 (hx ▸ hmem)
    · exact y.2 (hy ▸ hmem)⟩

/-- Meet after deleting a finite set of sup-irreducible elements. -/
noncomputable def deletedFinsetInfOfSupIrred
    {s : Finset L} (hs : ∀ a ∈ s, SupIrred a)
    (x y : DeletedFinset s) : DeletedFinset s := by
  classical
  let t := remainingLowerBounds s x.1 y.1
  refine ⟨t.sup id, ?_⟩
  intro hmem
  obtain ⟨z, hz, hza⟩ := (hs _ hmem).finset_sup_eq rfl
  have hz' : z ∈ remainingLowerBounds s x.1 y.1 := by
    simpa [t] using hz
  have hznot : z ∉ s := (Finset.mem_filter.mp hz').2.1
  apply hznot
  rw [show z = t.sup id by simpa only [id_eq] using hza]
  exact hmem

omit [Fintype L] [BoundedOrder L] in
private theorem isLUB_deletedFinsetSupOfSupIrred
    {s : Finset L} (hs : ∀ a ∈ s, SupIrred a)
    (x y : DeletedFinset s) :
    IsLUB {x, y} (deletedFinsetSupOfSupIrred hs x y) := by
  constructor
  · intro z hz
    rcases hz with rfl | hz
    · exact le_sup_left
    · rw [Set.mem_singleton_iff] at hz
      subst z
      exact le_sup_right
  · intro z hz
    exact sup_le (hz (by simp)) (hz (by simp))

private theorem isGLB_deletedFinsetInfOfSupIrred
    {s : Finset L} (hs : ∀ a ∈ s, SupIrred a)
    (x y : DeletedFinset s) :
    IsGLB {x, y} (deletedFinsetInfOfSupIrred hs x y) := by
  classical
  constructor
  · intro z hz
    rcases hz with rfl | hz
    · change (remainingLowerBounds s z.1 y.1).sup id ≤ z.1
      apply Finset.sup_le
      intro w hw
      exact (Finset.mem_filter.mp hw).2.2.1
    · rw [Set.mem_singleton_iff] at hz
      subst z
      change (remainingLowerBounds s x.1 y.1).sup id ≤ y.1
      apply Finset.sup_le
      intro w hw
      exact (Finset.mem_filter.mp hw).2.2.2
  · intro z hz
    change z.1 ≤ (remainingLowerBounds s x.1 y.1).sup id
    apply Finset.le_sup (f := id)
    simp only [remainingLowerBounds, Finset.mem_filter, Finset.mem_univ, true_and]
    exact ⟨z.2, hz (by simp), hz (by simp)⟩

/--
UC-WP05-L008, Bouchard Theorem 1.4, sup-irreducible direction: deleting a
finite set consisting entirely of sup-irreducible elements leaves a lattice.
-/
@[implicit_reducible]
noncomputable def deletedFinsetSupIrredLattice
    {s : Finset L} (hs : ∀ a ∈ s, SupIrred a) :
    Lattice (DeletedFinset s) :=
  Lattice.ofIsLUBofIsGLB
    (deletedFinsetSupOfSupIrred hs) (deletedFinsetInfOfSupIrred hs)
    (isLUB_deletedFinsetSupOfSupIrred hs) (isGLB_deletedFinsetInfOfSupIrred hs)

/-- Meet after deleting a finite set of inf-irreducible elements. -/
noncomputable def deletedFinsetInfOfInfIrred
    {s : Finset L} (hs : ∀ a ∈ s, InfIrred a)
    (x y : DeletedFinset s) : DeletedFinset s :=
  ⟨x.1 ⊓ y.1, by
    intro hmem
    rcases (hs _ hmem).2 rfl with hx | hy
    · exact x.2 (hx ▸ hmem)
    · exact y.2 (hy ▸ hmem)⟩

/-- Join after deleting a finite set of inf-irreducible elements. -/
noncomputable def deletedFinsetSupOfInfIrred
    {s : Finset L} (hs : ∀ a ∈ s, InfIrred a)
    (x y : DeletedFinset s) : DeletedFinset s := by
  classical
  let t := remainingUpperBounds s x.1 y.1
  refine ⟨t.inf id, ?_⟩
  intro hmem
  obtain ⟨z, hz, hza⟩ := (hs _ hmem).finset_inf_eq rfl
  have hz' : z ∈ remainingUpperBounds s x.1 y.1 := by
    simpa [t] using hz
  have hznot : z ∉ s := (Finset.mem_filter.mp hz').2.1
  apply hznot
  rw [show z = t.inf id by simpa only [id_eq] using hza]
  exact hmem

omit [Fintype L] [BoundedOrder L] in
private theorem isGLB_deletedFinsetInfOfInfIrred
    {s : Finset L} (hs : ∀ a ∈ s, InfIrred a)
    (x y : DeletedFinset s) :
    IsGLB {x, y} (deletedFinsetInfOfInfIrred hs x y) := by
  constructor
  · intro z hz
    rcases hz with rfl | hz
    · exact inf_le_left
    · rw [Set.mem_singleton_iff] at hz
      subst z
      exact inf_le_right
  · intro z hz
    exact le_inf (hz (by simp)) (hz (by simp))

private theorem isLUB_deletedFinsetSupOfInfIrred
    {s : Finset L} (hs : ∀ a ∈ s, InfIrred a)
    (x y : DeletedFinset s) :
    IsLUB {x, y} (deletedFinsetSupOfInfIrred hs x y) := by
  classical
  constructor
  · intro z hz
    rcases hz with rfl | hz
    · change z.1 ≤ (remainingUpperBounds s z.1 y.1).inf id
      apply Finset.le_inf
      intro w hw
      exact (Finset.mem_filter.mp hw).2.2.1
    · rw [Set.mem_singleton_iff] at hz
      subst z
      change y.1 ≤ (remainingUpperBounds s x.1 y.1).inf id
      apply Finset.le_inf
      intro w hw
      exact (Finset.mem_filter.mp hw).2.2.2
  · intro z hz
    change (remainingUpperBounds s x.1 y.1).inf id ≤ z.1
    apply Finset.inf_le (f := id)
    simp only [remainingUpperBounds, Finset.mem_filter, Finset.mem_univ, true_and]
    exact ⟨z.2, hz (by simp), hz (by simp)⟩

/--
UC-WP05-L008, Bouchard Theorem 1.4, inf-irreducible direction: deleting a
finite set consisting entirely of inf-irreducible elements leaves a lattice.
-/
@[implicit_reducible]
noncomputable def deletedFinsetInfIrredLattice
    {s : Finset L} (hs : ∀ a ∈ s, InfIrred a) :
    Lattice (DeletedFinset s) :=
  Lattice.ofIsLUBofIsGLB
    (deletedFinsetSupOfInfIrred hs) (deletedFinsetInfOfInfIrred hs)
    (isLUB_deletedFinsetSupOfInfIrred hs) (isGLB_deletedFinsetInfOfInfIrred hs)

/--
The least surviving element above `x` after deleting a finite set of
inf-irreducible elements.
-/
noncomputable def deletedFinsetCeilOfInfIrred
    {s : Finset L} (hs : ∀ a ∈ s, InfIrred a)
    (x : L) : DeletedFinset s := by
  classical
  let t := Finset.univ.filter fun z => z ∉ s ∧ x ≤ z
  refine ⟨t.inf id, ?_⟩
  intro hmem
  obtain ⟨z, hz, hza⟩ := (hs _ hmem).finset_inf_eq rfl
  have hz' : z ∈ t := by simpa [t] using hz
  have hznot : z ∉ s := (Finset.mem_filter.mp hz').2.1
  apply hznot
  rw [show z = t.inf id by simpa only [id_eq] using hza]
  exact hmem

theorem le_deletedFinsetCeilOfInfIrred
    {s : Finset L} (hs : ∀ a ∈ s, InfIrred a)
    (x : L) :
    x ≤ (deletedFinsetCeilOfInfIrred hs x).1 := by
  classical
  apply Finset.le_inf
  intro z hz
  exact (Finset.mem_filter.mp hz).2.2

theorem deletedFinsetCeilOfInfIrred_le
    {s : Finset L} (hs : ∀ a ∈ s, InfIrred a)
    {x z : L} (hz : z ∉ s) (hxz : x ≤ z) :
    deletedFinsetCeilOfInfIrred hs x ≤ (⟨z, hz⟩ : DeletedFinset s) := by
  classical
  apply Finset.inf_le (f := id)
  simp [hz, hxz]

theorem deletedFinsetCeilOfInfIrred_eq
    {s : Finset L} (hs : ∀ a ∈ s, InfIrred a)
    {x : L} (hx : x ∉ s) :
    deletedFinsetCeilOfInfIrred hs x = (⟨x, hx⟩ : DeletedFinset s) := by
  apply le_antisymm
  · exact deletedFinsetCeilOfInfIrred_le hs hx le_rfl
  · exact le_deletedFinsetCeilOfInfIrred hs x

theorem deletedFinsetCeilOfInfIrred_sup
    {s : Finset L} (hs : ∀ a ∈ s, InfIrred a)
    (x y : L) :
    letI : Lattice (DeletedFinset s) := deletedFinsetInfIrredLattice hs
    deletedFinsetCeilOfInfIrred hs (x ⊔ y) =
      deletedFinsetCeilOfInfIrred hs x ⊔
        deletedFinsetCeilOfInfIrred hs y := by
  letI : Lattice (DeletedFinset s) := deletedFinsetInfIrredLattice hs
  apply le_antisymm
  · apply deletedFinsetCeilOfInfIrred_le hs
      (deletedFinsetCeilOfInfIrred hs x ⊔
        deletedFinsetCeilOfInfIrred hs y).2
    have hx' :
        deletedFinsetCeilOfInfIrred hs x ≤
          deletedFinsetCeilOfInfIrred hs x ⊔
            deletedFinsetCeilOfInfIrred hs y := le_sup_left
    have hy' :
        deletedFinsetCeilOfInfIrred hs y ≤
          deletedFinsetCeilOfInfIrred hs x ⊔
            deletedFinsetCeilOfInfIrred hs y := le_sup_right
    exact sup_le
      ((le_deletedFinsetCeilOfInfIrred hs x).trans hx')
      ((le_deletedFinsetCeilOfInfIrred hs y).trans hy')
  · apply sup_le
    · apply deletedFinsetCeilOfInfIrred_le hs
        (deletedFinsetCeilOfInfIrred hs (x ⊔ y)).2
      exact le_sup_left.trans (le_deletedFinsetCeilOfInfIrred hs (x ⊔ y))
    · apply deletedFinsetCeilOfInfIrred_le hs
        (deletedFinsetCeilOfInfIrred hs (x ⊔ y)).2
      exact le_sup_right.trans (le_deletedFinsetCeilOfInfIrred hs (x ⊔ y))

/-- Homogeneous inf-irreducible deletion induces a surjective join map. -/
noncomputable def deletedFinsetCeilSupHom
    {s : Finset L} (hs : ∀ a ∈ s, InfIrred a) :
    letI : Lattice (DeletedFinset s) := deletedFinsetInfIrredLattice hs
    SupHom L (DeletedFinset s) := by
  letI : Lattice (DeletedFinset s) := deletedFinsetInfIrredLattice hs
  exact
    { toFun := deletedFinsetCeilOfInfIrred hs
      map_sup' := deletedFinsetCeilOfInfIrred_sup hs }

/--
Every sup-irreducible element created by homogeneous inf-irreducible deletion
is the least surviving element above an original sup-irreducible element.
-/
theorem deletedFinset_supIrred_has_origin
    {s : Finset L} (hs : ∀ a ∈ s, InfIrred a)
    (q : DeletedFinset s)
    (hq :
      letI : Lattice (DeletedFinset s) := deletedFinsetInfIrredLattice hs
      SupIrred q) :
    ∃ j : L,
      SupIrred j ∧ deletedFinsetCeilOfInfIrred hs j = q := by
  classical
  letI : Lattice (DeletedFinset s) := deletedFinsetInfIrredLattice hs
  have htop : (⊤ : L) ∉ s := by
    intro hmem
    exact (hs _ hmem).ne_top rfl
  letI : Nonempty (DeletedFinset s) := ⟨⟨⊤, htop⟩⟩
  letI : BoundedOrder (DeletedFinset s) := Fintype.toBoundedOrder _
  have hq' : SupIrred q := hq
  obtain ⟨t, htq, ht⟩ := exists_supIrred_decomposition q.1
  have htne : t.Nonempty := by
    rw [Finset.nonempty_iff_ne_empty]
    intro htempty
    subst t
    simp only [Finset.sup_empty] at htq
    apply hq'.not_isMin
    intro z _
    change q.1 ≤ z.1
    rw [← htq]
    exact bot_le
  let f := deletedFinsetCeilSupHom hs
  have hmap : t.sup (fun j => f j) = q := by
    rw [← Finset.sup'_eq_sup htne]
    calc
      t.sup' htne (fun j => f j) = f (t.sup' htne id) := by
        symm
        simpa only [Function.comp_apply, id_eq] using
          (map_finset_sup' f htne id)
      _ = f q.1 := by rw [Finset.sup'_eq_sup htne, htq]
      _ = q := deletedFinsetCeilOfInfIrred_eq hs q.2
  obtain ⟨j, hjt, hjq⟩ := hq'.finset_sup_eq hmap
  exact ⟨j, ht hjt, by simpa [f, deletedFinsetCeilSupHom] using hjq⟩

end MathCert.UnionClosed.Lattice
