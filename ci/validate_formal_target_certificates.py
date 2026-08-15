#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import types
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
BASE_COMMIT = "64e042ddb1147338ad7868a2847715fe7c1c079d"
SOURCE_PATH = "ci/validate_formal_target_certificates.py"
CERT_DIR = ROOT / "certificates" / "formal_sources"
SCHEMA_PATH = ROOT / "schemas" / "formal_target_certificate.schema.json"
EHRHART_SCHEMA_PATH = ROOT / "schemas" / "otp_ehrhart_qualified_output.schema.json"
PERMANENT_SCHEMA_PATH = ROOT / "schemas" / "otp_permanent_qualified_output.schema.json"
COMPACTNESS_SCHEMA_PATH = ROOT / "schemas" / "otp_compactness_qualified_output.schema.json"
REGISTRY_PATH = ROOT / "governance" / "certification_routes.json"
EHRHART_FILE = "MC-OTP-F-EHRHART-001.json"
EHRHART_BLOB = "27a855c949b67e71372c7f0d6601d80125d33968"
EHRHART_CONTENT_COMMIT = "24d99cbdcd6da33ae2404c0f6034d503498d9a4b"
EHRHART_TARGETS = [
    "Ehrhart.Volume.ehrhart_volume_inequality_for_sets",
    "Ehrhart.SimplexVolume.exists_centeredBody_sharp",
    "Ehrhart.SimplexVolume.barycenter_centeredSimplex",
    "Ehrhart.SimplexVolume.normalizedVolume_centeredSimplex",
]
PERMANENT_FILE = "MC-OTP-C-PERMANENT-001.json"
PERMANENT_BLOB = "ad10c427270cb1c747ebcacbc5c37e4c1ed1df04"
PERMANENT_CONTENT_COMMIT = "1344220f0f61f9e637c5b1fc668c0a0eb7ab4133"
PERMANENT_TARGETS = [
    "PermanentFormulaLowerBound.permanent_divisionFree_formula_logarithmic_lower_bound",
    "PermanentFormulaLowerBound.permanent_rational_formula_logarithmic_lower_bound",
]
COMPACTNESS_FILE = "MC-OTP-J1-COMPACTNESS-001.json"
COMPACTNESS_BLOB = "88531e28951854961e86eec0517356999a391759"
COMPACTNESS_CONTENT_COMMIT = "9fba5a8e918028ecc2b4d72abc00b3b72a5194f5"
COMPACTNESS_TARGETS = [
    "CompactnessConjecture.quantitativeCompactnessCounterexample",
    "CompactnessConjecture.compactnessCounterexample_bigO",
    "CompactnessConjecture.not_erdos_180",
]
LEGACY_FILES = {"MC-FC-WP00-RH-001.json", "MC-FC-WP00-NS-CI-001.json"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(data)}\0".encode("ascii") + data,
        usedforsecurity=False,
    ).hexdigest()


def git(*args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args], cwd=ROOT, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=False,
    )


def protected_module() -> types.ModuleType:
    shallow = git("rev-parse", "--is-shallow-repository")
    if shallow.returncode == 0 and shallow.stdout.decode().strip() == "true":
        result = git("fetch", "--no-tags", "--unshallow", "origin")
        if result.returncode != 0:
            raise RuntimeError("unable to unshallow formal-certificate history")
    if git("cat-file", "-e", f"{BASE_COMMIT}^{{commit}}").returncode != 0:
        result = git("fetch", "--no-tags", "origin", BASE_COMMIT)
        if result.returncode != 0:
            raise RuntimeError("unable to fetch protected formal-certificate validator")
    result = git("show", f"{BASE_COMMIT}:{SOURCE_PATH}")
    if result.returncode != 0:
        raise RuntimeError("unable to read protected formal-certificate validator")
    module = types.ModuleType("protected_formal_target_certificates")
    module.__file__ = str(ROOT / SOURCE_PATH)
    exec(compile(result.stdout.decode("utf-8"), module.__file__, "exec"), module.__dict__)
    return module


