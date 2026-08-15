#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
RECORD_PATH = ROOT / "governance/result_family_replay_evidence_successors/OTP-C-PERMANENT.json"
REGISTRY_PATH = ROOT / "governance/pre_route_candidates/OPENAI_TEN_PROOFS_PERMANENT_REPLAY_EVIDENCE.json"
RECORD_SCHEMA_PATH = ROOT / "schemas/openai_ten_proofs_permanent_cert_replay_evidence.schema.json"
REGISTRY_SCHEMA_PATH = ROOT / "schemas/openai_ten_proofs_permanent_cert_replay_evidence_registry.schema.json"
EVIDENCE_ROOT = ROOT / "evidence/openai_ten_proofs/permanent"
LEGACY_WRAPPER = ROOT / "evidence/openai_ten_proofs/permanent.zip.b64"
HISTORICAL_REGISTRY_PATH = ROOT / "governance/pre_route_candidates/OPENAI_TEN_PROOFS_WP04_REPLAY_EVIDENCE.json"
ROUTE_REGISTRY_PATH = ROOT / "governance/certification_routes.json"

RECORD_BLOB = "7b75a323b6d840730932bf90984f498b7d360cda"
HISTORICAL_REGISTRY_BLOB = "0d9b799181203a7cc38cd0d01ae297985c94cbbf"
MANIFEST_BLOB = "cbc185bd0cd182fddd3127d8373ae7a74f6389dd"
MANIFEST_SHA256 = "351ab107342d2fe72220098ae6e5dc600653e9b181119c99805182270559f969"
TRANSPORT_ZIP_SHA256 = "9f04dbfd0fe6c52329b9905371d33faa44b2f96719485460c6290bc8a74fd507"
EXECUTION_HEAD = "adb5000e6e1353fea52a8d81f3415be1a8d52193"
WORKFLOW_CHECKOUT = "dabf0eb117b48c03c6953a51e6b3a229a802b5b5"
RUN_ID = 31851083366
JOB_ID = 94926860758
ARTIFACT_ID = 9237666071
TARGETS = [
    "PermanentFormulaLowerBound.permanent_divisionFree_formula_logarithmic_lower_bound",
    "PermanentFormulaLowerBound.permanent_rational_formula_logarithmic_lower_bound",
]
WITNESSES = [
    "PermanentFormulaLowerBound.Nonvacuity.permanent_divisionFree_formula_nonvacuous",
    "PermanentFormulaLowerBound.Nonvacuity.permanent_rational_formula_nonvacuous",
]
EXPECTED_FILES = {
    "SHA256SUMS",
    "axiom-check.json",
    "challenge-build.log",
    "comparator.log",
    "environment.txt",
    "evidence-summary.json",
    "nonvacuity-replay.log",
    "solution-build.log",
    "source-identities.txt",
    "theorem-axioms.log",
    "trust-boundary-scan.txt",
}
HISTORICAL_FAMILIES = ["OTP-F-EHRHART", "OTP-J1-COMPACTNESS", "OTP-J2-TWO-DEGENERATE"]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1_bytes(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data, usedforsecurity=False).hexdigest()


def git_blob_sha1(path: Path) -> str:
    return git_blob_sha1_bytes(path.read_bytes())


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def schema_errors(instance, schema_path: Path, label: str) -> list[str]:
    validator = Draft202012Validator(load(schema_path))
    return [f"{label} schema: {e.message}" for e in sorted(validator.iter_errors(instance), key=lambda e: list(e.path))]


