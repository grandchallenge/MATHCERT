#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "governance/result_family_output_contracts/OTP-F-EHRHART.json"
CONTRACT_SCHEMA = ROOT / "schemas/otp_ehrhart_output_contract.schema.json"
FUTURE_SCHEMA = ROOT / "schemas/otp_ehrhart_qualified_output.schema.json"
ROUTES = ROOT / "governance/certification_routes.json"
ADJUDICATION = ROOT / "governance/result_family_adjudications/OTP-F-EHRHART.json"
ATTESTATION = ROOT / "governance/post_merge_attestations/OTP-F-EHRHART-CERT-ADJUDICATION-001.v1.json"
FUTURE_CERTIFICATE = ROOT / "certificates/formal_sources/MC-OTP-F-EHRHART-001.json"
OUTPUT_CANDIDATE = ROOT / "governance/result_family_output_candidates/OTP-F-EHRHART.json"

EXPECTED_TARGETS = [
    "Ehrhart.Volume.ehrhart_volume_inequality_for_sets",
    "Ehrhart.SimplexVolume.exists_centeredBody_sharp",
    "Ehrhart.SimplexVolume.barycenter_centeredSimplex",
    "Ehrhart.SimplexVolume.normalizedVolume_centeredSimplex",
]
EXPECTED_CONTRACT_FILES = {"OTP-F-EHRHART.json"}
EXPECTED_ADJUDICATION_BLOB = "dcea25320169b9309ebf6c7f48249df9a312555f"
EXPECTED_ATTESTATION_BLOB = "478811b443c9a60c12de85008d4e6da253de095a"
EXPECTED_FUTURE_SCHEMA_BLOB = "01bef61e1cc58544a3e007e3d74cde2420ec53bf"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload,
        usedforsecurity=False,
    ).hexdigest()


