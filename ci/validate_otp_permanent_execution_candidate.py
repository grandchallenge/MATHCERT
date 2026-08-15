#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "governance/result_family_execution_candidates/OTP-C-PERMANENT.json"
MANIFEST = ROOT / "governance/result_family_execution_candidate_manifests/OTP-C-PERMANENT.json"
CANDIDATE_SCHEMA = ROOT / "schemas/openai_ten_proofs_permanent_execution_candidate.schema.json"
MANIFEST_SCHEMA = ROOT / "schemas/openai_ten_proofs_permanent_execution_candidate_manifest.schema.json"
EVIDENCE_ROOT = ROOT / "evidence/openai_ten_proofs/permanent_candidate"
RAW_CANDIDATE = EVIDENCE_ROOT / "execution-candidate.json"
RAW_MANIFEST = EVIDENCE_ROOT / "bundle-manifest.json"
SHA256SUMS = EVIDENCE_ROOT / "SHA256SUMS"
CONTRACT = ROOT / "governance/result_family_adjudication_contracts/OTP-C-PERMANENT.json"
DESIGN_REGISTRY = ROOT / "governance/adjudication_design/OPENAI_TEN_PROOFS_PERMANENT_ADJUDICATION_CONTRACT.json"
ROUTES = ROOT / "governance/certification_routes.json"

