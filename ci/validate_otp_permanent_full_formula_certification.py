#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

import otp_full_formula_contract_membership as membership

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
    "certificate": ROOT / "governance/result_family_output_candidates/staged_certificates/MC-OTP-C-PERMANENT-FULL-FORMULA-001.json",
    "transition": ROOT / "governance/result_family_output_candidates/staged_route_transitions/OTP-C-PERMANENT-FULL-FORMULA.json",
}
SCHEMA = ROOT / "schemas/otp_permanent_full_formula_certification.schema.json"
PREDECESSOR_CERT = ROOT / "certificates/formal_sources/MC-OTP-C-PERMANENT-001.json"
ACTUAL_NEW_CERT = ROOT / "certificates/formal_sources/MC-OTP-C-PERMANENT-FULL-FORMULA-001.json"
GLOBAL_ROUTES = ROOT / "governance/certification_routes.json"
EXPECTED_PREDECESSOR_CERT_BLOB = "ad10c427270cb1c747ebcacbc5c37e4c1ed1df04"
EXPECTED_GLOBAL_ROUTES_BLOB = "2d17473b4731aa9d9c630b1e7777ad4bd794d993"
EXPECTED_OUTPUT_CONTRACT_BLOB = "e234a4bcf55353ed6519e54a41d479b51d93c82c"
EXPECTED_STAGED_CERT_BLOB = "f5b44312672b8c38383d55bd5c41bbdcbafe28fe"
EXPECTED_STAGED_CERT_COMMIT = "cb67f6b22f5257afd4ecc66cfe3c1d46cfa1be8c"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    return subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", f"HEAD:{rel}"], text=True).strip()


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

    schema = load(SCHEMA)
    errors.extend(f"certificate schema: {e.message}" for e in Draft202012Validator(schema).iter_errors(r["certificate"]))

    for name, rec in r.items():
        if name == "route":
            surface = rec.get("route", {}).get("campaign_id")
            if surface != "OTP-C-PERMANENT-FULL-FORMULA":
                errors.append("route campaign drift")
            continue
        if rec.get("surface_id") != "OTP-C-PERMANENT-FULL-FORMULA":
            errors.append(f"{name}: surface drift")
        if rec.get("result_family", "OTP-C-PERMANENT") != "OTP-C-PERMANENT":
            errors.append(f"{name}: result family drift")

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
    state = intake.get("state", {})
    if state.get("route_registered") is not False or state.get("adjudication") is not None or state.get("cert_output") is not None:
        errors.append("intake authority inflation")

    wp = r["wp"]
    if wp.get("target_scope", {}).get("lean_theorems") != TARGETS:
        errors.append("work-package target drift")
    wsp = copy.deepcopy(wp.get("target_scope", {}).get("source_projection", {}))
    if wsp.pop("historical_pdf_byte_equivalence", None) is not False or wsp != PROJECTION:
        errors.append("work-package source projection drift")
    if wp.get("execution", {}).get("aggregate_import_required") is not False:
        errors.append("aggregate import enabled")
    if wp.get("execution", {}).get("immutable_archive_overlay_mode") != "copy_protected_forge_overlay_into_ephemeral_worktree":
        errors.append("overlay execution mode drift")

    replay = r["replay"]
    pr = replay.get("protected_predecessor_replay", {})
    if (pr.get("run"), pr.get("job"), pr.get("lean_version")) != (31807864648, 94791029992, "4.32.0"):
        errors.append("protected replay identity drift")
    if any(pr.get(k) != "accepted" for k in ("lean_default_kernel", "nanoda_kernel", "comparator")):
        errors.append("protected replay acceptance lost")
    if replay.get("fresh_cert_replay", {}).get("exact_head_required") is not True:
        errors.append("fresh exact-head replay not required")

    proposal = r["proposal"]
    if proposal.get("requested_route_id") != "MC-ROUTE-OTP-C-PERMANENT-FULL-FORMULA":
        errors.append("route proposal id drift")
    if proposal.get("route_contract", {}).get("target_claim_ids") != TARGETS:
        errors.append("route proposal target drift")
    if proposal.get("route_contract", {}).get("cert_output_initial") is not None:
        errors.append("route proposal prepopulates cert output")

    route = r["route"]
    route_body = route.get("route", {})
    if route.get("base_registry", {}).get("digest") != EXPECTED_GLOBAL_ROUTES_BLOB:
        errors.append("route overlay base-registry substitution")
    if route_body.get("route_id") != "MC-ROUTE-OTP-C-PERMANENT-FULL-FORMULA":
        errors.append("route id drift")
    if route_body.get("intake_status") != "submitted" or route_body.get("cert_output") is not None:
        errors.append("live candidate route must remain submitted/no-output")
    if route_body.get("target_claim_ids") != TARGETS:
        errors.append("registered route target drift")
    if route_body.get("mathematical_target_proved") is not False or route_body.get("aggregate_output") is not False:
        errors.append("route proof/aggregate inflation")

    contract = r["contract"]
    if contract.get("admissible_dispositions") != ["adjudication_clear_encoded_targets_only", "adjudication_not_clear", "defer_insufficient_evidence"]:
        errors.append("adjudication vocabulary drift")
    if contract.get("exact_targets") != TARGETS:
        errors.append("adjudication contract target drift")
    if contract.get("positive_gate", {}).get("fresh_non_author_specialist_review_required") is not True:
        errors.append("specialist review gate removed")

    adjudication = r["adjudication"]
    if adjudication.get("disposition") != "adjudication_clear_encoded_targets_only":
        errors.append("unexpected candidate adjudication disposition")
    if adjudication.get("encoded_targets") != TARGETS:
        errors.append("adjudication target drift")
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

    cert = r["certificate"]
    if cert.get("encoded_targets") != TARGETS:
        errors.append("staged certificate target drift")
    csp = cert.get("qualification", {}).get("source_projection", {})
    if csp != PROJECTION:
        errors.append("staged certificate source projection drift")
    if cert.get("source_authority", {}).get("output_contract") != {
        "path": "governance/result_family_output_contract_successors/OTP-C-PERMANENT-FULL-FORMULA.json",
        "digest_algorithm": "git_blob_sha1",
        "digest": EXPECTED_OUTPUT_CONTRACT_BLOB,
    }:
        errors.append("staged certificate output-contract authority drift")
    if cert.get("state", {}).get("mathematical_target_proved") is not False or cert.get("state", {}).get("aggregate_output") is not False:
        errors.append("staged certificate proof/aggregate inflation")
    if cert.get("protected_effect") != "none_until_exact_head_gates_fresh_non_author_specialist_approval_and_protected_publication":
        errors.append("staged certificate protected-effect inflation")

    transition = r["transition"]
    if transition.get("certificate_content", {}).get("digest") != EXPECTED_STAGED_CERT_BLOB:
        errors.append("staged transition certificate digest drift")
    if transition.get("certificate_content", {}).get("content_commit") != EXPECTED_STAGED_CERT_COMMIT:
        errors.append("staged transition certificate commit drift")
    if transition.get("post_transition", {}).get("target_claim_ids") != TARGETS:
        errors.append("staged transition target drift")
    if transition.get("post_transition", {}).get("mathematical_target_proved") is not False or transition.get("post_transition", {}).get("aggregate_output") is not False:
        errors.append("staged transition proof/aggregate inflation")

    if ACTUAL_NEW_CERT.exists():
        errors.append("protected certificate path populated before publication authorization")

    if check_git:
        try:
            if git_blob(PREDECESSOR_CERT) != EXPECTED_PREDECESSOR_CERT_BLOB:
                errors.append("historical Permanent certificate mutated")
            if git_blob(GLOBAL_ROUTES) != EXPECTED_GLOBAL_ROUTES_BLOB:
                errors.append("global certification route registry mutated")
            if git_blob(PATHS["output_contract"]) != EXPECTED_OUTPUT_CONTRACT_BLOB:
                errors.append("canonical successor output-contract blob drift")
            if git_blob(PATHS["certificate"]) != EXPECTED_STAGED_CERT_BLOB:
                errors.append("staged certificate blob drift")
            subprocess.check_call(["git", "-C", str(ROOT), "merge-base", "--is-ancestor", EXPECTED_STAGED_CERT_COMMIT, "HEAD"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except (subprocess.CalledProcessError, OSError) as exc:
            errors.append(f"git ancestry/blob validation failed: {exc}")

    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("OTP Permanent full-formula certification candidate validates fail-closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
