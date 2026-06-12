import MathCert.Core.AlgebraicCertificate

/-!
# Gröbner certificate lane

The lane records the doctrine imported from recent Lean Gröbner work:

* formal Gröbner theory belongs in Lean/Mathlib;
* heavy symbolic computation may be delegated to an external CAS;
* the external result is untrusted until Lean checks the certificate-producing
  equality, membership, remainder, or Gröbner-basis statement.
-/

namespace MathCert.Algebraic

open MathCert

/-- MATHCERT's operational doctrine for Gröbner-backed algebraic claims. -/
def groebnerDoctrine : String :=
  "External CAS computation may suggest a Gröbner certificate; MATHCERT certifies only the Lean-checked replay."

/-- A reusable classifier for exact algebraic claims whose external output has not crossed the Lean boundary. -/
def requiresKernelReplay (boundary : AlgebraicTrustBoundary) : Bool :=
  !isCertifiedBoundary boundary

theorem external_certificate_requires_kernel_replay :
    requiresKernelReplay AlgebraicTrustBoundary.externalCertificateRecorded = true := by
  rfl

theorem integrated_theorem_does_not_require_kernel_replay :
    requiresKernelReplay AlgebraicTrustBoundary.integratedCheckedTheorem = false := by
  rfl

end MathCert.Algebraic
