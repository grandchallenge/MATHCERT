#!/usr/bin/env python3
from __future__ import annotations

import copy
import sys

import validate_openai_ten_proofs_route_registrations as historical
import validate_otp_j2_route_target_successor as j2
import validate_openai_ten_proofs_sphere_packing_route_registration as sphere
import validate_openai_ten_proofs_gapcvp_route_registration as gap

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

A_ROUTE_ID = "MC-ROUTE-OTP-A-SPHERE-PACKING"
A_PRE_REGISTRATION_PROVIDER_BASE = "aa06d3d81d20f5878b8a05ac6e5f1b9ce2ba2ddc"
H_ROUTE_ID = "MC-ROUTE-OTP-H-GAPCVP"
H_REGISTRATION_PROVIDER_BASE = "284e724d299bac02fc962b68e429b82398f6a08b"
H_PRE_REGISTRATION_PROVIDER_BASE = sphere.EXPECTED_PROPOSAL_MERGE

J2_HISTORICAL_BOUNDARY = "This registered route is limited to the exact Two-degenerate family targets and recorded current-revision theorem locus. It does not attribute the stronger coloring-side property to the source theorem, independently certify the construction beyond the encoded targets, compare the proof body in full, adjudicate or prove the theorem, issue a Cert output, or create an aggregate ten-proofs route."
J2_HISTORICAL_BLOCKERS = [
    "No MATHCERT adjudication has been authorized or recorded.",
    "The stronger coloring-side property remains excluded from source attribution.",
    "Whole-document manuscript equivalence and full proof-body comparison remain unestablished.",
]
J2_HISTORICAL_REOPENING = [
    "Update this route only through a separately authorized, exact-head reviewed MATHCERT adjudication or authority-repin operation."
]


def h_pre_registration_projection(routes: dict) -> dict:
    """Project only the independently validated H registration delta back to pre-H state."""
    projected = copy.deepcopy(routes)
    projected["routes"] = [
        row
        for row in projected.get("routes", [])
        if not (isinstance(row, dict) and row.get("route_id") == H_ROUTE_ID)
    ]
    if projected.get("provider_base_commit") == H_REGISTRATION_PROVIDER_BASE:
        projected["provider_base_commit"] = H_PRE_REGISTRATION_PROVIDER_BASE
    return projected


def a_pre_registration_projection(routes: dict) -> dict:
    """Project only the governed A registration delta back to the protected pre-registration registry.

    The live A registration is validated independently before this projection. Every
    non-A route and every unrelated registry field is preserved exactly as supplied.
    """
    projected = copy.deepcopy(routes)
    projected["routes"] = [
        row
        for row in projected.get("routes", [])
        if not (isinstance(row, dict) and row.get("route_id") == A_ROUTE_ID)
    ]
    if projected.get("provider_base_commit") == sphere.EXPECTED_PROPOSAL_MERGE:
        projected["provider_base_commit"] = A_PRE_REGISTRATION_PROVIDER_BASE
    return projected


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
        j2_predecessor_snapshot(j2_pre_output_projection(a_pre_registration_projection(h_pre_registration_projection(routes))))
    )


def sphere_validation_errors(projected: dict) -> list[str]:
    registration_blobs = {
        "routes": sphere.EXPECTED_OUTPUT_ROUTES_BLOB,
        "proposal": sphere.EXPECTED_PROPOSAL_BLOB,
        "proposal_registry": sphere.EXPECTED_PROPOSAL_REGISTRY_BLOB,
        "replay": sphere.EXPECTED_REPLAY_BLOB,
    }
    design_blobs = {
        "contract": sphere.EXPECTED_DESIGN_CONTRACT_BLOB,
        "registry": sphere.EXPECTED_DESIGN_REGISTRY_BLOB,
        "routes": sphere.EXPECTED_OUTPUT_ROUTES_BLOB,
        "registration_receipt": sphere.EXPECTED_REGISTRATION_RECEIPT_BLOB,
        "proposal": sphere.EXPECTED_PROPOSAL_BLOB,
        "proposal_registry": sphere.EXPECTED_PROPOSAL_REGISTRY_BLOB,
        "replay": sphere.EXPECTED_REPLAY_BLOB,
    }
    return sphere.validation_errors(
        routes=copy.deepcopy(projected),
        local_blobs=registration_blobs,
        design_blobs=design_blobs,
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
    errors: list[str] = []

    # Validate the live H registration before projecting it away for predecessor checks.
    errors.extend(gap.validation_errors(routes=copy.deepcopy(live)))
    pre_h = h_pre_registration_projection(live)

    # Validate the live A registration/output state on the exact pre-H projection.
    errors.extend(sphere_validation_errors(pre_h))

    pre_a = a_pre_registration_projection(pre_h)
    projected = j2_pre_output_projection(pre_a)

    errors.extend(j2.validation_errors(routes=copy.deepcopy(projected), check_files=False))

    live_j2 = j2.find_route(pre_a)
    if live_j2 is not None:
        if live_j2.get("target_claim_ids") == j2.NEW_TARGETS:
            errors.extend(j2.live_output_successor_errors(pre_a))
        else:
            errors.extend(j2.validation_errors(routes=copy.deepcopy(pre_a), check_files=False))

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
        # H is bound independently above; predecessor validators see only its exact projection.
        # J2's live semantics remain checked against the caller-preserving pre-A/pre-H state.
        errors.extend(j2.validation_errors(routes=j2.pre_output_routes(), check_files=True))
        errors.extend(j2.live_output_successor_errors(pre_a))
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"H-registration/A-registration/J2-successor-aware OTP route-registration validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print(
        "validated exact live submitted OTP-H-GAPCVP registration, projected only that H delta for predecessor checks, "
        "validated the exact live A registration/output successor, and preserved the J2 source-faithful output successor"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())