#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
RECORD_PATH = ROOT / "governance/result_family_work_package_successors/OTP-A-SPHERE-PACKING-CERT-WP-001.json"
SCHEMA_PATH = ROOT / "schemas/openai_ten_proofs_sphere_packing_certification_work_package.schema.json"
INTAKE_PATH = ROOT / "governance/result_family_intake_successors/OTP-A-SPHERE-PACKING.json"
HISTORICAL_WORK_PACKAGES = ROOT / "governance/pre_route_candidates/OPENAI_TEN_PROOFS_WP02_WORK_PACKAGES.json"
ROUTES = ROOT / "governance/certification_routes.json"

EXPECTED_RECORD_BLOB = "f0c91d1959035f35843c383920dfba0b6c24b485"
EXPECTED_INTAKE_BLOB = "294c9f7d6cceb1cdf7ec4c8e73255dd1ba130670"
EXPECTED_HISTORICAL_WORK_PACKAGES_BLOB = "997f38fb60ef4d3a43801916113a8e2f1ae34264"
EXPECTED_ROUTES_BLOB = "2d17473b4731aa9d9c630b1e7777ad4bd794d993"
FUTURE_ROUTE_ID = "MC-ROUTE-OTP-A-SPHERE-PACKING"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(data)}\0".encode("ascii") + data,
        usedforsecurity=False,
    ).hexdigest()


def schema_errors(instance: dict) -> list[str]:
    schema = load(SCHEMA_PATH)
    validator = Draft202012Validator(schema)
    return [
        f"schema: {'/'.join(map(str, err.absolute_path)) or '<root>'}: {err.message}"
        for err in sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path))
    ]


def _import_validation(path: Path, name: str) -> list[str]:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        if hasattr(module, "validation_errors"):
            return list(module.validation_errors())
        if hasattr(module, "validate_record") and hasattr(module, "validate_repository_guards"):
            module.validate_record(module.load_record())
            module.validate_repository_guards()
            return []
        raise RuntimeError(f"unsupported validator interface: {path}")
    except Exception as exc:
        return [str(exc)]


def validation_errors(
    record: dict | None = None,
    *,
    record_blob_override: str | None = None,
    intake_blob_override: str | None = None,
    historical_blob_override: str | None = None,
    routes_blob_override: str | None = None,
) -> list[str]:
    errors: list[str] = []
    record = load(RECORD_PATH) if record is None else record
    errors.extend(schema_errors(record))

    actual_record_blob = git_blob_sha1(RECORD_PATH) if record_blob_override is None else record_blob_override
    if actual_record_blob != EXPECTED_RECORD_BLOB:
        errors.append("sphere-packing work-package record blob drift")
    intake_blob = git_blob_sha1(INTAKE_PATH) if intake_blob_override is None else intake_blob_override
    if intake_blob != EXPECTED_INTAKE_BLOB:
        errors.append("protected sphere-packing intake record drift")
    historical_blob = git_blob_sha1(HISTORICAL_WORK_PACKAGES) if historical_blob_override is None else historical_blob_override
    if historical_blob != EXPECTED_HISTORICAL_WORK_PACKAGES_BLOB:
        errors.append("historical three-family work-package registry drift")
    routes_blob = git_blob_sha1(ROUTES) if routes_blob_override is None else routes_blob_override
    if routes_blob != EXPECTED_ROUTES_BLOB:
        errors.append("certification route registry changed during work-package-only operation")

    intake_errors = _import_validation(
        ROOT / "ci/validate_openai_ten_proofs_sphere_packing_intake_successor.py",
        "sphere_packing_intake_successor",
    )
    if intake_errors:
        errors.append("protected sphere-packing intake validation failed: " + "; ".join(intake_errors))

    historical_errors = _import_validation(
        ROOT / "ci/validate_openai_ten_proofs_certification_work_packages.py",
        "historical_otp_work_packages",
    )
    if historical_errors:
        errors.append("historical three-family work-package validation failed: " + "; ".join(historical_errors))

    authority = record.get("authority", {})
    if authority.get("protected_mathcert_base") != "9d3af5503f06e1a564562a49ce9f5b439a3d9364":
        errors.append("protected MATHCERT base drift")
    if authority.get("cert_intake_merge") != "947b3bed0effa79c2472dddc37d6c463f79c3126":
        errors.append("sphere-packing intake merge drift")
    if authority.get("solve_handoff_merge") != "c19735edf4c16ac9765bb66c7209bbf11bf1312e":
        errors.append("Solve handoff merge drift")
    if authority.get("producer_packet", {}).get("digest") != "9e3b46972bf01ac3d24c6a0ae5f522799335ecd1":
        errors.append("Solve producer packet drift")
    if authority.get("forge_composite_semantic", {}).get("digest") != "b2e309ad96e750651fc7149a6bad54c6bf99015b":
        errors.append("Forge composite semantic record drift")
    if authority.get("forge_bridge_semantic", {}).get("digest") != "7858b156fc4490ecc6e3572dcf449d84dcc99f93":
        errors.append("Forge bridge semantic record drift")

    official = authority.get("official_subject", {})
    if (
        official.get("commit") != "94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6"
        or official.get("tree") != "174289e4d4958cb0509874e6e53400e098213de7"
    ):
        errors.append("official source root/tree drift")

    execution = record.get("execution_contract", {})
    if execution.get("deterministic_commands") != [
        "lake exe cache get",
        "lake build SpherePacking",
        "lake exe comparator ComparatorChallenges/A_SpherePacking.json",
    ]:
        errors.append("deterministic replay command drift")
    if execution.get("expected_outputs") != [
        "Nanoda kernel accepts the solution",
        "Lean default kernel accepts the solution",
        "Your solution is okay!",
        "OTP_SUCCESSOR_COMPARATOR=ACCEPT",
    ]:
        errors.append("expected replay-output drift")
    if execution.get("permitted_axioms") != ["propext", "Quot.sound", "Classical.choice"]:
        errors.append("permitted-axiom boundary drift")

    scope = record.get("target_scope", {})
    if scope.get("lean_theorems") != [
        "PackingBounds.FullMain.exact_limit",
        "PackingBounds.FullMain.exact_binary_exponent",
        "PackingBounds.PackingBridge.sphere_packing_sharp_asymptotic_upper",
        "PackingBounds.sharpFullCohnElkiesManuscriptConclusions",
    ]:
        errors.append("sphere-packing target membership/order drift")

    route = record.get("route_state", {})
    zero_authority = {
        "certification_route_registry_entry": None,
        "route_registered": False,
        "may_adjudicate": False,
        "adjudication": None,
        "cert_output": None,
        "mathematical_target_proved": False,
        "aggregate_authority": False,
        "may_promote_claim": False,
    }
    if any(route.get(k) != v for k, v in zero_authority.items()):
        errors.append("sphere-packing work-package route/adjudication/output/proof authority inflation")

    route_ids = [r.get("route_id") for r in load(ROUTES).get("routes", []) if isinstance(r, dict)]
    if FUTURE_ROUTE_ID in route_ids:
        errors.append("future sphere-packing route is already registered during work-package-only operation")
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(
        "OTP-A-SPHERE-PACKING executable certification work package validation: PASS; "
        "later replay only, no route/adjudication/output/proof/aggregate authority created"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
