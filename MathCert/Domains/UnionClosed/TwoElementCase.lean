import MathCert.Domains.UnionClosed.FranklStatement

/-!
# Two-Element Member Case

Human theorem:
If a union-closed finite family contains `{a, b}`, then at least one of `a`
and `b` appears in at least half of the family.

Proof:
Partition the family according to whether a set contains neither element,
only `a`, only `b`, or both. Union with `{a, b}` injects the neither class
into the both class. The combined frequencies of `a` and `b` are therefore
at least the size of the family.
-/

namespace MathCert.UnionClosed

open Finset

variable {α : Type} [DecidableEq α]

/-- UC-WP04-L001: the two-element-member special case. -/
theorem two_element_case
    (F : Family α) (a b : α)
    (hUC : IsUnionClosed F)
    (hPair : ({a, b} : Finset α) ∈ F) :
    2 * freq F a ≥ F.card ∨ 2 * freq F b ≥ F.card := by
  let neither := F.filter (fun S => a ∉ S ∧ b ∉ S)
  let both := F.filter (fun S => a ∈ S ∧ b ∈ S)
  let onlyA := F.filter (fun S => a ∈ S ∧ b ∉ S)
  let onlyB := F.filter (fun S => a ∉ S ∧ b ∈ S)
  have hmap : ∀ S ∈ neither, S ∪ {a, b} ∈ both := by
    intro S hS
    simp only [neither, mem_filter] at hS
    simp only [both, mem_filter]
    exact ⟨hUC S hS.1 {a, b} hPair, by simp⟩
  have hinj : Set.InjOn (fun S : Finset α => S ∪ {a, b}) neither := by
    intro S hS T hT hEq
    change S ∈ neither at hS
    change T ∈ neither at hT
    simp only [neither, mem_filter] at hS hT
    apply Finset.ext
    intro x
    by_cases hxa : x = a
    · subst x
      simp [hS.2.1, hT.2.1]
    · by_cases hxb : x = b
      · subst x
        simp [hS.2.2, hT.2.2]
      · have := Finset.ext_iff.mp hEq x
        simpa [hxa, hxb] using this
  have hcard : neither.card ≤ both.card := by
    exact Finset.card_le_card_of_injOn (fun S => S ∪ {a, b}) hmap hinj
  have haSplit :
      both.card + onlyA.card = (F.filter (fun S => a ∈ S)).card := by
    simpa [both, onlyA, Finset.filter_filter, and_comm] using
      (Finset.card_filter_add_card_filter_not
        (s := F.filter (fun S => a ∈ S)) (fun S => b ∈ S))
  have hnaSplit :
      onlyB.card + neither.card = (F.filter (fun S => a ∉ S)).card := by
    simpa [onlyB, neither, Finset.filter_filter, and_comm] using
      (Finset.card_filter_add_card_filter_not
        (s := F.filter (fun S => a ∉ S)) (fun S => b ∈ S))
  have haPartition :
      (F.filter (fun S => a ∈ S)).card +
        (F.filter (fun S => a ∉ S)).card = F.card := by
    simpa using (Finset.card_filter_add_card_filter_not (s := F) (fun S => a ∈ S))
  have hbSplit :
      both.card + onlyB.card = (F.filter (fun S => b ∈ S)).card := by
    simpa [both, onlyB, Finset.filter_filter, and_comm] using
      (Finset.card_filter_add_card_filter_not
        (s := F.filter (fun S => b ∈ S)) (fun S => a ∈ S))
  change 2 * (F.filter (fun S => a ∈ S)).card ≥ F.card ∨
    2 * (F.filter (fun S => b ∈ S)).card ≥ F.card
  omega

end MathCert.UnionClosed
