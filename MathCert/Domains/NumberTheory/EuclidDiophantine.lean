import Mathlib.Data.Int.GCD
import Mathlib.Tactic

namespace MathCert.NumberTheory

/-- A signed two-variable linear Diophantine equation has an integer solution. -/
def LinearDiophantineSolvable (a b c : ℤ) : Prop :=
  ∃ x y : ℤ, a * x + b * y = c

/-- The integer gcd divides exactly the signed targets admitting a linear combination. -/
theorem linearDiophantine_iff_coeGcdDvd (a b c : ℤ) :
    LinearDiophantineSolvable a b c ↔ ((a.gcd b : ℕ) : ℤ) ∣ c := by
  constructor
  · rintro ⟨x, y, rfl⟩
    exact dvd_add
      (dvd_mul_of_dvd_left (Int.gcd_dvd_left a b) x)
      (dvd_mul_of_dvd_left (Int.gcd_dvd_right a b) y)
  · rintro ⟨k, rfl⟩
    refine ⟨a.gcdA b * k, a.gcdB b * k, ?_⟩
    calc
      a * (a.gcdA b * k) + b * (a.gcdB b * k)
          = (a * a.gcdA b + b * a.gcdB b) * k := by ring
      _ = ((a.gcd b : ℕ) : ℤ) * k := by rw [← Int.gcd_eq_gcd_ab]

/--
For a nonzero coefficient pair, solvability is equivalent to divisibility of
the absolute target by the normalized natural gcd. The nonzero hypothesis
preserves the admitted campaign statement and excludes the degenerate
zero-pair interpretation.
-/
theorem linearDiophantine_iff_gcdDvdNatAbs (a b c : ℤ)
    (_nonzero : a ≠ 0 ∨ b ≠ 0) :
    LinearDiophantineSolvable a b c ↔ a.gcd b ∣ c.natAbs := by
  simpa only [Int.natCast_dvd] using linearDiophantine_iff_coeGcdDvd a b c

/-- The positive fixture is witnessed by the scaled protected Bézout pair. -/
theorem diophantine25210584 :
    LinearDiophantineSolvable 252 105 84 := by
  exact ⟨-8, 20, by norm_num⟩

/-- The exact quotient-remainder obstruction retained by the negative fixture. -/
theorem obstruction25210520 :
    (20 : ℤ) = 0 * (21 : ℤ) + 20 ∧ 0 < (20 : ℤ) ∧ (20 : ℤ) < 21 := by
  norm_num

/-- No integer pair solves the negative fixture. -/
theorem noDiophantine25210520 :
    ¬ LinearDiophantineSolvable 252 105 20 := by
  intro h
  have hdiv : (252 : ℤ).gcd 105 ∣ (20 : ℤ).natAbs :=
    (linearDiophantine_iff_gcdDvdNatAbs 252 105 20 (by norm_num)).mp h
  norm_num at hdiv

/-- The zero target remains constructive for every signed coefficient pair. -/
theorem zeroTargetSolvable (a b : ℤ) :
    LinearDiophantineSolvable a b 0 := by
  exact ⟨0, 0, by ring⟩

#print axioms MathCert.NumberTheory.linearDiophantine_iff_coeGcdDvd
#print axioms MathCert.NumberTheory.linearDiophantine_iff_gcdDvdNatAbs
#print axioms MathCert.NumberTheory.diophantine25210584
#print axioms MathCert.NumberTheory.obstruction25210520
#print axioms MathCert.NumberTheory.noDiophantine25210520
#print axioms MathCert.NumberTheory.zeroTargetSolvable

end MathCert.NumberTheory
