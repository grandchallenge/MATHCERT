namespace MathCert

/-- Certification ladder levels. -/
inductive CertificateLevel where
  | level0_intake
  | level1_reproducibleExploration
  | level2_exactComputation
  | level3_formalStatement
  | level4_checkedLocalLemma
  | level5_checkedTheorem
  deriving Repr, DecidableEq, Ord

end MathCert
