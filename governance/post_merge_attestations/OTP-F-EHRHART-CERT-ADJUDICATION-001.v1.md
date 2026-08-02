# OTP-F-EHRHART adjudication post-merge attestation

## Protected closure receipt

This versioned attestation records the completed protected adjudication operation implemented by MATHCERT PR #65.

- exact reviewed head: `bbe171300a111761f7c92b4a289a07a2a4475f33`
- protected merge commit: `41a2d699204d73543a4ac4bd33b2865d3803c5d6`
- merged at: `2026-08-02T09:49:36Z`
- non-author specialist approval: review `4838000213` by `jimsteeg`, submitted `2026-08-02T09:46:12Z`
- Human Steward merge disposition: PR #65 comment `5156965080`, recorded before merge
- Cert checks: run `30742184194`, success
- GCL conformance: run `30742184403`, success
- OTP Ehrhart adjudication: run `30742184230`, success on Ubuntu 24.04 and Windows 2025
- protected adjudication record: `governance/result_family_adjudications/OTP-F-EHRHART.json`
- protected adjudication-record blob: `dcea25320169b9309ebf6c7f48249df9a312555f`

The binding disposition is `adjudication_clear_encoded_targets_only`.

It applies only to:

- `Ehrhart.Volume.ehrhart_volume_inequality_for_sets`
- `Ehrhart.SimplexVolume.exists_centeredBody_sharp`
- `Ehrhart.SimplexVolume.barycenter_centeredSimplex`
- `Ehrhart.SimplexVolume.normalizedVolume_centeredSimplex`
- the admitted centered-simplex sharpness witness

The route remains `submitted`. No Cert output is issued. No source theorem or mathematical target is marked proved. No equality-case classification, whole-document equivalence, full analytic-proof comparison, other-family adjudication, aggregate ten-proofs authority, or novelty, priority, publication, patentability, product, or commercial claim is created.

## Verbatim Human Steward merge disposition

I, Human Steward, record the protected merge disposition for MATHCERT PR #65 at exact head `bbe171300a111761f7c92b4a289a07a2a4475f33`.

I recognize the non-author specialist `APPROVED` review submitted by `jimsteeg` on August 2, 2026, together with the successful exact-head validation:

- Cert checks run `30742184194`;
- GCL conformance run `30742184403`;
- OTP Ehrhart adjudication run `30742184230`, including Ubuntu 24.04 and Windows 2025.

I authorize protected merge of that exact head.

This disposition adopts only:

`adjudication_clear_encoded_targets_only`

for the four exact encoded OTP-F-EHRHART targets and the admitted centered-simplex sharpness witness under `MC-OTP-ADJUDICATION-CONTRACT-F-EHRHART`.

This disposition does not:

- classify or establish uniqueness of all equality cases;
- establish whole-document byte or semantic equivalence;
- claim that the analytic proof body was compared in full;
- issue a Cert output;
- mark the source theorem or any mathematical target proved;
- adjudicate Compactness, Two-degenerate, or any other result family;
- repair Permanent, GapCVP, or the `All.lean` namespace collision;
- create aggregate ten-proofs authority; or
- authorize novelty, priority, publication, patentability, product, or commercial claims.

This authorization is valid only for exact head `bbe171300a111761f7c92b4a289a07a2a4475f33`. Any head change requires renewed exact-head validation, non-author specialist review, and Human Steward merge disposition.
