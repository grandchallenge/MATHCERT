#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "governance/result_family_output_contracts/OTP-C-PERMANENT.json"
CONTRACT_SCHEMA = ROOT / "schemas/otp_permanent_output_contract.schema.json"
FUTURE_SCHEMA = ROOT / "schemas/otp_permanent_qualified_output.schema.json"
ROUTES = ROOT / "governance/certification_routes.json"
ADJUDICATION = ROOT / "governance/result_family_adjudications/OTP-C-PERMANENT.json"
FUTURE_CERTIFICATE = ROOT / "certificates/formal_sources/MC-OTP-C-PERMANENT-001.json"
OUTPUT_CANDIDATE = ROOT / "governance/result_family_output_candidates/OTP-C-PERMANENT.json"
STAGED_CERTIFICATE = ROOT / "governance/result_family_output_candidates/staged_certificates/MC-OTP-C-PERMANENT-001.json"
STAGED_ROUTE = ROOT / "governance/result_family_output_candidates/staged_route_transitions/OTP-C-PERMANENT.json"
EXPECTED_TARGETS = [
    "PermanentFormulaLowerBound.permanent_divisionFree_formula_logarithmic_lower_bound",
    "PermanentFormulaLowerBound.permanent_rational_formula_logarithmic_lower_bound",
]
EXPECTED_ADJUDICATION_BLOB = "233d3e92ceed6654e6f6759718adf32f1b6c5415"
EXPECTED_FUTURE_SCHEMA_BLOB = "b3a9f0a10861b44f2fac7ad9094f976041562d0d"
EXPECTED_CONTRACT_FILES = {"OTP-F-EHRHART.json", "OTP-C-PERMANENT.json"}
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
                      adjudication=None, adjudication_blob=None, future_schema_blob=None,
                      future_certificate_present=None, candidate_present=None,
                      staged_certificate_present=None, staged_route_present=None,
                      contract_files=None) -> list[str]:
    errors: list[str] = []
    contract = load(CONTRACT) if contract is None else contract
    contract_schema = load(CONTRACT_SCHEMA) if contract_schema is None else contract_schema
    future_schema = load(FUTURE_SCHEMA) if future_schema is None else future_schema
    routes = load(ROUTES) if routes is None else routes
    adjudication = load(ADJUDICATION) if adjudication is None else adjudication
    adjudication_blob = git_blob_sha1(ADJUDICATION) if adjudication_blob is None else adjudication_blob
    future_schema_blob = git_blob_sha1(FUTURE_SCHEMA) if future_schema_blob is None else future_schema_blob
    future_certificate_present = FUTURE_CERTIFICATE.exists() if future_certificate_present is None else future_certificate_present
    candidate_present = OUTPUT_CANDIDATE.exists() if candidate_present is None else candidate_present
    staged_certificate_present = STAGED_CERTIFICATE.exists() if staged_certificate_present is None else staged_certificate_present
    staged_route_present = STAGED_ROUTE.exists() if staged_route_present is None else staged_route_present
    contract_files = {p.name for p in CONTRACT.parent.glob("*.json")} if contract_files is None else contract_files

    if contract_files != EXPECTED_CONTRACT_FILES:
        errors.append("output-contract membership drift")
    if contract_schema.get("additionalProperties") is not False:
        errors.append("output-contract schema must remain closed")
    for error in Draft202012Validator(contract_schema).iter_errors(contract):
        errors.append(f"output-contract schema violation: {error.message}")
    if future_schema.get("additionalProperties") is not False:
        errors.append("future qualification schema must remain closed")
    if future_schema.get("$id") != "https://grandchallenge.ai/schemas/otp_permanent_qualified_output.schema.json":
        errors.append("future qualification schema identity drift")
    source_authority = future_schema.get("properties", {}).get("source_authority", {})
    if source_authority.get("additionalProperties") is not False:
        errors.append("future qualification source authority object open")
    output_contract_schema = source_authority.get("properties", {}).get("output_contract", {})
    if output_contract_schema.get("additionalProperties") is not False:
        errors.append("future qualification output-contract authority object open")
    if future_schema_blob != EXPECTED_FUTURE_SCHEMA_BLOB:
        errors.append("future qualification schema blob drift")
    if adjudication_blob != EXPECTED_ADJUDICATION_BLOB:
        errors.append("protected adjudication-record blob drift")

    authority = contract.get("protected_authority", {})
    if authority.get("adjudication") != {
        "merge_commit": "685faa7730b7147ba70ae0d0bb5fdd916b68c1a7",
        "record": {"path": "governance/result_family_adjudications/OTP-C-PERMANENT.json", "digest_algorithm": "git_blob_sha1", "digest": EXPECTED_ADJUDICATION_BLOB},
        "disposition": "adjudication_clear_encoded_targets_only",
        "exact_reviewed_head": "e1deff40163730d61b974a8fdbee1d15466a23b9",
        "binding_review": {"reviewer": "jimsteeg", "review_id": 4943110222, "state": "APPROVED"},
        "review_packet_comment_id": 5300816794,
        "closure_comment_id": 5301025261,
    }:
        errors.append("protected adjudication authority drift")
    if authority.get("control_plan") != {
        "conformance": "within_admitted_contract",
        "control_plan_change_requested": False,
        "human_steward_intervention_required_only_for_control_plan_change": True,
        "routine_stage_progression_without_human_steward_intervention": True,
    }:
        errors.append("Permanent streamlined control plan drift")
    if contract.get("contract_state") != "design_only":
        errors.append("output contract is not design-only")

    scope = contract.get("output_scope", {})
    if scope.get("encoded_targets") != EXPECTED_TARGETS:
        errors.append("output target membership or order drift")
    if scope.get("source_projection") != {
        "coefficient_field": "complex", "dimension_threshold": 32, "log_base": 2,
        "division_free_variable_leaf_constant": 128, "rational_variable_leaf_constant": 192,
        "formula_target_count": 2, "circuit_target_count": 0,
    }:
        errors.append("source projection drift or scope inflation")
    if contract.get("qualification_semantics", {}).get("permitted_disposition") != "qualified_encoded_targets_only":
        errors.append("permitted qualification disposition drift")

    future = contract.get("future_certificate", {})
    if future != {
        "certificate_id": "MC-OTP-C-PERMANENT-QUAL-001",
        "path": "certificates/formal_sources/MC-OTP-C-PERMANENT-001.json",
        "schema": {"path": "schemas/otp_permanent_qualified_output.schema.json", "digest_algorithm": "git_blob_sha1", "digest": EXPECTED_FUTURE_SCHEMA_BLOB},
        "record_type": "otp_permanent_qualified_output",
        "disposition": "qualified_encoded_targets_only",
        "mathematical_target_proved": False,
    }:
        errors.append("future certificate identity or semantics drift")
    if contract.get("publication_protocol") != EXPECTED_PUBLICATION:
        errors.append("publication protocol drift")

    candidate = contract.get("execution_candidate_requirements", {})
    if candidate.get("candidate_state") != "output_candidate_prepared_pending_execution":
        errors.append("execution candidate state drift")
    if candidate.get("protected_effect_before_execution") != "none":
        errors.append("execution candidate gains premature protected effect")

    gate = contract.get("execution_gate", {})
    for key in ("protected_contract_merge_and_blob_required", "exact_head_cert_checks_required",
                "exact_head_gcl_conformance_required", "linux_windows_output_validation_required",
                "codeql_no_new_alerts_required", "fresh_non_author_specialist_approval_required",
                "protected_merge_required", "protected_merge_method_must_preserve_ancestry",
                "head_change_requires_revalidation_and_reapproval",
                "human_steward_intervention_required_only_for_control_plan_change"):
        if gate.get(key) is not True:
            errors.append(f"execution gate disabled: {key}")
    if gate.get("separate_human_steward_authorization_required") is not False:
        errors.append("separate Human Steward authorization improperly introduced")

    if contract.get("state") != {
        "route_state": "submitted", "cert_output": None, "mathematical_target_proved": False,
        "may_issue_output": False, "may_promote_claim": False, "aggregate_output": False,
    }:
        errors.append("design-only state drift or authority inflation")

    route = next((r for r in routes.get("routes", []) if r.get("route_id") == "MC-ROUTE-OTP-C-PERMANENT-FORMULA"), None)
    if route is None:
        errors.append("Permanent route missing")
    else:
        if route.get("intake_status") != "submitted": errors.append("Permanent route changed before output execution")
        if route.get("cert_output") is not None: errors.append("Permanent Cert output inserted during design")
        if route.get("target_claim_ids") != EXPECTED_TARGETS: errors.append("Permanent registered targets drift")

    if adjudication.get("encoded_targets") != EXPECTED_TARGETS:
        errors.append("protected adjudication target drift")
    if adjudication.get("decision", {}).get("disposition") != "adjudication_clear_encoded_targets_only":
        errors.append("protected adjudication disposition mismatch")
    adjudication_state = adjudication.get("state", {})
    for key, value in {"route_state":"submitted", "cert_output":None, "mathematical_target_proved":False,
                       "may_issue_output":False, "may_promote_claim":False,
                       "aggregate_adjudication":False, "aggregate_output":False}.items():
        if adjudication_state.get(key) != value:
            errors.append(f"protected adjudication state drift: {key}")

    props = future_schema.get("properties", {})
    if props.get("encoded_targets", {}).get("const") != EXPECTED_TARGETS:
        errors.append("future certificate target drift")
    if props.get("qualification", {}).get("const", {}).get("disposition") != "qualified_encoded_targets_only":
        errors.append("future certificate disposition drift")
    if props.get("state", {}).get("const") != {"route_state":"qualified", "cert_output_inserted":True,
        "mathematical_target_proved":False, "may_promote_claim":False, "aggregate_output":False}:
        errors.append("future certificate state drift")
    limitations = props.get("preserved_limitations", {}).get("const", {})
    for key in ("circuit_targets_in_scope", "gate_bounds_in_scope", "total_size_consequences_in_scope",
                "unrestricted_source_theorem_proof_claim", "other_family_outputs_authorized",
                "aggregate_openai_ten_proofs_authority"):
        if limitations.get(key) is not False: errors.append(f"future certificate limitation inflated: {key}")
    if limitations.get("historical_pdf_byte_equivalence") != "not_established":
        errors.append("historical PDF equivalence inflated")

    if future_certificate_present:
        errors.append("future Cert output exists during design-only stage")
    if candidate_present or staged_certificate_present or staged_route_present:
        errors.append("Permanent output execution artifact exists during design-only stage")

    preserved = contract.get("preserved_limitations", {})
    for key in ("circuit_targets_in_scope", "gate_bounds_in_scope", "total_size_consequences_in_scope",
                "unrestricted_source_theorem_proof_claim", "other_family_outputs_authorized",
                "aggregate_openai_ten_proofs_authority"):
        if preserved.get(key) is not False: errors.append(f"contract limitation inflated: {key}")
    if preserved.get("historical_pdf_byte_equivalence") != "not_established":
        errors.append("contract historical PDF equivalence inflated")

    boundary = str(contract.get("claim_boundary", "")).lower()
    for token in ("design-only", "does not issue a certificate", "submitted route", "theorem 1.1",
                  "256/384", "historical admitted-pdf byte equivalence", "mathematical target proved",
                  "aggregate openai ten proofs", "squash", "rebase", "commercial claims"):
        if token not in boundary: errors.append(f"claim boundary missing token: {token}")
    return errors

def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"OTP-C-PERMANENT output-contract validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print("validated design-only OTP-C-PERMANENT output contract, exact two-target claim boundary, corrected non-self-referential publication protocol, and zero present output authority")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
