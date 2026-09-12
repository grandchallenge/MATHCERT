#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "governance/pre_route_candidates/OPENAI_TEN_PROOFS_B2_SPHERICAL_CODES_ROUTE_REGISTRATION.json"
ROUTES = ROOT / "governance/certification_routes.json"
PROPOSAL = ROOT / "governance/result_family_route_proposal_successors/OTP-B2-SPHERICAL-CODES.json"
PROPOSAL_REGISTRY = ROOT / "governance/pre_route_candidates/OPENAI_TEN_PROOFS_B2_SPHERICAL_CODES_ROUTE_PROPOSAL.json"
INTAKE = ROOT / "governance/result_family_intake_successors/OTP-B2-SPHERICAL-CODES.json"
WORK_PACKAGE = ROOT / "governance/result_family_work_package_successors/OTP-B2-SPHERICAL-CODES-CERT-WP-001.json"
REPLAY = ROOT / "governance/result_family_replay_evidence_successors/OTP-B2-SPHERICAL-CODES.json"
READBACK = ROOT / "governance/result_family_replay_evidence_readbacks/OTP-H-B1-B2.json"
SCHEMA = ROOT / "schemas/openai_ten_proofs_spherical_codes_route_registration.schema.json"

ROUTE_ID = "MC-ROUTE-OTP-B2-SPHERICAL-CODES"
TARGETS = [
    "MetricCodes.Johnson.main_binary_theorem",
    "MetricCodes.Spherical.HigherHierarchy.main_general",
    "MetricCodes.Spherical.HigherHierarchy.strict_hierarchy",
    "MetricCodes.Spherical.HigherHierarchy.NumericalMaximum.eventually_kissingNumber_lt_published",
]
CLASSIFICATIONS = [
    "source_faithful_exact_projection",
    "source_faithful_structured_projection",
    "source_faithful_structured_projection",
    "formal_strengthening_entailing_source_asymptotic_numerical_statement",
]
EXPECTED_BLOBS = {
    "proposal": "12145d4936c040defe279b28586b68fc76930b7e",
    "proposal_registry": "ec47a6cf7f8eb7ca33f46805c4ecb908be48a1f9",
    "intake": "8b74bd90d703eb1903a0a7a84387867a5df7b4e3",
    "work_package": "50dc2c9c5bc8aad49f22414536102cef0e82ce20",
    "replay": "288193448eee80c041beef57059182e1abe2e33c",
    "readback": "fde8ed79681dce929916b524176b236960cac4f6",
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob(path: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), "hash-object", str(path)],
        check=True, capture_output=True, text=True,
    ).stdout.strip()


def validation_errors(*, receipt: dict[str, Any] | None = None, routes: dict[str, Any] | None = None, local_blobs: dict[str, str] | None = None) -> list[str]:
    receipt = load(RECEIPT) if receipt is None else receipt
    routes = load(ROUTES) if routes is None else routes
    schema = load(SCHEMA)
    errors = [f"schema: {e.message}" for e in Draft202012Validator(schema).iter_errors(receipt)]
    blobs = {
        "routes": git_blob(ROUTES), "proposal": git_blob(PROPOSAL),
        "proposal_registry": git_blob(PROPOSAL_REGISTRY), "intake": git_blob(INTAKE),
        "work_package": git_blob(WORK_PACKAGE), "replay": git_blob(REPLAY),
        "readback": git_blob(READBACK),
    }
    if local_blobs:
        blobs.update(local_blobs)
    authority = receipt.get("authority", {})
    for name, expected in EXPECTED_BLOBS.items():
        if blobs.get(name) != expected:
            errors.append(f"{name} protected blob drift")
    expected_authority = {
        "proposal_record_blob": EXPECTED_BLOBS["proposal"],
        "proposal_registry_blob": EXPECTED_BLOBS["proposal_registry"],
        "cert_intake_blob": EXPECTED_BLOBS["intake"],
        "cert_work_package_blob": EXPECTED_BLOBS["work_package"],
        "cert_replay_evidence_blob": EXPECTED_BLOBS["replay"],
        "cert_replay_readback_blob": EXPECTED_BLOBS["readback"],
    }
    for field, expected in expected_authority.items():
        if authority.get(field) != expected:
            errors.append(f"receipt {field} drift")
    route_rows = [row for row in routes.get("routes", []) if row.get("route_id") == ROUTE_ID]
    if len(route_rows) != 1:
        errors.append("B2 route must exist exactly once")
        return errors
    route = route_rows[0]
    if route.get("campaign_id") != "OTP-B2-SPHERICAL-CODES" or route.get("target_claim_ids") != TARGETS:
        errors.append("B2 route scope drift")
    if route.get("intake_status") not in {"submitted", "qualified"}:
        errors.append("B2 route status is neither submitted nor qualified successor")
    if route.get("intake_status") == "submitted":
        if route.get("cert_output") is not None:
            errors.append("submitted B2 route has output authority")
        if blobs["routes"] != authority.get("registered_route_registry_candidate_blob"):
            errors.append("submitted registry candidate blob drift")
    elif not isinstance(route.get("cert_output"), dict) or route["cert_output"].get("path") != "certificates/formal_sources/MC-OTP-B2-SPHERICAL-CODES-001.json":
        errors.append("qualified B2 successor has invalid certificate binding")
    proposal = load(PROPOSAL)
    if proposal.get("proposal_state") != "proposed_only" or proposal.get("target_scope", {}).get("lean_theorems") != TARGETS:
        errors.append("protected B2 proposal scope drift")
    if receipt.get("registration", {}).get("target_claim_ids") != TARGETS or receipt.get("registration", {}).get("classifications") != CLASSIFICATIONS:
        errors.append("registration target/classification drift")
    controls = receipt.get("route_controls", {})
    if any(controls.get(k) is not False for k in ["may_adjudicate", "may_issue_cert_output", "may_mark_target_proved", "may_promote_claim", "may_transfer_predecessor_surface_authority", "may_attribute_formal_strengthening_as_source_verbatim", "may_broaden_hierarchy_or_localization_domains"]):
        errors.append("registration authority inflation")
    if any(row.get("route_id") == "MC-ROUTE-OPENAI-TEN-PROOFS-001" for row in routes.get("routes", [])):
        errors.append("aggregate OTP route prohibited")
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("validated exact four-target B2 spherical-codes submitted route with zero adjudication/output authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
