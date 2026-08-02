#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ATTESTATION = ROOT / "governance/post_merge_attestations/OTP-CERT-ROUTE-REGISTRATION-001.v1.json"
DOCUMENT = ROOT / "governance/post_merge_attestations/OTP-CERT-ROUTE-REGISTRATION-001.v1.md"
SCHEMA = ROOT / "schemas/human_steward_post_merge_attestation.schema.json"
ROUTES = ROOT / "governance/certification_routes.json"
TRANSITION = ROOT / "governance/result_family_output_candidates/staged_route_transitions/OTP-F-EHRHART.json"
RECEIPT = ROOT / "governance/pre_route_candidates/OPENAI_TEN_PROOFS_WP06_ROUTE_REGISTRATIONS.json"
HISTORICAL_ROUTE_BLOB = "b5541045591f8589130b1577c50d51d70c3b4337"

EXPECTED_DOCUMENT = """# Post-merge Human Steward disposition and ratification

I, Human Steward, record my disposition for MATHCERT PR #57, `OTP-CERT-ROUTE-REGISTRATION-001`.

I approve the bounded route-registration operation at exact reviewed head:

`4b9930d8785867bd1c59f4848795cb2b7b960dcf`

I ratify its protected merge as merge commit:

`cec85b13f5be48439e02fbbfedcf7ca1d839c097`

My disposition is limited to registration of the following three independent routes in non-adjudicated `submitted` state:

- `MC-ROUTE-OTP-F-EHRHART`
- `MC-ROUTE-OTP-J1-COMPACTNESS`
- `MC-ROUTE-OTP-J2-TWO-DEGENERATE`

This disposition does not authorize adjudication, proof acceptance, a Cert output, mathematical-target promotion, an aggregate route, aggregate certification, or any mathematical truth, novelty, priority, publication, patentability, product, or commercial claim.

The preserved limitations remain binding: whole-document byte and semantic equivalence are not established; proof bodies were not compared in full; Permanent and GapCVP remain blocked; `All.lean` remains separate integration debt; and the remaining nine result families remain outside this route-registration tranche.

Because the merge occurred before this disposition was recorded, this entry is a retrospective ratification and chronology exception record. It does not represent that the disposition preceded the merge. Future governed merges requiring an exact-head Human Steward disposition must record that disposition before merge.
"""
EXPECTED_ROUTES = [
    "MC-ROUTE-OTP-F-EHRHART",
    "MC-ROUTE-OTP-J1-COMPACTNESS",
    "MC-ROUTE-OTP-J2-TWO-DEGENERATE",
]
EXPECTED_TOP_KEYS = {
    "schema_version", "record_type", "attestation_id", "attestation_version",
    "tracker_issue", "subject", "non_author_review", "exact_head_checks",
    "repository_mirror", "attestation_document", "bound_artifacts", "chronology",
    "ratified_scope", "preserved_limitations", "effect", "claim_boundary",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1_bytes(payload: bytes) -> str:
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload,
        usedforsecurity=False,
    ).hexdigest()


def git_blob_sha1(path: Path) -> str:
    return git_blob_sha1_bytes(path.read_bytes())


def historical_routes(routes: dict[str, Any]) -> dict[str, Any]:
    snapshot = copy.deepcopy(routes)
    before = load(TRANSITION)["before"]
    index = next(
        i for i, item in enumerate(snapshot["routes"])
        if item.get("route_id") == "MC-ROUTE-OTP-F-EHRHART"
    )
    snapshot["routes"][index] = before
    return snapshot


