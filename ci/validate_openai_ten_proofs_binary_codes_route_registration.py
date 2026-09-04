#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

import certification_route_state as route_state

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "governance/pre_route_candidates/OPENAI_TEN_PROOFS_B1_BINARY_CODES_ROUTE_REGISTRATION.json"
ROUTES = ROOT / route_state.ROUTES_REL
PROPOSAL = ROOT / "governance/result_family_route_proposal_successors/OTP-B1-BINARY-CODES.json"
PROPOSAL_REGISTRY = ROOT / "governance/pre_route_candidates/OPENAI_TEN_PROOFS_B1_BINARY_CODES_ROUTE_PROPOSAL.json"
INTAKE = ROOT / "governance/result_family_intake_successors/OTP-B1-BINARY-CODES.json"
WORK_PACKAGE = ROOT / "governance/result_family_work_package_successors/OTP-B1-BINARY-CODES-CERT-WP-001.json"
REPLAY = ROOT / "governance/result_family_replay_evidence_successors/OTP-B1-BINARY-CODES.json"
READBACK = ROOT / "governance/result_family_replay_evidence_readbacks/OTP-H-B1-B2.json"
SCHEMA = ROOT / "schemas/openai_ten_proofs_binary_codes_route_registration.schema.json"

FAMILY = "OTP-B1-BINARY-CODES"
ROUTE_ID = "MC-ROUTE-OTP-B1-BINARY-CODES"
PROPOSAL_MERGE = "d782c2f451f0ec2f0f88fbc0c76b9914809fac54"
PROPOSAL_HEAD = "8caa9d4ef2df4c5c325e679456b72e006c2a2945"
PROPOSAL_REVIEW_ID = 5108399809
PREREQUISITE_MERGE = "e6237705f3153345f88948dad855ba2662b0f553"
PREREQUISITE_HEAD = "ee56b18eba93dc2098a1d12519f395304c9acd81"
EXPECTED_BEFORE_BLOB = "ffc95950e571efebe1c90a3e6d1bf279b37b71b1"
EXPECTED_ROUTES_BLOB = "94ba63af418cc8299b1f3197f9eead53d61ab61d"
EXPECTED_PROPOSAL_BLOB = "d476d4ab8c018f38cb604d4570d43619fca6d25b"
EXPECTED_PROPOSAL_REGISTRY_BLOB = "833439191db393d2e2b48b2b005e0f9497bff481"
EXPECTED_INTAKE_BLOB = "9ba1e66679d5d46aceef16164194147d8fac530a"
EXPECTED_WORK_PACKAGE_BLOB = "19e1eaf5e24ce212bb020c8c40d4177ff5b4f8f9"
EXPECTED_REPLAY_BLOB = "fd669ae6cfc39110560656c2123d5d4449200830"
EXPECTED_READBACK_BLOB = "fde8ed79681dce929916b524176b236960cac4f6"

