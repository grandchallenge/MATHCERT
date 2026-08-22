#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "governance/result_family_adjudications/OTP-A-SPHERE-PACKING.json"
SCHEMA = ROOT / "schemas/openai_ten_proofs_sphere_packing_adjudication.schema.json"
INPUT = ROOT / "governance/result_family_adjudication_execution_inputs/OTP-A-SPHERE-PACKING.json"
CONTRACT = ROOT / "governance/result_family_adjudication_contracts/OTP-A-SPHERE-PACKING.json"
DESIGN = ROOT / "governance/adjudication_design/OPENAI_TEN_PROOFS_A_SPHERE_PACKING_ADJUDICATION_CONTRACT.json"
ROUTES = ROOT / "governance/certification_routes.json"
RECEIPT = ROOT / "governance/pre_route_candidates/OPENAI_TEN_PROOFS_A_SPHERE_PACKING_ROUTE_REGISTRATION.json"
REPLAY = ROOT / "governance/result_family_replay_evidence_successors/OTP-A-SPHERE-PACKING.json"

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
EXPECTED = {
    "record_blob": "3e0b34dbc74fdbe123f551d559e4f93fc1901c48",
    "input_blob": "c4cc4aaecaccbab62e8d14d737f3048d1b598b3a",
    "contract_blob": "5f56cdc5c5c839e1040bea84c2d756d805dd1c3b",
    "design_blob": "3605d660e4c4b57405ea03c4abfedb32d9deab93",
    "route_blob": "b9bb0dc9e18856f50a88162df37c20c034327439",
    "receipt_blob": "2d9a520a3ef868c4d6d721cffc6cf89e546c6d09",
    "replay_blob": "5a2d17d158ee9e8b535de8ed0a1ed41612c5abd2",
    "runtime_head": "5c35035aab713573c905eeb05abf07a62667a6a2",
    "runtime_run": 32234321274,
    "runtime_job": 96010971666,
    "runtime_artifact": 9358858485,
    "runtime_artifact_size": 26371,
    "runtime_artifact_sha256": "9ec79cfeb47b1580caa6f464e7e6ffd632ee352eecff8e36b8c96ae239095417",
    "runtime_adjudication_bundle_sha256": "8dcdd1aff048410fbbadee5a9c94268fa69c6d6dec276bba9090d90b219c8513",
    "runtime_replay_bundle_sha256": "c7a4420601960544a0538d7aef3383b60feae0601937ff5a26688cf74c0eb2d5",
}
OBJECTS = {
    "governance/result_family_adjudications/OTP-A-SPHERE-PACKING.json": EXPECTED["record_blob"],
    "governance/result_family_adjudication_execution_inputs/OTP-A-SPHERE-PACKING.json": EXPECTED["input_blob"],
    "governance/result_family_adjudication_contracts/OTP-A-SPHERE-PACKING.json": EXPECTED["contract_blob"],
    "governance/adjudication_design/OPENAI_TEN_PROOFS_A_SPHERE_PACKING_ADJUDICATION_CONTRACT.json": EXPECTED["design_blob"],
    "governance/pre_route_candidates/OPENAI_TEN_PROOFS_A_SPHERE_PACKING_ROUTE_REGISTRATION.json": EXPECTED["receipt_blob"],
    "governance/result_family_replay_evidence_successors/OTP-A-SPHERE-PACKING.json": EXPECTED["replay_blob"],
    "governance/certification_routes.json": EXPECTED["route_blob"],
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(ROOT), *args], text=True, capture_output=True, check=check)


def repo_blob(rel: str) -> str:
    return git("rev-parse", f"HEAD:{rel}").stdout.strip()


def commit_available(sha: str) -> bool:
    return git("cat-file", "-e", f"{sha}^{{commit}}", check=False).returncode == 0


