#!/usr/bin/env python3
from __future__ import annotations

import base64
import hashlib
import importlib.util
import io
import json
import sys
import zipfile
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
RECORD_PATH = ROOT / "governance/result_family_replay_evidence_successors/OTP-C-PERMANENT.json"
REGISTRY_PATH = ROOT / "governance/pre_route_candidates/OPENAI_TEN_PROOFS_PERMANENT_REPLAY_EVIDENCE.json"
RECORD_SCHEMA_PATH = ROOT / "schemas/openai_ten_proofs_permanent_cert_replay_evidence.schema.json"
REGISTRY_SCHEMA_PATH = ROOT / "schemas/openai_ten_proofs_permanent_cert_replay_evidence_registry.schema.json"
BUNDLE_PATH = ROOT / "evidence/openai_ten_proofs/permanent.zip.b64"
HISTORICAL_REGISTRY_PATH = ROOT / "governance/pre_route_candidates/OPENAI_TEN_PROOFS_WP04_REPLAY_EVIDENCE.json"
ROUTE_REGISTRY_PATH = ROOT / "governance/certification_routes.json"

RECORD_BLOB = "8141ee919813aec3eb04e4b58ec804cc90b457ba"
BUNDLE_BLOB = "44adfbd80018dda202133e3c177050caa118da7c"
HISTORICAL_REGISTRY_BLOB = "0d9b799181203a7cc38cd0d01ae297985c94cbbf"
DECODED_ZIP_SHA256 = "9f04dbfd0fe6c52329b9905371d33faa44b2f96719485460c6290bc8a74fd507"
ENCODED_SHA256 = "b2fe4c0122c73f104da742a12236a5e920b4e8bb7551308e45a77c458a6af28d"
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
EXPECTED_ZIP_FILES = {
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
    encoded_bundle: bytes | None = None,
    record_blob_override: str | None = None,
    historical_blob_override: str | None = None,
    **_,
) -> list[str]:
    errors: list[str] = []
    record = load(RECORD_PATH) if record is None else record
    registry = load(REGISTRY_PATH) if registry is None else registry
    encoded = BUNDLE_PATH.read_bytes() if encoded_bundle is None else encoded_bundle

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

    if git_blob_sha1_bytes(encoded) != BUNDLE_BLOB:
        errors.append("repository replay bundle git blob drift")
    if sha256(encoded) != ENCODED_SHA256:
        errors.append("repository replay bundle encoded SHA-256 drift")
    if len(encoded) != 8753:
        errors.append("repository replay bundle encoded byte length drift")

    try:
        decoded = base64.b64decode(encoded, validate=False)
    except Exception as exc:
        errors.append(f"repository replay bundle is not valid base64: {exc}")
        decoded = b""
    if len(decoded) != 6563:
        errors.append("repository replay bundle decoded byte length drift")
    if sha256(decoded) != DECODED_ZIP_SHA256:
        errors.append("repository replay bundle decoded SHA-256 drift")
    artifact = record.get("actions_artifact", {})
    if artifact.get("sha256") != sha256(decoded) or artifact.get("bytes") != len(decoded):
        errors.append("Actions artifact / repository bundle mismatch")
    if artifact.get("artifact_id") != ARTIFACT_ID or artifact.get("source_run_id") != RUN_ID or artifact.get("source_head_sha") != EXECUTION_HEAD:
        errors.append("Actions artifact provenance drift")

    files: dict[str, bytes] = {}
    if decoded:
        try:
            with zipfile.ZipFile(io.BytesIO(decoded)) as zf:
                names = set(zf.namelist())
                if names != EXPECTED_ZIP_FILES:
                    errors.append("repository replay ZIP membership drift")
                for name in names:
                    if name.endswith("/"):
                        errors.append("repository replay ZIP contains unexpected directory")
                        continue
                    files[name] = zf.read(name)
        except Exception as exc:
            errors.append(f"repository replay bundle is not a readable ZIP: {exc}")

    evidence_meta = record.get("evidence_files", {})
    if set(evidence_meta) != EXPECTED_ZIP_FILES:
        errors.append("evidence-file inventory drift")
    for name in EXPECTED_ZIP_FILES & files.keys():
        data = files[name]
        meta = evidence_meta.get(name, {})
        if meta.get("bytes") != len(data): errors.append(f"{name} byte length drift")
        if meta.get("sha256") != sha256(data): errors.append(f"{name} SHA-256 drift")
        if meta.get("git_blob_sha1") != git_blob_sha1_bytes(data): errors.append(f"{name} Git blob drift")

    if "evidence-summary.json" in files:
        try:
            summary = json.loads(files["evidence-summary.json"].decode("utf-8"))
            execution = summary.get("execution", {})
            if execution.get("mathcert_head_sha") != EXECUTION_HEAD or execution.get("workflow_checkout_sha") != WORKFLOW_CHECKOUT:
                errors.append("evidence summary execution identity drift")
            targets = summary.get("targets", {})
            if targets.get("theorem_names") != TARGETS or targets.get("nonvacuity_witnesses") != WITNESSES:
                errors.append("evidence summary target/witness drift")
            results = summary.get("results", {})
            if results != {
                "solution_build":"pass","challenge_build":"pass","comparator":"pass","lean_kernel":"accept","nanoda":"accept","nonvacuity_replay":"pass","theorem_axiom_report":"permitted_only","trust_boundary_scan":"clear","semantic_concordance":"protected_predecessor_reconfirmed"
            }:
                errors.append("evidence summary replay-result drift")
            projection = summary.get("source_projection", {})
            if projection != {
                "formula_target_count":2,"circuit_target_count":0,"coefficient_field":"complex","dimension_threshold":32,"log_base":2,"division_free_variable_leaf_constant":128,"rational_variable_leaf_constant":192,"gate_bounds_in_replay":False,"total_leaves_vertices_in_replay":False,"historical_pdf_byte_equivalence":False
            }:
                errors.append("evidence summary source projection drift")
            route = summary.get("route_state", {})
            if route != {
                "requested_future_route_id":"MC-ROUTE-OTP-C-PERMANENT-FORMULA","proposed_route_record":None,"registered_route":None,"may_adjudicate":False,"cert_output":None,"mathematical_target_proved":False,"may_promote_claim":False
            }:
                errors.append("evidence summary route/proof authority inflation")
        except Exception as exc:
            errors.append(f"invalid evidence summary: {exc}")

    if "axiom-check.json" in files:
        try:
            ax = json.loads(files["axiom-check.json"].decode("utf-8"))
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

    if "comparator.log" in files:
        text = files["comparator.log"].decode("utf-8", errors="replace")
        for marker in ["Nanoda kernel accepts the solution", "Lean default kernel accepts the solution", "Your solution is okay!"]:
            if marker not in text: errors.append(f"Comparator acceptance marker missing: {marker}")
    if "trust-boundary-scan.txt" in files:
        text = files["trust-boundary-scan.txt"].decode("utf-8", errors="replace")
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
    review = record.get("review_state", {})
    if review != {"specialist_review_required":True,"status":"pending_exact_head_non_author_review"}:
        errors.append("specialist review state drift")

    routes = load(ROUTE_REGISTRY_PATH).get("routes", [])
    if any(r.get("route_id") == "MC-ROUTE-OTP-C-PERMANENT-FORMULA" for r in routes):
        errors.append("Permanent route registered before replay-evidence admission")

    reg_state = registry.get("execution_state", {})
    if reg_state != {"authorized_target_count":2,"circuit_target_count":0,"replay_evidence_bundle_count":1,"specialist_review_count":0,"route_proposal_count":0,"registered_route_count":0,"adjudication_count":0,"cert_output_count":0,"mathematical_target_proved_count":0}:
        errors.append("successor replay-evidence registry state inflation")
    if registry.get("route_controls") != {"requested_future_route":"MC-ROUTE-OTP-C-PERMANENT-FORMULA","route_proposal_created":False,"route_registration_created":False,"may_adjudicate":False,"may_promote_claim":False,"aggregate_route_prohibited":True}:
        errors.append("successor replay-evidence route controls drift")

    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("validated Permanent exact-family replay evidence; repository bundle matches successful Actions artifact; historical three-family evidence preserved; no route, adjudication, output, proof, circuit, gate, total-size, PDF-equivalence, or aggregate authority created")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
