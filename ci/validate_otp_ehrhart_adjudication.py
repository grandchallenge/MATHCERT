#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import jsonschema
import otp_ehrhart_candidate_control as candidate_control

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "governance/result_family_adjudications/OTP-F-EHRHART.json"
SCHEMA = ROOT / "schemas/openai_ten_proofs_ehrhart_adjudication.schema.json"
CONTRACT = ROOT / "governance/result_family_adjudication_contracts/OTP-F-EHRHART.json"
CANDIDATE = ROOT / "governance/result_family_execution_candidates/OTP-F-EHRHART.json"
CANDIDATE_MANIFEST = ROOT / "governance/result_family_execution_candidate_manifests/OTP-F-EHRHART.json"
ROUTES = ROOT / "governance/certification_routes.json"
TRANSITION = ROOT / "governance/result_family_output_candidates/staged_route_transitions/OTP-F-EHRHART.json"
CERT_OUTPUT = ROOT / "certificates/openai_ten_proofs/OTP-F-EHRHART.json"
EVIDENCE_ROOT = ROOT / "evidence/openai_ten_proofs/ehrhart_refresh"

TARGETS = [
    "Ehrhart.Volume.ehrhart_volume_inequality_for_sets",
    "Ehrhart.SimplexVolume.exists_centeredBody_sharp",
    "Ehrhart.SimplexVolume.barycenter_centeredSimplex",
    "Ehrhart.SimplexVolume.normalizedVolume_centeredSimplex",
]
EXPECTED_BLOBS = {
    "contract": "6e1c210d82440210da71fd661daffe986df81f03",
    "candidate": "caff4c5b6f99cfbee373af1858174c9e1102d990",
    "candidate_manifest": "6b1b3cf62df8e3005870a4468d2410b080ac3499",
    "route_registry": "b5541045591f8589130b1577c50d51d70c3b4337",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(data)}\0".encode() + data,
        usedforsecurity=False,
    ).hexdigest()


