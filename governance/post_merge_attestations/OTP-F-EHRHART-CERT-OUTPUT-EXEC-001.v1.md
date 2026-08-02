# OTP-F-EHRHART restricted output execution post-merge attestation

## Protected closure receipt

This versioned attestation records the completed protected restricted-output execution implemented by MATHCERT PR #77.

- exact reviewed head: `5e1dfee97e952ca38cc9df1c3d3bf12895268378`
- protected merge commit: `1d5b1e6514787005ed75e363df7ea953dcd9391a`
- merged at: `2026-08-02T22:33:46Z`
- non-author specialist approval: review `4839871557` by `jimsteeg`, submitted `2026-08-02T22:33:24Z`
- Human Steward merge disposition: PR #77 comment `5160662599`, recorded before merge
- Cert checks: run `30769719257`, success
- GCL conformance: run `30769719470`, success
- OTP Ehrhart adjudication: run `30769719253`, success
- certificate-content commit: `24d99cbdcd6da33ae2404c0f6034d503498d9a4b`
- route-transition commit: `94f7e37abe56b9423396c3bc4b9da6c0d64aec51`
- protected certificate: `certificates/formal_sources/MC-OTP-F-EHRHART-001.json`
- protected certificate blob: `27a855c949b67e71372c7f0d6601d80125d33968`
- protected route-registry blob: `0487c3ebf702229741f16a544d68af25cf994e41`
- protected historical execution-candidate blob: `38d6eb4a483387d04c25bd9f6991c54af67bd9c5`

The binding disposition is `qualified_encoded_targets_only`.

It applies only to:

- `Ehrhart.Volume.ehrhart_volume_inequality_for_sets`
- `Ehrhart.SimplexVolume.exists_centeredBody_sharp`
- `Ehrhart.SimplexVolume.barycenter_centeredSimplex`
- `Ehrhart.SimplexVolume.normalizedVolume_centeredSimplex`
- the admitted centered-simplex sharpness witness

The historical pre-merge candidate remains immutable and retains its historical pending-publication language. The repository-owned successor closure record states that protected publication occurred and supersedes that candidate state.

The current OTP family state is:

- Ehrhart: `qualified`, one adjudication, one restricted Cert output
- Compactness: `submitted`, no adjudication, no Cert output
- Two-degenerate: `submitted`, no adjudication, no Cert output
- aggregate outputs: `0`
- mathematical targets marked proved: `0`

No equality-case classification, whole-document equivalence, full analytic-proof comparison, other-family qualification, aggregate ten-proofs authority, or novelty, priority, publication, patentability, product, or commercial claim is created.

## Verbatim Human Steward merge disposition

I, Human Steward, authorize protected merge of MATHCERT PR #77 at exact head:

`5e1dfee97e952ca38cc9df1c3d3bf12895268378`

I recognize the successful exact-head validation:

- Cert checks run `30769719257`;
- GCL conformance run `30769719470`;
- OTP Ehrhart adjudication run `30769719253`;

together with the binding non-author `APPROVED` review submitted against this exact head.

This disposition authorizes only the bounded operation `OTP-F-EHRHART-CERT-OUTPUT-EXEC-001` under MATHCERT issue #75.

The authorized protected publication consists of the ordered execution history:

1. certificate-content commit `24d99cbdcd6da33ae2404c0f6034d503498d9a4b`, creating `certificates/formal_sources/MC-OTP-F-EHRHART-001.json` with Git blob `27a855c949b67e71372c7f0d6601d80125d33968`; and
2. route-transition commit `94f7e37abe56b9423396c3bc4b9da6c0d64aec51`, changing exactly `MC-ROUTE-OTP-F-EHRHART` from `submitted` to `qualified` and inserting exactly one restricted `cert_output`.

I authorize the restricted disposition:

`qualified_encoded_targets_only`

The qualification is limited to the four encoded Ehrhart targets and the admitted centered-simplex sharpness witness already bound by the protected adjudication and output contract.

The following limitations remain binding:

- `mathematical_target_proved` remains `false`;
- no classification, uniqueness, or completeness claim is made for all equality cases;
- whole-document byte equivalence is not established;
- whole-document semantic equivalence is not established;
- the analytic proof bodies were not compared in full;
- no other OpenAI Ten Proofs result family is qualified;
- no aggregate ten-proofs certification or authority is created;
- protected Union-Closed qualification state remains unchanged;
- no mathematical truth, novelty, priority, publication, patentability, product, or commercial claim is authorized.

The successor-control repairs included in the exact head preserve historical route-registration, ratification, adjudication-design, and submitted-route snapshots while validating the separately governed qualified Ehrhart successor. They do not retrospectively alter or enlarge any earlier authority.

Protected merge must use the ordinary merge-commit method with expected head SHA:

`5e1dfee97e952ca38cc9df1c3d3bf12895268378`

Squash merge and rebase merge are prohibited because they would destroy the authorized ordered certificate-content and route-transition commit identities.

This authorization is valid only for exact head `5e1dfee97e952ca38cc9df1c3d3bf12895268378`. Any head change requires renewed exact-head CI validation, a fresh binding non-author review, and a new Human Steward merge disposition.
