#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROPOSAL_DIR = ROOT / "governance/result_family_route_proposals"
REGISTRY_PATH = ROOT / "governance/pre_route_candidates/OPENAI_TEN_PROOFS_WP05_ROUTE_PROPOSALS.json"
ROUTES_PATH = ROOT / "governance/certification_routes.json"
SCHEMA_PATHS = (
    ROOT / "schemas/openai_ten_proofs_route_proposal.schema.json",
    ROOT / "schemas/openai_ten_proofs_route_proposal_registry.schema.json",
)

ROUTES_BLOB = "5b3e8d48b9f6c5b03ed3dc439bf9e43876e017b1"
TRACKER = "https://github.com/grandchallenge/MATHCERT/issues/53"
MERGES = {
    "solve_handoff_merge": "443daf537dc7e4ee34ab43aeb01508d9177816ab",
    "forge_semantic_merge": "cb0a203c36a9ef33270d62ab369df7bc27d3b242",
    "cert_intake_merge": "d99d2625ee838945087a91a50923cddc2dcc8d85",
    "cert_work_package_merge": "677a58a126145977581050bcb5d12d5b6a99fb51",
    "cert_replay_evidence_merge": "563c29c9687aad1bd06330436e3056cce7745c93",
}
OFFICIAL_SUBJECT = {
    "repository": "openai/ten-proofs",
    "commit": "e62211d28e3a9131950c89caa6542cfe5eff3bca",
    "tree": "2f8e7ac5ae7f157b6b1de636c2c343b1c7a7e365",
    "archive_sha256": "3022e62ffbed8f5f74d232034a703dc645e6b301879dff1e87df72979914294f",
}
SOURCE_REVISION_AUDIT = {
    "repository": "grandchallenge/MATHFORGE",
    "commit_sha": "a498ef40b7652b55bf121b5682604e259b8d3073",
    "path": "sources/OPENAI-TEN-PROOFS-001/source_revision_audits/OTP-TRANCHE-001.json",
    "digest_algorithm": "git_blob_sha1",
    "digest": "80d473b1b545fd9ca05fc5200bcf70ff5f9fcb05",
}
PROVIDER_MANIFEST = {
    "repository": "grandchallenge/MATHFORGE",
    "commit_sha": "0ea98866de3066e6a44ea1ca2cf93ade8a9e1c15",
    "path": "provider_manifests/OPENAI-TEN-PROOFS-001.json",
    "digest_algorithm": "git_blob_sha1",
    "digest": "fe1dab478e4ef9d6ddfe1b94a289fe7b51f58472",
}
EXPECTED = {
    "OTP-F-EHRHART": {
        "slug": "F-EHRHART",
        "packet_blob": "4653985d4980113514266c3c421804437bacb019",
        "semantic_blob": "a3dc4de4c38a80b7aec1fae6506b08e14d2e58bb",
        "intake_blob": "1c6a5f349803bba09b000ceb3f8a53ee3038ca48",
        "work_package_blob": "056149e7a659fb6b24b7d7389a3dcd68bb581bcd",
        "evidence_blob": "d17d36d02f6505060f5a9e5f1f71f3c323fa1af8",
        "bundle_slug": "ehrhart",
        "bundle_blob": "346eebb415609e6e66a9cb04510b7ba4994cf309",
        "bundle_sha256": "22fcaad533db94c03569439bb41fcda68618386826abd3aa624bbf90e9345adb",
        "locus": {"chapter": 8, "theorem": "Theorem 1.1", "pdf_page_index": 219, "printed_page": 218, "concordance": "clear_at_recorded_locus"},
        "exclusion_token": "classification",
    },
    "OTP-J1-COMPACTNESS": {
        "slug": "J1-COMPACTNESS",
        "packet_blob": "2d9c6e555a03b71eb33c476321e7f2d311ed168f",
        "semantic_blob": "659396358d0d999c00011645f72602f30ccf6b0e",
        "intake_blob": "d08eec02d7ee44f3bc2692cf7949c70d8e0f2bbf",
        "work_package_blob": "d80cade6d99c7ca54f4384a68e178b2f4335a8b2",
        "evidence_blob": "5fe635510a0d2aa05da641e342078cf8b2b34aa6",
        "bundle_slug": "compactness",
        "bundle_blob": "0f2a8918e669734ab89ece34b3f6dc60774552e2",
        "bundle_sha256": "852d0fa51a328199e6aeaf67a51fdd384ab30ec62ef6a7e28c5e22e597b3a99b",
        "locus": {"chapter": 10, "theorem": "Theorem 1.1", "pdf_page_index": 236, "printed_page": 235, "concordance": "clear_at_recorded_locus"},
        "exclusion_token": "construction",
    },
    "OTP-J2-TWO-DEGENERATE": {
        "slug": "J2-TWO-DEGENERATE",
        "packet_blob": "0d226492bf13e13bc1a437be01104db3d4c96f79",
        "semantic_blob": "7bd168c46921f64364b20021b6315d68f0fde7d0",
        "intake_blob": "6e9cfee8f988e357aabdd53e2883220d170b7e60",
        "work_package_blob": "dbbc4ab59f21b3f5cb2f313c51f754b9b306389c",
        "evidence_blob": "215ce18b4139159c89d167ab11cab6c35d5a38ff",
        "bundle_slug": "two-degenerate",
        "bundle_blob": "14d050b03ccc9891f8c3e5ec4f522aa5aa00b8aa",
        "bundle_sha256": "b3efb532152677dd84c0872071a9d2aa061ea56b9a8a7d9175c6382766f27ed4",
        "locus": {"chapter": 10, "theorem": "Theorem 1.2", "pdf_page_index": 236, "printed_page": 235, "concordance": "clear_at_recorded_locus"},
        "exclusion_token": "coloring",
    },
}

