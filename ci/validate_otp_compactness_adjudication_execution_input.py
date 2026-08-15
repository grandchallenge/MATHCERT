#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "governance/result_family_adjudication_execution_inputs/OTP-J1-COMPACTNESS.json"
SCHEMA = ROOT / "schemas/openai_ten_proofs_compactness_adjudication_execution_input.schema.json"
ROUTES = ROOT / "governance/certification_routes.json"
ADJUDICATION = ROOT / "governance/result_family_adjudications/OTP-J1-COMPACTNESS.json"
CERTIFICATE = ROOT / "certificates/formal_sources/MC-OTP-J1-COMPACTNESS-001.json"

TARGETS = [
    "CompactnessConjecture.quantitativeCompactnessCounterexample",
    "CompactnessConjecture.compactnessCounterexample_bigO",
    "CompactnessConjecture.not_erdos_180",
]
DISPOSITIONS = [
    "adjudication_clear_encoded_targets_only",
    "adjudication_not_clear",
    "defer_insufficient_evidence",
]
PINS = {
    "governance/result_family_adjudication_contracts/OTP-J1-COMPACTNESS.json": "4288cf2199603ffc90d897062a575a5865326d70",
    "governance/result_family_construction_evidence/OTP-J1-COMPACTNESS.json": "872cdf678412d63df22d1244b3b5c13185f29571",
    "evidence/openai_ten_proofs/compactness_construction/source_authority.json": "148ff82af760bba80c7d16a3a35c58d490dadc95",
    "evidence/openai_ten_proofs/compactness_construction/reconstruction.json": "ed79d855016a1e642d361e9162ed2b70d267b800",
    "governance/certification_routes.json": "aa460c1310a7c81b64b88013b7aa4cfdc056f37b",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def blob(path: Path) -> str:
    return subprocess.check_output(["git", "hash-object", str(path)], cwd=ROOT, text=True).strip()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_record(record: dict, *, check_repository: bool = True) -> None:
    schema = load(SCHEMA)
    errors = sorted(Draft202012Validator(schema).iter_errors(record), key=lambda e: list(e.path))
    if errors:
        raise ValueError("schema validation failed: " + "; ".join(e.message for e in errors[:4]))

    require(record["protected_base"] == "ad80e83ceb6dd1ac980d4c2c02cd07b11b8c3d90", "protected base drift")
    require(record["contract"]["contract_id"] == "MC-OTP-ADJUDICATION-CONTRACT-J1-COMPACTNESS", "contract substitution")
    require(record["encoded_targets"] == TARGETS, "target set/order drift")
    require(record["decision_contract"]["admissible_dispositions"] == DISPOSITIONS, "disposition set drift")
    require(record["decision_contract"]["disposition_at_input_stage"] is None, "premature adjudication disposition")

    evidence = record["protected_evidence"]
    require(evidence["merge_commit"] == "ad80e83ceb6dd1ac980d4c2c02cd07b11b8c3d90", "evidence merge drift")
    require(evidence["record_git_blob_sha1"] == PINS["governance/result_family_construction_evidence/OTP-J1-COMPACTNESS.json"], "evidence record pin drift")
    require(evidence["source_manifest_git_blob_sha1"] == PINS["evidence/openai_ten_proofs/compactness_construction/source_authority.json"], "source manifest pin drift")
    require(evidence["reconstruction_git_blob_sha1"] == PINS["evidence/openai_ten_proofs/compactness_construction/reconstruction.json"], "reconstruction pin drift")
    require(evidence["evidence_disposition"] == "CONSTRUCTION_EVIDENCE_COMPLETE_READY_TO_REQUEST_ADJUDICATION", "evidence disposition drift")

    source = record["current_source"]
    require(source["expected_bytes"] == 2487031, "source byte-count drift")
    require(source["expected_sha256"] == "ebc561ab5c53dbd240e17a8fdb6fffeb648591eca85dbfc7466f563638f8c566", "source SHA-256 drift")
    require(source["whole_document_equivalence_between_revisions"] == "not_established", "whole-document equivalence inflation")

    recipe = record["execution_recipe"]
    require(recipe["human_steward_authorization_required"] is True, "Human Steward gate removed")
    require(recipe["authorization_must_name_contract_and_exact_head"] is True, "exact-head authorization gate weakened")
    require(recipe["execution_authorized"] is False and recipe["authorization"] is None, "authorization prepopulation")
    require(recipe["fresh_source_reacquisition_required"] is True, "fresh source gate removed")
    require(recipe["fresh_isolated_replay_required"] is True, "fresh replay gate removed")
    require(recipe["publication_must_be_descendant_of_authorized_input_head"] is True, "authorization ancestry gate removed")

    state = record["required_state"]
    require(state == {
        "adjudication": None,
        "aggregate_adjudication": False,
        "aggregate_output": False,
        "cert_output": None,
        "mathematical_target_proved": False,
        "may_adjudicate": False,
        "may_promote_claim": False,
        "route_state": "submitted",
    }, "required state inflated")
    require(record["review_gate"]["recorded_review"] is None, "review authority prepopulated")
    require(record["preserved_limitations"]["proof_body_compared_in_full"] is False, "proof-body scope inflated")
    require(record["preserved_limitations"]["aggregate_openai_ten_proofs_authority"] is False, "aggregate authority inflated")

    if not check_repository:
        return

    for rel, expected in PINS.items():
        actual = blob(ROOT / rel)
        require(actual == expected, f"protected blob drift for {rel}: expected {expected}, found {actual}")

    routes = load(ROUTES)
    matches = [r for r in routes["routes"] if r.get("route_id") == "MC-ROUTE-OTP-J1-COMPACTNESS"]
    require(len(matches) == 1, "Compactness route missing/duplicated")
    route = matches[0]
    require(route.get("intake_status") == "submitted", "live Compactness route transitioned")
    require(route.get("cert_output") is None, "live Compactness Cert output inserted")
    require(route.get("target_claim_ids") == TARGETS, "live Compactness target set drift")

    require(not ADJUDICATION.exists(), "Compactness adjudication record exists before exact-head Human Steward authorization")
    require(not CERTIFICATE.exists(), "Compactness certificate exists before adjudication/output authority")


def main() -> int:
    try:
        validate_record(load(INPUT))
    except Exception as exc:
        print(f"Compactness adjudication execution-input validation failed: {exc}", file=sys.stderr)
        return 1
    print("validated frozen Compactness adjudication execution input: no disposition, no authorization, submitted route")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
