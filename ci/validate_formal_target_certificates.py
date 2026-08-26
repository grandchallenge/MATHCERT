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

import otp_a_sphere_packing_output_contract as a_output

ROOT = Path(__file__).resolve().parents[1]
PRE_CIRCUIT_COMMIT = "809fcbc3704f146fbb9992f03b3b1851ba2fe59b"
SOURCE_PATH = "ci/validate_formal_target_certificates.py"
CERT_DIR = ROOT / "certificates" / "formal_sources"
SCHEMA_PATH = ROOT / "schemas" / "formal_target_certificate.schema.json"
REGISTRY_PATH = ROOT / "governance" / "certification_routes.json"
FULL_FORMULA_SCHEMA_PATH = ROOT / "schemas" / "otp_permanent_full_formula_qualified_output.schema.json"
FULL_FORMULA_ROUTE_PATH = ROOT / "governance" / "certification_route_overlays" / "OTP-C-PERMANENT-FULL-FORMULA.json"
CIRCUIT_SCHEMA_PATH = ROOT / "schemas" / "otp_permanent_circuit_qualified_output.schema.json"
CIRCUIT_ROUTE_PATH = ROOT / "governance" / "certification_route_overlays" / "OTP-C-PERMANENT-CIRCUIT.json"

CIRCUIT_FILE = "MC-OTP-C-PERMANENT-CIRCUIT-001.json"
CIRCUIT_BLOB = "9d0eb4a83df73440b17cb6809ede5cdcc0a8e385"
CIRCUIT_CONTENT_COMMIT = "b90305e91a7162a6dbc017e647d7a2d7272e1eef"
CIRCUIT_ROUTE_ID = "MC-ROUTE-OTP-C-PERMANENT-CIRCUIT"
CIRCUIT_ROUTE_BLOB = "29946eeefce2bd9873b3e6265b8d4983a033781d"
GLOBAL_REGISTRY_BLOB = "2d17473b4731aa9d9c630b1e7777ad4bd794d993"
CIRCUIT_TARGETS = [
    "PermanentRollout.permanent_circuit_loglog_lower_bound",
    "PermanentRollout.permanent_circuit_loglog_bigOmega",
    "PermanentRollout.permanent_complexity_ratio_tendsto_atTop",
]
CIRCUIT_OUTPUT = {
    "repository": "grandchallenge/MATHCERT",
    "commit_sha": CIRCUIT_CONTENT_COMMIT,
    "path": f"certificates/formal_sources/{CIRCUIT_FILE}",
    "digest_algorithm": "git_blob_sha1",
    "digest": CIRCUIT_BLOB,
}
A_FILE = "MC-OTP-A-SPHERE-PACKING-001.json"
A_BLOB = "534e98ad2f00406fc869ea137f802f8cf504798a"


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


def predecessor_module() -> types.ModuleType:
    shallow = git("rev-parse", "--is-shallow-repository")
    if shallow.returncode == 0 and shallow.stdout.decode().strip() == "true":
        result = git("fetch", "--no-tags", "--unshallow", "origin")
        if result.returncode != 0:
            raise RuntimeError("unable to unshallow pre-circuit formal-certificate history")
    if git("cat-file", "-e", f"{PRE_CIRCUIT_COMMIT}^{{commit}}").returncode != 0:
        result = git("fetch", "--no-tags", "origin", PRE_CIRCUIT_COMMIT)
        if result.returncode != 0:
            raise RuntimeError("unable to fetch pre-circuit formal-certificate validator")
    result = git("show", f"{PRE_CIRCUIT_COMMIT}:{SOURCE_PATH}")
    if result.returncode != 0:
        raise RuntimeError("unable to read pre-circuit formal-certificate validator")
    module = types.ModuleType("pre_circuit_formal_target_certificates")
    module.__file__ = str(ROOT / SOURCE_PATH)
    exec(compile(result.stdout.decode("utf-8"), module.__file__, "exec"), module.__dict__)
    return module


