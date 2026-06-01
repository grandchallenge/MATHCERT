import MathCert.Domains.UnionClosed.Basic
import Mathlib.Data.Finset.Powerset

/-!
# Union-Closed Families: Frequency Lemmas

Human statements:
An element lies in the support exactly when it lies in a family member.
For a nonempty union-closed family, the union of all members belongs to the family.
In a full powerset, each supported element appears in exactly half of the members.
-/

namespace MathCert.UnionClosed

open Finset

variable {α : Type} [DecidableEq α]

/-- UC-WP02-L001: support membership has the expected witness form. -/
theorem mem_support_iff (F : Family α) (x : α) :
    x ∈ support F ↔ ∃ S ∈ F, x ∈ S := by
  simp [support]

/-- UC-WP02-L005: nontriviality is equivalent to having a nonempty member. -/
theorem isNontrivial_iff_exists_nonempty (F : Family α) :
    IsNontrivial F ↔ ∃ S ∈ F, S.Nonempty := by
  simp only [IsNontrivial, Finset.Nonempty, mem_support_iff]
  aesop

/-- UC-WP02-L003: the union of a nonempty union-closed family belongs to it. -/
theorem support_mem_of_nonempty
    (F : Family α) (hF : F.Nonempty) (hUC : IsUnionClosed F) :
    support F ∈ F := by
  classical
  have subfamily_union_mem :
      ∀ S : Family α, S ⊆ F → S.Nonempty → support S ∈ F := by
    intro S
    induction S using Finset.induction_on with
    | empty =>
        simp
    | @insert A S hAS ih =>
        intro hSF hS
        by_cases hSEmpty : S.Nonempty
        · rw [support, Finset.biUnion_insert]
          exact hUC A (hSF (Finset.mem_insert_self A S))
            (support S) (ih (fun B hB => hSF (Finset.mem_insert_of_mem hB)) hSEmpty)
        · rw [Finset.not_nonempty_iff_eq_empty] at hSEmpty
          subst S
          simpa [support] using hSF (Finset.mem_insert_self A ∅)
  exact subfamily_union_mem F (fun _ h => h) hF

/-- UC-WP02-L004: a supported element belongs to exactly half of a powerset. -/
theorem freq_powerset (U : Finset α) (x : α) (hx : x ∈ U) :
    2 * freq U.powerset x = U.powerset.card := by
  classical
  have hfilter :
      U.powerset.filter (fun A => x ∈ A) =
        (U.erase x).powerset.image (insert x) := by
    ext A
    simp only [Finset.mem_filter, Finset.mem_powerset, Finset.mem_image]
    constructor
    · rintro ⟨hAU, hxA⟩
      refine ⟨A.erase x, ?_, ?_⟩
      · exact Finset.erase_subset_erase x hAU
      · exact Finset.insert_erase hxA
    · rintro ⟨B, hBU, rfl⟩
      exact ⟨Finset.insert_subset hx (hBU.trans (Finset.erase_subset x U)),
        Finset.mem_insert_self x B⟩
  rw [freq, hfilter, Finset.card_image_iff.mpr]
  · rw [Finset.card_powerset, Finset.card_powerset,
      ← Finset.card_erase_add_one hx, pow_succ]
    simp [Nat.mul_comm]
  · intro A hA B hB hEq
    exact Finset.insert_erase_invOn.2.injOn
      (Finset.notMem_mono (Finset.mem_powerset.mp hA) (Finset.notMem_erase x U))
      (Finset.notMem_mono (Finset.mem_powerset.mp hB) (Finset.notMem_erase x U)) hEq

end MathCert.UnionClosed
