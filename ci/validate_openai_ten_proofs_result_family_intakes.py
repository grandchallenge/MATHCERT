#!/usr/bin/env python3
"""Validate independent OpenAI ten-proofs MATHCERT intake records."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INTAKE_DIR = ROOT / "governance" / "result_family_intakes"
REGISTRY_PATH = ROOT / "governance" / "pre_route_candidates" / "OPENAI_TEN_PROOFS_WP01_INTAKE.json"
INTAKE_SCHEMA_PATH = ROOT / "schemas" / "openai_ten_proofs_result_family_intake.schema.json"
REGISTRY_SCHEMA_PATH = ROOT / "schemas" / "openai_ten_proofs_cert_intake_registry.schema.json"

EXPECTED = {
    "OTP-F-EHRHART": {
        "intake_id": "MC-OTP-INTAKE-F-EHRHART",
        "path": "governance/result_family_intakes/OTP-F-EHRHART.json",
        "packet_path": "work_packages/OPENAI_TEN_PROOFS_WP00/result_family_handoffs/OTP-F-EHRHART.json",
        "packet_digest": "4653985d4980113514266c3c421804437bacb019",
        "semantic_path": "sources/OPENAI-TEN-PROOFS-001/semantic_audits/OTP-F-EHRHART.json",
        "semantic_digest": "a3dc4de4c38a80b7aec1fae6506b08e14d2e58bb",
        "route_id": "MC-ROUTE-OTP-F-EHRHART",
    },
    "OTP-J1-COMPACTNESS": {
        "intake_id": "MC-OTP-INTAKE-J1-COMPACTNESS",
        "path": "governance/result_family_intakes/OTP-J1-COMPACTNESS.json",
        "packet_path": "work_packages/OPENAI_TEN_PROOFS_WP00/result_family_handoffs/OTP-J1-COMPACTNESS.json",
        "packet_digest": "2d9c6e555a03b71eb33c476321e7f2d311ed168f",
        "semantic_path": "sources/OPENAI-TEN-PROOFS-001/semantic_audits/OTP-J1-COMPACTNESS.json",
        "semantic_digest": "659396358d0d999c00011645f72602f30ccf6b0e",
        "route_id": "MC-ROUTE-OTP-J1-COMPACTNESS",
    },
    "OTP-J2-TWO-DEGENERATE": {
        "intake_id": "MC-OTP-INTAKE-J2-TWO-DEGENERATE",
        "path": "governance/result_family_intakes/OTP-J2-TWO-DEGENERATE.json",
        "packet_path": "work_packages/OPENAI_TEN_PROOFS_WP00/result_family_handoffs/OTP-J2-TWO-DEGENERATE.json",
        "packet_digest": "0d226492bf13e13bc1a437be01104db3d4c96f79",
        "semantic_path": "sources/OPENAI-TEN-PROOFS-001/semantic_audits/OTP-J2-TWO-DEGENERATE.json",
        "semantic_digest": "7bd168c46921f64364b20021b6315d68f0fde7d0",
        "route_id": "MC-ROUTE-OTP-J2-TWO-DEGENERATE",
    },
}
EXPECTED_FAMILIES = tuple(EXPECTED)
EXPECTED_BLOCKED = ["OTP-C-PERMANENT", "OTP-H-GAPCVP"]

INTAKE_KEYS = {
    "schema_version", "record_type", "intake_id", "candidate_id", "result_family",
    "intake_status", "authority", "gates", "target_scope", "certification_state",
    "activation", "route_controls", "claim_boundary",
}
AUTHORITY_KEYS = {
    "solve_handoff_merge", "solve_reviewed_head", "solve_review", "producer_packet",
    "forge_semantic_merge", "semantic_record", "cert_pre_route_merge", "official_subject",
}
REVIEW_KEYS = {"review_id", "reviewer", "state", "submitted_at"}
ARTIFACT_KEYS = {"repository", "commit_sha", "path", "digest_algorithm", "digest"}
SUBJECT_KEYS = {"repository", "commit", "tree", "archive_sha256"}
GATE_KEYS = {"kernel_replay", "source_semantic", "nonvacuity", "aggregate_import_required"}
TARGET_KEYS = {"source_theorem", "normalized_statement", "lean_theorems", "nonvacuity_witnesses", "scope_exclusions"}
CERT_STATE_KEYS = {
    "requested_route_id", "certification_route_registry_entry", "cert_output",
    "may_design_work_package_after_activation", "may_adjudicate",
    "mathematical_target_proved", "may_promote_claim",
}
ACTIVATION_KEYS = {"condition", "head_change_requires_reapproval", "effect"}
INTAKE_ROUTE_KEYS = {
    "result_family_only", "may_create_aggregate_intake", "may_create_aggregate_route",
    "may_imply_certification", "may_imply_proof",
}
REGISTRY_KEYS = {
    "schema_version", "record_id", "candidate_id", "state", "tracker", "authority",
    "gate_state", "intakes", "blocked_repair_lanes", "aggregate_integration",
    "cert_state", "activation", "route_controls", "supersedes_state_of", "claim_boundary",
}
REGISTRY_AUTHORITY_KEYS = {
    "solve_handoff_merge", "solve_reviewed_head", "solve_review_id",
    "forge_semantic_merge", "cert_pre_route_merge",
}
REGISTRY_GATE_KEYS = {
    "kernel_replay_clear_count", "semantic_clear_count", "result_family_count",
    "clear_families", "solve_packet_count",
}
INTAKE_REF_KEYS = {
    "result_family", "intake_id", "path", "digest_algorithm", "digest",
    "producer_packet_digest", "semantic_record_digest",
}
AGGREGATE_KEYS = {
    "state", "failure", "reopens_family_replay", "reopens_semantic_gates", "creates_cert_route",
}
REGISTRY_CERT_KEYS = {
    "intake_candidate_count", "registered_route_count", "adjudication_count",
    "cert_output_count", "mathematical_target_proved_count",
}
REGISTRY_ROUTE_KEYS = {
    "global_certification_route_registry_modified", "aggregate_intake",
    "aggregate_route_prohibited", "result_family_granularity", "may_adjudicate",
    "may_promote_claim",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload,
        usedforsecurity=False,
    ).hexdigest()


def closed_object(value: Any, expected_keys: set[str], label: str, errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{label}: expected object")
        return {}
    actual = set(value)
    for missing in sorted(expected_keys - actual):
        errors.append(f"{label}: missing field {missing}")
    for extra in sorted(actual - expected_keys):
        errors.append(f"{label}: unexpected field {extra}")
    return value


def string_list(value: Any, label: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list) or not value:
        errors.append(f"{label}: expected nonempty list")
        return []
    if not all(isinstance(item, str) and item for item in value):
        errors.append(f"{label}: entries must be nonempty strings")
        return []
    if len(value) != len(set(value)):
        errors.append(f"{label}: duplicate entries")
    return value


def intake_shape_errors(intake: Any, label: str) -> list[str]:
    errors: list[str] = []
    intake = closed_object(intake, INTAKE_KEYS, label, errors)
    authority = closed_object(intake.get("authority"), AUTHORITY_KEYS, f"{label}.authority", errors)
    closed_object(authority.get("solve_review"), REVIEW_KEYS, f"{label}.authority.solve_review", errors)
    closed_object(authority.get("producer_packet"), ARTIFACT_KEYS, f"{label}.authority.producer_packet", errors)
    closed_object(authority.get("semantic_record"), ARTIFACT_KEYS, f"{label}.authority.semantic_record", errors)
    closed_object(authority.get("official_subject"), SUBJECT_KEYS, f"{label}.authority.official_subject", errors)
    closed_object(intake.get("gates"), GATE_KEYS, f"{label}.gates", errors)
    target = closed_object(intake.get("target_scope"), TARGET_KEYS, f"{label}.target_scope", errors)
    string_list(target.get("lean_theorems"), f"{label}.target_scope.lean_theorems", errors)
    string_list(target.get("nonvacuity_witnesses"), f"{label}.target_scope.nonvacuity_witnesses", errors)
    string_list(target.get("scope_exclusions"), f"{label}.target_scope.scope_exclusions", errors)
    if not isinstance(target.get("source_theorem"), str) or len(target.get("source_theorem", "")) < 20:
        errors.append(f"{label}.target_scope.source_theorem: statement is too short")
    if not isinstance(target.get("normalized_statement"), str) or len(target.get("normalized_statement", "")) < 100:
        errors.append(f"{label}.target_scope.normalized_statement: statement is too short")
    closed_object(intake.get("certification_state"), CERT_STATE_KEYS, f"{label}.certification_state", errors)
    closed_object(intake.get("activation"), ACTIVATION_KEYS, f"{label}.activation", errors)
    closed_object(intake.get("route_controls"), INTAKE_ROUTE_KEYS, f"{label}.route_controls", errors)
    if not isinstance(intake.get("claim_boundary"), str) or len(intake.get("claim_boundary", "")) < 180:
        errors.append(f"{label}.claim_boundary: boundary is too short")
    return errors


def registry_shape_errors(registry: Any, label: str) -> list[str]:
    errors: list[str] = []
    registry = closed_object(registry, REGISTRY_KEYS, label, errors)
    closed_object(registry.get("authority"), REGISTRY_AUTHORITY_KEYS, f"{label}.authority", errors)
    closed_object(registry.get("gate_state"), REGISTRY_GATE_KEYS, f"{label}.gate_state", errors)
    refs = registry.get("intakes")
    if not isinstance(refs, list) or len(refs) != 3:
        errors.append(f"{label}.intakes: expected exactly three records")
        refs = []
    for index, item in enumerate(refs):
        closed_object(item, INTAKE_REF_KEYS, f"{label}.intakes[{index}]", errors)
    string_list(registry.get("blocked_repair_lanes"), f"{label}.blocked_repair_lanes", errors)
    closed_object(registry.get("aggregate_integration"), AGGREGATE_KEYS, f"{label}.aggregate_integration", errors)
    closed_object(registry.get("cert_state"), REGISTRY_CERT_KEYS, f"{label}.cert_state", errors)
    closed_object(registry.get("activation"), ACTIVATION_KEYS, f"{label}.activation", errors)
    closed_object(registry.get("route_controls"), REGISTRY_ROUTE_KEYS, f"{label}.route_controls", errors)
    if not isinstance(registry.get("claim_boundary"), str) or len(registry.get("claim_boundary", "")) < 180:
        errors.append(f"{label}.claim_boundary: boundary is too short")
    return errors


def validation_errors(
    registry: dict[str, Any] | None = None,
    intakes: dict[str, dict[str, Any]] | None = None,
    intake_blobs: dict[str, str] | None = None,
) -> list[str]:
    errors: list[str] = []
    if registry is None:
        registry = load_json(REGISTRY_PATH)
    if intakes is None:
        intakes = {path.stem: load_json(path) for path in sorted(INTAKE_DIR.glob("*.json"))}
    if intake_blobs is None:
        intake_blobs = {path.stem: git_blob_sha1(path) for path in sorted(INTAKE_DIR.glob("*.json"))}

    for schema_path in (INTAKE_SCHEMA_PATH, REGISTRY_SCHEMA_PATH):
        schema = load_json(schema_path)
        if schema.get("additionalProperties") is not False:
            errors.append(f"{schema_path}: top-level schema must remain closed")
    errors.extend(registry_shape_errors(registry, str(REGISTRY_PATH)))

    actual = set(intakes)
    expected = set(EXPECTED_FAMILIES)
    for missing in sorted(expected - actual):
        errors.append(f"OTP-CERT-INTAKE-001: missing intake {missing}")
    for unknown in sorted(actual - expected):
        errors.append(f"OTP-CERT-INTAKE-001: unexpected intake {unknown}")

    seen_ids: list[str] = []
    seen_routes: list[str] = []
    for family, expected_record in EXPECTED.items():
        intake = intakes.get(family)
        if not isinstance(intake, dict):
            continue
        label = f"OTP-CERT-INTAKE-001: {family}"
        errors.extend(intake_shape_errors(intake, label))
        if intake.get("schema_version") != "1.0.0":
            errors.append(f"{label}: schema version drift")
        if intake.get("record_type") != "openai_ten_proofs_result_family_intake":
            errors.append(f"{label}: record type drift")
        if intake.get("candidate_id") != "OPENAI-TEN-PROOFS-001":
            errors.append(f"{label}: candidate identity drift")
        if intake.get("intake_status") != "accepted_after_protected_mathcert_merge":
            errors.append(f"{label}: intake activation status drift")
        if intake.get("result_family") != family:
            errors.append(f"{label}: result-family identity drift")
        if intake.get("intake_id") != expected_record["intake_id"]:
            errors.append(f"{label}: intake identity drift")

        authority = intake.get("authority", {})
        if authority.get("solve_handoff_merge") != "443daf537dc7e4ee34ab43aeb01508d9177816ab":
            errors.append(f"{label}: Solve handoff merge drift")
        if authority.get("solve_reviewed_head") != "675706f5c0fe6fcbbcdf2998186fa10577fe05f5":
            errors.append(f"{label}: reviewed Solve head drift")
        if authority.get("forge_semantic_merge") != "cb0a203c36a9ef33270d62ab369df7bc27d3b242":
            errors.append(f"{label}: Forge semantic merge drift")
        if authority.get("cert_pre_route_merge") != "993286f982c2fccc144475cdbf9a35d0c7f5f24c":
            errors.append(f"{label}: Cert pre-route merge drift")
        review = authority.get("solve_review", {})
        if review != {
            "review_id": 4835520166,
            "reviewer": "jimsteeg",
            "state": "APPROVED",
            "submitted_at": "2026-08-01T19:14:38Z",
        }:
            errors.append(f"{label}: Solve review identity drift")
        subject = authority.get("official_subject", {})
        if subject != {
            "repository": "openai/ten-proofs",
            "commit": "e62211d28e3a9131950c89caa6542cfe5eff3bca",
            "tree": "2f8e7ac5ae7f157b6b1de636c2c343b1c7a7e365",
            "archive_sha256": "3022e62ffbed8f5f74d232034a703dc645e6b301879dff1e87df72979914294f",
        }:
            errors.append(f"{label}: official subject identity drift")

        packet = authority.get("producer_packet", {})
        if packet.get("repository") != "grandchallenge/MATHSOLVE":
            errors.append(f"{label}: producer repository drift")
        if packet.get("commit_sha") != "443daf537dc7e4ee34ab43aeb01508d9177816ab":
            errors.append(f"{label}: producer merge drift")
        if packet.get("path") != expected_record["packet_path"]:
            errors.append(f"{label}: producer packet path drift")
        if packet.get("digest_algorithm") != "git_blob_sha1":
            errors.append(f"{label}: producer digest algorithm drift")
        if packet.get("digest") != expected_record["packet_digest"]:
            errors.append(f"{label}: producer packet digest drift")

        semantic = authority.get("semantic_record", {})
        if semantic.get("repository") != "grandchallenge/MATHFORGE":
            errors.append(f"{label}: semantic repository drift")
        if semantic.get("commit_sha") != "cb0a203c36a9ef33270d62ab369df7bc27d3b242":
            errors.append(f"{label}: semantic merge drift")
        if semantic.get("path") != expected_record["semantic_path"]:
            errors.append(f"{label}: semantic record path drift")
        if semantic.get("digest_algorithm") != "git_blob_sha1":
            errors.append(f"{label}: semantic digest algorithm drift")
        if semantic.get("digest") != expected_record["semantic_digest"]:
            errors.append(f"{label}: semantic record digest drift")

        state = intake.get("certification_state", {})
        if state.get("requested_route_id") != expected_record["route_id"]:
            errors.append(f"{label}: requested route identity drift")
        if state.get("certification_route_registry_entry") is not None:
            errors.append(f"{label}: certification route was registered prematurely")
        if state.get("cert_output") is not None:
            errors.append(f"{label}: Cert output was injected")
        if state.get("may_design_work_package_after_activation") is not True:
            errors.append(f"{label}: post-activation work-package design was disabled")
        if state.get("may_adjudicate") is not False:
            errors.append(f"{label}: adjudication was enabled")
        if state.get("mathematical_target_proved") is not False:
            errors.append(f"{label}: target was marked proved")
        if state.get("may_promote_claim") is not False:
            errors.append(f"{label}: claim promotion was enabled")

        activation = intake.get("activation", {})
        if activation != {
            "condition": "exact-head CI, non-author APPROVED review, and protected MATHCERT merge",
            "head_change_requires_reapproval": True,
            "effect": "intake_accepted_no_route_no_adjudication",
        }:
            errors.append(f"{label}: activation contract drift")
        controls = intake.get("route_controls", {})
        if controls.get("result_family_only") is not True:
            errors.append(f"{label}: result-family granularity removed")
        for field in (
            "may_create_aggregate_intake", "may_create_aggregate_route",
            "may_imply_certification", "may_imply_proof",
        ):
            if controls.get(field) is not False:
                errors.append(f"{label}: prohibited control enabled: {field}")
        gates = intake.get("gates", {})
        for field in ("kernel_replay", "source_semantic", "nonvacuity"):
            if gates.get(field) != "clear":
                errors.append(f"{label}: required gate is not clear: {field}")
        if gates.get("aggregate_import_required") is not False:
            errors.append(f"{label}: aggregate All.lean import was made a family prerequisite")
        seen_ids.append(str(intake.get("intake_id", "")))
        seen_routes.append(str(state.get("requested_route_id", "")))

    for duplicate in sorted({value for value in seen_ids if seen_ids.count(value) > 1}):
        errors.append(f"OTP-CERT-INTAKE-001: duplicate intake identity {duplicate}")
    for duplicate in sorted({value for value in seen_routes if seen_routes.count(value) > 1}):
        errors.append(f"OTP-CERT-INTAKE-001: duplicate requested route identity {duplicate}")

    if registry.get("schema_version") != "1.0.0":
        errors.append("OTP-CERT-INTAKE-001: registry schema version drift")
    if registry.get("record_id") != "MC-OTP-CERT-INTAKE-001":
        errors.append("OTP-CERT-INTAKE-001: registry identity drift")
    if registry.get("candidate_id") != "OPENAI-TEN-PROOFS-001":
        errors.append("OTP-CERT-INTAKE-001: registry candidate identity drift")
    if registry.get("state") != "three_intake_candidates_pending_cert_activation":
        errors.append("OTP-CERT-INTAKE-001: registry branch-state drift")
    if registry.get("tracker") != "https://github.com/grandchallenge/MATHCERT/issues/46":
        errors.append("OTP-CERT-INTAKE-001: tracker drift")
    if registry.get("supersedes_state_of") != "governance/pre_route_candidates/OPENAI_TEN_PROOFS_WP00_SYNC.json":
        errors.append("OTP-CERT-INTAKE-001: supersession chain drift")
    if registry.get("authority") != {
        "solve_handoff_merge": "443daf537dc7e4ee34ab43aeb01508d9177816ab",
        "solve_reviewed_head": "675706f5c0fe6fcbbcdf2998186fa10577fe05f5",
        "solve_review_id": 4835520166,
        "forge_semantic_merge": "cb0a203c36a9ef33270d62ab369df7bc27d3b242",
        "cert_pre_route_merge": "993286f982c2fccc144475cdbf9a35d0c7f5f24c",
    }:
        errors.append("OTP-CERT-INTAKE-001: registry authority drift")

    refs = registry.get("intakes", [])
    if not isinstance(refs, list):
        refs = []
    indexed = [str(item.get("result_family", "")) for item in refs if isinstance(item, dict)]
    if indexed != list(EXPECTED_FAMILIES):
        errors.append("OTP-CERT-INTAKE-001: intake registry order or membership drift")
    for item in refs:
        if not isinstance(item, dict):
            continue
        family = str(item.get("result_family", ""))
        expected_record = EXPECTED.get(family)
        if expected_record is None:
            continue
        if item.get("intake_id") != expected_record["intake_id"]:
            errors.append(f"OTP-CERT-INTAKE-001: registry intake ID drift for {family}")
        if item.get("path") != expected_record["path"]:
            errors.append(f"OTP-CERT-INTAKE-001: registry path drift for {family}")
        if item.get("digest_algorithm") != "git_blob_sha1":
            errors.append(f"OTP-CERT-INTAKE-001: registry digest algorithm drift for {family}")
        if item.get("digest") != intake_blobs.get(family):
            errors.append(f"OTP-CERT-INTAKE-001: local intake Git blob drift for {family}")
        if item.get("producer_packet_digest") != expected_record["packet_digest"]:
            errors.append(f"OTP-CERT-INTAKE-001: registry producer digest drift for {family}")
        if item.get("semantic_record_digest") != expected_record["semantic_digest"]:
            errors.append(f"OTP-CERT-INTAKE-001: registry semantic digest drift for {family}")

    gate = registry.get("gate_state", {})
    if gate.get("kernel_replay_clear_count") != 12:
        errors.append("OTP-CERT-INTAKE-001: kernel replay count drift")
    if gate.get("semantic_clear_count") != 3:
        errors.append("OTP-CERT-INTAKE-001: semantic clear count must remain exactly 3")
    if gate.get("result_family_count") != 12:
        errors.append("OTP-CERT-INTAKE-001: result-family denominator drift")
    if gate.get("clear_families") != list(EXPECTED_FAMILIES):
        errors.append("OTP-CERT-INTAKE-001: clear-family set drift")
    if gate.get("solve_packet_count") != 3:
        errors.append("OTP-CERT-INTAKE-001: Solve packet count drift")
    if registry.get("blocked_repair_lanes") != EXPECTED_BLOCKED:
        errors.append("OTP-CERT-INTAKE-001: blocked repair lanes drift")

    aggregate = registry.get("aggregate_integration", {})
    if aggregate.get("state") != "failed_separate_obligation":
        errors.append("OTP-CERT-INTAKE-001: All.lean state drift")
    if aggregate.get("failure") != "All.lean namespace collision on replicate_to_periodic_packing":
        errors.append("OTP-CERT-INTAKE-001: All.lean failure identity drift")
    for field in ("reopens_family_replay", "reopens_semantic_gates", "creates_cert_route"):
        if aggregate.get(field) is not False:
            errors.append(f"OTP-CERT-INTAKE-001: All.lean debt changed protected state: {field}")

    cert = registry.get("cert_state", {})
    if cert.get("intake_candidate_count") != 3:
        errors.append("OTP-CERT-INTAKE-001: intake candidate count drift")
    for field in (
        "registered_route_count", "adjudication_count", "cert_output_count",
        "mathematical_target_proved_count",
    ):
        if cert.get(field) != 0:
            errors.append(f"OTP-CERT-INTAKE-001: Cert state inflated: {field}")

    if registry.get("activation") != {
        "condition": "exact-head CI, non-author APPROVED review, and protected MATHCERT merge",
        "head_change_requires_reapproval": True,
        "effect": "three_independent_intakes_accepted_no_routes_no_adjudication",
    }:
        errors.append("OTP-CERT-INTAKE-001: registry activation contract drift")
    controls = registry.get("route_controls", {})
    if controls.get("global_certification_route_registry_modified") is not False:
        errors.append("OTP-CERT-INTAKE-001: global certification route registry was marked modified")
    if controls.get("aggregate_intake") is not None:
        errors.append("OTP-CERT-INTAKE-001: aggregate intake injected")
    if controls.get("aggregate_route_prohibited") is not True:
        errors.append("OTP-CERT-INTAKE-001: aggregate route prohibition removed")
    if controls.get("result_family_granularity") is not True:
        errors.append("OTP-CERT-INTAKE-001: result-family granularity removed")
    if controls.get("may_adjudicate") is not False:
        errors.append("OTP-CERT-INTAKE-001: registry adjudication enabled")
    if controls.get("may_promote_claim") is not False:
        errors.append("OTP-CERT-INTAKE-001: registry claim promotion enabled")
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"OpenAI ten-proofs Cert intake validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print(
        "validated three independent content-addressed Cert intake candidates, exact Solve and Forge authority, "
        "zero routes, zero adjudications, zero outputs, blocked repair lanes, and aggregate prohibition"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
