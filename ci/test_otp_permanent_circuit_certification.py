#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import validate_otp_permanent_circuit_certification as V
import otp_permanent_circuit_execution_history as H
import otp_permanent_circuit_output_execution as O


def write_json(payload) -> Path:
    handle = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    with handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    return Path(handle.name)


def expect_output_fail(*, cert_mutate=None, route_mutate=None, label: str) -> None:
    cert = json.loads(O.CERT.read_text(encoding="utf-8"))
    route = json.loads(O.ROUTE.read_text(encoding="utf-8"))
    if cert_mutate is not None:
        cert_mutate(cert)
    if route_mutate is not None:
        route_mutate(route)
    cert_path = write_json(cert)
    route_path = write_json(route)
    old_cert, old_route = O.CERT, O.ROUTE
    try:
        O.CERT, O.ROUTE = cert_path, route_path
        if not O.validation_errors():
            raise AssertionError(f"mutation unexpectedly accepted: {label}")
    finally:
        O.CERT, O.ROUTE = old_cert, old_route
        cert_path.unlink(missing_ok=True)
        route_path.unlink(missing_ok=True)


def expect_receipt_fail(mutate, label: str) -> None:
    receipt = json.loads(H.RECEIPT.read_text(encoding="utf-8"))
    mutate(receipt)
    path = write_json(receipt)
    old = H.RECEIPT
    try:
        H.RECEIPT = path
        if not H.validation_errors():
            raise AssertionError(f"mutation unexpectedly accepted: {label}")
    finally:
        H.RECEIPT = old
        path.unlink(missing_ok=True)


def main() -> int:
    errors = V.validation_errors()
    if errors:
        raise AssertionError("current executed circuit output does not validate: " + "; ".join(errors))

    if not O.accepted_live_global_routes_blob(O.EXPECTED_GLOBAL_ROUTES_BLOB):
        raise AssertionError("historical circuit registry snapshot unexpectedly rejected")
    if not O.accepted_live_global_routes_blob(O.EXPECTED_A_REGISTRATION_GLOBAL_ROUTES_BLOB):
        raise AssertionError("exact A registration successor unexpectedly rejected")
    if O.accepted_live_global_routes_blob("0" * 40):
        raise AssertionError("unknown route-registry successor unexpectedly accepted")

    expect_output_fail(
        cert_mutate=lambda c: c["qualification"]["source_projection"].__setitem__("dimension_threshold", 65535),
        label="threshold drift",
    )
    expect_output_fail(
        cert_mutate=lambda c: c["qualification"]["source_projection"].__setitem__("finite_bound_denominator", 143),
        label="denominator drift",
    )
    expect_output_fail(
        cert_mutate=lambda c: c["qualification"]["source_projection"].__setitem__("division_allowed", True),
        label="division enabled",
    )
    expect_output_fail(
        cert_mutate=lambda c: c["encoded_targets"].pop(),
        label="asymptotic target omitted",
    )
    expect_output_fail(
        cert_mutate=lambda c: c["state"].__setitem__("mathematical_target_proved", True),
        label="proof promotion",
    )
    expect_output_fail(
        cert_mutate=lambda c: c["preserved_limitations"].__setitem__("formula_targets_in_scope", True),
        label="formula scope insertion",
    )
    expect_output_fail(
        route_mutate=lambda r: r["route"]["cert_output"].__setitem__("digest", "0" * 40),
        label="route certificate digest drift",
    )
    expect_output_fail(
        route_mutate=lambda r: r["route"].__setitem__("mathematical_target_proved", True),
        label="route proof promotion",
    )
    expect_receipt_fail(
        lambda r: r["candidate_authorization"].__setitem__("reviewed_candidate_head", "0" * 40),
        "candidate authorization drift",
    )
    expect_receipt_fail(
        lambda r: r["execution_ancestry"].__setitem__("route_transition_is_direct_child_of_certificate_commit", False),
        "direct-child assertion removal",
    )
    expect_receipt_fail(
        lambda r: r["publication_constraints"].__setitem__("squash_prohibited", False),
        "squash enabled",
    )

    print("OTP Permanent circuit executed-output adversarial mutations all rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