def _restricted_output_errors(
    *,
    path: Path,
    schema_path: Path,
    expected_blob: str,
    certificate_id: str,
    result_family: str,
    route_id: str,
    targets: list[str],
) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return errors
    data = load_json(path)
    schema = load_json(schema_path)
    if schema.get("additionalProperties") is not False:
        errors.append(f"{result_family}: qualification schema must remain closed")
    errors.extend(
        f"{path}: {result_family} schema violation: {error.message}"
        for error in Draft202012Validator(schema).iter_errors(data)
    )
    if git_blob(path) != expected_blob:
        errors.append(f"{path}: certificate blob identity drift")
    if data.get("certificate_id") != certificate_id:
        errors.append(f"{path}: certificate identity drift")
    if data.get("result_family") != result_family or data.get("route_id") != route_id:
        errors.append(f"{path}: family/route identity drift")
    if data.get("encoded_targets") != targets:
        errors.append(f"{path}: encoded target scope drift")
    qualification = data.get("qualification", {})
    if qualification.get("disposition") != "qualified_encoded_targets_only":
        errors.append(f"{path}: disposition inflation")
    state = data.get("state", {})
    if state.get("mathematical_target_proved") is not False:
        errors.append(f"{path}: mathematical target must remain unproved")
    if state.get("may_promote_claim") is not False or state.get("aggregate_output") is not False:
        errors.append(f"{path}: state inflation")
    return errors


