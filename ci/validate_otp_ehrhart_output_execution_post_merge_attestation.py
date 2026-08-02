#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
ATTESTATION = ROOT / "governance/post_merge_attestations/OTP-F-EHRHART-CERT-OUTPUT-EXEC-001.v1.json"
DOCUMENT = ROOT / "governance/post_merge_attestations/OTP-F-EHRHART-CERT-OUTPUT-EXEC-001.v1.md"
ATTESTATION_SCHEMA = ROOT / "schemas/otp_ehrhart_output_execution_post_merge_attestation.schema.json"
CLOSURE = ROOT / "governance/result_family_output_execution_closures/OTP-F-EHRHART.json"
CLOSURE_SCHEMA = ROOT / "schemas/otp_ehrhart_output_execution_closure.schema.json"
HISTORICAL_CANDIDATE = ROOT / "governance/result_family_output_candidates/OTP-F-EHRHART.json"
ROUTES = ROOT / "governance/certification_routes.json"
CERTIFICATE = ROOT / "certificates/formal_sources/MC-OTP-F-EHRHART-001.json"
ADJUDICATION = ROOT / "governance/result_family_adjudications/OTP-F-EHRHART.json"

EXPECTED = {
    "document": "032f5c1f1f252db5b73305e0974928729c6f7a9c",
    "attestation_schema": "cb570d766334b1a5b81fa51b794cc751e8f6f97e",
    "closure": "c50a397a84873b358a54db2e602058da103b75e8",
    "closure_schema": "4cbd6e6f5aec5dee28ae788975da919dde4fc28f",
    "historical_candidate": "38d6eb4a483387d04c25bd9f6991c54af67bd9c5",
    "routes": "0487c3ebf702229741f16a544d68af25cf994e41",
    "certificate": "27a855c949b67e71372c7f0d6601d80125d33968",
    "adjudication": "dcea25320169b9309ebf6c7f48249df9a312555f",
}
COMMITS = {
    "reviewed_head": "5e1dfee97e952ca38cc9df1c3d3bf12895268378",
    "merge": "1d5b1e6514787005ed75e363df7ea953dcd9391a",
    "certificate_content": "24d99cbdcd6da33ae2404c0f6034d503498d9a4b",
    "route_transition": "94f7e37abe56b9423396c3bc4b9da6c0d64aec51",
}
TARGETS = [
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


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def ensure_commit(commit: str) -> None:
    shallow = git("rev-parse", "--is-shallow-repository")
    if shallow.returncode == 0 and shallow.stdout.strip() == "true":
        result = git("fetch", "--no-tags", "--unshallow", "origin")
        if result.returncode != 0:
            raise RuntimeError("unable to unshallow repository history")
    if git("cat-file", "-e", f"{commit}^{{commit}}").returncode != 0:
        result = git("fetch", "--no-tags", "origin", commit)
        if result.returncode != 0:
            raise RuntimeError(f"unable to fetch governed commit {commit}")


def object_blob(commit: str, path: str) -> str:
    ensure_commit(commit)
    result = git("rev-parse", f"{commit}:{path}")
    if result.returncode != 0:
        raise RuntimeError(f"unable to resolve {path} at {commit}")
    return result.stdout.strip()


def tracked_blob(path: Path) -> str:
    """Return the checked-out Git object identity independent of line endings."""
    return object_blob("HEAD", path.relative_to(ROOT).as_posix())


def is_ancestor(ancestor: str, descendant: str) -> bool:
    ensure_commit(ancestor)
    ensure_commit(descendant)
    return git("merge-base", "--is-ancestor", ancestor, descendant).returncode == 0


def git_receipt() -> dict[str, Any]:
    for commit in COMMITS.values():
        ensure_commit(commit)
    parents_result = git("rev-list", "--parents", "-n", "1", COMMITS["merge"])
    if parents_result.returncode != 0:
        raise RuntimeError("unable to inspect protected merge parents")
    parts = parents_result.stdout.strip().split()
    return {
        "merge_parent_count": max(0, len(parts) - 1),
        "reviewed_head_is_direct_parent": COMMITS["reviewed_head"] in parts[1:],
        "certificate_content_is_ancestor_of_reviewed_head": is_ancestor(
            COMMITS["certificate_content"], COMMITS["reviewed_head"]
        ),
        "route_transition_is_ancestor_of_reviewed_head": is_ancestor(
            COMMITS["route_transition"], COMMITS["reviewed_head"]
        ),
        "reviewed_head_is_ancestor_of_merge": is_ancestor(
            COMMITS["reviewed_head"], COMMITS["merge"]
        ),
        "certificate_blob_at_content_commit": object_blob(
            COMMITS["certificate_content"],
            "certificates/formal_sources/MC-OTP-F-EHRHART-001.json",
        ),
        "route_blob_at_content_commit": object_blob(
            COMMITS["certificate_content"], "governance/certification_routes.json"
        ),
        "route_blob_at_transition_commit": object_blob(
            COMMITS["route_transition"], "governance/certification_routes.json"
        ),
        "certificate_blob_at_merge": object_blob(
            COMMITS["merge"], "certificates/formal_sources/MC-OTP-F-EHRHART-001.json"
        ),
        "route_blob_at_merge": object_blob(
            COMMITS["merge"], "governance/certification_routes.json"
        ),
    }


def validation_errors(
    *,
    attestation: dict[str, Any] | None = None,
    closure: dict[str, Any] | None = None,
    attestation_schema: dict[str, Any] | None = None,
    closure_schema: dict[str, Any] | None = None,
    document_text: str | None = None,
    historical_candidate: dict[str, Any] | None = None,
    routes: dict[str, Any] | None = None,
    certificate: dict[str, Any] | None = None,
    adjudication: dict[str, Any] | None = None,
    blobs: dict[str, str] | None = None,
    receipt: dict[str, Any] | None = None,
    other_adjudication_present: bool | None = None,
) -> list[str]:
    errors: list[str] = []
    attestation = load(ATTESTATION) if attestation is None else attestation
    closure = load(CLOSURE) if closure is None else closure
    attestation_schema = load(ATTESTATION_SCHEMA) if attestation_schema is None else attestation_schema
    closure_schema = load(CLOSURE_SCHEMA) if closure_schema is None else closure_schema
    document_text = DOCUMENT.read_text(encoding="utf-8") if document_text is None else document_text
    historical_candidate = load(HISTORICAL_CANDIDATE) if historical_candidate is None else historical_candidate
    routes = load(ROUTES) if routes is None else routes
    certificate = load(CERTIFICATE) if certificate is None else certificate
    adjudication = load(ADJUDICATION) if adjudication is None else adjudication
    blobs = {
        "document": tracked_blob(DOCUMENT),
        "attestation_schema": tracked_blob(ATTESTATION_SCHEMA),
        "closure": tracked_blob(CLOSURE),
        "closure_schema": tracked_blob(CLOSURE_SCHEMA),
        "historical_candidate": tracked_blob(HISTORICAL_CANDIDATE),
        "routes": tracked_blob(ROUTES),
        "certificate": tracked_blob(CERTIFICATE),
        "adjudication": tracked_blob(ADJUDICATION),
    } if blobs is None else blobs
    receipt = git_receipt() if receipt is None else receipt
    other_adjudication_present = (
        (ROOT / "governance/result_family_adjudications/OTP-J1-COMPACTNESS.json").exists()
        or (ROOT / "governance/result_family_adjudications/OTP-J2-TWO-DEGENERATE.json").exists()
    ) if other_adjudication_present is None else other_adjudication_present

    for name, schema, record in (
        ("attestation", attestation_schema, attestation),
        ("closure", closure_schema, closure),
    ):
        if schema.get("additionalProperties") is not False:
            errors.append(f"{name} schema must remain closed")
        try:
            errors.extend(
                f"{name} schema violation: {error.message}"
                for error in Draft202012Validator(schema).iter_errors(record)
            )
        except Exception as exc:
            errors.append(f"{name} schema is invalid: {exc}")

    if git_blob_sha1_bytes(document_text.encode("utf-8")) != EXPECTED["document"]:
        errors.append("attestation document text drift")
    for key, expected in EXPECTED.items():
        if blobs.get(key) != expected:
            errors.append(f"protected blob drift: {key}")

    branch_state = historical_candidate.get("branch_execution_state", {})
    if branch_state.get("execution_state") != "output_execution_prepared_pending_protected_merge":
        errors.append("historical candidate execution state was rewritten")
    if branch_state.get("protected_main_effect") != "none_until_merge":
        errors.append("historical candidate protected-main effect was rewritten")
    if closure.get("historical_candidate", {}).get("mutation_prohibited") is not True:
        errors.append("closure does not prohibit historical-candidate mutation")
    supersession = closure.get("supersession", {})
    if supersession.get("protected_publication_occurred") is not True:
        errors.append("protected publication is not recorded")
    if supersession.get("supersedes_candidate_state_only") is not True:
        errors.append("successor scope exceeds candidate-state supersession")

    expected_receipt = {
        "merge_parent_count": 2,
        "reviewed_head_is_direct_parent": True,
        "certificate_content_is_ancestor_of_reviewed_head": True,
        "route_transition_is_ancestor_of_reviewed_head": True,
        "reviewed_head_is_ancestor_of_merge": True,
        "certificate_blob_at_content_commit": EXPECTED["certificate"],
        "route_blob_at_content_commit": "cf876f43ae824f965a3aedf411671c110c380028",
        "route_blob_at_transition_commit": EXPECTED["routes"],
        "certificate_blob_at_merge": EXPECTED["certificate"],
        "route_blob_at_merge": EXPECTED["routes"],
    }
    for key, value in expected_receipt.items():
        if receipt.get(key) != value:
            errors.append(f"protected Git receipt drift: {key}")

    route_map = {entry.get("campaign_id"): entry for entry in routes.get("routes", [])}
    ehrhart = route_map.get("OTP-F-EHRHART", {})
    compactness = route_map.get("OTP-J1-COMPACTNESS", {})
    two_deg = route_map.get("OTP-J2-TWO-DEGENERATE", {})
    if ehrhart.get("intake_status") != "qualified":
        errors.append("Ehrhart route is not qualified")
    expected_output = {
        "repository": "grandchallenge/MATHCERT",
        "commit_sha": COMMITS["certificate_content"],
        "path": "certificates/formal_sources/MC-OTP-F-EHRHART-001.json",
        "digest_algorithm": "git_blob_sha1",
        "digest": EXPECTED["certificate"],
    }
    if ehrhart.get("cert_output") != expected_output:
        errors.append("Ehrhart restricted Cert output drift")
    for name, route in (("Compactness", compactness), ("Two-degenerate", two_deg)):
        if route.get("intake_status") != "submitted":
            errors.append(f"{name} route state inflation")
        if route.get("cert_output") is not None:
            errors.append(f"{name} Cert output inserted")
    otp_outputs = [
        route for key, route in route_map.items()
        if isinstance(key, str) and key.startswith("OTP-") and route.get("cert_output") is not None
    ]
    if [route.get("campaign_id") for route in otp_outputs] != ["OTP-F-EHRHART"]:
        errors.append("OTP family output membership drift")
    if other_adjudication_present:
        errors.append("Compactness or Two-degenerate adjudication inserted")

    if certificate.get("certificate_id") != "MC-OTP-F-EHRHART-QUAL-001":
        errors.append("certificate identity drift")
    if certificate.get("qualification", {}).get("disposition") != "qualified_encoded_targets_only":
        errors.append("certificate disposition drift")
    if certificate.get("encoded_targets") != TARGETS:
        errors.append("certificate target membership or order drift")
    state = certificate.get("state", {})
    if state.get("route_state") != "qualified" or state.get("cert_output_inserted") is not True:
        errors.append("certificate current-state drift")
    if state.get("mathematical_target_proved") is not False:
        errors.append("mathematical proof-status promotion")
    if state.get("aggregate_output") is not False:
        errors.append("aggregate output authority inserted")

    if adjudication.get("decision", {}).get("disposition") != "adjudication_clear_encoded_targets_only":
        errors.append("bound adjudication disposition drift")
    if adjudication.get("encoded_targets") != TARGETS:
        errors.append("bound adjudication target drift")

    current = closure.get("current_otp_family_state", {})
    expected_families = [
        {"result_family": "OTP-F-EHRHART", "route_state": "qualified", "adjudication_count": 1, "restricted_cert_output_count": 1},
        {"result_family": "OTP-J1-COMPACTNESS", "route_state": "submitted", "adjudication_count": 0, "restricted_cert_output_count": 0},
        {"result_family": "OTP-J2-TWO-DEGENERATE", "route_state": "submitted", "adjudication_count": 0, "restricted_cert_output_count": 0},
    ]
    if current.get("families") != expected_families:
        errors.append("current OTP family-state reconciliation drift")
    if current.get("aggregate_output_count") != 0:
        errors.append("aggregate output count inflation")
    if current.get("mathematical_targets_marked_proved") != 0:
        errors.append("mathematical target proved count inflation")

    for label, boundary in (
        ("attestation", str(attestation.get("claim_boundary", ""))),
        ("closure", str(closure.get("claim_boundary", ""))),
    ):
        for token in (
            "historical candidate",
            "mathematical_target_proved",
            "all equality cases",
            "whole-document",
            "another result family",
            "aggregate ten-proofs authority",
            "commercial claims",
        ):
            if token not in boundary:
                errors.append(f"{label} claim boundary missing token: {token}")
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(
            f"OTP-F-EHRHART output execution post-merge attestation failed with {len(errors)} error(s)",
            file=sys.stderr,
        )
        return 1
    print(
        "validated OTP-F-EHRHART protected output execution closure, immutable historical candidate, "
        "qualified restricted route, one family output, zero aggregate output, and zero proved targets"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
