import MathCert.Domains.UnionClosed.FranklStatement

/-!
# Singleton Case Target

Human theorem target:
If a union-closed finite family contains the singleton `{a}`, then `a` appears in at least half of the family.

Proof idea:
Map every set not containing `a` to its union with `{a}`. The map is injective and lands in the sets containing `a`.

Certification status:
UC-WP02-L002 checked lemma.
-/

namespace MathCert.UnionClosed

open Finset

variable {α : Type} [DecidableEq α]

/-- UC-WP02-L002: a singleton member pairs every set not containing `a`
with a distinct family member that contains `a`. -/
theorem singleton_case_target
    (F : Family α) (a : α)
    (hUC : IsUnionClosed F)
    (hSing : ({a} : Finset α) ∈ F) :
    2 * freq F a ≥ F.card := by
  let withoutA := F.filter (fun S => a ∉ S)
  let withA := F.filter (fun S => a ∈ S)
  have hmap : ∀ S ∈ withoutA, S ∪ {a} ∈ withA := by
    intro S hS
    simp only [withoutA, mem_filter] at hS
    simp only [withA, mem_filter, mem_union, mem_singleton]
    exact ⟨hUC S hS.1 {a} hSing, by simp⟩
  have hinj : Set.InjOn (fun S : Finset α => S ∪ {a}) withoutA := by
    intro S hS T hT hEq
    change S ∈ withoutA at hS
    change T ∈ withoutA at hT
    simp only [withoutA, mem_filter] at hS hT
    apply Finset.ext
    intro x
    by_cases hxa : x = a
    · subst x
      simp [hS.2, hT.2]
    · have := Finset.ext_iff.mp hEq x
      simpa [hxa] using this
  have hcard : withoutA.card ≤ withA.card := by
    exact Finset.card_le_card_of_injOn (fun S => S ∪ {a}) hmap hinj
  have hpartition : withoutA.card + withA.card = F.card := by
    simpa [withoutA, withA, Nat.add_comm] using
      (Finset.card_filter_add_card_filter_not (s := F) (fun S => a ∈ S))
  have hfreq : withA.card = freq F a := by
    rfl
  omega

/-- UC-WP02-L006: the singleton case produces a Frankl-abundance witness. -/
theorem singleton_case_abundant
    (F : Family α) (a : α)
    (hUC : IsUnionClosed F)
    (hSing : ({a} : Finset α) ∈ F) :
    IsFranklAbundant F := by
  refine ⟨a, (mem_support_iff F a).mpr ?_, singleton_case_target F a hUC hSing⟩
  exact ⟨{a}, hSing, by simp⟩

end MathCert.UnionClosed
