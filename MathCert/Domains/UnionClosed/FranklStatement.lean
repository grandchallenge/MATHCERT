import MathCert.Domains.UnionClosed.Frequency

/-!
# Frankl's Union-Closed Sets Conjecture: Formal Statement Scaffold

Human statement:
Every finite nontrivial union-closed family contains an element that appears in at least half of the sets in the family.

Certification status:
Statement scaffold only. This file must not be described as a proof of Frankl's conjecture.
-/

namespace MathCert.UnionClosed

variable {α : Type} [DecidableEq α]

/-- A family is Frankl-abundant if some element appears in at least half its sets. -/
def IsFranklAbundant (F : Family α) : Prop :=
  ∃ x ∈ support F, 2 * freq F x ≥ F.card

/-- Frankl's conjecture over a type `α`, as a formal statement. -/
def FranklStatementFor (α : Type) [DecidableEq α] : Prop :=
  ∀ F : Family α, IsUnionClosed F → IsNontrivial F → IsFranklAbundant F

end MathCert.UnionClosed