TARGETS = [
    "MetricCodes.Hamming.binaryRate_lt_classicalRate",
    "MetricCodes.Hamming.exists_binaryRate_improvement",
    "MetricCodes.Johnson.binaryRate_le_combinedVariationalRate",
    "MetricCodes.MRRW.strict_mrrw2",
    "MetricCodes.Johnson.binaryRate_lt_mrrw",
    "MetricCodes.Johnson.exists_binaryRate_mrrw_improvement",
]
CLASSIFICATIONS = [
    "source_faithful_derived_consequence",
    "derived_positive_margin_certificate",
    "source_faithful_exact_projection",
    "source_faithful_exact_projection",
    "source_faithful_derived_consequence",
    "derived_positive_margin_certificate",
]
QUALIFICATIONS = [
    "The two positive-margin existential targets are derived certificate normal forms, not source-verbatim statements.",
    "The Lean sInf representation of M2 is source-equivalent only through the protected minimizer-existence and attainment bridge on the target domain.",
    "Binary-rate logarithm base, ceiling convention, strict spectral feasibility, and variational domains remain exactly as protected by the Forge audit.",
    "No whole-chapter semantic equivalence or full proof-body comparison is established.",
    "Forge semantic admission and replay do not independently certify the source proof.",
]
AXIOMS = ["propext", "Quot.sound", "Classical.choice"]
FORGE = {
    "repository": "grandchallenge/MATHFORGE",
    "commit_sha": "24a1fa0f020ee9cc7fbe2e7aea4cd840268ca748",
    "path": "sources/OPENAI-TEN-PROOFS-001/semantic/OTP-B1-BINARY-CODES/audit_record.json",
    "digest_algorithm": "git_blob_sha1",
    "digest": "0ab4d973bc046084e9d2dc6c7552ab5428d7412d",
}
SOLVE = {
    "repository": "grandchallenge/MATHSOLVE",
    "commit_sha": "7858f1350439e6324bdee149931bdb7661098729",
    "path": "work_packages/OPENAI_TEN_PROOFS_WP00/result_family_handoff_successors/OTP-B1-BINARY-CODES.json",
    "digest_algorithm": "git_blob_sha1",
    "digest": "1847dd7a17cda51cb02f017766c59d372811fb12",
}
SUBJECT = {
    "repository": "openai/ten-proofs",
    "commit": "94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6",
    "tree": "174289e4d4958cb0509874e6e53400e098213de7",
}
PRIOR_ROUTE_IDS = {
    "MC-ROUTE-UC-001", "MC-ROUTE-NS-CI-001", "MC-ROUTE-HC-001", "MC-ROUTE-BSD-001",
    "MC-ROUTE-PNP-001", "MC-ROUTE-RH-001", "MC-ROUTE-YM-001", "MC-ROUTE-OZ-001",
    "MC-ROUTE-OTP-F-EHRHART", "MC-ROUTE-OTP-J1-COMPACTNESS",
    "MC-ROUTE-OTP-J2-TWO-DEGENERATE", "MC-ROUTE-OTP-C-PERMANENT-FORMULA",
    "MC-ROUTE-OTP-A-SPHERE-PACKING", "MC-ROUTE-OTP-H-GAPCVP",
}
ROUTE_BOUNDARY = (
    "This submitted route is limited to exactly the six protected OTP-B1-BINARY-CODES targets and their protected source-versus-derived classifications. "
    "The two positive-margin existential targets remain derived certificate normal forms rather than source-verbatim statements; the Lean sInf representation of M2 remains source-equivalent only through the protected minimizer-existence and attainment bridge; and the protected logarithm-base, ceiling, strict spectral-feasibility, and variational-domain qualifications remain unchanged. "
    "It does not adjudicate or prove a target, issue a Cert output, establish whole-chapter or full proof-body equivalence, qualify another family, transfer cross-family authority, or create aggregate OpenAI Ten Proofs authority."
)
ROUTE_BLOCKERS = [
    "No MATHCERT adjudication has been authorized or recorded for OTP-B1-BINARY-CODES.",
    "The two positive-margin existential targets remain derived certificate normal forms rather than source-verbatim statements, and the MRRW sInf representation remains governed by the protected minimizer-existence and attainment bridge.",
    "Forge semantic admission, Solve handoff, and replay evidence do not independently certify the source proof; whole-chapter and full proof-body equivalence remain unestablished.",
]
ROUTE_REOPEN = [
    "Update this route only through a separately governed, exact-head reviewed operation when the six-target scope, source/derived classifications, source/Solve/intake/work-package/replay/proposal authority, minimizer-attainment bridge, permitted axioms, adjudication state, output state, or mathematical proof status changes."
]


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data, usedforsecurity=False).hexdigest()


def find_route(routes: dict[str, Any]) -> dict[str, Any]:
    return next((row for row in routes.get("routes", []) if isinstance(row, dict) and row.get("route_id") == ROUTE_ID), {})


