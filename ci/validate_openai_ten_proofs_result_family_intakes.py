#!/usr/bin/env python3
"""Validate independent OpenAI Ten Proofs MATHCERT intake records."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
INTAKE_DIR = ROOT / "governance" / "result_family_intakes"
REGISTRY_PATH = ROOT / "governance" / "pre_route_candidates" / "OPENAI_TEN_PROOFS_WP01_INTAKE.json"
LEGACY_SCHEMA_PATH = ROOT / "schemas" / "openai_ten_proofs_result_family_intake.schema.json"
PERMANENT_SCHEMA_PATH = ROOT / "schemas" / "openai_ten_proofs_permanent_result_family_intake.schema.json"
REGISTRY_SCHEMA_PATH = ROOT / "schemas" / "openai_ten_proofs_cert_intake_registry.schema.json"

EXPECTED = {
    "OTP-F-EHRHART": {
        "intake_id": "MC-OTP-INTAKE-F-EHRHART",
        "path": "governance/result_family_intakes/OTP-F-EHRHART.json",
        "packet_digest": "4653985d4980113514266c3c421804437bacb019",
        "semantic_digest": "a3dc4de4c38a80b7aec1fae6506b08e14d2e58bb",
        "route_id": "MC-ROUTE-OTP-F-EHRHART",
        "schema": "legacy",
    },
    "OTP-J1-COMPACTNESS": {
        "intake_id": "MC-OTP-INTAKE-J1-COMPACTNESS",
        "path": "governance/result_family_intakes/OTP-J1-COMPACTNESS.json",
        "packet_digest": "2d9c6e555a03b71eb33c476321e7f2d311ed168f",
        "semantic_digest": "659396358d0d999c00011645f72602f30ccf6b0e",
        "route_id": "MC-ROUTE-OTP-J1-COMPACTNESS",
        "schema": "legacy",
    },
    "OTP-J2-TWO-DEGENERATE": {
        "intake_id": "MC-OTP-INTAKE-J2-TWO-DEGENERATE",
        "path": "governance/result_family_intakes/OTP-J2-TWO-DEGENERATE.json",
        "packet_digest": "0d226492bf13e13bc1a437be01104db3d4c96f79",
        "semantic_digest": "7bd168c46921f64364b20021b6315d68f0fde7d0",
        "route_id": "MC-ROUTE-OTP-J2-TWO-DEGENERATE",
        "schema": "legacy",
    },
    "OTP-C-PERMANENT": {
        "intake_id": "MC-OTP-INTAKE-C-PERMANENT-FORMULA",
        "path": "governance/result_family_intakes/OTP-C-PERMANENT.json",
        "packet_digest": "a993c530880021930a2b468e76235b91122ca854",
        "semantic_digest": "3e04bd16bd8a91eaf9b6702de89fcdcc72f61099",
        "route_id": "MC-ROUTE-OTP-C-PERMANENT-FORMULA",
        "schema": "permanent",
    },
}
EXPECTED_FAMILIES = tuple(EXPECTED)
EXPECTED_BLOCKED = ["OTP-H-GAPCVP"]
EXPECTED_PERMANENT_UNACCEPTED = [
    "source Theorem 1.1 arithmetic-circuit complexity",
    "Theorem 1.2 internal-gate bound with constant 256",
    "Theorem 1.3 internal-gate bound with constant 384",
    "Theorems 1.2/1.3 total-leaves and total-vertices consequences",
    "historical admitted-PDF byte equivalence",
]
EXPECTED_PERMANENT_PROJECTION = {
    "formula_target_count": 2,
    "circuit_target_count": 0,
    "coefficient_field": "complex",
    "dimension_threshold": 32,
    "log_base": 2,
    "division_free_variable_leaf_constant": 128,
    "division_free_source_gate_constant": 256,
    "rational_variable_leaf_constant": 192,
    "rational_source_gate_constant": 384,
    "gate_bounds_in_intake": False,
    "total_leaves_vertices_in_intake": False,
    "historical_pdf_byte_equivalence": False,
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload,
        usedforsecurity=False,
    ).hexdigest()


def schema_errors(instance: dict[str, Any], schema: dict[str, Any], label: str) -> list[str]:
    return [
        f"{label}: {error.json_path}: {error.message}"
        for error in sorted(Draft202012Validator(schema).iter_errors(instance), key=lambda e: list(e.path))
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
        intakes = {p.stem: load_json(p) for p in sorted(INTAKE_DIR.glob("*.json"))}
    if intake_blobs is None:
        intake_blobs = {p.stem: git_blob_sha1(p) for p in sorted(INTAKE_DIR.glob("*.json"))}

    legacy_schema = load_json(LEGACY_SCHEMA_PATH)
    permanent_schema = load_json(PERMANENT_SCHEMA_PATH)
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
        schema = permanent_schema if expected_record["schema"] == "permanent" else legacy_schema
        errors.extend(schema_errors(intake, schema, label))
        if intake.get("result_family") != family:
            errors.append(f"{label}: result-family identity drift")
        if intake.get("intake_id") != expected_record["intake_id"]:
            errors.append(f"{label}: intake identity drift")
        authority = intake.get("authority", {})
        producer = authority.get("producer_packet", {})
        semantic = authority.get("semantic_record", {})
        if producer.get("digest") != expected_record["packet_digest"]:
            errors.append(f"{label}: producer packet digest drift")
        if semantic.get("digest") != expected_record["semantic_digest"]:
            errors.append(f"{label}: semantic record digest drift")
        state = intake.get("certification_state", {})
        if state.get("requested_route_id") != expected_record["route_id"]:
            errors.append(f"{label}: requested route identity drift")
        if state.get("certification_route_registry_entry") is not None:
            errors.append(f"{label}: route registered during intake")
        if state.get("cert_output") is not None:
            errors.append(f"{label}: Cert output present during intake")
        if state.get("may_adjudicate") is not False:
            errors.append(f"{label}: adjudication enabled during intake")
        if state.get("mathematical_target_proved") is not False:
            errors.append(f"{label}: proof state promoted during intake")
        if state.get("may_promote_claim") is not False:
            errors.append(f"{label}: claim promotion enabled during intake")
        controls = intake.get("route_controls", {})
        if controls.get("may_create_aggregate_intake") is not False:
            errors.append(f"{label}: aggregate intake enabled")
        if controls.get("may_create_aggregate_route") is not False:
            errors.append(f"{label}: aggregate route enabled")
        if controls.get("may_imply_certification") is not False:
            errors.append(f"{label}: certification implication enabled")
        if controls.get("may_imply_proof") is not False:
            errors.append(f"{label}: proof implication enabled")
        if family == "OTP-C-PERMANENT":
            if intake.get("target_scope", {}).get("source_projection") != EXPECTED_PERMANENT_PROJECTION:
                errors.append(f"{label}: Permanent source projection drift")
            if intake.get("target_scope", {}).get("lean_theorems") != [
                "PermanentFormulaLowerBound.permanent_divisionFree_formula_logarithmic_lower_bound",
                "PermanentFormulaLowerBound.permanent_rational_formula_logarithmic_lower_bound",
            ]:
                errors.append(f"{label}: Permanent target-set drift")
            if authority.get("solve_handoff_merge") != "90f8a8544e546a603b34c9b27b2d6a4a68e06de8":
                errors.append(f"{label}: protected Solve merge drift")
            if authority.get("forge_semantic_merge") != "60f6e06c957139447bf5943eed731941b22ac608":
                errors.append(f"{label}: protected Forge semantic merge drift")
            witness = authority.get("nonvacuity_witness", {})
            if witness.get("digest") != "e756c8476bac1795f3fb8ca0b7235d3a4a5c59ea":
                errors.append(f"{label}: nonvacuity witness drift")
            for field in ("may_include_circuit_target", "may_include_gate_bounds", "may_include_total_size_consequences"):
                if controls.get(field) is not False:
                    errors.append(f"{label}: Permanent scope inflation enabled: {field}")
        seen_ids.append(str(intake.get("intake_id", "")))
        seen_routes.append(str(state.get("requested_route_id", "")))

    for duplicate in sorted({x for x in seen_ids if seen_ids.count(x) > 1}):
        errors.append(f"OTP-CERT-INTAKE-001: duplicate intake identity {duplicate}")
    for duplicate in sorted({x for x in seen_routes if seen_routes.count(x) > 1}):
        errors.append(f"OTP-CERT-INTAKE-001: duplicate requested route identity {duplicate}")

    refs = registry.get("intakes", [])
    indexed = [str(x.get("result_family", "")) for x in refs if isinstance(x, dict)]
    if indexed != list(EXPECTED_FAMILIES):
        errors.append("OTP-CERT-INTAKE-001: registry intake order or membership drift")
    for item in refs if isinstance(refs, list) else []:
        if not isinstance(item, dict):
            continue
        family = str(item.get("result_family", ""))
        expected_record = EXPECTED.get(family)
        if expected_record is None:
            continue
        if item.get("intake_id") != expected_record["intake_id"]:
            errors.append(f"OTP-CERT-INTAKE-001: registry intake identity drift for {family}")
        if item.get("path") != expected_record["path"]:
            errors.append(f"OTP-CERT-INTAKE-001: registry path drift for {family}")
        if item.get("producer_packet_digest") != expected_record["packet_digest"]:
            errors.append(f"OTP-CERT-INTAKE-001: registry producer digest drift for {family}")
        if item.get("semantic_record_digest") != expected_record["semantic_digest"]:
            errors.append(f"OTP-CERT-INTAKE-001: registry semantic digest drift for {family}")
        if item.get("digest") != intake_blobs.get(family):
            errors.append(f"OTP-CERT-INTAKE-001: intake Git blob drift for {family}")

    gate = registry.get("gate_state", {})
    if gate.get("semantic_clear_count") != 4 or gate.get("solve_packet_count") != 4:
        errors.append("OTP-CERT-INTAKE-001: four-family clear/packet count drift")
    if gate.get("clear_families") != list(EXPECTED_FAMILIES):
        errors.append("OTP-CERT-INTAKE-001: clear-family set drift")
    if gate.get("permanent_scope") != "two encoded variable-leaf targets only":
        errors.append("OTP-CERT-INTAKE-001: Permanent scope drift")
    if registry.get("blocked_repair_lanes") != EXPECTED_BLOCKED:
        errors.append("OTP-CERT-INTAKE-001: blocked repair lanes drift")
    if registry.get("permanent_unaccepted_successors") != EXPECTED_PERMANENT_UNACCEPTED:
        errors.append("OTP-CERT-INTAKE-001: Permanent unaccepted-successor boundary drift")

    aggregate = registry.get("aggregate_integration", {})
    for field in ("reopens_family_replay", "reopens_semantic_gates", "creates_cert_route"):
        if aggregate.get(field) is not False:
            errors.append(f"OTP-CERT-INTAKE-001: aggregate debt inflated authority: {field}")
    cert = registry.get("cert_state", {})
    if cert.get("intake_candidate_count") != 4:
        errors.append("OTP-CERT-INTAKE-001: intake candidate count drift")
    for field in ("registered_route_count", "adjudication_count", "cert_output_count", "mathematical_target_proved_count"):
        if cert.get(field) != 0:
            errors.append(f"OTP-CERT-INTAKE-001: Cert state inflated: {field}")
    controls = registry.get("route_controls", {})
    if controls.get("global_certification_route_registry_modified") is not False:
        errors.append("OTP-CERT-INTAKE-001: global route registry modified")
    if controls.get("aggregate_intake") is not None:
        errors.append("OTP-CERT-INTAKE-001: aggregate intake injected")
    if controls.get("aggregate_route_prohibited") is not True:
        errors.append("OTP-CERT-INTAKE-001: aggregate route prohibition removed")
    if controls.get("result_family_granularity") is not True or controls.get("permanent_subset_only") is not True:
        errors.append("OTP-CERT-INTAKE-001: result-family/subset granularity removed")
    if controls.get("may_adjudicate") is not False or controls.get("may_promote_claim") is not False:
        errors.append("OTP-CERT-INTAKE-001: adjudication or promotion enabled")
    if controls.get("may_include_permanent_circuit_or_omitted_formula_conclusions") is not False:
        errors.append("OTP-CERT-INTAKE-001: Permanent omitted conclusions inserted")
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"MATHCERT result-family intake validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print("validated four independent MATHCERT intake candidates, zero routes/adjudications/outputs, and bounded Permanent variable-leaf scope")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
