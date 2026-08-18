#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "governance/pre_route_candidates/OPENAI_TEN_PROOFS_A_SPHERE_PACKING_ROUTE_REGISTRATION.json"
ROUTES = ROOT / "governance/certification_routes.json"
PROPOSAL = ROOT / "governance/result_family_route_proposal_successors/OTP-A-SPHERE-PACKING.json"
PROPOSAL_REGISTRY = ROOT / "governance/pre_route_candidates/OPENAI_TEN_PROOFS_A_SPHERE_PACKING_ROUTE_PROPOSAL.json"
REPLAY = ROOT / "governance/result_family_replay_evidence_successors/OTP-A-SPHERE-PACKING.json"
SCHEMA = ROOT / "schemas/openai_ten_proofs_sphere_packing_route_registration.schema.json"

ROUTE_ID = "MC-ROUTE-OTP-A-SPHERE-PACKING"
EXPECTED_BEFORE_BLOB = "2d17473b4731aa9d9c630b1e7777ad4bd794d993"
EXPECTED_ROUTES_BLOB = "b9bb0dc9e18856f50a88162df37c20c034327439"
EXPECTED_PROPOSAL_BLOB = "e216cfc893a99d853ca798a68c46adbf013239ff"
EXPECTED_PROPOSAL_REGISTRY_BLOB = "3543ce68170b40fdc79dfdfebfe9ffbd3d4c0add"
EXPECTED_REPLAY_BLOB = "5a2d17d158ee9e8b535de8ed0a1ed41612c5abd2"
EXPECTED_PROPOSAL_MERGE = "4b194b9632a9aa57fee21c3c054498d6b4a8ed57"
EXPECTED_PROPOSAL_HEAD = "e6d1747899e5cae7ac90152cc8c852eacd7561e9"
EXPECTED_TARGETS = [
    "PackingBounds.FullMain.exact_limit",
    "PackingBounds.FullMain.exact_binary_exponent",
    "PackingBounds.PackingBridge.sphere_packing_sharp_asymptotic_upper",
    "PackingBounds.sharpFullCohnElkiesManuscriptConclusions",
]
EXPECTED_CLASSIFICATIONS = [
    "direct_source_theorem_projection_modulo_proved_full_radial_equivalence",
    "derived_base_two_logarithmic_consequence",
    "source_faithful_displayed_consequence_with_proved_scale_normalization",
    "source_faithful_derived_composite_certificate",
]
EXPECTED_AXIOMS = ["propext", "Quot.sound", "Classical.choice"]
EXPECTED_SOURCE = {
    "repository": "grandchallenge/MATHFORGE",
    "commit_sha": "706d0291370bf3f14aa37be0823e33d06f7343b0",
    "path": "sources/OPENAI-TEN-PROOFS-001/semantic/OTP-A-SPHERE-PACKING-COMPOSITE/audit_record.json",
    "digest_algorithm": "git_blob_sha1",
    "digest": "b2e309ad96e750651fc7149a6bad54c6bf99015b",
}
EXPECTED_BRIDGE = {
    "repository": "grandchallenge/MATHFORGE",
    "commit_sha": "5a0cb9a7b7eef210dd0fce5c527d09b6eef3bc12",
    "path": "sources/OPENAI-TEN-PROOFS-001/semantic/OTP-A-SPHERE-PACKING-BRIDGE/audit_record.json",
    "digest_algorithm": "git_blob_sha1",
    "digest": "7858b156fc4490ecc6e3572dcf449d84dcc99f93",
}
EXPECTED_PACKET = {
    "repository": "grandchallenge/MATHSOLVE",
    "commit_sha": "c19735edf4c16ac9765bb66c7209bbf11bf1312e",
    "path": "work_packages/OPENAI_TEN_PROOFS_WP00/result_family_handoff_successors/OTP-A-SPHERE-PACKING.json",
    "digest_algorithm": "git_blob_sha1",
    "digest": "9e3b46972bf01ac3d24c6a0ae5f522799335ecd1",
}
EXPECTED_PRIOR_ROUTE_IDS = {
    "MC-ROUTE-UC-001", "MC-ROUTE-NS-CI-001", "MC-ROUTE-HC-001", "MC-ROUTE-BSD-001",
    "MC-ROUTE-PNP-001", "MC-ROUTE-RH-001", "MC-ROUTE-YM-001", "MC-ROUTE-OZ-001",
    "MC-ROUTE-OTP-F-EHRHART", "MC-ROUTE-OTP-J1-COMPACTNESS",
    "MC-ROUTE-OTP-J2-TWO-DEGENERATE", "MC-ROUTE-OTP-C-PERMANENT-FORMULA",
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


def validation_errors(receipt: dict[str, Any] | None = None, routes: dict[str, Any] | None = None, local_blobs: dict[str, str] | None = None) -> list[str]:
    errors: list[str] = []
    receipt = load(RECEIPT) if receipt is None else receipt
    routes = load(ROUTES) if routes is None else routes
    schema = load(SCHEMA)

    if open_object_paths(schema):
        errors.append("registration schema contains open object")
    for error in sorted(Draft202012Validator(schema).iter_errors(receipt), key=lambda e: list(e.path)):
        errors.append(f"schema: {'/'.join(map(str, error.path))}: {error.message}")

    blobs = {
        "routes": git_blob_sha1(ROUTES),
        "proposal": git_blob_sha1(PROPOSAL),
        "proposal_registry": git_blob_sha1(PROPOSAL_REGISTRY),
        "replay": git_blob_sha1(REPLAY),
    } if local_blobs is None else local_blobs
    if blobs.get("routes") != EXPECTED_ROUTES_BLOB: errors.append("registered route registry blob drift")
    if blobs.get("proposal") != EXPECTED_PROPOSAL_BLOB: errors.append("proposal record blob drift")
    if blobs.get("proposal_registry") != EXPECTED_PROPOSAL_REGISTRY_BLOB: errors.append("proposal registry blob drift")
    if blobs.get("replay") != EXPECTED_REPLAY_BLOB: errors.append("replay evidence blob drift")

    authority = receipt.get("authority", {})
    expected_authority_scalars = {
        "proposal_merge": EXPECTED_PROPOSAL_MERGE,
        "proposal_reviewed_head": EXPECTED_PROPOSAL_HEAD,
        "proposal_review_id": 4966426476,
        "proposal_reviewer": "jimsteeg",
        "proposal_disposition_comment": 5335273281,
        "registered_route_registry_before_blob": EXPECTED_BEFORE_BLOB,
        "registered_route_registry_candidate_blob": EXPECTED_ROUTES_BLOB,
        "cert_intake_merge": "947b3bed0effa79c2472dddc37d6c463f79c3126",
        "cert_intake_blob": "294c9f7d6cceb1cdf7ec4c8e73255dd1ba130670",
        "cert_work_package_merge": "54b883bb5c6ffaf099efd7270df3519a45b13038",
        "cert_work_package_blob": "f0c91d1959035f35843c383920dfba0b6c24b485",
        "cert_replay_evidence_merge": "036646952651057deadc5c485ef9e80a086865cd",
        "cert_replay_evidence_blob": EXPECTED_REPLAY_BLOB,
        "cert_replay_evidence_id": "MC-OTP-A-SPHERE-PACKING-REPLAY-EVIDENCE-001",
        "evidence_bundle_sha256": "0ec443cd35cee041d5bdc154de2e5d1697a21cdffbcc01d21c08c6aad61f10f3",
    }
    for key, value in expected_authority_scalars.items():
        if authority.get(key) != value: errors.append(f"authority drift: {key}")
    if authority.get("proposal_record", {}).get("digest") != EXPECTED_PROPOSAL_BLOB: errors.append("proposal record authority drift")
    if authority.get("proposal_registry", {}).get("digest") != EXPECTED_PROPOSAL_REGISTRY_BLOB: errors.append("proposal registry authority drift")
    if authority.get("forge_composite_semantic") != EXPECTED_SOURCE: errors.append("composite semantic authority drift")
    if authority.get("forge_bridge_semantic") != EXPECTED_BRIDGE: errors.append("bridge semantic authority drift")
    if authority.get("solve_handoff") != EXPECTED_PACKET: errors.append("Solve handoff authority drift")
    if authority.get("official_subject") != {"repository":"openai/ten-proofs","commit":"94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6","tree":"174289e4d4958cb0509874e6e53400e098213de7"}: errors.append("official subject drift")

    if routes.get("provider_base_commit") != EXPECTED_PROPOSAL_MERGE: errors.append("provider base does not bind protected proposal merge")
    route_list = routes.get("routes", [])
    if not isinstance(route_list, list): return errors + ["routes must be a list"]
    route_ids = [r.get("route_id") for r in route_list if isinstance(r, dict)]
    if len(route_ids) != 13 or set(route_ids) != EXPECTED_PRIOR_ROUTE_IDS | {ROUTE_ID}: errors.append("route membership drift")
    if route_ids.count(ROUTE_ID) != 1: errors.append("A route membership must be exactly one")
    if "MC-ROUTE-OPENAI-TEN-PROOFS-001" in route_ids or "OPENAI-TEN-PROOFS-001" in route_ids: errors.append("aggregate route inserted")
    route = next((r for r in route_list if isinstance(r, dict) and r.get("route_id") == ROUTE_ID), {})
    if route.get("campaign_id") != "OTP-A-SPHERE-PACKING" or route.get("tracker_issue") != "https://github.com/grandchallenge/MATHCERT/issues/158": errors.append("A route identity drift")
    if route.get("source_manifest") != EXPECTED_SOURCE: errors.append("A route source authority drift")
    if route.get("intake_packet") != EXPECTED_PACKET: errors.append("A route Solve packet drift")
    if route.get("intake_status") != "submitted": errors.append("A route must remain submitted/non-adjudicated")
    if route.get("target_claim_ids") != EXPECTED_TARGETS: errors.append("A route target drift")
    if route.get("cert_output") is not None: errors.append("Cert output inserted")
    if not any("adjudication" in str(x).lower() for x in route.get("blockers", [])): errors.append("adjudication blocker missing")
    claim = str(route.get("claim_boundary", ""))
    for token in ("does not adjudicate", "30-decimal", "positive-rescaling/unit-separation", "manuscript-verbatim", "aggregate"):
        if token not in claim: errors.append(f"A route claim boundary missing {token}")

    registration = receipt.get("registration", {})
    if registration.get("route_status") != "submitted": errors.append("receipt route status drift")
    if registration.get("target_count") != 4 or registration.get("target_claim_ids") != EXPECTED_TARGETS: errors.append("receipt target drift")
    if registration.get("classifications") != EXPECTED_CLASSIFICATIONS: errors.append("receipt classification drift")
    if registration.get("permitted_axioms") != EXPECTED_AXIOMS: errors.append("permitted axiom drift")
    quals = registration.get("mandatory_qualifications", [])
    for token in ("not a single verbatim manuscript theorem", "not manuscript-authored precision", "positive rescaling invariance", "not a stronger rate claim", "No whole-chapter"):
        if not any(token in str(q) for q in quals): errors.append(f"mandatory qualification missing {token}")

    if receipt.get("state") != {"registered_route_count_created_by_this_operation":1,"submitted_route_count":1,"adjudication_count":0,"cert_output_count":0,"mathematical_target_proved_count":0,"aggregate_route_count":0}: errors.append("registration state inflation")
    controls = receipt.get("route_controls", {})
    if controls.get("registration_scope") != "exact_one_sphere_packing_four_target_route": errors.append("registration scope drift")
    for key in ("may_adjudicate","may_issue_cert_output","may_mark_target_proved","may_promote_claim","may_reclassify_composite_as_verbatim_source_theorem","may_attribute_decimal_precision_to_source","may_remove_scale_normalization_boundary","whole_chapter_equivalence_established","full_proof_body_equivalence_established"):
        if controls.get(key) is not False: errors.append(f"registration authority inflation: {key}")
    if controls.get("aggregate_route_prohibited") is not True: errors.append("aggregate route prohibition removed")
    if receipt.get("candidate_disposition") != "A_SPHERE_PACKING_CERT_ROUTE_REGISTERED__NO_ADJUDICATION_OR_OUTPUT_AUTHORITY": errors.append("candidate disposition drift")
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"A sphere-packing route registration validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print("A_SPHERE_PACKING_CERT_ROUTE_REGISTERED__NO_ADJUDICATION_OR_OUTPUT_AUTHORITY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
