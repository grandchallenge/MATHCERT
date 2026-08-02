#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
ATTESTATION = ROOT / "governance/post_merge_attestations/OTP-F-EHRHART-CERT-ADJUDICATION-001.v1.json"
DOCUMENT = ROOT / "governance/post_merge_attestations/OTP-F-EHRHART-CERT-ADJUDICATION-001.v1.md"
SCHEMA = ROOT / "schemas/otp_ehrhart_adjudication_post_merge_attestation.schema.json"
ADJUDICATION = ROOT / "governance/result_family_adjudications/OTP-F-EHRHART.json"

EXPECTED_DOCUMENT_BLOB = "f55f2f5cfaab0dc4c9cfbf0788975ca833730e22"
EXPECTED_SCHEMA_BLOB = "970385fb65d30cad6a9a10748278901a16a97443"
EXPECTED_ADJUDICATION_BLOB = "dcea25320169b9309ebf6c7f48249df9a312555f"
EXPECTED_TARGETS = [
    "Ehrhart.Volume.ehrhart_volume_inequality_for_sets",
    "Ehrhart.SimplexVolume.exists_centeredBody_sharp",
    "Ehrhart.SimplexVolume.barycenter_centeredSimplex",
    "Ehrhart.SimplexVolume.normalizedVolume_centeredSimplex",
]


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1_bytes(payload: bytes) -> str:
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload,
        usedforsecurity=False,
    ).hexdigest()


def git_blob_sha1(path: Path) -> str:
    return git_blob_sha1_bytes(path.read_bytes())


def validation_errors(
    *,
    attestation: dict[str, Any] | None = None,
    document_text: str | None = None,
    schema: dict[str, Any] | None = None,
    adjudication: dict[str, Any] | None = None,
    document_blob: str | None = None,
    schema_blob: str | None = None,
    adjudication_blob: str | None = None,
) -> list[str]:
    errors: list[str] = []
    attestation = load(ATTESTATION) if attestation is None else attestation
    document_text = DOCUMENT.read_text(encoding="utf-8") if document_text is None else document_text
    schema = load(SCHEMA) if schema is None else schema
    adjudication = load(ADJUDICATION) if adjudication is None else adjudication
    document_blob = git_blob_sha1(DOCUMENT) if document_blob is None else document_blob
    schema_blob = git_blob_sha1(SCHEMA) if schema_blob is None else schema_blob
    adjudication_blob = git_blob_sha1(ADJUDICATION) if adjudication_blob is None else adjudication_blob

    if schema.get("additionalProperties") is not False:
        errors.append("post-merge attestation schema must remain closed")
    if schema_blob != EXPECTED_SCHEMA_BLOB:
        errors.append("post-merge attestation schema Git blob drift")
    try:
        schema_errors = Draft202012Validator(schema).iter_errors(attestation)
        errors.extend(f"attestation schema violation: {error.message}" for error in schema_errors)
    except Exception as exc:
        errors.append(f"post-merge attestation schema is invalid: {exc}")

    if git_blob_sha1_bytes(document_text.encode("utf-8")) != EXPECTED_DOCUMENT_BLOB:
        errors.append("post-merge attestation document text drift")
    if document_blob != EXPECTED_DOCUMENT_BLOB:
        errors.append("post-merge attestation document Git blob drift")
    if adjudication_blob != EXPECTED_ADJUDICATION_BLOB:
        errors.append("protected adjudication-record Git blob drift")

    if adjudication.get("adjudication_id") != "MC-OTP-F-EHRHART-ADJUDICATION-001":
        errors.append("protected adjudication identity drift")
    if adjudication.get("result_family") != "OTP-F-EHRHART":
        errors.append("protected adjudication result-family drift")
    if adjudication.get("contract_id") != "MC-OTP-ADJUDICATION-CONTRACT-F-EHRHART":
        errors.append("protected adjudication contract drift")
    if adjudication.get("encoded_targets") != EXPECTED_TARGETS:
        errors.append("protected adjudication target membership or order drift")

    decision = adjudication.get("decision", {})
    if decision.get("disposition") != "adjudication_clear_encoded_targets_only":
        errors.append("protected adjudication disposition drift")
    if decision.get("scope") != (
        "The exact four encoded Ehrhart targets and the admitted "
        "centered-simplex sharpness witness only."
    ):
        errors.append("protected adjudication scope drift")

    state = adjudication.get("state", {})
    if state.get("route_state") != "submitted":
        errors.append("OTP-F-EHRHART route-state inflation")
    if state.get("cert_output") is not None:
        errors.append("OTP-F-EHRHART Cert output inserted")
    if state.get("mathematical_target_proved") is not False:
        errors.append("OTP-F-EHRHART proof-status promotion")
    if state.get("may_promote_claim") is not False:
        errors.append("OTP-F-EHRHART claim-promotion authority inserted")
    if state.get("aggregate_adjudication") is not False:
        errors.append("aggregate adjudication authority inserted")

    limitations = adjudication.get("preserved_limitations", {})
    expected_limitations = {
        "classification_or_uniqueness_of_all_equality_cases": "excluded",
        "whole_document_semantic_equivalence": "not_established",
        "proof_body_compared_in_full": False,
        "other_family_adjudications_executed": False,
        "blocked_repair_lanes": ["OTP-C-PERMANENT", "OTP-H-GAPCVP"],
        "all_lean_state": "failed_namespace_collision",
        "unexamined_result_family_count": 9,
    }
    for key, value in expected_limitations.items():
        if limitations.get(key) != value:
            errors.append(f"protected limitation drift: {key}")

    boundary = str(attestation.get("claim_boundary", ""))
    for token in (
        "does not alter the submitted route",
        "Cert output",
        "mathematical target proved",
        "all equality cases",
        "whole-document equivalence",
        "another result family",
        "aggregate ten-proofs authority",
        "commercial claims",
    ):
        if token not in boundary:
            errors.append(f"post-merge claim boundary missing token: {token}")
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"OTP-F-EHRHART post-merge attestation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print(
        "validated OTP-F-EHRHART adjudication post-merge attestation, submitted route, "
        "and zero Cert, proof-promotion, equality-classification, or aggregate authority"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
