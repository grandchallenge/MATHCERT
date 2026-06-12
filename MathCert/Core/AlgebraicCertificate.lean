/-!
# Algebraic certificate metadata

This file contains the Lean-side vocabulary for MATHCERT's algebraic certificate
lane. It is intentionally lightweight: external computer algebra systems may
discover certificates, but the MATHCERT trust boundary remains a checked local
lemma or theorem in Lean.
-/

namespace MathCert

/-- Algebraic certificate forms that MATHCERT knows how to classify. -/
inductive AlgebraicCertificateKind where
  | polynomialIdentity
  | remainderVerification
  | groebnerBasis
  | idealMembership
  | idealNonmembership
  | idealEquality
  | radicalMembership
  | finiteTruncation
  | finiteToInfiniteBridge
  deriving Repr, DecidableEq

/-- External symbolic backends are provenance, not trusted proof kernels. -/
inductive AlgebraicBackend where
  | sageMath
  | sympy
  | singular
  | magma
  | custom
  deriving Repr, DecidableEq

/-- The trust boundary attached to an algebraic artifact. -/
inductive AlgebraicTrustBoundary where
  | externalOutputOnly
  | externalCertificateRecorded
  | replayedByIndependentScript
  | leanKernelChecked
  | integratedCheckedTheorem
  deriving Repr, DecidableEq, Ord

/-- Minimal metadata required to register an algebraic certificate in a claim ledger. -/
structure AlgebraicCertificateMetadata where
  claimId : String
  certificateId : String
  certificateKind : AlgebraicCertificateKind
  coefficientDomain : String
  variableUniverse : String
  monomialOrder : String
  backend : AlgebraicBackend
  externalOutputHash : String
  leanTheorem? : Option String
  trustBoundary : AlgebraicTrustBoundary
  deriving Repr

/--
A MATHCERT algebraic artifact crosses the certification boundary only when Lean's
kernel checks the relevant local lemma or an integrated theorem depending on it.
-/
def isCertifiedBoundary : AlgebraicTrustBoundary → Bool
  | .leanKernelChecked => true
  | .integratedCheckedTheorem => true
  | _ => false

theorem external_output_not_certified :
    isCertifiedBoundary AlgebraicTrustBoundary.externalOutputOnly = false := by
  rfl

theorem lean_kernel_checked_is_certified :
    isCertifiedBoundary AlgebraicTrustBoundary.leanKernelChecked = true := by
  rfl

end MathCert
