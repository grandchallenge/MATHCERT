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
DESIGN_CONTRACT = ROOT / "governance/result_family_adjudication_contracts/OTP-A-SPHERE-PACKING.json"
DESIGN_REGISTRY = ROOT / "governance/adjudication_design/OPENAI_TEN_PROOFS_A_SPHERE_PACKING_ADJUDICATION_CONTRACT.json"
DESIGN_CONTRACT_SCHEMA = ROOT / "schemas/openai_ten_proofs_sphere_packing_adjudication_contract.schema.json"
DESIGN_REGISTRY_SCHEMA = ROOT / "schemas/openai_ten_proofs_sphere_packing_adjudication_contract_registry.schema.json"
EXECUTED_ADJUDICATION = ROOT / "governance/result_family_adjudications/OTP-A-SPHERE-PACKING.json"
CERTIFICATE = ROOT / "certificates/formal_sources/MC-OTP-A-SPHERE-PACKING-001.json"

ROUTE_ID = "MC-ROUTE-OTP-A-SPHERE-PACKING"
EXPECTED_BEFORE_BLOB = "2d17473b4731aa9d9c630b1e7777ad4bd794d993"
EXPECTED_ROUTES_BLOB = "b9bb0dc9e18856f50a88162df37c20c034327439"
EXPECTED_OUTPUT_ROUTES_BLOB = "4d5c8e3f2b33d5148d98e7057991e167938c75bb"
EXPECTED_OUTPUT_CERTIFICATE_BLOB = "534e98ad2f00406fc869ea137f802f8cf504798a"
EXPECTED_OUTPUT_CONTENT_COMMIT = "1815f1b4010122e5bef0438f84da0b06204ba487"
EXPECTED_REGISTRATION_RECEIPT_BLOB = "2d9a520a3ef868c4d6d721cffc6cf89e546c6d09"
EXPECTED_PROPOSAL_BLOB = "e216cfc893a99d853ca798a68c46adbf013239ff"
EXPECTED_PROPOSAL_REGISTRY_BLOB = "3543ce68170b40fdc79dfdfebfe9ffbd3d4c0add"
EXPECTED_REPLAY_BLOB = "5a2d17d158ee9e8b535de8ed0a1ed41612c5abd2"
EXPECTED_PROPOSAL_MERGE = "4b194b9632a9aa57fee21c3c054498d6b4a8ed57"
EXPECTED_PROPOSAL_HEAD = "e6d1747899e5cae7ac90152cc8c852eacd7561e9"
EXPECTED_REGISTRATION_MERGE = "7179ed9c6060f44e46fb821a569e2c0c2f75c215"
EXPECTED_REGISTRATION_HEAD = "bc695488de218ba7625244b63fc450b4e107c23c"
EXPECTED_REGISTRATION_DISPOSITION_COMMENT = 5337346274
EXPECTED_DESIGN_AUTHORIZATION_COMMENT = 5337465770
EXPECTED_DESIGN_CONTRACT_BLOB = "5f56cdc5c5c839e1040bea84c2d756d805dd1c3b"
EXPECTED_DESIGN_REGISTRY_BLOB = "3605d660e4c4b57405ea03c4abfedb32d9deab93"
EXPECTED_EXECUTED_ADJUDICATION_BLOB = "3e0b34dbc74fdbe123f551d559e4f93fc1901c48"
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
EXPECTED_DISPOSITIONS = ["adjudication_clear_protected_four_targets_only", "adjudication_not_clear", "defer_insufficient_evidence"]
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
EXPECTED_OUTPUT = {
    "repository": "grandchallenge/MATHCERT",
    "commit_sha": EXPECTED_OUTPUT_CONTENT_COMMIT,
    "path": "certificates/formal_sources/MC-OTP-A-SPHERE-PACKING-001.json",
    "digest_algorithm": "git_blob_sha1",
    "digest": EXPECTED_OUTPUT_CERTIFICATE_BLOB,
}
OLD_BOUNDARY = "This registered route is limited to the exact four protected OTP-A-SPHERE-PACKING targets and preserves their mixed source/derived classifications, formal-only provenance of the 30-decimal base-two exponent enclosure, and the proved positive-rescaling/unit-separation normalization required for the packing bridge. It does not adjudicate or prove any target, issue a Cert output, represent the ten-field composite as one manuscript-verbatim theorem, attribute formal decimal precision to the manuscript, establish whole-chapter or full proof-body equivalence, qualify another result family, or create aggregate OpenAI Ten Proofs authority."
OLD_BLOCKERS = [
    "No MATHCERT adjudication has been authorized or recorded.",
    "The ten-field composite remains a mixed source/derived certificate rather than one manuscript-verbatim theorem, and the 30-decimal enclosure remains formal-only precision.",
    "The packing bridge remains governed by the protected positive-rescaling/unit-separation normalization; whole-chapter and full proof-body equivalence remain unestablished.",
]
OLD_REOPENING = ["Update this route only through a separately authorized, exact-head reviewed MATHCERT adjudication, authority-repin, or scope-change operation; any change to the four targets, source/derived classifications, normalization boundary, source precision attribution, or proof status requires separate governance."]
NEW_BOUNDARY = "This restricted route qualification applies only to the exact four protected OTP-A-SPHERE-PACKING targets under their distinct source-derived classifications and protected disposition qualified_protected_four_targets_only. It does not mark any mathematical target proved, represent the ten-field composite as one manuscript-verbatim theorem, attribute the formal 30-decimal base-two exponent enclosure to manuscript-authored precision, erase the positive-rescaling or unit-separation normalization required for the packing bridge, strengthen the explicit little-o normal form, establish whole-chapter or full proof-body equivalence, qualify another result family, or create aggregate OpenAI Ten Proofs authority."
NEW_BLOCKERS = [
    "No mathematical target is marked proved by this restricted qualification.",
    "The ten-field composite remains a mixed source/derived certificate rather than one manuscript-verbatim theorem, and the 30-decimal enclosure remains formal-only precision.",
    "The packing bridge remains governed by the protected positive-rescaling/unit-separation normalization; the explicit little-o witness remains a normal form only; whole-chapter and full proof-body equivalence remain unestablished.",
]
NEW_REOPENING = ["Update this route only through a separately governed, exact-head reviewed operation when the exact four-target scope, source/derived classifications, protected certificate identity, normalization boundary, source precision attribution, little-o boundary, or mathematical proof status changes."]


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
            for key, child in node.items(): walk(child, f"{path}/{key}")
        elif isinstance(node, list):
            for i, child in enumerate(node): walk(child, f"{path}/{i}")
    walk(value)
    return found