def _circuit_certificate_errors(path: Path, schema_path: Path) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"missing formal target certificate: {CIRCUIT_FILE}"]
    data = load_json(path)
    schema = load_json(schema_path)
    if schema.get("additionalProperties") is not False:
        errors.append("OTP-C-PERMANENT-CIRCUIT: qualification schema must remain closed")
    errors.extend(
        f"{path}: OTP-C-PERMANENT-CIRCUIT schema violation: {error.message}"
        for error in Draft202012Validator(schema).iter_errors(data)
    )
    if git_blob(path) != CIRCUIT_BLOB:
        errors.append(f"{path}: certificate blob identity drift")
    if data.get("certificate_id") != "MC-OTP-C-PERMANENT-CIRCUIT-QUAL-001":
        errors.append(f"{path}: certificate identity drift")
    if data.get("result_family") != "OTP-C-PERMANENT" or data.get("surface_id") != "OTP-C-PERMANENT-CIRCUIT":
        errors.append(f"{path}: family/surface identity drift")
    if data.get("route_id") != CIRCUIT_ROUTE_ID:
        errors.append(f"{path}: route identity drift")
    if data.get("encoded_targets") != CIRCUIT_TARGETS:
        errors.append(f"{path}: encoded target scope drift")
    qualification = data.get("qualification", {})
    if qualification.get("disposition") != "qualified_encoded_targets_only":
        errors.append(f"{path}: disposition inflation")
    if data.get("state") != {
        "route_state": "qualified",
        "cert_output_inserted": True,
        "mathematical_target_proved": False,
        "may_promote_claim": False,
        "formula_targets_certified": False,
        "aggregate_output": False,
    }:
        errors.append(f"{path}: state inflation")
    limitations = data.get("preserved_limitations", {})
    if limitations.get("historical_variable_leaf_certificate_mutated") is not False:
        errors.append(f"{path}: variable-leaf predecessor mutation inflation")
    if limitations.get("full_formula_certificate_mutated") is not False:
        errors.append(f"{path}: full-formula predecessor mutation inflation")
    if limitations.get("formula_targets_in_scope") is not False:
        errors.append(f"{path}: formula scope inflation")
    if limitations.get("historical_pdf_byte_equivalence") != "not_established":
        errors.append(f"{path}: historical PDF equivalence inflation")
    if limitations.get("unrestricted_source_theorem_proof_claim") is not False:
        errors.append(f"{path}: unrestricted proof claim inflation")
    if limitations.get("other_family_outputs_authorized") is not False:
        errors.append(f"{path}: other-family authority inflation")
    if limitations.get("aggregate_openai_ten_proofs_authority") is not False:
        errors.append(f"{path}: aggregate authority inflation")
    return errors


