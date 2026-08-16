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
    return historical.registration_snapshot(j2_predecessor_snapshot(routes))


def validation_errors(
    receipt=None,
    routes=None,
    proposal_registry=None,
    proposal_blobs=None,
    routes_blob=None,
    proposal_registry_blob=None,
) -> list[str]:
    live = historical.load(historical.ROUTES) if routes is None else routes
    errors = j2.validation_errors(routes=copy.deepcopy(live), check_files=False)
    errors.extend(
        historical.validation_errors(
            receipt=receipt,
            routes=j2_predecessor_snapshot(live),
            proposal_registry=proposal_registry,
            proposal_blobs=proposal_blobs,
            routes_blob=routes_blob,
            proposal_registry_blob=proposal_registry_blob,
        )
    )
    if routes is None:
        errors.extend(j2.validation_errors())
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"J2-successor-aware OTP route-registration validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print(
        "validated historical OTP route registration against its predecessor J2 snapshot and separately "
        "validated the explicit source-faithful J2 live target successor"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
