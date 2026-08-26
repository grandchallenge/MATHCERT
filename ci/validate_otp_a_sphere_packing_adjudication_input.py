#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "governance/result_family_adjudication_execution_inputs/OTP-A-SPHERE-PACKING.json"
SCHEMA = ROOT / "schemas/openai_ten_proofs_sphere_packing_adjudication_execution_input.schema.json"
ROUTES = ROOT / "governance/certification_routes.json"
CONTRACT = ROOT / "governance/result_family_adjudication_contracts/OTP-A-SPHERE-PACKING.json"
DESIGN_REGISTRY = ROOT / "governance/adjudication_design/OPENAI_TEN_PROOFS_A_SPHERE_PACKING_ADJUDICATION_CONTRACT.json"
RECEIPT = ROOT / "governance/pre_route_candidates/OPENAI_TEN_PROOFS_A_SPHERE_PACKING_ROUTE_REGISTRATION.json"
REPLAY = ROOT / "governance/result_family_replay_evidence_successors/OTP-A-SPHERE-PACKING.json"
CONTRACT_REL = "governance/result_family_adjudication_contracts/OTP-A-SPHERE-PACKING.json"
ROUTES_REL = "governance/certification_routes.json"

TARGETS = [
    "PackingBounds.FullMain.exact_limit",
    "PackingBounds.FullMain.exact_binary_exponent",
    "PackingBounds.PackingBridge.sphere_packing_sharp_asymptotic_upper",
    "PackingBounds.sharpFullCohnElkiesManuscriptConclusions",
]
CLASSIFICATIONS = [
    "direct_source_theorem_projection_modulo_proved_full_radial_equivalence",
    "derived_base_two_logarithmic_consequence",
    "source_faithful_displayed_consequence_with_proved_scale_normalization",
    "source_faithful_derived_composite_certificate",
]
AXIOMS = ["propext", "Quot.sound", "Classical.choice"]
PRE_OUTPUT_ROUTES_BLOB = "b9bb0dc9e18856f50a88162df37c20c034327439"
OUTPUT_ROUTES_BLOB = "4d5c8e3f2b33d5148d98e7057991e167938c75bb"
EXPECTED_OUTPUT = {
    "repository": "grandchallenge/MATHCERT",
    "commit_sha": "1815f1b4010122e5bef0438f84da0b06204ba487",
    "path": "certificates/formal_sources/MC-OTP-A-SPHERE-PACKING-001.json",
    "digest_algorithm": "git_blob_sha1",
    "digest": "534e98ad2f00406fc869ea137f802f8cf504798a",
}
EXPECTED_BLOBS = {
    "governance/result_family_adjudication_execution_inputs/OTP-A-SPHERE-PACKING.json": "c4cc4aaecaccbab62e8d14d737f3048d1b598b3a",
    CONTRACT_REL: "5f56cdc5c5c839e1040bea84c2d756d805dd1c3b",
    "governance/adjudication_design/OPENAI_TEN_PROOFS_A_SPHERE_PACKING_ADJUDICATION_CONTRACT.json": "3605d660e4c4b57405ea03c4abfedb32d9deab93",
    "governance/pre_route_candidates/OPENAI_TEN_PROOFS_A_SPHERE_PACKING_ROUTE_REGISTRATION.json": "2d9a520a3ef868c4d6d721cffc6cf89e546c6d09",
    "governance/result_family_replay_evidence_successors/OTP-A-SPHERE-PACKING.json": "5a2d17d158ee9e8b535de8ed0a1ed41612c5abd2",
    ROUTES_REL: PRE_OUTPUT_ROUTES_BLOB,
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def repo_blob(rel: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", f"HEAD:{rel}"], text=True).strip()


def commit_available(sha: str) -> bool:
    return subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e", f"{sha}^{{commit}}"], capture_output=True).returncode == 0


def is_ancestor(sha: str) -> bool:
    return subprocess.run(["git", "-C", str(ROOT), "merge-base", "--is-ancestor", sha, "HEAD"], capture_output=True).returncode == 0


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
    errors: list[str] = []
    record = load(INPUT) if record is None else record
    for err in Draft202012Validator(load(SCHEMA)).iter_errors(record):
        errors.append(f"schema: {err.message}")

    if record.get("encoded_targets") != TARGETS:
        errors.append("target drift")
    if record.get("classifications") != CLASSIFICATIONS:
        errors.append("classification drift")
    if record.get("permitted_axioms") != AXIOMS:
        errors.append("permitted axiom drift")
    if record.get("nonvacuity_state") != "clear_for_current_root_four_target_surface":
        errors.append("nonvacuity boundary drift")
    if record.get("decision_contract", {}).get("disposition_at_input_stage") is not None:
        errors.append("execution input pre-adjudicates")

    recipe = record.get("execution_recipe", {})
    if recipe.get("routine_stage_progression_without_human_steward_intervention") is not True:
        errors.append("routine progression disabled")
    if recipe.get("separate_human_steward_authorization_required") is not False:
        errors.append("unnecessary Human Steward gate reintroduced")
    if recipe.get("execution_authorized_by_protected_contract") is not True:
        errors.append("protected contract execution authority missing")
    if recipe.get("human_steward_intervention_required_only_for_control_plan_change") is not True:
        errors.append("control-plan intervention boundary weakened")

    state = record.get("required_state", {})
    required_false = [
        "aggregate_adjudication", "aggregate_output", "mathematical_target_proved", "may_issue_output",
        "may_promote_claim", "manuscript_decimal_precision_attributed", "composite_is_single_verbatim_source_theorem",
        "whole_chapter_equivalence_established", "full_proof_body_equivalence_established",
    ]
    if state.get("route_state") != "submitted":
        errors.append("route transition at input")
    if state.get("adjudication") is not None:
        errors.append("adjudication inserted at input")
    if state.get("cert_output") is not None:
        errors.append("Cert output inserted at input")
    for key in required_false:
        if state.get(key) is not False:
            errors.append(f"input authority inflation: {key}")
    if state.get("scale_normalization_boundary_required") is not True:
        errors.append("scale normalization boundary erased")

    limits = record.get("preserved_limitations", {})
    if limits.get("target_classification_separation_required") is not True:
        errors.append("classification separation weakened")
    if limits.get("manuscript_decimal_precision_attributed") is not False:
        errors.append("formal decimal precision attributed to manuscript")
    if limits.get("scale_normalization_boundary_required") is not True:
        errors.append("normalization boundary removed")
    if limits.get("little_o_strengthened") is not False:
        errors.append("little-o normal form strengthened")
    if limits.get("composite_is_single_verbatim_source_theorem") is not False:
        errors.append("mixed composite inflated to verbatim theorem")

    if not check_repository:
        return errors

    # The execution-input record is historical and remains submitted/null.
    # The live repository may subsequently contain only the exact protected
    # qualified-output successor; no other route-registry successor is accepted.
    protected_design = "38fd4333b9f5aa6f4d754c1c097fd342a9b9321c"
    if commit_available(protected_design) and not is_ancestor(protected_design):
        errors.append("protected design merge is not an ancestor")
    for rel, expected in EXPECTED_BLOBS.items():
        try:
            actual = repo_blob(rel)
        except subprocess.CalledProcessError:
            errors.append(f"missing protected object: {rel}")
            continue
        if rel == ROUTES_REL:
            if actual not in {PRE_OUTPUT_ROUTES_BLOB, OUTPUT_ROUTES_BLOB}:
                errors.append(f"protected object drift: {rel}: {actual}")
        elif actual != expected:
            errors.append(f"protected object drift: {rel}: {actual}")

    contract = load(CONTRACT)
    if contract.get("contract_state") != "design_only":
        errors.append("protected contract state drift")
    if contract.get("route_scope", {}).get("target_claim_ids") != TARGETS:
        errors.append("contract target drift")
    if contract.get("route_scope", {}).get("classifications") != CLASSIFICATIONS:
        errors.append("contract classification drift")
    if contract.get("route_scope", {}).get("permitted_axioms") != AXIOMS:
        errors.append("contract axiom drift")
    if contract.get("route_scope", {}).get("nonvacuity_state") != "clear_for_current_root_four_target_surface":
        errors.append("contract nonvacuity drift")
    gate = contract.get("execution_gate", {})
    if gate.get("routine_stage_progression_without_human_steward_intervention") is not True:
        errors.append("protected contract routine progression disabled")
    if gate.get("human_steward_intervention_required_for_control_plan_change") is not True:
        errors.append("protected contract intervention boundary drift")
    if contract.get("state", {}).get("cert_output") is not None:
        errors.append("protected contract gained Cert output")

    registry = load(DESIGN_REGISTRY)
    activation = registry.get("activation", {})
    if activation.get("routine_stage_progression_without_human_steward_intervention") is not True:
        errors.append("design registry routine progression disabled")
    if activation.get("human_steward_intervention_required_for_control_plan_change") is not True:
        errors.append("design registry intervention boundary drift")
    rows = registry.get("contracts", [])
    if len(rows) != 1 or rows[0].get("contract", {}).get("digest") != EXPECTED_BLOBS[CONTRACT_REL]:
        errors.append("design registry contract binding drift")

    route = find_route(load(ROUTES), "MC-ROUTE-OTP-A-SPHERE-PACKING")
    if route is None:
        errors.append("live A route missing")
    else:
        if route.get("target_claim_ids") != TARGETS:
            errors.append("live A target drift")
        route_state = route.get("intake_status")
        if route_state == "submitted":
            if route.get("cert_output") is not None:
                errors.append("submitted live A route contains Cert output")
        elif route_state == "qualified":
            if route.get("cert_output") != EXPECTED_OUTPUT:
                errors.append("qualified live A route output identity drift")
        else:
            errors.append("live A route has unauthorized state")

    receipt = load(RECEIPT)
    controls = receipt.get("route_controls", {})
    for key in ("may_adjudicate", "may_issue_cert_output", "may_mark_target_proved", "may_promote_claim"):
        if controls.get(key) is not False:
            errors.append(f"registration control inflated: {key}")

    replay = load(REPLAY)
    if replay.get("evidence_id") != "MC-OTP-A-SPHERE-PACKING-REPLAY-EVIDENCE-001":
        errors.append("replay evidence identity drift")
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    live = find_route(load(ROUTES), "MC-ROUTE-OTP-A-SPHERE-PACKING") or {}
    print(f"validated historical A adjudication execution input and exact live route successor state={live.get('intake_status')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