def find_route(routes: dict[str, Any]) -> dict[str, Any]:
    return next((r for r in routes.get("routes", []) if isinstance(r, dict) and r.get("route_id") == ROUTE_ID), {})


def live_successor_errors(routes: dict[str, Any], route_blob: str | None = None) -> list[str]:
    errors: list[str] = []
    rows = routes.get("routes", [])
    ids = [r.get("route_id") for r in rows if isinstance(r, dict)] if isinstance(rows, list) else []
    if len(ids) != 13 or set(ids) != EXPECTED_PRIOR_ROUTE_IDS | {ROUTE_ID}: errors.append("route membership drift")
    if ids.count(ROUTE_ID) != 1: errors.append("A route membership must be exactly one")
    if "MC-ROUTE-OPENAI-TEN-PROOFS-001" in ids or "OPENAI-TEN-PROOFS-001" in ids: errors.append("aggregate route inserted")
    route = find_route(routes)
    if route.get("campaign_id") != "OTP-A-SPHERE-PACKING" or route.get("tracker_issue") != "https://github.com/grandchallenge/MATHCERT/issues/158": errors.append("A route identity drift")
    if route.get("source_manifest") != EXPECTED_SOURCE: errors.append("A route source authority drift")
    if route.get("intake_packet") != EXPECTED_PACKET: errors.append("A route Solve packet drift")
    if route.get("target_claim_ids") != EXPECTED_TARGETS: errors.append("A route target drift")
    if route.get("requested_modalities") != ["LEAN_FORMALIZATION", "SEMANTIC_REPLAY", "SPECIALIST_AUDIT_PENDING"]: errors.append("A route modality drift")
    state = route.get("intake_status")
    if state == "submitted":
        if route_blob is not None and route_blob != EXPECTED_ROUTES_BLOB: errors.append("submitted A route registry blob drift")
        if route.get("cert_output") is not None: errors.append("submitted A route gained Cert output")
        if route.get("claim_boundary") != OLD_BOUNDARY or route.get("blockers") != OLD_BLOCKERS or route.get("reopening_conditions") != OLD_REOPENING: errors.append("submitted A route semantic drift")
    elif state == "qualified":
        if route_blob is not None and route_blob != EXPECTED_OUTPUT_ROUTES_BLOB: errors.append("qualified A route registry blob drift")
        if route.get("cert_output") != EXPECTED_OUTPUT: errors.append("qualified A Cert output identity drift")
        if route.get("claim_boundary") != NEW_BOUNDARY or route.get("blockers") != NEW_BLOCKERS or route.get("reopening_conditions") != NEW_REOPENING: errors.append("qualified A route semantic drift")
    else:
        errors.append("A route has unauthorized state")
    return errors


