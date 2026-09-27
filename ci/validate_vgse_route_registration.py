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
TE3_AUDIT_PATH = ROOT / "evidence" / "vgse" / "VGSE-WP00-CERT-001-te3-conformance-audit.json"
RECONCILIATION_PATH = ROOT / "governance" / "result_family_adjudication_reconciliations" / "VGSE-001-C05-TE3.json"
RECONCILIATION_SCHEMA_PATH = ROOT / "schemas" / "vgse_c05_te3_current_state_reconciliation.schema.json"
HISTORICAL_C05_STATEMENT = "The five retained algebraic witnesses extend to five planar t-embeddings satisfying the recorded boundary and geometric constraints."
ACTIVE_C05_STATEMENT = "The five retained algebraic witnesses extend to five planar algebraic Kenyon–Smirnov realizations satisfying the certified discrete-holomorphic, primitive-closure, prescribed-boundary, strict-convexity/noncrossing, Kawasaki, boundary-angle, and distinctness constraints."
EXPECTED_TE3_AUDIT_BLOB = "db6d0d8505dd754a8148a1fd77068c53aa032903"
EXPECTED_TE3_AUDIT_MERGE = "15b68c196d020045bea42fc34236e0647b87cbb9"
EXPECTED_HISTORICAL_VGSE_BLOBS = {
    "governance/result_family_adjudication_contracts/VGSE-001.json": "2214eb6e442ac758c78ec5bc4b1de335c831cffa",
    "governance/result_family_adjudication_execution_inputs/VGSE-001.json": "6ed94cce042978c0373d3c72de0e5ba080cfe320",
    "governance/vgse_adjudications/VGSE-001.json": "57668860de1c96370fb0075e0c7e8f43f7dc0067",
    "certificates/vgse/MC-VGSE-WP00-R4-QUAL-001.json": "e6489fab69506adacc4a33214f22dd20413ec40a",
    "governance/certification_route_overlays/VGSE-001-R4.json": "578547c57d91df0616197ae56fd4497ffd6e1576",
}
EXPECTED_C05_CERTIFIED_PROPERTIES = [
    "five_discrete_holomorphic_extensions",
    "five_primitives_exactly_closed",
    "prescribed_boundary_exact",
    "strict_convexity",
    "noncrossing",
    "kawasaki_equalities_exact",
    "boundary_angle_inequalities_certified",
    "five_embeddings_distinct",
]
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



