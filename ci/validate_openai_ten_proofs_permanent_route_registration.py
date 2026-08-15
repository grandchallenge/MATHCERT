#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "governance/pre_route_candidates/OPENAI_TEN_PROOFS_PERMANENT_ROUTE_REGISTRATION.json"
ROUTES = ROOT / "governance/certification_routes.json"
PROPOSAL = ROOT / "governance/result_family_route_proposal_successors/OTP-C-PERMANENT.json"
PROPOSAL_REGISTRY = ROOT / "governance/pre_route_candidates/OPENAI_TEN_PROOFS_PERMANENT_ROUTE_PROPOSAL.json"
SCHEMA = ROOT / "schemas/openai_ten_proofs_permanent_route_registration.schema.json"

ROUTE_ID = "MC-ROUTE-OTP-C-PERMANENT-FORMULA"
EXPECTED_BEFORE_BLOB = "0487c3ebf702229741f16a544d68af25cf994e41"
EXPECTED_ROUTES_BLOB = "4b7f98414958999c8404e30a4a7c0a2a104578da"
EXPECTED_PROPOSAL_BLOB = "27eb80d2361a571fdebeec0e31faa69b6c307604"
EXPECTED_PROPOSAL_REGISTRY_BLOB = "6da927a836fee276323edc1e4e5e7fefe7669ba0"
EXPECTED_PROPOSAL_MERGE = "aa06d3d81d20f5878b8a05ac6e5f1b9ce2ba2ddc"
EXPECTED_PROPOSAL_HEAD = "7b527cac7fef0100a38763c110628b538c9bbe8f"
EXPECTED_TARGETS = [
    "PermanentFormulaLowerBound.permanent_divisionFree_formula_logarithmic_lower_bound",
    "PermanentFormulaLowerBound.permanent_rational_formula_logarithmic_lower_bound",
]
EXPECTED_SOURCE_MANIFEST = {
    "repository": "grandchallenge/MATHFORGE",
    "commit_sha": "60f6e06c957139447bf5943eed731941b22ac608",
    "path": "sources/OPENAI-TEN-PROOFS-001/semantic/OTP-C-PERMANENT/semantic_audit_record.json",
    "digest_algorithm": "git_blob_sha1",
    "digest": "3e04bd16bd8a91eaf9b6702de89fcdcc72f61099",
}
EXPECTED_PACKET = {
    "repository": "grandchallenge/MATHSOLVE",
    "commit_sha": "90f8a8544e546a603b34c9b27b2d6a4a68e06de8",
    "path": "work_packages/OPENAI_TEN_PROOFS_WP00/result_family_handoffs/OTP-C-PERMANENT.json",
    "digest_algorithm": "git_blob_sha1",
    "digest": "a993c530880021930a2b468e76235b91122ca854",
}
EXPECTED_PRIOR_OTP_ROUTES = {
    "MC-ROUTE-OTP-F-EHRHART",
    "MC-ROUTE-OTP-J1-COMPACTNESS",
    "MC-ROUTE-OTP-J2-TWO-DEGENERATE",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(f"blob {len(payload)}\0".encode("ascii") + payload, usedforsecurity=False).hexdigest()


def open_object_paths(schema: Any) -> list[str]:
    found: list[str] = []
    def walk(value: Any, path: str = "") -> None:
        if isinstance(value, dict):
            if value.get("type") == "object" and value.get("additionalProperties") is not False:
                found.append(path or "/")
            for key, child in value.items():
                walk(child, f"{path}/{key}")
        elif isinstance(value, list):
            for i, child in enumerate(value):
                walk(child, f"{path}/{i}")
    walk(schema)
    return found


def validation_errors(
    receipt: dict[str, Any] | None = None,
    routes: dict[str, Any] | None = None,
    local_blobs: dict[str, str] | None = None,
) -> list[str]:
    errors: list[str] = []
    receipt = load(RECEIPT) if receipt is None else receipt
    routes = load(ROUTES) if routes is None else routes
    schema = load(SCHEMA)

    if open_object_paths(schema):
        errors.append("registration schema contains open object")
    for error in sorted(Draft202012Validator(schema).iter_errors(receipt), key=lambda e: list(e.path)):
        errors.append(f"schema: {'/'.join(map(str, error.path))}: {error.message}")

    blobs = {
        "routes": git_blob_sha1(ROUTES),
        "proposal": git_blob_sha1(PROPOSAL),
        "proposal_registry": git_blob_sha1(PROPOSAL_REGISTRY),
    } if local_blobs is None else local_blobs
    if blobs.get("routes") != EXPECTED_ROUTES_BLOB:
        errors.append("registered route registry blob drift")
    if blobs.get("proposal") != EXPECTED_PROPOSAL_BLOB:
        errors.append("proposal record blob drift")
    if blobs.get("proposal_registry") != EXPECTED_PROPOSAL_REGISTRY_BLOB:
        errors.append("proposal registry blob drift")

    authority = receipt.get("authority", {})
    if authority.get("proposal_merge") != EXPECTED_PROPOSAL_MERGE:
        errors.append("proposal merge drift")
    if authority.get("proposal_reviewed_head") != EXPECTED_PROPOSAL_HEAD:
        errors.append("proposal head drift")
    if authority.get("proposal_review_id") != 4942263873 or authority.get("proposal_reviewer") != "jimsteeg":
        errors.append("proposal review drift")
    if authority.get("proposal_disposition_comment") != 5299722269:
        errors.append("proposal disposition drift")
    if authority.get("proposal_record", {}).get("digest") != EXPECTED_PROPOSAL_BLOB:
        errors.append("proposal record authority drift")
    if authority.get("proposal_registry", {}).get("digest") != EXPECTED_PROPOSAL_REGISTRY_BLOB:
        errors.append("proposal registry authority drift")
    if authority.get("registered_route_registry_before_blob") != EXPECTED_BEFORE_BLOB:
        errors.append("pre-registration route registry drift")
    if authority.get("registered_route_registry_candidate_blob") != EXPECTED_ROUTES_BLOB:
        errors.append("candidate route registry authority drift")

    if routes.get("provider_base_commit") != EXPECTED_PROPOSAL_MERGE:
        errors.append("provider base does not bind protected proposal merge")
    route_list = routes.get("routes", [])
    if not isinstance(route_list, list):
        return errors + ["routes must be a list"]
    route_ids = [r.get("route_id") for r in route_list if isinstance(r, dict)]
    if route_ids.count(ROUTE_ID) != 1:
        errors.append("Permanent route membership must be exactly one")
    if not EXPECTED_PRIOR_OTP_ROUTES.issubset(set(route_ids)):
        errors.append("prior OTP route membership drift")
    if "MC-ROUTE-OPENAI-TEN-PROOFS-001" in route_ids or "OPENAI-TEN-PROOFS-001" in route_ids:
        errors.append("aggregate route inserted")

    route = next((r for r in route_list if isinstance(r, dict) and r.get("route_id") == ROUTE_ID), {})
    if route.get("campaign_id") != "OTP-C-PERMANENT" or route.get("tracker_issue") != "https://github.com/grandchallenge/MATHCERT/issues/101":
        errors.append("Permanent route identity drift")
    if route.get("source_manifest") != EXPECTED_SOURCE_MANIFEST:
        errors.append("Permanent source authority drift")
    if route.get("intake_packet") != EXPECTED_PACKET:
        errors.append("Permanent Solve packet drift")
    if route.get("intake_status") != "submitted":
        errors.append("Permanent route must remain submitted/non-adjudicated")
    if route.get("target_claim_ids") != EXPECTED_TARGETS:
        errors.append("Permanent target drift")
    if route.get("cert_output") is not None:
        errors.append("Cert output inserted")
    blockers = route.get("blockers", [])
    if not isinstance(blockers, list) or not any("adjudication" in str(x).lower() for x in blockers):
        errors.append("adjudication blocker missing")
    claim = str(route.get("claim_boundary", ""))
    for token in ("does not adjudicate", "256/384", "total-leaf/vertex", "historical admitted-PDF", "aggregate"):
        if token not in claim:
            errors.append(f"Permanent route claim boundary missing {token}")

    registration = receipt.get("registration", {})
    if registration.get("target_claim_ids") != EXPECTED_TARGETS:
        errors.append("receipt target drift")
    if registration.get("route_status") != "submitted":
        errors.append("receipt route status drift")
    source_projection = registration.get("source_projection", {})
    expected_projection = {
        "coefficient_field": "complex",
        "dimension_threshold": 32,
        "log_base": 2,
        "division_free_variable_leaf_constant": 128,
        "rational_variable_leaf_constant": 192,
        "gate_bounds_in_route": False,
        "total_leaves_vertices_in_route": False,
        "historical_pdf_byte_equivalence": False,
    }
    if source_projection != expected_projection:
        errors.append("source projection drift")

    state = receipt.get("state", {})
    expected_state = {
        "registered_route_count_created_by_this_operation": 1,
        "submitted_route_count": 1,
        "adjudication_count": 0,
        "cert_output_count": 0,
        "mathematical_target_proved_count": 0,
        "aggregate_route_count": 0,
    }
    if state != expected_state:
        errors.append("registration state inflation")
    controls = receipt.get("route_controls", {})
    false_keys = (
        "may_adjudicate", "may_issue_cert_output", "may_mark_target_proved",
        "may_include_circuit_target", "may_include_gate_bounds",
        "may_include_total_size_consequences", "historical_pdf_equivalence_established",
        "may_promote_claim",
    )
    if controls.get("registration_scope") != "exact_one_permanent_formula_route":
        errors.append("registration scope drift")
    if any(controls.get(k) is not False for k in false_keys):
        errors.append("registration authority inflation")
    if controls.get("aggregate_route_prohibited") is not True:
        errors.append("aggregate route prohibition removed")
    if receipt.get("candidate_disposition") != "PERMANENT_FORMULA_CERT_ROUTE_REGISTERED__NO_ADJUDICATION_OR_OUTPUT_AUTHORITY":
        errors.append("candidate disposition drift")
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"Permanent route registration validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print("validated one registered submitted Permanent formula route with exact proposal/evidence authority and zero adjudication/output/proof authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
