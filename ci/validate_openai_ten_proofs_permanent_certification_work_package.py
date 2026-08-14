#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
RECORD_PATH = ROOT / "governance/result_family_work_package_successors/OTP-C-PERMANENT-CERT-WP01.json"
REGISTRY_PATH = ROOT / "governance/pre_route_candidates/OPENAI_TEN_PROOFS_WP02A_PERMANENT_WORK_PACKAGE.json"
HISTORICAL_REGISTRY_PATH = ROOT / "governance/pre_route_candidates/OPENAI_TEN_PROOFS_WP02_WORK_PACKAGES.json"
ROUTE_REGISTRY_PATH = ROOT / "governance/certification_routes.json"
RECORD_SCHEMA_PATH = ROOT / "schemas/openai_ten_proofs_permanent_certification_work_package.schema.json"
REGISTRY_SCHEMA_PATH = ROOT / "schemas/openai_ten_proofs_permanent_certification_work_package_registry.schema.json"

HISTORICAL_REGISTRY_BLOB = "997f38fb60ef4d3a43801916113a8e2f1ae34264"
RECORD_BLOB = "f3000340c2699ec819acbcd223c1ee4c63af1cc8"
TARGETS = [
    "PermanentFormulaLowerBound.permanent_divisionFree_formula_logarithmic_lower_bound",
    "PermanentFormulaLowerBound.permanent_rational_formula_logarithmic_lower_bound",
]
WITNESSES = [
    "PermanentFormulaLowerBound.Nonvacuity.permanent_divisionFree_formula_nonvacuous",
    "PermanentFormulaLowerBound.Nonvacuity.permanent_rational_formula_nonvacuous",
]
TOOLCHAIN = {
    "lean": "leanprover/lean4:v4.32.0",
    "comparator_commit": "07bc4ea40f2266dcb861820a2ec1fa3244ed307f",
    "mathlib_commit": "81a5d257c8e410db227a6665ed08f64fea08e997",
    "lean4export_commit": "4e7915201d3f9f04470d9eae002fa695f7cdc589",
    "lean4checker_commit": "b7398199245524275543dec6113229c9bb4902e5",
    "nanoda_commit": "ddfac2bf5a7b56cb46e141494427ff3dd55963c7",
    "landrun_commit": "811cfff51ceaf3d9843708aa6d22e9b84ccac8b4",
    "checkout_action_commit": "3d3c42e5aac5ba805825da76410c181273ba90b1",
    "lean_action_commit": "138a564e38a62ce545e8d47d86a97628463aced4",
}
PROJECTION = {
    "formula_target_count": 2,
    "circuit_target_count": 0,
    "coefficient_field": "complex",
    "dimension_threshold": 32,
    "log_base": 2,
    "division_free_variable_leaf_constant": 128,
    "division_free_source_gate_constant": 256,
    "rational_variable_leaf_constant": 192,
    "rational_source_gate_constant": 384,
    "gate_bounds_in_work_package": False,
    "total_leaves_vertices_in_work_package": False,
    "historical_pdf_byte_equivalence": False,
}
ZERO_STATE = {
    "authorized_work_package_count_in_this_successor": 1,
    "executing_count": 0,
    "evidence_bundle_count": 0,
    "proposed_route_count": 0,
    "registered_route_count_created_by_this_operation": 0,
    "adjudication_count": 0,
    "cert_output_count": 0,
    "mathematical_target_proved_count": 0,
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data, usedforsecurity=False).hexdigest()


def schema_errors(instance, schema_path: Path, label: str) -> list[str]:
    schema = load(schema_path)
    validator = Draft202012Validator(schema)
    return [f"{label} schema: {err.message}" for err in sorted(validator.iter_errors(instance), key=lambda e: list(e.path))]