def historical_evidence_errors() -> list[str]:
    spec = importlib.util.spec_from_file_location(
        "historical_replay_evidence", ROOT / "ci/validate_openai_ten_proofs_replay_evidence.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validation_errors()


def validation_errors(
    record=None,
    registry=None,
    file_overrides: dict[str, bytes] | None = None,
    record_blob_override: str | None = None,
    historical_blob_override: str | None = None,
    **_,
) -> list[str]:
    errors: list[str] = []
    record = load(RECORD_PATH) if record is None else record
    registry = load(REGISTRY_PATH) if registry is None else registry
    overrides = {} if file_overrides is None else file_overrides

    errors.extend(schema_errors(record, RECORD_SCHEMA_PATH, "Permanent replay evidence"))
    errors.extend(schema_errors(registry, REGISTRY_SCHEMA_PATH, "Permanent replay evidence registry"))

    actual_record_blob = git_blob_sha1(RECORD_PATH) if record_blob_override is None else record_blob_override
    if actual_record_blob != RECORD_BLOB:
        errors.append("Permanent replay evidence record blob drift")
    if registry.get("successor_evidence", {}).get("digest") != actual_record_blob:
        errors.append("successor registry/evidence record digest mismatch")

    actual_historical_blob = git_blob_sha1(HISTORICAL_REGISTRY_PATH) if historical_blob_override is None else historical_blob_override
    if actual_historical_blob != HISTORICAL_REGISTRY_BLOB:
        errors.append("historical three-family replay-evidence registry blob drift")
    historical = load(HISTORICAL_REGISTRY_PATH)
    if [x.get("result_family") for x in historical.get("evidence_records", [])] != HISTORICAL_FAMILIES:
        errors.append("historical three-family replay-evidence membership drift")
    if historical_evidence_errors():
        errors.append("historical three-family replay-evidence validation failed")

    if LEGACY_WRAPPER.exists():
        errors.append("obsolete encoded replay wrapper must not be retained")
    if not EVIDENCE_ROOT.is_dir():
        errors.append("repository replay evidence directory is missing")
        actual_names: set[str] = set()
    else:
        actual_names = {p.name for p in EVIDENCE_ROOT.iterdir() if p.is_file()}
    if actual_names != EXPECTED_FILES:
        errors.append("repository replay evidence directory membership drift")

    meta = record.get("evidence_files", {})
    if set(meta) != EXPECTED_FILES:
        errors.append("evidence-file inventory drift")

    file_data: dict[str, bytes] = {}
    for name in EXPECTED_FILES:
        path = EVIDENCE_ROOT / name
        if name in overrides:
            data = overrides[name]
        elif path.exists():
            data = path.read_bytes()
        else:
            continue
        file_data[name] = data
        expected = meta.get(name, {})
        if expected.get("bytes") != len(data): errors.append(f"{name} byte length drift")
        if expected.get("sha256") != sha256(data): errors.append(f"{name} SHA-256 drift")
        if expected.get("git_blob_sha1") != git_blob_sha1_bytes(data): errors.append(f"{name} Git blob drift")

    if "SHA256SUMS" in file_data:
        manifest = file_data["SHA256SUMS"]
        if sha256(manifest) != MANIFEST_SHA256 or git_blob_sha1_bytes(manifest) != MANIFEST_BLOB:
            errors.append("repository evidence manifest identity drift")
        listed: dict[str, str] = {}
        for line in manifest.decode("utf-8").splitlines():
            digest, path = line.split(None, 1)
            listed[Path(path.strip()).name] = digest
        expected_listed = EXPECTED_FILES - {"SHA256SUMS"}
        if set(listed) != expected_listed:
            errors.append("repository evidence manifest membership drift")
        for name in expected_listed & file_data.keys():
            if listed.get(name) != sha256(file_data[name]):
                errors.append(f"repository evidence manifest digest mismatch for {name}")

    artifact = record.get("actions_artifact", {})
    if artifact != {
        "artifact_id": ARTIFACT_ID,
        "name": "otp-permanent-evidence",
        "bytes": 6563,
        "sha256": TRANSPORT_ZIP_SHA256,
        "source_run_id": RUN_ID,
        "source_head_sha": EXECUTION_HEAD,
    }:
        errors.append("Actions artifact provenance drift")
    bundle = record.get("repository_bundle", {})
    if bundle != {
        "root":"evidence/openai_ten_proofs/permanent",
        "format":"content_addressed_directory",
        "file_count":11,
        "manifest_path":"evidence/openai_ten_proofs/permanent/SHA256SUMS",
        "manifest_git_blob_sha1":MANIFEST_BLOB,
        "manifest_sha256":MANIFEST_SHA256,
        "transport_zip_bytes":6563,
        "transport_zip_sha256":TRANSPORT_ZIP_SHA256,
    }:
        errors.append("repository evidence bundle contract drift")

    if "evidence-summary.json" in file_data:
        try:
            summary = json.loads(file_data["evidence-summary.json"].decode("utf-8"))
            execution = summary.get("execution", {})
            if execution.get("mathcert_head_sha") != EXECUTION_HEAD or execution.get("workflow_checkout_sha") != WORKFLOW_CHECKOUT:
                errors.append("evidence summary execution identity drift")
            targets = summary.get("targets", {})
            if targets.get("theorem_names") != TARGETS or targets.get("nonvacuity_witnesses") != WITNESSES:
                errors.append("evidence summary target/witness drift")
            if summary.get("results") != {
                "solution_build":"pass","challenge_build":"pass","comparator":"pass","lean_kernel":"accept","nanoda":"accept","nonvacuity_replay":"pass","theorem_axiom_report":"permitted_only","trust_boundary_scan":"clear","semantic_concordance":"protected_predecessor_reconfirmed"
            }:
                errors.append("evidence summary replay-result drift")
            if summary.get("source_projection") != {
                "formula_target_count":2,"circuit_target_count":0,"coefficient_field":"complex","dimension_threshold":32,"log_base":2,"division_free_variable_leaf_constant":128,"rational_variable_leaf_constant":192,"gate_bounds_in_replay":False,"total_leaves_vertices_in_replay":False,"historical_pdf_byte_equivalence":False
            }:
                errors.append("evidence summary source projection drift")
            if summary.get("route_state") != {
                "requested_future_route_id":"MC-ROUTE-OTP-C-PERMANENT-FORMULA","proposed_route_record":None,"registered_route":None,"may_adjudicate":False,"cert_output":None,"mathematical_target_proved":False,"may_promote_claim":False
            }:
                errors.append("evidence summary route/proof authority inflation")
        except Exception as exc:
            errors.append(f"invalid evidence summary: {exc}")

    if "axiom-check.json" in file_data:
        try:
            ax = json.loads(file_data["axiom-check.json"].decode("utf-8"))
            if ax.get("permitted") != ["Classical.choice", "Quot.sound", "propext"]:
                errors.append("axiom permitted-set drift")
            reports = ax.get("reports", [])
            if [r.get("theorem") for r in reports] != TARGETS:
                errors.append("axiom report theorem membership drift")
            for report in reports:
                if report.get("axioms") != ["Classical.choice", "Quot.sound", "propext"] or report.get("unexpected") != []:
                    errors.append("unexpected theorem axiom evidence")
        except Exception as exc:
            errors.append(f"invalid axiom report: {exc}")

    if "comparator.log" in file_data:
        text = file_data["comparator.log"].decode("utf-8", errors="replace")
        for marker in ["Nanoda kernel accepts the solution", "Lean default kernel accepts the solution", "Your solution is okay!"]:
            if marker not in text: errors.append(f"Comparator acceptance marker missing: {marker}")
    if "trust-boundary-scan.txt" in file_data:
        text = file_data["trust-boundary-scan.txt"].decode("utf-8", errors="replace")
        for marker in ["placeholder and unsafe/custom-axiom scan: clear", "aggregate All import scan: clear"]:
            if marker not in text: errors.append(f"trust-boundary marker missing: {marker}")

    execution = record.get("execution", {})
    if execution.get("subject_head_sha") != EXECUTION_HEAD or execution.get("workflow_checkout_sha") != WORKFLOW_CHECKOUT or execution.get("workflow_run_id") != RUN_ID or execution.get("workflow_job_id") != JOB_ID:
        errors.append("governed execution identity drift")
    if execution.get("clean_room_runner") is not True or execution.get("isolated_family_replay") is not True or execution.get("aggregate_all_import_used") is not False:
        errors.append("governed replay isolation drift")

    scope = record.get("target_scope", {})
    if scope.get("theorems") != TARGETS or scope.get("nonvacuity_witnesses") != WITNESSES:
        errors.append("governed target membership drift")
    if scope.get("formula_target_count") != 2 or scope.get("circuit_target_count") != 0:
        errors.append("formula/circuit target count drift")
    projection = scope.get("source_projection", {})
    if projection.get("gate_bounds_in_replay") is not False or projection.get("total_leaves_vertices_in_replay") is not False or projection.get("historical_pdf_byte_equivalence") is not False:
        errors.append("excluded source authority admitted into replay")

    route = record.get("route_state", {})
    if route != {
        "requested_future_route_id":"MC-ROUTE-OTP-C-PERMANENT-FORMULA","route_proposal_created":False,"registered_route":None,"may_adjudicate":False,"cert_output":None,"mathematical_target_proved":False,"may_promote_claim":False,"aggregate_route_prohibited":True
    }:
        errors.append("replay evidence route/adjudication/proof authority inflation")
    if record.get("review_state") != {"specialist_review_required":True,"status":"pending_exact_head_non_author_review"}:
        errors.append("specialist review state drift")

    routes = load(ROUTE_REGISTRY_PATH).get("routes", [])
    if any(r.get("route_id") == "MC-ROUTE-OTP-C-PERMANENT-FORMULA" for r in routes):
        errors.append("Permanent route registered before replay-evidence admission")

    if registry.get("execution_state") != {"authorized_target_count":2,"circuit_target_count":0,"replay_evidence_bundle_count":1,"specialist_review_count":0,"route_proposal_count":0,"registered_route_count":0,"adjudication_count":0,"cert_output_count":0,"mathematical_target_proved_count":0}:
        errors.append("successor replay-evidence registry state inflation")
    if registry.get("route_controls") != {"requested_future_route":"MC-ROUTE-OTP-C-PERMANENT-FORMULA","route_proposal_created":False,"route_registration_created":False,"may_adjudicate":False,"may_promote_claim":False,"aggregate_route_prohibited":True}:
        errors.append("successor replay-evidence route controls drift")

    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("validated Permanent exact-family replay evidence directory; manifest and all file hashes match the successful Actions artifact; historical three-family evidence preserved; no route, adjudication, output, proof, circuit, gate, total-size, PDF-equivalence, or aggregate authority created")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
