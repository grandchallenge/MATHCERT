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
BASE_COMMIT = "2270241c9715287bd306cc0e6eaf962ccab33541"
SOURCE_PATH = "ci/validate_formal_target_certificates.py"
CERT_DIR = ROOT / "certificates" / "formal_sources"
SCHEMA_PATH = ROOT / "schemas" / "formal_target_certificate.schema.json"
REGISTRY_PATH = ROOT / "governance" / "certification_routes.json"
FULL_FORMULA_SCHEMA_PATH = ROOT / "schemas" / "otp_permanent_full_formula_qualified_output.schema.json"
FULL_FORMULA_ROUTE_PATH = ROOT / "governance" / "certification_route_overlays" / "OTP-C-PERMANENT-FULL-FORMULA.json"

FULL_FORMULA_FILE = "MC-OTP-C-PERMANENT-FULL-FORMULA-001.json"
FULL_FORMULA_BLOB = "2940f551805794b96c7b0793bfe0d14e9fcd9954"
FULL_FORMULA_CONTENT_COMMIT = "1abf088387cbfc33a17fb34e99d23437a6b56164"
FULL_FORMULA_ROUTE_ID = "MC-ROUTE-OTP-C-PERMANENT-FULL-FORMULA"
FULL_FORMULA_ROUTE_BLOB = "3a208d3391514de74853f4ad182e26c74f631913"
GLOBAL_REGISTRY_BLOB = "2d17473b4731aa9d9c630b1e7777ad4bd794d993"
FULL_FORMULA_TARGETS = [
    "PermanentFormulaLowerBound.permanent_divisionFree_formula_lower_bound",
    "PermanentFormulaLowerBound.permanent_rational_formula_lower_bound",
]
FULL_FORMULA_OUTPUT = {
    "repository": "grandchallenge/MATHCERT",
    "commit_sha": FULL_FORMULA_CONTENT_COMMIT,
    "path": f"certificates/formal_sources/{FULL_FORMULA_FILE}",
    "digest_algorithm": "git_blob_sha1",
    "digest": FULL_FORMULA_BLOB,
}
FULL_FORMULA_PROJECTION = {
    "coefficient_field": "complex",
    "dimension_threshold": 32,
    "log_base": 2,
    "division_free": {
        "variable_leaves": 128,
        "total_leaves": 128,
        "vertices": 128,
        "internal_gates": 256,
    },
    "rational": {
        "variable_leaves": 192,
        "total_leaves": 192,
        "vertices": 192,
        "internal_gates": 384,
    },
    "formula_target_count": 2,
    "circuit_target_count": 0,
}


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
            raise RuntimeError("unable to unshallow predecessor formal-certificate history")
    if git("cat-file", "-e", f"{BASE_COMMIT}^{{commit}}").returncode != 0:
        result = git("fetch", "--no-tags", "origin", BASE_COMMIT)
        if result.returncode != 0:
            raise RuntimeError("unable to fetch predecessor formal-certificate validator")
    result = git("show", f"{BASE_COMMIT}:{SOURCE_PATH}")
    if result.returncode != 0:
        raise RuntimeError("unable to read predecessor formal-certificate validator")
    module = types.ModuleType("pre_full_formula_formal_target_certificates")
    module.__file__ = str(ROOT / SOURCE_PATH)
    exec(compile(result.stdout.decode("utf-8"), module.__file__, "exec"), module.__dict__)
    return module


def _full_formula_certificate_errors(path: Path, schema_path: Path) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"missing formal target certificate: {FULL_FORMULA_FILE}"]
    data = load_json(path)
    schema = load_json(schema_path)
    if schema.get("additionalProperties") is not False:
        errors.append("OTP-C-PERMANENT-FULL-FORMULA: qualification schema must remain closed")
    errors.extend(
        f"{path}: OTP-C-PERMANENT-FULL-FORMULA schema violation: {error.message}"
        for error in Draft202012Validator(schema).iter_errors(data)
    )
    if git_blob(path) != FULL_FORMULA_BLOB:
        errors.append(f"{path}: certificate blob identity drift")
    if data.get("certificate_id") != "MC-OTP-C-PERMANENT-FULL-FORMULA-QUAL-001":
        errors.append(f"{path}: certificate identity drift")
    if data.get("result_family") != "OTP-C-PERMANENT" or data.get("surface_id") != "OTP-C-PERMANENT-FULL-FORMULA":
        errors.append(f"{path}: family/surface identity drift")
    if data.get("route_id") != FULL_FORMULA_ROUTE_ID:
        errors.append(f"{path}: route identity drift")
    if data.get("encoded_targets") != FULL_FORMULA_TARGETS:
        errors.append(f"{path}: encoded target scope drift")
    qualification = data.get("qualification", {})
    if qualification.get("disposition") != "qualified_encoded_targets_only":
        errors.append(f"{path}: disposition inflation")
    if qualification.get("source_projection") != FULL_FORMULA_PROJECTION:
        errors.append(f"{path}: full-formula projection or scope inflation")
    if data.get("source_authority") != {
        "adjudication": {
            "path": "governance/result_family_adjudications/OTP-C-PERMANENT-FULL-FORMULA.json",
            "digest_algorithm": "git_blob_sha1",
            "digest": "2b5f0cd02b53365a8504a325594a7fc366682db0",
            "disposition": "adjudication_clear_encoded_targets_only",
        },
        "output_contract": {
            "path": "governance/result_family_output_contract_successors/OTP-C-PERMANENT-FULL-FORMULA.json",
            "digest_algorithm": "git_blob_sha1",
            "digest": "e234a4bcf55353ed6519e54a41d479b51d93c82c",
        },
        "forge_semantic_blob": "520bdaa3bba075e411f7a0a2b8422e9c9d42c818",
        "solve_packet_blob": "8755a1067963e5b46555872cb46025fff2625295",
        "overlay_json_blob": "ad102cacd81736f154437826ddefff1cef648f13",
        "overlay_lean_blob": "8846ebdbae05e31d7d69f0e751a677e927023e48",
        "nonvacuity_witness_blob": "e756c8476bac1795f3fb8ca0b7235d3a4a5c59ea",
    }:
        errors.append(f"{path}: protected source authority drift")
    if data.get("state") != {
        "route_state": "qualified",
        "cert_output_inserted": True,
        "mathematical_target_proved": False,
        "may_promote_claim": False,
        "circuit_targets_certified": False,
        "aggregate_output": False,
    }:
        errors.append(f"{path}: state inflation")
    if data.get("preserved_limitations") != {
        "historical_variable_leaf_certificate_mutated": False,
        "circuit_targets_in_scope": False,
        "historical_pdf_byte_equivalence": "not_established",
        "unrestricted_source_theorem_proof_claim": False,
        "other_family_outputs_authorized": False,
        "aggregate_openai_ten_proofs_authority": False,
    }:
        errors.append(f"{path}: limitation inflation")
    return errors


