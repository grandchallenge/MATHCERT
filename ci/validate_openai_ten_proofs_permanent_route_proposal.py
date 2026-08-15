#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "governance/result_family_route_proposal_successors/OTP-C-PERMANENT.json"
REGISTRY = ROOT / "governance/pre_route_candidates/OPENAI_TEN_PROOFS_PERMANENT_ROUTE_PROPOSAL.json"
ROUTES = ROOT / "governance/certification_routes.json"
INTAKE = ROOT / "governance/result_family_intakes/OTP-C-PERMANENT.json"
WORK_PACKAGE = ROOT / "governance/result_family_work_package_successors/OTP-C-PERMANENT-CERT-WP01.json"
REPLAY = ROOT / "governance/result_family_replay_evidence_successors/OTP-C-PERMANENT.json"
MANIFEST = ROOT / "evidence/openai_ten_proofs/permanent/SHA256SUMS"
SCHEMAS = (
    ROOT / "schemas/openai_ten_proofs_permanent_route_proposal.schema.json",
    ROOT / "schemas/openai_ten_proofs_permanent_route_proposal_registry.schema.json",
)

TRACKER = "https://github.com/grandchallenge/MATHCERT/issues/99"
ROUTE_ID = "MC-ROUTE-OTP-C-PERMANENT-FORMULA"
PROPOSAL_ID = "MC-OTP-ROUTE-PROPOSAL-C-PERMANENT-FORMULA"
PROPOSAL_BLOB = "27eb80d2361a571fdebeec0e31faa69b6c307604"
ROUTES_BLOB = "0487c3ebf702229741f16a544d68af25cf994e41"
INTAKE_BLOB = "80a9cf59ac4bad7cc08185e80b0d9ffe27b855e6"
WORK_PACKAGE_BLOB = "f3000340c2699ec819acbcd223c1ee4c63af1cc8"
REPLAY_BLOB = "7b75a323b6d840730932bf90984f498b7d360cda"
MANIFEST_BLOB = "cbc185bd0cd182fddd3127d8373ae7a74f6389dd"
MANIFEST_SHA256 = "351ab107342d2fe72220098ae6e5dc600653e9b181119c99805182270559f969"
THEOREMS = [
    "PermanentFormulaLowerBound.permanent_divisionFree_formula_logarithmic_lower_bound",
    "PermanentFormulaLowerBound.permanent_rational_formula_logarithmic_lower_bound",
]
WITNESSES = [
    "PermanentFormulaLowerBound.Nonvacuity.permanent_divisionFree_formula_nonvacuous",
    "PermanentFormulaLowerBound.Nonvacuity.permanent_rational_formula_nonvacuous",
]
SOURCE_PROJECTION = {
    "formula_target_count": 2,
    "circuit_target_count": 0,
    "coefficient_field": "complex",
    "dimension_threshold": 32,
    "log_base": 2,
    "division_free_variable_leaf_constant": 128,
    "rational_variable_leaf_constant": 192,
    "gate_bounds_in_route": False,
    "total_leaves_vertices_in_route": False,
    "historical_pdf_byte_equivalence": False,
}
ROUTE_CONTROLS = {
    "global_registered_route_registry_modified": False,
    "route_registry_entry": None,
    "may_register_route": False,
    "may_adjudicate": False,
    "cert_output": None,
    "mathematical_target_proved": False,
    "may_promote_claim": False,
    "aggregate_route": False,
    "aggregate_adjudication": False,
}
REGISTRY_CONTROLS = {
    "global_registered_route_registry_modified": False,
    "proposal_registry_separate": True,
    "may_register_route": False,
    "may_adjudicate": False,
    "may_issue_cert_output": False,
    "may_mark_target_proved": False,
    "aggregate_route_prohibited": True,
    "may_promote_claim": False,
}
EXPECTED_AUTHORITY = {
    "official_subject": {
        "repository": "openai/ten-proofs",
        "commit": "e62211d28e3a9131950c89caa6542cfe5eff3bca",
        "tree": "2f8e7ac5ae7f157b6b1de636c2c343b1c7a7e365",
        "archive_sha256": "3022e62ffbed8f5f74d232034a703dc645e6b301879dff1e87df72979914294f",
    },
    "forge_semantic": {
        "merge": "60f6e06c957139447bf5943eed731941b22ac608",
        "semantic_record_blob": "3e04bd16bd8a91eaf9b6702de89fcdcc72f61099",
        "nonvacuity_witness_blob": "e756c8476bac1795f3fb8ca0b7235d3a4a5c59ea",
    },
    "solve_handoff": {
        "merge": "90f8a8544e546a603b34c9b27b2d6a4a68e06de8",
        "producer_packet_blob": "a993c530880021930a2b468e76235b91122ca854",
    },
    "cert_intake": {
        "merge": "59e678a5692c873cb7b12b8913231bf520571f51",
        "record_blob": INTAKE_BLOB,
    },
    "cert_work_package": {
        "merge": "4b5d9e81afea50b5b51b4e390065f52275c886cd",
        "record_blob": WORK_PACKAGE_BLOB,
    },
    "cert_replay_evidence": {
        "merge": "7f42194bfcfb5b28f2bdb1f5b3203650a6b5ff15",
        "admitted_head": "6b86532820e5a7004fad6dbddc6fd8b01200776b",
        "record_blob": REPLAY_BLOB,
        "successor_registry_blob": "8cba28b623e2fac0aebacdcb12fe4f269c471ada",
        "evidence_root": "evidence/openai_ten_proofs/permanent/",
        "manifest_blob": MANIFEST_BLOB,
        "manifest_sha256": MANIFEST_SHA256,
        "transport_artifact_id": 9237666071,
        "transport_sha256": "9f04dbfd0fe6c52329b9905371d33faa44b2f96719485460c6290bc8a74fd507",
    },
    "global_registered_route_registry_blob": ROUTES_BLOB,
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data, usedforsecurity=False).hexdigest()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def validation_errors(
    proposal: dict[str, Any] | None = None,
    registry: dict[str, Any] | None = None,
    routes: dict[str, Any] | None = None,
    local_blobs: dict[str, str] | None = None,
) -> list[str]:
    errors: list[str] = []
    for schema_path in SCHEMAS:
        if open_object_paths(load(schema_path)):
            errors.append(f"{schema_path.name}: open object schema")

    proposal = load(PROPOSAL) if proposal is None else proposal
    registry = load(REGISTRY) if registry is None else registry
    routes = load(ROUTES) if routes is None else routes
    if local_blobs is None:
        local_blobs = {
            "proposal": git_blob_sha1(PROPOSAL),
            "intake": git_blob_sha1(INTAKE),
            "work_package": git_blob_sha1(WORK_PACKAGE),
            "replay": git_blob_sha1(REPLAY),
            "manifest": git_blob_sha1(MANIFEST),
        }

    successor_members = sorted(p.name for p in PROPOSAL.parent.glob("*.json"))
    if successor_members != ["OTP-C-PERMANENT.json"]:
        errors.append("successor proposal membership drift")

    expected_identity = (
        "1.0.0",
        "openai_ten_proofs_permanent_route_proposal",
        PROPOSAL_ID,
        "OPENAI-TEN-PROOFS-001",
        "OTP-C-PERMANENT",
        ROUTE_ID,
        "proposed_only",
        TRACKER,
    )
    actual_identity = (
        proposal.get("schema_version"), proposal.get("record_type"), proposal.get("proposal_id"),
        proposal.get("candidate_id"), proposal.get("result_family"), proposal.get("requested_route_id"),
        proposal.get("proposal_state"), proposal.get("tracker_issue"),
    )
    if actual_identity != expected_identity:
        errors.append("proposal identity/state drift")
    if proposal.get("authority") != EXPECTED_AUTHORITY:
        errors.append("proposal authority drift")

    scope = proposal.get("target_scope", {})
    if scope.get("lean_theorems") != THEOREMS:
        errors.append("theorem target drift")
    if scope.get("nonvacuity_witnesses") != WITNESSES:
        errors.append("nonvacuity witness drift")
    if scope.get("source_projection") != SOURCE_PROJECTION:
        errors.append("source projection drift")
    exclusions = scope.get("scope_exclusions", [])
    required_exclusion_tokens = ("circuit", "256", "384", "total-leaf", "PDF", "aggregate")
    joined = "\n".join(str(x) for x in exclusions)
    for token in required_exclusion_tokens:
        if token not in joined:
            errors.append(f"scope exclusion removed: {token}")

    expected_results = {
        "protected_archive_identity": "clear",
        "solution_build": "pass",
        "challenge_build": "pass_with_expected_comparator_boundary_sorries",
        "nonvacuity_replay": "pass",
        "comparator": "pass",
        "lean_kernel": "accept",
        "nanoda": "accept",
        "theorem_axiom_report": "permitted_only",
        "trust_boundary_scan": "clear",
        "semantic_concordance": "protected_predecessor_reconfirmed",
        "aggregate_all_dependency": "absent",
    }
    if proposal.get("evidence_disposition") != expected_results:
        errors.append("replay evidence disposition drift")
    if proposal.get("route_controls") != ROUTE_CONTROLS:
        errors.append("route registration/adjudication/output/proof inflation")
    if proposal.get("candidate_disposition") != "PERMANENT_FORMULA_CERT_ROUTE_PROPOSAL_CLEAR__REGISTRATION_NOT_YET_AUTHORIZED":
        errors.append("candidate disposition drift")
    claim = str(proposal.get("claim_boundary", ""))
    if not all(token in claim for token in ("does not register", "adjudicate", "Cert output", "circuit", "256/384", "aggregate")):
        errors.append("proposal claim boundary weakened")

    if local_blobs.get("proposal") != PROPOSAL_BLOB:
        errors.append("proposal blob drift")
    if local_blobs.get("intake") != INTAKE_BLOB:
        errors.append("protected intake blob drift")
    if local_blobs.get("work_package") != WORK_PACKAGE_BLOB:
        errors.append("protected work-package blob drift")
    if local_blobs.get("replay") != REPLAY_BLOB:
        errors.append("protected replay-evidence blob drift")
    if local_blobs.get("manifest") != MANIFEST_BLOB or sha256(MANIFEST) != MANIFEST_SHA256:
        errors.append("retained evidence manifest drift")

    registered_ids = [item.get("route_id") for item in routes.get("routes", []) if isinstance(item, dict)]
    if registered_ids.count(ROUTE_ID) > 1:
        errors.append("duplicate Permanent route registration")

    expected_registry_identity = (
        "1.0.0", "openai_ten_proofs_permanent_route_proposal_registry",
        "MC-OTP-C-PERMANENT-ROUTE-PROPOSAL-001", "OPENAI-TEN-PROOFS-001", TRACKER,
    )
    actual_registry_identity = (
        registry.get("schema_version"), registry.get("record_type"), registry.get("registry_id"),
        registry.get("candidate_id"), registry.get("tracker_issue"),
    )
    if actual_registry_identity != expected_registry_identity:
        errors.append("proposal registry identity drift")
    expected_registry_authority = {
        "cert_replay_evidence_merge": "7f42194bfcfb5b28f2bdb1f5b3203650a6b5ff15",
        "cert_replay_evidence_record_blob": REPLAY_BLOB,
        "global_registered_route_registry_blob": ROUTES_BLOB,
    }
    if registry.get("authority") != expected_registry_authority:
        errors.append("proposal registry authority drift")
    expected_ref = {
        "result_family": "OTP-C-PERMANENT",
        "proposal_id": PROPOSAL_ID,
        "requested_route_id": ROUTE_ID,
        "path": "governance/result_family_route_proposal_successors/OTP-C-PERMANENT.json",
        "digest_algorithm": "git_blob_sha1",
        "digest": PROPOSAL_BLOB,
    }
    if registry.get("proposal") != expected_ref:
        errors.append("proposal registry content-addressed ref drift")
    expected_state = {
        "proposal_count": 1,
        "registered_route_count_created_by_this_operation": 0,
        "adjudication_count": 0,
        "cert_output_count": 0,
        "mathematical_target_proved_count": 0,
        "aggregate_route_count": 0,
    }
    if registry.get("state") != expected_state:
        errors.append("proposal registry state inflation")
    if registry.get("scope") != {
        "formula_target_count": 2,
        "circuit_target_count": 0,
        "gate_bounds_in_route": False,
        "total_leaves_vertices_in_route": False,
        "historical_pdf_byte_equivalence": False,
    }:
        errors.append("proposal registry scope drift")
    if registry.get("route_controls") != REGISTRY_CONTROLS:
        errors.append("proposal registry authority inflation")
    registry_claim = str(registry.get("claim_boundary", ""))
    if not all(token in registry_claim for token in ("does not modify", "register", "adjudicate", "Cert output", "aggregate")):
        errors.append("proposal registry claim boundary weakened")
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"Permanent route proposal validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print("validated immutable proposed-only Permanent route predecessor; any downstream registration is governed separately with zero proposal-stage adjudication/output/proof authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
