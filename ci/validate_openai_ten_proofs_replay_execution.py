#!/usr/bin/env python3
"""Validate the submitted OpenAI ten-proofs family replay execution."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RECORD_PATH = ROOT / "governance" / "pre_route_candidates" / "OPENAI_TEN_PROOFS_WP03_REPLAY_EXECUTION.json"
WORK_PACKAGE_REGISTRY = ROOT / "governance" / "pre_route_candidates" / "OPENAI_TEN_PROOFS_WP02_WORK_PACKAGES.json"
ROUTES_PATH = ROOT / "governance" / "certification_routes.json"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "otp-family-replay.yml"
RUNNER_PATH = ROOT / "ci" / "run_openai_ten_proofs_family_replay.sh"
ADAPTER_PATH = ROOT / "ci" / "landrun_comparator_adapter.sh"

EXPECTED_ROUTES_BLOB = "5b3e8d48b9f6c5b03ed3dc439bf9e43876e017b1"
EXPECTED_WP_REGISTRY_BLOB = "997f38fb60ef4d3a43801916113a8e2f1ae34264"
EXPECTED_FAMILIES = [
    {
        "result_family": "OTP-F-EHRHART",
        "tracker_issue": "https://github.com/grandchallenge/MATHCERT/issues/48",
        "config": "ComparatorChallenges/F_EhrhartVolumeInequality.json",
        "solution_module": "EhrhartVolumeInequality",
        "challenge_module": "ComparatorChallenges.F_EhrhartVolumeInequality",
    },
    {
        "result_family": "OTP-J1-COMPACTNESS",
        "tracker_issue": "https://github.com/grandchallenge/MATHCERT/issues/49",
        "config": "ComparatorChallenges/J_CompactnessConjecture.json",
        "solution_module": "CompactnessAndDegeneracy",
        "challenge_module": "ComparatorChallenges.J_CompactnessConjecture",
    },
    {
        "result_family": "OTP-J2-TWO-DEGENERATE",
        "tracker_issue": "https://github.com/grandchallenge/MATHCERT/issues/50",
        "config": "ComparatorChallenges/J_TwoDegenerateGraphs.json",
        "solution_module": "CompactnessAndDegeneracy",
        "challenge_module": "ComparatorChallenges.J_TwoDegenerateGraphs",
    },
]
EXPECTED_TOOLCHAIN = {
    "lean": "4.32.0",
    "comparator": "07bc4ea40f2266dcb861820a2ec1fa3244ed307f",
    "lean4export": "4e7915201d3f9f04470d9eae002fa695f7cdc589",
    "lean4checker": "b7398199245524275543dec6113229c9bb4902e5",
    "landrun": "811cfff51ceaf3d9843708aa6d22e9b84ccac8b4d",
    "nanoda": "ddfac2bf5a7b56cb46e141494427ff3dd55963c7",
}
EXPECTED_SOURCE_REVISION = {
    "status": "source_revision_drift_detected",
    "forge_audit_issue": "https://github.com/grandchallenge/MATHFORGE/issues/52",
    "admitted_manuscript": {
        "bytes": 2266052,
        "sha256": "f318c6508c9d49ef876a5a26cd73928705f96c07bb43e92a0cb35bd3f666ea53",
    },
    "observed_manuscript": {
        "bytes": 2266371,
        "sha256": "64b900d5fae6fe22f2ae1b8e3b712d20055194a6c81cf343a2455e5898ac7dd6",
        "observed_at": "2026-08-02",
    },
    "reasoning_notes": {
        "bytes": 441468,
        "sha256": "13b95999f060c0be2142089cfb8b17b75e9231c3c1f3fa0980445ff1b35f0b3b",
        "status": "byte_identical",
    },
    "current_revision_semantic_concordance": "blocked_pending_forge_audit",
}
REQUESTED_ROUTES = {
    "MC-ROUTE-OTP-F-EHRHART",
    "MC-ROUTE-OTP-J1-COMPACTNESS",
    "MC-ROUTE-OTP-J2-TWO-DEGENERATE",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(data)}\0".encode("ascii") + data,
        usedforsecurity=False,
    ).hexdigest()


def exact_keys(value: Any, keys: set[str], label: str, errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{label}: expected object")
        return {}
    actual = set(value)
    if actual != keys:
        errors.append(f"{label}: key drift: expected {sorted(keys)}, found {sorted(actual)}")
    return value


def validation_errors(
    record: dict[str, Any] | None = None,
    workflow_text: str | None = None,
    runner_text: str | None = None,
    adapter_text: str | None = None,
    routes: dict[str, Any] | None = None,
    routes_blob: str | None = None,
    wp_registry_blob: str | None = None,
) -> list[str]:
    errors: list[str] = []
    record = load_json(RECORD_PATH) if record is None else record
    workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8") if workflow_text is None else workflow_text
    runner_text = RUNNER_PATH.read_text(encoding="utf-8") if runner_text is None else runner_text
    adapter_text = ADAPTER_PATH.read_text(encoding="utf-8") if adapter_text is None else adapter_text
    routes = load_json(ROUTES_PATH) if routes is None else routes
    routes_blob = git_blob_sha1(ROUTES_PATH) if routes_blob is None else routes_blob
    wp_registry_blob = git_blob_sha1(WORK_PACKAGE_REGISTRY) if wp_registry_blob is None else wp_registry_blob

    top = exact_keys(
        record,
        {
            "schema_version", "record_type", "execution_id", "candidate_id",
            "authority", "workflow", "source_revision", "families",
            "execution_state", "route_controls", "claim_boundary",
        },
        "OTP-CERT-REPLAY-001",
        errors,
    )
    expected_scalars = {
        "schema_version": "1.0.0",
        "record_type": "openai_ten_proofs_replay_execution",
        "execution_id": "MC-OTP-CERT-REPLAY-001",
        "candidate_id": "OPENAI-TEN-PROOFS-001",
    }
    for field, expected in expected_scalars.items():
        if top.get(field) != expected:
            errors.append(f"OTP-CERT-REPLAY-001: {field} drift")

    authority = exact_keys(
        top.get("authority"),
        {"work_package_merge", "reviewed_head", "review_id", "reviewer"},
        "OTP-CERT-REPLAY-001.authority",
        errors,
    )
    if authority != {
        "work_package_merge": "677a58a126145977581050bcb5d12d5b6a99fb51",
        "reviewed_head": "ceefe8efe037a0190de745098a37e011b4d170f8",
        "review_id": 4836164204,
        "reviewer": "jimsteeg",
    }:
        errors.append("OTP-CERT-REPLAY-001: protected work-package authority drift")

    workflow = exact_keys(
        top.get("workflow"),
        {"path", "clean_room_matrix", "toolchain"},
        "OTP-CERT-REPLAY-001.workflow",
        errors,
    )
    if workflow.get("path") != ".github/workflows/otp-family-replay.yml":
        errors.append("OTP-CERT-REPLAY-001: workflow path drift")
    if workflow.get("clean_room_matrix") is not True:
        errors.append("OTP-CERT-REPLAY-001: clean-room matrix disabled")
    if workflow.get("toolchain") != EXPECTED_TOOLCHAIN:
        errors.append("OTP-CERT-REPLAY-001: toolchain identity drift")
    if top.get("source_revision") != EXPECTED_SOURCE_REVISION:
        errors.append("OTP-CERT-REPLAY-001: source revision identities or blocked disposition drift")
    if top.get("families") != EXPECTED_FAMILIES:
        errors.append("OTP-CERT-REPLAY-001: family matrix drift")

    if top.get("execution_state") != {
        "state": "submitted_for_exact_head_ci_execution",
        "submitted_family_count": 3,
        "completed_family_count": 0,
        "evidence_bundle_count": 0,
        "proposed_route_count": 0,
        "registered_route_count": 0,
        "adjudication_count": 0,
        "cert_output_count": 0,
        "mathematical_target_proved_count": 0,
    }:
        errors.append("OTP-CERT-REPLAY-001: submitted execution state inflated or drifted")
    if top.get("route_controls") != {
        "global_route_registry_modified": False,
        "aggregate_route_prohibited": True,
        "may_adjudicate": False,
        "may_promote_claim": False,
    }:
        errors.append("OTP-CERT-REPLAY-001: route controls drift")
    if not str(top.get("claim_boundary", "")).strip():
        errors.append("OTP-CERT-REPLAY-001: claim boundary missing")

    required_workflow_tokens = [
        "runs-on: ubuntu-24.04",
        "timeout-minutes: 55",
        "fail-fast: false",
        "MATHCERT_HEAD_SHA:",
        "MATHCERT_WORKFLOW_SHA:",
        "openai/ten-proofs",
        "e62211d28e3a9131950c89caa6542cfe5eff3bca",
        "cb0a203c36a9ef33270d62ab369df7bc27d3b242",
        "443daf537dc7e4ee34ab43aeb01508d9177816ab",
        "grandchallenge/lean-action@aa909e45950f6e5dd89e05dfed6b78e190ed99b8",
        "use-mathlib-cache: false",
        "elan toolchain install leanprover/lean4:v4.32.0",
        "ELAN_TOOLCHAIN=leanprover/lean4:v4.32.0",
        "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02",
        "4e7915201d3f9f04470d9eae002fa695f7cdc589",
        "ddfac2bf5a7b56cb46e141494427ff3dd55963c7",
        "811cfff51ceaf3d9843708aa6d22e9b84ccac8b4d",
        "OTP-F-EHRHART",
        "OTP-J1-COMPACTNESS",
        "OTP-J2-TWO-DEGENERATE",
        "if: always()",
    ]
    for token in required_workflow_tokens:
        if token not in workflow_text:
            errors.append(f"OTP-CERT-REPLAY-001: workflow token missing: {token}")
    for line in workflow_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("uses:") or stripped.startswith("- uses:"):
            ref = stripped.rsplit("@", 1)[-1].split()[0]
            if len(ref) != 40 or any(c not in "0123456789abcdef" for c in ref):
                errors.append(f"OTP-CERT-REPLAY-001: unpinned action: {stripped}")

    required_runner_tokens = [
        "expected_lean_version=\"4.32.0\"",
        "Lean toolchain mismatch",
        ".lake/packages/Lean4Checker",
        "mathcert_head_sha=",
        "workflow_checkout_sha=",
        "lake exe comparator",
        "#print axioms",
        "Nanoda kernel accepts the solution",
        "Lean default kernel accepts the solution",
        "expected_comparator_boundary",
        "source_revision_drift_detected",
        "blocked_pending_forge_audit",
        "https://github.com/grandchallenge/MATHFORGE/issues/52",
        "f318c6508c9d49ef876a5a26cd73928705f96c07bb43e92a0cb35bd3f666ea53",
        "64b900d5fae6fe22f2ae1b8e3b712d20055194a6c81cf343a2455e5898ac7dd6",
        "pending_source_revision_audit_and_exact_head_non_author_specialist_review",
        "aggregate_all_import_used",
        "may_adjudicate",
        "mathematical_target_proved",
        "-not -name 'SHA256SUMS'",
    ]
    for token in required_runner_tokens:
        if token not in runner_text:
            errors.append(f"OTP-CERT-REPLAY-001: runner token missing: {token}")
    if "github_head" in runner_text:
        errors.append("OTP-CERT-REPLAY-001: ambiguous github_head field remains in runner")
    if "exec \"$real_landrun\" \"${prefix[@]}\" -- \"$@\"" not in adapter_text:
        errors.append("OTP-CERT-REPLAY-001: landrun command separator adapter drift")

    if routes_blob != EXPECTED_ROUTES_BLOB:
        errors.append("OTP-CERT-REPLAY-001: global certification route registry changed")
    if wp_registry_blob != EXPECTED_WP_REGISTRY_BLOB:
        errors.append("OTP-CERT-REPLAY-001: protected work-package registry changed")
    route_ids = {
        str(item.get("route_id", ""))
        for item in routes.get("routes", [])
        if isinstance(item, dict)
    }
    premature = sorted(REQUESTED_ROUTES & route_ids)
    if premature:
        errors.append(f"OTP-CERT-REPLAY-001: routes registered prematurely: {premature}")
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"OpenAI ten-proofs replay execution validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print(
        "validated three submitted clean-room formal replays, exact PR-head capture, governed Lean 4.32.0, "
        "complete checker identities, separated manuscript revisions, zero evidence promotion, zero routes, "
        "zero adjudication, and aggregate prohibition"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