def current_state_reconciliation_errors(reconciliation: dict[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    candidate = json.loads(RECONCILIATION_PATH.read_text(encoding="utf-8")) if reconciliation is None else reconciliation
    schema = json.loads(RECONCILIATION_SCHEMA_PATH.read_text(encoding="utf-8"))
    for error in Draft202012Validator(schema).iter_errors(candidate):
        errors.append(f"reconciliation schema: {error.json_path}: {error.message}")
    if errors:
        return errors

    predecessor = candidate["protected_predecessor"]
    expected_predecessor = {
        "adjudication_merge": "df9fd2e493da277646e844d3e20fbc65e965d861",
        "adjudication_path": "governance/vgse_adjudications/VGSE-001.json",
        "adjudication_blob": EXPECTED_HISTORICAL_VGSE_BLOBS["governance/vgse_adjudications/VGSE-001.json"],
        "contract_path": "governance/result_family_adjudication_contracts/VGSE-001.json",
        "contract_blob": EXPECTED_HISTORICAL_VGSE_BLOBS["governance/result_family_adjudication_contracts/VGSE-001.json"],
        "execution_input_path": "governance/result_family_adjudication_execution_inputs/VGSE-001.json",
        "execution_input_blob": EXPECTED_HISTORICAL_VGSE_BLOBS["governance/result_family_adjudication_execution_inputs/VGSE-001.json"],
        "r4_certificate_path": "certificates/vgse/MC-VGSE-WP00-R4-QUAL-001.json",
        "r4_certificate_blob": EXPECTED_HISTORICAL_VGSE_BLOBS["certificates/vgse/MC-VGSE-WP00-R4-QUAL-001.json"],
        "r4_route_path": "governance/certification_route_overlays/VGSE-001-R4.json",
        "r4_route_blob": EXPECTED_HISTORICAL_VGSE_BLOBS["governance/certification_route_overlays/VGSE-001-R4.json"],
    }
    if predecessor != expected_predecessor:
        errors.append("C05 reconciliation protected-predecessor identity drift")

    policy = candidate["historical_record_policy"]
    if policy["historical_c05_statement"] != HISTORICAL_C05_STATEMENT or policy["historical_statement_is_current"] is not False:
        errors.append("C05 historical/current statement boundary drift")
    observed_files = {entry.get("path"): entry.get("blob") for entry in policy.get("files", [])}
    if observed_files != EXPECTED_HISTORICAL_VGSE_BLOBS:
        errors.append("C05 reconciliation historical file set/blob drift")
    for relpath, expected_blob in EXPECTED_HISTORICAL_VGSE_BLOBS.items():
        path = ROOT / relpath
        if not path.exists() or blob_sha1(path) != expected_blob:
            errors.append(f"historical VGSE protected bytes changed: {relpath}")

    evidence = candidate["new_evidence"]
    if evidence["audit_merge"] != EXPECTED_TE3_AUDIT_MERGE or evidence["audit_blob"] != EXPECTED_TE3_AUDIT_BLOB:
        errors.append("C05 reconciliation TE3 audit identity drift")
    if blob_sha1(TE3_AUDIT_PATH) != EXPECTED_TE3_AUDIT_BLOB:
        errors.append("protected C05 TE3 audit bytes drift")
    audit = json.loads(TE3_AUDIT_PATH.read_text(encoding="utf-8"))
    conclusion = audit.get("conclusion", {})
    if conclusion.get("disposition") != "TE3_FAILS_FOR_PROTECTED_C04_WEIGHT_CLASS_ON_ALL_FIVE_RETAINED_C05_BRANCHES":
        errors.append("C05 TE3 audit disposition drift")
    if conclusion.get("all_five_branches_exclude_te3") is not True:
        errors.append("C05 TE3 all-five-branches exclusion weakened")
    if conclusion.get("maximum_certified_squared_ratio_strictly_below") != "1/1000" or conclusion.get("te3_required_squared_ratio") != "1":
        errors.append("C05 TE3 quantitative exclusion drift")

    current = candidate["current_state"]
    if current["claim_id"] != "VGSE-C05" or current["active_statement"] != ACTIVE_C05_STATEMENT:
        errors.append("C05 active reconciled statement drift")
    if "t-embeddings" in current["active_statement"] or "source-defined t-embeddings" in current["active_statement"]:
        errors.append("C05 active statement improperly restores t-embedding terminology")
    if current["certified_properties"] != EXPECTED_C05_CERTIFIED_PROPERTIES:
        errors.append("C05 retained certified-property set drift")
    if current["applies_to_route_ids"] != ["MC-ROUTE-VGSE-001", "MC-ROUTE-VGSE-001-R4"]:
        errors.append("C05 reconciliation route applicability drift")
    if current["r4_qualification_interpretation"] != "qualified_only_under_current_reconciled_c05_statement":
        errors.append("C05 R4 current-state qualification interpretation drift")
    if current["historical_adjudication_superseded_interpretation_only"] is not True:
        errors.append("C05 historical-adjudication preservation weakened")

    authority = candidate["authority"]
    if any(value is not False for value in authority.values()):
        errors.append("C05 reconciliation contains unauthorized positive authority")

    preserved = candidate["preserved_claims"]
    if preserved != {
        "unchanged_claim_ids": ["VGSE-C00", "VGSE-C01", "VGSE-C04"],
        "excluded_claim_ids": ["VGSE-C06"],
        "c06_state": "BLOCKED_VISIBLE_GEOMETRIC_WEIGHT_BRIDGE_TO_PINNED_C",
    }:
        errors.append("C05 reconciliation collateral claim boundary drift")

    certificate = json.loads(CERTIFICATE_PATH.read_text(encoding="utf-8"))
    successor = json.loads(SUCCESSOR_PATH.read_text(encoding="utf-8"))
    if "VGSE-C05" not in certificate.get("target_claim_ids", []) or "VGSE-C05" not in successor.get("target_claim_ids", []):
        errors.append("C05 reconciliation lost protected R4 target identity")
    if certificate.get("state", {}).get("mathematical_target_proved") is not False or successor.get("claim_boundary", {}).get("mathematical_target_proved") is not False:
        errors.append("C05 reconciliation improperly promotes mathematical target")

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
    errors = validation_errors() + contract_validation_errors() + current_state_reconciliation_errors() + qualified_output_validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"VGSE route/certificate validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    if CERTIFICATE_PATH.exists():
        print("validated VGSE predecessor, C05 TE3 current-state reconciliation, and restricted qualified R4 output; C06 remains excluded and blocked")
    else:
        print("validated VGSE pending route and design-only exact four-claim adjudication contract; C06 remains excluded and blocked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())