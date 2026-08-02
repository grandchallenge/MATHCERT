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
CANDIDATE = ROOT / "governance/result_family_output_candidates/OTP-F-EHRHART.json"
CANDIDATE_SCHEMA = ROOT / "schemas/otp_ehrhart_output_candidate.schema.json"
STAGED_CERTIFICATE = ROOT / "governance/result_family_output_candidates/staged_certificates/MC-OTP-F-EHRHART-001.json"
TRANSITION = ROOT / "governance/result_family_output_candidates/staged_route_transitions/OTP-F-EHRHART.json"
FUTURE_SCHEMA = ROOT / "schemas/otp_ehrhart_qualified_output.schema.json"
LIVE_CERTIFICATE = ROOT / "certificates/formal_sources/MC-OTP-F-EHRHART-001.json"
ROUTES = ROOT / "governance/certification_routes.json"

CONTENT_COMMIT = "7b79b459422951cc6e36feda34c8a6e3d615ef17"
ROUTE_COMMIT = "34b34687ab8960089806a7e57dab7d5db4429ad1"
CORRECTION_MERGE = "686a48bb49015e4b8558bbc83d182f21f8b9e097"
CERT_PATH = "certificates/formal_sources/MC-OTP-F-EHRHART-001.json"
ROUTES_PATH = "governance/certification_routes.json"
EXPECTED_TARGETS = [
    "Ehrhart.Volume.ehrhart_volume_inequality_for_sets",
    "Ehrhart.SimplexVolume.exists_centeredBody_sharp",
    "Ehrhart.SimplexVolume.barycenter_centeredSimplex",
    "Ehrhart.SimplexVolume.normalizedVolume_centeredSimplex",
]
EXPECTED_BLOBS = {
    "candidate": "7637665719df1c93d92934817b73e95cf12c8c30",
    "candidate_schema": "11d3aa8d828c0a7fa8571a576549aa704b7f7961",
    "certificate": "27a855c949b67e71372c7f0d6601d80125d33968",
    "transition": "fd3c39ce2fbb4ba6a62085d6778d9dcb59d8453c",
    "future_schema": "01bef61e1cc58544a3e007e3d74cde2420ec53bf",
    "routes_before": "b5541045591f8589130b1577c50d51d70c3b4337",
    "routes_after": "f4df18d612459af629615fdd36d67dad192a297a",
}
EXPECTED_CANDIDATE_FILES = {
    "OTP-F-EHRHART.json",
    "staged_certificates/MC-OTP-F-EHRHART-001.json",
    "staged_route_transitions/OTP-F-EHRHART.json",
}
ALLOWED_EXECUTION_FILES = {
    CERT_PATH,
    ROUTES_PATH,
    "governance/result_family_output_candidates/OTP-F-EHRHART.json",
    "schemas/otp_ehrhart_output_candidate.schema.json",
    "ci/validate_otp_ehrhart_output_candidate.py",
    "ci/test_otp_ehrhart_output_candidate.py",
    "ci/validate_certification_routes.py",
    "ci/test_validate_certification_routes.py",
    "ci/validate_formal_target_certificates.py",
    "ci/test_formal_target_certificates.py",
    "ci/test_otp_ehrhart_output_contract.py",
    "ci/validate_openai_ten_proofs_route_registrations.py",
    "ci/validate_otp_ehrhart_adjudication.py",
    "ci/validate_human_steward_post_merge_attestation.py",
    "ci/test_human_steward_post_merge_attestation.py",
    "ci/validate_openai_ten_proofs_adjudication_design_with_successors.py",
    "ci/test_openai_ten_proofs_adjudication_contracts.py",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_bytes(payload: bytes) -> str:
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload,
        usedforsecurity=False,
    ).hexdigest()


def git_blob(path: Path) -> str:
    return git_blob_bytes(path.read_bytes())


