import Mathlib.Tactic

/-!
# Toy polynomial identity

This is a deliberately small checked local lemma used by the algebraic certificate
fixture. It demonstrates the intended boundary: the JSON artifact may record
external CAS provenance, but the certified fact is the Lean theorem below.
-/

namespace MathCert.Algebraic

/-- GB-DEMO-001: kernel-checked polynomial identity fixture. -/
theorem toy_square_identity (x y : ℚ) :
    (x + y) ^ 2 = x ^ 2 + 2 * x * y + y ^ 2 := by
  ring

end MathCert.Algebraic
