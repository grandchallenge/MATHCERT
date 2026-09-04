#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import certification_route_state as route_state

ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "governance/result_family_route_proposal_successors/OTP-B1-BINARY-CODES.json"
REGISTRY = ROOT / "governance/pre_route_candidates/OPENAI_TEN_PROOFS_B1_BINARY_CODES_ROUTE_PROPOSAL.json"
PROPOSAL_PROTECTED_PREDECESSOR_HEAD = "a727a64576ec8fe4071de4d362d4be0ee39c7a91"
INTAKE = ROOT / "governance/result_family_intake_successors/OTP-B1-BINARY-CODES.json"
WORK_PACKAGE = ROOT / "governance/result_family_work_package_successors/OTP-B1-BINARY-CODES-CERT-WP-001.json"
REPLAY = ROOT / "governance/result_family_replay_evidence_successors/OTP-B1-BINARY-CODES.json"
READBACK = ROOT / "governance/result_family_replay_evidence_readbacks/OTP-H-B1-B2.json"

TRACKER = "https://github.com/grandchallenge/MATHCERT/issues/205"
FAMILY = "OTP-B1-BINARY-CODES"
ROUTE_ID = "MC-ROUTE-OTP-B1-BINARY-CODES"
PROPOSAL_ID = "MC-OTP-ROUTE-PROPOSAL-B1-BINARY-CODES"
PROPOSAL_BLOB = "d476d4ab8c018f38cb604d4570d43619fca6d25b"
REGISTRY_BLOB = "833439191db393d2e2b48b2b005e0f9497bff481"
ROUTES_BLOB = "ffc95950e571efebe1c90a3e6d1bf279b37b71b1"
INTAKE_BLOB = "9ba1e66679d5d46aceef16164194147d8fac530a"
WORK_PACKAGE_BLOB = "19e1eaf5e24ce212bb020c8c40d4177ff5b4f8f9"
REPLAY_BLOB = "fd669ae6cfc39110560656c2123d5d4449200830"
READBACK_BLOB = "fde8ed79681dce929916b524176b236960cac4f6"
REPLAY_MERGE = "d8daab1c0deec3d41ac438714e21ee752c14ac46"
REPLAY_HEAD = "67f445b9a5e015083644416d96f4a10722efe032"
READBACK_MERGE = "1e64a4c147cb8f35255d3effa80342ce64ee3682"

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


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data, usedforsecurity=False).hexdigest()


def route_blob_at_commit(commit: str) -> str:
    return route_state.blob_at(commit)


def load_routes_at_commit(commit: str) -> Any:
    raw = subprocess.check_output(
        ["git", "show", f"{commit}:{route_state.ROUTES_REL}"], cwd=ROOT, text=True
    )
    return json.loads(raw)


