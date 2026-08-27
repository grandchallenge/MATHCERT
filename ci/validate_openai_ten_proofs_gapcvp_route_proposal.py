#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "governance/result_family_route_proposal_successors/OTP-H-GAPCVP.json"
REGISTRY = ROOT / "governance/pre_route_candidates/OPENAI_TEN_PROOFS_H_GAPCVP_ROUTE_PROPOSAL.json"
ROUTES = ROOT / "governance/certification_routes.json"
ROUTE_REGISTRY_PATH = "governance/certification_routes.json"
PROPOSAL_PROTECTED_PREDECESSOR_HEAD = "0c3e3399a39c01d64fa9fff9621f841d706e0171"
INTAKE = ROOT / "governance/result_family_intake_successors/OTP-H-GAPCVP.json"
WORK_PACKAGE = ROOT / "governance/result_family_work_package_successors/OTP-H-GAPCVP-CERT-WP-001.json"
REPLAY = ROOT / "governance/result_family_replay_evidence_successors/OTP-H-GAPCVP.json"
READBACK = ROOT / "governance/result_family_replay_evidence_readbacks/OTP-H-B1-B2.json"
SCHEMAS = (
    ROOT / "schemas/openai_ten_proofs_gapcvp_route_proposal.schema.json",
    ROOT / "schemas/openai_ten_proofs_gapcvp_route_proposal_registry.schema.json",
)

TRACKER = "https://github.com/grandchallenge/MATHCERT/issues/190"
ROUTE_ID = "MC-ROUTE-OTP-H-GAPCVP"
PROPOSAL_ID = "MC-OTP-ROUTE-PROPOSAL-H-GAPCVP"
PROPOSAL_BLOB = "68062c38d4705ac09e5d1a7f2b177ba5bdd55261"
REGISTRY_BLOB = "bdcddbc5dab3f3e59b86c15a73d0ae79e7e38993"
ROUTES_BLOB = "4d5c8e3f2b33d5148d98e7057991e167938c75bb"
INTAKE_BLOB = "a171482c04f62134812ed6084e19a9b803db3478"
WORK_PACKAGE_BLOB = "0f811d163f0d36b028cf6539963e2cf278517137"
REPLAY_BLOB = "a12f2c553b71f4daec9255e1f254f48a21f439c3"
READBACK_BLOB = "fde8ed79681dce929916b524176b236960cac4f6"
REPLAY_MERGE = "f34f33b22292ca244956781065fdf84efe2b43f2"
REPLAY_HEAD = "fca63848cfb1428292e4b74a4ed8980646d45aa2"
READBACK_MERGE = "1e64a4c147cb8f35255d3effa80342ce64ee3682"

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


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data, usedforsecurity=False).hexdigest()


def blob_at_commit(commit: str, path: str) -> str:
    return subprocess.check_output(["git", "rev-parse", f"{commit}:{path}"], cwd=ROOT, text=True).strip()


def load_at_commit(commit: str, path: str) -> Any:
    raw = subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=ROOT, text=True)
    return json.loads(raw)


def schema_errors(document: Any, schema_path: Path) -> list[str]:
    validator = Draft202012Validator(load(schema_path))
    return [f"{schema_path.name}: {e.message}" for e in sorted(validator.iter_errors(document), key=lambda e: list(e.path))]


