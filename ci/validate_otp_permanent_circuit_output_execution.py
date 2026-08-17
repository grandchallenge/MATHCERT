#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
CERT = ROOT / "certificates/formal_sources/MC-OTP-C-PERMANENT-CIRCUIT-001.json"
SCHEMA = ROOT / "schemas/otp_permanent_circuit_qualified_output.schema.json"
ROUTE = ROOT / "governance/certification_route_overlays/OTP-C-PERMANENT-CIRCUIT.json"
GLOBAL_ROUTES = ROOT / "governance/certification_routes.json"
VARIABLE_CERT = ROOT / "certificates/formal_sources/MC-OTP-C-PERMANENT-001.json"
FULL_FORMULA_CERT = ROOT / "certificates/formal_sources/MC-OTP-C-PERMANENT-FULL-FORMULA-001.json"
FULL_FORMULA_ROUTE = ROOT / "governance/certification_route_overlays/OTP-C-PERMANENT-FULL-FORMULA.json"

EXPECTED_CERT_BLOB = "9d0eb4a83df73440b17cb6809ede5cdcc0a8e385"
EXPECTED_GLOBAL_ROUTES_BLOB = "2d17473b4731aa9d9c630b1e7777ad4bd794d993"
EXPECTED_VARIABLE_CERT_BLOB = "ad10c427270cb1c747ebcacbc5c37e4c1ed1df04"
EXPECTED_FULL_FORMULA_CERT_BLOB = "2940f551805794b96c7b0793bfe0d14e9fcd9954"
EXPECTED_FULL_FORMULA_ROUTE_BLOB = "3a208d3391514de74853f4ad182e26c74f631913"
TARGETS = [
    "PermanentRollout.permanent_circuit_loglog_lower_bound",
    "PermanentRollout.permanent_circuit_loglog_bigOmega",
    "PermanentRollout.permanent_complexity_ratio_tendsto_atTop",
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(data)}\0".encode("ascii") + data,
        usedforsecurity=False,
    ).hexdigest()


def head_blob(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    return subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", f"HEAD:{rel}"], text=True
    ).strip()


def validation_errors() -> list[str]:
    errors: list[str] = []

    for path, expected, label in (
        (GLOBAL_ROUTES, EXPECTED_GLOBAL_ROUTES_BLOB, "historical certification route registry"),
        (VARIABLE_CERT, EXPECTED_VARIABLE_CERT_BLOB, "historical variable-leaf certificate"),
        (FULL_FORMULA_CERT, EXPECTED_FULL_FORMULA_CERT_BLOB, "protected full-formula certificate"),
        (FULL_FORMULA_ROUTE, EXPECTED_FULL_FORMULA_ROUTE_BLOB, "protected full-formula route overlay"),
    ):
        try:
            if head_blob(path) != expected:
                errors.append(f"{label} mutated")
        except subprocess.CalledProcessError as exc:
            errors.append(f"cannot verify {label}: {exc}")

    route_overlay = load(ROUTE)
    route = route_overlay.get("route", {})
    if route_overlay.get("base_registry", {}).get("digest") != EXPECTED_GLOBAL_ROUTES_BLOB:
        errors.append("circuit route base registry substitution")
    if route.get("route_id") != "MC-ROUTE-OTP-C-PERMANENT-CIRCUIT":
        errors.append("circuit route identity drift")
    if route.get("target_claim_ids") != TARGETS:
        errors.append("circuit route target drift")
    if route.get("mathematical_target_proved") is not False or route.get("aggregate_output") is not False:
        errors.append("circuit route authority inflation")
    preserved = route_overlay.get("preserved_formula_authority", {})
    if preserved != {
        "variable_leaf_certificate_id": "MC-OTP-C-PERMANENT-QUAL-001",
        "variable_leaf_certificate_blob": EXPECTED_VARIABLE_CERT_BLOB,
        "full_formula_certificate_id": "MC-OTP-C-PERMANENT-FULL-FORMULA-QUAL-001",
        "full_formula_certificate_blob": EXPECTED_FULL_FORMULA_CERT_BLOB,
        "mutable": False,
    }:
        errors.append("formula authority preservation drift")

    if not CERT.exists():
        if route.get("intake_status") != "submitted" or route.get("cert_output") is not None:
            errors.append("route advanced before circuit certificate insertion")
        return errors

    schema = load(SCHEMA)
    data = load(CERT)
    if schema.get("additionalProperties") is not False:
        errors.append("circuit qualified-output schema must remain closed")
    errors.extend(
        f"circuit qualified-output schema violation: {error.message}"
        for error in Draft202012Validator(schema).iter_errors(data)
    )
    if blob(CERT) != EXPECTED_CERT_BLOB:
        errors.append("circuit certificate blob identity drift")

    if route.get("intake_status") == "submitted":
        if route.get("cert_output") is not None:
            errors.append("submitted circuit route has premature cert_output")
    elif route.get("intake_status") == "qualified":
        output = route.get("cert_output") or {}
        if output.get("repository") != "grandchallenge/MATHCERT":
            errors.append("qualified circuit route repository drift")
        if output.get("path") != "certificates/formal_sources/MC-OTP-C-PERMANENT-CIRCUIT-001.json":
            errors.append("qualified circuit route certificate path drift")
        if output.get("digest_algorithm") != "git_blob_sha1" or output.get("digest") != EXPECTED_CERT_BLOB:
            errors.append("qualified circuit route certificate digest drift")
        if not isinstance(output.get("commit_sha"), str) or len(output.get("commit_sha", "")) != 40:
            errors.append("qualified circuit route missing certificate content commit")
    else:
        errors.append("circuit route state outside submitted/qualified execution states")

    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"OTP Permanent circuit output execution validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    if CERT.exists():
        print("validated exact restricted OTP-C-PERMANENT-CIRCUIT output execution state")
    else:
        print("validated pre-insertion OTP-C-PERMANENT-CIRCUIT execution state")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