def validation_errors(*, proposal: Any | None = None, registry: Any | None = None,
                      routes: Any | None = None, replay: Any | None = None,
                      readback: Any | None = None, local_blobs: dict[str, str] | None = None) -> list[str]:
    proposal = load(PROPOSAL) if proposal is None else proposal
    registry = load(REGISTRY) if registry is None else registry
    routes = load_routes_at_commit(PROPOSAL_PROTECTED_PREDECESSOR_HEAD) if routes is None else routes
    replay = load(REPLAY) if replay is None else replay
    readback = load(READBACK) if readback is None else readback
    blobs = {
        "proposal": git_blob_sha1(PROPOSAL),
        "registry": git_blob_sha1(REGISTRY),
        "routes": route_blob_at_commit(PROPOSAL_PROTECTED_PREDECESSOR_HEAD),
        "intake": git_blob_sha1(INTAKE),
        "work_package": git_blob_sha1(WORK_PACKAGE),
        "replay": git_blob_sha1(REPLAY),
        "readback": git_blob_sha1(READBACK),
    }
    if local_blobs:
        blobs.update(local_blobs)

    errors: list[str] = []
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
    if proposal.get("candidate_id") != "OPENAI-TEN-PROOFS-001" or proposal.get("result_family") != FAMILY:
        errors.append("proposal family/candidate drift")
    if proposal.get("proposal_state") != "proposed_only":
        errors.append("proposal state must remain proposed_only")
    if proposal.get("tracker_issue") != TRACKER:
        errors.append("tracker drift")

    expected_authority = {
        "official_subject": {"repository": "openai/ten-proofs", "commit": "94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6", "tree": "174289e4d4958cb0509874e6e53400e098213de7"},
        "source_pdf": {"revision": "2026-08-06", "sha256": "ebc561ab5c53dbd240e17a8fdb6fffeb648591eca85dbfc7466f563638f8c566", "byte_length": 2487031},
        "forge_semantic": {"merge": "24a1fa0f020ee9cc7fbe2e7aea4cd840268ca748", "record_blob": "0ab4d973bc046084e9d2dc6c7552ab5428d7412d"},
        "solve_handoff": {"merge": "7858f1350439e6324bdee149931bdb7661098729", "producer_packet_blob": "1847dd7a17cda51cb02f017766c59d372811fb12"},
        "cert_intake": {"merge": "5bddc3eb7d02638cf4fe959accfbfeade4964592", "record_blob": INTAKE_BLOB},
        "cert_work_package": {"merge": "83a8951a89a72a892d5fdc132d6a22e508d6cdc2", "record_blob": WORK_PACKAGE_BLOB},
        "cert_replay_evidence": {
            "protected_merge": REPLAY_MERGE,
            "admitted_head": REPLAY_HEAD,
            "historical_record_blob": REPLAY_BLOB,
            "evidence_id": "MC-OTP-B1-BINARY-CODES-REPLAY-EVIDENCE-001",
            "family_replay_run": 32849083880,
            "cert_run": 32849083816,
            "gcl_run": 32849084349,
            "compatibility_run": 32849083761,
            "terminal_disposition": "B1_REPLAY_EVIDENCE_PROTECTED__ZERO_ROUTE_OUTPUT_AUTHORITY",
        },
        "cert_replay_readback": {
            "protected_merge": READBACK_MERGE,
            "record_blob": READBACK_BLOB,
            "reconciliation_id": "MC-OTP-H-B1-B2-REPLAY-READBACK-001",
            "reviewer": "jimsteeg",
            "review_id": 5023771071,
        },
        "global_registered_route_registry_blob": ROUTES_BLOB,
    }
    if proposal.get("authority") != expected_authority:
        errors.append("authority surface drift")

    scope = proposal.get("target_scope", {})
    if scope.get("lean_theorems") != TARGETS:
        errors.append("target membership/order drift")
    if scope.get("classifications") != CLASSIFICATIONS:
        errors.append("classification drift")
    if scope.get("mandatory_qualifications") != QUALIFICATIONS:
        errors.append("mandatory qualification drift")
    if scope.get("nonvacuity_state") != "protected_replay_nonvacuity_clear":
        errors.append("nonvacuity state drift")
    if scope.get("minimizer_attainment_state") != "protected_bridge_clear":
        errors.append("minimizer attainment state drift")
    if scope.get("permitted_axioms") != AXIOMS:
        errors.append("permitted axiom drift")
    exclusions = scope.get("scope_exclusions", [])
    for phrase in ("source-verbatim", "sInf representation", "logarithm base", "whole-chapter", "independently certify", "aggregate OpenAI Ten Proofs"):
        if not any(phrase in item for item in exclusions):
            errors.append(f"scope exclusion missing: {phrase}")

    expected_evidence = {
        "source_identity": "clear",
        "solution_build": "pass",
        "challenge_boundary": "six_expected_challenge_sorries_no_solution_authority",
        "nonvacuity": "clear",
        "minimizer_attainment": "clear",
        "comparator": "accept",
        "lean_kernel": "accept",
        "nanoda": "accept",
        "theorem_axiom_report": "permitted_only",
        "trust_boundary_scan": "clear",
        "semantic_concordance": "protected_B1_predecessors_reconfirmed",
        "protected_replay_readback": "clear",
        "aggregate_all_dependency": "absent",
    }
    if proposal.get("evidence_disposition") != expected_evidence:
        errors.append("evidence disposition drift")

    expected_controls = {
        "global_registered_route_registry_modified": False,
        "route_registry_entry": None,
        "may_register_route": False,
        "may_adjudicate": False,
        "adjudication": None,
        "cert_output": None,
        "mathematical_target_proved": False,
        "may_promote_claim": False,
        "cross_family_transfer": False,
        "aggregate_route": False,
        "aggregate_adjudication": False,
    }
    if proposal.get("route_controls") != expected_controls:
        errors.append("route authority inflation or drift")
    if any(route.get("route_id") == ROUTE_ID for route in routes.get("routes", [])):
        errors.append("proposed B1 route must not appear in registered route registry at proposal predecessor")

    activation = proposal.get("activation", {})
    if activation.get("head_change_requires_reapproval") is not True:
        errors.append("head-change reapproval gate removed")
    for phrase in ("canonical Cert", "validator and test reached canonically", "fresh non-author coding-theory/Lean specialist APPROVED review", "expected-head merge", "protected-main readback"):
        if phrase not in activation.get("condition", ""):
            errors.append(f"activation gate missing: {phrase}")
    if activation.get("effect") != "binary_codes_route_proposal_admitted_no_registration_no_adjudication":
        errors.append("activation effect drift")
    if proposal.get("candidate_disposition") != "B1_CERT_ROUTE_PROPOSAL_CLEAR__REGISTRATION_NOT_YET_AUTHORIZED":
        errors.append("candidate disposition drift")

    if replay.get("result_family") != FAMILY or replay.get("evidence_id") != "MC-OTP-B1-BINARY-CODES-REPLAY-EVIDENCE-001":
        errors.append("historical replay identity drift")
    replay_route = replay.get("route_state", {})
    if replay_route.get("route_proposed") is not False or replay_route.get("route_registered") is not False:
        errors.append("historical replay route state inflated")
    if replay_route.get("may_adjudicate") is not False or replay_route.get("cert_output") is not None or replay_route.get("mathematical_target_proved") is not False:
        errors.append("historical replay authority inflated")

    b1 = next((f for f in readback.get("families", []) if f.get("result_family") == FAMILY), None)
    if not b1:
        errors.append("B1 protected readback missing")
    else:
        expected_b1 = {
            "exact_reviewed_head": REPLAY_HEAD,
            "protected_merge": REPLAY_MERGE,
            "terminal_disposition": "B1_REPLAY_EVIDENCE_PROTECTED__ZERO_ROUTE_OUTPUT_AUTHORITY",
            "next_boundary": "separate_family_specific_B1_route_proposal",
        }
        for key, value in expected_b1.items():
            if b1.get(key) != value:
                errors.append(f"B1 protected readback drift: {key}")
        if b1.get("exact_head_runs") != {"family_replay": 32849083880, "cert": 32849083816, "gcl": 32849084349, "compatibility": 32849083761}:
            errors.append("B1 protected readback run identity drift")
        review = b1.get("non_author_review", {})
        if review.get("reviewer") != "jimsteeg" or review.get("review_id") != 5023771071 or review.get("state") != "APPROVED" or review.get("commit_id") != REPLAY_HEAD:
            errors.append("B1 protected readback review drift")
        for key, expected in (("route_proposed", False), ("route_registered", False), ("may_adjudicate", False), ("mathematical_target_proved", False), ("aggregate_authority", False)):
            if b1.get(key) is not expected:
                errors.append(f"B1 protected readback authority drift: {key}")
        if b1.get("cert_output") is not None or b1.get("adjudication") is not None:
            errors.append("B1 protected readback output/adjudication inflated")

    expected_registry_authority = {
        "cert_replay_evidence_merge": REPLAY_MERGE,
        "cert_replay_evidence_record_blob": REPLAY_BLOB,
        "cert_replay_readback_merge": READBACK_MERGE,
        "cert_replay_readback_blob": READBACK_BLOB,
        "global_registered_route_registry_blob": ROUTES_BLOB,
    }
    if registry.get("authority") != expected_registry_authority:
        errors.append("proposal registry authority drift")
    expected_registry_proposal = {
        "result_family": FAMILY,
        "proposal_id": PROPOSAL_ID,
        "requested_route_id": ROUTE_ID,
        "path": "governance/result_family_route_proposal_successors/OTP-B1-BINARY-CODES.json",
        "digest_algorithm": "git_blob_sha1",
        "digest": PROPOSAL_BLOB,
    }
    if registry.get("proposal") != expected_registry_proposal:
        errors.append("proposal registry pointer drift")
    if registry.get("tracker_issue") != TRACKER or registry.get("candidate_id") != "OPENAI-TEN-PROOFS-001":
        errors.append("proposal registry identity drift")
    expected_state = {
        "proposal_count": 1,
        "registered_route_count_created_by_this_operation": 0,
        "adjudication_count": 0,
        "cert_output_count": 0,
        "mathematical_target_proved_count": 0,
        "aggregate_route_count": 0,
    }
    if registry.get("state") != expected_state:
        errors.append("proposal registry state inflation or drift")
    expected_registry_scope = {
        "target_count": 6,
        "another_family_target_count": 0,
        "aggregate_route": False,
        "whole_chapter_equivalence": False,
        "proof_body_equivalence": False,
        "derived_positive_margin_target_count": 2,
        "minimizer_attainment_bridge_preserved": True,
        "logarithm_base_preserved": True,
        "ceiling_convention_preserved": True,
        "strict_spectral_feasibility_preserved": True,
        "variational_domains_preserved": True,
    }
    if registry.get("scope") != expected_registry_scope:
        errors.append("proposal registry scope drift")
    expected_registry_controls = {
        "global_registered_route_registry_modified": False,
        "proposal_registry_separate": True,
        "may_register_route": False,
        "may_adjudicate": False,
        "may_issue_cert_output": False,
        "may_mark_target_proved": False,
        "cross_family_transfer_prohibited": True,
        "aggregate_route_prohibited": True,
        "may_promote_claim": False,
    }
    if registry.get("route_controls") != expected_registry_controls:
        errors.append("proposal registry authority inflation or drift")
    reg_activation = registry.get("activation", {})
    if reg_activation.get("head_change_requires_reapproval") is not True:
        errors.append("proposal registry reapproval gate removed")
    if reg_activation.get("effect") != "one_binary_codes_route_proposal_admitted_no_registration_no_adjudication":
        errors.append("proposal registry activation effect drift")
    if registry.get("candidate_disposition") != "B1_CERT_ROUTE_PROPOSAL_CLEAR__REGISTRATION_NOT_YET_AUTHORIZED":
        errors.append("proposal registry disposition drift")

    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("validated B1 binary-codes proposed-only route against protected replay/readback and historical registered-route snapshot")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
