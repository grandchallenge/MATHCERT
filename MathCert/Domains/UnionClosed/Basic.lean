import Mathlib.Data.Finset.Card
import Mathlib.Data.Finset.Filter
import Mathlib.Data.Finset.Union

/-!
# Union-Closed Families: Basic Definitions

Human statement:
A finite family of finite sets is union-closed if the union of any two members is again a member.

Certification status:
Definition scaffold. Proof-bearing lemmas should be added in later Work Packages.
-/

namespace MathCert.UnionClosed

open Finset

variable {α : Type} [DecidableEq α]

/-- A finite family of finite subsets of `α`. -/
abbrev Family (α : Type) [DecidableEq α] := Finset (Finset α)

/-- Union-closure for a finite family. -/
def IsUnionClosed (F : Family α) : Prop :=
  ∀ A ∈ F, ∀ B ∈ F, A ∪ B ∈ F

/-- Support of a finite family: all elements appearing in at least one member. -/
def support (F : Family α) : Finset α :=
  F.biUnion id

/-- A nontrivial family for Frankl purposes: nonempty support. -/
def IsNontrivial (F : Family α) : Prop :=
  (support F).Nonempty

/-- Frequency of an element in a finite family. -/
def freq (F : Family α) (x : α) : Nat :=
  (F.filter (fun A => x ∈ A)).card

end MathCert.UnionClosed
