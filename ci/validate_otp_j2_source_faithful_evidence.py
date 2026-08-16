#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "governance/result_family_construction_evidence/OTP-J2-TWO-DEGENERATE.json"
SCHEMA = ROOT / "schemas/openai_ten_proofs_j2_source_faithful_evidence.schema.json"
ROUTES = ROOT / "governance/certification_routes.json"

EXPECTED = {
    "route_blob": "bc4640661443f1b3de213aaa82a333a4fdb6849b",
    "scope_repair_blob": "5884bc57ba4e9c1d4576b96793f7e78009223b15",
    "source_blob": "956320bfc94760d408c7f1a6af9bb6a8e8e1d1fc",
    "recon_blob": "3905455458f247b768353bc0b082ecbf7c8dd0ff",
    "ledger_blob": "0d81c00d9d190e92ed6f30de867e940bc03b2237",
    "projection_blob": "ac1ec20e95d6acbcd1c3a111afe28bca92a43377",
    "runtime_run": 31921405987,
    "runtime_artifact": 9256527089,
    "runtime_digest": "7a004143eeb0f6f66c1dc6713f245a2f48959a6340fe9fd823dbc75edd151d12",
    "runtime_head": "4eadd7a73c58b9125598dd808e91bc1b53e68be1",
}
HISTORICAL_TARGETS = [
    "TwoDegenerateGraphs.twoDegenerateExtremalCounterexample",
    "TwoDegenerateGraphs.not_erdos_146",
]
EVIDENCE_SUBJECTS = [
    "TwoDegenerateGraphs.mathcert_sourceFaithfulTwoDegenerateExtremalCounterexample",
    "TwoDegenerateGraphs.mathcert_sourceFaithfulNotErdos146",
]
OBJECTS = {
    "governance/certification_routes.json": EXPECTED["route_blob"],
    "governance/result_family_scope_repairs/OTP-J2-TWO-DEGENERATE.json": EXPECTED["scope_repair_blob"],
    "evidence/openai_ten_proofs/two_degenerate_construction/source_authority.json": EXPECTED["source_blob"],
    "evidence/openai_ten_proofs/two_degenerate_construction/reconstruction.json": EXPECTED["recon_blob"],
    "evidence/openai_ten_proofs/two_degenerate_construction/proof_dependency_ledger.json": EXPECTED["ledger_blob"],
    "evidence/openai_ten_proofs/two_degenerate_scope_repair/SourceFaithfulProjection.lean": EXPECTED["projection_blob"],
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args],
        capture_output=True,
        text=True,
        check=check,
    )


def repo_blob(rel: str) -> str:
    return git("rev-parse", f"HEAD:{rel}").stdout.strip()


def is_ancestor(older: str, newer: str = "HEAD") -> bool:
    return git("merge-base", "--is-ancestor", older, newer, check=False).returncode == 0


def find_route(node: Any, route_id: str) -> dict[str, Any] | None:
    if isinstance(node, dict):
        if node.get("route_id") == route_id:
            return node
        for value in node.values():
            hit = find_route(value, route_id)
            if hit is not None:
                return hit
    elif isinstance(node, list):
        for value in node:
            hit = find_route(value, route_id)
            if hit is not None:
                return hit
    return None


def route_targets(route: dict[str, Any]) -> list[str] | None:
    for key in ("target_claim_ids", "target_theorems", "target_ids", "lean_theorems", "targets"):
        value = route.get(key)
        if isinstance(value, list) and all(isinstance(x, str) for x in value):
            return value
    for value in route.values():
        if isinstance(value, dict):
            hit = route_targets(value)
            if hit is not None:
                return hit
    return None


def validation_errors(
    record: dict[str, Any] | None = None,
    routes: dict[str, Any] | None = None,
    check_files: bool = True,
) -> list[str]:
    errors: list[str] = []
    record = load(RECORD) if record is None else record
    routes = load(ROUTES) if routes is None else routes
    schema = load(SCHEMA)

    try:
        Draft202012Validator.check_schema(schema)
    except Exception as exc:
        errors.append(f"invalid closed J2 evidence schema: {exc}")
    else:
        for err in Draft202012Validator(schema).iter_errors(record):
            errors.append(f"closed-schema violation: {err.message}")

    if record.get("evidence_subjects") != EVIDENCE_SUBJECTS:
        errors.append("source-faithful evidence subject drift")
    if record.get("historical_registered_targets") != HISTORICAL_TARGETS:
        errors.append("historical target drift")

    runtime = record.get("fresh_runtime_replay", {})
    exact_runtime = {
        "status": "clear",
        "workflow_run_id": EXPECTED["runtime_run"],
        "artifact_id": EXPECTED["runtime_artifact"],
        "artifact_sha256": EXPECTED["runtime_digest"],
        "execution_head": EXPECTED["runtime_head"],
        "comparator": "pass_derivation_carrier_only",
        "lean_kernel": "accept",
        "nanoda": "accept",
        "source_faithful_projection": "accept",
        "dependency_separation": "accept",
        "theorem_axiom_report": "permitted_only",
        "trust_scan": "clear",
    }
    for key, expected in exact_runtime.items():
        if runtime.get(key) != expected:
            errors.append(f"runtime provenance/result drift: {key}")

    disposition = record.get("disposition", {})
    if disposition.get("evidence_disposition") != "J2_SOURCE_FAITHFUL_EVIDENCE_COMPLETE_READY_FOR_ROUTE_TARGET_SUCCESSOR":
        errors.append("final evidence disposition drift")
    if disposition.get("ready_for_route_target_successor") is not True:
        errors.append("route-target successor readiness lost")
    if disposition.get("adjudication_authorized") is not False:
        errors.append("evidence candidate improperly authorizes adjudication")

    state = record.get("required_state", {})
    if state != {
        "route_state": "submitted",
        "live_route_target_list_changed": False,
        "may_adjudicate": False,
        "adjudication": None,
        "cert_output": None,
        "mathematical_target_proved": False,
        "may_promote_claim": False,
        "aggregate_authority": False,
    }:
        errors.append("fail-closed J2 state drift")

    route = find_route(routes, "MC-ROUTE-OTP-J2-TWO-DEGENERATE")
    if route is None:
        errors.append("live J2 route missing")
    else:
        status = route.get("intake_status", route.get("route_state", route.get("status")))
        if status != "submitted":
            errors.append("live J2 route is not submitted")
        if route.get("cert_output") is not None:
            errors.append("live J2 route gained Cert output")
        if route_targets(route) != HISTORICAL_TARGETS:
            errors.append("live J2 route targets changed during evidence stage")

    if check_files:
        for rel, expected in OBJECTS.items():
            if repo_blob(rel) != expected:
                errors.append(f"repository object identity drift: {rel}")
        if not is_ancestor(EXPECTED["runtime_head"]):
            errors.append("bound runtime head is not an ancestor of the current evidence head")

    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"J2 source-faithful evidence validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print(
        "validated completed J2 source-faithful evidence: exact runtime artifact bound, "
        "runtime head ancestral, route unchanged/submitted, and adjudication/output authority absent"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
