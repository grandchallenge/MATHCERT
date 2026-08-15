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
RECORD = ROOT / "governance/result_family_output_candidates/OTP-C-PERMANENT.json"
SCHEMA = ROOT / "schemas/otp_permanent_output_execution.schema.json"
CERTIFICATE = ROOT / "certificates/formal_sources/MC-OTP-C-PERMANENT-001.json"
STAGED_CERTIFICATE = ROOT / "governance/result_family_output_candidates/staged_certificates/MC-OTP-C-PERMANENT-001.json"
STAGED_ROUTE = ROOT / "governance/result_family_output_candidates/staged_route_transitions/OTP-C-PERMANENT.json"
CERTIFICATE_SCHEMA = ROOT / "schemas/otp_permanent_qualified_output.schema.json"
CONTRACT = ROOT / "governance/result_family_output_contracts/OTP-C-PERMANENT.json"
ADJUDICATION = ROOT / "governance/result_family_adjudications/OTP-C-PERMANENT.json"
ROUTES = ROOT / "governance/certification_routes.json"

BASE_COMMIT = "2e2d4509c993b9ae4bd4aaab48ecced429813b83"
CONTENT_COMMIT = "1344220f0f61f9e637c5b1fc668c0a0eb7ab4133"
ROUTE_COMMIT = "48941f6351071c07f9b4685577f98d8bbda03536"
CERT_PATH = "certificates/formal_sources/MC-OTP-C-PERMANENT-001.json"
ROUTES_PATH = "governance/certification_routes.json"
PERMANENT_ROUTE = "MC-ROUTE-OTP-C-PERMANENT-FORMULA"
TARGETS = [
    "PermanentFormulaLowerBound.permanent_divisionFree_formula_logarithmic_lower_bound",
    "PermanentFormulaLowerBound.permanent_rational_formula_logarithmic_lower_bound",
]
EXPECTED = {
    "record": "46d83056721767b8b838bc211da1d582ac2c8d41",
    "schema": "69df466908ae983812f9096f1fc3ff4f74cf2d43",
    "certificate": "ad10c427270cb1c747ebcacbc5c37e4c1ed1df04",
    "staged_route": "cb85830a973e08444554e56703b8103d70e7c958",
    "contract": "b40762d73ecbd5a7f3238e04cc2351e9fdfade2f",
    "adjudication": "233d3e92ceed6654e6f6759718adf32f1b6c5415",
    "certificate_schema": "b3a9f0a10861b44f2fac7ad9094f976041562d0d",
    "routes_before": "4b7f98414958999c8404e30a4a7c0a2a104578da",
    "routes_after": "aa460c1310a7c81b64b88013b7aa4cfdc056f37b",
}
EXPECTED_OUTPUT = {
    "repository": "grandchallenge/MATHCERT",
    "commit_sha": CONTENT_COMMIT,
    "path": CERT_PATH,
    "digest_algorithm": "git_blob_sha1",
    "digest": EXPECTED["certificate"],
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_bytes(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data, usedforsecurity=False).hexdigest()


def git_blob(path: Path) -> str:
    return git_blob_bytes(path.read_bytes())


def git(*args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(["git", *args], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def ensure_history() -> None:
    shallow = git("rev-parse", "--is-shallow-repository")
    if shallow.returncode == 0 and shallow.stdout.decode().strip() == "true":
        result = git("fetch", "--no-tags", "--unshallow", "origin")
        if result.returncode != 0:
            raise RuntimeError("unable to unshallow Permanent output execution history")
    for commit in (BASE_COMMIT, CONTENT_COMMIT, ROUTE_COMMIT):
        if git("cat-file", "-e", f"{commit}^{{commit}}").returncode != 0:
            result = git("fetch", "--no-tags", "origin", commit)
            if result.returncode != 0:
                raise RuntimeError(f"unable to fetch governed commit {commit}")


def object_bytes(commit: str, path: str) -> bytes | None:
    result = git("show", f"{commit}:{path}")
    return result.stdout if result.returncode == 0 else None


def object_blob(commit: str, path: str) -> str | None:
    data = object_bytes(commit, path)
    return git_blob_bytes(data) if data is not None else None


def object_json(commit: str, path: str) -> Any | None:
    data = object_bytes(commit, path)
    return json.loads(data.decode("utf-8")) if data is not None else None


def parent(commit: str) -> str:
    result = git("rev-parse", f"{commit}^")
    return result.stdout.decode().strip() if result.returncode == 0 else ""


def is_ancestor(ancestor: str, descendant: str) -> bool:
    return git("merge-base", "--is-ancestor", ancestor, descendant).returncode == 0


def commit_files(commit: str) -> list[str]:
    result = git("diff-tree", "--no-commit-id", "--name-only", "-r", commit)
    return [x for x in result.stdout.decode().splitlines() if x] if result.returncode == 0 else []


def receipt() -> dict[str, Any]:
    ensure_history()
    head = git("rev-parse", "HEAD").stdout.decode().strip()
    return {
        "head": head,
        "base_is_ancestor": is_ancestor(BASE_COMMIT, head),
        "content_parent": parent(CONTENT_COMMIT),
        "route_parent": parent(ROUTE_COMMIT),
        "content_is_ancestor_of_route": is_ancestor(CONTENT_COMMIT, ROUTE_COMMIT),
        "content_is_ancestor_of_head": is_ancestor(CONTENT_COMMIT, head),
        "route_is_ancestor_of_head": is_ancestor(ROUTE_COMMIT, head),
        "certificate_at_base": object_blob(BASE_COMMIT, CERT_PATH),
        "certificate_at_content": object_blob(CONTENT_COMMIT, CERT_PATH),
        "certificate_at_route": object_blob(ROUTE_COMMIT, CERT_PATH),
        "certificate_at_head": object_blob(head, CERT_PATH),
        "routes_at_content": object_blob(CONTENT_COMMIT, ROUTES_PATH),
        "routes_at_route": object_blob(ROUTE_COMMIT, ROUTES_PATH),
        "routes_at_head": object_blob(head, ROUTES_PATH),
        "routes_json_at_content": object_json(CONTENT_COMMIT, ROUTES_PATH),
        "routes_json_at_route": object_json(ROUTE_COMMIT, ROUTES_PATH),
        "content_files": commit_files(CONTENT_COMMIT),
        "route_files": commit_files(ROUTE_COMMIT),
    }


def permanent_route(routes: dict[str, Any]) -> dict[str, Any]:
    return next((r for r in routes.get("routes", []) if isinstance(r, dict) and r.get("route_id") == PERMANENT_ROUTE), {})


def non_permanent_routes(routes: dict[str, Any]) -> list[dict[str, Any]]:
    return [r for r in routes.get("routes", []) if isinstance(r, dict) and r.get("route_id") != PERMANENT_ROUTE]


def validation_errors(*, record=None, schema=None, certificate=None, staged_certificate=None,
                      staged_route=None, routes=None, history=None, blobs=None) -> list[str]:
    record = load(RECORD) if record is None else record
    schema = load(SCHEMA) if schema is None else schema
    certificate = load(CERTIFICATE) if certificate is None else certificate
    staged_certificate = load(STAGED_CERTIFICATE) if staged_certificate is None else staged_certificate
    staged_route = load(STAGED_ROUTE) if staged_route is None else staged_route
    routes = load(ROUTES) if routes is None else routes
    if history is None:
        try:
            history = receipt()
        except RuntimeError as exc:
            return [str(exc)]
    blobs = blobs or {
        "record": git_blob(RECORD), "schema": git_blob(SCHEMA),
        "certificate": git_blob(CERTIFICATE), "staged_certificate": git_blob(STAGED_CERTIFICATE),
        "staged_route": git_blob(STAGED_ROUTE), "contract": git_blob(CONTRACT),
        "adjudication": git_blob(ADJUDICATION), "certificate_schema": git_blob(CERTIFICATE_SCHEMA),
    }
    errors: list[str] = []

    if schema.get("additionalProperties") is not False:
        errors.append("execution schema must remain closed")
    errors.extend(f"execution schema violation: {e.message}" for e in Draft202012Validator(schema).iter_errors(record))
    for key in ("record", "schema", "certificate", "staged_route", "contract", "adjudication", "certificate_schema"):
        if blobs.get(key) != EXPECTED[key]:
            errors.append(f"{key} blob drift")
    if blobs.get("staged_certificate") != EXPECTED["certificate"]:
        errors.append("staged certificate blob drift")

    cert_schema = load(CERTIFICATE_SCHEMA)
    errors.extend(f"certificate schema violation: {e.message}" for e in Draft202012Validator(cert_schema).iter_errors(certificate))
    if certificate != staged_certificate:
        errors.append("live certificate differs from staged certificate bytes")
    if certificate.get("encoded_targets") != TARGETS:
        errors.append("certificate target scope drift")
    if certificate.get("qualification", {}).get("disposition") != "qualified_encoded_targets_only":
        errors.append("certificate disposition inflation")
    state = certificate.get("state", {})
    if any(state.get(k) is not False for k in ("mathematical_target_proved", "may_promote_claim", "aggregate_output")):
        errors.append("certificate state authority inflation")
    limits = certificate.get("preserved_limitations", {})
    for key in ("circuit_targets_in_scope", "gate_bounds_in_scope", "total_size_consequences_in_scope",
                "unrestricted_source_theorem_proof_claim", "other_family_outputs_authorized",
                "aggregate_openai_ten_proofs_authority"):
        if limits.get(key) is not False:
            errors.append(f"certificate limitation inflated: {key}")
    if limits.get("historical_pdf_byte_equivalence") != "not_established":
        errors.append("historical PDF equivalence inflated")
    text = CERTIFICATE.read_text(encoding="utf-8")
    if CONTENT_COMMIT in text or ROUTE_COMMIT in text:
        errors.append("certificate improperly names publication commit identity")

    route = permanent_route(routes)
    if route.get("intake_status") != "qualified":
        errors.append("Permanent route is not qualified on execution branch")
    if route.get("cert_output") != EXPECTED_OUTPUT:
        errors.append("Permanent route output identity drift")
    if route.get("target_claim_ids") != TARGETS:
        errors.append("Permanent route target drift")
    boundary = str(route.get("claim_boundary", "")).lower()
    for token in ("qualified_encoded_targets_only", "n >= 32", "128/192", "theorem 1.1", "256/384",
                  "historical admitted-pdf byte equivalence", "aggregate openai ten proofs"):
        if token not in boundary:
            errors.append(f"qualified route boundary missing token: {token}")
    blockers = " ".join(route.get("blockers", [])).lower()
    for token in ("permanentrollout", "256/384", "total-leaf/total-vertex",
                  "historical admitted-pdf byte equivalence", "neither encoded mathematical target is marked proved"):
        if token not in blockers:
            errors.append(f"qualified route blockers missing token: {token}")

    transition = staged_route.get("route_transition", {})
    if transition.get("from") != "submitted" or transition.get("to") != "qualified":
        errors.append("staged route transition state drift")
    if transition.get("certificate_content_commit") != CONTENT_COMMIT or transition.get("route_transition_commit") != ROUTE_COMMIT:
        errors.append("staged route transition commit identity drift")
    if transition.get("cert_output") != EXPECTED_OUTPUT:
        errors.append("staged route output identity drift")
    if staged_route.get("protected_main_effect") != "none_until_protected_merge":
        errors.append("staged transition gains premature protected effect")

    if record.get("candidate_state") != "output_candidate_prepared_pending_execution":
        errors.append("candidate state drift")
    commits = record.get("execution_commits", {})
    if commits.get("certificate_content_commit") != CONTENT_COMMIT:
        errors.append("certificate-content commit drift")
    if commits.get("route_transition_commit") != ROUTE_COMMIT:
        errors.append("route-transition commit drift")
    branch = record.get("branch_execution_state", {})
    if branch.get("route_state") != "qualified" or branch.get("cert_output") != EXPECTED_OUTPUT:
        errors.append("branch execution state drift")
    if any(branch.get(k) is not False for k in ("mathematical_target_proved", "may_promote_claim", "aggregate_output")):
        errors.append("branch execution authority inflation")
    if record.get("review_gate", {}).get("recorded_review") is not None:
        errors.append("pre-merge execution record must not prepopulate binding review")
    gate = record.get("publication_gate", {})
    required_true = (
        "exact_head_cert_checks_required", "exact_head_gcl_conformance_required",
        "linux_windows_output_validation_required", "codeql_no_new_alerts_required",
        "fresh_non_author_specialist_approval_required",
        "human_steward_intervention_required_only_for_control_plan_change",
        "squash_merge_prohibited", "rebase_merge_prohibited", "expected_head_required",
        "certificate_content_commit_must_remain_ancestor", "route_transition_commit_must_remain_ancestor",
        "protected_main_atomic_publication_required", "partial_protected_main_state_prohibited",
        "head_change_requires_revalidation_and_reapproval",
    )
    for key in required_true:
        if gate.get(key) is not True:
            errors.append(f"publication gate disabled: {key}")
    if gate.get("separate_human_steward_authorization_required") is not False:
        errors.append("separate Human Steward authorization improperly introduced")
    if gate.get("protected_merge_method") != "merge":
        errors.append("merge-only publication requirement removed")

    for key, message in {
        "base_is_ancestor": "protected output-contract base is not ancestor of exact head",
        "content_is_ancestor_of_route": "certificate-content commit does not precede route transition",
        "content_is_ancestor_of_head": "certificate-content commit is not ancestor of exact head",
        "route_is_ancestor_of_head": "route-transition commit is not ancestor of exact head",
    }.items():
        if history.get(key) is not True:
            errors.append(message)
    if history.get("content_parent") != BASE_COMMIT:
        errors.append("certificate-content commit is not directly based on protected contract merge")
    if history.get("route_parent") != CONTENT_COMMIT:
        errors.append("route-transition commit is not direct descendant of certificate-content commit")
    if history.get("certificate_at_base") is not None:
        errors.append("certificate existed before certificate-content commit")
    for key in ("certificate_at_content", "certificate_at_route", "certificate_at_head"):
        if history.get(key) != EXPECTED["certificate"]:
            errors.append(f"certificate bytes not preserved: {key}")
    if history.get("routes_at_content") != EXPECTED["routes_before"]:
        errors.append("route registry changed in certificate-content commit")
    if history.get("routes_at_route") != EXPECTED["routes_after"]:
        errors.append("historical Permanent route-transition registry bytes drift")
    if history.get("content_files") != [CERT_PATH]:
        errors.append("certificate-content commit scope drift")
    if history.get("route_files") != [ROUTES_PATH]:
        errors.append("route-transition commit scope drift")

    before = history.get("routes_json_at_content") or {}
    after = history.get("routes_json_at_route") or {}
    for key in ("schema_version", "registry_id", "provider_repository", "provider_base_commit", "programme_issue"):
        if before.get(key) != after.get(key):
            errors.append(f"route registry metadata changed during Permanent transition: {key}")
    if non_permanent_routes(before) != non_permanent_routes(after):
        errors.append("non-Permanent routes changed during Permanent route transition")
    before_perm = permanent_route(before)
    if before_perm.get("intake_status") != "submitted" or before_perm.get("cert_output") is not None:
        errors.append("pre-transition Permanent route was not submitted/null")
    if permanent_route(after) != route:
        errors.append("live Permanent route differs from historical transition result")
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"OTP-C-PERMANENT output execution validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    r = receipt()
    print(f"validated certificate-first OTP-C-PERMANENT restricted output execution with independent later route evolution: content {CONTENT_COMMIT}, route {ROUTE_COMMIT}, head {r['head']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
