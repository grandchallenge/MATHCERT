#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    "PermanentRollout.permanent_circuit_loglog_lower_bound",
    "PermanentRollout.permanent_circuit_loglog_bigOmega",
    "PermanentRollout.permanent_complexity_ratio_tendsto_atTop",
]
WITNESSES = [
    "PermanentRollout.exists_arithmeticCircuit_polynomial",
    "PermanentRollout.permanent_representable",
    "PermanentRollout.circuitComplexity_attained",
]
PROJECTION = {
    "formula_target_count": 0,
    "circuit_target_count": 3,
    "coefficient_field": "complex",
    "model": "division_free_arithmetic_circuit_dag",
    "input_gates": ["matrix_variable", "arbitrary_complex_scalar"],
    "arithmetic_gates": ["add", "sub", "mul"],
    "division_allowed": False,
    "fanout_reuse_allowed": True,
    "size_counts_arithmetic_gates_only": True,
    "input_gates_counted": False,
    "depth_restriction": False,
    "degree_restriction": False,
    "fanout_restriction": False,
    "cancellation_restriction": False,
    "dimension_threshold": 65536,
    "finite_bound_denominator": 144,
    "finite_bound": "n^2 * (log_2(log_2 n) - 3) / 144 <= circuitComplexity(permanent_n)",
    "bigomega_consequence": "circuitComplexity(permanent_n) = Omega(n^2 log_2 log_2 n)",
    "ratio_divergence_consequence": "circuitComplexity(permanent_n) / n^2 tends to +infinity",
    "historical_pdf_byte_equivalence": False,
}
PATHS = {
    "intake": ROOT / "governance/result_family_intake_successors/OTP-C-PERMANENT-CIRCUIT.json",
    "wp": ROOT / "governance/result_family_work_package_successors/OTP-C-PERMANENT-CIRCUIT-CERT-WP01.json",
    "replay": ROOT / "governance/result_family_replay_evidence_successors/OTP-C-PERMANENT-CIRCUIT.json",
    "proposal": ROOT / "governance/result_family_route_proposal_successors/OTP-C-PERMANENT-CIRCUIT.json",
    "route": ROOT / "governance/certification_route_overlays/OTP-C-PERMANENT-CIRCUIT.json",
    "contract": ROOT / "governance/result_family_adjudication_contract_successors/OTP-C-PERMANENT-CIRCUIT.json",
    "adjudication": ROOT / "governance/result_family_adjudications/OTP-C-PERMANENT-CIRCUIT.json",
    "output_contract": ROOT / "governance/result_family_output_contract_successors/OTP-C-PERMANENT-CIRCUIT.json",
    "staged_certificate": ROOT / "governance/result_family_output_candidates/staged_certificates/MC-OTP-C-PERMANENT-CIRCUIT-001.json",
    "transition": ROOT / "governance/result_family_output_candidates/staged_route_transitions/OTP-C-PERMANENT-CIRCUIT.json",
}
SCHEMA = ROOT / "schemas/otp_permanent_circuit_certification.schema.json"
GLOBAL_ROUTES = ROOT / "governance/certification_routes.json"
VARIABLE_CERT = ROOT / "certificates/formal_sources/MC-OTP-C-PERMANENT-001.json"
FULL_FORMULA_CERT = ROOT / "certificates/formal_sources/MC-OTP-C-PERMANENT-FULL-FORMULA-001.json"
FULL_FORMULA_ROUTE = ROOT / "governance/certification_route_overlays/OTP-C-PERMANENT-FULL-FORMULA.json"
LIVE_CERT = ROOT / "certificates/formal_sources/MC-OTP-C-PERMANENT-CIRCUIT-001.json"
EXPECTED_GLOBAL_ROUTES_BLOB = "2d17473b4731aa9d9c630b1e7777ad4bd794d993"
EXPECTED_VARIABLE_CERT_BLOB = "ad10c427270cb1c747ebcacbc5c37e4c1ed1df04"
EXPECTED_FULL_FORMULA_CERT_BLOB = "2940f551805794b96c7b0793bfe0d14e9fcd9954"
EXPECTED_FULL_FORMULA_ROUTE_BLOB = "3a208d3391514de74853f4ad182e26c74f631913"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    return subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", f"HEAD:{rel}"], text=True).strip()


def records_from_disk():
    return {name: load(path) for name, path in PATHS.items()}


def projection_without_pdf(value):
    p = copy.deepcopy(value or {})
    pdf = p.pop("historical_pdf_byte_equivalence", None)
    return p, pdf