def _full_formula_route_errors(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return ["OTP-C-PERMANENT-FULL-FORMULA: missing qualified successor route overlay"]
    route_overlay = load_json(path)
    if git_blob(path) != FULL_FORMULA_ROUTE_BLOB:
        errors.append("OTP-C-PERMANENT-FULL-FORMULA: qualified route overlay blob drift")
    if route_overlay.get("overlay_id") != "MC-ROUTE-OVERLAY-OTP-C-PERMANENT-FULL-FORMULA":
        errors.append("OTP-C-PERMANENT-FULL-FORMULA: route overlay identity drift")
    if route_overlay.get("base_registry") != {
        "path": "governance/certification_routes.json",
        "digest_algorithm": "git_blob_sha1",
        "digest": GLOBAL_REGISTRY_BLOB,
    }:
        errors.append("OTP-C-PERMANENT-FULL-FORMULA: base registry identity drift")
    route = route_overlay.get("route", {})
    if route.get("route_id") != FULL_FORMULA_ROUTE_ID or route.get("campaign_id") != "OTP-C-PERMANENT-FULL-FORMULA":
        errors.append("OTP-C-PERMANENT-FULL-FORMULA: route identity drift")
    if route.get("intake_status") != "qualified":
        errors.append("OTP-C-PERMANENT-FULL-FORMULA: route is not qualified")
    if route.get("target_claim_ids") != FULL_FORMULA_TARGETS:
        errors.append("OTP-C-PERMANENT-FULL-FORMULA: route target scope drift")
    if route.get("cert_output") != FULL_FORMULA_OUTPUT:
        errors.append("OTP-C-PERMANENT-FULL-FORMULA: route output identity drift")
    if route.get("mathematical_target_proved") is not False or route.get("aggregate_output") is not False:
        errors.append("OTP-C-PERMANENT-FULL-FORMULA: route authority inflation")
    if route_overlay.get("preserved_predecessor") != {
        "route_id": "MC-ROUTE-OTP-C-PERMANENT-FORMULA",
        "certificate_id": "MC-OTP-C-PERMANENT-QUAL-001",
        "mutable": False,
    }:
        errors.append("OTP-C-PERMANENT-FULL-FORMULA: predecessor preservation drift")
    return errors


def certificate_errors(
    directory: Path = CERT_DIR,
    schema_path: Path = SCHEMA_PATH,
    registry_path: Path = REGISTRY_PATH,
    root: Path = ROOT,
    full_formula_schema_path: Path = FULL_FORMULA_SCHEMA_PATH,
    full_formula_route_path: Path = FULL_FORMULA_ROUTE_PATH,
) -> list[str]:
    errors: list[str] = []
    try:
        base = protected_module()
    except RuntimeError as exc:
        return [str(exc)]

    # Replay the entire predecessor validator against exactly the predecessor
    # certificate surface. The new full-formula certificate is admitted only
    # by the bounded successor checks below; all historical checks stay intact.
    with tempfile.TemporaryDirectory() as temporary:
        predecessor_dir = Path(temporary)
        for source in directory.glob("*.json"):
            if source.name != FULL_FORMULA_FILE:
                shutil.copyfile(source, predecessor_dir / source.name)
        errors.extend(
            base.certificate_errors(
                directory=predecessor_dir,
                schema_path=schema_path,
                registry_path=registry_path,
                root=root,
            )
        )

    expected = set(base.LEGACY_FILES) | {
        base.EHRHART_FILE,
        base.PERMANENT_FILE,
        base.COMPACTNESS_FILE,
        base.J2_FILE,
        FULL_FORMULA_FILE,
    }
    actual = {path.name for path in directory.glob("*.json")}
    for missing in sorted(expected - actual):
        errors.append(f"missing formal target certificate: {missing}")
    for unknown in sorted(actual - expected):
        errors.append(f"unregistered formal target certificate: {unknown}")

    errors.extend(_full_formula_certificate_errors(directory / FULL_FORMULA_FILE, full_formula_schema_path))
    errors.extend(_full_formula_route_errors(full_formula_route_path))
    return errors


def main() -> int:
    errors = certificate_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"formal target certificate validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print(
        "validated protected predecessor certificates plus exact restricted "
        "OTP-C-PERMANENT-FULL-FORMULA qualified successor output"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