EXPECTED_CONTRACT_BLOB = "f9429395e7026f838ad6994b8f908a86506cfe06"
EXPECTED_DESIGN_REGISTRY_BLOB = "2af852600796e35afe034bbaf9b9e13950055a29"
EXPECTED_ROUTES_BLOB = "4b7f98414958999c8404e30a4a7c0a2a104578da"
EXPECTED_RAW_CANDIDATE_SHA256 = "c5f109008c87710dbf1c7e49800b6be8ca730a684b0d13201f2b0a1dcfe14ee7"
EXPECTED_RAW_MANIFEST_SHA256 = "dfa3443ed4197fae90676ad21093109214cda34e9c495ef1998c1da8d3b0d369"
EXPECTED_ARTIFACT_SHA256 = "13126f10d7976cacb933c58aa5607db03c753370035988827d94c47fce93df0a"
EXPECTED_TARGETS = [
    "PermanentFormulaLowerBound.permanent_divisionFree_formula_logarithmic_lower_bound",
    "PermanentFormulaLowerBound.permanent_rational_formula_logarithmic_lower_bound",
]
ROUTE_ID = "MC-ROUTE-OTP-C-PERMANENT-FORMULA"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data, usedforsecurity=False).hexdigest()


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
    *,
    candidate: dict[str, Any] | None = None,
    manifest: dict[str, Any] | None = None,
    routes: dict[str, Any] | None = None,
    contract_blob: str | None = None,
    design_registry_blob: str | None = None,
    routes_blob: str | None = None,
) -> list[str]:
    candidate = load(CANDIDATE) if candidate is None else candidate
    manifest = load(MANIFEST) if manifest is None else manifest
    routes = load(ROUTES) if routes is None else routes
    candidate_schema = load(CANDIDATE_SCHEMA)
    manifest_schema = load(MANIFEST_SCHEMA)
    errors: list[str] = []

    for label, schema in (("candidate", candidate_schema), ("manifest", manifest_schema)):
        open_paths = open_object_paths(schema)
        if open_paths:
            errors.append(f"{label} schema contains open object: {open_paths[0]}")
        for error in Draft202012Validator(schema).iter_errors(
            candidate if label == "candidate" else manifest
        ):
            errors.append(f"{label} schema: {'/'.join(map(str, error.path))}: {error.message}")

    if (git_blob_sha1(CONTRACT) if contract_blob is None else contract_blob) != EXPECTED_CONTRACT_BLOB:
        errors.append("governing adjudication-contract blob drift")
    if (git_blob_sha1(DESIGN_REGISTRY) if design_registry_blob is None else design_registry_blob) != EXPECTED_DESIGN_REGISTRY_BLOB:
        errors.append("governing adjudication-design registry blob drift")
    if (git_blob_sha1(ROUTES) if routes_blob is None else routes_blob) != EXPECTED_ROUTES_BLOB:
        errors.append("registered-route registry drift")

    route_list = routes.get("routes", [])
    route = next((r for r in route_list if isinstance(r, dict) and r.get("route_id") == ROUTE_ID), None)
    if route is None:
        errors.append("registered Permanent route missing")
    else:
        if route.get("intake_status") != "submitted":
            errors.append("Permanent route state is not submitted")
        if route.get("target_claim_ids") != EXPECTED_TARGETS:
            errors.append("Permanent live route target drift")
        if route.get("cert_output") is not None:
            errors.append("Permanent live route gained Cert output")

    if not EVIDENCE_ROOT.is_dir():
        errors.append("repository evidence root missing")
        return errors

    # The raw generated candidate and raw generated manifest must be retained exactly.
    if not RAW_CANDIDATE.is_file() or sha256(RAW_CANDIDATE) != EXPECTED_RAW_CANDIDATE_SHA256:
        errors.append("raw execution-candidate bytes drift")
    if not RAW_MANIFEST.is_file() or sha256(RAW_MANIFEST) != EXPECTED_RAW_MANIFEST_SHA256:
        errors.append("raw bundle-manifest bytes drift")
    if load(RAW_MANIFEST) != manifest:
        errors.append("governance manifest differs from raw generated manifest")

    manifest_files = manifest.get("files", [])
    names: set[str] = set()
    for entry in manifest_files:
        name = entry.get("name")
        if not isinstance(name, str) or not name or "/" in name or "\\" in name:
            errors.append("invalid evidence manifest file name")
            continue
        if name in names:
            errors.append(f"duplicate evidence manifest entry: {name}")
            continue
        names.add(name)
        path = EVIDENCE_ROOT / name
        if not path.is_file():
            errors.append(f"missing retained evidence file: {name}")
            continue
        if path.stat().st_size != entry.get("bytes"):
            errors.append(f"retained evidence byte-count drift: {name}")
        if sha256(path) != entry.get("sha256"):
            errors.append(f"retained evidence SHA-256 drift: {name}")
        if git_blob_sha1(path) != entry.get("git_blob_sha1"):
            errors.append(f"retained evidence Git-blob drift: {name}")

    expected_manifest_names = {
        "axiom-check.json", "challenge-build.log", "comparator.log", "environment.txt",
        "evidence-summary.json", "execution-candidate.json", "nonvacuity-replay.log",
        "solution-build.log", "source-identities.txt", "theorem-axioms.log",
        "trust-boundary-scan.txt",
    }
    if names != expected_manifest_names:
        errors.append("retained evidence manifest membership drift")

    if not SHA256SUMS.is_file():
        errors.append("SHA256SUMS missing")
    else:
        sums: dict[str, str] = {}
        for line in SHA256SUMS.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            parts = line.split("  ", 1)
            if len(parts) != 2:
                errors.append("malformed SHA256SUMS line")
                continue
            sums[parts[1]] = parts[0]
        for path in sorted(p for p in EVIDENCE_ROOT.iterdir() if p.is_file() and p.name != "SHA256SUMS"):
            if sums.get(path.name) != sha256(path):
                errors.append(f"SHA256SUMS mismatch: {path.name}")

    # Independent semantic checks beyond the exact schema.
    generation = candidate.get("generation", {})
    artifact = generation.get("artifact", {})
    if generation.get("workflow_run_id") != 31865384142 or generation.get("job_id") != 94965489228:
        errors.append("fresh workflow provenance drift")
    if generation.get("generation_head") != "5b1f26662a9f355493f773d48c43aa54da57ca9c":
        errors.append("fresh generation-head drift")
    if generation.get("workflow_checkout_sha") != "97c22a582769036193288e95618fceba7ccc99f1":
        errors.append("fresh workflow-checkout drift")
    if artifact.get("id") != 9241937165 or artifact.get("sha256") != EXPECTED_ARTIFACT_SHA256:
        errors.append("raw workflow artifact identity drift")
    if candidate.get("encoded_targets") != EXPECTED_TARGETS:
        errors.append("candidate target drift")
    if candidate.get("candidate_state") != "evidence_prepared":
        errors.append("candidate is not evidence_prepared")
    state = candidate.get("state", {})
    if state != {
        "adjudication": None,
        "aggregate_adjudication": False,
        "cert_output": None,
        "mathematical_target_proved": False,
        "may_adjudicate": False,
        "may_issue_output": False,
        "may_promote_claim": False,
        "route_state": "submitted",
    }:
        errors.append("candidate authority/state inflation")
    control = candidate.get("control_plan", {})
    if control != {
        "conformance": "within_admitted_contract",
        "control_plan_change_requested": False,
        "human_steward_intervention_required_only_for_control_plan_change": True,
        "routine_stage_progression_without_human_steward_intervention": True,
    }:
        errors.append("streamlined control-plan drift")
    limitations = candidate.get("preserved_limitations", {})
    if limitations != {
        "aggregate_openai_ten_proofs_authority": False,
        "circuit_targets_in_scope": False,
        "gate_bounds_in_scope": False,
        "historical_pdf_byte_equivalence": "not_established",
        "total_size_consequences_in_scope": False,
    }:
        errors.append("candidate preserved-limitations drift")

    raw = load(RAW_CANDIDATE) if RAW_CANDIDATE.is_file() else {}
    if raw.get("candidate_id") != candidate.get("candidate_id"):
        errors.append("raw/governance candidate identity mismatch")
    if raw.get("control_plan") != candidate.get("control_plan"):
        errors.append("raw/governance control-plan mismatch")
    if raw.get("state") != candidate.get("state"):
        errors.append("raw/governance authority-state mismatch")
    if raw.get("encoded_targets") != candidate.get("encoded_targets"):
        errors.append("raw/governance target mismatch")

    summary_path = EVIDENCE_ROOT / "evidence-summary.json"
    if summary_path.is_file():
        summary = load(summary_path)
        if summary.get("results") != {
            "challenge_build": "pass",
            "comparator": "pass",
            "lean_kernel": "accept",
            "nanoda": "accept",
            "nonvacuity_replay": "pass",
            "semantic_concordance": "protected_predecessor_reconfirmed",
            "solution_build": "pass",
            "theorem_axiom_report": "permitted_only",
            "trust_boundary_scan": "clear",
        }:
            errors.append("fresh replay result drift")
        if summary.get("targets", {}).get("theorem_names") != EXPECTED_TARGETS:
            errors.append("fresh replay target drift")

    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"Permanent execution-candidate validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print(
        "validated fresh non-adjudicated OTP-C-PERMANENT execution candidate; "
        "route remains submitted and streamlined control plan is preserved"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
