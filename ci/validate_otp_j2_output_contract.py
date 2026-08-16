#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "governance/result_family_output_contracts/OTP-J2-TWO-DEGENERATE.json"
CONTRACT_SCHEMA = ROOT / "schemas/otp_j2_source_faithful_output_contract.schema.json"
FUTURE_SCHEMA = ROOT / "schemas/otp_j2_source_faithful_qualified_output.schema.json"
ROUTES = ROOT / "governance/certification_routes.json"
ADJUDICATION = ROOT / "governance/result_family_adjudications/OTP-J2-TWO-DEGENERATE.json"
FUTURE_CERTIFICATE = ROOT / "certificates/formal_sources/MC-OTP-J2-TWO-DEGENERATE-001.json"
OUTPUT_CANDIDATE = ROOT / "governance/result_family_output_candidates/OTP-J2-TWO-DEGENERATE.json"
STAGED_CERTIFICATE = ROOT / "governance/result_family_output_candidates/staged_certificates/MC-OTP-J2-TWO-DEGENERATE-001.json"
STAGED_ROUTE = ROOT / "governance/result_family_output_candidates/staged_route_transitions/OTP-J2-TWO-DEGENERATE.json"

EXPECTED_TARGETS = [
    "TwoDegenerateGraphs.mathcert_sourceFaithfulTwoDegenerateExtremalCounterexample",
    "TwoDegenerateGraphs.mathcert_sourceFaithfulNotErdos146",
]
EXPECTED_HISTORICAL_TARGETS = [
    "TwoDegenerateGraphs.twoDegenerateExtremalCounterexample",
    "TwoDegenerateGraphs.not_erdos_146",
]
EXPECTED_ADJUDICATION_BLOB = "87286722951770b3383de2eedba30f2b53e0dabc"
EXPECTED_FUTURE_SCHEMA_BLOB = "94656e2aaf651ce2cfc56574929b13a28ce50cd2"
EXPECTED_CONTRACT_FILES = {
    "OTP-F-EHRHART.json",
    "OTP-C-PERMANENT.json",
    "OTP-J1-COMPACTNESS.json",
    "OTP-J2-TWO-DEGENERATE.json",
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
    "route_first_ordering_prohibited": True,
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
    if contract_schema.get("const") != contract:
        errors.append("J2 output-contract schema is not exact/closed")
    for error in Draft202012Validator(contract_schema).iter_errors(contract):
        errors.append(f"J2 output-contract schema violation: {error.message}")
    if future_schema.get("additionalProperties") is not False:
        errors.append("future J2 qualification schema must remain closed")
    if future_schema.get("$id") != "https://grandchallenge.ai/schemas/otp_j2_source_faithful_qualified_output.schema.json":
        errors.append("future J2 qualification schema identity drift")
    if future_schema_blob != EXPECTED_FUTURE_SCHEMA_BLOB:
        errors.append("future J2 qualification schema blob drift")
    if adjudication_blob != EXPECTED_ADJUDICATION_BLOB:
        errors.append("protected J2 adjudication-record blob drift")

    if contract.get("implementation_authorization") != {
        "comment_id": 5306277121,
        "disposition": "AUTHORIZE_J2_SOURCE_FAITHFUL_CERT_OUTPUT_CONTROL_PLAN",
        "scope": "design_only_source_faithful_restricted_qualification_output_contract",
        "streamlined_downstream_execution": True,
    }:
        errors.append("Human Steward J2 output-plan authorization drift")

    authority = contract.get("protected_authority", {})
    if authority.get("adjudication") != {
        "merge_commit": "60c8aef1ce29373e879fedc549219f459f32a608",
        "record": {"path": "governance/result_family_adjudications/OTP-J2-TWO-DEGENERATE.json", "digest_algorithm": "git_blob_sha1", "digest": EXPECTED_ADJUDICATION_BLOB},
        "disposition": "adjudication_clear_source_faithful_targets_only",
        "exact_reviewed_head": "6c6d357f7c48cc34c3536ec3a780efbd5fdfa404",
        "binding_review": {"reviewer": "jimsteeg", "review_id": 4945615812, "state": "APPROVED"},
        "review_packet_comment_id": 5305979608,
        "closure_comment_id": 5306218805,
    }:
        errors.append("protected J2 adjudication authority drift")
    if authority.get("route_target_successor") != {
        "merge_commit": "ca66279862dcec276d2280749e6fae45f6e1e7a0",
        "record": {"path": "governance/result_family_route_target_successors/OTP-J2-TWO-DEGENERATE.json", "digest_algorithm": "git_blob_sha1", "digest": "5b72e13448cdbea88e0f2cf1e637c2d787b297a6"},
        "successor_contract_digest": "1feaeac515beb792c5552bc795826bd999f4e535",
    }:
        errors.append("protected J2 route-target successor authority drift")
    evidence = authority.get("evidence", {})
    if evidence != {
        "construction_record_digest": "e1bc1f04daf28b04a85e92e605732f466ab1e2d6",
        "source_faithful_projection_digest": "ac1ec20e95d6acbcd1c3a111afe28bca92a43377",
        "current_source_bytes": 2487031,
        "current_source_sha256": "ebc561ab5c53dbd240e17a8fdb6fffeb648591eca85dbfc7466f563638f8c566",
        "source_locus": "Chapter 10, Theorem 1.2",
        "formal_subject_commit": "94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6",
        "formal_subject_tree": "174289e4d4958cb0509874e6e53400e098213de7",
        "lean_version": "4.32.0",
    }:
        errors.append("protected J2 source/evidence authority drift")
    if authority.get("control_plan") != {
        "conformance": "within_human_steward_authorized_output_plan",
        "control_plan_change_requested": False,
        "human_steward_intervention_required_only_for_control_plan_change": True,
        "routine_stage_progression_without_human_steward_intervention_after_protected_design": True,
    }:
        errors.append("J2 streamlined output control plan drift")

    if contract.get("contract_state") != "design_only":
        errors.append("J2 output contract is not design-only")
    scope = contract.get("output_scope", {})
    if scope.get("encoded_targets") != EXPECTED_TARGETS:
        errors.append("J2 output target membership/order drift")
    if scope.get("historical_predecessor_targets") != EXPECTED_HISTORICAL_TARGETS:
        errors.append("J2 historical predecessor target identity drift")
    projection = scope.get("source_projection", {})
    if projection.get("stronger_coloring_side_property_in_scope") is not False:
        errors.append("stronger coloring-side property reintroduced into J2 output scope")
    for key in ("fixed_finite_graph", "connected", "bipartite", "two_degenerate", "positive_c", "positive_epsilon", "eventual_extremal_lower_bound_above_three_halves", "source_core_refutes_r2_degeneracy_bound"):
        if projection.get(key) is not True:
            errors.append(f"source-faithful J2 output projection weakened: {key}")
    if contract.get("qualification_semantics", {}).get("permitted_disposition") != "qualified_source_faithful_targets_only":
        errors.append("J2 qualification disposition drift")

    future = contract.get("future_certificate", {})
    if future != {
        "certificate_id": "MC-OTP-J2-TWO-DEGENERATE-QUAL-001",
        "path": "certificates/formal_sources/MC-OTP-J2-TWO-DEGENERATE-001.json",
        "schema": {"path": "schemas/otp_j2_source_faithful_qualified_output.schema.json", "digest_algorithm": "git_blob_sha1", "digest": EXPECTED_FUTURE_SCHEMA_BLOB},
        "record_type": "otp_j2_source_faithful_qualified_output",
        "disposition": "qualified_source_faithful_targets_only",
        "mathematical_target_proved": False,
    }:
        errors.append("future J2 certificate identity or semantics drift")
    if contract.get("publication_protocol") != EXPECTED_PUBLICATION:
        errors.append("J2 publication protocol drift")

    execution = contract.get("execution_requirements", {})
    for key in ("certificate_content_commit_must_change_only_certificate_semantics", "route_transition_must_change_only_j2_route_semantics", "route_transition_must_preserve_exact_target_set", "route_transition_must_insert_exactly_one_cert_output", "later_execution_control_commits_must_preserve_certificate_bytes_and_route_semantics"):
        if execution.get(key) is not True:
            errors.append(f"J2 execution requirement weakened: {key}")
    if execution.get("protected_effect_before_execution_merge") != "none":
        errors.append("J2 execution gains premature protected effect")

    gate = contract.get("execution_gate", {})
    for key in ("protected_contract_merge_and_blob_required", "exact_head_cert_checks_required", "exact_head_gcl_conformance_required", "linux_windows_output_validation_required", "codeql_no_new_alerts_required", "fresh_non_author_specialist_approval_required", "protected_merge_required", "protected_merge_method_must_preserve_ancestry", "expected_head_guard_required", "protected_main_readback_required", "head_change_requires_revalidation_and_reapproval", "human_steward_intervention_required_only_for_control_plan_change"):
        if gate.get(key) is not True:
            errors.append(f"J2 execution gate disabled: {key}")
    if gate.get("separate_human_steward_authorization_required") is not False:
        errors.append("redundant Human Steward execution authorization reintroduced")

    if contract.get("state") != {
        "route_state": "submitted", "cert_output": None, "mathematical_target_proved": False,
        "may_issue_output": False, "may_promote_claim": False,
        "stronger_coloring_property_certified": False, "aggregate_output": False,
    }:
        errors.append("J2 design-only contract state drift or authority inflation")

    if any((future_certificate_present, candidate_present, staged_certificate_present, staged_route_present)):
        errors.append("operative/staged J2 output artifact exists during design-only operation")

    route = next((r for r in routes.get("routes", []) if r.get("route_id") == "MC-ROUTE-OTP-J2-TWO-DEGENERATE"), None)
    if route is None:
        errors.append("J2 route missing")
    else:
        if route.get("intake_status") != "submitted":
            errors.append("J2 route changed during output-contract design")
        if route.get("cert_output") is not None:
            errors.append("J2 Cert output inserted during output-contract design")
        if route.get("target_claim_ids") != EXPECTED_TARGETS:
            errors.append("J2 live registered targets drift")

    if adjudication.get("encoded_targets") != EXPECTED_TARGETS:
        errors.append("protected J2 adjudication target drift")
    if adjudication.get("decision", {}).get("disposition") != "adjudication_clear_source_faithful_targets_only":
        errors.append("protected J2 adjudication disposition mismatch")
    adjudication_state = adjudication.get("state", {})
    for key, value in {"route_state": "submitted", "cert_output": None, "mathematical_target_proved": False, "may_issue_output": False, "may_promote_claim": False, "stronger_coloring_property_certified": False, "aggregate_adjudication": False, "aggregate_output": False}.items():
        if adjudication_state.get(key) != value:
            errors.append(f"protected J2 adjudication state drift: {key}")

    props = future_schema.get("properties", {})
    if props.get("encoded_targets", {}).get("const") != EXPECTED_TARGETS:
        errors.append("future J2 certificate target drift")
    qual = props.get("qualification", {}).get("const", {})
    if qual.get("disposition") != "qualified_source_faithful_targets_only":
        errors.append("future J2 certificate disposition drift")
    if qual.get("source_projection", {}).get("stronger_coloring_side_property_in_scope") is not False:
        errors.append("future J2 certificate reintroduces stronger coloring-side scope")
    state = props.get("state", {}).get("const", {})
    if state != {"route_state": "qualified", "cert_output_inserted": True, "mathematical_target_proved": False, "may_promote_claim": False, "stronger_coloring_property_certified": False, "aggregate_output": False}:
        errors.append("future J2 certificate state drift")

    limitations = contract.get("preserved_limitations", {})
    for key in ("historical_stronger_targets_qualified", "stronger_coloring_property_source_authorized", "stronger_coloring_property_certified", "proof_body_compared_in_full", "source_internal_entropy_lemmas_reformalized", "unrestricted_source_theorem_proof_claim", "other_family_outputs_authorized", "aggregate_openai_ten_proofs_authority"):
        if limitations.get(key) is not False:
            errors.append(f"J2 contract limitation inflated: {key}")
    if limitations.get("whole_document_byte_equivalence") != "not_established" or limitations.get("whole_document_semantic_equivalence") != "not_established":
        errors.append("J2 whole-document equivalence inflated")

    future_limitations = props.get("preserved_limitations", {}).get("const", {})
    if future_limitations != limitations:
        errors.append("future J2 certificate limitations diverge from contract")

    boundary = str(contract.get("claim_boundary", "")).lower()
    for token in ("design-only", "does not issue a certificate", "submitted route", "historical stronger", "stronger coloring-side", "whole-document", "proof body", "entropy", "mathematical target proved", "aggregate openai ten proofs", "route-first", "squash", "rebase", "commercial claims"):
        if token not in boundary:
            errors.append(f"J2 claim boundary missing token: {token}")
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"OTP-J2-TWO-DEGENERATE output-contract validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print("validated design-only OTP-J2 source-faithful output contract; no output or route authority executed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
