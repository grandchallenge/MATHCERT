/-
  IdealFamily/Core.lean

  Purpose.
    Core definitions and basic API for finite set families on a fixed ground set:
      • SetFamily: ground, membership predicate, carrier (filtered powerset)
      • Ideal: SetFamily + {∅} ∈ F, ground ∈ F, and downward closure below non-ground
      • Basic numerics: numEdges, totalSize, degreeNat/degree, normalizedDegreeAt, nds

  Notes.
    – No UC/NEP assumptions appear anywhere in this file.
    – Arithmetic exposed to other modules is in ℤ; naturals are cast explicitly.
    – One-import-per-line policy; no `induction'`, no `simpa using`.
-/
import Mathlib.Data.Finset.Basic
import Mathlib.Data.Finset.Card
import Mathlib.Data.Finset.Powerset
import Mathlib.Algebra.BigOperators.Group.Finset.Basic

namespace IdealFamily

open scoped BigOperators
open Finset

/- ********************  Core structures  ******************** -/

structure SetFamily (α : Type*) [DecidableEq α] where
  ground : Finset α
  sets   : Finset α → Prop
  inc_ground : ∀ {s : Finset α}, sets s → s ⊆ ground
  nonempty_ground : ground.Nonempty

attribute [simp] SetFamily.inc_ground
attribute [simp] SetFamily.nonempty_ground

namespace SetFamily

variable {α : Type*} [DecidableEq α]
variable (SF : SetFamily α)
variable [DecidablePred SF.sets]

/-- Carrier of a family: all subsets of `ground` that satisfy `sets`. -/
def carrier : Finset (Finset α) :=
  SF.ground.powerset.filter SF.sets

/-- Membership in the carrier is equivalent to being a subset of `ground`
    and satisfying the predicate. -/
lemma mem_carrier_iff {s : Finset α} :
  s ∈ SF.carrier ↔ s ⊆ SF.ground ∧ SF.sets s := by
  -- unfold carrier and analyze filter membership
  unfold carrier
  constructor
  · intro hs
    have hpf : s ∈ SF.ground.powerset := (Finset.mem_filter.mp hs).1
    have hset : SF.sets s := (Finset.mem_filter.mp hs).2
    -- from powerset membership we get the subset relation
    have hsub : s ⊆ SF.ground := (Finset.mem_powerset.mp hpf)
    exact And.intro hsub hset
  · intro h
    -- build filter membership from (subset, sets)
    have hpf : s ∈ SF.ground.powerset := (Finset.mem_powerset.mpr h.1)
    exact Finset.mem_filter.mpr ⟨hpf, h.2⟩

/-- The carrier is contained in the powerset of the ground. -/
lemma carrier_subset_powerset :
  SF.carrier ⊆ SF.ground.powerset := by
  intro s hs
  have : s ⊆ SF.ground ∧ SF.sets s := (SF.mem_carrier_iff).mp hs
  exact (Finset.mem_powerset.mpr this.1)

/- ********************  A/B/C partitions relative to a vertex  ******************** -/

variable (v : α)

/-- B-side at `v`: members **containing** `v`. -/
def S : Finset (Finset α) :=
  SF.carrier.filter (fun s => v ∈ s)

/-- A-side at `v`: members **not containing** `v`. -/
def delCarrier : Finset (Finset α) :=
  SF.carrier.filter (fun s => v ∉ s)

/-- C-side (contraction image): erase `v` on the B-side. -/
def contrCarrier : Finset (Finset α) :=
  (SF.S v).image (fun s => s.erase v)

/-- Convenience: the ground size as ℤ. -/
def groundZ : ℤ := (SF.ground.card : ℤ)

/- ********************  Basic numerics (Nat and ℤ)  ******************** -/

/-- Number of hyperedges (Nat). -/
def numEdgesNat : ℕ := (SF.carrier.card)

/-- Number of hyperedges (ℤ). -/
def numEdges : ℤ := (SF.numEdgesNat : ℤ)

/-- Total size (sum of set cardinalities) as Nat. -/
def totalSizeNat : ℕ := (SF.carrier.sum (fun s => s.card))

/-- Total size as ℤ. -/
def totalSize : ℤ := (SF.totalSizeNat : ℤ)

