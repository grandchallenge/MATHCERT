#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import subprocess
import sys

import validate_otp_j2_output_execution as historical
import validate_openai_ten_proofs_sphere_packing_route_registration as sphere

A_ROUTE_ID = "MC-ROUTE-OTP-A-SPHERE-PACKING"
A_PROPOSAL_MERGE = "4b194b9632a9aa57fee21c3c054498d6b4a8ed57"
PRE_A_PROVIDER_BASE = "aa06d3d81d20f5878b8a05ac6e5f1b9ce2ba2ddc"
PRE_B1_QUALIFICATION = "e0c3905b8e5ca39612f46d90a522fd289c73f4ba"
B1_ROUTE_ID = "MC-ROUTE-OTP-B1-BINARY-CODES"


def project_b1_qualification(routes: dict) -> dict:
    """Remove only the later B1 qualification semantics from J2/A history."""
    raw = subprocess.check_output(
        ["git", "show", f"{PRE_B1_QUALIFICATION}:{historical.ROUTES_PATH}"],
        cwd=historical.ROOT, text=True,
    )
    predecessor = json.loads(raw)
    predecessor_b1 = next(
        route for route in predecessor.get("routes", [])
        if isinstance(route, dict) and route.get("route_id") == B1_ROUTE_ID
    )
    projected = copy.deepcopy(routes)
    projected["routes"] = [
        copy.deepcopy(predecessor_b1)
        if isinstance(route, dict) and route.get("route_id") == B1_ROUTE_ID
        else route
        for route in projected.get("routes", [])
    ]
    return projected


def project_a_registration(routes: dict) -> dict:
    projected = copy.deepcopy(routes)
    projected["routes"] = [
        route
        for route in projected.get("routes", [])
        if not (isinstance(route, dict) and route.get("route_id") == A_ROUTE_ID)
    ]
    if projected.get("provider_base_commit") == A_PROPOSAL_MERGE:
        projected["provider_base_commit"] = PRE_A_PROVIDER_BASE
    return projected


def validation_errors() -> list[str]:
    live_routes = historical.load(historical.ROUTES)
    pre_b1_routes = project_b1_qualification(live_routes)
    errors = list(sphere.validation_errors(routes=copy.deepcopy(pre_b1_routes)))

    try:
        historical.ensure_history()
        exact_post_j2 = historical.obj_json(historical.ROUTE, historical.ROUTES_PATH)
        history = historical.receipt()
    except RuntimeError as exc:
        return errors + [str(exc)]

    projected = project_a_registration(pre_b1_routes)
    if projected != exact_post_j2:
        errors.append("live registry differs from exact post-J2 snapshot by more than the governed A registration delta")
        return errors

    projected_history = copy.deepcopy(history)
    projected_history["routes_head"] = historical.EXPECTED["routes_after"]

    projected_blobs = {
        "record": historical.blob(historical.RECORD),
        "schema": historical.blob(historical.SCHEMA),
        "certificate": historical.blob(historical.CERT),
        "staged_certificate": historical.blob(historical.STAGED_CERT),
        "staged_route": historical.blob(historical.STAGED_ROUTE),
        "contract": historical.blob(historical.CONTRACT),
        "adjudication": historical.blob(historical.ADJUDICATION),
        "certificate_schema": historical.blob(historical.CERT_SCHEMA),
        "routes_after": historical.EXPECTED["routes_after"],
    }
    errors.extend(
        historical.validation_errors(
            routes=copy.deepcopy(exact_post_j2),
            history=projected_history,
            blobs=projected_blobs,
        )
    )
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"A-registration-aware J2 output execution failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print(
        "validated immutable J2 output execution against its exact post-transition registry snapshot "
        "plus exactly one separately governed submitted A registration successor"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