def predecessor_routes(routes: dict[str, Any]) -> dict[str, Any]:
    snapshot = copy.deepcopy(routes)
    before = load(TRANSITION)["before"]
    rows = snapshot.get("routes", [])
    index = next(
        i for i, row in enumerate(rows)
        if row.get("campaign_id") == "OTP-F-EHRHART"
    )
    rows[index] = before
    return snapshot


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
    snapshot_routes = predecessor_routes(routes)
    errors: list[str] = []

    predecessor_errors = (
        candidate_control.validation_errors(
            routes=snapshot_routes,
            authority_blobs={
                "contract": blob(CONTRACT),
                "design_registry": candidate_control.EXPECTED_BLOBS["design_registry"],
                "route_registry": EXPECTED_BLOBS["route_registry"],
            },
            executed_present=False,
        )
        if candidate_errors is None
        else list(candidate_errors)
    )
    errors.extend(
        f"predecessor candidate invalid: {error}"
        for error in predecessor_errors
    )

    authority_blobs = authority_blobs or {
        "contract": blob(CONTRACT),
        "candidate": blob(CANDIDATE),
        "candidate_manifest": blob(CANDIDATE_MANIFEST),
        "route_registry": EXPECTED_BLOBS["route_registry"],
    }
    for name, expected in EXPECTED_BLOBS.items():
        if authority_blobs.get(name) != expected:
            errors.append(f"{name} authority blob drift")

    if schema.get("type") != "object" or schema.get("additionalProperties") is not False:
        errors.append("adjudication schema is not closed")
    if set(schema.get("required", [])) != set(record):
        errors.append("adjudication schema required-field drift")
    if set(schema.get("properties", {})) != set(record):
        errors.append("adjudication schema property-membership drift")
    try:
        jsonschema.Draft202012Validator(schema).validate(record)
    except Exception as exc:
        errors.append(f"adjudication schema validation failed: {exc}")

    identity = (
        record.get("schema_version"),
        record.get("record_type"),
        record.get("adjudication_id"),
        record.get("result_family"),
        record.get("route_id"),
        record.get("contract_id"),
        record.get("tracker_issue"),
    )
    if identity != (
        "1.0.0",
        "openai_ten_proofs_ehrhart_adjudication",
        "MC-OTP-F-EHRHART-ADJUDICATION-001",
        "OTP-F-EHRHART",
        "MC-ROUTE-OTP-F-EHRHART",
        "MC-OTP-ADJUDICATION-CONTRACT-F-EHRHART",
        "https://github.com/grandchallenge/MATHCERT/issues/64",
    ):
        errors.append("adjudication identity drift")

    expected_authority = {
        "contract_design_merge": "9f5ec626306092a352aa5ba8d9920b6ddb11b8bb",
        "contract_blob": EXPECTED_BLOBS["contract"],
        "execution_candidate_head": "883a4ae09c6996367a601eed2b4719972b351aab",
        "execution_candidate_merge": "0c11710965219d5a68968dda8ee6c8eceb20112d",
        "execution_candidate_record_blob": EXPECTED_BLOBS["candidate"],
        "execution_candidate_manifest_blob": EXPECTED_BLOBS["candidate_manifest"],
        "human_steward_authorization": {
            "issue": "https://github.com/grandchallenge/MATHCERT/issues/62",
            "comment_id": 5156788834,
            "named_contract": "MC-OTP-ADJUDICATION-CONTRACT-F-EHRHART",
            "named_candidate_head": "883a4ae09c6996367a601eed2b4719972b351aab",
            "named_candidate_merge": "0c11710965219d5a68968dda8ee6c8eceb20112d",
        },
    }
    if record.get("authority") != expected_authority:
        errors.append("adjudication authority or Human Steward authorization drift")
    if record.get("encoded_targets") != TARGETS:
        errors.append("encoded target membership/order drift")

    assessment = record.get("evidence_assessment", {})
    if (
        assessment.get("equality_case_classification") != "excluded"
        or assessment.get("whole_document_equivalence") != "not_established"
        or assessment.get("proof_body_compared_in_full") is not False
    ):
        errors.append("evidence assessment drift or scope inflation")

    decision = record.get("decision", {})
    if decision.get("disposition") != "adjudication_clear_encoded_targets_only":
        errors.append("governed adjudication disposition drift")
    if decision.get("scope") != "The exact four encoded Ehrhart targets and the admitted centered-simplex sharpness witness only.":
        errors.append("decision scope drift")
    if len(decision.get("rationale", [])) != 5:
        errors.append("decision rationale membership drift")
    if "protected merge" not in decision.get("binding_effect", ""):
        errors.append("binding-effect gate weakened")

    if record.get("review_gate") != {
        "fresh_non_author_specialist_review_required": True,
        "minimum_reviewers": 1,
        "required_state": "APPROVED",
        "must_bind_exact_head": True,
        "recorded_review": None,
    }:
        errors.append("specialist review gate weakened or prepopulated")

    if record.get("state") != {
        "route_state": "submitted",
        "adjudication_operation_authorized": True,
        "adjudication_recorded_on_branch": True,
        "cert_output": None,
        "mathematical_target_proved": False,
        "may_promote_claim": False,
        "aggregate_adjudication": False,
    }:
        errors.append("route/output/proof/aggregate state inflation")

    limits = record.get("preserved_limitations", {})
    if (
        limits.get("classification_or_uniqueness_of_all_equality_cases") != "excluded"
        or limits.get("whole_document_byte_equivalence") != "not_established_between_all_revisions"
        or limits.get("whole_document_semantic_equivalence") != "not_established"
        or limits.get("proof_body_compared_in_full") is not False
        or limits.get("other_family_adjudications_executed") is not False
        or limits.get("unexamined_result_family_count") != 9
        or limits.get("blocked_repair_lanes") != ["OTP-C-PERMANENT", "OTP-H-GAPCVP"]
        or limits.get("all_lean_state") != "failed_namespace_collision"
    ):
        errors.append("preserved limitation drift")

    route = next(
        (row for row in snapshot_routes.get("routes", []) if row.get("campaign_id") == "OTP-F-EHRHART"),
        {},
    )
    if (
        route.get("route_id") != "MC-ROUTE-OTP-F-EHRHART"
        or route.get("intake_status") != "submitted"
        or route.get("target_claim_ids") != TARGETS
        or route.get("cert_output") is not None
    ):
        errors.append("protected submitted route drift")

    if evidence_files is None:
        evidence_files = {
            path.name: path.read_bytes()
            for path in EVIDENCE_ROOT.iterdir()
            if path.is_file()
        }
    required = {
        "axiom-check.json",
        "comparator.log",
        "source-locus-theorem-1.1.txt",
        "source-revision-report.txt",
        "trust-boundary-scan.txt",
    }
    if not required.issubset(evidence_files):
        errors.append("required retained evidence missing")
    else:
        axiom = json.loads(evidence_files["axiom-check.json"])
        if axiom.get("permitted") != ["Classical.choice", "Quot.sound", "propext"]:
            errors.append("permitted axiom set drift")
        if [row.get("theorem") for row in axiom.get("reports", [])] != TARGETS:
            errors.append("theorem-level axiom target drift")
        if any(row.get("unexpected") for row in axiom.get("reports", [])):
            errors.append("unexpected theorem axiom admitted")

    certificate_present = CERT_OUTPUT.exists() if certificate_present is None else certificate_present
    if certificate_present:
        errors.append("Cert output exists before separately governed output operation")

    boundary = record.get("claim_boundary", "")
    for token in (
        "exact encoded OTP-F-EHRHART targets",
        "does not classify",
        "whole-document equivalence",
        "Cert output",
        "mathematical target proved",
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
        print(
            f"OTP-F-EHRHART adjudication validation failed with {len(errors)} error(s)",
            file=sys.stderr,
        )
        return 1
    print(
        "validated protected OTP-F-EHRHART adjudication snapshot and its submitted-route predecessor, with the restricted output handled by successor controls"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