def registration_validation_errors(receipt: dict[str, Any] | None = None, routes: dict[str, Any] | None = None, local_blobs: dict[str, str] | None = None) -> list[str]:
    errors: list[str] = []
    receipt = load(RECEIPT) if receipt is None else receipt
    routes = load(ROUTES) if routes is None else routes
    schema = load(SCHEMA)
    if open_object_paths(schema): errors.append("registration schema contains open object")
    for error in sorted(Draft202012Validator(schema).iter_errors(receipt), key=lambda e: list(e.path)):
        errors.append(f"schema: {'/'.join(map(str, error.path))}: {error.message}")
    blobs = ({"routes":git_blob_sha1(ROUTES),"proposal":git_blob_sha1(PROPOSAL),"proposal_registry":git_blob_sha1(PROPOSAL_REGISTRY),"replay":git_blob_sha1(REPLAY)} if local_blobs is None else local_blobs)
    if blobs.get("proposal") != EXPECTED_PROPOSAL_BLOB: errors.append("proposal record blob drift")
    if blobs.get("proposal_registry") != EXPECTED_PROPOSAL_REGISTRY_BLOB: errors.append("proposal registry blob drift")
    if blobs.get("replay") != EXPECTED_REPLAY_BLOB: errors.append("replay evidence blob drift")
    errors.extend(live_successor_errors(routes, blobs.get("routes")))
    authority = receipt.get("authority", {})
    expected_scalars = {
        "proposal_merge": EXPECTED_PROPOSAL_MERGE, "proposal_reviewed_head": EXPECTED_PROPOSAL_HEAD,
        "proposal_review_id": 4966426476, "proposal_reviewer": "jimsteeg", "proposal_disposition_comment": 5335273281,
        "registered_route_registry_before_blob": EXPECTED_BEFORE_BLOB, "registered_route_registry_candidate_blob": EXPECTED_ROUTES_BLOB,
        "cert_intake_merge": "947b3bed0effa79c2472dddc37d6c463f79c3126", "cert_intake_blob": "294c9f7d6cceb1cdf7ec4c8e73255dd1ba130670",
        "cert_work_package_merge": "54b883bb5c6ffaf099efd7270df3519a45b13038", "cert_work_package_blob": "f0c91d1959035f35843c383920dfba0b6c24b485",
        "cert_replay_evidence_merge": "036646952651057deadc5c485ef9e80a086865cd", "cert_replay_evidence_blob": EXPECTED_REPLAY_BLOB,
        "cert_replay_evidence_id": "MC-OTP-A-SPHERE-PACKING-REPLAY-EVIDENCE-001", "evidence_bundle_sha256": "0ec443cd35cee041d5bdc154de2e5d1697a21cdffbcc01d21c08c6aad61f10f3",
    }
    for key, value in expected_scalars.items():
        if authority.get(key) != value: errors.append(f"authority drift: {key}")
    if authority.get("proposal_record", {}).get("digest") != EXPECTED_PROPOSAL_BLOB: errors.append("proposal record authority drift")
    if authority.get("proposal_registry", {}).get("digest") != EXPECTED_PROPOSAL_REGISTRY_BLOB: errors.append("proposal registry authority drift")
    if authority.get("forge_composite_semantic") != EXPECTED_SOURCE: errors.append("composite semantic authority drift")
    if authority.get("forge_bridge_semantic") != EXPECTED_BRIDGE: errors.append("bridge semantic authority drift")
    if authority.get("solve_handoff") != EXPECTED_PACKET: errors.append("Solve handoff authority drift")
    if authority.get("official_subject") != {"repository":"openai/ten-proofs","commit":"94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6","tree":"174289e4d4958cb0509874e6e53400e098213de7"}: errors.append("official subject drift")
    registration = receipt.get("registration", {})
    if registration.get("route_status") != "submitted" or registration.get("target_count") != 4 or registration.get("target_claim_ids") != EXPECTED_TARGETS: errors.append("historical registration scope/state drift")
    if registration.get("classifications") != EXPECTED_CLASSIFICATIONS or registration.get("permitted_axioms") != EXPECTED_AXIOMS: errors.append("historical registration classification/axiom drift")
    if receipt.get("state") != {"registered_route_count_created_by_this_operation":1,"submitted_route_count":1,"adjudication_count":0,"cert_output_count":0,"mathematical_target_proved_count":0,"aggregate_route_count":0}: errors.append("historical registration state inflation")
    controls = receipt.get("route_controls", {})
    for key in ("may_adjudicate","may_issue_cert_output","may_mark_target_proved","may_promote_claim","may_reclassify_composite_as_verbatim_source_theorem","may_attribute_decimal_precision_to_source","may_remove_scale_normalization_boundary","whole_chapter_equivalence_established","full_proof_body_equivalence_established"):
        if controls.get(key) is not False: errors.append(f"registration authority inflation: {key}")
    if controls.get("aggregate_route_prohibited") is not True: errors.append("aggregate route prohibition removed")
    if receipt.get("candidate_disposition") != "A_SPHERE_PACKING_CERT_ROUTE_REGISTERED__NO_ADJUDICATION_OR_OUTPUT_AUTHORITY": errors.append("candidate disposition drift")
    return errors


