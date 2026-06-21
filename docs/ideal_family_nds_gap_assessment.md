# Ideal-Family NDS Gap Assessment

Date: 2026-06-20

## Current Checked Boundary

The bridge now has a checked local conversion from MATHCERT finite families to
the ported predicate-style ideal-family structure.

Checked Lean theorems:

- `localIdealFamily_exists_rare`
- `localIdealFamily_averageRare_of_port_nds`
- `localIdealFamily_averageRare_of_port_nds_nonpos`
- `localIdealFamily_port_nds_nonpos`
- `localIdealFamily_averageRare`
- `sum_card_eq_sum_freq_on`
- `isAverageRareOn_iff_sum_freq_on`
- `everywhereRare_averageRare`
- `existsRare_not_sufficient_for_averageRare`
- `IdealFamily.SetFamily.sum_degreeNat_over_ground_eq_totalSizeNat`
- `IdealFamily.SetFamily.sum_degree_over_ground_eq_totalSize`
- `IdealFamily.SetFamily.sum_normalizedDegree_over_ground_eq_nds`
- `IdealFamily.Ideal.exists_rare_of_nds_le_zero`
- `IdealFamily.Ideal.nds_eq_zero_card_one`
- `IdealFamily.Ideal.degreeNat_eq_one_of_not_singleton`
- `IdealFamily.Ideal.trace_carrier_eq_del_union_contr`
- `IdealFamily.Ideal.trace_ground_card_lt`
- `IdealFamily.SetFamily.erase_injective_on_S`
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
- `complementFamilyOn_unionClosed_of_ideal`
- `complementFamilyOn_abundant_of_exists_rare`
- `complementFamilyOn_averageAbundant_of_averageRare`
- `localIdealFamily_complement_frankl`
- `localIdealFamily_complement_averageAbundant`

New checked file:

- `MathCert/Domains/UnionClosed/IdealFamilyNDS.lean`
- `MathCert/Domains/UnionClosed/IdealFamilyTrace.lean`
- `MathCert/Domains/UnionClosed/IdealFamilyContraction.lean`
- `MathCert/Domains/UnionClosed/IdealFamilyNDSDiff.lean`
- `MathCert/Domains/UnionClosed/IdealFamilyNDSEndgame.lean`
- `MathCert/Domains/UnionClosed/IdealFamilyDuality.lean`

## Former Gap Now Closed

The desired unconditional theorem is:

```lean
localIdealFamily_averageRare :
  IsIdealFamilyOn F U -> IsAverageRareOn F U
```

The bridge previously proved this only after receiving:

```lean
(toPortIdeal F U h).toSetFamily.nds <= 0
```

The 2026-06-20 endgame pass now proves that obligation locally.  The checked
proof adds the singleton contraction ideal, bounds the singleton trace
intersection block by the contraction NDS, and runs a strong induction on
ground cardinality.  The resulting theorem is:

```lean
theorem localIdealFamily_port_nds_nonpos
    {F : Family alpha} {U : Finset alpha}
    (h : IsIdealFamilyOn F U) :
    (toPortIdeal F U h).toSetFamily.nds <= 0
```

The unconditional `localIdealFamily_averageRare` theorem is now a checked
wrapper around `localIdealFamily_averageRare_of_port_nds_nonpos`.

## Why Rare Vertex Is Not Enough

The checked rare-vertex theorem gives:

```lean
exists x in U, 2 * freq F x <= F.card
```

Average rarity is stronger:

```lean
2 * (F.sum fun S => S.card) <= U.card * F.card
```

The new double-counting lemma rewrites this as:

```lean
2 * (U.sum fun x => freq F x) <= U.card * F.card
```

So average rarity controls the sum of all frequencies, not just one frequency.
The new Bool counterexample formally records that a single rare element does
not imply average rarity for arbitrary finite families.

## Next Formal Target

The local ideal-family average-rarity bridge and its complement-duality bridge
to union-closed abundance are now closed.  The next formal target should be
selected from the source roadmap rather than extending this branch ad hoc.

Do not promote the upstream NDS theorem until its active proof placeholders are
removed.  The local proof now supplies the MATHCERT theorem independently; the
upstream repository remains provenance for source comparison, not a trusted
dependency.
