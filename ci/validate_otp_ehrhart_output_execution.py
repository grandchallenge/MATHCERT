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
RECORD = ROOT / "governance/result_family_output_candidates/OTP-F-EHRHART.json"
SCHEMA = ROOT / "schemas/otp_ehrhart_output_candidate.schema.json"
CERTIFICATE = ROOT / "certificates/formal_sources/MC-OTP-F-EHRHART-001.json"
STAGED_CERTIFICATE = ROOT / "governance/result_family_output_candidates/staged_certificates/MC-OTP-F-EHRHART-001.json"
CERTIFICATE_SCHEMA = ROOT / "schemas/otp_ehrhart_qualified_output.schema.json"
ROUTES = ROOT / "governance/certification_routes.json"

BASE_COMMIT = "64e042ddb1147338ad7868a2847715fe7c1c079d"
CONTENT_COMMIT = "24d99cbdcd6da33ae2404c0f6034d503498d9a4b"
ROUTE_COMMIT = "94f7e37abe56b9423396c3bc4b9da6c0d64aec51"
CERT_PATH = "certificates/formal_sources/MC-OTP-F-EHRHART-001.json"
ROUTES_PATH = "governance/certification_routes.json"
EXPECTED = {
    "record": "38d6eb4a483387d04c25bd9f6991c54af67bd9c5",
    "schema": "850f657cfde83f34c1d69d4a219169bbed161711",
    "certificate": "27a855c949b67e71372c7f0d6601d80125d33968",
    "routes_before": "cf876f43ae824f965a3aedf411671c110c380028",
    "routes_after": "0487c3ebf702229741f16a544d68af25cf994e41",
}
TARGETS = [
    "Ehrhart.Volume.ehrhart_volume_inequality_for_sets",
    "Ehrhart.SimplexVolume.exists_centeredBody_sharp",
    "Ehrhart.SimplexVolume.barycenter_centeredSimplex",
    "Ehrhart.SimplexVolume.normalizedVolume_centeredSimplex",
]
COMPACTNESS_TARGETS = [
    "CompactnessConjecture.quantitativeCompactnessCounterexample",
    "CompactnessConjecture.compactnessCounterexample_bigO",
    "CompactnessConjecture.not_erdos_180",
]
COMPACTNESS_OUTPUT = {
    "repository": "grandchallenge/MATHCERT",
    "commit_sha": "9fba5a8e918028ecc2b4d72abc00b3b72a5194f5",
    "path": "certificates/formal_sources/MC-OTP-J1-COMPACTNESS-001.json",
    "digest_algorithm": "git_blob_sha1",
    "digest": "88531e28951854961e86eec0517356999a391759",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_bytes(data: bytes) -> str:
    return hashlib.sha1(
        f"blob {len(data)}\0".encode("ascii") + data,
        usedforsecurity=False,
    ).hexdigest()


def git_blob(path: Path) -> str:
    return git_blob_bytes(path.read_bytes())


def git(*args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args], cwd=ROOT, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=False,
    )


def ensure_history() -> None:
    shallow = git("rev-parse", "--is-shallow-repository")
    if shallow.returncode == 0 and shallow.stdout.decode().strip() == "true":
        result = git("fetch", "--no-tags", "--unshallow", "origin")
        if result.returncode != 0:
            raise RuntimeError("unable to unshallow execution history")
    for commit in (BASE_COMMIT, CONTENT_COMMIT, ROUTE_COMMIT):
        if git("cat-file", "-e", f"{commit}^{{commit}}").returncode != 0:
            result = git("fetch", "--no-tags", "origin", commit)
            if result.returncode != 0:
                raise RuntimeError(f"unable to fetch governed commit {commit}")


def object_blob(commit: str, path: str) -> str | None:
    result = git("show", f"{commit}:{path}")
    return git_blob_bytes(result.stdout) if result.returncode == 0 else None


def is_ancestor(ancestor: str, descendant: str) -> bool:
    return git("merge-base", "--is-ancestor", ancestor, descendant).returncode == 0


def commit_files(commit: str) -> list[str]:
    result = git("diff-tree", "--no-commit-id", "--name-only", "-r", commit)
    if result.returncode != 0:
        return []
    return [line for line in result.stdout.decode().splitlines() if line]


