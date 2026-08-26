#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

import otp_full_formula_contract_membership as membership
import validate_openai_ten_proofs_sphere_packing_route_registration as sphere_registration

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    "PermanentFormulaLowerBound.permanent_divisionFree_formula_lower_bound",
    "PermanentFormulaLowerBound.permanent_rational_formula_lower_bound",
]
PROJECTION = {
    "coefficient_field": "complex",
    "dimension_threshold": 32,
    "log_base": 2,
    "division_free": {"variable_leaves": 128, "total_leaves": 128, "vertices": 128, "internal_gates": 256},
    "rational": {"variable_leaves": 192, "total_leaves": 192, "vertices": 192, "internal_gates": 384},
    "formula_target_count": 2,
    "circuit_target_count": 0,
}
EXPECTED_HISTORICAL_CONTRACT_FILES = {
    "OTP-F-EHRHART.json",
    "OTP-C-PERMANENT.json",
    "OTP-J1-COMPACTNESS.json",
    "OTP-J2-TWO-DEGENERATE.json",
}
PATHS = {
    "intake": ROOT / "governance/result_family_intake_successors/OTP-C-PERMANENT-FULL-FORMULA.json",
    "wp": ROOT / "governance/result_family_work_package_successors/OTP-C-PERMANENT-FULL-FORMULA-CERT-WP01.json",
    "replay": ROOT / "governance/result_family_replay_evidence_successors/OTP-C-PERMANENT-FULL-FORMULA.json",
    "proposal": ROOT / "governance/result_family_route_proposal_successors/OTP-C-PERMANENT-FULL-FORMULA.json",
    "route": ROOT / "governance/certification_route_overlays/OTP-C-PERMANENT-FULL-FORMULA.json",
    "contract": ROOT / "governance/result_family_adjudication_contract_successors/OTP-C-PERMANENT-FULL-FORMULA.json",
    "adjudication": ROOT / "governance/result_family_adjudications/OTP-C-PERMANENT-FULL-FORMULA.json",
    "output_contract": ROOT / "governance/result_family_output_contract_successors/OTP-C-PERMANENT-FULL-FORMULA.json",
    "staged_certificate": ROOT / "governance/result_family_output_candidates/staged_certificates/MC-OTP-C-PERMANENT-FULL-FORMULA-001.json",
    "transition": ROOT / "governance/result_family_output_candidates/staged_route_transitions/OTP-C-PERMANENT-FULL-FORMULA.json",
    "certificate": ROOT / "certificates/formal_sources/MC-OTP-C-PERMANENT-FULL-FORMULA-001.json",
}
SCHEMA = ROOT / "schemas/otp_permanent_full_formula_certification.schema.json"
PREDECESSOR_CERT = ROOT / "certificates/formal_sources/MC-OTP-C-PERMANENT-001.json"
GLOBAL_ROUTES = ROOT / "governance/certification_routes.json"
EXPECTED_PREDECESSOR_CERT_BLOB = "ad10c427270cb1c747ebcacbc5c37e4c1ed1df04"
EXPECTED_GLOBAL_ROUTES_BLOB = "2d17473b4731aa9d9c630b1e7777ad4bd794d993"
EXPECTED_A_REGISTRATION_GLOBAL_ROUTES_BLOB = "b9bb0dc9e18856f50a88162df37c20c034327439"
EXPECTED_OUTPUT_CONTRACT_BLOB = "e234a4bcf55353ed6519e54a41d479b51d93c82c"
EXPECTED_STAGED_CERT_BLOB = "f5b44312672b8c38383d55bd5c41bbdcbafe28fe"
EXPECTED_CERT_BLOB = "2940f551805794b96c7b0793bfe0d14e9fcd9954"
EXPECTED_ROUTE_BLOB = "3a208d3391514de74853f4ad182e26c74f631913"
REVIEWED_CANDIDATE_HEAD = "6aac1679196f7a1fae6aa43318e8f046401f4471"
CONTENT_COMMIT = "1abf088387cbfc33a17fb34e99d23437a6b56164"
ROUTE_COMMIT = "3fe4d77aabd7a2c58480b264577f07871802d92e"
CANDIDATE_ROUTE_BLOB = "ba5bf3c44c68776a0dc4c7e961785dc8629fc6af"
CERT_PATH = "certificates/formal_sources/MC-OTP-C-PERMANENT-FULL-FORMULA-001.json"
ROUTE_PATH = "governance/certification_route_overlays/OTP-C-PERMANENT-FULL-FORMULA.json"
EXPECTED_OUTPUT = {
    "repository": "grandchallenge/MATHCERT",
    "commit_sha": CONTENT_COMMIT,
    "path": CERT_PATH,
    "digest_algorithm": "git_blob_sha1",
    "digest": EXPECTED_CERT_BLOB,
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(ROOT), *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def git_blob(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    return subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", f"HEAD:{rel}"], text=True).strip()


def obj_blob(commit: str, path: str) -> str | None:
    r = git("rev-parse", f"{commit}:{path}")
    return r.stdout.strip() if r.returncode == 0 else None


def parent(commit: str) -> str:
    r = git("rev-parse", f"{commit}^")
    return r.stdout.strip() if r.returncode == 0 else ""


def files(commit: str) -> list[str]:
    r = git("diff-tree", "--no-commit-id", "--name-only", "-r", commit)
    return r.stdout.splitlines() if r.returncode == 0 else []


def ancestor(older: str, newer: str) -> bool:
    return git("merge-base", "--is-ancestor", older, newer).returncode == 0


def records_from_disk():
    return {name: load(path) for name, path in PATHS.items()}


def validation_errors(records=None, *, check_git=True):
    r = records_from_disk() if records is None else records
    errors: list[str] = []
    for name in PATHS:
        if name not in r:
            errors.append(f"missing record: {name}")
    if errors:
        return errors

    errors.extend(membership.membership_errors(ROOT, EXPECTED_HISTORICAL_CONTRACT_FILES))

    staged = r["staged_certificate"]
    schema = load(SCHEMA)
    errors.extend(f"candidate certificate schema: {e.message}" for e in Draft202012Validator(schema).iter_errors(staged))

    intake = r["intake"]
    if intake.get("authority", {}).get("producer_packet", {}).get("digest") != "8755a1067963e5b46555872cb46025fff2625295":
        errors.append("Solve packet substitution")
    if intake.get("authority", {}).get("semantic_record", {}).get("digest") != "520bdaa3bba075e411f7a0a2b8422e9c9d42c818":
        errors.append("Forge semantic substitution")
    overlay = intake.get("authority", {}).get("comparator_overlay", {})
    if overlay.get("json_digest") != "ad102cacd81736f154437826ddefff1cef648f13" or overlay.get("lean_digest") != "8846ebdbae05e31d7d69f0e751a677e927023e48":
        errors.append("Comparator overlay substitution")
    if intake.get("authority", {}).get("nonvacuity_witness_digest") != "e756c8476bac1795f3fb8ca0b7235d3a4a5c59ea":
        errors.append("nonvacuity witness substitution")
    if intake.get("target_scope", {}).get("lean_theorems") != TARGETS:
        errors.append("intake target drift")
    isp = copy.deepcopy(intake.get("target_scope", {}).get("source_projection", {}))
    if isp.pop("historical_pdf_byte_equivalence", None) is not False or isp != PROJECTION:
        errors.append("intake source projection drift")

    wp = r["wp"]
    if wp.get("target_scope", {}).get("lean_theorems") != TARGETS:
        errors.append("work-package target drift")
    if wp.get("execution", {}).get("aggregate_import_required") is not False:
        errors.append("aggregate import enabled")

    replay = r["replay"]
    pr = replay.get("protected_predecessor_replay", {})
    if (pr.get("run"), pr.get("job"), pr.get("lean_version")) != (31807864648, 94791029992, "4.32.0"):
        errors.append("protected replay identity drift")
    if any(pr.get(k) != "accepted" for k in ("lean_default_kernel", "nanoda_kernel", "comparator")):
        errors.append("protected replay acceptance lost")
    if replay.get("fresh_cert_replay", {}).get("exact_head_required") is not True:
        errors.append("fresh exact-head replay not required")

    proposal = r["proposal"]
    if proposal.get("requested_route_id") != "MC-ROUTE-OTP-C-PERMANENT-FULL-FORMULA" or proposal.get("route_contract", {}).get("target_claim_ids") != TARGETS:
        errors.append("route proposal drift")
    if proposal.get("route_contract", {}).get("cert_output_initial") is not None:
        errors.append("route proposal prepopulates cert output")

    contract = r["contract"]
    if contract.get("admissible_dispositions") != ["adjudication_clear_encoded_targets_only", "adjudication_not_clear", "defer_insufficient_evidence"]:
        errors.append("adjudication vocabulary drift")
    if contract.get("exact_targets") != TARGETS or contract.get("positive_gate", {}).get("fresh_non_author_specialist_review_required") is not True:
        errors.append("adjudication contract scope/gate drift")

    adjudication = r["adjudication"]
    if adjudication.get("disposition") != "adjudication_clear_encoded_targets_only" or adjudication.get("encoded_targets") != TARGETS:
        errors.append("adjudication drift")
    if adjudication.get("judgment", {}).get("mathematical_target_proved") is not False:
        errors.append("adjudication proof promotion")
    if adjudication.get("basis", {}).get("fresh_exact_head_replay_required") is not True or adjudication.get("basis", {}).get("fresh_non_author_specialist_review_required") is not True:
        errors.append("adjudication final gate removed")

    out = r["output_contract"]
    permitted = out.get("permitted_output", {})
    if permitted.get("certificate_id") != "MC-OTP-C-PERMANENT-FULL-FORMULA-QUAL-001" or permitted.get("encoded_targets") != TARGETS:
        errors.append("output contract scope drift")
    order = out.get("publication_order", {})
    if order.get("certificate_content_commit_before_route_transition") is not True or order.get("squash_prohibited") is not True or order.get("rebase_prohibited") is not True:
        errors.append("publication ordering weakened")

    if staged.get("record_type") != "otp_permanent_full_formula_qualified_output_candidate" or staged.get("encoded_targets") != TARGETS:
        errors.append("candidate certificate drift")
    if staged.get("qualification", {}).get("source_projection") != PROJECTION:
        errors.append("candidate projection drift")
    if staged.get("state", {}).get("candidate_only") is not True:
        errors.append("candidate certificate lost candidate-only boundary")

    cert = r["certificate"]
    if cert.get("record_type") != "otp_permanent_full_formula_qualified_output":
        errors.append("live certificate record type drift")
    if cert.get("certificate_id") != "MC-OTP-C-PERMANENT-FULL-FORMULA-QUAL-001" or cert.get("encoded_targets") != TARGETS:
        errors.append("live certificate identity/target drift")
    if cert.get("qualification", {}).get("source_projection") != PROJECTION:
        errors.append("live certificate projection drift")
    if cert.get("source_authority", {}).get("output_contract", {}).get("digest") != EXPECTED_OUTPUT_CONTRACT_BLOB:
        errors.append("live certificate output-contract authority drift")
    state = cert.get("state", {})
    if state.get("route_state") != "qualified" or state.get("cert_output_inserted") is not True:
        errors.append("live certificate state drift")
    for key in ("mathematical_target_proved", "may_promote_claim", "circuit_targets_certified", "aggregate_output"):
        if state.get(key) is not False:
            errors.append(f"live certificate authority inflation: {key}")

    route = r["route"]
    body = route.get("route", {})
    if route.get("base_registry", {}).get("digest") != EXPECTED_GLOBAL_ROUTES_BLOB:
        errors.append("route overlay base-registry substitution")
    if body.get("route_id") != "MC-ROUTE-OTP-C-PERMANENT-FULL-FORMULA" or body.get("intake_status") != "qualified":
        errors.append("executed route state drift")
    if body.get("target_claim_ids") != TARGETS or body.get("cert_output") != EXPECTED_OUTPUT:
        errors.append("executed route target/output drift")
    if body.get("mathematical_target_proved") is not False or body.get("aggregate_output") is not False:
        errors.append("route proof/aggregate inflation")
    if route.get("preserved_predecessor", {}).get("mutable") is not False:
        errors.append("predecessor route mutation enabled")

    transition = r["transition"]
    if transition.get("record_type") != "otp_permanent_full_formula_executed_route_transition_receipt":
        errors.append("execution receipt type drift")
    if transition.get("reviewed_candidate_head") != REVIEWED_CANDIDATE_HEAD:
        errors.append("candidate authorization head drift")
    review = transition.get("candidate_authorization_review", {})
    if review.get("reviewer") != "jimsteeg" or review.get("state") != "APPROVED" or review.get("review_id") != "PRR_kwDOSuU7Ic8AAAABJxbnnQ":
        errors.append("candidate authorization review drift")
    executed = transition.get("executed_certificate", {})
    if executed.get("certificate_content_commit") != CONTENT_COMMIT or executed.get("digest") != EXPECTED_CERT_BLOB:
        errors.append("execution receipt certificate drift")
    rt = transition.get("route_transition", {})
    if rt.get("route_transition_commit") != ROUTE_COMMIT or rt.get("overlay_blob_after") != EXPECTED_ROUTE_BLOB or rt.get("cert_output") != EXPECTED_OUTPUT:
        errors.append("execution receipt route transition drift")
    post = transition.get("post_transition", {})
    if post.get("target_claim_ids") != TARGETS:
        errors.append("execution receipt target drift")
    for key in ("mathematical_target_proved", "may_promote_claim", "circuit_targets_certified", "aggregate_output"):
        if post.get(key) is not False:
            errors.append(f"execution receipt authority inflation: {key}")
    gates = transition.get("publication_constraints", {})
    for key in ("fresh_exact_head_replay_required", "fresh_non_author_algebraic_complexity_specialist_approved_review_required", "review_must_bind_final_execution_head", "head_change_requires_revalidation_and_reapproval", "ordinary_ancestry_preserving_merge_required", "squash_prohibited", "rebase_prohibited", "expected_head_required", "protected_main_readback_required", "partial_publication_prohibited"):
        if gates.get(key) is not True:
            errors.append(f"publication gate disabled: {key}")

    if check_git:
        try:
            if git_blob(PREDECESSOR_CERT) != EXPECTED_PREDECESSOR_CERT_BLOB:
                errors.append("historical Permanent certificate mutated")
            global_routes_blob = git_blob(GLOBAL_ROUTES)
            if global_routes_blob != EXPECTED_GLOBAL_ROUTES_BLOB:
                successor_errors = sphere_registration.validation_errors(routes=load(GLOBAL_ROUTES))
                if successor_errors:
                    errors.append("current separately governed A successor is invalid: " + "; ".join(successor_errors))
            if git_blob(PATHS["output_contract"]) != EXPECTED_OUTPUT_CONTRACT_BLOB:
                errors.append("canonical successor output-contract blob drift")
            if git_blob(PATHS["staged_certificate"]) != EXPECTED_STAGED_CERT_BLOB:
                errors.append("candidate certificate blob drift")
            if git_blob(PATHS["certificate"]) != EXPECTED_CERT_BLOB:
                errors.append("live certificate blob drift")
            if git_blob(PATHS["route"]) != EXPECTED_ROUTE_BLOB:
                errors.append("qualified route overlay blob drift")
            head = git("rev-parse", "HEAD").stdout.strip()
            if parent(CONTENT_COMMIT) != REVIEWED_CANDIDATE_HEAD:
                errors.append("certificate-content commit is not direct child of reviewed candidate head")
            if parent(ROUTE_COMMIT) != CONTENT_COMMIT:
                errors.append("route transition is not direct child of certificate-content commit")
            if files(CONTENT_COMMIT) != [CERT_PATH]:
                errors.append("certificate-content commit changed paths outside certificate")
            if files(ROUTE_COMMIT) != [ROUTE_PATH]:
                errors.append("route-transition commit changed paths outside successor route overlay")
            if not ancestor(REVIEWED_CANDIDATE_HEAD, CONTENT_COMMIT) or not ancestor(CONTENT_COMMIT, ROUTE_COMMIT) or not ancestor(ROUTE_COMMIT, head):
                errors.append("output execution ancestry broken")
            if obj_blob(REVIEWED_CANDIDATE_HEAD, CERT_PATH) is not None:
                errors.append("live certificate existed at reviewed candidate head")
            if obj_blob(CONTENT_COMMIT, CERT_PATH) != EXPECTED_CERT_BLOB or obj_blob(ROUTE_COMMIT, CERT_PATH) != EXPECTED_CERT_BLOB or obj_blob(head, CERT_PATH) != EXPECTED_CERT_BLOB:
                errors.append("certificate bytes drift across execution history")
            if obj_blob(REVIEWED_CANDIDATE_HEAD, ROUTE_PATH) != CANDIDATE_ROUTE_BLOB:
                errors.append("candidate route overlay history drift")
            if obj_blob(CONTENT_COMMIT, ROUTE_PATH) != CANDIDATE_ROUTE_BLOB:
                errors.append("route changed in certificate-content commit")
            if obj_blob(ROUTE_COMMIT, ROUTE_PATH) != EXPECTED_ROUTE_BLOB or obj_blob(head, ROUTE_PATH) != EXPECTED_ROUTE_BLOB:
                errors.append("qualified route overlay bytes drift")
        except (subprocess.CalledProcessError, OSError) as exc:
            errors.append(f"git ancestry/blob validation failed: {exc}")

    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("OTP Permanent full-formula output execution validates fail-closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
