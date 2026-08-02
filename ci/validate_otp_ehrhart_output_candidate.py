#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "governance/result_family_output_candidates/OTP-F-EHRHART.json"
CANDIDATE_SCHEMA = ROOT / "schemas/otp_ehrhart_output_candidate.schema.json"
STAGED_CERTIFICATE = ROOT / "governance/result_family_output_candidates/staged_certificates/MC-OTP-F-EHRHART-001.json"
TRANSITION = ROOT / "governance/result_family_output_candidates/staged_route_transitions/OTP-F-EHRHART.json"
TRANSITION_SCHEMA = ROOT / "schemas/otp_ehrhart_atomic_route_transition_template.schema.json"
FUTURE_SCHEMA = ROOT / "schemas/otp_ehrhart_qualified_output.schema.json"
LIVE_CERTIFICATE = ROOT / "certificates/formal_sources/MC-OTP-F-EHRHART-001.json"
ROUTES = ROOT / "governance/certification_routes.json"
CONTRACT = ROOT / "governance/result_family_output_contracts/OTP-F-EHRHART.json"
ADJUDICATION = ROOT / "governance/result_family_adjudications/OTP-F-EHRHART.json"
ATTESTATION = ROOT / "governance/post_merge_attestations/OTP-F-EHRHART-CERT-ADJUDICATION-001.v1.json"

BASE_SPEC = importlib.util.spec_from_file_location(
    "validate_otp_ehrhart_output_contract",
    ROOT / "ci/validate_otp_ehrhart_output_contract.py",
)
assert BASE_SPEC and BASE_SPEC.loader
BASE = importlib.util.module_from_spec(BASE_SPEC)
BASE_SPEC.loader.exec_module(BASE)

EXPECTED_TARGETS = [
    "Ehrhart.Volume.ehrhart_volume_inequality_for_sets",
    "Ehrhart.SimplexVolume.exists_centeredBody_sharp",
    "Ehrhart.SimplexVolume.barycenter_centeredSimplex",
    "Ehrhart.SimplexVolume.normalizedVolume_centeredSimplex",
]
EXPECTED_BLOBS = {
    "candidate_schema": "8fc02d4c7c78858688252e989c1547cf5df9fc7e",
    "transition_schema": "8a22bf22a09cbf5d802a95ffa8401246bf5519f3",
    "staged_certificate": "27a855c949b67e71372c7f0d6601d80125d33968",
    "transition": "2862950612fde71331cce92161ecf208f57f3eb9",
    "contract": "bdcfcc4d8b94b5d9c6993842260c8347fc2f6458",
    "future_schema": "01bef61e1cc58544a3e007e3d74cde2420ec53bf",
    "adjudication": "dcea25320169b9309ebf6c7f48249df9a312555f",
    "attestation": "478811b443c9a60c12de85008d4e6da253de095a",
    "routes": "b5541045591f8589130b1577c50d51d70c3b4337",
}
EXPECTED_CANDIDATE_FILES = {
    "OTP-F-EHRHART.json",
    "staged_certificates/MC-OTP-F-EHRHART-001.json",
    "staged_route_transitions/OTP-F-EHRHART.json",
}
EXECUTION_TOKEN = "$PROTECTED_EXECUTION_MERGE"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload,
        usedforsecurity=False,
    ).hexdigest()


def actual_candidate_files() -> set[str]:
    root = CANDIDATE.parent
    return {path.relative_to(root).as_posix() for path in root.rglob("*.json")}


