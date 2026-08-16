#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
ROUTES = ROOT / "governance/certification_routes.json"
RECEIPT = ROOT / "governance/result_family_route_target_successors/OTP-J2-TWO-DEGENERATE.json"
CONTRACT = ROOT / "governance/result_family_adjudication_contract_successors/OTP-J2-TWO-DEGENERATE.json"
RECEIPT_SCHEMA = ROOT / "schemas/openai_ten_proofs_j2_route_target_successor.schema.json"
CONTRACT_SCHEMA = ROOT / "schemas/openai_ten_proofs_j2_adjudication_contract_successor.schema.json"

ROUTE_ID = "MC-ROUTE-OTP-J2-TWO-DEGENERATE"
PREDECESSOR_ROUTE_BLOB = "bc4640661443f1b3de213aaa82a333a4fdb6849b"
PREDECESSOR_CONTRACT_BLOB = "2bb9d70b931ea0a07487664c112644f990527760"
SCOPE_REPAIR_BLOB = "5884bc57ba4e9c1d4576b96793f7e78009223b15"
EVIDENCE_BLOB = "e1bc1f04daf28b04a85e92e605732f466ab1e2d6"
PROJECTION_BLOB = "ac1ec20e95d6acbcd1c3a111afe28bca92a43377"
SOURCE_AUTHORITY_BLOB = "956320bfc94760d408c7f1a6af9bb6a8e8e1d1fc"
PROTECTED_PREDECESSOR_MAIN = "a2b1a464ac992b9807061e8ede9d2f7c42ad4cf6"
OUTPUT_CONTRACT_MERGE = "d1f0d69e145029e8b7bc29c0ec60543f7db29272"
OUTPUT_CERTIFICATE_COMMIT = "24cff6e55709c067c7f966c1a533255af707bec0"
OUTPUT_ROUTE_COMMIT = "15559390e2489ae73d872f389a9601c7412b77ed"
OUTPUT_CERTIFICATE_BLOB = "308a2eb7087fb24a07a6ae8c93a83b593468d2f7"
OUTPUT_CERTIFICATE_PATH = "certificates/formal_sources/MC-OTP-J2-TWO-DEGENERATE-001.json"
OUTPUT_CERT = {
    "repository": "grandchallenge/MATHCERT",
    "commit_sha": OUTPUT_CERTIFICATE_COMMIT,
    "path": OUTPUT_CERTIFICATE_PATH,
    "digest_algorithm": "git_blob_sha1",
    "digest": OUTPUT_CERTIFICATE_BLOB,
}
OLD_TARGETS = [
    "TwoDegenerateGraphs.twoDegenerateExtremalCounterexample",
    "TwoDegenerateGraphs.not_erdos_146",
]
NEW_TARGETS = [
    "TwoDegenerateGraphs.mathcert_sourceFaithfulTwoDegenerateExtremalCounterexample",
    "TwoDegenerateGraphs.mathcert_sourceFaithfulNotErdos146",
]
ALLOWED_J2_ROUTE_MUTATIONS = {
    "target_claim_ids",
    "claim_boundary",
    "blockers",
    "reopening_conditions",
}
OBJECTS = {
    "governance/result_family_adjudication_contracts/OTP-J2-TWO-DEGENERATE.json": PREDECESSOR_CONTRACT_BLOB,
    "governance/result_family_scope_repairs/OTP-J2-TWO-DEGENERATE.json": SCOPE_REPAIR_BLOB,
    "governance/result_family_construction_evidence/OTP-J2-TWO-DEGENERATE.json": EVIDENCE_BLOB,
    "evidence/openai_ten_proofs/two_degenerate_scope_repair/SourceFaithfulProjection.lean": PROJECTION_BLOB,
    "evidence/openai_ten_proofs/two_degenerate_construction/source_authority.json": SOURCE_AUTHORITY_BLOB,
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


def blob_json(blob: str) -> Any:
    return json.loads(git("cat-file", "blob", blob).stdout)


def commit_json(commit: str, rel: str) -> Any:
    return json.loads(git("show", f"{commit}:{rel}").stdout)


def is_ancestor(older: str, newer: str = "HEAD") -> bool:
    return git("merge-base", "--is-ancestor", older, newer, check=False).returncode == 0


def find_route(routes: dict[str, Any], route_id: str = ROUTE_ID) -> dict[str, Any] | None:
    for route in routes.get("routes", []):
        if route.get("route_id") == route_id:
            return route
    return None


def route_map(routes: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {route["route_id"]: route for route in routes.get("routes", [])}


def pre_output_routes() -> dict[str, Any]:
    """Exact route registry at the certificate-content commit, before J2 route transition."""
    return commit_json(OUTPUT_CERTIFICATE_COMMIT, "governance/certification_routes.json")


def live_output_successor_errors(routes: dict[str, Any] | None = None) -> list[str]:
    """Validate only the separately governed live J2 output successor state."""
    routes = load(ROUTES) if routes is None else routes
    errors: list[str] = []
    live = find_route(routes)
    if live is None:
        return ["live J2 route missing"]
    if live.get("campaign_id") != "OTP-J2-TWO-DEGENERATE":
        errors.append("J2 campaign identity drift")
    if live.get("target_claim_ids") != NEW_TARGETS:
        errors.append("J2 live target set is not exactly the source-faithful pair")
    if live.get("intake_status") != "qualified":
        errors.append("governed J2 output successor is not qualified")
    if live.get("cert_output") != OUTPUT_CERT:
        errors.append("governed J2 output successor Cert output identity drift")
    boundary = str(live.get("claim_boundary", "")).lower()
    for token in (
        "qualified_source_faithful_targets_only",
        "stronger coloring-side",
        "historical stronger",
        "aggregate openai ten proofs",
    ):
        if token not in boundary:
            errors.append(f"governed J2 output successor boundary missing {token}")
    if not is_ancestor(OUTPUT_CONTRACT_MERGE):
        errors.append("protected J2 output-contract merge is not an ancestor")
    if not is_ancestor(OUTPUT_CERTIFICATE_COMMIT):
        errors.append("J2 certificate-content commit is not an ancestor")
    if not is_ancestor(OUTPUT_ROUTE_COMMIT):
        errors.append("J2 route-transition commit is not an ancestor")
    return errors


def schema_errors(instance: Any, schema_path: Path, label: str) -> list[str]:
    errors: list[str] = []
    schema = load(schema_path)
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as exc:
        return [f"invalid {label} schema: {exc}"]
    for err in Draft202012Validator(schema).iter_errors(instance):
        errors.append(f"{label} closed-schema violation: {err.message}")
    return errors


def validation_errors(
    receipt: dict[str, Any] | None = None,
    contract: dict[str, Any] | None = None,
    routes: dict[str, Any] | None = None,
    check_files: bool = True,
) -> list[str]:
    """Validate the immutable route-target successor at its pre-output state."""
    errors: list[str] = []
    receipt = load(RECEIPT) if receipt is None else receipt
    contract = load(CONTRACT) if contract is None else contract
    routes = load(ROUTES) if routes is None else routes

    errors.extend(schema_errors(receipt, RECEIPT_SCHEMA, "J2 route-target successor receipt"))
    errors.extend(schema_errors(contract, CONTRACT_SCHEMA, "J2 adjudication-contract successor"))

    live = find_route(routes)
    if live is None:
        errors.append("live J2 route missing")
    else:
        if live.get("campaign_id") != "OTP-J2-TWO-DEGENERATE":
            errors.append("J2 campaign identity drift")
        if live.get("intake_status") != "submitted":
            errors.append("J2 route state changed from submitted")
        if live.get("target_claim_ids") != NEW_TARGETS:
            errors.append("J2 live target set is not exactly the source-faithful pair")
        if live.get("cert_output") is not None:
            errors.append("J2 route gained Cert output")
        boundary = live.get("claim_boundary", "")
        if "source-faithful" not in boundary or "stronger coloring-side" not in boundary:
            errors.append("J2 live claim boundary does not preserve source-faithful/coloring exclusion")

    if receipt.get("predecessor_live_target_claim_ids") != OLD_TARGETS:
        errors.append("receipt predecessor target identity drift")
    if receipt.get("successor_live_target_claim_ids") != NEW_TARGETS:
        errors.append("receipt successor target identity drift")
    if receipt.get("route_state_after_successor") != "submitted":
        errors.append("receipt route state drift")
    if receipt.get("authority", {}).get("predecessor_route_registry", {}).get("digest") != PREDECESSOR_ROUTE_BLOB:
        errors.append("receipt predecessor route-registry authority drift")
    if receipt.get("authority", {}).get("predecessor_adjudication_contract", {}).get("digest") != PREDECESSOR_CONTRACT_BLOB:
        errors.append("receipt predecessor adjudication-contract authority drift")
    streamlined = receipt.get("streamlined_control_plan", {})
    if streamlined.get("applies") is not True:
        errors.append("receipt lost streamlined control-plan binding")
    if streamlined.get("separate_human_steward_authorization_required_for_this_stage") is not False:
        errors.append("receipt reintroduced a routine Human Steward authorization gate")
    if streamlined.get("human_steward_intervention_required_only_for_control_plan_change") is not True:
        errors.append("receipt weakened the Human Steward intervention boundary")
    required = receipt.get("required_state", {})
    expected_required = {
        "route_state": "submitted",
        "may_adjudicate": False,
        "adjudication": None,
        "cert_output": None,
        "mathematical_target_proved": False,
        "may_promote_claim": False,
        "aggregate_authority": False,
        "stronger_coloring_property_source_authorized": False,
        "stronger_coloring_property_certified": False,
    }
    if required != expected_required:
        errors.append("receipt fail-closed authority state drift")

    if contract.get("contract_state") != "design_only":
        errors.append("successor contract is not design_only")
    if contract.get("route_id") != ROUTE_ID:
        errors.append("successor contract route identity drift")
    scope = contract.get("route_scope", {})
    if scope.get("registered_route_state") != "submitted":
        errors.append("successor contract route state drift")
    if scope.get("target_claim_ids") != NEW_TARGETS:
        errors.append("successor contract target set mismatch")
    if scope.get("historical_predecessor_target_claim_ids") != OLD_TARGETS:
        errors.append("successor contract predecessor-target history drift")
    exclusions = "\n".join(scope.get("scope_exclusions", []))
    if "stronger two-coloring" not in exclusions or "not source-authorized" not in exclusions:
        errors.append("successor contract lost stronger-coloring exclusion")
    gate = contract.get("execution_gate", {})
    expected_gate = {
        "streamlined_control_plan_applies": True,
        "separate_human_steward_authorization_required": False,
        "human_steward_intervention_required_only_for_control_plan_change": True,
        "exact_head_cert_checks_required": True,
        "exact_head_gcl_conformance_required": True,
        "fresh_non_author_approval_required": True,
        "protected_expected_head_merge_required": True,
        "protected_main_readback_required": True,
        "head_change_requires_revalidation_and_reapproval": True,
        "design_merge_effect": "source_faithful_contract_successor_admitted_design_only_no_adjudication",
    }
    if gate != expected_gate:
        errors.append("successor contract execution-gate drift")
    state = contract.get("state", {})
    if state != {
        "may_adjudicate": False,
        "adjudication": None,
        "cert_output": None,
        "mathematical_target_proved": False,
        "may_promote_claim": False,
        "aggregate_adjudication": False,
    }:
        errors.append("successor contract gained adjudication/output/promotion authority")
    limitations = contract.get("preserved_limitations", {})
    for key in (
        "stronger_coloring_property_source_authorized",
        "stronger_coloring_property_certified",
        "historical_records_rewritten",
        "proof_body_compared_in_full",
        "other_result_family_modified",
        "aggregate_openai_ten_proofs_authority",
    ):
        if limitations.get(key) is not False:
            errors.append(f"successor contract limitation drift: {key}")

    if live is not None and scope.get("target_claim_ids") != live.get("target_claim_ids"):
        errors.append("route/contract target mismatch")

    if check_files:
        predecessor_routes = blob_json(PREDECESSOR_ROUTE_BLOB)
        old_map = route_map(predecessor_routes)
        new_map = route_map(routes)
        if set(old_map) != set(new_map):
            errors.append("route registry membership changed during J2 target successor")
        for rid, old_route in old_map.items():
            current = new_map.get(rid)
            if current is None:
                continue
            if rid != ROUTE_ID:
                if current != old_route:
                    errors.append(f"unrelated route modified: {rid}")
                continue
            for key in set(old_route) | set(current):
                if key in ALLOWED_J2_ROUTE_MUTATIONS:
                    continue
                if old_route.get(key) != current.get(key):
                    errors.append(f"unauthorized J2 route field mutation: {key}")

        for rel, expected in OBJECTS.items():
            if repo_blob(rel) != expected:
                errors.append(f"protected predecessor/evidence object drift: {rel}")
        if not is_ancestor(PROTECTED_PREDECESSOR_MAIN):
            errors.append("protected predecessor main is not an ancestor of successor head")

    return errors


def main() -> int:
    live_routes = load(ROUTES)
    live = find_route(live_routes)
    if live is not None and live.get("intake_status") == "qualified":
        errors = validation_errors(routes=pre_output_routes(), check_files=True)
        errors.extend(live_output_successor_errors(live_routes))
        mode = "historical source-faithful successor plus governed restricted output successor"
    else:
        errors = validation_errors(routes=live_routes, check_files=True)
        mode = "source-faithful route-target successor"
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"J2 route-target successor validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print(
        f"validated J2 {mode}: exact source-faithful target pair and historical authority preserved"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
