#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "governance/result_family_adjudication_contracts/OTP-C-PERMANENT.json"
REGISTRY = ROOT / "governance/adjudication_design/OPENAI_TEN_PROOFS_PERMANENT_ADJUDICATION_CONTRACT.json"
ROUTES = ROOT / "governance/certification_routes.json"
CONTRACT_SCHEMA = ROOT / "schemas/openai_ten_proofs_permanent_adjudication_contract.schema.json"
REGISTRY_SCHEMA = ROOT / "schemas/openai_ten_proofs_permanent_adjudication_contract_registry.schema.json"

ROUTE_ID = "MC-ROUTE-OTP-C-PERMANENT-FORMULA"
CONTRACT_ID = "MC-OTP-ADJUDICATION-CONTRACT-C-PERMANENT-FORMULA"
EXPECTED_ROUTES_BLOB = "4b7f98414958999c8404e30a4a7c0a2a104578da"
EXPECTED_TARGETS = [
    "PermanentFormulaLowerBound.permanent_divisionFree_formula_logarithmic_lower_bound",
    "PermanentFormulaLowerBound.permanent_rational_formula_logarithmic_lower_bound",
]
EXPECTED_AUTHORITY = {
    "registration_reviewed_head": "7c647c042c465fa760725db70c7ba85048480449",
    "registration_merge": "48a0ea7929af09785b0b467dcf54651cbea355da",
    "registration_review_id": 4942637852,
    "registration_reviewer": "jimsteeg",
    "registration_disposition_comment": 5300406802,
    "registered_route_registry_blob": EXPECTED_ROUTES_BLOB,
    "forge_semantic_merge": "60f6e06c957139447bf5943eed731941b22ac608",
    "semantic_record_blob": "3e04bd16bd8a91eaf9b6702de89fcdcc72f61099",
    "nonvacuity_witness_blob": "e756c8476bac1795f3fb8ca0b7235d3a4a5c59ea",
    "solve_handoff_merge": "90f8a8544e546a603b34c9b27b2d6a4a68e06de8",
    "producer_packet_blob": "a993c530880021930a2b468e76235b91122ca854",
    "cert_intake_merge": "59e678a5692c873cb7b12b8913231bf520571f51",
    "cert_intake_blob": "80a9cf59ac4bad7cc08185e80b0d9ffe27b855e6",
    "cert_work_package_merge": "4b5d9e81afea50b5b51b4e390065f52275c886cd",
    "cert_work_package_blob": "f3000340c2699ec819acbcd223c1ee4c63af1cc8",
    "cert_replay_evidence_merge": "7f42194bfcfb5b28f2bdb1f5b3203650a6b5ff15",
    "cert_replay_evidence_blob": "7b75a323b6d840730932bf90984f498b7d360cda",
    "evidence_manifest_blob": "cbc185bd0cd182fddd3127d8373ae7a74f6389dd",
    "evidence_manifest_sha256": "351ab107342d2fe72220098ae6e5dc600653e9b181119c99805182270559f969",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(f"blob {len(payload)}\0".encode("ascii") + payload, usedforsecurity=False).hexdigest()


def open_object_paths(schema: Any) -> list[str]:
    found: list[str] = []
    def walk(value: Any, path: str = "") -> None:
        if isinstance(value, dict):
            if value.get("type") == "object" and value.get("additionalProperties") is not False:
                found.append(path or "/")
            for key, child in value.items():
                walk(child, f"{path}/{key}")
        elif isinstance(value, list):
            for i, child in enumerate(value):
                walk(child, f"{path}/{i}")
    walk(schema)
    return found


def validation_errors(
    contract: dict[str, Any] | None = None,
    registry: dict[str, Any] | None = None,
    routes: dict[str, Any] | None = None,
    routes_blob: str | None = None,
) -> list[str]:
    contract = load(CONTRACT) if contract is None else contract
    registry = load(REGISTRY) if registry is None else registry
    routes = load(ROUTES) if routes is None else routes
    contract_schema = load(CONTRACT_SCHEMA)
    registry_schema = load(REGISTRY_SCHEMA)
    errors: list[str] = []

    for label, schema in (("contract", contract_schema), ("registry", registry_schema)):
        paths = open_object_paths(schema)
        if paths:
            errors.append(f"{label} schema contains open object: {paths[0]}")
    for error in Draft202012Validator(contract_schema).iter_errors(contract):
        errors.append(f"contract schema: {'/'.join(map(str, error.path))}: {error.message}")
    for error in Draft202012Validator(registry_schema).iter_errors(registry):
        errors.append(f"registry schema: {'/'.join(map(str, error.path))}: {error.message}")

    if (git_blob_sha1(ROUTES) if routes_blob is None else routes_blob) != EXPECTED_ROUTES_BLOB:
        errors.append("live route registry changed during design-only operation")
    if contract.get("authority") != EXPECTED_AUTHORITY:
        errors.append("protected authority chain drift")
    if contract.get("contract_id") != CONTRACT_ID or contract.get("contract_state") != "design_only":
        errors.append("contract identity/state drift")
    route_scope = contract.get("route_scope", {})
    if route_scope.get("registered_route_state") != "submitted":
        errors.append("contract attempts route-state promotion")
    if route_scope.get("target_claim_ids") != EXPECTED_TARGETS:
        errors.append("contract target scope drift")
    projection = route_scope.get("source_projection", {})
    expected_projection = {
        "coefficient_field": "complex",
        "dimension_threshold": 32,
        "log_base": 2,
        "division_free_variable_leaf_constant": 128,
        "rational_variable_leaf_constant": 192,
        "formula_target_count": 2,
        "circuit_target_count": 0,
    }
    if projection != expected_projection:
        errors.append("source projection drift")

    dispositions = contract.get("decision_contract", {}).get("admissible_dispositions")
    if dispositions != ["adjudication_clear_encoded_targets_only", "adjudication_not_clear", "defer_insufficient_evidence"]:
        errors.append("admissible disposition drift")
    state = contract.get("state", {})
    expected_state = {
        "may_adjudicate": False,
        "adjudication": None,
        "cert_output": None,
        "mathematical_target_proved": False,
        "may_issue_output": False,
        "may_promote_claim": False,
        "aggregate_adjudication": False,
    }
    if state != expected_state:
        errors.append("design-only state inflation")
    limitations = contract.get("preserved_limitations", {})
    if limitations != {
        "circuit_targets_in_scope": False,
        "gate_bounds_in_scope": False,
        "total_size_consequences_in_scope": False,
        "historical_pdf_byte_equivalence": "not_established",
        "aggregate_openai_ten_proofs_authority": False,
    }:
        errors.append("preserved limitation drift")

    contracts = registry.get("contracts", [])
    if registry.get("contract_count") != 1 or len(contracts) != 1:
        errors.append("Permanent design registry membership must be exactly one")
    if contracts and contracts[0].get("contract_id") != CONTRACT_ID:
        errors.append("registry contract identity drift")
    if registry.get("state") != {
        "may_adjudicate": False,
        "adjudication_count": 0,
        "cert_output_count": 0,
        "mathematical_target_proved_count": 0,
        "aggregate_contract_count": 0,
    }:
        errors.append("registry authority inflation")

    route_list = routes.get("routes", [])
    route = next((r for r in route_list if isinstance(r, dict) and r.get("route_id") == ROUTE_ID), None)
    if route is None:
        errors.append("registered Permanent route missing")
    else:
        if route.get("intake_status") != "submitted":
            errors.append("live Permanent route is not submitted")
        if route.get("target_claim_ids") != EXPECTED_TARGETS:
            errors.append("live Permanent route target drift")
        if route.get("cert_output") is not None:
            errors.append("live Permanent route gained Cert output")
    route_ids = [r.get("route_id") for r in route_list if isinstance(r, dict)]
    if "MC-ROUTE-OPENAI-TEN-PROOFS-001" in route_ids:
        errors.append("aggregate route inserted")
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"Permanent adjudication-contract validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print("validated one design-only Permanent formula adjudication contract; route remains submitted with zero adjudication/output/proof authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