def validation_errors(
    *,
    candidate: dict[str, Any] | None = None,
    candidate_schema: dict[str, Any] | None = None,
    staged_certificate: dict[str, Any] | None = None,
    transition: dict[str, Any] | None = None,
    transition_schema: dict[str, Any] | None = None,
    future_schema: dict[str, Any] | None = None,
    routes: dict[str, Any] | None = None,
    contract: dict[str, Any] | None = None,
    adjudication: dict[str, Any] | None = None,
    attestation: dict[str, Any] | None = None,
    blobs: dict[str, str] | None = None,
    live_certificate_present: bool | None = None,
    candidate_files: set[str] | None = None,
) -> list[str]:
    errors = BASE.validation_errors(candidate_present=False)
    candidate = load(CANDIDATE) if candidate is None else candidate
    candidate_schema = load(CANDIDATE_SCHEMA) if candidate_schema is None else candidate_schema
    staged_certificate = load(STAGED_CERTIFICATE) if staged_certificate is None else staged_certificate
    transition = load(TRANSITION) if transition is None else transition
    transition_schema = load(TRANSITION_SCHEMA) if transition_schema is None else transition_schema
    future_schema = load(FUTURE_SCHEMA) if future_schema is None else future_schema
    routes = load(ROUTES) if routes is None else routes
    contract = load(CONTRACT) if contract is None else contract
    adjudication = load(ADJUDICATION) if adjudication is None else adjudication
    attestation = load(ATTESTATION) if attestation is None else attestation
    if blobs is None:
        blobs = {
            "candidate_schema": git_blob_sha1(CANDIDATE_SCHEMA),
            "transition_schema": git_blob_sha1(TRANSITION_SCHEMA),
            "staged_certificate": git_blob_sha1(STAGED_CERTIFICATE),
            "transition": git_blob_sha1(TRANSITION),
            "contract": git_blob_sha1(CONTRACT),
            "future_schema": git_blob_sha1(FUTURE_SCHEMA),
            "adjudication": git_blob_sha1(ADJUDICATION),
            "attestation": git_blob_sha1(ATTESTATION),
            "routes": EXPECTED_BLOBS["routes"],
        }
    live_certificate_present = LIVE_CERTIFICATE.exists() if live_certificate_present is None else live_certificate_present
    candidate_files = actual_candidate_files() if candidate_files is None else candidate_files

    if candidate_schema.get("additionalProperties") is not False:
        errors.append("candidate schema must remain closed")
    if candidate_schema.get("$id") != "https://grandchallenge.ai/schemas/otp_ehrhart_output_candidate.schema.json":
        errors.append("candidate schema identity drift")
    for error in Draft202012Validator(candidate_schema).iter_errors(candidate):
        errors.append(f"candidate schema violation: {error.message}")

    if transition_schema.get("additionalProperties") is not False:
        errors.append("transition schema must remain closed")
    if transition_schema.get("$id") != "https://grandchallenge.ai/schemas/otp_ehrhart_atomic_route_transition_template.schema.json":
        errors.append("transition schema identity drift")
    for error in Draft202012Validator(transition_schema).iter_errors(transition):
        errors.append(f"transition schema violation: {error.message}")

    for error in Draft202012Validator(future_schema).iter_errors(staged_certificate):
        errors.append(f"staged certificate schema violation: {error.message}")

    for name, expected in EXPECTED_BLOBS.items():
        if blobs.get(name) != expected:
            errors.append(f"{name} blob drift")

    if candidate_files != EXPECTED_CANDIDATE_FILES:
        errors.append("output-candidate file membership drift")
    if live_certificate_present:
        errors.append("live Cert output exists during candidate preparation")

    if candidate.get("implementation_authorization") != {
        "issue": "https://github.com/grandchallenge/MATHCERT/issues/70",
        "comment_id": 5157454689,
        "author": "jimsteeg",
        "scope": "non_operational_exact_output_candidate_preparation_only",
    }:
        errors.append("Human Steward candidate authorization drift")
    if candidate.get("candidate_state") != "output_candidate_prepared_pending_authorization":
        errors.append("candidate state drift")
    if candidate.get("encoded_targets") != EXPECTED_TARGETS:
        errors.append("candidate target membership or order drift")

    authority = candidate.get("protected_authority", {})
    if authority.get("contract") != {
        "merge_commit": "0a8df66a768fe1b2671cb5301ecb20464d9b5ecf",
        "path": "governance/result_family_output_contracts/OTP-F-EHRHART.json",
        "digest_algorithm": "git_blob_sha1",
        "digest": EXPECTED_BLOBS["contract"],
    }:
        errors.append("protected output-contract authority drift")
    if authority.get("restricted_output_schema", {}).get("digest") != EXPECTED_BLOBS["future_schema"]:
        errors.append("protected restricted-output schema drift")
    if authority.get("adjudication", {}).get("digest") != EXPECTED_BLOBS["adjudication"]:
        errors.append("protected adjudication authority drift")
    if authority.get("adjudication", {}).get("disposition") != "adjudication_clear_encoded_targets_only":
        errors.append("protected adjudication disposition drift")
    if authority.get("closure_attestation", {}).get("digest") != EXPECTED_BLOBS["attestation"]:
        errors.append("protected closure-attestation authority drift")
    if authority.get("live_route_registry", {}).get("digest") != EXPECTED_BLOBS["routes"]:
        errors.append("live registry authority drift")

    staged = candidate.get("staged_artifacts", {})
    cert_ref = staged.get("certificate", {})
    if cert_ref.get("digest") != EXPECTED_BLOBS["staged_certificate"]:
        errors.append("staged certificate identity drift")
    if cert_ref.get("future_live_path") != "certificates/formal_sources/MC-OTP-F-EHRHART-001.json":
        errors.append("future live certificate path drift")
    if cert_ref.get("disposition") != "qualified_encoded_targets_only":
        errors.append("staged certificate disposition drift")
    transition_ref = staged.get("route_transition", {})
    if transition_ref.get("digest") != EXPECTED_BLOBS["transition"]:
        errors.append("staged route-transition identity drift")
    if transition_ref.get("execution_commit_token") != EXECUTION_TOKEN:
        errors.append("execution-commit token drift")

    if staged_certificate.get("certificate_id") != "MC-OTP-F-EHRHART-QUAL-001":
        errors.append("staged certificate identity drift")
    if staged_certificate.get("encoded_targets") != EXPECTED_TARGETS:
        errors.append("staged certificate target drift")
    qualification = staged_certificate.get("qualification", {})
    if qualification.get("disposition") != "qualified_encoded_targets_only":
        errors.append("staged qualification disposition drift")
    if qualification.get("source_theorem_mathematically_proved") is not False:
        errors.append("staged certificate promotes source theorem proof")
    if staged_certificate.get("axiom_report") != {
        "kernel_axioms": ["Classical.choice", "Quot.sound", "propext"],
        "imported_domain_axioms": [],
        "unexpected_axioms": [],
    }:
        errors.append("staged certificate axiom boundary drift")
    if staged_certificate.get("trust_boundary") != {
        "solution_placeholder_count": 0,
        "unsafe_declaration_count": 0,
        "custom_axiom_count": 0,
    }:
        errors.append("staged certificate trust-boundary drift")
    if staged_certificate.get("state") != {
        "route_state": "qualified",
        "cert_output_inserted": True,
        "mathematical_target_proved": False,
        "may_promote_claim": False,
        "aggregate_output": False,
    }:
        errors.append("staged certificate state drift")

    live_route = next(
        (item for item in routes.get("routes", []) if item.get("route_id") == "MC-ROUTE-OTP-F-EHRHART"),
        None,
    )
    before = transition.get("before", {})
    after = transition.get("after_template", {})
    if live_route is None:
        errors.append("live OTP-F-EHRHART route missing")
    else:
        if live_route != before:
            errors.append("staged transition before-state does not exactly match live route")
        if live_route.get("intake_status") != "submitted" or live_route.get("cert_output") is not None:
            errors.append("live route changed during candidate preparation")

    allowed_changed = {"intake_status", "claim_boundary", "cert_output", "blockers", "reopening_conditions"}
    for key in set(before) | set(after):
        if key not in allowed_changed and before.get(key) != after.get(key):
            errors.append(f"unauthorized route-field mutation in staged transition: {key}")
    if before.get("intake_status") != "submitted" or before.get("cert_output") is not None:
        errors.append("transition before-state is not submitted with null output")
    if after.get("intake_status") != "qualified":
        errors.append("transition after-state is not qualified")
    output = after.get("cert_output", {})
    if output != {
        "repository": "grandchallenge/MATHCERT",
        "commit_sha": EXECUTION_TOKEN,
        "path": "certificates/formal_sources/MC-OTP-F-EHRHART-001.json",
        "digest_algorithm": "git_blob_sha1",
        "digest": EXPECTED_BLOBS["staged_certificate"],
    }:
        errors.append("staged cert_output insertion drift")
    if transition.get("execution_commit_binding", {}).get("unresolved_during_candidate_preparation") is not True:
        errors.append("execution commit resolved prematurely")
    atomicity = transition.get("atomicity", {})
    if atomicity.get("route_and_certificate_same_protected_commit_required") is not True:
        errors.append("route/certificate atomicity disabled")
    if atomicity.get("partial_application_prohibited") is not True:
        errors.append("partial execution admitted")
    if atomicity.get("certificate_digest") != EXPECTED_BLOBS["staged_certificate"]:
        errors.append("atomic transition certificate digest drift")
    if transition.get("candidate_effect") != "none_until_separately_authorized_atomic_execution":
        errors.append("candidate gains premature operative effect")

    if candidate.get("atomic_execution_plan") != {
        "route_transition": {"from": "submitted", "to": "qualified"},
        "certificate_insertion": "exactly_one",
        "same_protected_commit_required": True,
        "partial_application_prohibited": True,
        "execution_commit_token_must_be_resolved": True,
    }:
        errors.append("candidate atomic execution plan drift")
    if candidate.get("review_state") != {
        "fresh_non_author_specialist_review_required": True,
        "specialist_review": None,
        "status": "pending_exact_head_non_author_specialist_review",
    }:
        errors.append("candidate review state drift")
    if candidate.get("execution_authorization") != {
        "separate_human_steward_authorization_required": True,
        "must_name_contract_exact_candidate_head_protected_candidate_merge_and_candidate_blob": True,
        "authorization": None,
    }:
        errors.append("candidate execution authorization gate drift")
    if candidate.get("state") != {
        "may_execute": False,
        "live_route_state": "submitted",
        "live_cert_output": None,
        "mathematical_target_proved": False,
        "may_promote_claim": False,
        "aggregate_output": False,
        "protected_effect": "none",
    }:
        errors.append("candidate state inflation")

    if contract.get("contract_id") != "MC-OTP-F-EHRHART-OUTPUT-CONTRACT-001":
        errors.append("protected contract identity drift")
    if contract.get("state", {}).get("may_issue_output") is not False:
        errors.append("protected design contract gains output authority")
    if adjudication.get("decision", {}).get("disposition") != "adjudication_clear_encoded_targets_only":
        errors.append("adjudication disposition mismatch")
    if attestation.get("binding_disposition", {}).get("value") != "adjudication_clear_encoded_targets_only":
        errors.append("attestation disposition mismatch")

    limitations = candidate.get("preserved_limitations", {})
    if limitations.get("classification_or_uniqueness_of_all_equality_cases") != "excluded":
        errors.append("equality-case exclusion removed")
    if limitations.get("proof_body_compared_in_full") is not False:
        errors.append("proof-body scope inflated")
    if limitations.get("other_family_outputs_authorized") is not False:
        errors.append("other-family authority inserted")

    boundary = str(candidate.get("claim_boundary", ""))
    for token in (
        "non-operative",
        "does not execute",
        "live submitted route",
        "live Cert output",
        "mathematical target proved",
        "equality cases",
        "whole-document equivalence",
        "aggregate ten-proofs authority",
        "commercial claims",
    ):
        if token not in boundary:
            errors.append(f"candidate claim boundary missing token: {token}")

    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"OTP-F-EHRHART output-candidate validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print(
        "validated non-operative OTP-F-EHRHART output candidate, staged restricted certificate, "
        "exact live-route before-state, atomic transition template, and zero live output authority"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