def validation_errors(records=None, *, check_git=True):
    r = records_from_disk() if records is None else records
    errors: list[str] = []
    missing = [name for name in PATHS if name not in r]
    if missing:
        return [f"missing record: {name}" for name in missing]

    staged = r["staged_certificate"]
    errors.extend(
        f"candidate certificate schema: {e.message}"
        for e in Draft202012Validator(load(SCHEMA)).iter_errors(staged)
    )

    intake = r["intake"]
    auth = intake.get("authority", {})
    producer = auth.get("producer_packet", {})
    if (producer.get("commit_sha"), producer.get("digest"), producer.get("reviewed_head"), producer.get("review_node_id"), producer.get("reviewer")) != (
        "7d1f9edf16558ba4c4396126e24fd2c9ae4826f7",
        "f8443c47cee03890ca52af3e0cd39f1a54b5fc71",
        "245bfc57a898697db9a3c2a6a651b8d70a23518f",
        "PRR_kwDOSuU7KM8AAAABJuNjyw",
        "jimsteeg",
    ):
        errors.append("Solve authority substitution")
    semantic = auth.get("semantic_record", {})
    if (semantic.get("commit_sha"), semantic.get("digest")) != (
        "20a4cb716dba2586931e3eaebb079890c66044bd",
        "d47a50df90174ed03669b11b8469dc1c0788a1ea",
    ):
        errors.append("Forge semantic substitution")
    overlay = auth.get("comparator_overlay", {})
    if (overlay.get("json_digest"), overlay.get("lean_digest")) != (
        "1c2aad24890425ef82f8e45fa654de32dc0e2659",
        "18fc438580bab2bc003d4d3cfd9fa283da421b04",
    ):
        errors.append("Comparator overlay substitution")
    scope = intake.get("target_scope", {})
    if scope.get("lean_theorems") != TARGETS or scope.get("nonvacuity_witnesses") != WITNESSES:
        errors.append("intake target/nonvacuity drift")
    if scope.get("source_projection") != PROJECTION:
        errors.append("intake source projection drift")

    wp = r["wp"]
    if wp.get("target_scope", {}).get("lean_theorems") != TARGETS:
        errors.append("work-package target drift")
    if wp.get("target_scope", {}).get("source_projection") != PROJECTION:
        errors.append("work-package projection drift")
    execution = wp.get("execution", {})
    for key in (
        "isolated_family_replay_required",
        "clean_room_environment_required",
        "comparator_default_kernel_required",
        "nanoda_required",
        "theorem_level_axiom_reports_required",
        "nonvacuity_replay_required",
        "linux_and_windows_governance_required",
        "trust_boundary_scan_required",
    ):
        if execution.get(key) is not True:
            errors.append(f"work-package gate removed: {key}")
    if execution.get("aggregate_import_required") is not False or execution.get("lean_version") != "4.32.0":
        errors.append("work-package toolchain/aggregate drift")

    replay = r["replay"]
    pr = replay.get("protected_producer_replay", {})
    if (pr.get("run"), pr.get("job"), pr.get("lean_version"), pr.get("target_count")) != (31809287009, 94795718599, "4.32.0", 3):
        errors.append("protected replay identity drift")
    if any(pr.get(k) != "accepted" for k in ("lean_default_kernel", "nanoda_kernel", "comparator")):
        errors.append("protected replay acceptance lost")
    if pr.get("immutable_archive_modified") is not False:
        errors.append("protected archive mutation")
    fresh = replay.get("fresh_cert_replay", {})
    for key in ("exact_head_required", "clean_room_required", "evidence_artifact_required", "comparator_default_kernel_required", "nanoda_required", "nonvacuity_replay_required", "theorem_level_axiom_report_required"):
        if fresh.get(key) is not True:
            errors.append(f"fresh replay gate removed: {key}")

    proposal = r["proposal"]
    rc = proposal.get("route_contract", {})
    if proposal.get("requested_route_id") != "MC-ROUTE-OTP-C-PERMANENT-CIRCUIT" or rc.get("target_claim_ids") != TARGETS:
        errors.append("route proposal target/identity drift")
    if rc.get("initial_route_state") != "submitted" or rc.get("cert_output_initial") is not None:
        errors.append("route proposal authority inflation")

    route = r["route"]
    body = route.get("route", {})
    if route.get("base_registry", {}).get("digest") != EXPECTED_GLOBAL_ROUTES_BLOB:
        errors.append("route base registry substitution")
    if body.get("route_id") != "MC-ROUTE-OTP-C-PERMANENT-CIRCUIT" or body.get("intake_status") != "submitted":
        errors.append("candidate route state drift")
    if body.get("target_claim_ids") != TARGETS or body.get("cert_output") is not None:
        errors.append("candidate route target/output drift")
    if body.get("mathematical_target_proved") is not False or body.get("aggregate_output") is not False:
        errors.append("candidate route authority inflation")
    preserved = route.get("preserved_formula_authority", {})
    if preserved.get("mutable") is not False or preserved.get("variable_leaf_certificate_blob") != EXPECTED_VARIABLE_CERT_BLOB or preserved.get("full_formula_certificate_blob") != EXPECTED_FULL_FORMULA_CERT_BLOB:
        errors.append("formula predecessor preservation drift")

    contract = r["contract"]
    if contract.get("exact_targets") != TARGETS:
        errors.append("adjudication contract target drift")
    if contract.get("admissible_dispositions") != ["adjudication_clear_encoded_targets_only", "adjudication_not_clear", "defer_insufficient_evidence"]:
        errors.append("adjudication vocabulary drift")
    positive = contract.get("positive_gate", {})
    for key in ("fresh_exact_head_replay_required", "fresh_non_author_specialist_review_required", "review_must_bind_exact_subject_head"):
        if positive.get(key) is not True:
            errors.append(f"adjudication positive gate removed: {key}")

    adjudication = r["adjudication"]
    if adjudication.get("state") != "candidate_disposition_pending_exact_head_gates_review_and_protected_merge":
        errors.append("candidate adjudication state inflation")
    if adjudication.get("disposition") != "adjudication_clear_encoded_targets_only" or adjudication.get("encoded_targets") != TARGETS:
        errors.append("candidate adjudication drift")
    judgment = adjudication.get("judgment", {})
    if judgment.get("candidate_clear_for_bounded_output_execution_after_authorization") is not True:
        errors.append("candidate execution gate missing")
    for key in ("mathematical_target_proved", "claim_promotion_authorized", "formula_targets_certified", "other_family_outputs_authorized", "aggregate_authority", "historical_pdf_byte_equivalence"):
        if judgment.get(key) is not False:
            errors.append(f"adjudication authority inflation: {key}")

    out = r["output_contract"]
    permitted = out.get("permitted_output", {})
    if permitted.get("certificate_id") != "MC-OTP-C-PERMANENT-CIRCUIT-QUAL-001" or permitted.get("encoded_targets") != TARGETS:
        errors.append("output contract scope drift")
    order = out.get("publication_order", {})
    for key in ("candidate_authorization_before_execution", "certificate_content_commit_before_route_transition", "route_transition_must_be_direct_child_of_certificate_content_commit", "final_review_after_execution", "ordinary_ancestry_preserving_merge_required", "squash_prohibited", "rebase_prohibited", "protected_main_readback_required"):
        if order.get(key) is not True:
            errors.append(f"output publication gate removed: {key}")

    if staged.get("encoded_targets") != TARGETS:
        errors.append("staged certificate target drift")
    if staged.get("qualification", {}).get("source_projection") != {k: v for k, v in PROJECTION.items() if k != "historical_pdf_byte_equivalence"}:
        errors.append("staged certificate projection drift")
    state = staged.get("state", {})
    if state.get("candidate_only") is not True or state.get("route_state") != "submitted" or state.get("cert_output_inserted") is not False:
        errors.append("staged certificate candidate boundary lost")
    for key in ("mathematical_target_proved", "may_promote_claim", "formula_targets_certified", "aggregate_output"):
        if state.get(key) is not False:
            errors.append(f"staged certificate authority inflation: {key}")

    transition = r["transition"]
    if transition.get("status") != "planned_not_executed" or transition.get("record_type") != "otp_permanent_circuit_staged_route_transition":
        errors.append("staged transition state drift")
    ca = transition.get("candidate_authorization", {})
    if ca.get("reviewed_candidate_head") is not None or ca.get("reviewer") is not None or ca.get("review_id") is not None or ca.get("state") != "pending":
        errors.append("candidate authorization fabricated")
    planned = transition.get("planned_certificate", {})
    if planned.get("certificate_content_commit") is not None or planned.get("digest") is not None:
        errors.append("certificate execution fabricated")
    rt = transition.get("planned_route_transition", {})
    if rt.get("route_transition_commit") is not None or rt.get("cert_output_after") is not None:
        errors.append("route execution fabricated")
    gates = transition.get("publication_constraints", {})
    for key in ("candidate_review_required_before_execution", "certificate_content_commit_before_route_transition", "route_transition_direct_child_required", "fresh_exact_head_replay_required", "fresh_non_author_algebraic_complexity_specialist_approved_review_required", "review_must_bind_final_execution_head", "head_change_requires_revalidation_and_reapproval", "ordinary_ancestry_preserving_merge_required", "squash_prohibited", "rebase_prohibited", "expected_head_required", "protected_main_readback_required", "partial_publication_prohibited"):
        if gates.get(key) is not True:
            errors.append(f"transition publication gate removed: {key}")

    if LIVE_CERT.exists():
        errors.append("live circuit certificate exists before authorized output execution")

    if check_git:
        try:
            if git_blob(GLOBAL_ROUTES) != EXPECTED_GLOBAL_ROUTES_BLOB:
                errors.append("historical certification route registry mutated")
            if git_blob(VARIABLE_CERT) != EXPECTED_VARIABLE_CERT_BLOB:
                errors.append("historical variable-leaf certificate mutated")
            if git_blob(FULL_FORMULA_CERT) != EXPECTED_FULL_FORMULA_CERT_BLOB:
                errors.append("protected full-formula certificate mutated")
            if git_blob(FULL_FORMULA_ROUTE) != EXPECTED_FULL_FORMULA_ROUTE_BLOB:
                errors.append("protected full-formula route overlay mutated")
        except subprocess.CalledProcessError as exc:
            errors.append(f"git identity check failed: {exc}")

    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"OTP Permanent circuit candidate validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print("OTP Permanent circuit candidate chain validates fail-closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
