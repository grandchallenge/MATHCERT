#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "governance/result_family_intake_successors/OTP-A-SPHERE-PACKING.json"
SCHEMA = ROOT / "schemas/openai_ten_proofs_sphere_packing_result_family_intake_successor.schema.json"
LEGACY_DIR = ROOT / "governance/result_family_intakes"
LEGACY_VALIDATOR = ROOT / "ci/validate_openai_ten_proofs_result_family_intakes.py"
ROUTES = ROOT / "governance/certification_routes.json"
ROUTE_REGISTRY_PATH = "governance/certification_routes.json"
INTAKE_PROTECTED_PREDECESSOR_HEAD = "4b194b9632a9aa57fee21c3c054498d6b4a8ed57"

EXPECTED_LEGACY_VALIDATOR_BLOB = "e0a16870c45aadc2b2a323159df595da489384f7"
PRE_REGISTRATION_ROUTES_BLOB = "2d17473b4731aa9d9c630b1e7777ad4bd794d993"
A_ROUTE_ID = "MC-ROUTE-OTP-A-SPHERE-PACKING"


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def blob_at_commit(commit: str, path: str) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", f"{commit}:{path}"], cwd=ROOT, text=True
    ).strip()


def text_at_commit(commit: str, path: str) -> str:
    return subprocess.check_output(
        ["git", "show", f"{commit}:{path}"], cwd=ROOT, text=True
    )


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
    if (LEGACY_DIR / "OTP-A-SPHERE-PACKING.json").exists():
        raise ValueError("sphere-packing successor was inserted into frozen historical intake namespace")

    routes_blob = blob_at_commit(INTAKE_PROTECTED_PREDECESSOR_HEAD, ROUTE_REGISTRY_PATH)
    if routes_blob != PRE_REGISTRATION_ROUTES_BLOB:
        raise ValueError(
            "protected A intake predecessor route registry drift: "
            f"{routes_blob} != {PRE_REGISTRATION_ROUTES_BLOB}"
        )
    route_text = text_at_commit(INTAKE_PROTECTED_PREDECESSOR_HEAD, ROUTE_REGISTRY_PATH)
    if "OTP-A-SPHERE-PACKING" in route_text or A_ROUTE_ID in route_text:
        raise ValueError("sphere-packing route authority already present during protected intake snapshot")


def main() -> None:
    validate_record(load_record())
    validate_repository_guards()
    print(
        "OTP-A-SPHERE-PACKING successor intake validation: PASS; immutable intake preserved "
        "against exact protected pre-registration route snapshot; later governed route successors "
        "are validated separately"
    )


if __name__ == "__main__":
    main()