def historical_work_package_errors() -> list[str]:
    spec = importlib.util.spec_from_file_location(
        "historical_work_packages", ROOT / "ci/validate_openai_ten_proofs_certification_work_packages.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validation_errors()


def route_registration_errors() -> list[str]:
    spec = importlib.util.spec_from_file_location(
        "route_registrations", ROOT / "ci/validate_openai_ten_proofs_route_registrations.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validation_errors()


def validation_errors(record=None, registry=None, record_blob_override=None, historical_blob_override=None, **_) -> list[str]:
    errors: list[str] = []
    record = load(RECORD_PATH) if record is None else record
    registry = load(REGISTRY_PATH) if registry is None else registry

    errors.extend(schema_errors(record, RECORD_SCHEMA_PATH, "Permanent work package"))
    errors.extend(schema_errors(registry, REGISTRY_SCHEMA_PATH, "Permanent work-package registry"))

    historical_blob = git_blob_sha1(HISTORICAL_REGISTRY_PATH) if historical_blob_override is None else historical_blob_override
    if historical_blob != HISTORICAL_REGISTRY_BLOB:
        errors.append("historical three-family work-package registry blob drift")
    historical_registry = load(HISTORICAL_REGISTRY_PATH)
    historical_families = [x.get("result_family") for x in historical_registry.get("work_packages", [])]
    if historical_families != ["OTP-F-EHRHART", "OTP-J1-COMPACTNESS", "OTP-J2-TWO-DEGENERATE"]:
        errors.append("historical three-family work-package membership drift")

    if historical_work_package_errors():
        errors.append("historical three-family work-package validation failed")
    if route_registration_errors():
        errors.append("pre-existing route-registration authority invalid")

    authority = record.get("authority", {})
    review = authority.get("cert_intake_review", {})
    intake = authority.get("intake_record", {})
    if authority.get("cert_intake_merge") != "59e678a5692c873cb7b12b8913231bf520571f51": errors.append("Permanent intake merge drift")
    if authority.get("cert_intake_reviewed_head") != "41d66d1c12c667059e5942e0f858056c4e8cf8fc": errors.append("Permanent intake reviewed-head drift")
    if review != {"review_id":4941544685,"reviewer":"jimsteeg","state":"APPROVED","submitted_at":"2026-08-14T22:08:17Z"}: errors.append("Permanent intake review drift")
    if authority.get("cert_intake_disposition_comment") != 5298682910: errors.append("Permanent intake disposition drift")
    if intake.get("digest") != "80a9cf59ac4bad7cc08185e80b0d9ffe27b855e6": errors.append("Permanent intake record digest drift")
    if authority.get("solve_handoff_merge") != "90f8a8544e546a603b34c9b27b2d6a4a68e06de8": errors.append("Solve handoff merge drift")
    if authority.get("producer_packet", {}).get("digest") != "a993c530880021930a2b468e76235b91122ca854": errors.append("producer packet digest drift")
    if authority.get("forge_semantic_merge") != "60f6e06c957139447bf5943eed731941b22ac608": errors.append("Forge semantic merge drift")
    if authority.get("semantic_record", {}).get("digest") != "3e04bd16bd8a91eaf9b6702de89fcdcc72f61099": errors.append("semantic record digest drift")
    if authority.get("nonvacuity_witness", {}).get("digest") != "e756c8476bac1795f3fb8ca0b7235d3a4a5c59ea": errors.append("nonvacuity witness digest drift")
    official = authority.get("official_subject", {})
    if official.get("commit") != "e62211d28e3a9131950c89caa6542cfe5eff3bca" or official.get("tree") != "2f8e7ac5ae7f157b6b1de636c2c343b1c7a7e365": errors.append("protected Lean subject drift")
    if official.get("archive_sha256") != "3022e62ffbed8f5f74d232034a703dc645e6b301879dff1e87df72979914294f" or official.get("archive_bytes") != 21022720: errors.append("protected archive identity drift")
    if official.get("lake_manifest_git_blob_sha1") != "6b9fc4f8f8f7fc389016af602b459ea916e52904": errors.append("locked manifest identity drift")

    if record.get("toolchain") != TOOLCHAIN: errors.append("Permanent replay toolchain drift")
    execution = record.get("execution", {})
    if execution.get("allowed") is not True or execution.get("isolated_family_replay_required") is not True or execution.get("clean_room_environment_required") is not True or execution.get("aggregate_import_required") is not False: errors.append("Permanent execution controls drift")
    if execution.get("comparator_config") != "ComparatorChallenges/C_PermanentFormulaLowerBound.json" or execution.get("solution_module") != "Permanent" or execution.get("challenge_module") != "ComparatorChallenges.C_PermanentFormulaLowerBound": errors.append("Permanent Comparator surface drift")
    if execution.get("specialist_review_required") is not True: errors.append("specialist review requirement removed")

    scope = record.get("target_scope", {})
    if scope.get("lean_theorems") != TARGETS: errors.append("Permanent target membership/order drift")
    if scope.get("nonvacuity_witnesses") != WITNESSES: errors.append("Permanent nonvacuity witness drift")
    if scope.get("source_projection") != PROJECTION: errors.append("Permanent source projection drift")

    route = record.get("route_state", {})
    if route != {
        "requested_route_id":"MC-ROUTE-OTP-C-PERMANENT-FORMULA",
        "certification_route_registry_entry":None,
        "proposed_route_record":None,
        "cert_output":None,
        "may_register_route_on_branch":False,
        "may_adjudicate":False,
        "mathematical_target_proved":False,
        "may_promote_claim":False,
    }: errors.append("Permanent work-package route state inflation")
    controls = record.get("route_controls", {})
    expected_controls = {
        "result_family_subset_only":True,
        "may_create_aggregate_work_package":False,
        "may_create_aggregate_route":False,
        "may_imply_certification":False,
        "may_imply_proof":False,
        "may_include_circuit_target":False,
        "may_include_gate_bounds":False,
        "may_include_total_size_consequences":False,
    }
    if controls != expected_controls: errors.append("Permanent work-package authority controls drift")

    actual_record_blob = git_blob_sha1(RECORD_PATH) if record_blob_override is None else record_blob_override
    if actual_record_blob != RECORD_BLOB: errors.append("Permanent work-package record blob drift")
    registry_wp = registry.get("work_package", {})
    if registry_wp.get("digest") != actual_record_blob: errors.append("successor registry/work-package digest mismatch")
    if registry_wp.get("path") != "governance/result_family_work_package_successors/OTP-C-PERMANENT-CERT-WP01.json": errors.append("successor work-package path drift")
    if registry.get("historical_three_family_registry", {}).get("git_blob_sha1") != HISTORICAL_REGISTRY_BLOB: errors.append("successor historical-registry pin drift")
    if registry.get("execution_state") != ZERO_STATE: errors.append("Permanent successor execution state inflation")
    if registry.get("scope") != {"formula_target_count":2,"circuit_target_count":0,"gate_bounds_in_work_package":False,"total_leaves_vertices_in_work_package":False,"historical_pdf_byte_equivalence":False}: errors.append("Permanent successor scope drift")
    if registry.get("aggregate_integration") != {"all_lean_required":False,"creates_aggregate_work_package":False,"creates_aggregate_route":False,"reopens_other_family_replay":False}: errors.append("Permanent aggregate integration inflation")
    if registry.get("route_controls") != {"global_certification_route_registry_modified":False,"requested_future_route":"MC-ROUTE-OTP-C-PERMANENT-FORMULA","route_proposal_created":False,"route_registration_created":False,"may_adjudicate":False,"may_promote_claim":False}: errors.append("Permanent successor route authority inflation")

    routes = load(ROUTE_REGISTRY_PATH).get("routes", [])
    if any(r.get("route_id") == "MC-ROUTE-OTP-C-PERMANENT-FORMULA" for r in routes):
        errors.append("Permanent route registered prematurely")

    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("validated bounded Permanent certification work package; historical three-family work packages preserved; no replay evidence, route, adjudication, output, or proof authority created")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
