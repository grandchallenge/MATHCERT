#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "governance/result_family_output_contracts/OTP-J1-COMPACTNESS.json"
CONTRACT_SCHEMA = ROOT / "schemas/otp_compactness_output_contract.schema.json"
FUTURE_SCHEMA = ROOT / "schemas/otp_compactness_qualified_output.schema.json"
ROUTES = ROOT / "governance/certification_routes.json"
ADJUDICATION = ROOT / "governance/result_family_adjudications/OTP-J1-COMPACTNESS.json"
CONSTRUCTION = ROOT / "governance/result_family_construction_evidence/OTP-J1-COMPACTNESS.json"
FUTURE_CERTIFICATE = ROOT / "certificates/formal_sources/MC-OTP-J1-COMPACTNESS-001.json"
OUTPUT_CANDIDATE = ROOT / "governance/result_family_output_candidates/OTP-J1-COMPACTNESS.json"
STAGED_CERTIFICATE = ROOT / "governance/result_family_output_candidates/staged_certificates/MC-OTP-J1-COMPACTNESS-001.json"
STAGED_ROUTE = ROOT / "governance/result_family_output_candidates/staged_route_transitions/OTP-J1-COMPACTNESS.json"

EXPECTED_TARGETS = [
    "CompactnessConjecture.quantitativeCompactnessCounterexample",
    "CompactnessConjecture.compactnessCounterexample_bigO",
    "CompactnessConjecture.not_erdos_180",
]
EXPECTED_ADJUDICATION_BLOB = "175fb2d04c80de405655654d9024ffa6eb1f3b46"
EXPECTED_CONSTRUCTION_BLOB = "872cdf678412d63df22d1244b3b5c13185f29571"
EXPECTED_FUTURE_SCHEMA_BLOB = "1a96dc9e4e1fe0aabdf82067a829076ce25acff0"
EXPECTED_CONTRACT_FILES = {"OTP-F-EHRHART.json", "OTP-C-PERMANENT.json", "OTP-J1-COMPACTNESS.json"}
EXPECTED_SUCCESSOR_OUTPUT = {
    "repository": "grandchallenge/MATHCERT",
    "commit_sha": "9fba5a8e918028ecc2b4d72abc00b3b72a5194f5",
    "path": "certificates/formal_sources/MC-OTP-J1-COMPACTNESS-001.json",
    "digest_algorithm": "git_blob_sha1",
    "digest": "88531e28951854961e86eec0517356999a391759",
}
EXPECTED_PUBLICATION = {
    "mode": "certificate_content_commit_then_route_transition_commit",
    "route_transition": {"from": "submitted", "to": "qualified"},
    "certificate_insertion": "exactly_one",
    "certificate_content_commit_first": True,
    "route_transition_commit_must_descend_from_certificate_content_commit": True,
    "final_reviewed_head_must_descend_from_certificate_content_commit": True,
    "cert_output_commit_sha_must_equal_certificate_content_commit": True,
    "cert_output_digest_must_equal_certificate_blob": True,
    "certificate_must_not_name_its_own_containing_commit": True,
    "protected_merge_method": "merge",
    "squash_merge_prohibited": True,
    "rebase_merge_prohibited": True,
    "partial_state_on_protected_main_prohibited": True,
    "registry_blockers_must_be_rewritten_to_preserved_qualification_boundaries": True,
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(f"blob {len(payload)}\0".encode("ascii") + payload, usedforsecurity=False).hexdigest()


def validation_errors(*, contract=None, contract_schema=None, future_schema=None, routes=None,
                      adjudication=None, construction=None, adjudication_blob=None,
                      construction_blob=None, future_schema_blob=None,
                      future_certificate_present=None, candidate_present=None,
                      staged_certificate_present=None, staged_route_present=None,
                      contract_files=None) -> list[str]:
    errors: list[str] = []
    contract = load(CONTRACT) if contract is None else contract
    contract_schema = load(CONTRACT_SCHEMA) if contract_schema is None else contract_schema
    future_schema = load(FUTURE_SCHEMA) if future_schema is None else future_schema
    routes = load(ROUTES) if routes is None else routes
    adjudication = load(ADJUDICATION) if adjudication is None else adjudication
    construction = load(CONSTRUCTION) if construction is None else construction
    adjudication_blob = git_blob_sha1(ADJUDICATION) if adjudication_blob is None else adjudication_blob
    construction_blob = git_blob_sha1(CONSTRUCTION) if construction_blob is None else construction_blob
    future_schema_blob = git_blob_sha1(FUTURE_SCHEMA) if future_schema_blob is None else future_schema_blob
    future_certificate_present = FUTURE_CERTIFICATE.exists() if future_certificate_present is None else future_certificate_present
    candidate_present = OUTPUT_CANDIDATE.exists() if candidate_present is None else candidate_present
    staged_certificate_present = STAGED_CERTIFICATE.exists() if staged_certificate_present is None else staged_certificate_present
    staged_route_present = STAGED_ROUTE.exists() if staged_route_present is None else staged_route_present
    contract_files = {p.name for p in CONTRACT.parent.glob("*.json")} if contract_files is None else contract_files

    if contract_files != EXPECTED_CONTRACT_FILES:
        errors.append("output-contract membership drift")
    if contract_schema.get("const") != contract:
        errors.append("output-contract schema is not exact/closed")
    for error in Draft202012Validator(contract_schema).iter_errors(contract):
        errors.append(f"output-contract schema violation: {error.message}")
    if future_schema.get("additionalProperties") is not False:
        errors.append("future qualification schema must remain closed")
    if future_schema.get("$id") != "https://grandchallenge.ai/schemas/otp_compactness_qualified_output.schema.json":
        errors.append("future qualification schema identity drift")
    if future_schema_blob != EXPECTED_FUTURE_SCHEMA_BLOB:
        errors.append("future qualification schema blob drift")
    if adjudication_blob != EXPECTED_ADJUDICATION_BLOB:
        errors.append("protected adjudication-record blob drift")
    if construction_blob != EXPECTED_CONSTRUCTION_BLOB:
        errors.append("protected construction-evidence blob drift")

    if contract.get("implementation_authorization") != {"comment_id": 5304398601, "scope": "design_only_bounded_qualification_output_contract", "streamlined_workflow": True}:
        errors.append("Human Steward streamlined implementation authorization drift")
    authority = contract.get("protected_authority", {})
    adjudication_authority = authority.get("adjudication", {})
    if adjudication_authority.get("merge_commit") != "bbaecbde892d1373f50fa45cd75a1d2712652611": errors.append("adjudication merge drift")
    if adjudication_authority.get("record", {}).get("digest") != EXPECTED_ADJUDICATION_BLOB: errors.append("adjudication authority digest drift")
    if adjudication_authority.get("disposition") != "adjudication_clear_encoded_targets_only": errors.append("adjudication disposition drift")
    if adjudication_authority.get("exact_reviewed_head") != "d33b2848f837f9bb632b74fde0774f4424a7efbc": errors.append("reviewed adjudication head drift")
    if adjudication_authority.get("binding_review") != {"reviewer": "jimsteeg", "review_id": 4944779564, "state": "APPROVED"}: errors.append("binding adjudication review drift")
    construction_authority = authority.get("construction_evidence", {})
    if construction_authority.get("record_digest") != EXPECTED_CONSTRUCTION_BLOB: errors.append("construction authority digest drift")
    if construction_authority.get("current_source_sha256") != "ebc561ab5c53dbd240e17a8fdb6fffeb648591eca85dbfc7466f563638f8c566": errors.append("current source identity drift")
    if authority.get("control_plan") != {"conformance": "within_authorized_streamlined_design_plan", "control_plan_change_requested": False, "human_steward_intervention_required_only_for_control_plan_change": True, "routine_stage_progression_without_human_steward_intervention": True}:
        errors.append("streamlined control plan drift")

    if contract.get("contract_state") != "design_only": errors.append("output contract is not design-only")
    if contract.get("output_scope", {}).get("encoded_targets") != EXPECTED_TARGETS: errors.append("output target membership/order drift")
    if contract.get("qualification_semantics", {}).get("permitted_disposition") != "qualified_encoded_targets_only": errors.append("qualification disposition drift")
    future = contract.get("future_certificate", {})
    if future != {"certificate_id": "MC-OTP-J1-COMPACTNESS-QUAL-001", "path": "certificates/formal_sources/MC-OTP-J1-COMPACTNESS-001.json", "schema": {"path": "schemas/otp_compactness_qualified_output.schema.json", "digest_algorithm": "git_blob_sha1", "digest": EXPECTED_FUTURE_SCHEMA_BLOB}, "record_type": "otp_compactness_qualified_output", "disposition": "qualified_encoded_targets_only", "mathematical_target_proved": False}:
        errors.append("future certificate identity/semantics drift")
    if contract.get("publication_protocol") != EXPECTED_PUBLICATION: errors.append("publication protocol drift")
    gate = contract.get("execution_gate", {})
    for key in ("protected_contract_merge_and_blob_required", "exact_head_cert_checks_required", "exact_head_gcl_conformance_required", "linux_windows_output_validation_required", "codeql_no_new_alerts_required", "fresh_non_author_specialist_approval_required", "protected_merge_required", "protected_merge_method_must_preserve_ancestry", "head_change_requires_revalidation_and_reapproval", "human_steward_intervention_required_only_for_control_plan_change"):
        if gate.get(key) is not True: errors.append(f"execution gate disabled: {key}")
    if gate.get("separate_human_steward_authorization_required") is not False: errors.append("streamlined execution improperly requires a new Human Steward gate")
    if contract.get("state") != {"route_state": "submitted", "cert_output": None, "mathematical_target_proved": False, "may_issue_output": False, "may_promote_claim": False, "aggregate_output": False}:
        errors.append("design-only state drift/authority inflation")

    successor_flags = (future_certificate_present, candidate_present, staged_certificate_present, staged_route_present)
    successor_absent = not any(successor_flags)
    successor_complete = all(successor_flags)
    if not successor_absent and not successor_complete:
        errors.append("partial Compactness output successor state")

    route = next((r for r in routes.get("routes", []) if r.get("route_id") == "MC-ROUTE-OTP-J1-COMPACTNESS"), None)
    if route is None:
        errors.append("Compactness route missing")
    else:
        if route.get("target_claim_ids") != EXPECTED_TARGETS: errors.append("Compactness registered targets drift")
        if successor_absent:
            if route.get("intake_status") != "submitted": errors.append("Compactness route changed during design")
            if route.get("cert_output") is not None: errors.append("Compactness Cert output inserted during design")
        elif successor_complete:
            if route.get("intake_status") != "qualified": errors.append("complete Compactness successor route is not qualified")
            if route.get("cert_output") != EXPECTED_SUCCESSOR_OUTPUT: errors.append("complete Compactness successor output identity drift")

    if adjudication.get("encoded_targets") != EXPECTED_TARGETS: errors.append("protected adjudication target drift")
    if adjudication.get("decision", {}).get("disposition") != "adjudication_clear_encoded_targets_only": errors.append("protected adjudication decision drift")
    adjudication_state = adjudication.get("state", {})
    for key, value in {"route_state": "submitted", "cert_output": None, "mathematical_target_proved": False, "may_issue_output": False, "may_promote_claim": False, "aggregate_adjudication": False, "aggregate_output": False}.items():
        if adjudication_state.get(key) != value: errors.append(f"protected adjudication state drift: {key}")
    if construction.get("disposition", {}).get("evidence_disposition") != "CONSTRUCTION_EVIDENCE_COMPLETE_READY_TO_REQUEST_ADJUDICATION": errors.append("construction evidence disposition drift")

    props = future_schema.get("properties", {})
    if props.get("encoded_targets", {}).get("const") != EXPECTED_TARGETS: errors.append("future certificate target drift")
    if props.get("qualification", {}).get("const", {}).get("disposition") != "qualified_encoded_targets_only": errors.append("future certificate disposition drift")
    if props.get("state", {}).get("const", {}).get("mathematical_target_proved") is not False: errors.append("future certificate proof promotion")
    limitations = contract.get("preserved_limitations", {})
    for key in ("historical_compactness_formulations_admitted", "proof_body_compared_in_full", "unrestricted_source_theorem_proof_claim", "other_family_outputs_authorized", "aggregate_openai_ten_proofs_authority"):
        if limitations.get(key) is not False: errors.append(f"contract limitation inflated: {key}")
    if limitations.get("whole_document_byte_equivalence") != "not_established" or limitations.get("whole_document_semantic_equivalence") != "not_established": errors.append("whole-document equivalence inflated")
    boundary = str(contract.get("claim_boundary", "")).lower()
    for token in ("design-only", "does not issue a certificate", "submitted route", "historical", "proof body", "aggregate openai ten proofs", "squash", "rebase", "commercial claims"):
        if token not in boundary: errors.append(f"claim boundary missing token: {token}")
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"OTP-J1-COMPACTNESS output-contract validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print("validated historical design-only OTP-J1-COMPACTNESS output contract and its complete governed successor state")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