def validation_errors(
    *,
    contract: dict[str, Any] | None = None,
    contract_schema: dict[str, Any] | None = None,
    future_schema: dict[str, Any] | None = None,
    routes: dict[str, Any] | None = None,
    adjudication: dict[str, Any] | None = None,
    attestation: dict[str, Any] | None = None,
    adjudication_blob: str | None = None,
    attestation_blob: str | None = None,
    future_schema_blob: str | None = None,
    future_certificate_present: bool | None = None,
    candidate_present: bool | None = None,
    contract_files: set[str] | None = None,
) -> list[str]:
    errors: list[str] = []
    contract = load(CONTRACT) if contract is None else contract
    contract_schema = load(CONTRACT_SCHEMA) if contract_schema is None else contract_schema
    future_schema = load(FUTURE_SCHEMA) if future_schema is None else future_schema
    routes = load(ROUTES) if routes is None else routes
    adjudication = load(ADJUDICATION) if adjudication is None else adjudication
    attestation = load(ATTESTATION) if attestation is None else attestation
    adjudication_blob = git_blob_sha1(ADJUDICATION) if adjudication_blob is None else adjudication_blob
    attestation_blob = git_blob_sha1(ATTESTATION) if attestation_blob is None else attestation_blob
    future_schema_blob = git_blob_sha1(FUTURE_SCHEMA) if future_schema_blob is None else future_schema_blob
    future_certificate_present = FUTURE_CERTIFICATE.exists() if future_certificate_present is None else future_certificate_present
    candidate_present = OUTPUT_CANDIDATE.exists() if candidate_present is None else candidate_present
    contract_files = (
        {path.name for path in CONTRACT.parent.glob("*.json")}
        if contract_files is None
        else contract_files
    )

    if contract_files != EXPECTED_CONTRACT_FILES:
        errors.append("output-contract membership drift")
    if contract_schema.get("additionalProperties") is not False:
        errors.append("output-contract schema must remain closed")
    for error in Draft202012Validator(contract_schema).iter_errors(contract):
        errors.append(f"output-contract schema violation: {error.message}")

    if future_schema.get("additionalProperties") is not False:
        errors.append("future qualification schema must remain closed")
    if future_schema.get("$id") != "https://grandchallenge.ai/schemas/otp_ehrhart_qualified_output.schema.json":
        errors.append("future qualification schema identity drift")
    if set(future_schema.get("required", [])) != {
        "schema_version", "record_type", "certificate_id", "result_family", "route_id",
        "source_authority", "encoded_targets", "qualification", "evidence_receipts",
        "axiom_report", "trust_boundary", "state", "preserved_limitations", "claim_boundary",
    }:
        errors.append("future qualification schema required-field drift")
    if future_schema_blob != EXPECTED_FUTURE_SCHEMA_BLOB:
        errors.append("future qualification schema blob drift")

    if adjudication_blob != EXPECTED_ADJUDICATION_BLOB:
        errors.append("protected adjudication-record blob drift")
    if attestation_blob != EXPECTED_ATTESTATION_BLOB:
        errors.append("protected closure-attestation blob drift")

    authority = contract.get("protected_authority", {})
    if authority.get("adjudication", {}).get("record", {}).get("digest") != EXPECTED_ADJUDICATION_BLOB:
        errors.append("contract adjudication authority drift")
    if authority.get("adjudication", {}).get("disposition") != "adjudication_clear_encoded_targets_only":
        errors.append("contract adjudication disposition drift")
    if authority.get("closure_attestation", {}).get("manifest", {}).get("digest") != EXPECTED_ATTESTATION_BLOB:
        errors.append("contract closure-attestation authority drift")
    if contract.get("implementation_authorization") != {
        "issue": "https://github.com/grandchallenge/MATHCERT/issues/68",
        "comment_id": 5157303744,
        "author": "jimsteeg",
        "scope": "design_only_bounded_qualification_output_contract",
    }:
        errors.append("Human Steward implementation authorization drift")

    if contract.get("contract_state") != "design_only":
        errors.append("output contract is not design-only")
    if contract.get("output_scope", {}).get("encoded_targets") != EXPECTED_TARGETS:
        errors.append("output target membership or order drift")
    if contract.get("qualification_semantics", {}).get("permitted_disposition") != "qualified_encoded_targets_only":
        errors.append("permitted qualification disposition drift")

    future = contract.get("future_certificate", {})
    if future != {
        "certificate_id": "MC-OTP-F-EHRHART-QUAL-001",
        "path": "certificates/formal_sources/MC-OTP-F-EHRHART-001.json",
        "schema": {
            "path": "schemas/otp_ehrhart_qualified_output.schema.json",
            "digest_algorithm": "git_blob_sha1",
            "digest": EXPECTED_FUTURE_SCHEMA_BLOB,
        },
        "record_type": "otp_ehrhart_qualified_output",
        "disposition": "qualified_encoded_targets_only",
        "mathematical_target_proved": False,
    }:
        errors.append("future certificate identity or semantics drift")

    atomic = contract.get("atomic_execution", {})
    if atomic != {
        "mode": "single_protected_transaction",
        "route_transition": {"from": "submitted", "to": "qualified"},
        "certificate_insertion": "exactly_one",
        "route_and_output_same_commit_required": True,
        "partial_state_prohibited": True,
        "registry_blockers_must_be_rewritten_to_preserved_qualification_boundaries": True,
    }:
        errors.append("atomic execution contract drift")

    candidate = contract.get("execution_candidate_requirements", {})
    if candidate.get("candidate_state") != "output_candidate_prepared_pending_authorization":
        errors.append("execution-candidate state drift")
    if candidate.get("protected_effect_before_authorization") != "none":
        errors.append("execution candidate gains premature protected effect")

    gate = contract.get("execution_gate", {})
    for key in (
        "separate_human_steward_authorization_required",
        "authorization_must_name_contract_and_exact_candidate_head",
        "protected_contract_merge_and_blob_required",
        "exact_head_cert_checks_required",
        "exact_head_gcl_conformance_required",
        "fresh_non_author_specialist_approval_required",
        "exact_head_human_steward_merge_disposition_required",
        "protected_merge_required",
        "head_change_requires_revalidation_and_reapproval",
    ):
        if gate.get(key) is not True:
            errors.append(f"execution gate disabled: {key}")

    state = contract.get("state", {})
    if state != {
        "route_state": "submitted",
        "cert_output": None,
        "mathematical_target_proved": False,
        "may_issue_output": False,
        "may_promote_claim": False,
        "aggregate_output": False,
    }:
        errors.append("design-only state drift or authority inflation")

    route = next(
        (item for item in routes.get("routes", []) if item.get("route_id") == "MC-ROUTE-OTP-F-EHRHART"),
        None,
    )
    if route is None:
        errors.append("OTP-F-EHRHART route missing")
    else:
        if route.get("intake_status") != "submitted":
            errors.append("OTP-F-EHRHART route changed before output execution")
        if route.get("cert_output") is not None:
            errors.append("OTP-F-EHRHART Cert output inserted during design")
        if route.get("target_claim_ids") != EXPECTED_TARGETS:
            errors.append("OTP-F-EHRHART registered targets drift")

    if adjudication.get("encoded_targets") != EXPECTED_TARGETS:
        errors.append("protected adjudication target drift")
    if adjudication.get("decision", {}).get("disposition") != "adjudication_clear_encoded_targets_only":
        errors.append("protected adjudication disposition mismatch")
    if adjudication.get("state") != {
        "route_state": "submitted",
        "adjudication_operation_authorized": True,
        "adjudication_recorded_on_branch": True,
        "cert_output": None,
        "mathematical_target_proved": False,
        "may_promote_claim": False,
        "aggregate_adjudication": False,
    }:
        errors.append("protected adjudication state drift")

    binding = attestation.get("binding_disposition", {})
    if binding.get("value") != "adjudication_clear_encoded_targets_only":
        errors.append("closure attestation disposition mismatch")
    if binding.get("encoded_targets") != EXPECTED_TARGETS:
        errors.append("closure attestation target drift")
    if attestation.get("preserved_state") != {
        "route_state": "submitted",
        "cert_output": None,
        "mathematical_target_proved": False,
        "may_promote_claim": False,
        "aggregate_adjudication": False,
    }:
        errors.append("closure attestation state drift")

    certificate_properties = future_schema.get("properties", {})
    if certificate_properties.get("encoded_targets", {}).get("const") != EXPECTED_TARGETS:
        errors.append("future certificate schema target drift")
    if certificate_properties.get("qualification", {}).get("const", {}).get("disposition") != "qualified_encoded_targets_only":
        errors.append("future certificate schema disposition drift")
    future_state = certificate_properties.get("state", {}).get("const", {})
    if future_state != {
        "route_state": "qualified",
        "cert_output_inserted": True,
        "mathematical_target_proved": False,
        "may_promote_claim": False,
        "aggregate_output": False,
    }:
        errors.append("future certificate schema state drift")

    if future_certificate_present:
        errors.append("future Cert output exists during design-only stage")
    if candidate_present:
        errors.append("output execution candidate exists without separate authorization")

    limitations = contract.get("preserved_limitations", {})
    if limitations.get("classification_or_uniqueness_of_all_equality_cases") != "excluded":
        errors.append("equality-case exclusion removed")
    if limitations.get("proof_body_compared_in_full") is not False:
        errors.append("proof-body comparison inflated")
    if limitations.get("other_family_outputs_authorized") is not False:
        errors.append("other-family output authority inserted")

    boundary = str(contract.get("claim_boundary", ""))
    for token in (
        "design-only",
        "does not issue a certificate",
        "submitted route",
        "mathematical target proved",
        "equality cases",
        "whole-document equivalence",
        "aggregate ten-proofs authority",
        "commercial claims",
    ):
        if token not in boundary:
            errors.append(f"claim boundary missing token: {token}")

    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"OTP-F-EHRHART output-contract validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print(
        "validated design-only OTP-F-EHRHART qualification-output contract, exact protected "
        "authority chain, atomic future route/output transaction, and zero present output authority"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
