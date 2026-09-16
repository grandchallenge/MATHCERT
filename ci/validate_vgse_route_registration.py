#!/usr/bin/env python3
"""Validate bounded VGSE route, adjudication, and restricted qualification state."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import types
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = "ci/validate_vgse_route_registration.py"
ROUTES_PATH = "governance/certification_routes.json"
PROTECTED_BASE_COMMIT = "2e2d4509c993b9ae4bd4aaab48ecced429813b83"
EXPECTED_BASE_BLOB = "4b7f98414958999c8404e30a4a7c0a2a104578da"

RECORD_PATH = ROOT / "governance" / "certification_route_overlays" / "VGSE-001.json"
SCHEMA_PATH = ROOT / "schemas" / "vgse_route_registration.schema.json"
BASE_REGISTRY_PATH = ROOT / ROUTES_PATH
DOC_PATH = ROOT / "docs" / "work_packages" / "MC-VGSE-WP00-ROUTE-001.md"
CONTRACT_PATH = ROOT / "governance" / "result_family_adjudication_contracts" / "VGSE-001.json"
CONTRACT_SCHEMA_PATH = ROOT / "schemas" / "vgse_adjudication_contract.schema.json"
EXACT_EVIDENCE_PATH = ROOT / "evidence" / "vgse" / "VGSE-WP00-CERT-001-exact-algebraic-graph.json"
PLANAR_EVIDENCE_PATH = ROOT / "evidence" / "vgse" / "VGSE-WP00-CERT-001-planar.json"
C06_BINDING_PATH = ROOT / "evidence" / "vgse" / "VGSE-WP00-CERT-001-c06-producer-binding.json"
SUCCESSOR_PATH = ROOT / "governance" / "certification_route_overlays" / "VGSE-001-R4.json"
SUCCESSOR_SCHEMA_PATH = ROOT / "schemas" / "vgse_r4_route_registration.schema.json"
OUTPUT_CONTRACT_PATH = ROOT / "governance" / "vgse_output_contracts" / "VGSE-001-R4.json"
CERTIFICATE_PATH = ROOT / "certificates" / "vgse" / "MC-VGSE-WP00-R4-QUAL-001.json"
CERTIFICATE_SCHEMA_PATH = ROOT / "schemas" / "vgse_r4_qualified_output.schema.json"
EXPECTED_CERTIFICATE_COMMIT = "9001318adcc759e4841c6f68b6619b0fe25d0bb5"
EXPECTED_CERTIFICATE_BLOB = "e6489fab69506adacc4a33214f22dd20413ec40a"
EXPECTED_CERTIFICATE_RELPATH = "certificates/vgse/MC-VGSE-WP00-R4-QUAL-001.json"
EXPECTED_SUCCESSOR_BLOB = "578547c57d91df0616197ae56fd4497ffd6e1576"

EXPECTED_TARGETS = [
    {"claim_id":"VGSE-C00","statement":"For the recorded rational five-line arrangement, beta(C)=5.","support_type":"EXACT_RATIONAL_CERTIFICATE","evidence_path":"evidence/vgse/VGSE-WP00-CERT-001-exact-algebraic-graph.json"},
    {"claim_id":"VGSE-C01","statement":"After saturation by the arrangement divisor, the recorded Figure 16 chart has exactly five isolated solutions away from every alpha_i=0.","support_type":"COMPUTER_ALGEBRA_CERTIFICATE_WITH_REPLAY","evidence_path":"evidence/vgse/VGSE-WP00-CERT-001-exact-algebraic-graph.json"},
    {"claim_id":"VGSE-C04","statement":"A positive weighted representative of the reconstructed graph reproduces the recorded Plucker data up to one common scale.","support_type":"INTERVAL_ARITHMETIC_CERTIFICATE","evidence_path":"evidence/vgse/VGSE-WP00-CERT-001-exact-algebraic-graph.json"},
    {"claim_id":"VGSE-C05","statement":"The five retained algebraic witnesses extend to five planar t-embeddings satisfying the recorded boundary and geometric constraints.","support_type":"INTERVAL_ARITHMETIC_CERTIFICATE","evidence_path":"evidence/vgse/VGSE-WP00-CERT-001-planar.json"},
]
EXPECTED_TARGET_IDS = [item["claim_id"] for item in EXPECTED_TARGETS]


def git(*args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(["git", *args], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def ensure_commit(commit: str) -> None:
    shallow = git("rev-parse", "--is-shallow-repository")
    if shallow.returncode == 0 and shallow.stdout.decode().strip() == "true":
        result = git("fetch", "--no-tags", "--unshallow", "origin")
        if result.returncode != 0:
            raise RuntimeError("unable to unshallow VGSE route history")
    if git("cat-file", "-e", f"{commit}^{{commit}}").returncode != 0:
        result = git("fetch", "--no-tags", "origin", commit)
        if result.returncode != 0:
            raise RuntimeError(f"unable to fetch governed commit {commit}")


def git_show(commit: str, path: str) -> bytes:
    ensure_commit(commit)
    result = git("show", f"{commit}:{path}")
    if result.returncode != 0:
        raise RuntimeError(f"unable to read {path} at {commit}")
    return result.stdout


def protected_module() -> types.ModuleType:
    source = git_show(PROTECTED_BASE_COMMIT, SOURCE_PATH).decode("utf-8")
    module = types.ModuleType("protected_vgse_route_registration")
    module.__file__ = str(ROOT / SOURCE_PATH)
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    return module


def snapshot_registry() -> dict[str, Any]:
    return json.loads(git_show(PROTECTED_BASE_COMMIT, ROUTES_PATH))


def validation_errors(record: dict[str, Any] | None = None, *, schema: dict[str, Any] | None = None, base_registry: dict[str, Any] | None = None, base_blob: str | None = None, documentation: str | None = None) -> list[str]:
    try:
        base = protected_module()
        pinned_registry = snapshot_registry() if base_registry is None else base_registry
    except RuntimeError as exc:
        return [str(exc)]
    return base.validation_errors(record, schema=schema, base_registry=pinned_registry, base_blob=EXPECTED_BASE_BLOB if base_blob is None else base_blob, documentation=documentation)


def blob_sha1(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(f"blob {len(payload)}\0".encode("ascii") + payload, usedforsecurity=False).hexdigest()


def contract_validation_errors(contract: dict[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    candidate = json.loads(CONTRACT_PATH.read_text(encoding="utf-8")) if contract is None else contract
    schema = json.loads(CONTRACT_SCHEMA_PATH.read_text(encoding="utf-8"))
    for error in Draft202012Validator(schema).iter_errors(candidate):
        errors.append(f"contract schema: {error.json_path}: {error.message}")
    if errors:
        return errors

    if candidate["route_scope"]["target_claims"] != EXPECTED_TARGETS:
        errors.append("contract exact four-target statement set drift")
    if candidate["route_scope"]["excluded_route_claim_ids"] != ["VGSE-C06"]:
        errors.append("contract C06 exclusion drift")
    gate = candidate["execution_gate"]
    if gate["routine_stage_progression_without_human_steward_intervention"] is not True:
        errors.append("contract improperly reinstates ceremonial Human Steward intervention")
    if gate["human_steward_intervention_required_for_control_plan_change"] is not True:
        errors.append("contract control-plan-change Human Steward boundary weakened")
    if candidate["state"] != {"may_adjudicate":False,"adjudication":None,"cert_output":None,"mathematical_target_proved":False,"may_issue_output":False,"may_promote_claim":False,"aggregate_adjudication":False}:
        errors.append("contract design-only authority inflated")

    route = json.loads(RECORD_PATH.read_text(encoding="utf-8"))
    if candidate["route_scope"]["registered_route_state"] != route["route_state"]:
        errors.append("contract route-state mismatch")

    exact = json.loads(EXACT_EVIDENCE_PATH.read_text(encoding="utf-8"))
    planar = json.loads(PLANAR_EVIDENCE_PATH.read_text(encoding="utf-8"))
    c06 = json.loads(C06_BINDING_PATH.read_text(encoding="utf-8"))
    if exact.get("claims_addressed") != ["VGSE-C00", "VGSE-C01", "VGSE-C04"]:
        errors.append("exact evidence claim set drift")
    if planar.get("claim_id") != "VGSE-C05":
        errors.append("planar evidence claim drift")
    if c06.get("claims_addressed") != ["VGSE-C06"] or c06.get("cert_interpretation",{}).get("c06_state") != "BLOCKED_VISIBLE_GEOMETRIC_WEIGHT_BRIDGE_TO_PINNED_C":
        errors.append("C06 blocked-state evidence drift")

    authority = candidate["authority"]
    live_blobs = {
        "route_overlay_blob": blob_sha1(RECORD_PATH),
        "exact_algebraic_graph_evidence_blob": blob_sha1(EXACT_EVIDENCE_PATH),
        "planar_evidence_blob": blob_sha1(PLANAR_EVIDENCE_PATH),
        "c06_producer_binding_blob": blob_sha1(C06_BINDING_PATH),
    }
    for key, value in live_blobs.items():
        if authority.get(key) != value:
            errors.append(f"contract authority blob mismatch: {key}")
    if authority.get("cert_c06_reconciliation_merge") != "30efe4ecf4cd9b4553787968d19dfe853bbb67e5":
        errors.append("contract protected C06 reconciliation merge drift")
    if authority.get("c06_producer_merge") != "c8e81d262d4da1a36b312f017443777a4c7888db":
        errors.append("contract producer merge drift")
    return errors


def qualified_output_validation_errors(
    successor: dict[str, Any] | None = None,
    certificate: dict[str, Any] | None = None,
    *,
    certificate_paths: list[str] | None = None,
) -> list[str]:
    """Validate R4 qualified output when the protected certificate is present."""
    if certificate is None and not CERTIFICATE_PATH.exists():
        return []

    errors: list[str] = []
    successor_record = json.loads(SUCCESSOR_PATH.read_text(encoding="utf-8")) if successor is None else successor
    certificate_record = json.loads(CERTIFICATE_PATH.read_text(encoding="utf-8")) if certificate is None else certificate
    successor_schema = json.loads(SUCCESSOR_SCHEMA_PATH.read_text(encoding="utf-8"))
    certificate_schema = json.loads(CERTIFICATE_SCHEMA_PATH.read_text(encoding="utf-8"))

    for error in Draft202012Validator(successor_schema).iter_errors(successor_record):
        errors.append(f"R4 successor schema: {error.json_path}: {error.message}")
    for error in Draft202012Validator(certificate_schema).iter_errors(certificate_record):
        errors.append(f"R4 certificate schema: {error.json_path}: {error.message}")
    if errors:
        return errors

    output_contract = json.loads(OUTPUT_CONTRACT_PATH.read_text(encoding="utf-8"))
    expected_cert_output = {
        "repository": "grandchallenge/MATHCERT",
        "commit_sha": EXPECTED_CERTIFICATE_COMMIT,
        "path": EXPECTED_CERTIFICATE_RELPATH,
        "digest_algorithm": "git_blob_sha1",
        "digest": EXPECTED_CERTIFICATE_BLOB,
    }
    if successor_record["route_state"] != "qualified" or successor_record["intake_status"] != "qualified":
        errors.append("R4 qualified route state drift")
    if successor_record["cert_output"] != expected_cert_output:
        errors.append("R4 cert_output binding drift")
    if successor_record["target_claim_ids"] != EXPECTED_TARGET_IDS:
        errors.append("R4 target claim set drift")
    if successor_record["may_adjudicate"] is not False:
        errors.append("R4 may_adjudicate authority inflated")
    if successor_record["claim_boundary"].get("mathematical_target_proved") is not False:
        errors.append("R4 mathematical-target-proved boundary weakened")
    if successor_record["excluded_claims"] != [{
        "claim_id": "VGSE-C06",
        "predecessor_route_id": "MC-ROUTE-VGSE-001",
        "state": "BLOCKED_VISIBLE_GEOMETRIC_WEIGHT_BRIDGE_TO_PINNED_C",
        "included_in_successor": False,
        "reopening_condition": "Exact source graph/weight-generation data establishing the Figure-16-to-pinned-C bridge, or a separately governed source-authorized correspondence declared before matcher execution."
    }]:
        errors.append("R4 C06 exclusion drift")

    if certificate_record["target_claim_ids"] != EXPECTED_TARGET_IDS:
        errors.append("R4 certificate target set drift")
    if certificate_record["qualification"]["disposition"] != "qualified_exact_four_claims_only":
        errors.append("R4 certificate disposition drift")
    if certificate_record["state"] != {
        "route_state": "qualified",
        "cert_output_inserted": True,
        "mathematical_target_proved": False,
        "may_promote_claim": False,
        "aggregate_authority": False,
        "c06_in_scope": False,
    }:
        errors.append("R4 certificate authority boundary drift")
    if certificate_record["preserved_limitations"].get("c06_state") != "BLOCKED_VISIBLE_GEOMETRIC_WEIGHT_BRIDGE_TO_PINNED_C":
        errors.append("R4 certificate C06 limitation drift")

    if certificate is None and blob_sha1(CERTIFICATE_PATH) != EXPECTED_CERTIFICATE_BLOB:
        errors.append("R4 certificate blob drift")
    if successor is None and blob_sha1(SUCCESSOR_PATH) != EXPECTED_SUCCESSOR_BLOB:
        errors.append("R4 qualified successor blob drift")
    if certificate_record["source_authority"]["output_contract"]["digest"] != blob_sha1(OUTPUT_CONTRACT_PATH):
        errors.append("R4 certificate output-contract digest drift")
    if output_contract["future_certificate"]["path"] != EXPECTED_CERTIFICATE_RELPATH:
        errors.append("R4 output contract certificate path drift")
    if output_contract["output_scope"]["target_claim_ids"] != EXPECTED_TARGET_IDS or output_contract["output_scope"]["excluded_claim_ids"] != ["VGSE-C06"]:
        errors.append("R4 output contract scope drift")
    if output_contract["state"] != {"route_state":"registered_pending_evidence","intake_status":"pending","cert_output":None,"mathematical_target_proved":False,"may_issue_output":False,"may_promote_claim":False,"c06_in_scope":False}:
        errors.append("R4 design-only output contract mutated during publication")

    if certificate_paths is None:
        family_dir = ROOT / "certificates" / "vgse"
        certificate_paths = sorted(
            str(path.relative_to(ROOT)).replace("\\", "/")
            for path in family_dir.glob("*.json")
            if path.is_file()
        ) if family_dir.exists() else []
    if certificate_paths != [EXPECTED_CERTIFICATE_RELPATH]:
        errors.append("VGSE certificate family contains an unauthorized or missing artifact")

    return errors


def main() -> int:
    errors = validation_errors() + contract_validation_errors() + qualified_output_validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"VGSE route/certificate validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    if CERTIFICATE_PATH.exists():
        print("validated VGSE predecessor plus restricted qualified R4 output; C06 remains excluded and blocked")
    else:
        print("validated VGSE pending route and design-only exact four-claim adjudication contract; C06 remains excluded and blocked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())