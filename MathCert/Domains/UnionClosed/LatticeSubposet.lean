import Mathlib.Data.Fintype.Order
import Mathlib.Order.Atoms.Finite
import Mathlib.Order.Hom.Basic
import Mathlib.Order.Irreducible

/-!
# Finite induced subposets of finite lattices

Bouchard's Theorem 2.15 works with a finite lattice subposet of a minimum
counterexample.  The Lean representation used here is a finite lattice `K`
equipped with an order embedding `e : K ↪o L` into the ambient lattice `L`.
The carrier inside `L` is the finite image of `e`.

This avoids typeclass diamonds from putting arbitrary lattice operations on a
subtype while still recording exactly that the subposet order is induced from
the ambient order.
-/

namespace MathCert.UnionClosed.Lattice

open Finset Set

universe u

variable {L K : Type u}
variable [Fintype L] [Lattice L] [BoundedOrder L]
variable [Fintype K] [Lattice K] [BoundedOrder K]

namespace EmbeddedSubposet

/-- The finite carrier of an embedded finite subposet. -/
noncomputable def carrier (e : K ↪o L) : Finset L := by
  classical
  exact Finset.univ.image e

omit [Fintype L] [BoundedOrder L] [BoundedOrder K] in
@[simp]
theorem mem_carrier {e : K ↪o L} {y : L} :
    y ∈ carrier e ↔ ∃ x : K, e x = y := by
  classical
  simp [carrier]

omit [Fintype L] [BoundedOrder L] [BoundedOrder K] in
@[simp]
theorem apply_mem_carrier (e : K ↪o L) (x : K) :
    e x ∈ carrier e := by
  classical
  exact (mem_carrier (e := e)).2 ⟨x, rfl⟩

/-- A boundary touch by a non-endpoint element of an embedded finite subposet. -/
def HasBoundaryTouch (e : K ↪o L) : Prop :=
  ∃ x : K, x ≠ ⊥ ∧ x ≠ ⊤ ∧
    ∃ y : L, y ∉ carrier e ∧ (y ⋖ e x ∨ e x ⋖ y)

omit [Fintype L] [BoundedOrder L] in
theorem lower_cover_mem_of_noBoundary
    {e : K ↪o L} (hno : ¬HasBoundaryTouch e)
    {x : K} (hx_bot : x ≠ ⊥) (hx_top : x ≠ ⊤)
    {y : L} (hyx : y ⋖ e x) :
    y ∈ carrier e := by
  classical
  by_contra hy
  exact hno ⟨x, hx_bot, hx_top, y, hy, Or.inl hyx⟩

omit [Fintype L] [BoundedOrder L] in
theorem upper_cover_mem_of_noBoundary
    {e : K ↪o L} (hno : ¬HasBoundaryTouch e)
    {x : K} (hx_bot : x ≠ ⊥) (hx_top : x ≠ ⊤)
    {y : L} (hxy : e x ⋖ y) :
    y ∈ carrier e := by
  classical
  by_contra hy
  exact hno ⟨x, hx_bot, hx_top, y, hy, Or.inr hxy⟩

