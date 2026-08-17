from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "governance/result_family_output_candidates/staged_route_transitions/OTP-C-PERMANENT-CIRCUIT.json"
CANDIDATE_HEAD = "9c87c89842387af419e825da18be0070e28a3932"
PREP_HEAD = "809fcbc3704f146fbb9992f03b3b1851ba2fe59b"
CERT_COMMIT = "b90305e91a7162a6dbc017e647d7a2d7272e1eef"
ROUTE_COMMIT = "dffc19e45665790954b0d686da147c73bede84ce"
CERT_PATH = "certificates/formal_sources/MC-OTP-C-PERMANENT-CIRCUIT-001.json"
ROUTE_PATH = "governance/certification_route_overlays/OTP-C-PERMANENT-CIRCUIT.json"
CERT_BLOB = "9d0eb4a83df73440b17cb6809ede5cdcc0a8e385"
ROUTE_BLOB = "29946eeefce2bd9873b3e6265b8d4983a033781d"
REVIEW_ID = "PRR_kwDOSuU7Ic8AAAABJ1A1JQ"
PINNED_COMMITS = (CANDIDATE_HEAD, PREP_HEAD, CERT_COMMIT, ROUTE_COMMIT)
PUBLICATION_CONSTRAINTS = (
    "candidate_review_required_before_execution",
    "certificate_content_commit_before_route_transition",
    "route_transition_direct_child_required",
    "fresh_exact_head_replay_required",
    "fresh_non_author_algebraic_complexity_specialist_approved_review_required",
    "review_must_bind_final_execution_head",
    "head_change_requires_revalidation_and_reapproval",
    "ordinary_ancestry_preserving_merge_required",
    "squash_prohibited",
    "rebase_prohibited",
    "expected_head_required",
    "protected_main_readback_required",
    "partial_publication_prohibited",
)


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def ensure_history() -> None:
    shallow = git("rev-parse", "--is-shallow-repository")
    if shallow.returncode == 0 and shallow.stdout.strip() == "true":
        result = git("fetch", "--no-tags", "--unshallow", "origin")
        if result.returncode != 0:
            raise RuntimeError("unable to unshallow circuit execution history: " + result.stderr.strip())
    for commit in PINNED_COMMITS:
        if git("cat-file", "-e", f"{commit}^{{commit}}").returncode == 0:
            continue
        result = git("fetch", "--no-tags", "origin", commit)
        if result.returncode != 0:
            raise RuntimeError(f"unable to fetch pinned circuit execution commit {commit}: {result.stderr.strip()}")


def changed_paths(commit: str) -> list[str]:
    result = git("diff-tree", "--no-commit-id", "--name-only", "-r", commit)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    return [line for line in result.stdout.splitlines() if line]


def parent(commit: str) -> str:
    result = git("rev-parse", f"{commit}^")
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    return result.stdout.strip()


def blob_at(commit: str, path: str) -> str | None:
    result = git("rev-parse", f"{commit}:{path}")
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def is_ancestor(ancestor: str, descendant: str) -> bool:
    return git("merge-base", "--is-ancestor", ancestor, descendant).returncode == 0


def validation_errors() -> list[str]:
    errors: list[str] = []
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))

    auth = receipt.get("candidate_authorization", {})
    if auth != {
        "reviewed_candidate_head": CANDIDATE_HEAD,
        "reviewer": "jimsteeg",
        "review_id": REVIEW_ID,
        "review_state": "APPROVED",
        "submitted_at": "2026-08-17T21:01:29Z",
        "state": "authorized_for_bounded_output_execution",
    }:
        errors.append("candidate authorization receipt drift")

    if receipt.get("status") != "executed_on_branch_pending_final_review_and_protected_merge":
        errors.append("execution receipt status drift")
    if receipt.get("record_type") != "otp_permanent_circuit_executed_route_transition":
        errors.append("execution receipt record type drift")

    cert = receipt.get("planned_certificate", {})
    if cert.get("certificate_content_commit") != CERT_COMMIT or cert.get("digest") != CERT_BLOB:
        errors.append("certificate execution identity drift")
    route = receipt.get("planned_route_transition", {})
    if route.get("route_transition_commit") != ROUTE_COMMIT or route.get("route_overlay_digest") != ROUTE_BLOB:
        errors.append("route execution identity drift")

    try:
        ensure_history()
        if parent(CERT_COMMIT) != PREP_HEAD:
            errors.append("certificate content commit parent drift")
        if parent(ROUTE_COMMIT) != CERT_COMMIT:
            errors.append("route transition is not direct child of certificate content commit")
        if changed_paths(CERT_COMMIT) != [CERT_PATH]:
            errors.append("certificate content commit path surface drift")
        if changed_paths(ROUTE_COMMIT) != [ROUTE_PATH]:
            errors.append("route transition commit path surface drift")
        if not is_ancestor(CANDIDATE_HEAD, PREP_HEAD):
            errors.append("candidate reviewed head is not ancestor of execution prep head")
        if blob_at(CANDIDATE_HEAD, CERT_PATH) is not None:
            errors.append("live circuit certificate existed at candidate reviewed head")
        if blob_at(CERT_COMMIT, CERT_PATH) != CERT_BLOB:
            errors.append("certificate blob at content commit drift")
        if blob_at(ROUTE_COMMIT, CERT_PATH) != CERT_BLOB:
            errors.append("certificate blob changed during route transition")
        if blob_at(ROUTE_COMMIT, ROUTE_PATH) != ROUTE_BLOB:
            errors.append("qualified route blob at route transition drift")
    except RuntimeError as exc:
        errors.append(f"execution history git inspection failed: {exc}")

    ancestry = receipt.get("execution_ancestry", {})
    if ancestry.get("candidate_reviewed_head") != CANDIDATE_HEAD:
        errors.append("receipt candidate ancestry drift")
    if ancestry.get("execution_prep_head") != PREP_HEAD:
        errors.append("receipt prep ancestry drift")
    if ancestry.get("certificate_content_commit") != CERT_COMMIT:
        errors.append("receipt certificate ancestry drift")
    if ancestry.get("route_transition_commit") != ROUTE_COMMIT:
        errors.append("receipt route ancestry drift")
    if ancestry.get("certificate_commit_changed_paths") != [CERT_PATH]:
        errors.append("receipt certificate path drift")
    if ancestry.get("route_transition_changed_paths") != [ROUTE_PATH]:
        errors.append("receipt route path drift")
    if ancestry.get("route_transition_is_direct_child_of_certificate_commit") is not True:
        errors.append("receipt direct-child assertion lost")

    constraints = receipt.get("publication_constraints", {})
    for key in PUBLICATION_CONSTRAINTS:
        if constraints.get(key) is not True:
            errors.append(f"execution publication constraint removed: {key}")
    if set(constraints) != set(PUBLICATION_CONSTRAINTS):
        errors.append("execution publication constraint membership drift")

    boundary = receipt.get("authority_boundary", {})
    for key in ("mathematical_target_proved", "may_promote_claim", "formula_targets_certified", "aggregate_output"):
        if boundary.get(key) is not False:
            errors.append(f"execution receipt authority inflation: {key}")

    return errors