def run_git(*args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def ensure_history() -> None:
    shallow = run_git("rev-parse", "--is-shallow-repository")
    if shallow.returncode == 0 and shallow.stdout.decode().strip() == "true":
        result = run_git("fetch", "--no-tags", "--unshallow", "origin")
        if result.returncode != 0:
            raise RuntimeError(
                "unable to unshallow repository for execution ancestry validation: "
                + result.stderr.decode(errors="replace")
            )
    for commit in (CORRECTION_MERGE, CONTENT_COMMIT, ROUTE_COMMIT):
        if run_git("cat-file", "-e", f"{commit}^{{commit}}").returncode != 0:
            result = run_git("fetch", "--no-tags", "origin", commit)
            if result.returncode != 0:
                raise RuntimeError(
                    f"unable to fetch governed commit {commit}: "
                    + result.stderr.decode(errors="replace")
                )


def git_object_blob(commit: str, path: str) -> str | None:
    result = run_git("show", f"{commit}:{path}")
    return git_blob_bytes(result.stdout) if result.returncode == 0 else None


def changed_files(commit: str) -> list[str] | None:
    result = run_git("diff-tree", "--no-commit-id", "--name-only", "-r", commit)
    if result.returncode != 0:
        return None
    return [line for line in result.stdout.decode().splitlines() if line]


def diff_files(base: str, head: str) -> list[str] | None:
    result = run_git("diff", "--name-only", base, head)
    if result.returncode != 0:
        return None
    return [line for line in result.stdout.decode().splitlines() if line]


def is_ancestor(ancestor: str, descendant: str) -> bool:
    return run_git("merge-base", "--is-ancestor", ancestor, descendant).returncode == 0


def actual_git_receipt() -> dict[str, Any]:
    ensure_history()
    head_result = run_git("rev-parse", "HEAD")
    head = head_result.stdout.decode().strip() if head_result.returncode == 0 else ""
    return {
        "head": head,
        "content_commit_is_ancestor_of_route_commit": is_ancestor(CONTENT_COMMIT, ROUTE_COMMIT),
        "content_commit_is_ancestor_of_head": is_ancestor(CONTENT_COMMIT, head) if head else False,
        "route_commit_is_ancestor_of_head": is_ancestor(ROUTE_COMMIT, head) if head else False,
        "certificate_blob_at_content_commit": git_object_blob(CONTENT_COMMIT, CERT_PATH),
        "certificate_blob_at_route_commit": git_object_blob(ROUTE_COMMIT, CERT_PATH),
        "certificate_blob_at_head": git_object_blob(head, CERT_PATH) if head else None,
        "registry_blob_at_content_commit": git_object_blob(CONTENT_COMMIT, ROUTES_PATH),
        "registry_blob_at_route_commit": git_object_blob(ROUTE_COMMIT, ROUTES_PATH),
        "content_commit_files": changed_files(CONTENT_COMMIT),
        "route_commit_files": changed_files(ROUTE_COMMIT),
        "execution_changed_files": diff_files(CORRECTION_MERGE, head) if head else None,
    }


def actual_candidate_files() -> set[str]:
    root = CANDIDATE.parent
    return {path.relative_to(root).as_posix() for path in root.rglob("*.json")}


def validation_errors(
    *,
    candidate: dict[str, Any] | None = None,
    candidate_schema: dict[str, Any] | None = None,
    certificate: dict[str, Any] | None = None,
    staged_certificate: dict[str, Any] | None = None,
    transition: dict[str, Any] | None = None,
    future_schema: dict[str, Any] | None = None,
    routes: dict[str, Any] | None = None,
    blobs: dict[str, str] | None = None,
    candidate_files: set[str] | None = None,
    git_receipt: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    candidate = load(CANDIDATE) if candidate is None else candidate
    candidate_schema = load(CANDIDATE_SCHEMA) if candidate_schema is None else candidate_schema
    certificate = load(LIVE_CERTIFICATE) if certificate is None else certificate
    staged_certificate = load(STAGED_CERTIFICATE) if staged_certificate is None else staged_certificate
    transition = load(TRANSITION) if transition is None else transition
    future_schema = load(FUTURE_SCHEMA) if future_schema is None else future_schema
    routes = load(ROUTES) if routes is None else routes
    candidate_files = actual_candidate_files() if candidate_files is None else candidate_files
    if git_receipt is None:
        try:
            git_receipt = actual_git_receipt()
        except RuntimeError as exc:
            return [str(exc)]
    if blobs is None:
        blobs = {
            "candidate": git_blob(CANDIDATE),
            "candidate_schema": git_blob(CANDIDATE_SCHEMA),
            "certificate": git_blob(LIVE_CERTIFICATE),
            "transition": git_blob(TRANSITION),
            "future_schema": git_blob(FUTURE_SCHEMA),
            "routes_after": git_blob(ROUTES),
        }

    if candidate_schema.get("additionalProperties") is not False:
        errors.append("execution schema must remain closed")
    if candidate_schema.get("$id") != "https://grandchallenge.ai/schemas/otp_ehrhart_output_candidate.schema.json":
        errors.append("execution schema identity drift")
    for error in Draft202012Validator(candidate_schema).iter_errors(candidate):
        errors.append(f"execution schema violation: {error.message}")
    for key in ("candidate", "candidate_schema", "certificate", "transition", "future_schema", "routes_after"):
        if blobs.get(key) != EXPECTED_BLOBS[key]:
            errors.append(f"{key} blob drift")
    if candidate_files != EXPECTED_CANDIDATE_FILES:
        errors.append("output execution candidate membership drift")

    for error in Draft202012Validator(future_schema).iter_errors(certificate):
        errors.append(f"live certificate schema violation: {error.message}")
    if certificate != staged_certificate:
        errors.append("live certificate bytes differ from protected staged certificate")
    if certificate.get("encoded_targets") != EXPECTED_TARGETS:
        errors.append("certificate target scope drift")
    qualification = certificate.get("qualification", {})
    if qualification.get("disposition") != "qualified_encoded_targets_only":
        errors.append("certificate disposition inflation")
    if qualification.get("source_theorem_mathematically_proved") is not False:
        errors.append("certificate promotes source theorem proof")
    if qualification.get("equality_case_classification") != "excluded":
        errors.append("certificate equality-case inflation")
    if certificate.get("state") != {
        "route_state": "qualified",
        "cert_output_inserted": True,
        "mathematical_target_proved": False,
        "may_promote_claim": False,
        "aggregate_output": False,
    }:
        errors.append("certificate state inflation")

    route_map = {
        route.get("campaign_id"): route
        for route in routes.get("routes", [])
        if isinstance(route, dict)
    }
    ehrhart = route_map.get("OTP-F-EHRHART")
    expected_route = json.loads(json.dumps(transition.get("after_template", {})))
    if expected_route.get("cert_output"):
        expected_route["cert_output"]["commit_sha"] = CONTENT_COMMIT
    if ehrhart != expected_route:
        errors.append("live OTP-F-EHRHART route differs from authorized transition")
    if ehrhart and ehrhart.get("target_claim_ids") != EXPECTED_TARGETS:
        errors.append("live route target scope drift")
    otp_outputs = [
        route.get("campaign_id")
        for route in routes.get("routes", [])
        if str(route.get("campaign_id", "")).startswith("OTP-")
        and route.get("cert_output") is not None
    ]
    if otp_outputs != ["OTP-F-EHRHART"]:
        errors.append("OTP output membership drift")
    for family in ("OTP-J1-COMPACTNESS", "OTP-J2-TWO-DEGENERATE"):
        route = route_map.get(family, {})
        if route.get("intake_status") != "submitted" or route.get("cert_output") is not None:
            errors.append(f"{family}: unauthorized route/output promotion")
    if "OPENAI-TEN-PROOFS-001" in route_map:
        errors.append("aggregate ten-proofs route inserted")

    if candidate.get("execution_authorization", {}).get("comment_id") != 5157828756:
        errors.append("Human Steward execution authorization drift")
    if candidate.get("execution_commits", {}).get("certificate_content_commit") != CONTENT_COMMIT:
        errors.append("certificate-content commit drift")
    if candidate.get("execution_commits", {}).get("route_transition_commit") != ROUTE_COMMIT:
        errors.append("route-transition commit drift")
    if candidate.get("branch_execution_state", {}).get("cert_output") != expected_route.get("cert_output"):
        errors.append("execution record cert_output drift")
    if candidate.get("branch_execution_state", {}).get("protected_main_effect") != "none_until_merge":
        errors.append("execution record claims premature protected effect")
    gate = candidate.get("publication_gate", {})
    if gate.get("protected_merge_method") != "merge":
        errors.append("merge-commit publication requirement removed")
    for key in (
        "squash_merge_prohibited",
        "rebase_merge_prohibited",
        "expected_head_required",
        "certificate_content_commit_must_remain_ancestor",
        "protected_main_atomic_publication_required",
        "partial_protected_main_state_prohibited",
    ):
        if gate.get(key) is not True:
            errors.append(f"publication gate disabled: {key}")

    if not git_receipt.get("content_commit_is_ancestor_of_route_commit"):
        errors.append("certificate-content commit is not ancestor of route-transition commit")
    if not git_receipt.get("content_commit_is_ancestor_of_head"):
        errors.append("certificate-content commit is not ancestor of exact head")
    if not git_receipt.get("route_commit_is_ancestor_of_head"):
        errors.append("route-transition commit is not ancestor of exact head")
    if git_receipt.get("certificate_blob_at_content_commit") != EXPECTED_BLOBS["certificate"]:
        errors.append("certificate blob missing or altered at content commit")
    if git_receipt.get("certificate_blob_at_route_commit") != EXPECTED_BLOBS["certificate"]:
        errors.append("certificate blob not preserved at route-transition commit")
    if git_receipt.get("certificate_blob_at_head") != EXPECTED_BLOBS["certificate"]:
        errors.append("certificate blob not preserved at exact head")
    if git_receipt.get("registry_blob_at_content_commit") != EXPECTED_BLOBS["routes_before"]:
        errors.append("route registry changed in certificate-content commit")
    if git_receipt.get("registry_blob_at_route_commit") != EXPECTED_BLOBS["routes_after"]:
        errors.append("route-transition commit registry blob drift")
    if git_receipt.get("content_commit_files") != [CERT_PATH]:
        errors.append("certificate-content commit changes files outside the certificate path")
    if git_receipt.get("route_commit_files") != [ROUTES_PATH]:
        errors.append("route-transition commit changes files outside the route registry")
    changed = git_receipt.get("execution_changed_files")
    if not isinstance(changed, list):
        errors.append("unable to enumerate execution-branch changes")
    elif set(changed) - ALLOWED_EXECUTION_FILES:
        errors.append("execution branch contains unauthorized changed files")

    limitations = candidate.get("preserved_limitations", {})
    if limitations.get("classification_or_uniqueness_of_all_equality_cases") != "excluded":
        errors.append("equality-case exclusion removed")
    if limitations.get("whole_document_semantic_equivalence") != "not_established":
        errors.append("whole-document equivalence inflated")
    if limitations.get("proof_body_compared_in_full") is not False:
        errors.append("proof-body comparison inflated")
    if limitations.get("other_family_outputs_issued") is not False:
        errors.append("other-family output admitted")
    boundary = str(candidate.get("claim_boundary", ""))
    for token in (
        "does not independently prove",
        "equality cases",
        "whole-document",
        "another result family",
        "aggregate ten-proofs authority",
        "commercial claims",
        "Mathematical target proved remains false",
    ):
        if token not in boundary:
            errors.append(f"claim boundary missing token: {token}")
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"OTP-F-EHRHART execution validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    head = actual_git_receipt().get("head")
    print(
        "validated OTP-F-EHRHART certificate-first execution, exact ancestor commit "
        f"{CONTENT_COMMIT}, later route transition {ROUTE_COMMIT}, and exact head {head}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
