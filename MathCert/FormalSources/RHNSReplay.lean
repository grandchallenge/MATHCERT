import MathSolve.FormalConjectures.RiemannHypothesis
import MathSolve.FormalConjectures.NSCriticalIntegrability

/-!
# Independent MATHCERT replay of the RH and NS-CI target interfaces

These wrapper theorems force the MATHCERT kernel environment to elaborate the
exact MATHSOLVE declarations and their correspondence boundaries. They do not
prove either open mathematical target.
-/

namespace MathCert.FormalSources

namespace RH

/-- MATHCERT replay of the Programme-to-mathlib RH definitional concordance. -/
theorem targetConcordance :
    MathSolve.FormalConjectures.RH.ProgrammeRiemannHypothesis =
      _root_.RiemannHypothesis :=
  MathSolve.FormalConjectures.RH.programmeRiemannHypothesis_eq_mathlib

end RH

namespace NS

/-- MATHCERT replay of the exact NS-CI quantifier order and exponent carrier. -/
theorem targetInterface :
    MathSolve.FormalConjectures.NS.UniversalCriticalIntegrability =
      (∀ (viscosity : ℝ), 0 < viscosity →
        ∀ (u0 : MathSolve.FormalConjectures.NS.RapidlyDecreasingDatum)
          (u : MathSolve.FormalConjectures.NS.VelocityField),
          MathSolve.FormalConjectures.NS.IsUnforcedLerayHopfSolution viscosity u0 u →
            ∀ (T : ℝ), 0 < T →
              MathSolve.FormalConjectures.NS.MixedNormFiniteOnZeroT
                MathSolve.FormalConjectures.NS.criticalL4L6 T u) := by
  rfl

/-- MATHCERT replay that the recorded Clay bridge is one-way and unproved. -/
theorem bridgeInterface :
    MathSolve.FormalConjectures.NS.CriticalIntegrabilityImpliesClay =
      (MathSolve.FormalConjectures.NS.UniversalCriticalIntegrability →
        MathSolve.FormalConjectures.NS.PositiveClayWholeSpaceAlternative) := by
  rfl

end NS

#check RH.targetConcordance
#check NS.targetInterface
#check NS.bridgeInterface

#print axioms RH.targetConcordance
#print axioms NS.targetInterface
#print axioms NS.bridgeInterface

end MathCert.FormalSources
