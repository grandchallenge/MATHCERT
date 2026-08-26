#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "governance/result_family_route_proposal_successors/OTP-A-SPHERE-PACKING.json"
REGISTRY = ROOT / "governance/pre_route_candidates/OPENAI_TEN_PROOFS_A_SPHERE_PACKING_ROUTE_PROPOSAL.json"
ROUTES = ROOT / "governance/certification_routes.json"
INTAKE = ROOT / "governance/result_family_intake_successors/OTP-A-SPHERE-PACKING.json"
WORK_PACKAGE = ROOT / "governance/result_family_work_package_successors/OTP-A-SPHERE-PACKING-CERT-WP-001.json"
REPLAY = ROOT / "governance/result_family_replay_evidence_successors/OTP-A-SPHERE-PACKING.json"
SCHEMAS = (
    ROOT / "schemas/openai_ten_proofs_sphere_packing_route_proposal.schema.json",
    ROOT / "schemas/openai_ten_proofs_sphere_packing_route_proposal_registry.schema.json",
)

TRACKER = "https://github.com/grandchallenge/MATHCERT/issues/156"
ROUTE_ID = "MC-ROUTE-OTP-A-SPHERE-PACKING"
PROPOSAL_ID = "MC-OTP-ROUTE-PROPOSAL-A-SPHERE-PACKING"
PROPOSAL_BLOB = "e216cfc893a99d853ca798a68c46adbf013239ff"
ROUTES_BLOB = "2d17473b4731aa9d9c630b1e7777ad4bd794d993"
A_REGISTRATION_ROUTES_BLOB = "b9bb0dc9e18856f50a88162df37c20c034327439"
A_OUTPUT_ROUTES_BLOB = "4d5c8e3f2b33d5148d98e7057991e167938c75bb"
INTAKE_BLOB = "294c9f7d6cceb1cdf7ec4c8e73255dd1ba130670"
WORK_PACKAGE_BLOB = "f0c91d1959035f35843c383920dfba0b6c24b485"
REPLAY_BLOB = "5a2d17d158ee9e8b535de8ed0a1ed41612c5abd2"
REPLAY_MERGE = "036646952651057deadc5c485ef9e80a086865cd"
REPLAY_HEAD = "62bcc5b4d2986a39e437d03fd2a52244fcf3b84f"
BUNDLE_SHA256 = "0ec443cd35cee041d5bdc154de2e5d1697a21cdffbcc01d21c08c6aad61f10f3"

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
QUALIFICATIONS = [
    "The ten-field composite is not a single verbatim manuscript theorem.",
    "The 30-decimal base-two exponent enclosure is a formal numerical consequence of the exact alpha_* expression, not manuscript-authored precision.",
    "The packing bridge relies on proved positive rescaling invariance and unit-separation supremum equivalence; declaration-name similarity is not used as authority.",
    "The explicit little-o witness is a normal form of the source asymptotic and is not a stronger rate claim.",
    "No whole-chapter semantic equivalence or independent proof certification is transferred by this proposal.",
]
NONVACUITY = [
    "CohnElkies.admissible_nonempty",
    "fullQuotientSet_eq_radial",
    "SpherePacking singleton unit-separated packing witness",
    "SpherePacking.upper_packing_density_le_one",
    "positive-dimensional bridge quantification",
]
AXIOMS = ["propext", "Quot.sound", "Classical.choice"]


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def schema_errors(document: Any, schema_path: Path) -> list[str]:
    schema = load(schema_path)
    validator = Draft202012Validator(schema)
    return [f"{schema_path.name}: {e.message}" for e in sorted(validator.iter_errors(document), key=lambda e: list(e.path))]


