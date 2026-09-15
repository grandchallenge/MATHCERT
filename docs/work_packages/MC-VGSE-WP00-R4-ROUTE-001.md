# MC-VGSE-WP00-R4-ROUTE-001

## Purpose

Register `MC-ROUTE-VGSE-001-R4` as an additive restricted successor of `MC-ROUTE-VGSE-001` for exactly four already-adjudicated claims:

- `VGSE-C00`;
- `VGSE-C01`;
- `VGSE-C04`;
- `VGSE-C05`.

This route exists because the original five-claim route remains blocked on `VGSE-C06` while protected MATHCERT adjudication `df9fd2e493da277646e844d3e20fbc65e965d861` clears the other four claims.

## Human Steward control-plan disposition

MATHCERT issue #301, comment `5680762776`, authorizes Path B as an additive restricted successor route with identity `MC-ROUTE-VGSE-001-R4`.

The authorization requires the predecessor route to remain unchanged and keeps `VGSE-C06` fail-closed on that predecessor.

## Predecessor preservation

`MC-ROUTE-VGSE-001` remains the original five-claim route. Its protected overlay blob is `6dbd22485548114c91568dbc7ac18ac938e5f7e1` at protected MATHCERT commit `df9fd2e493da277646e844d3e20fbc65e965d861`.

Registration of this successor does not modify that overlay, remove C06, or create a partial-qualified state on the predecessor.

## Bound authority

The successor binds:

- protected four-claim adjudication blob `57668860de1c96370fb0075e0c7e8f43f7dc0067`;
- adjudication contract blob `2214eb6e442ac758c78ec5bc4b1de335c831cffa`;
- adjudication execution-input blob `6ed94cce042978c0373d3c72de0e5ba080cfe320`;
- exact algebraic/graph evidence blob `f804023ea346feea9bbcc7feecdc19b442f0448d`;
- planar evidence blob `4ec159d6c7786f4c576f0b5b8a6a1088bf054a7a`;
- protected C06 producer-binding blob `80ca458063ac2d500a2046f9594e90de0d737f86`;
- protected MATHFORGE source-package audit merge `7a7c1bcaba3c31726e34353f311a6de6d9530dbc`, whose provider record blob is `742a14910b5448d3fd9714434c7c5d0d3f7a61dc`.

## State

Registration uses the existing MATHCERT route vocabulary:

- `route_state = registered_pending_evidence`;
- `intake_status = pending`;
- `may_adjudicate = false`;
- `cert_output = null`.

The route already binds protected evidence and adjudication, but registration itself does not qualify the route or issue a certificate. Qualification and certificate publication are a separate protected output operation.

## C06 boundary

`VGSE-C06` is not a target of `MC-ROUTE-VGSE-001-R4`.

It remains `BLOCKED_VISIBLE_GEOMETRIC_WEIGHT_BRIDGE_TO_PINNED_C` on the predecessor route. The published arXiv v2 source package does not provide exact source graph/weight-generation material that satisfies its reopening condition.

Nothing in the R4 route broadens an equivalence relation or refutes the source paper.

## Downstream exclusions

This route does not establish rigid foldability, collision freedom, finite thickness, manufacturability, novelty, priority, publication merit, patentability, product performance, or commercial value.

Programme and INTELLECT routing remain unchanged unless a later separately governed operation explicitly changes them.
