#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
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

BASE_SPEC = importlib.util.spec_from_file_location(
    "validate_otp_ehrhart_output_contract",
    ROOT / "ci/validate_otp_ehrhart_output_contract.py",
)
assert BASE_SPEC and BASE_SPEC.loader
BASE = importlib.util.module_from_spec(BASE_SPEC)
BASE_SPEC.loader.exec_module(BASE)

EXPECTED_BLOBS = {
    "candidate": "2caf48f8db9dfc68c82dbc7f5def386382952199",
    "candidate_schema": "3a80a5b78fe0e69b3232cd1649ec67fb0362d479",
    "transition": "fd3c39ce2fbb4ba6a62085d6778d9dcb59d8453c",
    "transition_schema": "22560521720bde3f74f3825969d9ce2dadd0b766",
    "staged_certificate": "27a855c949b67e71372c7f0d6601d80125d33968",
    "routes": "b5541045591f8589130b1577c50d51d70c3b4337",
}
EXPECTED_CANDIDATE_FILES = {
    "OTP-F-EHRHART.json",
    "staged_certificates/MC-OTP-F-EHRHART-001.json",
    "staged_route_transitions/OTP-F-EHRHART.json",
}
CONTENT_TOKEN = "$CERTIFICATE_CONTENT_COMMIT"
FORBIDDEN_TOKEN = "$PROTECTED_EXECUTION_MERGE"
HEX40 = re.compile(r"^[0-9a-f]{40}$")


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


def future_execution_errors(
    *,
    certificate_content_commit: str,
    exact_execution_head: str,
    certificate_content_commit_is_ancestor: bool,
    certificate_exists_at_content_commit: bool,
    certificate_blob_at_content_commit: str,
    certificate_blob_at_execution_head: str,
    registry_blob_at_content_commit: str,
    route_changed_at_content_commit: bool,
    route_transition_commit_after_content_commit: bool,
    cert_output_commit_sha: str,
    merge_method: str,
    protected_main_publication_atomic: bool,
    protected_main_route_state_before_merge: str,
    protected_main_certificate_present_before_merge: bool,
    protected_main_cert_output_present_before_merge: bool,
    mathematical_target_proved: bool = False,
    equality_case_classified: bool = False,
    other_family_output: bool = False,
    aggregate_output: bool = False,
) -> list[str]:
    errors: list[str] = []
    checks = [
        (not HEX40.fullmatch(certificate_content_commit), "certificate-content commit must be a full Git SHA"),
        (not HEX40.fullmatch(exact_execution_head), "exact execution head must be a full Git SHA"),
        (certificate_content_commit == exact_execution_head, "certificate-content commit must precede the exact execution head"),
        (not certificate_content_commit_is_ancestor, "certificate-content commit is not an ancestor of the exact execution head"),
        (not certificate_exists_at_content_commit, "live certificate path is absent at the certificate-content commit"),
        (certificate_blob_at_content_commit != EXPECTED_BLOBS["staged_certificate"], "certificate blob at content commit is incorrect"),
        (certificate_blob_at_execution_head != EXPECTED_BLOBS["staged_certificate"], "exact execution head does not preserve certificate bytes"),
        (registry_blob_at_content_commit != EXPECTED_BLOBS["routes"], "route registry changed in certificate-content commit"),
        (route_changed_at_content_commit, "route-first or combined content-commit ordering is prohibited"),
        (not route_transition_commit_after_content_commit, "route transition must occur after the certificate-content commit"),
        (cert_output_commit_sha != certificate_content_commit, "cert_output does not point to the certificate-content commit"),
        (merge_method != "merge", "protected execution must use merge-commit method"),
        (not protected_main_publication_atomic, "protected-main certificate/route publication is not atomic"),
        (protected_main_route_state_before_merge != "submitted", "protected-main route changed before protected merge"),
        (protected_main_certificate_present_before_merge, "protected-main certificate appeared before protected merge"),
        (protected_main_cert_output_present_before_merge, "protected-main cert_output appeared before protected merge"),
        (mathematical_target_proved, "mathematical proof status promotion is prohibited"),
        (equality_case_classified, "equality-case classification is prohibited"),
        (other_family_output, "other-family output is prohibited"),
        (aggregate_output, "aggregate output authority is prohibited"),
    ]
    errors.extend(message for failed, message in checks if failed)
    return errors


