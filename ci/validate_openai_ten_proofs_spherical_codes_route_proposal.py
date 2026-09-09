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
PROPOSAL = ROOT / "governance/result_family_route_proposal_successors/OTP-B2-SPHERICAL-CODES.json"
REGISTRY = ROOT / "governance/pre_route_candidates/OPENAI_TEN_PROOFS_B2_SPHERICAL_CODES_ROUTE_PROPOSAL.json"
INTAKE = ROOT / "governance/result_family_intake_successors/OTP-B2-SPHERICAL-CODES.json"
WORK_PACKAGE = ROOT / "governance/result_family_work_package_successors/OTP-B2-SPHERICAL-CODES-CERT-WP-001.json"
REPLAY = ROOT / "governance/result_family_replay_evidence_successors/OTP-B2-SPHERICAL-CODES.json"
READBACK = ROOT / "governance/result_family_replay_evidence_readbacks/OTP-H-B1-B2.json"

PREDECESSOR_HEAD = "a727a64576ec8fe4071de4d362d4be0ee39c7a91"
TRACKER = "https://github.com/grandchallenge/MATHCERT/issues/206"
FAMILY = "OTP-B2-SPHERICAL-CODES"
ROUTE_ID = "MC-ROUTE-OTP-B2-SPHERICAL-CODES"
PROPOSAL_ID = "MC-OTP-ROUTE-PROPOSAL-B2-SPHERICAL-CODES"
PROPOSAL_BLOB = "12145d4936c040defe279b28586b68fc76930b7e"
REGISTRY_BLOB = "ec47a6cf7f8eb7ca33f46805c4ecb908be48a1f9"
ROUTES_BLOB = "ffc95950e571efebe1c90a3e6d1bf279b37b71b1"
INTAKE_BLOB = "8b74bd90d703eb1903a0a7a84387867a5df7b4e3"
WORK_PACKAGE_BLOB = "50dc2c9c5bc8aad49f22414536102cef0e82ce20"
REPLAY_BLOB = "288193448eee80c041beef57059182e1abe2e33c"
READBACK_BLOB = "fde8ed79681dce929916b524176b236960cac4f6"
REPLAY_MERGE = "938738844c4659b30a21d963da468ddfd1df51ad"
REPLAY_HEAD = "da41ab10f440b45fe53d321bc08bd3ffa8770930"
READBACK_MERGE = "1e64a4c147cb8f35255d3effa80342ce64ee3682"

TARGETS = [
    "MetricCodes.Johnson.main_binary_theorem",
    "MetricCodes.Spherical.HigherHierarchy.main_general",
    "MetricCodes.Spherical.HigherHierarchy.strict_hierarchy",
    "MetricCodes.Spherical.HigherHierarchy.NumericalMaximum.eventually_kissingNumber_lt_published",
]
CLASSIFICATIONS = [
    "source_faithful_exact_projection",
    "source_faithful_structured_projection",
    "source_faithful_structured_projection",
    "formal_strengthening_entailing_source_asymptotic_numerical_statement",
]
QUALIFICATIONS = [
    "The predecessor seven-target spherical surface transfers no authority to this successor route proposal.",
    "The exact eventual 0.39661 target is not attributed to the manuscript verbatim.",
    "The manuscript prints 0.39661+o(1); the exact eventual inequality below 0.39661 is a formal strengthening entailing that source asymptotic statement.",
    "Hierarchy, interlacing, and localization domains remain bound to the protected current-root semantic and nonvacuity audit.",
    "No whole-chapter semantic equivalence or full proof-body comparison is established.",
    "Forge semantic admission and replay do not independently certify the source proof.",
]
AXIOMS = ["propext", "Quot.sound", "Classical.choice"]


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data, usedforsecurity=False).hexdigest()


def load_routes_at_commit(commit: str) -> Any:
    raw = subprocess.check_output(
        ["git", "show", f"{commit}:{route_state.ROUTES_REL}"], cwd=ROOT, text=True
    )
    return json.loads(raw)


