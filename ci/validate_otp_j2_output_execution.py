#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

import validate_otp_j2_route_target_successor as j2

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "governance/result_family_output_candidates/OTP-J2-TWO-DEGENERATE.json"
SCHEMA = ROOT / "schemas/otp_j2_source_faithful_output_execution.schema.json"
CERT = ROOT / "certificates/formal_sources/MC-OTP-J2-TWO-DEGENERATE-001.json"
STAGED_CERT = ROOT / "governance/result_family_output_candidates/staged_certificates/MC-OTP-J2-TWO-DEGENERATE-001.json"
STAGED_ROUTE = ROOT / "governance/result_family_output_candidates/staged_route_transitions/OTP-J2-TWO-DEGENERATE.json"
CERT_SCHEMA = ROOT / "schemas/otp_j2_source_faithful_qualified_output.schema.json"
CONTRACT = ROOT / "governance/result_family_output_contracts/OTP-J2-TWO-DEGENERATE.json"
ADJUDICATION = ROOT / "governance/result_family_adjudications/OTP-J2-TWO-DEGENERATE.json"
ROUTES = ROOT / "governance/certification_routes.json"

BASE = "d1f0d69e145029e8b7bc29c0ec60543f7db29272"
CONTENT = "24cff6e55709c067c7f966c1a533255af707bec0"
ROUTE = "15559390e2489ae73d872f389a9601c7412b77ed"
CERT_PATH = "certificates/formal_sources/MC-OTP-J2-TWO-DEGENERATE-001.json"
ROUTES_PATH = "governance/certification_routes.json"
ROUTE_ID = "MC-ROUTE-OTP-J2-TWO-DEGENERATE"
TARGETS = [
    "TwoDegenerateGraphs.mathcert_sourceFaithfulTwoDegenerateExtremalCounterexample",
    "TwoDegenerateGraphs.mathcert_sourceFaithfulNotErdos146",
]
EXPECTED = {
    "record": "721a3e882e7d405ee9842b9433a060ffefd78647",
    "schema": "66815b82ba8c0b64028529d9021c3fd9e52a34af",
    "certificate": "308a2eb7087fb24a07a6ae8c93a83b593468d2f7",
    "staged_route": "f3b5ad53eb95e36c584f48565d1ce65b7806b6d1",
    "contract": "4f5a03ff588cd6890c45482cf2d77522dc70756d",
    "adjudication": "87286722951770b3383de2eedba30f2b53e0dabc",
    "certificate_schema": "94656e2aaf651ce2cfc56574929b13a28ce50cd2",
    "routes_before": "eb2ad35f73ec1f7a29c7432aa9e5ad299116dbfe",
    "routes_after": "2d17473b4731aa9d9c630b1e7777ad4bd794d993",
}
EXPECTED_OUTPUT = {
    "repository": "grandchallenge/MATHCERT",
    "commit_sha": CONTENT,
    "path": CERT_PATH,
    "digest_algorithm": "git_blob_sha1",
    "digest": EXPECTED["certificate"],
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def blob_bytes(data: bytes) -> str:
    return hashlib.sha1(
        f"blob {len(data)}\0".encode("ascii") + data,
        usedforsecurity=False,
    ).hexdigest()


def blob(path: Path) -> str:
    return blob_bytes(path.read_bytes())


def git(*args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def ensure_history() -> None:
    shallow = git("rev-parse", "--is-shallow-repository").stdout.decode().strip()
    if shallow == "true":
        if git("fetch", "--no-tags", "--unshallow", "origin").returncode:
            raise RuntimeError("unable to unshallow J2 output-execution history")
    for commit in (BASE, CONTENT, ROUTE):
        if git("cat-file", "-e", f"{commit}^{{commit}}").returncode:
            if git("fetch", "--no-tags", "origin", commit).returncode:
                raise RuntimeError(f"unable to fetch governed J2 commit {commit}")


def obj(commit: str, path: str) -> bytes | None:
    result = git("show", f"{commit}:{path}")
    return result.stdout if result.returncode == 0 else None


def obj_blob(commit: str, path: str) -> str | None:
    data = obj(commit, path)
    return blob_bytes(data) if data is not None else None


def obj_json(commit: str, path: str) -> Any:
    data = obj(commit, path)
    return json.loads(data.decode("utf-8")) if data is not None else None


def parent(commit: str) -> str:
    result = git("rev-parse", f"{commit}^")
    return result.stdout.decode().strip() if result.returncode == 0 else ""


def ancestor(older: str, newer: str) -> bool:
    return git("merge-base", "--is-ancestor", older, newer).returncode == 0


def files(commit: str) -> list[str]:
    result = git("diff-tree", "--no-commit-id", "--name-only", "-r", commit)
    return result.stdout.decode().splitlines() if result.returncode == 0 else []


def route_of(routes: dict[str, Any]) -> dict[str, Any]:
    return next(
        (route for route in routes.get("routes", []) if route.get("route_id") == ROUTE_ID),
        {},
    )


def others(routes: dict[str, Any]) -> list[dict[str, Any]]:
    return [route for route in routes.get("routes", []) if route.get("route_id") != ROUTE_ID]


def receipt() -> dict[str, Any]:
    ensure_history()
    head = git("rev-parse", "HEAD").stdout.decode().strip()
    return {
        "head": head,
        "base_ancestor": ancestor(BASE, head),
        "content_parent": parent(CONTENT),
        "route_parent": parent(ROUTE),
        "content_route": ancestor(CONTENT, ROUTE),
        "content_head": ancestor(CONTENT, head),
        "route_head": ancestor(ROUTE, head),
        "cert_base": obj_blob(BASE, CERT_PATH),
        "cert_content": obj_blob(CONTENT, CERT_PATH),
        "cert_route": obj_blob(ROUTE, CERT_PATH),
        "cert_head": obj_blob(head, CERT_PATH),
        "routes_base": obj_blob(BASE, ROUTES_PATH),
        "routes_content": obj_blob(CONTENT, ROUTES_PATH),
        "routes_route": obj_blob(ROUTE, ROUTES_PATH),
        "routes_head": obj_blob(head, ROUTES_PATH),
        "json_content": obj_json(CONTENT, ROUTES_PATH),
        "json_route": obj_json(ROUTE, ROUTES_PATH),
        "content_files": files(CONTENT),
        "route_files": files(ROUTE),
    }


def validation_errors(
    *,
    record: dict[str, Any] | None = None,
    schema: dict[str, Any] | None = None,
    certificate: dict[str, Any] | None = None,
    staged_certificate: dict[str, Any] | None = None,
    staged_route: dict[str, Any] | None = None,
    routes: dict[str, Any] | None = None,
    history: dict[str, Any] | None = None,
    blobs: dict[str, str] | None = None,
) -> list[str]:
    record = load(RECORD) if record is None else record
    schema = load(SCHEMA) if schema is None else schema
    certificate = load(CERT) if certificate is None else certificate
    staged_certificate = load(STAGED_CERT) if staged_certificate is None else staged_certificate
    staged_route = load(STAGED_ROUTE) if staged_route is None else staged_route
    routes = load(ROUTES) if routes is None else routes

    if history is None:
        try:
            history = receipt()
        except RuntimeError as exc:
            return [str(exc)]

    if blobs is None:
        blobs = {
            "record": blob(RECORD),
            "schema": blob(SCHEMA),
            "certificate": blob(CERT),
            "staged_certificate": blob(STAGED_CERT),
            "staged_route": blob(STAGED_ROUTE),
            "contract": blob(CONTRACT),
            "adjudication": blob(ADJUDICATION),
            "certificate_schema": blob(CERT_SCHEMA),
            "routes_after": blob(ROUTES),
        }

    errors: list[str] = []

    if schema.get("additionalProperties") is not False:
        errors.append("J2 output-execution schema must remain closed")
    errors.extend(
        f"J2 output-execution schema violation: {error.message}"
        for error in Draft202012Validator(schema).iter_errors(record)
    )

    for key in (
        "record",
        "schema",
        "certificate",
        "staged_route",
        "contract",
        "adjudication",
        "certificate_schema",
        "routes_after",
    ):
        if blobs.get(key) != EXPECTED[key]:
            errors.append(f"J2 {key} blob drift")
    if blobs.get("staged_certificate") != EXPECTED["certificate"]:
        errors.append("J2 staged certificate blob drift")

    cert_schema = load(CERT_SCHEMA)
    errors.extend(
        f"J2 certificate schema violation: {error.message}"
        for error in Draft202012Validator(cert_schema).iter_errors(certificate)
    )
    if certificate != staged_certificate:
        errors.append("live J2 certificate differs from staged certificate")
    if certificate.get("encoded_targets") != TARGETS:
        errors.append("J2 certificate target drift")
    if certificate.get("qualification", {}).get("disposition") != "qualified_source_faithful_targets_only":
        errors.append("J2 certificate disposition drift")
    projection = certificate.get("qualification", {}).get("source_projection", {})
    if projection.get("stronger_coloring_side_property_in_scope") is not False:
        errors.append("J2 certificate reintroduced stronger coloring-side scope")
    cert_state = certificate.get("state", {})
    for key in (
        "mathematical_target_proved",
        "may_promote_claim",
        "stronger_coloring_property_certified",
        "aggregate_output",
    ):
        if cert_state.get(key) is not False:
            errors.append(f"J2 certificate authority inflation: {key}")
    cert_text = CERT.read_text(encoding="utf-8")
    if CONTENT in cert_text or ROUTE in cert_text:
        errors.append("J2 certificate improperly names publication commits")

    route = route_of(routes)
    if route.get("intake_status") != "qualified":
        errors.append("J2 live route is not qualified")
    if route.get("cert_output") != EXPECTED_OUTPUT:
        errors.append("J2 live route output identity drift")
    if route.get("target_claim_ids") != TARGETS:
        errors.append("J2 live route target drift")
    boundary = str(route.get("claim_boundary", "")).lower()
    blockers = " ".join(route.get("blockers", [])).lower()
    for token in (
        "qualified_source_faithful_targets_only",
        "chapter 10",
        "historical stronger",
        "stronger coloring-side",
        "aggregate openai ten proofs",
    ):
        if token not in boundary:
            errors.append(f"J2 qualified route boundary missing {token}")
    for token in (
        "unrestricted chapter 10",
        "historical stronger declarations",
        "stronger coloring-side property",
        "whole-document byte and semantic equivalence",
        "proof body",
    ):
        if token not in blockers:
            errors.append(f"J2 qualified route blockers missing {token}")

    transition = staged_route.get("route_transition", {})
    if transition.get("from") != "submitted" or transition.get("to") != "qualified":
        errors.append("J2 staged route state transition drift")
    if transition.get("certificate_content_commit") != CONTENT:
        errors.append("J2 staged certificate-content commit drift")
    if transition.get("route_transition_commit") != ROUTE:
        errors.append("J2 staged route-transition commit drift")
    if transition.get("cert_output") != EXPECTED_OUTPUT:
        errors.append("J2 staged Cert-output identity drift")

    execution = record.get("execution_commits", {})
    if execution.get("protected_base") != BASE:
        errors.append("J2 execution protected base drift")
    if execution.get("certificate_content_commit") != CONTENT:
        errors.append("J2 execution certificate-content commit drift")
    if execution.get("route_transition_commit") != ROUTE:
        errors.append("J2 execution route-transition commit drift")

    branch = record.get("branch_execution_state", {})
    if branch.get("route_state") != "qualified" or branch.get("cert_output") != EXPECTED_OUTPUT:
        errors.append("J2 branch execution state drift")
    for key in (
        "mathematical_target_proved",
        "may_promote_claim",
        "stronger_coloring_property_certified",
        "aggregate_output",
    ):
        if branch.get(key) is not False:
            errors.append(f"J2 branch authority inflation: {key}")
    if record.get("review_gate", {}).get("recorded_review") is not None:
        errors.append("J2 execution review prepopulation")

    gate = record.get("publication_gate", {})
    for key in (
        "exact_head_cert_checks_required",
        "exact_head_gcl_conformance_required",
        "linux_windows_output_validation_required",
        "codeql_no_new_alerts_required",
        "fresh_non_author_specialist_approval_required",
        "human_steward_intervention_required_only_for_control_plan_change",
        "squash_merge_prohibited",
        "rebase_merge_prohibited",
        "expected_head_required",
        "certificate_content_commit_must_remain_ancestor",
        "route_transition_commit_must_remain_ancestor",
        "protected_main_atomic_publication_required",
        "partial_protected_main_state_prohibited",
        "head_change_requires_revalidation_and_reapproval",
    ):
        if gate.get(key) is not True:
            errors.append(f"J2 publication gate disabled: {key}")
    if gate.get("separate_human_steward_authorization_required") is not False:
        errors.append("J2 execution reintroduced redundant Human Steward gate")
    if gate.get("protected_merge_method") != "merge":
        errors.append("J2 protected merge method drift")

    for key, message in (
        ("base_ancestor", "protected J2 output-contract merge is not ancestor of execution head"),
        ("content_route", "J2 certificate commit does not precede route transition"),
        ("content_head", "J2 certificate commit is not ancestor of execution head"),
        ("route_head", "J2 route-transition commit is not ancestor of execution head"),
    ):
        if history.get(key) is not True:
            errors.append(message)
    if history.get("content_parent") != BASE:
        errors.append("J2 certificate-content commit is not direct child of protected base")
    if history.get("route_parent") != CONTENT:
        errors.append("J2 route-transition commit is not direct child of certificate-content commit")
    if history.get("cert_base") is not None:
        errors.append("J2 certificate existed at protected execution base")
    for key in ("cert_content", "cert_route", "cert_head"):
        if history.get(key) != EXPECTED["certificate"]:
            errors.append(f"J2 certificate bytes drift: {key}")
    if history.get("routes_base") != EXPECTED["routes_before"]:
        errors.append("J2 protected-base route registry drift")
    if history.get("routes_content") != EXPECTED["routes_before"]:
        errors.append("J2 route registry changed in certificate-content commit")
    if history.get("routes_route") != EXPECTED["routes_after"]:
        errors.append("J2 route-transition registry bytes drift")
    if history.get("routes_head") != EXPECTED["routes_after"]:
        errors.append("J2 route registry changed after route-transition commit")
    if history.get("content_files") != [CERT_PATH]:
        errors.append("J2 certificate-content commit changed paths outside certificate")
    if history.get("route_files") != [ROUTES_PATH]:
        errors.append("J2 route-transition commit changed paths outside route registry")

    before = history.get("json_content") or {}
    after = history.get("json_route") or {}
    if others(before) != others(after):
        errors.append("non-J2 route changed in J2 route-transition commit")
    before_route = route_of(before)
    after_route = route_of(after)
    if before_route.get("intake_status") != "submitted" or before_route.get("cert_output") is not None:
        errors.append("pre-transition J2 route is not submitted/null")
    if before_route.get("target_claim_ids") != TARGETS:
        errors.append("pre-transition J2 target set drift")
    if after_route.get("intake_status") != "qualified" or after_route.get("cert_output") != EXPECTED_OUTPUT:
        errors.append("post-transition J2 route is not qualified/exact-output")
    if after_route.get("target_claim_ids") != TARGETS:
        errors.append("post-transition J2 target set drift")

    # Preserve the historical route-target-successor proof against the exact
    # pre-output route snapshot rather than weakening that old validator.
    errors.extend(j2.validation_errors(routes=copy.deepcopy(before), check_files=True))

    limitations = record.get("preserved_limitations", {})
    for key in (
        "historical_stronger_targets_qualified",
        "stronger_coloring_property_source_authorized",
        "stronger_coloring_property_certified",
        "proof_body_compared_in_full",
        "source_internal_entropy_lemmas_reformalized",
        "unrestricted_source_theorem_proof_claim",
        "other_family_outputs_authorized",
        "aggregate_openai_ten_proofs_authority",
    ):
        if limitations.get(key) is not False:
            errors.append(f"J2 execution limitation inflated: {key}")
    if limitations.get("whole_document_byte_equivalence") != "not_established":
        errors.append("J2 execution whole-document byte equivalence inflated")
    if limitations.get("whole_document_semantic_equivalence") != "not_established":
        errors.append("J2 execution whole-document semantic equivalence inflated")

    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(
            f"OTP-J2-TWO-DEGENERATE output execution failed with {len(errors)} error(s)",
            file=sys.stderr,
        )
        return 1
    print(
        "validated certificate-first OTP-J2-TWO-DEGENERATE restricted source-faithful "
        f"output execution: content {CONTENT}, route {ROUTE}; historical route-target "
        "successor preserved against exact pre-output snapshot"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
