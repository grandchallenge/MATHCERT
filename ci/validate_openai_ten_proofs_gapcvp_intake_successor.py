#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "governance/result_family_intake_successors/OTP-H-GAPCVP.json"
SCHEMA = ROOT / "schemas/openai_ten_proofs_gapcvp_result_family_intake_successor.schema.json"
LEGACY_DIR = ROOT / "governance/result_family_intakes"
LEGACY_VALIDATOR = ROOT / "ci/validate_openai_ten_proofs_result_family_intakes.py"
ROUTES = ROOT / "governance/certification_routes.json"

EXPECTED_LEGACY_VALIDATOR_BLOB = "e0a16870c45aadc2b2a323159df595da489384f7"
EXPECTED_ROUTES_BLOB = "2d17473b4731aa9d9c630b1e7777ad4bd794d993"

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

def validate_repository_guards() -> None:
    if git_blob_sha1(LEGACY_VALIDATOR) != EXPECTED_LEGACY_VALIDATOR_BLOB:
        raise ValueError("historical result-family intake validator changed")
    if git_blob_sha1(ROUTES) != EXPECTED_ROUTES_BLOB:
        raise ValueError("certification route registry changed during intake-only operation")
    if (LEGACY_DIR / "OTP-H-GAPCVP.json").exists():
        raise ValueError("GapCVP successor was inserted into frozen historical intake namespace")
    route_text = ROUTES.read_text(encoding="utf-8")
    if "OTP-H-GAPCVP" in route_text or "MC-ROUTE-OTP-H-GAPCVP" in route_text:
        raise ValueError("GapCVP route authority already present during intake-only operation")

def main() -> None:
    validate_record(load_record())
    validate_repository_guards()
    print("OTP-H-GAPCVP successor intake validation: PASS")

if __name__ == "__main__":
    main()
