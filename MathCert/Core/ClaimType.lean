namespace MathCert

/-- Claim classes used by the Grand Challenge claim ledger. -/
inductive ClaimType where
  | provedInPackage
  | formalized
  | computedExactly
  | intervalCertified
  | literatureDerived
  | heuristic
  | conjectural
  | failedAttempt
  | needsAudit
  | superseded
  | refuted
  deriving Repr, DecidableEq

end MathCert