def validation_errors(
    receipt: dict[str, Any] | None = None,
    routes: dict[str, Any] | None = None,
    local_blobs: dict[str, str] | None = None,
) -> list[str]:
    receipt = load(RECEIPT) if receipt is None else receipt
    routes = load(ROUTES) if routes is None else routes
    proposal = load(PROPOSAL)
    proposal_registry = load(PROPOSAL_REGISTRY)
    intake = load(INTAKE)
    work_package = load(WORK_PACKAGE)
    replay = load(REPLAY)
    readback = load(READBACK)
    schema = load(SCHEMA)
    errors: list[str] = []

    for err in sorted(Draft202012Validator(schema).iter_errors(receipt), key=lambda e: list(e.path)):
        errors.append(f"schema: {'/'.join(map(str, err.path))}: {err.message}")

    blobs = {
        "routes": git_blob_sha1(ROUTES),
        "proposal": git_blob_sha1(PROPOSAL),
        "proposal_registry": git_blob_sha1(PROPOSAL_REGISTRY),
        "intake": git_blob_sha1(INTAKE),
        "work_package": git_blob_sha1(WORK_PACKAGE),
        "replay": git_blob_sha1(REPLAY),
        "readback": git_blob_sha1(READBACK),
    }
    if local_blobs:
        blobs.update(local_blobs)
    expected_blobs = {
        "routes": EXPECTED_ROUTES_BLOB,
        "proposal": EXPECTED_PROPOSAL_BLOB,
        "proposal_registry": EXPECTED_PROPOSAL_REGISTRY_BLOB,
        "intake": EXPECTED_INTAKE_BLOB,
        "work_package": EXPECTED_WORK_PACKAGE_BLOB,
        "replay": EXPECTED_REPLAY_BLOB,
        "readback": EXPECTED_READBACK_BLOB,
    }
    for key, expected in expected_blobs.items():
        if blobs.get(key) != expected:
            errors.append(f"{key} blob drift: {blobs.get(key)} != {expected}")

    try:
        if route_state.blob_at(PROPOSAL_MERGE) != EXPECTED_BEFORE_BLOB:
            errors.append("protected predecessor route blob drift")
    except Exception as exc:
        errors.append(f"protected predecessor route read failed: {exc}")

    rows = routes.get("routes", [])
    ids = [row.get("route_id") for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []
    if len(ids) != 15 or set(ids) != PRIOR_ROUTE_IDS | {ROUTE_ID}:
        errors.append("route membership drift")
    if ids.count(ROUTE_ID) != 1:
        errors.append("B1 route membership must be exactly one")
    if any(route_id in ids for route_id in ("MC-ROUTE-OPENAI-TEN-PROOFS-001", "OPENAI-TEN-PROOFS-001")):
        errors.append("aggregate route inserted")
    if routes.get("provider_base_commit") != PROPOSAL_MERGE:
        errors.append("route provider predecessor drift")

    route = find_route(routes)
    expected_route = {
        "route_id": ROUTE_ID,
        "campaign_id": FAMILY,
        "tracker_issue": "https://github.com/grandchallenge/MATHCERT/issues/205",
        "source_manifest": FORGE,
        "intake_status": "submitted",
        "intake_packet": SOLVE,
        "target_claim_ids": TARGETS,
        "requested_modalities": ["LEAN_FORMALIZATION", "SEMANTIC_REPLAY", "SPECIALIST_AUDIT_PENDING"],
        "claim_boundary": ROUTE_BOUNDARY,
        "cert_output": None,
        "blockers": ROUTE_BLOCKERS,
        "reopening_conditions": ROUTE_REOPEN,
    }
    if route != expected_route:
        errors.append("B1 route record drift")

    authority = receipt.get("authority", {})
    scalar_authority = {
        "proposal_merge": PROPOSAL_MERGE,
        "proposal_reviewed_head": PROPOSAL_HEAD,
        "proposal_review_id": PROPOSAL_REVIEW_ID,
        "proposal_reviewer": "jimsteeg",
        "registration_ci_prerequisite_merge": PREREQUISITE_MERGE,
        "registration_ci_prerequisite_head": PREREQUISITE_HEAD,
        "registered_route_registry_before_blob": EXPECTED_BEFORE_BLOB,
        "registered_route_registry_candidate_blob": EXPECTED_ROUTES_BLOB,
        "cert_intake_merge": "5bddc3eb7d02638cf4fe959accfbfeade4964592",
        "cert_intake_blob": EXPECTED_INTAKE_BLOB,
        "cert_work_package_merge": "83a8951a89a72a892d5fdc132d6a22e508d6cdc2",
        "cert_work_package_blob": EXPECTED_WORK_PACKAGE_BLOB,
        "cert_replay_evidence_merge": "d8daab1c0deec3d41ac438714e21ee752c14ac46",
        "cert_replay_evidence_blob": EXPECTED_REPLAY_BLOB,
        "cert_replay_evidence_id": "MC-OTP-B1-BINARY-CODES-REPLAY-EVIDENCE-001",
        "cert_replay_readback_merge": "1e64a4c147cb8f35255d3effa80342ce64ee3682",
        "cert_replay_readback_blob": EXPECTED_READBACK_BLOB,
    }
    for key, expected in scalar_authority.items():
        if authority.get(key) != expected:
            errors.append(f"receipt authority drift: {key}")
    if authority.get("forge_semantic") != FORGE:
        errors.append("receipt Forge authority drift")
    if authority.get("solve_handoff") != SOLVE:
        errors.append("receipt Solve authority drift")
    if authority.get("official_subject") != SUBJECT:
        errors.append("receipt formal subject drift")
    if authority.get("proposal_record") != {"path":"governance/result_family_route_proposal_successors/OTP-B1-BINARY-CODES.json","digest_algorithm":"git_blob_sha1","digest":EXPECTED_PROPOSAL_BLOB}:
        errors.append("receipt proposal artifact drift")
    if authority.get("proposal_registry") != {"path":"governance/pre_route_candidates/OPENAI_TEN_PROOFS_B1_BINARY_CODES_ROUTE_PROPOSAL.json","digest_algorithm":"git_blob_sha1","digest":EXPECTED_PROPOSAL_REGISTRY_BLOB}:
        errors.append("receipt proposal registry artifact drift")

    reg = receipt.get("registration", {})
    if reg.get("route_status") != "submitted" or reg.get("target_count") != 6:
        errors.append("registration state/count drift")
    if reg.get("target_claim_ids") != TARGETS:
        errors.append("registration target drift")
    if reg.get("classifications") != CLASSIFICATIONS:
        errors.append("registration classification drift")
    if reg.get("mandatory_qualifications") != QUALIFICATIONS:
        errors.append("registration qualification drift")
    if reg.get("permitted_axioms") != AXIOMS:
        errors.append("registration axiom drift")
    if reg.get("nonvacuity_state") != "protected_replay_nonvacuity_clear":
        errors.append("registration nonvacuity drift")
    if reg.get("minimizer_attainment_state") != "protected_bridge_clear":
        errors.append("registration minimizer-attainment drift")

    expected_state = {"registered_route_count_created_by_this_operation":1,"submitted_route_count":1,"adjudication_count":0,"cert_output_count":0,"mathematical_target_proved_count":0,"aggregate_route_count":0}
    if receipt.get("state") != expected_state:
        errors.append("registration state inflation")
    expected_controls = {
        "registration_scope":"exact_one_binary_codes_six_target_route",
        "may_adjudicate":False,"may_issue_cert_output":False,"may_mark_target_proved":False,"may_promote_claim":False,
        "cross_family_transfer_prohibited":True,"aggregate_route_prohibited":True,
        "may_reclassify_derived_as_source_verbatim":False,"may_remove_minimizer_attainment_bridge":False,
        "may_broaden_logarithm_base":False,"may_broaden_ceiling_convention":False,
        "may_broaden_spectral_feasibility":False,"may_broaden_variational_domains":False,
        "whole_document_equivalence_established":False,"full_proof_body_equivalence_established":False,
    }
    if receipt.get("route_controls") != expected_controls:
        errors.append("registration control drift/inflation")

    if proposal.get("proposal_state") != "proposed_only" or proposal.get("requested_route_id") != ROUTE_ID:
        errors.append("protected proposal state/identity drift")
    pscope = proposal.get("target_scope", {})
    if pscope.get("lean_theorems") != TARGETS or pscope.get("classifications") != CLASSIFICATIONS:
        errors.append("protected proposal target/classification drift")
    if pscope.get("mandatory_qualifications") != QUALIFICATIONS or pscope.get("permitted_axioms") != AXIOMS:
        errors.append("protected proposal qualification/axiom drift")
    if pscope.get("minimizer_attainment_state") != "protected_bridge_clear":
        errors.append("protected proposal minimizer-attainment drift")
    pcontrols = proposal.get("route_controls", {})
    if pcontrols.get("may_register_route") is not False or pcontrols.get("may_adjudicate") is not False or pcontrols.get("cert_output") is not None or pcontrols.get("mathematical_target_proved") is not False:
        errors.append("historical proposal authority inflated")

    if proposal_registry.get("proposal", {}).get("requested_route_id") != ROUTE_ID:
        errors.append("proposal registry route identity drift")
    if proposal_registry.get("state") != {"proposal_count":1,"registered_route_count_created_by_this_operation":0,"adjudication_count":0,"cert_output_count":0,"mathematical_target_proved_count":0,"aggregate_route_count":0}:
        errors.append("historical proposal registry state drift")

    if intake.get("state", {}).get("route_registered") is not False or intake.get("state", {}).get("may_adjudicate") is not False:
        errors.append("historical intake authority inflated")
    if work_package.get("state", {}).get("route_registered") is not False or work_package.get("state", {}).get("may_adjudicate") is not False:
        errors.append("historical work-package authority inflated")
    if replay.get("route_state", {}).get("route_proposed") is not False or replay.get("route_state", {}).get("route_registered") is not False:
        errors.append("historical replay route state inflated")
    b1 = next((f for f in readback.get("families", []) if f.get("result_family") == FAMILY), None)
    if not b1 or b1.get("protected_merge") != "d8daab1c0deec3d41ac438714e21ee752c14ac46" or b1.get("terminal_disposition") != "B1_REPLAY_EVIDENCE_PROTECTED__ZERO_ROUTE_OUTPUT_AUTHORITY":
        errors.append("B1 protected replay readback drift")

    forbidden = [
        ROOT / "governance/result_family_adjudications/OTP-B1-BINARY-CODES.json",
        ROOT / "certificates/formal_sources/MC-OTP-B1-BINARY-CODES-001.json",
    ]
    if any(path.exists() for path in forbidden):
        errors.append("premature B1 adjudication/output artifact exists")

    if receipt.get("candidate_disposition") != "B1_BINARY_CODES_CERT_ROUTE_REGISTERED__NO_ADJUDICATION_OR_OUTPUT_AUTHORITY":
        errors.append("candidate disposition drift")
    activation = receipt.get("activation", {})
    for phrase in ("canonical Cert", "MATHCERT_CANONICAL_SCOPE=OTP-B1-BINARY-CODES", "validator and test reached canonically", "fresh non-author coding-theory/Lean specialist APPROVED review", "expected-head merge", "protected-main readback"):
        if phrase not in activation.get("condition", ""):
            errors.append(f"activation gate missing: {phrase}")
    if activation.get("head_change_requires_reapproval") is not True or activation.get("effect") != "binary_codes_route_registered_no_adjudication_no_output":
        errors.append("activation semantics drift")

    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("validated OTP-B1 Binary Codes submitted route registration; no adjudication or output authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
