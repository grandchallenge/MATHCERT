#!/usr/bin/env python3
"""Validate independent OpenAI ten-proofs MATHCERT intake records."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

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


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload,
        usedforsecurity=False,
    ).hexdigest()


def schema_errors(instance: dict[str, Any], schema: dict[str, Any], label: str) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [
        f"{label}: {error.json_path}: {error.message}"
        for error in sorted(validator.iter_errors(instance), key=lambda item: list(item.path))
    ]


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

    intake_schema = load_json(INTAKE_SCHEMA_PATH)
    registry_schema = load_json(REGISTRY_SCHEMA_PATH)
    errors.extend(schema_errors(registry, registry_schema, str(REGISTRY_PATH)))

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
        errors.extend(schema_errors(intake, intake_schema, label))
        if intake.get("result_family") != family:
            errors.append(f"{label}: result-family identity drift")
        if intake.get("intake_id") != expected_record["intake_id"]:
            errors.append(f"{label}: intake identity drift")

        authority = intake.get("authority", {})
        packet = authority.get("producer_packet", {})
        if packet.get("repository") != "grandchallenge/MATHSOLVE":
            errors.append(f"{label}: producer repository drift")
        if packet.get("commit_sha") != "443daf537dc7e4ee34ab43aeb01508d9177816ab":
            errors.append(f"{label}: producer merge drift")
        if packet.get("path") != expected_record["packet_path"]:
            errors.append(f"{label}: producer packet path drift")
        if packet.get("digest") != expected_record["packet_digest"]:
            errors.append(f"{label}: producer packet digest drift")

        semantic = authority.get("semantic_record", {})
        if semantic.get("repository") != "grandchallenge/MATHFORGE":
            errors.append(f"{label}: semantic repository drift")
        if semantic.get("commit_sha") != "cb0a203c36a9ef33270d62ab369df7bc27d3b242":
            errors.append(f"{label}: semantic merge drift")
        if semantic.get("path") != expected_record["semantic_path"]:
            errors.append(f"{label}: semantic record path drift")
        if semantic.get("digest") != expected_record["semantic_digest"]:
            errors.append(f"{label}: semantic record digest drift")

        state = intake.get("certification_state", {})
        if state.get("requested_route_id") != expected_record["route_id"]:
            errors.append(f"{label}: requested route identity drift")
        if state.get("certification_route_registry_entry") is not None:
            errors.append(f"{label}: certification route was registered prematurely")
        if state.get("cert_output") is not None:
            errors.append(f"{label}: Cert output was injected")
        if state.get("may_adjudicate") is not False:
            errors.append(f"{label}: adjudication was enabled")
        if state.get("mathematical_target_proved") is not False:
            errors.append(f"{label}: target was marked proved")
        if state.get("may_promote_claim") is not False:
            errors.append(f"{label}: claim promotion was enabled")

        controls = intake.get("route_controls", {})
        if controls.get("result_family_only") is not True:
            errors.append(f"{label}: result-family granularity removed")
        for field in (
            "may_create_aggregate_intake",
            "may_create_aggregate_route",
            "may_imply_certification",
            "may_imply_proof",
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
    for field in ("reopens_family_replay", "reopens_semantic_gates", "creates_cert_route"):
        if aggregate.get(field) is not False:
            errors.append(f"OTP-CERT-INTAKE-001: All.lean debt changed protected state: {field}")

    cert = registry.get("cert_state", {})
    if cert.get("intake_candidate_count") != 3:
        errors.append("OTP-CERT-INTAKE-001: intake candidate count drift")
    for field in (
        "registered_route_count",
        "adjudication_count",
        "cert_output_count",
        "mathematical_target_proved_count",
    ):
        if cert.get(field) != 0:
            errors.append(f"OTP-CERT-INTAKE-001: Cert state inflated: {field}")

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
