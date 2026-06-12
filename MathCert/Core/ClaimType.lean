namespace MathCert

/-- Claim classes used by the Grand Challenge claim ledger. -/
inductive ClaimType where
  | provedInPackage
  | formalized
  | computedExactly
  | algebraicCertified
  | intervalCertified
  | satSmtCertified
  | literatureDerived
  | heuristic
  | conjectural
  | failedAttempt
  | needsAudit
  | superseded
  | refuted
  deriving Repr, DecidableEq

end MathCert
