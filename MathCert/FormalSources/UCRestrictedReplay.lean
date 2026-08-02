import MathCert.Domains.UnionClosed.SingletonCase
import MathCert.Domains.UnionClosed.TwoElementCase

/-!
# UC-001 restricted qualification replay

This module independently re-exports the two exact restricted Union-Closed
claims admitted by `MC-HANDOFF-UC-001`. It does not state or prove Frankl's
conjecture.
-/

namespace MathCert.FormalSources.UC

open Finset
open MathCert.UnionClosed

variable {α : Type} [DecidableEq α]

/-- Replay of `UC-WP02-L002`: the singleton-containing restricted case. -/
theorem singletonTarget
    (F : Family α) (a : α)
    (hUC : IsUnionClosed F)
    (hSing : ({a} : Finset α) ∈ F) :
    2 * freq F a ≥ F.card := by
  exact singleton_case_target F a hUC hSing

/-- Replay of `UC-WP04-L001`: the two-element-member restricted case. -/
theorem twoElementTarget
    (F : Family α) (a b : α)
    (hUC : IsUnionClosed F)
    (hPair : ({a, b} : Finset α) ∈ F) :
    2 * freq F a ≥ F.card ∨ 2 * freq F b ≥ F.card := by
  exact two_element_case F a b hUC hPair

#print axioms singletonTarget
#print axioms twoElementTarget

end MathCert.FormalSources.UC
