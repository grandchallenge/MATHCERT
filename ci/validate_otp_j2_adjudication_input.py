#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

import validate_otp_j2_route_target_successor as j2

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "governance/result_family_adjudication_execution_inputs/OTP-J2-TWO-DEGENERATE.json"
SCHEMA = ROOT / "schemas/openai_ten_proofs_j2_adjudication_execution_input.schema.json"
ROUTES = ROOT / "governance/certification_routes.json"
CONTRACT = ROOT / "governance/result_family_adjudication_contract_successors/OTP-J2-TWO-DEGENERATE.json"

TARGETS = [
    "TwoDegenerateGraphs.mathcert_sourceFaithfulTwoDegenerateExtremalCounterexample",
    "TwoDegenerateGraphs.mathcert_sourceFaithfulNotErdos146",
]
EXPECTED_BLOBS = {
    "governance/result_family_adjudication_execution_inputs/OTP-J2-TWO-DEGENERATE.json": "bd18b84bc257b7f06b875a6cf5fa4c038eb7c3cd",
    "governance/result_family_adjudication_contract_successors/OTP-J2-TWO-DEGENERATE.json": "1feaeac515beb792c5552bc795826bd999f4e535",
    "governance/result_family_route_target_successors/OTP-J2-TWO-DEGENERATE.json": "5b72e13448cdbea88e0f2cf1e637c2d787b297a6",
    "governance/result_family_construction_evidence/OTP-J2-TWO-DEGENERATE.json": "e1bc1f04daf28b04a85e92e605732f466ab1e2d6",
    "evidence/openai_ten_proofs/two_degenerate_construction/source_authority.json": "956320bfc94760d408c7f1a6af9bb6a8e8e1d1fc",
    "evidence/openai_ten_proofs/two_degenerate_construction/reconstruction.json": "3905455458f247b768353bc0b082ecbf7c8dd0ff",
    "evidence/openai_ten_proofs/two_degenerate_construction/proof_dependency_ledger.json": "0d81c00d9d190e92ed6f30de867e940bc03b2237",
    "evidence/openai_ten_proofs/two_degenerate_scope_repair/SourceFaithfulProjection.lean": "ac1ec20e95d6acbcd1c3a111afe28bca92a43377",
    "governance/certification_routes.json": "eb2ad35f73ec1f7a29c7432aa9e5ad299116dbfe",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def repo_blob(rel: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", f"HEAD:{rel}"], text=True
    ).strip()


def commit_blob(commit: str, rel: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", f"{commit}:{rel}"], text=True
    ).strip()


def is_ancestor(sha: str) -> bool:
    return subprocess.run(
        ["git", "-C", str(ROOT), "merge-base", "--is-ancestor", sha, "HEAD"]
    ).returncode == 0


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


def validation_errors(record: dict[str, Any] | None = None, *, check_repository: bool = True) -> list[str]:
    """Validate the immutable adjudication input in its historical submitted/null state."""
    errors: list[str] = []
    record = load(INPUT) if record is None else record
    schema = load(SCHEMA)
    for err in Draft202012Validator(schema).iter_errors(record):
        errors.append(f"schema: {err.message}")

    recipe = record.get("execution_recipe", {})
    if recipe.get("streamlined_control_plan_applies") is not True:
        errors.append("streamlined control plan disabled")
    if recipe.get("separate_human_steward_authorization_required") is not False:
        errors.append("unnecessary Human Steward authorization gate reintroduced")
    if recipe.get("execution_authorized_by_protected_contract") is not True:
        errors.append("protected contract execution authority missing")
    if recipe.get("human_steward_intervention_required_only_for_control_plan_change") is not True:
        errors.append("control-plan change intervention boundary weakened")
    if record.get("encoded_targets") != TARGETS:
        errors.append("encoded target drift")
    if record.get("decision_contract", {}).get("disposition_at_input_stage") is not None:
        errors.append("execution input pre-adjudicates")
    if record.get("required_state", {}).get("cert_output") is not None:
        errors.append("execution input inserts Cert output")
    if record.get("required_state", {}).get("route_state") != "submitted":
        errors.append("execution input transitions route")
    if record.get("required_state", {}).get("stronger_coloring_property_source_authorized") is not False:
        errors.append("stronger coloring property source-authorized")
    if record.get("required_state", {}).get("stronger_coloring_property_certified") is not False:
        errors.append("stronger coloring property certified")

    if not check_repository:
        return errors

    if not is_ancestor("ca66279862dcec276d2280749e6fae45f6e1e7a0"):
        errors.append("protected route-target successor merge is not an ancestor")
    for rel, expected in EXPECTED_BLOBS.items():
        try:
            actual = repo_blob(rel)
        except subprocess.CalledProcessError:
            errors.append(f"missing protected object: {rel}")
            continue
        if actual != expected:
            errors.append(f"protected object drift: {rel}: {actual}")

    contract = load(CONTRACT)
    gate = contract.get("execution_gate", {})
    if gate.get("streamlined_control_plan_applies") is not True:
        errors.append("protected contract does not authorize streamlined progression")
    if gate.get("separate_human_steward_authorization_required") is not False:
        errors.append("protected contract unexpectedly requires separate Human Steward authorization")
    if gate.get("human_steward_intervention_required_only_for_control_plan_change") is not True:
        errors.append("protected contract intervention boundary drift")
    if contract.get("route_scope", {}).get("target_claim_ids") != TARGETS:
        errors.append("contract target scope drift")
    if contract.get("state", {}).get("cert_output") is not None:
        errors.append("contract already contains Cert output")

    route = find_route(load(ROUTES), "MC-ROUTE-OTP-J2-TWO-DEGENERATE")
    if route is None:
        errors.append("live J2 route missing")
    else:
        if route.get("intake_status") != "submitted":
            errors.append("live J2 route not submitted")
        if route.get("target_claim_ids") != TARGETS:
            errors.append("live J2 target set drift")
        if route.get("cert_output") is not None:
            errors.append("live J2 route contains Cert output")

    projection = (ROOT / "evidence/openai_ten_proofs/two_degenerate_scope_repair/SourceFaithfulProjection.lean").read_text(encoding="utf-8")
    signature = projection.split("theorem mathcert_sourceFaithfulTwoDegenerateExtremalCounterexample", 1)[1].split(":= by", 1)[0]
    if "Coloring" in signature:
        errors.append("excluded coloring property leaked into source-faithful target signature")
    return errors


def compatibility_errors(record: dict[str, Any] | None = None) -> list[str]:
    """Preserve the immutable input while validating the separately governed output descendant."""
    errors = validation_errors(record, check_repository=False)

    if not is_ancestor("ca66279862dcec276d2280749e6fae45f6e1e7a0"):
        errors.append("protected route-target successor merge is not an ancestor")

    for rel, expected in EXPECTED_BLOBS.items():
        if rel == "governance/certification_routes.json":
            continue
        try:
            actual = repo_blob(rel)
        except subprocess.CalledProcessError:
            errors.append(f"missing protected object: {rel}")
            continue
        if actual != expected:
            errors.append(f"protected object drift: {rel}: {actual}")

    try:
        pre_output_blob = commit_blob(
            j2.OUTPUT_CERTIFICATE_COMMIT,
            "governance/certification_routes.json",
        )
    except subprocess.CalledProcessError:
        pre_output_blob = ""
    if pre_output_blob != EXPECTED_BLOBS["governance/certification_routes.json"]:
        errors.append("historical adjudication-input route snapshot drift")

    contract = load(CONTRACT)
    gate = contract.get("execution_gate", {})
    if gate.get("streamlined_control_plan_applies") is not True:
        errors.append("protected contract does not authorize streamlined progression")
    if gate.get("separate_human_steward_authorization_required") is not False:
        errors.append("protected contract unexpectedly requires separate Human Steward authorization")
    if gate.get("human_steward_intervention_required_only_for_control_plan_change") is not True:
        errors.append("protected contract intervention boundary drift")
    if contract.get("route_scope", {}).get("target_claim_ids") != TARGETS:
        errors.append("contract target scope drift")
    if contract.get("state", {}).get("cert_output") is not None:
        errors.append("immutable adjudication contract gained Cert output")

    errors.extend(j2.live_output_successor_errors(load(ROUTES)))

    projection = (ROOT / "evidence/openai_ten_proofs/two_degenerate_scope_repair/SourceFaithfulProjection.lean").read_text(encoding="utf-8")
    signature = projection.split("theorem mathcert_sourceFaithfulTwoDegenerateExtremalCounterexample", 1)[1].split(":= by", 1)[0]
    if "Coloring" in signature:
        errors.append("excluded coloring property leaked into source-faithful target signature")
    return errors


def main() -> int:
    route = find_route(load(ROUTES), "MC-ROUTE-OTP-J2-TWO-DEGENERATE")
    if route is not None and route.get("intake_status") == "qualified":
        errors = compatibility_errors()
        label = "immutable J2 adjudication execution input plus governed restricted output successor"
    else:
        errors = validation_errors()
        label = "J2 adjudication execution input"
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(
        f"validated {label}: protected contract authority, exact source-faithful targets, "
        "no redundant Human Steward gate, and stronger-coloring exclusion preserved"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
