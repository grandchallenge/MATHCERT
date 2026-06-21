# Ideal-Family Bridge Phase Closeout

Closeout status: complete for the bridge phase.

Workspace-local closeout date: 2026-06-19

NDS infrastructure update: 2026-06-20

NDS endgame update: 2026-06-20

## Scope Closed

This phase established a narrow, checked bridge from MATHCERT's local

```lean
Family alpha := Finset (Finset alpha)
```

representation to the ported predicate-style ideal-family surface.

The first bridge pass deliberately did not claim the unconditional
average-rarity theorem, because the audited upstream NDS theorem path contains
active proof placeholders and did not produce a clean external build
certificate.  The later local NDS endgame now supplies that theorem inside
MATHCERT without importing the upstream repository as a trusted dependency.

## Checked Lean Surface

Primary files:

- `MathCert/Domains/UnionClosed/IdealFamilyPort/Core.lean`
- `MathCert/Domains/UnionClosed/IdealFamilyPort/FranklRare.lean`
- `MathCert/Domains/UnionClosed/IdealFamilyPort.lean`
- `MathCert/Domains/UnionClosed/IdealFamilyBridge.lean`
- `MathCert/Domains/UnionClosed/IdealFamilyNDS.lean`
- `MathCert/Domains/UnionClosed/IdealFamilyTrace.lean`
- `MathCert/Domains/UnionClosed/IdealFamilyContraction.lean`
- `MathCert/Domains/UnionClosed/IdealFamilyNDSDiff.lean`
- `MathCert/Domains/UnionClosed/IdealFamilyNDSEndgame.lean`
- `MathCert/Domains/UnionClosed/IdealFamilyDuality.lean`

Checked bridge theorems:

- `toPortIdeal_carrier_eq`
- `toPortIdeal_degreeNat_eq_freq`
- `toPortIdeal_nds_eq`
- `localIdealFamily_averageRare_of_port_nds`
- `localIdealFamily_port_nds_nonpos`
- `localIdealFamily_averageRare`
- `localIdealFamily_exists_rare`
- `sum_card_eq_sum_freq_on`
- `isAverageRareOn_iff_sum_freq_on`
- `everywhereRare_averageRare`
- `existsRare_not_sufficient_for_averageRare`
- `complementFamilyOn_unionClosed_of_ideal`
- `complementFamilyOn_abundant_of_exists_rare`
- `complementFamilyOn_averageAbundant_of_averageRare`
- `localIdealFamily_complement_frankl`
- `localIdealFamily_complement_averageAbundant`

Checked NDS support theorems:

- `IdealFamily.SetFamily.sum_degreeNat_over_ground_eq_totalSizeNat`
- `IdealFamily.SetFamily.sum_degree_over_ground_eq_totalSize`
- `IdealFamily.SetFamily.sum_normalizedDegree_over_ground_eq_nds`
- `IdealFamily.Ideal.exists_rare_of_nds_le_zero`
- `IdealFamily.Ideal.nds_eq_zero_card_one`
- `IdealFamily.Ideal.degreeNat_eq_one_of_not_singleton`
- `MathCert.UnionClosed.localIdealFamily_averageRare_of_port_nds_nonpos`
- `IdealFamily.Ideal.trace_carrier_eq_del_union_contr`
- `IdealFamily.Ideal.trace_ground_card_lt`
- `IdealFamily.SetFamily.card_contr_eq_cardS`
- `IdealFamily.SetFamily.sum_card_contr_eq_sum_cardS_sub_one`
- `IdealFamily.Ideal.nds_diff_trace_as_normdeg`
- `IdealFamily.Ideal.S_eq_singleton_ground_of_degreeNat_eq_one`
- `IdealFamily.Ideal.nds_diff_deg1_groundErase_notin`
- `IdealFamily.Ideal.nds_diff_deg1_groundErase_in_nonpos`
- `IdealFamily.Ideal.contrIdeal`
- `IdealFamily.Ideal.contrIdeal_carrier_eq_contrCarrier`
- `IdealFamily.Ideal.inter_sum_le_contr_nds`
- `IdealFamily.Ideal.nds_diff_singleton_nonpos_of_contr_nds`
- `IdealFamily.Ideal.port_nds_nonpos`

## Audit And Ledger Artifacts

External audit:

- `MATHSOLVE/external_audits/frankl_lean/BUILD_AUDIT.md`

MATHCERT assessment and claim ledger:

- `MATHCERT/docs/ideal_family_nds_gap_assessment.md`
- `MATHCERT/claim_ledger_ideal_family_bridge.yaml`

## Verification Evidence

The full MATHCERT gate passed:

```powershell
.\ci\check_lean.ps1
```

This includes:

- `lake build`
- claim-ledger validation and rejection tests
- algebraic certificate validation and rejection tests
- exact certificate replay
- no-sorry scan

The build still emits pre-existing lattice linter warnings, but exits
successfully.

The 2026-06-20 endgame update was also checked with:

```powershell
lake build MathCert
lake build MathCert.Domains.UnionClosed.IdealFamilyNDSEndgame
```

Both commands completed successfully.  The same pre-existing lattice linter
warnings appear during aggregate builds.

## Closed Target

The singleton/contraction branch and final trace/contraction induction now
prove the explicit theorem:

```lean
theorem localIdealFamily_port_nds_nonpos
    {F : Family alpha} {U : Finset alpha}
    (h : IsIdealFamilyOn F U) :
    (toPortIdeal F U h).toSetFamily.nds <= 0
```

The originally requested `localIdealFamily_averageRare` theorem is now a
checked wrapper around `localIdealFamily_averageRare_of_port_nds_nonpos`.

## Closure Rule

The local ideal-family average-rarity bridge is closed.  Do not import the
upstream repository as a trusted dependency unless a newly audited upstream
commit is placeholder-free and reproducibly builds.  Further use of the
ideal-family result should proceed through local wrappers, such as complement
duality to union-closed abundance, or through the next source-roadmap target.
