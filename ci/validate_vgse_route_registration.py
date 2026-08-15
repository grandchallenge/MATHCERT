#!/usr/bin/env python3
"""Validate the bounded, pending VGSE certification route registration."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
RECORD_PATH = ROOT / "governance" / "certification_route_overlays" / "VGSE-001.json"
SCHEMA_PATH = ROOT / "schemas" / "vgse_route_registration.schema.json"
BASE_REGISTRY_PATH = ROOT / "governance" / "certification_routes.json"
DOC_PATH = ROOT / "docs" / "work_packages" / "MC-VGSE-WP00-ROUTE-001.md"

EXPECTED_BASE_BLOB = "4b7f98414958999c8404e30a4a7c0a2a104578da"
EXPECTED_ALGEBRAIC = ["VGSE-C00", "VGSE-C01"]
EXPECTED_PLANAR = ["VGSE-C04", "VGSE-C05", "VGSE-C06"]
EXPECTED_ALGEBRAIC_MODALITIES = {
    "EXACT_RATIONAL_CERTIFICATE",
    "COMPUTER_ALGEBRA_CERTIFICATE_WITH_REPLAY",
    "INTERVAL_ARITHMETIC_CERTIFICATE",
    "SPECIALIST_AUDIT_PENDING",
}
EXPECTED_PLANAR_MODALITIES = {
    "INTERVAL_ARITHMETIC_CERTIFICATE",
    "SEMANTIC_REPLAY",
    "SPECIALIST_AUDIT_PENDING",
}
PROHIBITED_TRUE_FIELDS = {
    "mathematical_target_proved",
    "mechanical_claim_authorized",
    "manufacturing_claim_authorized",
    "novelty_or_priority_claim_authorized",
    "patentability_claim_authorized",
    "product_or_commercial_claim_authorized",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload,
        usedforsecurity=False,
    ).hexdigest()


def validation_errors(
    record: dict[str, Any] | None = None,
    *,
    schema: dict[str, Any] | None = None,
    base_registry: dict[str, Any] | None = None,
    base_blob: str | None = None,
    documentation: str | None = None,
) -> list[str]:
    errors: list[str] = []
    if record is None:
        record = load_json(RECORD_PATH)
    if schema is None:
        schema = load_json(SCHEMA_PATH)
    if base_registry is None:
        base_registry = load_json(BASE_REGISTRY_PATH)
    if base_blob is None:
        base_blob = git_blob_sha1(BASE_REGISTRY_PATH)
    if documentation is None:
        documentation = DOC_PATH.read_text(encoding="utf-8") if DOC_PATH.exists() else ""

    validator = Draft202012Validator(schema)
    for error in sorted(validator.iter_errors(record), key=lambda item: list(item.path)):
        errors.append(f"schema: {error.json_path}: {error.message}")

    if base_blob != EXPECTED_BASE_BLOB:
        errors.append(f"base certification registry blob drift: {base_blob}")

    routes = base_registry.get("routes", [])
    route_ids = [str(item.get("route_id", "")) for item in routes if isinstance(item, dict)]
    campaign_ids = [str(item.get("campaign_id", "")) for item in routes if isinstance(item, dict)]
    if len(route_ids) != len(set(route_ids)):
        errors.append("base certification registry contains duplicate route IDs")
    if len(campaign_ids) != len(set(campaign_ids)):
        errors.append("base certification registry contains duplicate campaign IDs")
    if "MC-ROUTE-VGSE-001" in route_ids or "VGSE-001" in campaign_ids:
        errors.append("VGSE route must be additive and absent from the pinned historical base registry")

    lanes = record.get("lanes", {})
    algebraic = lanes.get("algebraic", {})
    planar = lanes.get("planar_geometry", {})
    algebraic_claims = algebraic.get("target_claim_ids", [])
    planar_claims = planar.get("target_claim_ids", [])
    if algebraic_claims != EXPECTED_ALGEBRAIC:
        errors.append("algebraic target set drift")
    if planar_claims != EXPECTED_PLANAR:
        errors.append("planar target set drift")
    if set(algebraic_claims) & set(planar_claims):
        errors.append("algebraic and planar target lanes overlap")
    if set(algebraic_claims) | set(planar_claims) != set(EXPECTED_ALGEBRAIC + EXPECTED_PLANAR):
        errors.append("registered target set is incomplete or inflated")
    if set(algebraic.get("requested_modalities", [])) != EXPECTED_ALGEBRAIC_MODALITIES:
        errors.append("algebraic modality set drift")
    if set(planar.get("requested_modalities", [])) != EXPECTED_PLANAR_MODALITIES:
        errors.append("planar modality set drift")

    if record.get("may_adjudicate") is not False:
        errors.append("pending route may not adjudicate")
    if record.get("cert_output") is not None:
        errors.append("pending route may not carry a certificate output")
    effect = record.get("activation_effect", {})
    if effect.get("mathcert_route_registered") is not True:
        errors.append("route registration effect missing")
    for field in (
        "mathcert_adjudication_authorized",
        "certificate_output_authorized",
        "programme_active_routing_changed",
    ):
        if effect.get(field) is not False:
            errors.append(f"premature activation effect: {field}")

    boundary = record.get("claim_boundary", {})
    if boundary.get("bounded_algebraic_and_planar_intake_only") is not True:
        errors.append("bounded intake boundary missing")
    for field in PROHIBITED_TRUE_FIELDS:
        if boundary.get(field) is not False:
            errors.append(f"prohibited claim authority: {field}")

    required_doc_phrases = (
        "registered pending route",
        "does not authorize adjudication",
        "does not issue a certificate",
        "does not activate Programme routing",
        "rigid foldability",
        "manufacturability",
        "commercial",
    )
    for phrase in required_doc_phrases:
        if phrase not in documentation:
            errors.append(f"documentation boundary missing: {phrase}")

    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"VGSE route registration failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print(
        "validated additive VGSE pending route, exact upstream identities, separated lanes, "
        "and closed adjudication, output, Programme-routing, and promotion boundaries"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