def git_receipt() -> dict[str, Any]:
    ensure_history()
    head = git("rev-parse", "HEAD").stdout.decode().strip()
    return {
        "head": head,
        "base_is_ancestor": is_ancestor(BASE_COMMIT, head),
        "content_is_ancestor_of_route": is_ancestor(CONTENT_COMMIT, ROUTE_COMMIT),
        "content_is_ancestor_of_head": is_ancestor(CONTENT_COMMIT, head),
        "route_is_ancestor_of_head": is_ancestor(ROUTE_COMMIT, head),
        "certificate_at_content": object_blob(CONTENT_COMMIT, CERT_PATH),
        "certificate_at_route": object_blob(ROUTE_COMMIT, CERT_PATH),
        "certificate_at_head": object_blob(head, CERT_PATH),
        "routes_at_content": object_blob(CONTENT_COMMIT, ROUTES_PATH),
        "routes_at_route": object_blob(ROUTE_COMMIT, ROUTES_PATH),
        "routes_at_head": object_blob(head, ROUTES_PATH),
        "content_files": commit_files(CONTENT_COMMIT),
        "route_files": commit_files(ROUTE_COMMIT),
    }


def _compactness_successor_errors(route: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if route.get("target_claim_ids") != COMPACTNESS_TARGETS:
        errors.append("OTP-J1-COMPACTNESS: target drift")
    status = route.get("intake_status")
    output = route.get("cert_output")
    if status == "submitted" and output is None:
        return errors
    if status != "qualified":
        errors.append("OTP-J1-COMPACTNESS: invalid successor route state")
    if output != COMPACTNESS_OUTPUT:
        errors.append("OTP-J1-COMPACTNESS: successor output identity drift")
    boundary = str(route.get("claim_boundary", "")).lower()
    blockers = " ".join(route.get("blockers", [])).lower()
    for token in (
        "qualified_encoded_targets_only",
        "chapter 10",
        "historical",
        "whole-document",
        "aggregate openai ten proofs",
    ):
        if token not in boundary:
            errors.append(f"OTP-J1-COMPACTNESS: successor boundary missing token: {token}")
    for token in (
        "unrestricted chapter 10",
        "historical or stronger",
        "whole-document byte and semantic equivalence",
        "proof body",
    ):
        if token not in blockers:
            errors.append(f"OTP-J1-COMPACTNESS: successor blockers missing token: {token}")
    return errors


def validation_errors(
    *,
    record: dict[str, Any] | None = None,
    schema: dict[str, Any] | None = None,
    certificate: dict[str, Any] | None = None,
    staged_certificate: dict[str, Any] | None = None,
    routes: dict[str, Any] | None = None,
    receipt: dict[str, Any] | None = None,
    blobs: dict[str, str] | None = None,
) -> list[str]:
    record = load(RECORD) if record is None else record
    schema = load(SCHEMA) if schema is None else schema
    certificate = load(CERTIFICATE) if certificate is None else certificate
    staged_certificate = load(STAGED_CERTIFICATE) if staged_certificate is None else staged_certificate
    routes = load(ROUTES) if routes is None else routes
    if receipt is None:
        try:
            receipt = git_receipt()
        except RuntimeError as exc:
            return [str(exc)]
    blobs = blobs or {
        "record": git_blob(RECORD),
        "schema": git_blob(SCHEMA),
        "certificate": git_blob(CERTIFICATE),
        "routes_after": object_blob(ROUTE_COMMIT, ROUTES_PATH),
    }
    errors: list[str] = []

    if schema.get("additionalProperties") is not False:
        errors.append("execution schema must remain closed")
    errors.extend(
        f"execution schema violation: {error.message}"
        for error in Draft202012Validator(schema).iter_errors(record)
    )
    for name in ("record", "schema", "certificate", "routes_after"):
        if blobs.get(name) != EXPECTED[name]:
            errors.append(f"{name} blob drift")

    certificate_schema = load(CERTIFICATE_SCHEMA)
    errors.extend(
        f"certificate schema violation: {error.message}"
        for error in Draft202012Validator(certificate_schema).iter_errors(certificate)
    )
    if certificate != staged_certificate:
        errors.append("live certificate differs from protected staged bytes")
    if certificate.get("encoded_targets") != TARGETS:
        errors.append("certificate target scope drift")
    qualification = certificate.get("qualification", {})
    if qualification.get("disposition") != "qualified_encoded_targets_only":
        errors.append("certificate disposition inflation")
    if qualification.get("source_theorem_mathematically_proved") is not False:
        errors.append("mathematical proof promotion")
    if qualification.get("equality_case_classification") != "excluded":
        errors.append("equality-case classification inflation")
    if certificate.get("state", {}).get("aggregate_output") is not False:
        errors.append("aggregate output inflation")

    route_map = {route.get("campaign_id"): route for route in routes.get("routes", [])}
    ehrhart = route_map.get("OTP-F-EHRHART", {})
    if ehrhart.get("intake_status") != "qualified":
        errors.append("Ehrhart route is not qualified")
    expected_output = {
        "repository": "grandchallenge/MATHCERT",
        "commit_sha": CONTENT_COMMIT,
        "path": CERT_PATH,
        "digest_algorithm": "git_blob_sha1",
        "digest": EXPECTED["certificate"],
    }
    if ehrhart.get("cert_output") != expected_output:
        errors.append("Ehrhart route output identity drift")
    if ehrhart.get("target_claim_ids") != TARGETS:
        errors.append("Ehrhart route target drift")
    uc = route_map.get("UC-001", {})
    if uc.get("intake_status") != "qualified" or uc.get("cert_output", {}).get("digest") != "265c185d6b2b2970dc675729efa3fc4860f29204":
        errors.append("protected UC qualification was not retained")

    compactness = route_map.get("OTP-J1-COMPACTNESS", {})
    errors.extend(_compactness_successor_errors(compactness))
    two_degenerate = route_map.get("OTP-J2-TWO-DEGENERATE", {})
    if two_degenerate.get("intake_status") != "submitted" or two_degenerate.get("cert_output") is not None:
        errors.append("OTP-J2-TWO-DEGENERATE: unauthorized output promotion")
    if "OPENAI-TEN-PROOFS-001" in route_map:
        errors.append("aggregate ten-proofs route inserted")

    if record.get("execution_authorization", {}).get("comment_id") != 5157828756:
        errors.append("execution authorization drift")
    if record.get("execution_commits", {}).get("certificate_content_commit") != CONTENT_COMMIT:
        errors.append("certificate-content commit drift")
    if record.get("execution_commits", {}).get("route_transition_commit") != ROUTE_COMMIT:
        errors.append("route-transition commit drift")
    if record.get("branch_execution_state", {}).get("cert_output") != expected_output:
        errors.append("execution record output drift")
    gate = record.get("publication_gate", {})
    if gate.get("protected_merge_method") != "merge":
        errors.append("merge-only publication requirement removed")
    for key in (
        "squash_merge_prohibited", "rebase_merge_prohibited",
        "expected_head_required", "certificate_content_commit_must_remain_ancestor",
        "protected_main_atomic_publication_required",
        "partial_protected_main_state_prohibited",
    ):
        if gate.get(key) is not True:
            errors.append(f"publication gate disabled: {key}")

    checks = {
        "base_is_ancestor": "protected base is not ancestor of exact head",
        "content_is_ancestor_of_route": "certificate commit does not precede route commit",
        "content_is_ancestor_of_head": "certificate commit is not ancestor of exact head",
        "route_is_ancestor_of_head": "route commit is not ancestor of exact head",
    }
    for key, message in checks.items():
        if receipt.get(key) is not True:
            errors.append(message)
    if receipt.get("certificate_at_content") != EXPECTED["certificate"]:
        errors.append("certificate blob missing at content commit")
    if receipt.get("certificate_at_route") != EXPECTED["certificate"] or receipt.get("certificate_at_head") != EXPECTED["certificate"]:
        errors.append("certificate bytes not preserved")
    if receipt.get("routes_at_content") != EXPECTED["routes_before"]:
        errors.append("route registry changed in certificate-content commit")
    if receipt.get("routes_at_route") != EXPECTED["routes_after"]:
        errors.append("historical Ehrhart route transition drift")
    if receipt.get("content_files") != [CERT_PATH]:
        errors.append("certificate-content commit scope drift")
    if receipt.get("route_files") != [ROUTES_PATH]:
        errors.append("route-transition commit scope drift")

    limitations = record.get("preserved_limitations", {})
    if limitations.get("classification_or_uniqueness_of_all_equality_cases") != "excluded":
        errors.append("equality-case limitation removed")
    if limitations.get("whole_document_semantic_equivalence") != "not_established":
        errors.append("whole-document equivalence inflated")
    if limitations.get("proof_body_compared_in_full") is not False:
        errors.append("proof-body comparison inflated")
    if limitations.get("other_family_outputs_issued") is not False:
        errors.append("historical Ehrhart record was rewritten to claim other-family output")
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"OTP-F-EHRHART execution validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    receipt = git_receipt()
    print(
        "validated historical certificate-first OTP-F-EHRHART execution and exact later Compactness successor: "
        f"content {CONTENT_COMMIT}, route {ROUTE_COMMIT}, head {receipt['head']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
