#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "governance/pre_route_candidates/OPENAI_TEN_PROOFS_H_GAPCVP_ROUTE_REGISTRATION.json"
ROUTES = ROOT / "governance/certification_routes.json"
PROPOSAL = ROOT / "governance/result_family_route_proposal_successors/OTP-H-GAPCVP.json"
PROPOSAL_REGISTRY = ROOT / "governance/pre_route_candidates/OPENAI_TEN_PROOFS_H_GAPCVP_ROUTE_PROPOSAL.json"
INTAKE = ROOT / "governance/result_family_intake_successors/OTP-H-GAPCVP.json"
WORK_PACKAGE = ROOT / "governance/result_family_work_package_successors/OTP-H-GAPCVP-CERT-WP-001.json"
REPLAY = ROOT / "governance/result_family_replay_evidence_successors/OTP-H-GAPCVP.json"
READBACK = ROOT / "governance/result_family_replay_evidence_readbacks/OTP-H-B1-B2.json"
SCHEMA = ROOT / "schemas/openai_ten_proofs_gapcvp_route_registration.schema.json"

ROUTE_ID = "MC-ROUTE-OTP-H-GAPCVP"
EXPECTED_ROUTES_BLOB = "ffc95950e571efebe1c90a3e6d1bf279b37b71b1"
EXPECTED_BEFORE_BLOB = "4d5c8e3f2b33d5148d98e7057991e167938c75bb"
EXPECTED_PROPOSAL_BLOB = "68062c38d4705ac09e5d1a7f2b177ba5bdd55261"
EXPECTED_PROPOSAL_REGISTRY_BLOB = "bdcddbc5dab3f3e59b86c15a73d0ae79e7e38993"
EXPECTED_INTAKE_BLOB = "a171482c04f62134812ed6084e19a9b803db3478"
EXPECTED_WORK_PACKAGE_BLOB = "0f811d163f0d36b028cf6539963e2cf278517137"
EXPECTED_REPLAY_BLOB = "a12f2c553b71f4daec9255e1f254f48a21f439c3"
EXPECTED_READBACK_BLOB = "fde8ed79681dce929916b524176b236960cac4f6"

TARGETS = [
    "GapCVP.Comparator.gapCVP400IsNPHard",
    "GapCVP.Comparator.binaryNearestCodewordIsNPHard",
    "GapCVP.Comparator.binarySyndromeDecodingIsNPHard",
    "GapCVP.Comparator.finitePNormGapCVPIsNPHard",
]
PROMISES = [
    "GapCVP.Comparator.gapCVP400Promise",
    "GapCVP.Comparator.binaryNearestCodewordPromise",
    "GapCVP.Comparator.binarySyndromeDecodingPromise",
    "GapCVP.Comparator.finitePGapCVPPromise",
]
CLASSIFICATIONS = [
    "source_faithful_restricted_consequence_integer_target",
    "source_faithful_up_to_generator_orientation",
    "source_faithful_restricted_consequence_consistent_syndrome",
    "source_faithful_fixed_rational_p_consequence",
]
GAPS = ["n^(1/400)", "n^(1/200)", "n^(1/200)", "n^(1/(200p))"]
QUALIFICATIONS = [
    "400, 200 and 200p are exponent denominators in dimension-dependent gaps, not constant approximation factors.",
    "The Euclidean formal promise is restricted to integer targets, matching the source Theorem 1 reduction output rather than the source's most general rational-target interface.",
    "The syndrome NO side is restricted to consistent systems sufficient for the source Corollary 15 reduction.",
    "Binary generator row/column orientation is treated only as a transpose convention preserving the represented code.",
    "Malformed/non-encoding and threshold-intermediate bitstrings remain outside the promise.",
    "The finite-p theorem parameter p is fixed rational with 1 <= p and is external to the input encoding.",
    "Forge replay and semantic admission do not independently certify NP-hardness proof correctness.",
]
AXIOMS = ["propext", "Classical.choice", "Quot.sound"]
PRIOR_ROUTE_IDS = {
    "MC-ROUTE-UC-001", "MC-ROUTE-NS-CI-001", "MC-ROUTE-HC-001", "MC-ROUTE-BSD-001",
    "MC-ROUTE-PNP-001", "MC-ROUTE-RH-001", "MC-ROUTE-YM-001", "MC-ROUTE-OZ-001",
    "MC-ROUTE-OTP-F-EHRHART", "MC-ROUTE-OTP-J1-COMPACTNESS",
    "MC-ROUTE-OTP-J2-TWO-DEGENERATE", "MC-ROUTE-OTP-C-PERMANENT-FORMULA",
    "MC-ROUTE-OTP-A-SPHERE-PACKING",
}
FORGE = {
    "repository": "grandchallenge/MATHFORGE",
    "commit_sha": "b9dda1a5b958fd1be37a26324a025013a39584c1",
    "path": "sources/OPENAI-TEN-PROOFS-001/semantic/OTP-H-GAPCVP/audit_record.json",
    "digest_algorithm": "git_blob_sha1",
    "digest": "673f541fbb552d307cc226c51d2f0fd2916b328d",
}
SOLVE = {
    "repository": "grandchallenge/MATHSOLVE",
    "commit_sha": "e42c48dfe6a83eb19f398ba114f61fd700694ce5",
    "path": "work_packages/OPENAI_TEN_PROOFS_WP00/result_family_handoff_successors/OTP-H-GAPCVP.json",
    "digest_algorithm": "git_blob_sha1",
    "digest": "0dd2b38e40a126a1a2a2d57989038f788b8e40e4",
}
SUBJECT = {
    "repository": "openai/ten-proofs",
    "commit": "94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6",
    "tree": "174289e4d4958cb0509874e6e53400e098213de7",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data, usedforsecurity=False).hexdigest()


