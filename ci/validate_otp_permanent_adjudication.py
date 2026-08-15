#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

import validate_otp_permanent_execution_candidate as candidate_control

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "governance/result_family_adjudications/OTP-C-PERMANENT.json"
SCHEMA = ROOT / "schemas/openai_ten_proofs_permanent_adjudication.schema.json"
CONTRACT = ROOT / "governance/result_family_adjudication_contracts/OTP-C-PERMANENT.json"
DESIGN_REGISTRY = ROOT / "governance/adjudication_design/OPENAI_TEN_PROOFS_PERMANENT_ADJUDICATION_CONTRACT.json"
CANDIDATE = ROOT / "governance/result_family_execution_candidates/OTP-C-PERMANENT.json"
CANDIDATE_MANIFEST = ROOT / "governance/result_family_execution_candidate_manifests/OTP-C-PERMANENT.json"
ROUTES = ROOT / "governance/certification_routes.json"
EVIDENCE_ROOT = ROOT / "evidence/openai_ten_proofs/permanent_candidate"
FORMAL_CERT_ROOT = ROOT / "certificates/formal_sources"

TARGETS = [
    "PermanentFormulaLowerBound.permanent_divisionFree_formula_logarithmic_lower_bound",
    "PermanentFormulaLowerBound.permanent_rational_formula_logarithmic_lower_bound",
]
WITNESSES = [
    "PermanentFormulaLowerBound.Nonvacuity.permanent_divisionFree_formula_nonvacuous",
    "PermanentFormulaLowerBound.Nonvacuity.permanent_rational_formula_nonvacuous",
]
EXPECTED_BLOBS = {
    "contract": "f9429395e7026f838ad6994b8f908a86506cfe06",
    "design_registry": "2af852600796e35afe034bbaf9b9e13950055a29",
    "candidate": "c9c764d6bffa580ff5a0f2229350b093ec5a3694",
    "candidate_manifest": "5b9ba2b7d2caf00063c38d4a9d8ccbfed334a4b8",
    "route_registry": "4b7f98414958999c8404e30a4a7c0a2a104578da",
}
EXPECTED_CONTROL_PLAN = {
    "conformance": "within_admitted_contract",
    "control_plan_change_requested": False,
    "human_steward_intervention_required_only_for_control_plan_change": True,
    "routine_stage_progression_without_human_steward_intervention": True,
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(data)}\0".encode("ascii") + data, usedforsecurity=False
    ).hexdigest()