/-- Degree at `v` as Nat. -/
def degreeNat : α → ℕ := fun v => (SF.S v).card

/-- Degree at `v` as ℤ. -/
def degree : α → ℤ := fun v => (SF.degreeNat v : ℤ)

/-- Normalized degree at `v`: `2*deg(v) - |F|` over ℤ. -/
def normalizedDegreeAt (v : α) : ℤ :=
  (2 : ℤ) * (SF.degree v) - (SF.numEdges)

/-- Frankl-style NDS over ℤ: `2*totalSize - |F|*|U|`. -/
def nds : ℤ :=
  (2 : ℤ) * SF.totalSize - SF.numEdges * (SF.ground.card : ℤ)

/- ********************  Small API lemmas  ******************** -/

/-- By definition, `degreeNat v = |B|`. -/
lemma degreeNat_eq_cardS :
  SF.degreeNat v = (SF.S v).card := by
  rfl

/-- `degree v` is the ℤ-cast of `degreeNat v`. -/
lemma degree_eq_zcast_degreeNat :
  SF.degree v = (SF.degreeNat v : ℤ) := by
  rfl

/-- `numEdges` is the ℤ-cast of the carrier size. -/
lemma numEdges_eq_zcast_card :
  SF.numEdges = (SF.carrier.card : ℤ) := by
  rfl

/-- `totalSize` is the ℤ-cast of the sum over sizes on the carrier. -/
lemma totalSize_eq_zcast_sum_card :
  SF.totalSize = (((SF.carrier.sum (fun s => s.card)) : ℕ) : ℤ) := by
  rw [totalSize, totalSizeNat]

omit [DecidablePred SF.sets] in
/-- Ground size as ℤ is just the cast of its Nat size. -/
lemma groundZ_eq :
  SF.groundZ = (SF.ground.card : ℤ) := by
  rfl

end SetFamily

/- ********************  Ideals  ******************** -/

structure Ideal (α : Type*) [DecidableEq α] extends SetFamily α where
  has_empty : sets ∅
  has_ground : sets ground
  /- Downward closure below the top:
     for any `B ∈ F` with `B ≠ ground`, all `A ⊆ B` are also in `F`. -/
  down_closed :
    ∀ {A B : Finset α}, sets B → B ≠ ground → A ⊆ B → sets A

namespace Ideal

variable {α : Type*} [DecidableEq α]
variable (F : Ideal α)
variable [DecidablePred F.sets]

/- The `extends SetFamily` in the `Ideal` structure automatically provides
    the projection `toSetFamily : Ideal α → SetFamily α`, so no manual definition is needed. -/

omit [DecidablePred F.sets] in
@[simp] lemma toSetFamily_ground :
  (F.toSetFamily.ground) = F.ground := rfl

omit [DecidablePred F.sets] in
@[simp] lemma toSetFamily_sets :
  (F.toSetFamily.sets) = F.sets := rfl

omit [DecidablePred F.sets] in
/-- The ground is nonempty, hence its cardinal is positive. -/
lemma ground_card_pos : 0 < F.ground.card := by
  have hne : F.ground.Nonempty := F.nonempty_ground
  exact Finset.card_pos.mpr hne

/-- The empty set belongs to the carrier. -/
lemma empty_mem_carrier :
  ∅ ∈ (F.toSetFamily.carrier) := by
  classical
  -- ∅ ⊆ ground and sets ∅ (has_empty)
  have hsub : (∅ : Finset α) ⊆ F.ground := by
    intro x hx
    exact False.elim (Finset.notMem_empty x hx)
  have hset : F.sets ∅ := F.has_empty
  -- Build membership via `mem_carrier_iff`
  have := (SetFamily.mem_carrier_iff (SF := F.toSetFamily)).mpr (And.intro hsub hset)
  exact this

/-- The ground belongs to the carrier. -/
lemma ground_mem_carrier :
  F.ground ∈ (F.toSetFamily.carrier) := by
  classical
  have hsub : F.ground ⊆ F.ground := by
    intro x hx; exact hx
  have hset : F.sets F.ground := F.has_ground
  exact (SetFamily.mem_carrier_iff (SF := F.toSetFamily)).mpr (And.intro hsub hset)

end Ideal
end IdealFamily