# Backward-compatible aliases used by the mutation suite.
P = PROPOSAL_DIR
R = REGISTRY_PATH
G = ROUTES_PATH
E = {
    family: (
        data["slug"], data["packet_blob"], data["semantic_blob"], data["intake_blob"],
        data["work_package_blob"], data["evidence_blob"], data["bundle_slug"],
        data["bundle_blob"], data["bundle_sha256"], data["locus"]["chapter"],
        data["locus"]["theorem"], data["locus"]["pdf_page_index"],
        data["locus"]["printed_page"],
    )
    for family, data in EXPECTED.items()
}

PROPOSAL_KEYS = {"schema_version", "record_type", "proposal_id", "candidate_id", "result_family", "requested_route_id", "proposal_state", "tracker_issue", "authority", "source_scope", "evidence_disposition", "route_controls", "activation", "claim_boundary"}
AUTHORITY_KEYS = {"official_subject", "solve_handoff_merge", "producer_packet", "forge_semantic_merge", "semantic_record", "cert_intake_merge", "cert_intake", "cert_work_package_merge", "cert_work_package", "cert_replay_evidence_merge", "replay_evidence", "repository_bundle", "source_revision_audit", "provider_manifest"}
SOURCE_SCOPE_KEYS = {"source_theorem", "current_revision_locus", "normalized_statement", "lean_theorems", "nonvacuity_witnesses", "scope_exclusions"}
REGISTRY_KEYS = {"schema_version", "record_type", "record_id", "candidate_id", "tracker_issue", "authority", "state", "proposals", "blocked_repair_lanes", "unexamined_result_family_count", "aggregate_integration", "route_controls", "activation", "claim_boundary"}
EVIDENCE_DISPOSITION = {"kernel_replay": "clear", "lean_kernel": "accept", "nanoda": "accept", "theorem_axiom_report": "permitted_only", "trust_boundary_scan": "clear", "source_semantic": "clear", "nonvacuity": "clear", "current_revision_locus": "clear", "whole_document_byte_equivalence": "not_established", "whole_document_semantic_equivalence": "not_established", "proof_body_compared_in_full": False}
ROUTE_CONTROLS = {"global_registered_route_registry_modified": False, "route_registry_entry": None, "may_register_route": False, "may_adjudicate": False, "cert_output": None, "mathematical_target_proved": False, "may_promote_claim": False, "aggregate_route": False, "aggregate_adjudication": False}
ACTIVATION = {"condition": "exact-head Cert checks, GCL conformance, non-author APPROVED specialist review, explicit exact-head Human Steward disposition, and protected MATHCERT merge", "head_change_requires_reapproval": True, "effect": "route_proposal_admitted_no_registration_no_adjudication"}
REGISTRY_IDENTITY = {"schema_version": "1.0.0", "record_type": "openai_ten_proofs_route_proposal_registry", "record_id": "MC-OPENAI-TEN-PROOFS-WP05-ROUTE-PROPOSALS", "candidate_id": "OPENAI-TEN-PROOFS-001", "tracker_issue": TRACKER}
REGISTRY_AUTHORITY = {"cert_replay_evidence_merge": MERGES["cert_replay_evidence_merge"], "forge_source_revision_audit_merge": SOURCE_REVISION_AUDIT["commit_sha"], "forge_provider_manifest_merge": PROVIDER_MANIFEST["commit_sha"], "source_revision_audit_blob": SOURCE_REVISION_AUDIT["digest"], "provider_manifest_blob": PROVIDER_MANIFEST["digest"], "global_registered_route_registry_blob": ROUTES_BLOB}
REGISTRY_STATE = {"proposal_count": 3, "registered_route_count": 0, "adjudication_count": 0, "cert_output_count": 0, "mathematical_target_proved_count": 0, "aggregate_route_count": 0}
REGISTRY_AGGREGATE = {"all_lean_state": "failed_namespace_collision", "reopens_family_replay": False, "creates_route": False, "creates_adjudication": False}
REGISTRY_CONTROLS = {"global_registered_route_registry_modified": False, "proposal_registry_separate": True, "may_register_route": False, "may_adjudicate": False, "may_issue_cert_output": False, "may_mark_target_proved": False, "aggregate_route_prohibited": True, "may_promote_claim": False}
REGISTRY_ACTIVATION = {"condition": ACTIVATION["condition"], "head_change_requires_reapproval": True, "effect": "three_route_proposals_admitted_no_registration_no_adjudication"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(f"blob {len(payload)}\0".encode("ascii") + payload, usedforsecurity=False).hexdigest()


blob = git_blob_sha1


def artifact(repository: str, commit: str, path: str, digest: str) -> dict[str, str]:
    return {"repository": repository, "commit_sha": commit, "path": path, "digest_algorithm": "git_blob_sha1", "digest": digest}


def open_object_paths(schema: Any) -> list[str]:
    found: list[str] = []
    def walk(value: Any, path: str = "") -> None:
        if isinstance(value, dict):
            if value.get("type") == "object" and value.get("additionalProperties") is not False:
                found.append(path or "/")
            for key, child in value.items():
                walk(child, f"{path}/{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, f"{path}/{index}")
    walk(schema)
    return found


def validation_errors(proposals: dict[str, dict[str, Any]] | None = None, registry: dict[str, Any] | None = None, routes: dict[str, Any] | None = None, local_blobs: dict[str, str] | None = None) -> list[str]:
    errors: list[str] = []
    for schema_path in SCHEMA_PATHS:
        if open_object_paths(load_json(schema_path)):
            errors.append(f"{schema_path.name}: open object schema")
    if proposals is None:
        proposals = {path.stem: load_json(path) for path in sorted(PROPOSAL_DIR.glob("*.json"))}
    if registry is None:
        registry = load_json(REGISTRY_PATH)
    if routes is None:
        routes = load_json(ROUTES_PATH)
    if set(proposals) != set(EXPECTED):
        errors.append("proposal membership drift")
    proposal_refs: list[dict[str, str]] = []
    requested_route_ids: set[str] = set()
    for family, expected in EXPECTED.items():
        proposal = proposals.get(family)
        if not isinstance(proposal, dict):
            continue
        if set(proposal) != PROPOSAL_KEYS:
            errors.append(f"{family}: fields drift")
        slug = expected["slug"]
        proposal_id = f"MC-OTP-ROUTE-PROPOSAL-{slug}"
        route_id = f"MC-ROUTE-OTP-{slug}"
        requested_route_ids.add(route_id)
        identity = (proposal.get("schema_version"), proposal.get("record_type"), proposal.get("proposal_id"), proposal.get("candidate_id"), proposal.get("result_family"), proposal.get("requested_route_id"), proposal.get("proposal_state"), proposal.get("tracker_issue"))
        if identity != ("1.0.0", "openai_ten_proofs_result_family_route_proposal", proposal_id, "OPENAI-TEN-PROOFS-001", family, route_id, "proposed_only", TRACKER):
            errors.append(f"{family}: proposal identity/state drift")
        authority = proposal.get("authority", {})
        if not isinstance(authority, dict) or set(authority) != AUTHORITY_KEYS:
            errors.append(f"{family}: authority shape drift")
            authority = {}
        if authority.get("official_subject") != OFFICIAL_SUBJECT:
            errors.append(f"{family}: official subject drift")
        for key, value in MERGES.items():
            if authority.get(key) != value:
                errors.append(f"{family}: {key} drift")
        packet_path = f"work_packages/OPENAI_TEN_PROOFS_WP00/result_family_handoffs/{family}.json"
        semantic_path = f"sources/OPENAI-TEN-PROOFS-001/semantic_audits/{family}.json"
        intake_path = f"governance/result_family_intakes/{family}.json"
        work_package_path = f"governance/result_family_work_packages/{family}-CERT-WP01.json"
        evidence_path = f"governance/result_family_replay_evidence/{family}.json"
        bundle_path = f"evidence/openai_ten_proofs/{expected['bundle_slug']}.zip.b64"
        expected_artifacts = {
            "producer_packet": artifact("grandchallenge/MATHSOLVE", MERGES["solve_handoff_merge"], packet_path, expected["packet_blob"]),
            "semantic_record": artifact("grandchallenge/MATHFORGE", MERGES["forge_semantic_merge"], semantic_path, expected["semantic_blob"]),
            "cert_intake": artifact("grandchallenge/MATHCERT", MERGES["cert_intake_merge"], intake_path, expected["intake_blob"]),
            "cert_work_package": artifact("grandchallenge/MATHCERT", MERGES["cert_work_package_merge"], work_package_path, expected["work_package_blob"]),
            "replay_evidence": artifact("grandchallenge/MATHCERT", MERGES["cert_replay_evidence_merge"], evidence_path, expected["evidence_blob"]),
        }
        for key, expected_artifact in expected_artifacts.items():
            if authority.get(key) != expected_artifact:
                errors.append(f"{family}: {key} drift")
        expected_bundle = artifact("grandchallenge/MATHCERT", MERGES["cert_replay_evidence_merge"], bundle_path, expected["bundle_blob"])
        expected_bundle["decoded_sha256"] = expected["bundle_sha256"]
        if authority.get("repository_bundle") != expected_bundle:
            errors.append(f"{family}: bundle drift")
        if authority.get("source_revision_audit") != SOURCE_REVISION_AUDIT:
            errors.append(f"{family}: source revision authority drift")
        if authority.get("provider_manifest") != PROVIDER_MANIFEST:
            errors.append(f"{family}: provider manifest authority drift")
        actual_blobs = ({path: git_blob_sha1(ROOT / path) for path in (intake_path, work_package_path, evidence_path, bundle_path)} if local_blobs is None else local_blobs)
        for path, digest in ((intake_path, expected["intake_blob"]), (work_package_path, expected["work_package_blob"]), (evidence_path, expected["evidence_blob"]), (bundle_path, expected["bundle_blob"])):
            if actual_blobs.get(path) != digest:
                errors.append(f"{family}: local blob drift {path}")
        source_scope = proposal.get("source_scope", {})
        if not isinstance(source_scope, dict) or set(source_scope) != SOURCE_SCOPE_KEYS:
            errors.append(f"{family}: source scope fields drift")
            source_scope = {}
        intake_scope = load_json(ROOT / intake_path).get("target_scope", {})
        for key in ("source_theorem", "normalized_statement", "lean_theorems", "nonvacuity_witnesses"):
            if source_scope.get(key) != intake_scope.get(key):
                errors.append(f"{family}: protected intake scope drift {key}")
        if source_scope.get("current_revision_locus") != expected["locus"]:
            errors.append(f"{family}: current-revision locus drift")
        exclusions = source_scope.get("scope_exclusions", [])
        if not isinstance(exclusions, list) or not any(expected["exclusion_token"] in str(item) for item in exclusions):
            errors.append(f"{family}: family exclusion removed")
        if proposal.get("evidence_disposition") != EVIDENCE_DISPOSITION:
            errors.append(f"{family}: evidence inflation")
        if proposal.get("route_controls") != ROUTE_CONTROLS:
            errors.append(f"{family}: route/adjudication/output/proof inflation")
        if proposal.get("activation") != ACTIVATION:
            errors.append(f"{family}: activation drift")
        claim = str(proposal.get("claim_boundary", ""))
        if not all(token in claim for token in ("does not register", "adjudicate", "Cert output", "aggregate")):
            errors.append(f"{family}: claim boundary drift")
        path = PROPOSAL_DIR / f"{family}.json"
        if path.is_file():
            proposal_refs.append({"result_family": family, "proposal_id": proposal_id, "requested_route_id": route_id, "path": str(path.relative_to(ROOT)), "digest_algorithm": "git_blob_sha1", "digest": git_blob_sha1(path)})
    if git_blob_sha1(ROUTES_PATH) != ROUTES_BLOB:
        errors.append("registered-route registry changed")
    registered = {str(item.get("route_id", "")) for item in routes.get("routes", []) if isinstance(item, dict)}
    if requested_route_ids & registered:
        errors.append("OTP route registered prematurely")
    if not isinstance(registry, dict) or set(registry) != REGISTRY_KEYS:
        errors.append("registry fields drift")
        registry = registry if isinstance(registry, dict) else {}
    for key, value in REGISTRY_IDENTITY.items():
        if registry.get(key) != value:
            errors.append(f"registry identity drift: {key}")
    if registry.get("authority") != REGISTRY_AUTHORITY:
        errors.append("registry authority drift")
    if registry.get("proposals") != proposal_refs:
        errors.append("registry proposal refs drift")
    if registry.get("state") != REGISTRY_STATE:
        errors.append("registry state inflation")
    if registry.get("blocked_repair_lanes") != ["OTP-C-PERMANENT", "OTP-H-GAPCVP"]:
        errors.append("blocked repair lane drift")
    if registry.get("unexamined_result_family_count") != 9:
        errors.append("unexamined result-family count drift")
    if registry.get("aggregate_integration") != REGISTRY_AGGREGATE:
        errors.append("All.lean boundary drift")
    if registry.get("route_controls") != REGISTRY_CONTROLS:
        errors.append("registry authority inflation")
    if registry.get("activation") != REGISTRY_ACTIVATION:
        errors.append("registry activation drift")
    registry_claim = str(registry.get("claim_boundary", ""))
    if not all(token in registry_claim for token in ("does not modify", "register a route", "adjudicate", "Cert output", "aggregate")):
        errors.append("registry claim boundary drift")
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"route proposal validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print("validated three proposed-only OTP family routes, exact content-addressed evidence, unchanged registered routes, and zero adjudication/output/proof authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