def open_object_paths(schema: Any) -> list[str]:
    found: list[str] = []

    def walk(value: Any, path: str = "") -> None:
        if isinstance(value, dict):
            if value.get("type") == "object" and value.get("additionalProperties") is not False:
                found.append(path or "/")
            for key, child in value.items():
                walk(child, f"{path}/{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, f"{path}/{index}")

    walk(schema)
    return found


def defaults() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    return load(RECORD), load(SCHEMA), load(ROUTES)


def validation_errors(
    *,
    record: dict[str, Any] | None = None,
    schema: dict[str, Any] | None = None,
    routes: dict[str, Any] | None = None,
    candidate_errors: list[str] | None = None,
    authority_blobs: dict[str, str] | None = None,
    evidence_files: dict[str, bytes] | None = None,
    certificate_present: bool | None = None,
) -> list[str]:
    default_record, default_schema, default_routes = defaults()
    record = copy.deepcopy(default_record if record is None else record)
    schema = copy.deepcopy(default_schema if schema is None else schema)
    routes = copy.deepcopy(default_routes if routes is None else routes)
    errors: list[str] = []

    predecessor_errors = candidate_control.validation_errors() if candidate_errors is None else list(candidate_errors)
    errors.extend(f"predecessor candidate invalid: {error}" for error in predecessor_errors)

    authority_blobs = authority_blobs or {
        "contract": git_blob_sha1(CONTRACT),
        "design_registry": git_blob_sha1(DESIGN_REGISTRY),
        "candidate": git_blob_sha1(CANDIDATE),
        "candidate_manifest": git_blob_sha1(CANDIDATE_MANIFEST),
        "route_registry": git_blob_sha1(ROUTES),
    }
    for name, expected in EXPECTED_BLOBS.items():
        if authority_blobs.get(name) != expected:
            errors.append(f"{name} authority blob drift")

    open_paths = open_object_paths(schema)
    if open_paths:
        errors.append(f"adjudication schema contains open object: {open_paths[0]}")
    if set(schema.get("required", [])) != set(record):
        errors.append("adjudication schema required-field drift")
    if set(schema.get("properties", {})) != set(record):
        errors.append("adjudication schema property-membership drift")
    for error in Draft202012Validator(schema).iter_errors(record):
        errors.append(f"adjudication schema validation failed: {'/'.join(map(str, error.path))}: {error.message}")

    identity = (record.get("schema_version"), record.get("record_type"), record.get("adjudication_id"), record.get("result_family"), record.get("route_id"), record.get("contract_id"), record.get("tracker_issue"))
    if identity != ("1.0.0", "openai_ten_proofs_permanent_adjudication", "MC-OTP-C-PERMANENT-ADJUDICATION-001", "OTP-C-PERMANENT", "MC-ROUTE-OTP-C-PERMANENT-FORMULA", "MC-OTP-ADJUDICATION-CONTRACT-C-PERMANENT-FORMULA", "https://github.com/grandchallenge/MATHCERT/issues/107"):
        errors.append("adjudication identity drift")

    expected_authority = {
        "contract_design_merge": "67d78a99942df2c864f51728d741118d64bba183",
        "contract_blob": EXPECTED_BLOBS["contract"],
        "adjudication_design_registry_blob": EXPECTED_BLOBS["design_registry"],
        "execution_candidate_head": "08ab265158e6165a1de59452d33d26b9e9b8fd54",
        "execution_candidate_merge": "9406c91990a43880070d3a8bd468b4586fa94aef",
        "execution_candidate_record_blob": EXPECTED_BLOBS["candidate"],
        "execution_candidate_manifest_blob": EXPECTED_BLOBS["candidate_manifest"],
        "evidence_candidate_review": {"reviewer": "jimsteeg", "review_id": 4942963925, "reviewed_head": "08ab265158e6165a1de59452d33d26b9e9b8fd54", "state": "APPROVED"},
        "control_plan": EXPECTED_CONTROL_PLAN,
    }
    if record.get("authority") != expected_authority:
        errors.append("adjudication authority or streamlined control-plan drift")
    if record.get("encoded_targets") != TARGETS:
        errors.append("encoded target membership/order drift")

    expected_raw = {"artifact_id": 9241937165, "artifact_name": "otp-permanent-execution-candidate", "bytes": 10913, "sha256": "13126f10d7976cacb933c58aa5607db03c753370035988827d94c47fce93df0a", "raw_execution_candidate_sha256": "c5f109008c87710dbf1c7e49800b6be8ca730a684b0d13201f2b0a1dcfe14ee7", "raw_bundle_manifest_sha256": "dfa3443ed4197fae90676ad21093109214cda34e9c495ef1998c1da8d3b0d369", "retained_manifest_verified": True, "verification_result": "pass"}
    if record.get("raw_evidence_verification") != expected_raw:
        errors.append("raw evidence verification receipt drift")

    expected_assessment = {"authority_integrity": "clear", "isolated_checker_replay": "clear_two_encoded_formula_targets", "lean_kernel": "accept", "nanoda": "accept", "theorem_axioms": "permitted_only_Classical.choice_Quot.sound_propext", "trust_boundary": "clear_solution_and_witness_no_placeholder_unsafe_or_custom_axiom", "source_statement_concordance": "clear_for_complex_n_ge_32_log2_variable_leaf_constants_128_192", "nonvacuity": "clear_for_both_protected_formula_witnesses", "circuit_targets_in_scope": False, "gate_bounds_in_scope": False, "total_size_consequences_in_scope": False, "historical_pdf_byte_equivalence": "not_established"}
    if record.get("evidence_assessment") != expected_assessment:
        errors.append("evidence assessment drift or scope inflation")

    decision = record.get("decision", {})
    if decision.get("disposition") != "adjudication_clear_encoded_targets_only":
        errors.append("governed adjudication disposition drift")
    if decision.get("question") != "Does the complete admissible evidence support a family-specific MATHCERT adjudication of only the two exact encoded Permanent variable-leaf formula targets, with every recorded source-scope and authority limitation preserved?":
        errors.append("decision question drift")
    if decision.get("scope") != "The exact two encoded Permanent variable-leaf formula targets only.":
        errors.append("decision scope drift")
    if len(decision.get("rationale", [])) != 5:
        errors.append("decision rationale membership drift")
    binding = decision.get("binding_effect", "")
    for token in ("exact-head machine gates", "fresh binding non-author", "protected merge/readback"):
        if token not in binding:
            errors.append(f"binding-effect gate weakened: missing {token}")

    if record.get("review_gate") != {"fresh_non_author_specialist_review_required": True, "minimum_reviewers": 1, "required_state": "APPROVED", "must_bind_exact_head": True, "recorded_review": None}:
        errors.append("specialist review gate weakened or prepopulated")

    if record.get("state") != {"route_state": "submitted", "adjudication_operation_authorized": True, "adjudication_recorded_on_branch": True, "cert_output": None, "mathematical_target_proved": False, "may_issue_output": False, "may_promote_claim": False, "aggregate_adjudication": False, "aggregate_output": False}:
        errors.append("route/output/proof/aggregate state inflation")

    if record.get("preserved_limitations") != {"circuit_targets_in_scope": False, "gate_bounds_in_scope": False, "total_size_consequences_in_scope": False, "historical_pdf_byte_equivalence": "not_established", "aggregate_openai_ten_proofs_authority": False, "unrestricted_source_theorem_proof_claim": False}:
        errors.append("preserved limitation drift")

    route = next((row for row in routes.get("routes", []) if isinstance(row, dict) and row.get("route_id") == "MC-ROUTE-OTP-C-PERMANENT-FORMULA"), None)
    if route is None:
        errors.append("protected Permanent route missing")
    else:
        if route.get("intake_status") != "submitted": errors.append("protected Permanent route is not submitted")
        if route.get("target_claim_ids") != TARGETS: errors.append("protected Permanent route target drift")
        if route.get("cert_output") is not None: errors.append("protected Permanent route gained Cert output")

    if evidence_files is None:
        evidence_files = {path.name: path.read_bytes() for path in EVIDENCE_ROOT.iterdir() if path.is_file()}
    required = {"axiom-check.json", "comparator.log", "evidence-summary.json", "trust-boundary-scan.txt"}
    if not required.issubset(evidence_files):
        errors.append("required retained evidence missing")
    else:
        try:
            axiom = json.loads(evidence_files["axiom-check.json"])
            if axiom.get("permitted") != ["Classical.choice", "Quot.sound", "propext"]: errors.append("permitted axiom set drift")
            if [row.get("theorem") for row in axiom.get("reports", [])] != TARGETS: errors.append("theorem-level axiom target drift")
            if any(row.get("unexpected") for row in axiom.get("reports", [])): errors.append("unexpected theorem axiom admitted")
            comparator = evidence_files["comparator.log"].decode(errors="replace").lower()
            for token in ("nanoda kernel accepts the solution", "lean default kernel accepts the solution", "your solution is okay!"):
                if token not in comparator: errors.append(f"missing checker evidence token: {token}")
            trust = evidence_files["trust-boundary-scan.txt"].decode(errors="replace").lower()
            for token in ("solution/witness placeholder and unsafe/custom-axiom scan: clear", "aggregate all import scan: clear"):
                if token not in trust: errors.append(f"missing trust-boundary evidence token: {token}")
            summary = json.loads(evidence_files["evidence-summary.json"])
            if summary.get("targets", {}).get("theorem_names") != TARGETS: errors.append("evidence-summary target drift")
            if summary.get("targets", {}).get("nonvacuity_witnesses") != WITNESSES: errors.append("nonvacuity witness drift")
            if summary.get("results") != {"solution_build": "pass", "challenge_build": "pass", "comparator": "pass", "lean_kernel": "accept", "nanoda": "accept", "nonvacuity_replay": "pass", "theorem_axiom_report": "permitted_only", "trust_boundary_scan": "clear", "semantic_concordance": "protected_predecessor_reconfirmed"}: errors.append("fresh evidence result drift")
            if summary.get("source_projection") != {"formula_target_count": 2, "circuit_target_count": 0, "coefficient_field": "complex", "dimension_threshold": 32, "log_base": 2, "division_free_variable_leaf_constant": 128, "rational_variable_leaf_constant": 192, "gate_bounds_in_replay": False, "total_leaves_vertices_in_replay": False, "historical_pdf_byte_equivalence": False}: errors.append("source projection drift or scope inflation")
        except Exception as exc:
            errors.append(f"retained evidence assessment failed: {exc}")

    if certificate_present is None:
        certificate_present = FORMAL_CERT_ROOT.is_dir() and any(FORMAL_CERT_ROOT.glob("MC-OTP-C-PERMANENT*.json"))
    if certificate_present:
        errors.append("Permanent Cert output exists before separately governed output operation")

    boundary = record.get("claim_boundary", "")
    for token in ("exact two encoded OTP-C-PERMANENT", "does not certify circuit complexity", "256/384 gate bounds", "historical admitted-PDF byte equivalence", "Cert output", "mathematical target proved", "aggregate OpenAI Ten Proofs authority", "commercial claims"):
        if token not in boundary: errors.append(f"claim boundary missing token: {token}")
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"OTP-C-PERMANENT adjudication validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print("validated proposed OTP-C-PERMANENT disposition: adjudication_clear_encoded_targets_only; route remains submitted with no Cert output, proof promotion, circuit/gate/total-size authority, or aggregate authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