omit [BoundedOrder L] in
private theorem cover_below_mem_of_noBoundary
    {e : K ↪o L} (hno : ¬HasBoundaryTouch e)
    {q : K} (hq_bot : q ≠ ⊥) (hq_top : q ≠ ⊤)
    {a : L} (haq : a < e q) :
    ∃ z : K, a ≤ e z ∧ e z ⋖ e q := by
  classical
  obtain ⟨z, haz, hzq⟩ := haq.exists_le_covby
  have hzmem : z ∈ carrier e :=
    lower_cover_mem_of_noBoundary hno hq_bot hq_top hzq
  obtain ⟨z', hz'⟩ := (mem_carrier (e := e)).1 hzmem
  exact ⟨z', by simpa [hz'] using haz, by simpa [hz'] using hzq⟩

omit [BoundedOrder L] in
/--
If an internal non-top sup-irreducible element has no ambient boundary touch,
then its image is sup-irreducible in the ambient lattice.
-/
theorem ambient_supIrred_of_noBoundary
    {e : K ↪o L} (hno : ¬HasBoundaryTouch e)
    {q : K} (hq : SupIrred q) (hq_top : q ≠ ⊤) :
    SupIrred (e q) := by
  classical
  have hq_bot : q ≠ ⊥ := by
    intro h
    exact hq.not_isMin (by simp [h])
  constructor
  · intro hmin
    apply hq.not_isMin
    intro z hz
    exact (e.le_iff_le.mp (hmin (e.le_iff_le.mpr hz)))
  · intro a b hab
    by_cases ha : a = e q
    · exact Or.inl ha
    by_cases hb : b = e q
    · exact Or.inr hb
    have ha_le : a ≤ e q := by
      rw [← hab]
      exact le_sup_left
    have hb_le : b ≤ e q := by
      rw [← hab]
      exact le_sup_right
    have ha_lt : a < e q := lt_of_le_of_ne ha_le ha
    have hb_lt : b < e q := lt_of_le_of_ne hb_le hb
    obtain ⟨za, haza, hzaq⟩ :=
      cover_below_mem_of_noBoundary hno hq_bot hq_top ha_lt
    obtain ⟨zb, hbzb, hzbq⟩ :=
      cover_below_mem_of_noBoundary hno hq_bot hq_top hb_lt
    have hjoin : za ⊔ zb = q := by
      apply le_antisymm
      · exact sup_le (e.le_iff_le.mp hzaq.le) (e.le_iff_le.mp hzbq.le)
      · apply e.le_iff_le.mp
        rw [← hab]
        exact sup_le
          (haza.trans (e.le_iff_le.mpr le_sup_left))
          (hbzb.trans (e.le_iff_le.mpr le_sup_right))
    rcases hq.2 hjoin with hza | hzb
    · have hval := congrArg e hza
      exact (hzaq.ne hval).elim
    · have hval := congrArg e hzb
      exact (hzbq.ne hval).elim

omit [BoundedOrder L] in
private theorem cover_above_mem_of_noBoundary
    {e : K ↪o L} (hno : ¬HasBoundaryTouch e)
    {q : K} (hq_bot : q ≠ ⊥) (hq_top : q ≠ ⊤)
    {a : L} (hqa : e q < a) :
    ∃ z : K, e q ⋖ e z ∧ e z ≤ a := by
  classical
  obtain ⟨z, hqz, hza⟩ := hqa.exists_covby_le
  have hzmem : z ∈ carrier e :=
    upper_cover_mem_of_noBoundary hno hq_bot hq_top hqz
  obtain ⟨z', hz'⟩ := (mem_carrier (e := e)).1 hzmem
  exact ⟨z', by simpa [hz'] using hqz, by simpa [hz'] using hza⟩

omit [BoundedOrder L] in
/--
If an internal non-bottom inf-irreducible element has no ambient boundary
touch, then its image is inf-irreducible in the ambient lattice.
-/
theorem ambient_infIrred_of_noBoundary
    {e : K ↪o L} (hno : ¬HasBoundaryTouch e)
    {q : K} (hq : InfIrred q) (hq_bot : q ≠ ⊥) :
    InfIrred (e q) := by
  classical
  have hq_top : q ≠ ⊤ := by
    intro h
    exact hq.1 (by simp [h])
  constructor
  · intro hmax
    apply hq.1
    intro z hz
    exact e.le_iff_le.mp (hmax (e.le_iff_le.mpr hz))
  · intro a b hab
    by_cases ha : a = e q
    · exact Or.inl ha
    by_cases hb : b = e q
    · exact Or.inr hb
    have ha_le : e q ≤ a := by
      rw [← hab]
      exact inf_le_left
    have hb_le : e q ≤ b := by
      rw [← hab]
      exact inf_le_right
    have ha_lt : e q < a := lt_of_le_of_ne ha_le (Ne.symm ha)
    have hb_lt : e q < b := lt_of_le_of_ne hb_le (Ne.symm hb)
    obtain ⟨za, hqza, hzaa⟩ :=
      cover_above_mem_of_noBoundary hno hq_bot hq_top ha_lt
    obtain ⟨zb, hqzb, hzbb⟩ :=
      cover_above_mem_of_noBoundary hno hq_bot hq_top hb_lt
    have hmeet : za ⊓ zb = q := by
      apply le_antisymm
      · apply e.le_iff_le.mp
        rw [← hab]
        exact le_inf
          ((e.le_iff_le.mpr inf_le_left).trans hzaa)
          ((e.le_iff_le.mpr inf_le_right).trans hzbb)
      · exact le_inf (e.le_iff_le.mp hqza.le) (e.le_iff_le.mp hqzb.le)
    rcases hq.2 hmeet with hza | hzb
    · have hval := congrArg e hza
      exact False.elim ((ne_of_lt hqza.lt) hval.symm)
    · have hval := congrArg e hzb
      exact False.elim ((ne_of_lt hqzb.lt) hval.symm)

omit [BoundedOrder L] in
private theorem upper_candidate_top_le_of_noBoundary
    {e : K ↪o L} (hno : ¬HasBoundaryTouch e)
    {q : K} (hq_bot : q ≠ ⊥) (_hq_top : q ≠ ⊤)
    {y : L} (hqy : e q ≤ y) (hy : y ∉ carrier e) :
    e (⊤ : K) ≤ y := by
  classical
  let candidates : Finset K :=
    Finset.univ.filter fun z => q ≤ z ∧ e z ≤ y
  have hqmem : q ∈ candidates := by
    simp [candidates, hqy]
  obtain ⟨z, hzmax⟩ := candidates.exists_maximal ⟨q, hqmem⟩
  have hzcand : z ∈ candidates := hzmax.1
  have hqz : q ≤ z := (Finset.mem_filter.mp hzcand).2.1
  have hzy : e z ≤ y := (Finset.mem_filter.mp hzcand).2.2
  by_cases hz_top : z = ⊤
  · simpa [hz_top] using hzy
  have hz_bot : z ≠ ⊥ := by
    intro hzbot
    apply hq_bot
    have hqbot : q ≤ ⊥ := by
      simpa [hzbot] using hqz
    exact le_antisymm hqbot bot_le
  have hzy_lt : e z < y := by
    refine lt_of_le_of_ne hzy ?_
    intro hzy_eq
    exact hy (by
      rw [← hzy_eq]
      exact apply_mem_carrier e z)
  obtain ⟨w, hzw, hwy⟩ := hzy_lt.exists_covby_le
  exfalso
  by_cases hwmem : w ∈ carrier e
  · obtain ⟨w', hw'⟩ := (mem_carrier (e := e)).1 hwmem
    have hwcand : w' ∈ candidates := by
      simp only [candidates, Finset.mem_filter, Finset.mem_univ, true_and]
      exact ⟨hqz.trans (e.le_iff_le.mp (by simpa [hw'] using hzw.le)),
        by simpa [hw'] using hwy⟩
    have hwz : w' ≤ z :=
      hzmax.2 hwcand (e.le_iff_le.mp (by simpa [hw'] using hzw.le))
    exact (not_le_of_gt hzw.lt) (by simpa [hw'] using e.le_iff_le.mpr hwz)
  · exact (hno ⟨z, hz_bot, hz_top, w, hwmem, Or.inr hzw⟩).elim

/--
Under a no-boundary hypothesis and a coatom below the embedded top, every
ambient upper-cone point outside the embedded carrier is the ambient top.
-/
theorem outside_upperCone_eq_top_of_noBoundary
    {e : K ↪o L} (hno : ¬HasBoundaryTouch e)
    {d : L} (hd : IsCoatom d) (hdle : d ≤ e (⊤ : K))
    {q : K} (hq_bot : q ≠ ⊥) (hq_top : q ≠ ⊤)
    {y : L} (hqy : e q ≤ y) (hy : y ∉ carrier e) :
    y = ⊤ := by
  classical
  have htop_le : e (⊤ : K) ≤ y :=
    upper_candidate_top_le_of_noBoundary hno hq_bot hq_top hqy hy
  have hdy : d ≤ y := hdle.trans htop_le
  rcases hd.le_iff.mp hdy with h_top | h_eq
  · exact h_top
  · have hytop_mem : y ∈ carrier e := by
      have htop_eq : e (⊤ : K) = y :=
        le_antisymm htop_le (by simpa [h_eq] using hdle)
      rw [← htop_eq]
      exact apply_mem_carrier e ⊤
    exact (hy hytop_mem).elim

end EmbeddedSubposet

end MathCert.UnionClosed.Lattice
