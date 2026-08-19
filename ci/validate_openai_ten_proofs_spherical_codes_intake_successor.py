#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "governance/result_family_intake_successors/OTP-B2-SPHERICAL-CODES.json"
SCHEMA = ROOT / "schemas/openai_ten_proofs_spherical_codes_result_family_intake_successor.schema.json"
LEGACY_DIR = ROOT / "governance/result_family_intakes"
LEGACY_VALIDATOR = ROOT / "ci/validate_openai_ten_proofs_result_family_intakes.py"
ROUTES = ROOT / "governance/certification_routes.json"

EXPECTED_LEGACY_VALIDATOR_BLOB = "e0a16870c45aadc2b2a323159df595da489384f7"
PRE_REGISTRATION_ROUTES_BLOB = "2d17473b4731aa9d9c630b1e7777ad4bd794d993"
A_REGISTRATION_ROUTES_BLOB = "b9bb0dc9e18856f50a88162df37c20c034327439"
OWN_ROUTE_ID = "MC-ROUTE-OTP-B2-SPHERICAL-CODES"

def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()

def load_record() -> dict:
    return json.loads(RECORD.read_text(encoding="utf-8"))

def load_schema() -> dict:
    return json.loads(SCHEMA.read_text(encoding="utf-8"))

def validate_record(data: dict) -> None:
    validator = Draft202012Validator(load_schema())
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))
    if errors:
        rendered = "; ".join(
            f"{'/'.join(map(str, e.absolute_path)) or '<root>'}: {e.message}" for e in errors
        )
        raise ValueError(rendered)

def _a_registration_errors() -> list[str]:
    spec = importlib.util.spec_from_file_location(
        "sphere_packing_route_registration",
        ROOT / "ci/validate_openai_ten_proofs_sphere_packing_route_registration.py",
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return list(module.validation_errors())

def validate_repository_guards() -> None:
    if git_blob_sha1(LEGACY_VALIDATOR) != EXPECTED_LEGACY_VALIDATOR_BLOB:
        raise ValueError("historical result-family intake validator changed")
    if (LEGACY_DIR / "OTP-B2-SPHERICAL-CODES.json").exists():
        raise ValueError("spherical-codes successor was inserted into frozen historical intake namespace")
    route_text = ROUTES.read_text(encoding="utf-8")
    if "OTP-B2-SPHERICAL-CODES" in route_text or OWN_ROUTE_ID in route_text:
        raise ValueError("spherical-codes route authority already present during intake-only operation")
    routes_blob = git_blob_sha1(ROUTES)
    if routes_blob == PRE_REGISTRATION_ROUTES_BLOB:
        return
    if routes_blob == A_REGISTRATION_ROUTES_BLOB:
        errors = _a_registration_errors()
        if errors:
            raise ValueError("separately governed A route registration invalid: " + "; ".join(errors))
        return
    raise ValueError("certification route registry is neither protected intake snapshot nor exact governed A registration successor")

def main() -> None:
    validate_record(load_record())
    validate_repository_guards()
    print("OTP-B2-SPHERICAL-CODES successor intake validation: PASS; immutable intake preserved across exact separately governed A registration successor")

if __name__ == "__main__":
    main()
