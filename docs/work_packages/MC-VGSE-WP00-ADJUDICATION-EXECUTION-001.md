# MC-VGSE-WP00-ADJUDICATION-EXECUTION-001

## Purpose

This work package executes one bounded MATHCERT adjudication under protected contract `MC-VGSE-WP00-ADJUDICATION-CONTRACT-001`.

The adjudication scope is exactly:

1. `VGSE-C00`;
2. `VGSE-C01`;
3. `VGSE-C04`;
4. `VGSE-C05`.

`VGSE-C06` is excluded.

## Protected authority

The execution starts from protected MATHCERT merge `470e0f637b93577993925745bbb6b0bb422a4d27`.

The protected contract is:

- path: `governance/result_family_adjudication_contracts/VGSE-001.json`;
- blob: `2214eb6e442ac758c78ec5bc4b1de335c831cffa`.

The execution input binds the admitted exact algebraic/graph evidence, planar evidence, and protected C06 producer-binding record by Git blob identity.

The pinned MATHSOLVE handoff is `cert_handoffs/VGSE-001.json` at merge `1ebc9ace360e453fbc3707f6b23032b1c3c561eb`, blob `42cfa84978fd63c75f074b388afd8b1fcbd56091`. Its C00/C01/C04/C05 statements and support modalities match the adjudication target set exactly. Its fifth claim is C06, which remains excluded.

## Fresh replay requirement

The final publication head must freshly execute:

- `ci/replay_vgse_wp00_exact_evidence.py`;
- `ci/replay_vgse_wp00_planar_evidence.py`;
- `ci/replay_vgse_wp00_source_equivalence_audit.py`;
- the fail-closed VGSE route/design validator and mutation suite;
- the closed adjudication-input and adjudication schemas plus content-addressed identity checks.

The replay must reconfirm:

- C00 exact five-line bounded-region count;
- C01 saturated five-solution count, quotient dimension, squarefree/root-separation and divisor-exclusion conclusions;
- C04 exact positive graph-weight replay and common-scale Plucker match;
- C05 exact discrete-holomorphic and primitive closure plus interval-certified planar geometry;
- exact four-claim statement concordance;
- C06 exclusion and blocked state.

## Proposed disposition

The candidate disposition is:

`adjudication_clear_exact_four_claims_only`

It becomes binding only after the final exact head passes the required machine gates, receives a fresh binding non-author specialist `APPROVED` review on that exact head, is merged with an expected-head guard, and is read back from protected `main`.

## State boundary

This adjudication does not issue a certificate, transition the route, mark a mathematical target proved, or promote a claim.

It does not include `VGSE-C06`, infer or broaden an equivalence relation, refute the source paper, or authorize rigid foldability, collision freedom, finite thickness, manufacturability, novelty, priority, publication, patentability, product, performance, or commercial claims.

A Cert-output design or route/output transition is a later separately governed operation.

## Staffing policy

Protected `GI-STEWARD-0003` applies. Routine bounded progression under the unchanged control plan does not require a ceremonial Human Steward action. Human Steward intervention remains fail-closed if the control plan changes or another reserved-authority trigger is reached.