def validation_errors(
    *,
    attestation: dict[str, Any] | None = None,
    document_text: str | None = None,
    schema: dict[str, Any] | None = None,
    routes: dict[str, Any] | None = None,
    document_blob: str | None = None,
    route_blob: str | None = None,
    receipt_blob: str | None = None,
) -> list[str]:
    errors: list[str] = []
    attestation = load(ATTESTATION) if attestation is None else attestation
    document_text = DOCUMENT.read_text(encoding="utf-8") if document_text is None else document_text
    schema = load(SCHEMA) if schema is None else schema
    routes = historical_routes(load(ROUTES)) if routes is None else routes
    document_blob = git_blob_sha1(DOCUMENT) if document_blob is None else document_blob
    route_blob = HISTORICAL_ROUTE_BLOB if route_blob is None else route_blob
    receipt_blob = git_blob_sha1(RECEIPT) if receipt_blob is None else receipt_blob

    if schema.get("additionalProperties") is not False:
        errors.append("attestation schema must remain closed")
    if set(attestation) != EXPECTED_TOP_KEYS:
        errors.append("attestation top-level field set drift")
    if (
        attestation.get("schema_version") != "1.0.0"
        or attestation.get("record_type") != "human_steward_post_merge_attestation"
        or attestation.get("attestation_id") != "MC-HS-POST-MERGE-OTP-CERT-ROUTE-REGISTRATION-001-V1"
        or attestation.get("attestation_version") != 1
        or attestation.get("tracker_issue") != "https://github.com/grandchallenge/MATHCERT/issues/58"
    ):
        errors.append("attestation identity drift")

    if attestation.get("subject") != {
        "repository": "grandchallenge/MATHCERT",
        "pull_request": 57,
        "operation_id": "OTP-CERT-ROUTE-REGISTRATION-001",
        "exact_reviewed_head": "4b9930d8785867bd1c59f4848795cb2b7b960dcf",
        "merge_commit": "cec85b13f5be48439e02fbbfedcf7ca1d839c097",
        "merged_at": "2026-08-02T05:21:28Z",
    }:
        errors.append("attestation subject identity drift")
    if attestation.get("non_author_review") != {
        "reviewer": "jimsteeg",
        "state": "APPROVED",
        "submitted_at": "2026-08-02T05:21:21Z",
    }:
        errors.append("non-author review identity drift")
    if attestation.get("exact_head_checks") != {
        "cert_checks": {"run_id": 30732705290, "conclusion": "success"},
        "gcl_conformance": {"run_id": 30732705451, "conclusion": "success"},
        "otp_family_replay": {"run_id": 30732705279, "conclusion": "success"},
    }:
        errors.append("exact-head CI identity drift")

    mirror = attestation.get("repository_mirror", {})
    if (
        mirror.get("pull_request_comment_id") != 5155627280
        or mirror.get("comment_author") != "jimsteeg"
        or mirror.get("recording_capacity") != "delegated_recording_authority"
        or "does not establish that the disposition preceded merge" not in str(mirror.get("authority_note", ""))
    ):
        errors.append("repository mirror authority or chronology drift")

    if document_text != EXPECTED_DOCUMENT:
        errors.append("verbatim Human Steward disposition text drift")
    if attestation.get("attestation_document") != {
        "path": "governance/post_merge_attestations/OTP-CERT-ROUTE-REGISTRATION-001.v1.md",
        "digest_algorithm": "git_blob_sha1",
        "digest": "afe8b4241fe5c8cc99626f713f9ac76f48f7b805",
    }:
        errors.append("attestation document authority drift")
    if document_blob != "afe8b4241fe5c8cc99626f713f9ac76f48f7b805":
        errors.append("attestation document Git blob drift")

    bound = attestation.get("bound_artifacts", {})
    if bound.get("route_registration_receipt") != {
        "path": "governance/pre_route_candidates/OPENAI_TEN_PROOFS_WP06_ROUTE_REGISTRATIONS.json",
        "digest_algorithm": "git_blob_sha1",
        "digest": "38b1c03a6506f877ad9aed74e92cb6d202b444a5",
    }:
        errors.append("route-registration receipt authority drift")
    if bound.get("registered_route_registry") != {
        "path": "governance/certification_routes.json",
        "digest_algorithm": "git_blob_sha1",
        "digest": HISTORICAL_ROUTE_BLOB,
    }:
        errors.append("registered-route registry authority drift")
    if receipt_blob != "38b1c03a6506f877ad9aed74e92cb6d202b444a5":
        errors.append("route-registration receipt Git blob drift")
    if route_blob != HISTORICAL_ROUTE_BLOB:
        errors.append("registered-route registry Git blob drift")

    chronology = attestation.get("chronology", {})
    for key in (
        "disposition_recorded_after_merge", "chronology_exception",
        "retrospective_ratification", "does_not_rewrite_event_order",
    ):
        if chronology.get(key) is not True:
            errors.append(f"chronology control disabled: {key}")
    if "before merge" not in str(chronology.get("future_rule", "")):
        errors.append("future pre-merge disposition rule weakened")

    if attestation.get("ratified_scope") != {
        "registered_routes": EXPECTED_ROUTES,
        "route_state": "submitted",
        "adjudication_count": 0,
        "cert_output_count": 0,
        "mathematical_target_proved_count": 0,
        "aggregate_route_count": 0,
    }:
        errors.append("ratified scope drift or authority inflation")

    route_records = {
        str(item.get("route_id")): item
        for item in routes.get("routes", [])
        if isinstance(item, dict) and item.get("route_id") in EXPECTED_ROUTES
    }
    if list(route_records) != EXPECTED_ROUTES:
        errors.append("registered OTP route membership or order drift")
    for route_id in EXPECTED_ROUTES:
        route = route_records.get(route_id, {})
        if route.get("intake_status") != "submitted":
            errors.append(f"{route_id}: registered route state drift")
        if route.get("cert_output") is not None:
            errors.append(f"{route_id}: Cert output inserted")

    if attestation.get("preserved_limitations") != {
        "whole_document_byte_equivalence": "not_established",
        "whole_document_semantic_equivalence": "not_established",
        "proof_bodies_compared_in_full": False,
        "blocked_repair_lanes": ["OTP-C-PERMANENT", "OTP-H-GAPCVP"],
        "all_lean_state": "failed_namespace_collision",
        "unexamined_result_family_count": 9,
    }:
        errors.append("preserved limitation set drift")
    if attestation.get("effect") != "documentary_ratification_only_no_new_route_authority":
        errors.append("documentary-only effect drift")
    boundary = str(attestation.get("claim_boundary", ""))
    for token in (
        "does not represent that disposition preceded merge", "does not",
        "adjudicate or prove", "Cert output", "aggregate route", "commercial claims",
    ):
        if token not in boundary:
            errors.append(f"claim boundary missing token: {token}")
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"post-merge attestation validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print("validated immutable route-registration ratification snapshot; later route successors are governed separately")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