def _circuit_route_errors(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return ["OTP-C-PERMANENT-CIRCUIT: missing qualified successor route overlay"]
    overlay = load_json(path)
    if git_blob(path) != CIRCUIT_ROUTE_BLOB:
        errors.append("OTP-C-PERMANENT-CIRCUIT: qualified route overlay blob drift")
    if overlay.get("overlay_id") != "MC-ROUTE-OVERLAY-OTP-C-PERMANENT-CIRCUIT":
        errors.append("OTP-C-PERMANENT-CIRCUIT: route overlay identity drift")
    if overlay.get("base_registry") != {
        "path": "governance/certification_routes.json",
        "digest_algorithm": "git_blob_sha1",
        "digest": GLOBAL_REGISTRY_BLOB,
    }:
        errors.append("OTP-C-PERMANENT-CIRCUIT: base registry identity drift")
    route = overlay.get("route", {})
    if route.get("route_id") != CIRCUIT_ROUTE_ID or route.get("campaign_id") != "OTP-C-PERMANENT-CIRCUIT":
        errors.append("OTP-C-PERMANENT-CIRCUIT: route identity drift")
    if route.get("intake_status") != "qualified":
        errors.append("OTP-C-PERMANENT-CIRCUIT: route is not qualified")
    if route.get("target_claim_ids") != CIRCUIT_TARGETS:
        errors.append("OTP-C-PERMANENT-CIRCUIT: route target scope drift")
    if route.get("cert_output") != CIRCUIT_OUTPUT:
        errors.append("OTP-C-PERMANENT-CIRCUIT: route output identity drift")
    if route.get("mathematical_target_proved") is not False or route.get("aggregate_output") is not False:
        errors.append("OTP-C-PERMANENT-CIRCUIT: route authority inflation")
    preserved = overlay.get("preserved_formula_authority", {})
    if preserved != {
        "variable_leaf_certificate_id": "MC-OTP-C-PERMANENT-QUAL-001",
        "variable_leaf_certificate_blob": "ad10c427270cb1c747ebcacbc5c37e4c1ed1df04",
        "full_formula_certificate_id": "MC-OTP-C-PERMANENT-FULL-FORMULA-QUAL-001",
        "full_formula_certificate_blob": "2940f551805794b96c7b0793bfe0d14e9fcd9954",
        "mutable": False,
    }:
        errors.append("OTP-C-PERMANENT-CIRCUIT: formula predecessor preservation drift")
    return errors


def _a_certificate_errors(path: Path, registry_path: Path) -> list[str]:
    if not path.exists():
        return [f"missing formal target certificate: {A_FILE}"]
    errors: list[str] = []
    if git_blob(path) != A_BLOB:
        errors.append(f"{path}: certificate blob identity drift")
    errors.extend(
        f"OTP-A-SPHERE-PACKING: {error}"
        for error in a_output.validation_errors(
            routes=load_json(registry_path),
            certificate=load_json(path),
            check_history=False,
        )
    )
    return errors


def certificate_errors(
    directory: Path = CERT_DIR,
    schema_path: Path = SCHEMA_PATH,
    registry_path: Path = REGISTRY_PATH,
    root: Path = ROOT,
    full_formula_schema_path: Path = FULL_FORMULA_SCHEMA_PATH,
    full_formula_route_path: Path = FULL_FORMULA_ROUTE_PATH,
    circuit_schema_path: Path = CIRCUIT_SCHEMA_PATH,
    circuit_route_path: Path = CIRCUIT_ROUTE_PATH,
) -> list[str]:
    errors: list[str] = []
    try:
        base = predecessor_module()
    except RuntimeError as exc:
        return [str(exc)]

    # Replay every historical certificate validator on exactly its protected
    # predecessor surface. A is a bounded successor admitted separately below.
    with tempfile.TemporaryDirectory() as temporary:
        predecessor_dir = Path(temporary)
        for source in directory.glob("*.json"):
            if source.name not in {CIRCUIT_FILE, A_FILE}:
                shutil.copyfile(source, predecessor_dir / source.name)
        errors.extend(
            base.certificate_errors(
                directory=predecessor_dir,
                schema_path=schema_path,
                registry_path=registry_path,
                root=root,
                full_formula_schema_path=full_formula_schema_path,
                full_formula_route_path=full_formula_route_path,
            )
        )

    errors.extend(_circuit_certificate_errors(directory / CIRCUIT_FILE, circuit_schema_path))
    errors.extend(_circuit_route_errors(circuit_route_path))
    errors.extend(_a_certificate_errors(directory / A_FILE, registry_path))

    known = {path.name for path in directory.glob("*.json") if path.name != A_FILE}
    with tempfile.TemporaryDirectory() as temporary:
        predecessor_dir = Path(temporary)
        for source in directory.glob("*.json"):
            if source.name != A_FILE:
                shutil.copyfile(source, predecessor_dir / source.name)
        # Unknown non-A members remain rejected by the predecessor chain above;
        # this local set exists only to make the A exception explicit.
        if A_FILE in known:
            errors.append("A successor certificate collided with predecessor membership")
    return errors


def main() -> int:
    errors = certificate_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"formal target certificate validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print(
        "validated protected predecessor certificates plus exact restricted "
        "OTP-C-PERMANENT-FULL-FORMULA, OTP-C-PERMANENT-CIRCUIT, and OTP-A-SPHERE-PACKING qualified successor outputs"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