def validation_errors(
    *,
    candidate: dict[str, Any] | None = None,
    candidate_schema: dict[str, Any] | None = None,
    staged_certificate: dict[str, Any] | None = None,
    transition: dict[str, Any] | None = None,
    transition_schema: dict[str, Any] | None = None,
    future_schema: dict[str, Any] | None = None,
    routes: dict[str, Any] | None = None,
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
    if blobs is None:
        blobs = {
            "candidate": git_blob_sha1(CANDIDATE),
            "candidate_schema": git_blob_sha1(CANDIDATE_SCHEMA),
            "transition": git_blob_sha1(TRANSITION),
            "transition_schema": git_blob_sha1(TRANSITION_SCHEMA),
            "staged_certificate": git_blob_sha1(STAGED_CERTIFICATE),
            "routes": git_blob_sha1(ROUTES),
        }
    live_certificate_present = LIVE_CERTIFICATE.exists() if live_certificate_present is None else live_certificate_present
    candidate_files = actual_candidate_files() if candidate_files is None else candidate_files

    for label, schema, data, expected_id in (
        ("candidate", candidate_schema, candidate, "https://grandchallenge.ai/schemas/otp_ehrhart_output_candidate.schema.json"),
        ("transition", transition_schema, transition, "https://grandchallenge.ai/schemas/otp_ehrhart_atomic_route_transition_template.schema.json"),
    ):
        if schema.get("additionalProperties") is not False:
            errors.append(f"{label} schema must remain closed")
        if schema.get("$id") != expected_id:
            errors.append(f"{label} schema identity drift")
        errors.extend(
            f"{label} schema violation: {error.message}"
            for error in Draft202012Validator(schema).iter_errors(data)
        )
    errors.extend(
        f"staged certificate schema violation: {error.message}"
        for error in Draft202012Validator(future_schema).iter_errors(staged_certificate)
    )
    errors.extend(
        f"{name} blob drift"
        for name, expected in EXPECTED_BLOBS.items()
        if blobs.get(name) != expected
    )
    if candidate_files != EXPECTED_CANDIDATE_FILES:
        errors.append("output-candidate file membership drift")
    if live_certificate_present:
        errors.append("live Cert output exists during correction")

    serialized = json.dumps({"candidate": candidate, "transition": transition}, sort_keys=True)
    if FORBIDDEN_TOKEN in serialized:
        errors.append("protected-merge self-reference remains")
    if CONTENT_TOKEN not in serialized:
        errors.append("certificate-content commit token is missing")

    live_route = next(
        (item for item in routes.get("routes", []) if item.get("route_id") == "MC-ROUTE-OTP-F-EHRHART"),
        None,
    )
    before = transition.get("before", {})
    after = transition.get("after_template", {})
    if live_route is None:
        errors.append("live OTP-F-EHRHART route missing")
    elif live_route != before:
        errors.append("corrected transition before-state does not exactly match live route")
    if not live_route or live_route.get("intake_status") != "submitted" or live_route.get("cert_output") is not None:
        errors.append("live route changed during correction")

    allowed = {"intake_status", "claim_boundary", "cert_output", "blockers", "reopening_conditions"}
    errors.extend(
        f"unauthorized route-field mutation in corrected transition: {key}"
        for key in set(before) | set(after)
        if key not in allowed and before.get(key) != after.get(key)
    )
    output = after.get("cert_output", {})
    if output.get("commit_sha") != CONTENT_TOKEN:
        errors.append("corrected cert_output does not use certificate-content token")
    if output.get("digest") != EXPECTED_BLOBS["staged_certificate"]:
        errors.append("corrected cert_output certificate digest drift")

    binding = transition.get("certificate_content_commit_binding", {})
    if binding.get("unresolved_during_correction") is not True:
        errors.append("certificate-content commit resolved during correction")
    atomicity = transition.get("atomicity", {})
    required = {
        "certificate_content_commit_precedes_route_transition": True,
        "exact_reviewed_head_descends_from_certificate_content_commit": True,
        "protected_merge_method": "merge",
        "squash_merge_prohibited": True,
        "rebase_merge_prohibited": True,
        "protected_main_publishes_certificate_and_route_together": True,
        "partial_protected_main_state_prohibited": True,
    }
    errors.extend(
        f"corrected atomicity drift: {key}"
        for key, expected in required.items()
        if atomicity.get(key) != expected
    )
    if transition.get("execution_sequence", {}).get("route_first_ordering_prohibited") is not True:
        errors.append("route-first ordering is not prohibited")
    if transition.get("candidate_effect") != "none_until_separately_authorized_atomic_execution":
        errors.append("corrected candidate gains premature operative effect")

    qualification = staged_certificate.get("qualification", {})
    state = staged_certificate.get("state", {})
    if qualification.get("source_theorem_mathematically_proved") is not False:
        errors.append("staged certificate promotes source theorem proof")
    if qualification.get("equality_case_classification") != "excluded":
        errors.append("staged certificate inflates equality-case authority")
    if state.get("aggregate_output") is not False:
        errors.append("staged certificate gains aggregate authority")
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(
        "validated corrected non-operative OTP-F-EHRHART candidate, "
        "certificate-content ancestor binding, merge-only publication, "
        "and zero present route/output authority"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
