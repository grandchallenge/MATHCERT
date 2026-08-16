#!/usr/bin/env python3
from __future__ import annotations

import copy
import sys

import validate_openai_ten_proofs_route_registrations as historical
import validate_otp_j2_route_target_successor as j2

REG = historical.REG
ROUTES = historical.ROUTES
PROPOSAL_REG = historical.PROPOSAL_REG
EXPECTED_FAMILIES = historical.EXPECTED_FAMILIES
EXPECTED_ROUTE_BLOB = historical.EXPECTED_ROUTE_BLOB
COMPACTNESS_HISTORICAL_BOUNDARY = historical.COMPACTNESS_HISTORICAL_BOUNDARY
COMPACTNESS_HISTORICAL_BLOCKERS = historical.COMPACTNESS_HISTORICAL_BLOCKERS
COMPACTNESS_HISTORICAL_REOPENING = historical.COMPACTNESS_HISTORICAL_REOPENING
blob = historical.blob
load = historical.load

J2_HISTORICAL_BOUNDARY = "This registered route is limited to the exact Two-degenerate family targets and recorded current-revision theorem locus. It does not attribute the stronger coloring-side property to the source theorem, independently certify the construction beyond the encoded targets, compare the proof body in full, adjudicate or prove the theorem, issue a Cert output, or create an aggregate ten-proofs route."
J2_HISTORICAL_BLOCKERS = [
    "No MATHCERT adjudication has been authorized or recorded.",
    "The stronger coloring-side property remains excluded from source attribution.",
    "Whole-document manuscript equivalence and full proof-body comparison remain unestablished.",
]
J2_HISTORICAL_REOPENING = [
    "Update this route only through a separately authorized, exact-head reviewed MATHCERT adjudication or authority-repin operation."
]


def j2_pre_output_projection(routes: dict) -> dict:
    """Project only J2's governed output delta back to its exact pre-output state.

    All caller-supplied mutations outside those J2 output-transition fields remain
    intact so historical and live mutation suites cannot be accidentally masked.
    """
    projected = copy.deepcopy(routes)
    live = j2.find_route(projected)
    if live is None:
        return projected
    before = j2.find_route(j2.pre_output_routes())
    if before is None:
        return projected

    # The live source-faithful target set identifies the governed successor lane.
    # Normalize only fields changed by the certificate/output route transition;
    # preserve every other field and every other route exactly as supplied.
    if live.get("target_claim_ids") == j2.NEW_TARGETS:
        for key in (
            "intake_status",
            "cert_output",
            "claim_boundary",
            "blockers",
            "reopening_conditions",
        ):
            live[key] = copy.deepcopy(before.get(key))
    return projected


def j2_predecessor_snapshot(routes: dict) -> dict:
    snapshot = copy.deepcopy(routes)
    route = j2.find_route(snapshot)
    if route is None:
        return snapshot
    if route.get("target_claim_ids") == j2.NEW_TARGETS:
        route["target_claim_ids"] = copy.deepcopy(j2.OLD_TARGETS)
        route["claim_boundary"] = J2_HISTORICAL_BOUNDARY
        route["blockers"] = copy.deepcopy(J2_HISTORICAL_BLOCKERS)
        route["reopening_conditions"] = copy.deepcopy(J2_HISTORICAL_REOPENING)
    return snapshot


def registration_snapshot(routes: dict) -> dict:
    return historical.registration_snapshot(
        j2_predecessor_snapshot(j2_pre_output_projection(routes))
    )


def validation_errors(
    receipt=None,
    routes=None,
    proposal_registry=None,
    proposal_blobs=None,
    routes_blob=None,
    proposal_registry_blob=None,
) -> list[str]:
    live = historical.load(historical.ROUTES) if routes is None else copy.deepcopy(routes)
    projected = j2_pre_output_projection(live)

    errors: list[str] = []

    # Preserve the immutable source-faithful route-target successor against the
    # supplied registry projected only across the later output transition.
    errors.extend(j2.validation_errors(routes=copy.deepcopy(projected), check_files=False))

    # Validate the supplied live J2 state independently. This catches state,
    # target, output-pointer, and boundary mutations without weakening the
    # historical route-target successor.
    live_j2 = j2.find_route(live)
    if live_j2 is not None:
        if live_j2.get("target_claim_ids") == j2.NEW_TARGETS:
            errors.extend(j2.live_output_successor_errors(live))
        else:
            # Mixed/old target substitutions belong to the successor validator.
            errors.extend(j2.validation_errors(routes=copy.deepcopy(live), check_files=False))

    # The historical registration validator already validates the authorized
    # Compactness successor before projecting it, and its registration_snapshot
    # preserves unrelated route additions/omissions/mutations. Feed it the
    # caller-preserving J2 pre-output projection, then map only the older J2
    # target successor back to the protected original registration identity.
    errors.extend(
        historical.validation_errors(
            receipt=receipt,
            routes=j2_predecessor_snapshot(projected),
            proposal_registry=proposal_registry,
            proposal_blobs=proposal_blobs,
            routes_blob=routes_blob,
            proposal_registry_blob=proposal_registry_blob,
        )
    )

    if routes is None:
        # Repository-level identity/ancestry checks remain binding on the real
        # current tree in addition to the pure supplied-object validations above.
        errors.extend(j2.validation_errors(routes=j2.pre_output_routes(), check_files=True))
        errors.extend(j2.live_output_successor_errors(live))
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"J2-successor-aware OTP route-registration validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print(
        "validated historical OTP route registration against caller-preserving J2 predecessor/pre-output "
        "projection and separately validated the exact live source-faithful restricted output successor"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