def certificate_errors(
    directory: Path = CERT_DIR,
    schema_path: Path = SCHEMA_PATH,
    registry_path: Path = REGISTRY_PATH,
    root: Path = ROOT,
    ehrhart_schema_path: Path = EHRHART_SCHEMA_PATH,
    permanent_schema_path: Path = PERMANENT_SCHEMA_PATH,
    compactness_schema_path: Path = COMPACTNESS_SCHEMA_PATH,
) -> list[str]:
    errors: list[str] = []
    try:
        base = protected_module()
    except RuntimeError as exc:
        return [str(exc)]

    with tempfile.TemporaryDirectory() as temporary:
        legacy_dir = Path(temporary)
        for name in LEGACY_FILES:
            source = directory / name
            if source.exists():
                shutil.copyfile(source, legacy_dir / name)
        errors.extend(
            base.certificate_errors(
                directory=legacy_dir,
                schema_path=schema_path,
                registry_path=registry_path,
                root=root,
            )
        )

    actual = {path.name for path in directory.glob("*.json")}
    expected = LEGACY_FILES | {EHRHART_FILE, PERMANENT_FILE, COMPACTNESS_FILE}
    for missing in sorted(expected - actual):
        errors.append(f"missing formal target certificate: {missing}")
    for unknown in sorted(actual - expected):
        errors.append(f"unregistered formal target certificate: {unknown}")

    ehrhart_path = directory / EHRHART_FILE
    errors.extend(
        _restricted_output_errors(
            path=ehrhart_path,
            schema_path=ehrhart_schema_path,
            expected_blob=EHRHART_BLOB,
            certificate_id="MC-OTP-F-EHRHART-QUAL-001",
            result_family="OTP-F-EHRHART",
            route_id="MC-ROUTE-OTP-F-EHRHART",
            targets=EHRHART_TARGETS,
        )
    )
    if ehrhart_path.exists():
        ehrhart = load_json(ehrhart_path)
        qualification = ehrhart.get("qualification", {})
        if qualification.get("source_theorem_mathematically_proved") is not False:
            errors.append(f"{ehrhart_path}: mathematical target must remain unproved")
        if qualification.get("equality_case_classification") != "excluded":
            errors.append(f"{ehrhart_path}: equality-case inflation")
        if ehrhart.get("state") != {
            "route_state": "qualified",
            "cert_output_inserted": True,
            "mathematical_target_proved": False,
            "may_promote_claim": False,
            "aggregate_output": False,
        }:
            errors.append(f"{ehrhart_path}: state inflation")

    permanent_path = directory / PERMANENT_FILE
    errors.extend(
        _restricted_output_errors(
            path=permanent_path,
            schema_path=permanent_schema_path,
            expected_blob=PERMANENT_BLOB,
            certificate_id="MC-OTP-C-PERMANENT-QUAL-001",
            result_family="OTP-C-PERMANENT",
            route_id="MC-ROUTE-OTP-C-PERMANENT-FORMULA",
            targets=PERMANENT_TARGETS,
        )
    )
    if permanent_path.exists():
        permanent = load_json(permanent_path)
        qualification = permanent.get("qualification", {})
        if qualification.get("source_projection") != {
            "coefficient_field": "complex",
            "dimension_threshold": 32,
            "log_base": 2,
            "division_free_variable_leaf_constant": 128,
            "rational_variable_leaf_constant": 192,
            "formula_target_count": 2,
            "circuit_target_count": 0,
        }:
            errors.append(f"{permanent_path}: source projection or scope inflation")
        limitations = permanent.get("preserved_limitations", {})
        for key in (
            "circuit_targets_in_scope", "gate_bounds_in_scope", "total_size_consequences_in_scope",
            "unrestricted_source_theorem_proof_claim", "other_family_outputs_authorized",
            "aggregate_openai_ten_proofs_authority",
        ):
            if limitations.get(key) is not False:
                errors.append(f"{permanent_path}: limitation inflated: {key}")
        if limitations.get("historical_pdf_byte_equivalence") != "not_established":
            errors.append(f"{permanent_path}: historical PDF equivalence inflated")

    compactness_path = directory / COMPACTNESS_FILE
    errors.extend(
        _restricted_output_errors(
            path=compactness_path,
            schema_path=compactness_schema_path,
            expected_blob=COMPACTNESS_BLOB,
            certificate_id="MC-OTP-J1-COMPACTNESS-QUAL-001",
            result_family="OTP-J1-COMPACTNESS",
            route_id="MC-ROUTE-OTP-J1-COMPACTNESS",
            targets=COMPACTNESS_TARGETS,
        )
    )
    if compactness_path.exists():
        compactness = load_json(compactness_path)
        if compactness.get("qualification", {}).get("source_locus") != "Chapter 10, Theorem 1.1, current official PDF P240 / printed p236":
            errors.append(f"{compactness_path}: corrected source locus drift")
        limitations = compactness.get("preserved_limitations", {})
        for key in (
            "historical_compactness_formulations_admitted", "proof_body_compared_in_full",
            "unrestricted_source_theorem_proof_claim", "other_family_outputs_authorized",
            "aggregate_openai_ten_proofs_authority",
        ):
            if limitations.get(key) is not False:
                errors.append(f"{compactness_path}: limitation inflated: {key}")
        if limitations.get("whole_document_byte_equivalence") != "not_established" or limitations.get("whole_document_semantic_equivalence") != "not_established":
            errors.append(f"{compactness_path}: whole-document equivalence inflated")

    registry = load_json(registry_path)
    ehrhart_route = next((item for item in registry.get("routes", []) if item.get("campaign_id") == "OTP-F-EHRHART"), {})
    if ehrhart_route.get("intake_status") != "qualified": errors.append("OTP-F-EHRHART: route is not qualified")
    if ehrhart_route.get("cert_output") != {"repository": "grandchallenge/MATHCERT", "commit_sha": EHRHART_CONTENT_COMMIT, "path": "certificates/formal_sources/MC-OTP-F-EHRHART-001.json", "digest_algorithm": "git_blob_sha1", "digest": EHRHART_BLOB}:
        errors.append("OTP-F-EHRHART: route output identity drift")

    permanent_route = next((item for item in registry.get("routes", []) if item.get("campaign_id") == "OTP-C-PERMANENT"), {})
    if permanent_route.get("intake_status") != "qualified": errors.append("OTP-C-PERMANENT: route is not qualified")
    if permanent_route.get("target_claim_ids") != PERMANENT_TARGETS: errors.append("OTP-C-PERMANENT: route target scope drift")
    if permanent_route.get("cert_output") != {"repository": "grandchallenge/MATHCERT", "commit_sha": PERMANENT_CONTENT_COMMIT, "path": "certificates/formal_sources/MC-OTP-C-PERMANENT-001.json", "digest_algorithm": "git_blob_sha1", "digest": PERMANENT_BLOB}:
        errors.append("OTP-C-PERMANENT: route output identity drift")

    compactness_route = next((item for item in registry.get("routes", []) if item.get("campaign_id") == "OTP-J1-COMPACTNESS"), {})
    if compactness_route.get("intake_status") != "qualified": errors.append("OTP-J1-COMPACTNESS: route is not qualified")
    if compactness_route.get("target_claim_ids") != COMPACTNESS_TARGETS: errors.append("OTP-J1-COMPACTNESS: route target scope drift")
    if compactness_route.get("cert_output") != {"repository": "grandchallenge/MATHCERT", "commit_sha": COMPACTNESS_CONTENT_COMMIT, "path": "certificates/formal_sources/MC-OTP-J1-COMPACTNESS-001.json", "digest_algorithm": "git_blob_sha1", "digest": COMPACTNESS_BLOB}:
        errors.append("OTP-J1-COMPACTNESS: route output identity drift")
    return errors


def main() -> int:
    errors = certificate_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"formal target certificate validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print("validated protected RH/NS qualifications and exact restricted OTP-F-EHRHART / OTP-C-PERMANENT / OTP-J1-COMPACTNESS outputs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