def registration_errors(routes: Any) -> list[str]:
    spec = importlib.util.spec_from_file_location(
        "sphere_packing_route_registration",
        ROOT / "ci/validate_openai_ten_proofs_sphere_packing_route_registration.py",
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return list(module.validation_errors(routes=routes))


def validation_errors(*, proposal: Any | None = None, registry: Any | None = None,
                      routes: Any | None = None, local_blobs: dict[str, str] | None = None) -> list[str]:
    proposal = load(PROPOSAL) if proposal is None else proposal
    registry = load(REGISTRY) if registry is None else registry
    routes = load(ROUTES) if routes is None else routes
    blobs = {
        "proposal": git_blob_sha1(PROPOSAL),
        "routes": git_blob_sha1(ROUTES),
        "intake": git_blob_sha1(INTAKE),
        "work_package": git_blob_sha1(WORK_PACKAGE),
        "replay": git_blob_sha1(REPLAY),
    }
    if local_blobs is not None:
        blobs.update(local_blobs)

    errors: list[str] = []
    errors.extend(schema_errors(proposal, SCHEMAS[0]))
    errors.extend(schema_errors(registry, SCHEMAS[1]))

    expected_blobs = {
        "proposal": PROPOSAL_BLOB,
        "intake": INTAKE_BLOB,
        "work_package": WORK_PACKAGE_BLOB,
        "replay": REPLAY_BLOB,
    }
    for key, expected in expected_blobs.items():
        if blobs.get(key) != expected:
            errors.append(f"{key} blob drift: {blobs.get(key)} != {expected}")
    routes_blob = blobs.get("routes")
    if routes_blob not in {ROUTES_BLOB, A_REGISTRATION_ROUTES_BLOB, A_OUTPUT_ROUTES_BLOB}:
        errors.append(f"routes blob drift: {routes_blob} is neither protected proposal snapshot nor exact A registration/output successor")

    if proposal.get("proposal_id") != PROPOSAL_ID or proposal.get("requested_route_id") != ROUTE_ID:
        errors.append("proposal identity drift")
    if proposal.get("proposal_state") != "proposed_only":
        errors.append("proposal state must remain proposed_only")
    if proposal.get("tracker_issue") != TRACKER:
        errors.append("tracker drift")

    auth = proposal.get("authority", {})
    expected_auth = {
        "official_subject": {
            "repository": "openai/ten-proofs",
            "commit": "94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6",
            "tree": "174289e4d4958cb0509874e6e53400e098213de7",
        },
        "source_pdf": {
            "revision": "2026-08-06",
            "sha256": "ebc561ab5c53dbd240e17a8fdb6fffeb648591eca85dbfc7466f563638f8c566",
            "byte_length": 2487031,
        },
        "forge_composite_semantic": {
            "merge": "706d0291370bf3f14aa37be0823e33d06f7343b0",
            "record_blob": "b2e309ad96e750651fc7149a6bad54c6bf99015b",
        },
        "forge_bridge_semantic": {
            "merge": "5a0cb9a7b7eef210dd0fce5c527d09b6eef3bc12",
            "record_blob": "7858b156fc4490ecc6e3572dcf449d84dcc99f93",
        },
        "solve_handoff": {
            "merge": "c19735edf4c16ac9765bb66c7209bbf11bf1312e",
            "producer_packet_blob": "9e3b46972bf01ac3d24c6a0ae5f522799335ecd1",
        },
        "cert_intake": {
            "merge": "947b3bed0effa79c2472dddc37d6c463f79c3126",
            "record_blob": INTAKE_BLOB,
        },
        "cert_work_package": {
            "merge": "54b883bb5c6ffaf099efd7270df3519a45b13038",
            "record_blob": WORK_PACKAGE_BLOB,
        },
        "cert_replay_evidence": {
            "merge": REPLAY_MERGE,
            "admitted_head": REPLAY_HEAD,
            "record_blob": REPLAY_BLOB,
            "evidence_id": "MC-OTP-A-SPHERE-PACKING-REPLAY-EVIDENCE-001",
            "bundle_sha256": BUNDLE_SHA256,
            "final_replay_run": 32122158005,
            "final_replay_job": 95664825653,
        },
        "global_registered_route_registry_blob": ROUTES_BLOB,
    }
    if auth != expected_auth:
        errors.append("authority surface drift")

    scope = proposal.get("target_scope", {})
    if scope.get("lean_theorems") != TARGETS:
        errors.append("target membership/order drift")
    if scope.get("classifications") != CLASSIFICATIONS:
        errors.append("classification drift")
    if scope.get("mandatory_qualifications") != QUALIFICATIONS:
        errors.append("mandatory qualification drift")
    if scope.get("nonvacuity_state") != "clear_for_current_root_four_target_surface":
        errors.append("nonvacuity state drift")
    if scope.get("nonvacuity_evidence") != NONVACUITY:
        errors.append("nonvacuity evidence drift")
    if scope.get("permitted_axioms") != AXIOMS:
        errors.append("permitted axiom drift")
    exclusions = scope.get("scope_exclusions", [])
    for phrase in ("single verbatim manuscript theorem", "manuscript-authored precision", "scale and unit-separation normalization", "whole-chapter", "aggregate OpenAI Ten Proofs"):
        if not any(phrase in x for x in exclusions):
            errors.append(f"scope exclusion missing: {phrase}")

    expected_evidence = {
        "source_identity": "clear",
        "solution_build": "pass",
        "challenge_boundary": "four_expected_comparator_sorries_only",
        "nonvacuity": "clear",
        "comparator": "accept",
        "lean_kernel": "accept",
        "nanoda": "accept",
        "theorem_axiom_report": "permitted_only",
        "trust_boundary_scan": "clear",
        "semantic_concordance": "protected_predecessors_reconfirmed",
        "aggregate_all_dependency": "absent",
    }
    if proposal.get("evidence_disposition") != expected_evidence:
        errors.append("evidence disposition drift")

    controls = proposal.get("route_controls", {})
    expected_controls = {
        "global_registered_route_registry_modified": False,
        "route_registry_entry": None,
        "may_register_route": False,
        "may_adjudicate": False,
        "adjudication": None,
        "cert_output": None,
        "mathematical_target_proved": False,
        "may_promote_claim": False,
        "aggregate_route": False,
        "aggregate_adjudication": False,
    }
    if controls != expected_controls:
        errors.append("route authority inflation or drift")

    route_count = sum(1 for r in routes.get("routes", []) if isinstance(r, dict) and r.get("route_id") == ROUTE_ID)
    if routes_blob == ROUTES_BLOB and route_count != 0:
        errors.append("A route present in protected proposal-stage registry snapshot")
    if routes_blob in {A_REGISTRATION_ROUTES_BLOB, A_OUTPUT_ROUTES_BLOB}:
        if route_count != 1:
            errors.append("exact A registration/output successor missing or duplicated")
        else:
            errors.extend(registration_errors(routes))

    if proposal.get("candidate_disposition") != "A_CERT_ROUTE_PROPOSAL_CLEAR__REGISTRATION_NOT_YET_AUTHORIZED":
        errors.append("candidate disposition drift")
    activation = proposal.get("activation", {})
    if activation.get("head_change_requires_reapproval") is not True:
        errors.append("head change reapproval gate removed")
    if "Human Steward disposition" not in activation.get("condition", ""):
        errors.append("Human Steward exact-head gate removed")
    if activation.get("effect") != "sphere_packing_route_proposal_admitted_no_registration_no_adjudication":
        errors.append("activation effect drift")

    reg_expected = {
        "cert_replay_evidence_merge": REPLAY_MERGE,
        "cert_replay_evidence_record_blob": REPLAY_BLOB,
        "global_registered_route_registry_blob": ROUTES_BLOB,
    }
    if registry.get("authority") != reg_expected:
        errors.append("proposal registry authority drift")
    rp = registry.get("proposal", {})
    if rp != {
        "result_family": "OTP-A-SPHERE-PACKING",
        "proposal_id": PROPOSAL_ID,
        "requested_route_id": ROUTE_ID,
        "path": "governance/result_family_route_proposal_successors/OTP-A-SPHERE-PACKING.json",
        "digest_algorithm": "git_blob_sha1",
        "digest": PROPOSAL_BLOB,
    }:
        errors.append("proposal registry digest/identity drift")
    if registry.get("state") != {
        "proposal_count": 1,
        "registered_route_count_created_by_this_operation": 0,
        "adjudication_count": 0,
        "cert_output_count": 0,
        "mathematical_target_proved_count": 0,
        "aggregate_route_count": 0,
    }:
        errors.append("proposal registry state inflation")
    if registry.get("scope") != {
        "target_count": 4,
        "another_family_target_count": 0,
        "aggregate_route": False,
        "whole_chapter_equivalence": False,
        "proof_body_equivalence": False,
        "source_authored_30_decimal_precision": False,
        "normalization_bridge_required": True,
    }:
        errors.append("proposal registry scope drift")
    if registry.get("route_controls") != {
        "global_registered_route_registry_modified": False,
        "proposal_registry_separate": True,
        "may_register_route": False,
        "may_adjudicate": False,
        "may_issue_cert_output": False,
        "may_mark_target_proved": False,
        "aggregate_route_prohibited": True,
        "may_promote_claim": False,
    }:
        errors.append("proposal registry authority inflation")

    for boundary in (proposal.get("claim_boundary", ""), registry.get("claim_boundary", "")):
        for phrase in ("does not", "register", "adjudication", "Cert output", "aggregate"):
            if phrase not in boundary:
                errors.append(f"claim boundary weakening: missing {phrase}")

    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("OTP_A_SPHERE_PACKING_ROUTE_PROPOSAL_CLEAR__REGISTRATION_AND_OUTPUT_SEPARATELY_GOVERNED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