def design_validation_errors(contract: dict[str, Any] | None = None, registry: dict[str, Any] | None = None, local_blobs: dict[str, str] | None = None) -> list[str]:
    errors: list[str] = []
    contract = load(DESIGN_CONTRACT) if contract is None else contract
    registry = load(DESIGN_REGISTRY) if registry is None else registry
    c_schema = load(DESIGN_CONTRACT_SCHEMA); r_schema = load(DESIGN_REGISTRY_SCHEMA)
    if open_object_paths(c_schema) or open_object_paths(r_schema): errors.append("A adjudication-design schema contains open object")
    errors.extend(f"design contract schema: {e.message}" for e in Draft202012Validator(c_schema).iter_errors(contract))
    errors.extend(f"design registry schema: {e.message}" for e in Draft202012Validator(r_schema).iter_errors(registry))
    blobs = ({"contract":git_blob_sha1(DESIGN_CONTRACT),"registry":git_blob_sha1(DESIGN_REGISTRY),"routes":git_blob_sha1(ROUTES),"registration_receipt":git_blob_sha1(RECEIPT),"proposal":git_blob_sha1(PROPOSAL),"proposal_registry":git_blob_sha1(PROPOSAL_REGISTRY),"replay":git_blob_sha1(REPLAY)} if local_blobs is None else local_blobs)
    fixed = {"contract":EXPECTED_DESIGN_CONTRACT_BLOB,"registry":EXPECTED_DESIGN_REGISTRY_BLOB,"registration_receipt":EXPECTED_REGISTRATION_RECEIPT_BLOB,"proposal":EXPECTED_PROPOSAL_BLOB,"proposal_registry":EXPECTED_PROPOSAL_REGISTRY_BLOB,"replay":EXPECTED_REPLAY_BLOB}
    for key, value in fixed.items():
        if blobs.get(key) != value: errors.append(f"A adjudication-design protected blob drift: {key}")
    if blobs.get("routes") not in (EXPECTED_ROUTES_BLOB, EXPECTED_OUTPUT_ROUTES_BLOB): errors.append("A adjudication-design protected blob drift: routes")
    authority = contract.get("authority", {})
    if authority.get("registration_merge") != EXPECTED_REGISTRATION_MERGE or authority.get("registration_head") != EXPECTED_REGISTRATION_HEAD: errors.append("design registration authority drift")
    if authority.get("registration_human_steward_disposition_comment") != EXPECTED_REGISTRATION_DISPOSITION_COMMENT: errors.append("registration Human Steward disposition drift")
    if authority.get("registered_route_registry_blob") != EXPECTED_ROUTES_BLOB: errors.append("design contract historical route-registry authority drift")
    if authority.get("implementation_authorization") != {"tracker_issue":"https://github.com/grandchallenge/MATHCERT/issues/160","comment_id":EXPECTED_DESIGN_AUTHORIZATION_COMMENT,"scope":"design_only_sphere_packing_adjudication_contract"}: errors.append("design implementation authorization drift")
    if authority.get("solve_handoff") != EXPECTED_PACKET or authority.get("forge_composite_semantic") != EXPECTED_SOURCE or authority.get("forge_bridge_semantic") != EXPECTED_BRIDGE: errors.append("design protected source authority drift")
    scope = contract.get("route_scope", {})
    if scope.get("target_claim_ids") != EXPECTED_TARGETS or scope.get("classifications") != EXPECTED_CLASSIFICATIONS or scope.get("permitted_axioms") != EXPECTED_AXIOMS: errors.append("design route scope drift")
    if scope.get("registered_route_state") != "submitted": errors.append("historical design registered-route state drift")
    state = contract.get("state", {})
    for key in ("may_adjudicate","mathematical_target_proved","may_promote_claim","aggregate_adjudication"):
        if state.get(key) is not False: errors.append(f"design authority inflation: {key}")
    if state.get("adjudication") is not None or state.get("cert_output") is not None: errors.append("historical design inserted adjudication/output")
    gate = contract.get("execution_gate", {})
    if gate.get("routine_stage_progression_without_human_steward_intervention") is not True or gate.get("human_steward_intervention_required_for_control_plan_change") is not True or gate.get("fresh_non_author_approval_required") is not True: errors.append("design execution gate drift")
    limits = contract.get("preserved_limitations", {})
    if limits.get("manuscript_decimal_precision_attributed") is not False or limits.get("scale_normalization_boundary_required") is not True or limits.get("composite_is_single_verbatim_source_theorem") is not False: errors.append("design preserved limitation drift")
    refs = registry.get("contracts", [])
    if len(refs) != 1 or refs[0].get("contract", {}).get("digest") != EXPECTED_DESIGN_CONTRACT_BLOB: errors.append("A design registry contract reference drift")
    if registry.get("state") != {"contract_count":1,"design_only_contract_count":1,"may_adjudicate_count":0,"adjudication_count":0,"cert_output_count":0,"mathematical_target_proved_count":0,"aggregate_adjudication_count":0}: errors.append("A design registry state inflation")
    controls = registry.get("controls", {})
    for key in ("may_adjudicate","may_issue_cert_output","may_mark_target_proved","may_promote_claim"):
        if controls.get(key) is not False: errors.append(f"A design registry authority inflation: {key}")
    activation = registry.get("activation", {})
    if activation.get("routine_stage_progression_without_human_steward_intervention") is not True or activation.get("human_steward_intervention_required_for_control_plan_change") is not True: errors.append("A design registry activation drift")
    if EXECUTED_ADJUDICATION.exists() and git_blob_sha1(EXECUTED_ADJUDICATION) != EXPECTED_EXECUTED_ADJUDICATION_BLOB: errors.append("executed A adjudication protected blob drift")
    if local_blobs is None:
        errors.extend(live_successor_errors(load(ROUTES), blobs.get("routes")))
    return errors


def validation_errors(receipt: dict[str, Any] | None = None, routes: dict[str, Any] | None = None, local_blobs: dict[str, str] | None = None, *, design_contract: dict[str, Any] | None = None, design_registry: dict[str, Any] | None = None, design_blobs: dict[str, str] | None = None) -> list[str]:
    return registration_validation_errors(receipt, routes, local_blobs) + design_validation_errors(design_contract, design_registry, design_blobs)


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"A route-registration/output-successor validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    state = find_route(load(ROUTES)).get("intake_status")
    print(f"validated immutable A registration/design history and exact live A route successor state={state}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