def is_ancestor(sha: str) -> bool:
    return git("merge-base", "--is-ancestor", sha, "HEAD", check=False).returncode == 0


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
    record = load(RECORD) if record is None else record
    errors: list[str] = []
    for err in Draft202012Validator(load(SCHEMA)).iter_errors(record):
        errors.append(f"closed schema: {err.message}")

    if record.get("encoded_targets") != TARGETS:
        errors.append("adjudication target drift")
    if record.get("classifications") != CLASSIFICATIONS:
        errors.append("adjudication classification drift")
    if record.get("permitted_axioms") != AXIOMS:
        errors.append("adjudication axiom drift")
    if [row.get("target") for row in record.get("target_assessments", [])] != TARGETS:
        errors.append("target assessment order/scope drift")
    if [row.get("classification") for row in record.get("target_assessments", [])] != CLASSIFICATIONS:
        errors.append("target assessment classification drift")

    decision = record.get("decision", {})
    if decision.get("disposition") != "adjudication_clear_protected_four_targets_only":
        errors.append("adjudication disposition drift")
    if decision.get("scope") != "exact_four_protected_targets_under_distinct_classifications_only":
        errors.append("adjudication scope drift")
    for key in ("does_not_mark_mathematical_target_proved", "does_not_issue_cert_output", "does_not_transition_route"):
        if decision.get(key) is not True:
            errors.append(f"decision authority exclusion weakened: {key}")

    runtime = record.get("fresh_execution", {})
    expected_runtime = {
        "execution_head": EXPECTED["runtime_head"],
        "workflow": ".github/workflows/otp-a-sphere-packing-adjudication.yml",
        "workflow_run_id": EXPECTED["runtime_run"],
        "replay_job_id": EXPECTED["runtime_job"],
        "input_control_ubuntu": "success",
        "input_control_windows": "success",
        "source_reacquisition": "exact_2026_08_06_bytes_reacquired",
        "solution_build": "pass",
        "comparator": "accept",
        "lean_default_kernel": "accept",
        "nanoda": "accept",
        "theorem_axioms": "permitted_only",
        "trust_boundary": "clear",
        "control_plan_conformance": "clear",
    }
    for key, expected in expected_runtime.items():
        if runtime.get(key) != expected:
            errors.append(f"fresh runtime drift: {key}")
    artifact = runtime.get("artifact", {})
    expected_artifact = {
        "artifact_id": EXPECTED["runtime_artifact"],
        "name": "otp-a-sphere-packing-adjudication-runtime",
        "size_in_bytes": EXPECTED["runtime_artifact_size"],
        "zip_sha256": EXPECTED["runtime_artifact_sha256"],
        "adjudication_bundle_sha256": EXPECTED["runtime_adjudication_bundle_sha256"],
        "replay_bundle_sha256": EXPECTED["runtime_replay_bundle_sha256"],
    }
    if artifact != expected_artifact:
        errors.append("fresh runtime artifact identity drift")

    source = record.get("current_source", {})
    if source.get("byte_length") != 2487031 or source.get("sha256") != "ebc561ab5c53dbd240e17a8fdb6fffeb648591eca85dbfc7466f563638f8c566":
        errors.append("current source identity drift")
    if source.get("whole_document_equivalence_between_revisions") != "not_established":
        errors.append("whole-document equivalence inflation")

    formal = record.get("formal_subject", {})
    if formal.get("commit") != "94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6" or formal.get("tree") != "174289e4d4958cb0509874e6e53400e098213de7":
        errors.append("formal subject identity drift")

    sf = record.get("source_formal_assessment", {})
    if sf.get("status") != "clear_for_exact_four_target_surface":
        errors.append("source-formal assessment not clear for exact protected surface")
    if sf.get("independent_source_reclassification_performed") is not False:
        errors.append("unauthorized fresh source reclassification claimed")
    if sf.get("decimal_provenance") != "formal_numerical_consequence_only_not_manuscript_precision":
        errors.append("decimal provenance drift")
    if sf.get("scale_normalization") != "proved_positive_rescaling_and_unit_separation_supremum_equivalence_required":
        errors.append("scale normalization drift")
    if sf.get("little_o") != "explicit_witness_normal_form_only_no_stronger_rate":
        errors.append("little-o boundary drift")
    if sf.get("composite_boundary") != "mixed_source_projection_and_checked_derived_consequence_not_single_verbatim_theorem":
        errors.append("composite boundary drift")
    if sf.get("whole_chapter_equivalence") is not False or sf.get("full_proof_body_equivalence") is not False:
        errors.append("source-formal equivalence overclaim")

    nv = record.get("nonvacuity", {})
    if nv.get("state") != "clear_for_current_root_four_target_surface" or nv.get("fresh_attestation") != "clear_bound_to_protected_current_root_evidence":
        errors.append("nonvacuity drift")

    state = record.get("state", {})
    expected_state = {
        "route_state": "submitted",
        "adjudication_recorded": True,
        "adjudication_authority_source": "protected_streamlined_a_sphere_packing_contract",
        "routine_stage_progression_without_human_steward_intervention": True,
        "human_steward_intervention_required_only_for_control_plan_change": True,
        "separate_human_steward_authorization_required": False,
        "cert_output": None,
        "mathematical_target_proved": False,
        "may_issue_output": False,
        "may_promote_claim": False,
        "aggregate_adjudication": False,
        "aggregate_output": False,
        "manuscript_decimal_precision_attributed": False,
        "scale_normalization_boundary_required": True,
        "little_o_strengthened": False,
        "composite_is_single_verbatim_source_theorem": False,
        "whole_chapter_equivalence_established": False,
        "full_proof_body_equivalence_established": False,
        "other_result_families_modified": False,
    }
    if state != expected_state:
        errors.append("adjudication no-output/no-route-transition state drift")

    gate = record.get("publication_gate", {})
    if gate.get("recorded_review") is not None:
        errors.append("final-head review prepopulated before external review")
    for key in ("exact_head_cert_required", "exact_head_gcl_required", "applicable_codeql_no_new_alert_required", "fresh_non_author_specialist_approval_required", "review_must_bind_final_publication_head", "expected_head_merge_required", "protected_main_readback_required", "head_change_requires_revalidation_and_reapproval"):
        if gate.get(key) is not True:
            errors.append(f"publication gate weakened: {key}")

    if not check_repository:
        return errors

    for rel, expected in OBJECTS.items():
        try:
            actual = repo_blob(rel)
        except subprocess.CalledProcessError:
            errors.append(f"missing protected object: {rel}")
            continue
        if actual != expected:
            errors.append(f"protected object drift: {rel}: {actual}")

    if commit_available(EXPECTED["runtime_head"]) and not is_ancestor(EXPECTED["runtime_head"]):
        errors.append("fresh execution head is not an ancestor of current publication head")
    if commit_available("38fd4333b9f5aa6f4d754c1c097fd342a9b9321c") and not is_ancestor("38fd4333b9f5aa6f4d754c1c097fd342a9b9321c"):
        errors.append("protected A design merge is not an ancestor")

    contract = load(CONTRACT)
    if contract.get("route_scope", {}).get("target_claim_ids") != TARGETS or contract.get("route_scope", {}).get("classifications") != CLASSIFICATIONS:
        errors.append("protected contract target/classification drift")
    if contract.get("execution_gate", {}).get("routine_stage_progression_without_human_steward_intervention") is not True:
        errors.append("protected streamlined control plan disabled")
    if contract.get("state", {}).get("cert_output") is not None:
        errors.append("protected contract gained output authority")

    input_record = load(INPUT)
    if input_record.get("decision_contract", {}).get("disposition_at_input_stage") is not None:
        errors.append("protected execution input was retroactively adjudicated")
    if input_record.get("execution_recipe", {}).get("separate_human_steward_authorization_required") is not False:
        errors.append("execution input reintroduced redundant Human Steward gate")

    route = find_route(load(ROUTES), "MC-ROUTE-OTP-A-SPHERE-PACKING")
    if route is None:
        errors.append("live A route missing")
    else:
        if route.get("intake_status") != "submitted":
            errors.append("live A route transitioned during adjudication")
        if route.get("target_claim_ids") != TARGETS:
            errors.append("live A target drift")
        if route.get("cert_output") is not None:
            errors.append("live A route gained Cert output")

    receipt = load(RECEIPT)
    for key in ("may_issue_cert_output", "may_mark_target_proved", "may_promote_claim"):
        if receipt.get("route_controls", {}).get(key) is not False:
            errors.append(f"registration authority inflated: {key}")

    replay = load(REPLAY)
    if replay.get("evidence_id") != "MC-OTP-A-SPHERE-PACKING-REPLAY-EVIDENCE-001":
        errors.append("protected replay evidence identity drift")
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("validated A sphere-packing adjudication: exact four-target clear disposition, fresh runtime identities, protected semantic boundaries, submitted/null output state, and streamlined governance preserved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