def open_object_paths(value: Any) -> list[str]:
    found: list[str] = []
    def walk(node: Any, path: str = "") -> None:
        if isinstance(node, dict):
            if node.get("type") == "object" and node.get("additionalProperties") is not False:
                found.append(path or "/")
            for key, child in node.items():
                walk(child, f"{path}/{key}")
        elif isinstance(node, list):
            for i, child in enumerate(node):
                walk(child, f"{path}/{i}")
    walk(value)
    return found


def find_route(routes: dict[str, Any]) -> dict[str, Any]:
    rows = routes.get("routes", [])
    return next((row for row in rows if isinstance(row, dict) and row.get("route_id") == ROUTE_ID), {})


def validation_errors(
    receipt: dict[str, Any] | None = None,
    routes: dict[str, Any] | None = None,
    local_blobs: dict[str, str] | None = None,
) -> list[str]:
    receipt = load(RECEIPT) if receipt is None else receipt
    routes = load(ROUTES) if routes is None else routes
    schema = load(SCHEMA)
    proposal = load(PROPOSAL)
    proposal_registry = load(PROPOSAL_REGISTRY)
    replay = load(REPLAY)
    readback = load(READBACK)
    errors: list[str] = []

    open_paths = open_object_paths(schema)
    if open_paths:
        errors.append(f"registration schema contains open object(s): {open_paths}")
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

    rows = routes.get("routes", [])
    ids = [row.get("route_id") for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []
    if len(ids) != 14 or set(ids) != PRIOR_ROUTE_IDS | {ROUTE_ID}:
        errors.append("route membership drift")
    if ids.count(ROUTE_ID) != 1:
        errors.append("H route membership must be exactly one")
    if any(route_id in ids for route_id in ("MC-ROUTE-OPENAI-TEN-PROOFS-001", "OPENAI-TEN-PROOFS-001")):
        errors.append("aggregate route inserted")
    if routes.get("provider_base_commit") != "284e724d299bac02fc962b68e429b82398f6a08b":
        errors.append("route provider predecessor drift")

    route = find_route(routes)
    expected_boundary = "This submitted route is limited to exactly the four protected OTP-H-GAPCVP promise-hardness targets and promise interfaces. It preserves the dimension-dependent gap exponents, integer-target Euclidean restriction, consistent-syndrome restriction, generator transpose convention, outside-promise boundary, fixed rational p >= 1 boundary, protected source/derived classifications, nonvacuity evidence, and permitted-axiom boundary. It does not adjudicate or prove a target, issue a Cert output, broaden any promise interface, establish whole-document or full proof-body equivalence, qualify another family, transfer cross-family authority, or create aggregate OpenAI Ten Proofs authority."
    if route.get("campaign_id") != "OTP-H-GAPCVP" or route.get("tracker_issue") != "https://github.com/grandchallenge/MATHCERT/issues/190":
        errors.append("H route identity drift")
    if route.get("source_manifest") != FORGE or route.get("intake_packet") != SOLVE:
        errors.append("H route source/Solve authority drift")
    if route.get("target_claim_ids") != TARGETS:
        errors.append("H route target drift")
    if route.get("requested_modalities") != ["LEAN_FORMALIZATION", "SEMANTIC_REPLAY", "SPECIALIST_AUDIT_PENDING"]:
        errors.append("H route modality drift")
    if route.get("intake_status") != "submitted" or route.get("cert_output") is not None:
        errors.append("H route state/output drift")
    if route.get("claim_boundary") != expected_boundary:
        errors.append("H route claim boundary drift")

    authority = receipt.get("authority", {})
    scalar_authority = {
        "proposal_merge": "284e724d299bac02fc962b68e429b82398f6a08b",
        "proposal_reviewed_head": "f1c68cb3c06a4ab5b779f3b3f1134fec53a09ea3",
        "proposal_review_id": 5036003579,
        "proposal_reviewer": "jimsteeg",
        "registration_ci_prerequisite_merge": "6bb06fd65f9f8c418a61206f43fa99aa6f1c797f",
        "registration_ci_prerequisite_head": "75ad62917ca15c7635ccb904e174bb6e98af3945",
        "registered_route_registry_before_blob": EXPECTED_BEFORE_BLOB,
        "registered_route_registry_candidate_blob": EXPECTED_ROUTES_BLOB,
        "cert_intake_merge": "ff9fa0a67a5a809f3519e0059f2ef9b082b1febb",
        "cert_intake_blob": EXPECTED_INTAKE_BLOB,
        "cert_work_package_merge": "10e6f3ee20d7a6e89feb27aef0115fa27710d5e4",
        "cert_work_package_blob": EXPECTED_WORK_PACKAGE_BLOB,
        "cert_replay_evidence_merge": "f34f33b22292ca244956781065fdf84efe2b43f2",
        "cert_replay_evidence_blob": EXPECTED_REPLAY_BLOB,
        "cert_replay_evidence_id": "MC-OTP-H-GAPCVP-REPLAY-EVIDENCE-001",
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
    if authority.get("proposal_record") != {"path":"governance/result_family_route_proposal_successors/OTP-H-GAPCVP.json","digest_algorithm":"git_blob_sha1","digest":EXPECTED_PROPOSAL_BLOB}:
        errors.append("receipt proposal artifact drift")
    if authority.get("proposal_registry") != {"path":"governance/pre_route_candidates/OPENAI_TEN_PROOFS_H_GAPCVP_ROUTE_PROPOSAL.json","digest_algorithm":"git_blob_sha1","digest":EXPECTED_PROPOSAL_REGISTRY_BLOB}:
        errors.append("receipt proposal registry artifact drift")

    reg = receipt.get("registration", {})
    if reg.get("route_status") != "submitted" or reg.get("target_count") != 4:
        errors.append("registration state/count drift")
    if reg.get("target_claim_ids") != TARGETS:
        errors.append("registration target drift")
    if reg.get("promise_interfaces") != PROMISES:
        errors.append("registration promise drift")
    if reg.get("classifications") != CLASSIFICATIONS:
        errors.append("registration classification drift")
    if reg.get("gap_factors") != GAPS:
        errors.append("registration gap-factor drift")
    if reg.get("mandatory_qualifications") != QUALIFICATIONS:
        errors.append("registration qualification drift")
    if reg.get("permitted_axioms") != AXIOMS:
        errors.append("registration axiom drift")
    if reg.get("nonvacuity_state") != "protected_replay_nonvacuity_clear":
        errors.append("registration nonvacuity drift")

    state = receipt.get("state", {})
    if state != {"registered_route_count_created_by_this_operation":1,"submitted_route_count":1,"adjudication_count":0,"cert_output_count":0,"mathematical_target_proved_count":0,"aggregate_route_count":0}:
        errors.append("registration state inflation")
    controls = receipt.get("route_controls", {})
    expected_controls = {
        "registration_scope":"exact_one_gapcvp_four_target_promise_route",
        "may_adjudicate":False,"may_issue_cert_output":False,"may_mark_target_proved":False,"may_promote_claim":False,
        "cross_family_transfer_prohibited":True,"aggregate_route_prohibited":True,
        "may_broaden_integer_target":False,"may_broaden_consistent_syndrome":False,
        "may_totalize_outside_promise":False,"may_make_p_input_dependent":False,
        "may_reinterpret_gap_denominators_as_constants":False,
        "whole_document_equivalence_established":False,"full_proof_body_equivalence_established":False,
    }
    if controls != expected_controls:
        errors.append("registration control drift/inflation")

    if proposal.get("proposal_state") != "proposed_only" or proposal.get("requested_route_id") != ROUTE_ID:
        errors.append("protected proposal state/identity drift")
    pscope = proposal.get("target_scope", {})
    if pscope.get("lean_theorems") != TARGETS or pscope.get("promise_interfaces") != PROMISES or pscope.get("classifications") != CLASSIFICATIONS or pscope.get("gap_factors") != GAPS:
        errors.append("protected proposal scope drift")
    if pscope.get("mandatory_qualifications") != QUALIFICATIONS or pscope.get("permitted_axioms") != AXIOMS:
        errors.append("protected proposal qualification/axiom drift")
    pcontrols = proposal.get("route_controls", {})
    if pcontrols.get("may_register_route") is not False or pcontrols.get("may_adjudicate") is not False or pcontrols.get("cert_output") is not None or pcontrols.get("mathematical_target_proved") is not False:
        errors.append("historical proposal authority inflated")

    if proposal_registry.get("proposal", {}).get("requested_route_id") != ROUTE_ID:
        errors.append("proposal registry route identity drift")
    if proposal_registry.get("state") != {"proposal_count":1,"registered_route_count_created_by_this_operation":0,"adjudication_count":0,"cert_output_count":0,"mathematical_target_proved_count":0,"aggregate_route_count":0}:
        errors.append("historical proposal registry state drift")
    if replay.get("route_state", {}).get("route_proposed") is not False or replay.get("route_state", {}).get("route_registered") is not False:
        errors.append("historical replay route state inflated")
    h = next((f for f in readback.get("families", []) if f.get("result_family") == "OTP-H-GAPCVP"), None)
    if not h or h.get("protected_merge") != "f34f33b22292ca244956781065fdf84efe2b43f2" or h.get("terminal_disposition") != "H_REPLAY_EVIDENCE_PROTECTED__ZERO_ROUTE_OUTPUT_AUTHORITY":
        errors.append("H protected replay readback drift")

    forbidden = [
        ROOT / "governance/result_family_adjudications/OTP-H-GAPCVP.json",
        ROOT / "certificates/formal_sources/MC-OTP-H-GAPCVP-001.json",
    ]
    if any(path.exists() for path in forbidden):
        errors.append("premature H adjudication/output artifact exists")

    if receipt.get("candidate_disposition") != "H_GAPCVP_CERT_ROUTE_REGISTERED__NO_ADJUDICATION_OR_OUTPUT_AUTHORITY":
        errors.append("candidate disposition drift")
    activation = receipt.get("activation", {})
    for phrase in ("canonical Cert", "validator and test reached canonically", "fresh non-author lattice/complexity/Lean specialist APPROVED review", "expected-head merge", "protected-main readback"):
        if phrase not in activation.get("condition", ""):
            errors.append(f"activation gate missing: {phrase}")
    if activation.get("head_change_requires_reapproval") is not True or activation.get("effect") != "gapcvp_route_registered_no_adjudication_no_output":
        errors.append("activation semantics drift")

    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("validated OTP-H GapCVP submitted route registration; no adjudication or output authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