def validation_errors(*, proposal: Any | None = None, registry: Any | None = None,
                      routes: Any | None = None, replay: Any | None = None,
                      readback: Any | None = None, local_blobs: dict[str, str] | None = None) -> list[str]:
    proposal = load(PROPOSAL) if proposal is None else proposal
    registry = load(REGISTRY) if registry is None else registry
    routes = load_at_commit(PROPOSAL_PROTECTED_PREDECESSOR_HEAD, ROUTE_REGISTRY_PATH) if routes is None else routes
    replay = load(REPLAY) if replay is None else replay
    readback = load(READBACK) if readback is None else readback
    blobs = {
        "proposal": git_blob_sha1(PROPOSAL),
        "registry": git_blob_sha1(REGISTRY),
        "routes": blob_at_commit(PROPOSAL_PROTECTED_PREDECESSOR_HEAD, ROUTE_REGISTRY_PATH),
        "intake": git_blob_sha1(INTAKE),
        "work_package": git_blob_sha1(WORK_PACKAGE),
        "replay": git_blob_sha1(REPLAY),
        "readback": git_blob_sha1(READBACK),
    }
    if local_blobs:
        blobs.update(local_blobs)

    errors: list[str] = []
    errors.extend(schema_errors(proposal, SCHEMAS[0]))
    errors.extend(schema_errors(registry, SCHEMAS[1]))

    expected_blobs = {
        "proposal": PROPOSAL_BLOB,
        "registry": REGISTRY_BLOB,
        "routes": ROUTES_BLOB,
        "intake": INTAKE_BLOB,
        "work_package": WORK_PACKAGE_BLOB,
        "replay": REPLAY_BLOB,
        "readback": READBACK_BLOB,
    }
    for key, expected in expected_blobs.items():
        if blobs.get(key) != expected:
            errors.append(f"{key} blob drift: {blobs.get(key)} != {expected}")

    if proposal.get("proposal_id") != PROPOSAL_ID or proposal.get("requested_route_id") != ROUTE_ID:
        errors.append("proposal identity drift")
    if proposal.get("result_family") != "OTP-H-GAPCVP" or proposal.get("proposal_state") != "proposed_only":
        errors.append("proposal family/state drift")
    if proposal.get("tracker_issue") != TRACKER:
        errors.append("tracker drift")

    expected_authority = {
        "official_subject": {"repository": "openai/ten-proofs", "commit": "94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6", "tree": "174289e4d4958cb0509874e6e53400e098213de7"},
        "source_pdf": {"revision": "2026-08-06", "sha256": "ebc561ab5c53dbd240e17a8fdb6fffeb648591eca85dbfc7466f563638f8c566", "byte_length": 2487031},
        "forge_semantic": {"merge": "b9dda1a5b958fd1be37a26324a025013a39584c1", "record_blob": "673f541fbb552d307cc226c51d2f0fd2916b328d"},
        "solve_handoff": {"merge": "e42c48dfe6a83eb19f398ba114f61fd700694ce5", "producer_packet_blob": "0dd2b38e40a126a1a2a2d57989038f788b8e40e4"},
        "cert_intake": {"merge": "ff9fa0a67a5a809f3519e0059f2ef9b082b1febb", "record_blob": INTAKE_BLOB},
        "cert_work_package": {"merge": "10e6f3ee20d7a6e89feb27aef0115fa27710d5e4", "record_blob": WORK_PACKAGE_BLOB},
        "cert_replay_evidence": {
            "protected_merge": REPLAY_MERGE, "admitted_head": REPLAY_HEAD, "historical_record_blob": REPLAY_BLOB,
            "evidence_id": "MC-OTP-H-GAPCVP-REPLAY-EVIDENCE-001", "family_replay_run": 32848939191,
            "cert_run": 32848939207, "gcl_run": 32848940096, "compatibility_run": 32848939106,
            "terminal_disposition": "H_REPLAY_EVIDENCE_PROTECTED__ZERO_ROUTE_OUTPUT_AUTHORITY",
        },
        "cert_replay_readback": {
            "protected_merge": READBACK_MERGE, "record_blob": READBACK_BLOB,
            "reconciliation_id": "MC-OTP-H-B1-B2-REPLAY-READBACK-001", "reviewer": "jimsteeg", "review_id": 5023763871,
        },
        "global_registered_route_registry_blob": ROUTES_BLOB,
    }
    if proposal.get("authority") != expected_authority:
        errors.append("authority surface drift")

    scope = proposal.get("target_scope", {})
    if scope.get("lean_theorems") != TARGETS: errors.append("target membership/order drift")
    if scope.get("promise_interfaces") != PROMISES: errors.append("promise membership/order drift")
    if scope.get("classifications") != CLASSIFICATIONS: errors.append("classification drift")
    if scope.get("gap_factors") != GAPS: errors.append("gap-factor drift")
    if scope.get("mandatory_qualifications") != QUALIFICATIONS: errors.append("mandatory qualification drift")
    if scope.get("nonvacuity_state") != "protected_replay_nonvacuity_clear": errors.append("nonvacuity state drift")
    if scope.get("permitted_axioms") != AXIOMS: errors.append("permitted axiom drift")
    exclusions = scope.get("scope_exclusions", [])
    for phrase in ("constant approximation factors", "rational-target", "consistent-system", "outside the promise", "input-dependent", "whole-document", "aggregate OpenAI Ten Proofs"):
        if not any(phrase in x for x in exclusions): errors.append(f"scope exclusion missing: {phrase}")

    expected_evidence = {
        "source_identity": "clear", "solution_build": "pass",
        "challenge_boundary": "eight_expected_challenge_sorries_no_solution_authority",
        "nonvacuity": "clear", "comparator": "accept", "lean_kernel": "accept", "nanoda": "accept",
        "theorem_axiom_report": "permitted_only", "trust_boundary_scan": "clear",
        "semantic_concordance": "protected_H_predecessors_reconfirmed", "protected_replay_readback": "clear",
        "aggregate_all_dependency": "absent",
    }
    if proposal.get("evidence_disposition") != expected_evidence: errors.append("evidence disposition drift")

    expected_controls = {
        "global_registered_route_registry_modified": False, "route_registry_entry": None,
        "may_register_route": False, "may_adjudicate": False, "adjudication": None, "cert_output": None,
        "mathematical_target_proved": False, "may_promote_claim": False, "cross_family_transfer": False,
        "aggregate_route": False, "aggregate_adjudication": False,
    }
    if proposal.get("route_controls") != expected_controls: errors.append("route authority inflation or drift")
    if any(r.get("route_id") == ROUTE_ID for r in routes.get("routes", [])):
        errors.append("proposed H route must not appear in registered route registry")

    if proposal.get("candidate_disposition") != "H_CERT_ROUTE_PROPOSAL_CLEAR__REGISTRATION_NOT_YET_AUTHORIZED":
        errors.append("candidate disposition drift")
    activation = proposal.get("activation", {})
    if activation.get("head_change_requires_reapproval") is not True: errors.append("head-change reapproval gate removed")
    for phrase in ("canonical Cert", "validator and test reached canonically", "fresh non-author specialist APPROVED review", "expected-head merge", "protected-main readback"):
        if phrase not in activation.get("condition", ""): errors.append(f"activation gate missing: {phrase}")
    if activation.get("effect") != "gapcvp_route_proposal_admitted_no_registration_no_adjudication": errors.append("activation effect drift")

    if replay.get("result_family") != "OTP-H-GAPCVP" or replay.get("evidence_id") != "MC-OTP-H-GAPCVP-REPLAY-EVIDENCE-001":
        errors.append("historical replay identity drift")
    if replay.get("route_state", {}).get("route_proposed") is not False or replay.get("route_state", {}).get("route_registered") is not False:
        errors.append("historical replay route state inflated")

    h = next((f for f in readback.get("families", []) if f.get("result_family") == "OTP-H-GAPCVP"), None)
    expected_h = {
        "exact_reviewed_head": REPLAY_HEAD,
        "protected_merge": REPLAY_MERGE,
        "terminal_disposition": "H_REPLAY_EVIDENCE_PROTECTED__ZERO_ROUTE_OUTPUT_AUTHORITY",
        "next_boundary": "separate_family_specific_H_route_proposal",
    }
    if not h: errors.append("H protected readback missing")
    else:
        for key, value in expected_h.items():
            if h.get(key) != value: errors.append(f"H protected readback drift: {key}")
        if h.get("exact_head_runs") != {"family_replay": 32848939191, "cert": 32848939207, "gcl": 32848940096, "compatibility": 32848939106}:
            errors.append("H protected readback run identity drift")
        review = h.get("non_author_review", {})
        if review.get("reviewer") != "jimsteeg" or review.get("review_id") != 5023763871 or review.get("state") != "APPROVED" or review.get("commit_id") != REPLAY_HEAD:
            errors.append("H protected readback review drift")

    if registry.get("authority") != {
        "cert_replay_evidence_merge": REPLAY_MERGE, "cert_replay_evidence_record_blob": REPLAY_BLOB,
        "cert_replay_readback_merge": READBACK_MERGE, "cert_replay_readback_blob": READBACK_BLOB,
        "global_registered_route_registry_blob": ROUTES_BLOB,
    }: errors.append("proposal registry authority drift")
    if registry.get("proposal") != {
        "result_family": "OTP-H-GAPCVP", "proposal_id": PROPOSAL_ID, "requested_route_id": ROUTE_ID,
        "path": "governance/result_family_route_proposal_successors/OTP-H-GAPCVP.json",
        "digest_algorithm": "git_blob_sha1", "digest": PROPOSAL_BLOB,
    }: errors.append("proposal registry digest/identity drift")
    if registry.get("state") != {"proposal_count": 1, "registered_route_count_created_by_this_operation": 0, "adjudication_count": 0, "cert_output_count": 0, "mathematical_target_proved_count": 0, "aggregate_route_count": 0}:
        errors.append("proposal registry state inflation")
    expected_registry_controls = {
        "global_registered_route_registry_modified": False, "proposal_registry_separate": True,
        "may_register_route": False, "may_adjudicate": False, "may_issue_cert_output": False,
        "may_mark_target_proved": False, "cross_family_transfer_prohibited": True,
        "aggregate_route_prohibited": True, "may_promote_claim": False,
    }
    if registry.get("route_controls") != expected_registry_controls: errors.append("proposal registry authority inflation")
    if registry.get("candidate_disposition") != "H_CERT_ROUTE_PROPOSAL_CLEAR__REGISTRATION_NOT_YET_AUTHORIZED": errors.append("proposal registry disposition drift")

    for boundary in (proposal.get("claim_boundary", ""), registry.get("claim_boundary", "")):
        for phrase in ("does not", "register", "adjudication", "Cert output", "target proved", "another family", "aggregate OpenAI Ten Proofs"):
            if phrase not in boundary: errors.append(f"claim boundary weakening: missing {phrase}")
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        for error in errors: print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("OTP_H_GAPCVP_ROUTE_PROPOSAL_CLEAR__REGISTRATION_NOT_AUTHORIZED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