def validation_errors(*, proposal: Any | None = None, registry: Any | None = None,
                      routes: Any | None = None, replay: Any | None = None,
                      readback: Any | None = None,
                      local_blobs: dict[str, str] | None = None) -> list[str]:
    proposal = load(PROPOSAL) if proposal is None else proposal
    registry = load(REGISTRY) if registry is None else registry
    routes = load_routes_at_commit(PREDECESSOR_HEAD) if routes is None else routes
    replay = load(REPLAY) if replay is None else replay
    readback = load(READBACK) if readback is None else readback
    blobs = {
        "proposal": git_blob_sha1(PROPOSAL),
        "registry": git_blob_sha1(REGISTRY),
        "routes": route_state.blob_at(PREDECESSOR_HEAD),
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

    authority = proposal.get("authority", {})
    expected_authority = {
        "official_subject": {"repository": "openai/ten-proofs", "commit": "94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6", "tree": "174289e4d4958cb0509874e6e53400e098213de7"},
        "source_pdf": {"revision": "2026-08-06", "sha256": "ebc561ab5c53dbd240e17a8fdb6fffeb648591eca85dbfc7466f563638f8c566", "byte_length": 2487031},
        "forge_semantic": {"merge": "0520d8bae3853798f2edca67c526133e46847a54", "record_blob": "394d1211757d3fc2bc61b238e914b37245967635"},
        "solve_handoff": {"merge": "63efb94f28ecb12c55a492c2243a9f70d655f646", "producer_packet_blob": "0266c9a431ca4a8e84989913fc626a5086496da6"},
        "cert_intake": {"merge": "9d3af5503f06e1a564562a49ce9f5b439a3d9364", "record_blob": INTAKE_BLOB},
        "cert_work_package": {"merge": "be26d65ba147922ec0975419196b5fdbc7427b8a", "record_blob": WORK_PACKAGE_BLOB},
        "cert_replay_evidence": {
            "protected_merge": REPLAY_MERGE, "admitted_head": REPLAY_HEAD,
            "historical_record_blob": REPLAY_BLOB,
            "evidence_id": "MC-OTP-B2-SPHERICAL-CODES-REPLAY-EVIDENCE-001",
            "family_replay_run": 32849224700, "cert_run": 32849225046,
            "gcl_run": 32849225863, "compatibility_run": 32849224740,
            "terminal_disposition": "B2_REPLAY_EVIDENCE_PROTECTED__ZERO_ROUTE_OUTPUT_AUTHORITY",
        },
        "cert_replay_readback": {
            "protected_merge": READBACK_MERGE, "record_blob": READBACK_BLOB,
            "reconciliation_id": "MC-OTP-H-B1-B2-REPLAY-READBACK-001",
            "reviewer": "jimsteeg", "review_id": 5023775055,
        },
        "global_registered_route_registry_blob": ROUTES_BLOB,
    }
    if authority != expected_authority:
        errors.append("authority surface drift")

    scope = proposal.get("target_scope", {})
    if scope.get("lean_theorems") != TARGETS:
        errors.append("target membership/order drift")
    if scope.get("classifications") != CLASSIFICATIONS:
        errors.append("classification drift")
    if scope.get("mandatory_qualifications") != QUALIFICATIONS:
        errors.append("mandatory qualification drift")
    if scope.get("permitted_axioms") != AXIOMS:
        errors.append("permitted axiom drift")
    if scope.get("nonvacuity_state") != "protected_replay_nonvacuity_clear":
        errors.append("nonvacuity state drift")
    if scope.get("hierarchy_domain_state") != "protected_current_root_domain_clear":
        errors.append("hierarchy domain drift")
    if scope.get("numerical_strengthening_state") != "protected_formal_strengthening_not_source_verbatim":
        errors.append("numerical strengthening boundary drift")

    expected_evidence = {
        "source_identity": "clear", "solution_build": "pass",
        "challenge_boundary": "four_expected_challenge_sorries_no_solution_authority",
        "nonvacuity": "clear", "hierarchy_domains": "clear",
        "numerical_strengthening": "clear_with_nonverbatim_qualification",
        "comparator": "accept", "lean_kernel": "accept", "nanoda": "accept",
        "theorem_axiom_report": "permitted_only", "trust_boundary_scan": "clear",
        "semantic_concordance": "protected_B2_predecessors_reconfirmed",
        "protected_replay_readback": "clear", "aggregate_all_dependency": "absent",
    }
    if proposal.get("evidence_disposition") != expected_evidence:
        errors.append("evidence disposition drift")

    expected_controls = {
        "global_registered_route_registry_modified": False, "route_registry_entry": None,
        "may_register_route": False, "may_adjudicate": False, "adjudication": None,
        "cert_output": None, "mathematical_target_proved": False,
        "may_promote_claim": False, "cross_family_transfer": False,
        "aggregate_route": False, "aggregate_adjudication": False,
    }
    if proposal.get("route_controls") != expected_controls:
        errors.append("route authority inflation or drift")
    if any(item.get("route_id") == ROUTE_ID for item in routes.get("routes", [])):
        errors.append("proposed B2 route must not appear in registered route registry at proposal predecessor")
    activation = proposal.get("activation", {})
    if activation.get("head_change_requires_reapproval") is not True:
        errors.append("head-change reapproval gate removed")
    if activation.get("effect") != "spherical_codes_route_proposal_admitted_no_registration_no_adjudication":
        errors.append("activation effect drift")
    if proposal.get("candidate_disposition") != "B2_CERT_ROUTE_PROPOSAL_CLEAR__REGISTRATION_NOT_YET_AUTHORIZED":
        errors.append("candidate disposition drift")

    if replay.get("result_family") != FAMILY or replay.get("evidence_id") != "MC-OTP-B2-SPHERICAL-CODES-REPLAY-EVIDENCE-001":
        errors.append("historical replay identity drift")
    replay_route = replay.get("route_state", {})
    if replay_route.get("route_proposed") is not False or replay_route.get("route_registered") is not False:
        errors.append("historical replay route state inflated")
    if replay_route.get("may_adjudicate") is not False or replay_route.get("cert_output") is not None:
        errors.append("historical replay authority inflated")

    b2 = next((item for item in readback.get("families", []) if item.get("result_family") == FAMILY), None)
    if not b2:
        errors.append("B2 protected readback missing")
    else:
        expected = {
            "exact_reviewed_head": REPLAY_HEAD,
            "protected_merge": REPLAY_MERGE,
            "terminal_disposition": "B2_REPLAY_EVIDENCE_PROTECTED__ZERO_ROUTE_OUTPUT_AUTHORITY",
            "next_boundary": "separate_family_specific_B2_route_proposal",
        }
        for key, value in expected.items():
            if b2.get(key) != value:
                errors.append(f"B2 protected readback drift: {key}")
        if b2.get("exact_head_runs") != {"family_replay": 32849224700, "cert": 32849225046, "gcl": 32849225863, "compatibility": 32849224740}:
            errors.append("B2 protected readback run identity drift")
        review = b2.get("non_author_review", {})
        if review.get("reviewer") != "jimsteeg" or review.get("review_id") != 5023775055 or review.get("state") != "APPROVED" or review.get("commit_id") != REPLAY_HEAD:
            errors.append("B2 protected readback review drift")
        for key in ("route_proposed", "route_registered", "may_adjudicate", "mathematical_target_proved", "aggregate_authority"):
            if b2.get(key) is not False:
                errors.append(f"B2 protected readback authority drift: {key}")
        if b2.get("cert_output") is not None or b2.get("adjudication") is not None:
            errors.append("B2 protected readback output/adjudication inflated")

    expected_registry_authority = {
        "cert_replay_evidence_merge": REPLAY_MERGE,
        "cert_replay_evidence_record_blob": REPLAY_BLOB,
        "cert_replay_readback_merge": READBACK_MERGE,
        "cert_replay_readback_blob": READBACK_BLOB,
        "global_registered_route_registry_blob": ROUTES_BLOB,
    }
    if registry.get("authority") != expected_registry_authority:
        errors.append("proposal registry authority drift")
    expected_pointer = {
        "result_family": FAMILY, "proposal_id": PROPOSAL_ID,
        "requested_route_id": ROUTE_ID,
        "path": "governance/result_family_route_proposal_successors/OTP-B2-SPHERICAL-CODES.json",
        "digest_algorithm": "git_blob_sha1", "digest": PROPOSAL_BLOB,
    }
    if registry.get("proposal") != expected_pointer:
        errors.append("proposal registry pointer drift")
    if registry.get("tracker_issue") != TRACKER or registry.get("candidate_id") != "OPENAI-TEN-PROOFS-001":
        errors.append("proposal registry identity drift")
    expected_state = {
        "proposal_count": 1, "registered_route_count_created_by_this_operation": 0,
        "adjudication_count": 0, "cert_output_count": 0,
        "mathematical_target_proved_count": 0, "aggregate_route_count": 0,
    }
    if registry.get("state") != expected_state:
        errors.append("proposal registry state inflation or drift")
    controls = registry.get("route_controls", {})
    if controls != {
        "global_registered_route_registry_modified": False, "proposal_registry_separate": True,
        "may_register_route": False, "may_adjudicate": False, "may_issue_cert_output": False,
        "may_mark_target_proved": False, "cross_family_transfer_prohibited": True,
        "aggregate_route_prohibited": True, "may_promote_claim": False,
    }:
        errors.append("proposal registry authority inflation or drift")
    if registry.get("activation", {}).get("head_change_requires_reapproval") is not True:
        errors.append("proposal registry reapproval gate removed")
    if registry.get("candidate_disposition") != "B2_CERT_ROUTE_PROPOSAL_CLEAR__REGISTRATION_NOT_YET_AUTHORIZED":
        errors.append("proposal registry disposition drift")
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("validated B2 spherical-codes proposed-only route against protected replay/readback and historical registered-route snapshot")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
