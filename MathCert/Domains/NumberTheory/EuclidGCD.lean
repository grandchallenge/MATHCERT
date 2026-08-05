import Mathlib

namespace MathCert.NumberTheory

/-- A bounded certificate predicate for a positive greatest common divisor. -/
structure AcceptedGCDCertificate (a b d : Nat) : Prop where
  positive : 0 < d
  dvdLeft : d ∣ a
  dvdRight : d ∣ b
  greatest : ∀ k : Nat, k ∣ a → k ∣ b → k ∣ d

/-- Every accepted certificate reports the kernel-defined natural-number gcd. -/
theorem acceptedGCDCertificate_sound {a b d : Nat}
    (h : AcceptedGCDCertificate a b d) : d = Nat.gcd a b := by
  apply Nat.dvd_antisymm
  · exact Nat.dvd_gcd h.dvdLeft h.dvdRight
  · exact h.greatest (Nat.gcd a b) (Nat.gcd_dvd_left a b) (Nat.gcd_dvd_right a b)

/-- The exact Euclidean trace used by the end-to-end fixture. -/
theorem euclidTrace252105 :
    252 = 2 * 105 + 42 ∧
    105 = 2 * 42 + 21 ∧
    42 = 2 * 21 + 0 := by
  norm_num

/-- The exact integer Bézout witness used by the fixture. -/
theorem bezout252105 : (-2 : Int) * 252 + 5 * 105 = 21 := by
  norm_num

/-- Concrete kernel replay of the normalized gcd result. -/
theorem gcd252105 : Nat.gcd 252 105 = 21 := by
  norm_num

/-- The concrete fixture satisfies the admitted certificate predicate. -/
theorem accepted252105 : AcceptedGCDCertificate 252 105 21 := by
  refine ⟨by norm_num, by norm_num, by norm_num, ?_⟩
  intro k hk252 hk105
  have hkg : k ∣ Nat.gcd 252 105 := Nat.dvd_gcd hk252 hk105
  simpa [gcd252105] using hkg

/-- Soundness specializes to the concrete fixture. -/
theorem accepted252105_sound : 21 = Nat.gcd 252 105 :=
  acceptedGCDCertificate_sound accepted252105

#print axioms acceptedGCDCertificate_sound
#print axioms euclidTrace252105
#print axioms bezout252105
#print axioms gcd252105
#print axioms accepted252105
#print axioms accepted252105_sound

end MathCert.NumberTheory
