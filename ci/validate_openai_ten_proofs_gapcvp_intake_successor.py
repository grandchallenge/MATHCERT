#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "governance/result_family_intake_successors/OTP-H-GAPCVP.json"
SCHEMA = ROOT / "schemas/openai_ten_proofs_gapcvp_result_family_intake_successor.schema.json"
LEGACY_DIR = ROOT / "governance/result_family_intakes"
LEGACY_VALIDATOR = ROOT / "ci/validate_openai_ten_proofs_result_family_intakes.py"

EXPECTED_LEGACY_VALIDATOR_BLOB = "e0a16870c45aadc2b2a323159df595da489384f7"
HISTORICAL_PROTECTED_BASE = "947b3bed0effa79c2472dddc37d6c463f79c3126"
FAMILY_ID = "OTP-H-GAPCVP"
OWN_ROUTE_ID = "MC-ROUTE-OTP-H-GAPCVP"


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def load_record() -> dict:
    return json.loads(RECORD.read_text(encoding="utf-8"))


def load_schema() -> dict:
    return json.loads(SCHEMA.read_text(encoding="utf-8"))


def load_historical_routes() -> dict:
    raw = subprocess.check_output(
        ["git", "show", f"{HISTORICAL_PROTECTED_BASE}:governance/certification_routes.json"],
        cwd=ROOT,
        text=True,
    )
    return json.loads(raw)


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
    if (LEGACY_DIR / "OTP-H-GAPCVP.json").exists():
        raise ValueError("GapCVP successor was inserted into frozen historical intake namespace")

    record = load_record()
    if record.get("mathcert_subject", {}).get("protected_base") != HISTORICAL_PROTECTED_BASE:
        raise ValueError("GapCVP intake historical protected-base identity drift")

    historical = load_historical_routes()
    routes = historical.get("routes")
    if not isinstance(routes, list):
        raise ValueError("historical GapCVP intake route snapshot has invalid routes surface")
    if any(
        isinstance(route, dict)
        and (route.get("route_id") == OWN_ROUTE_ID or route.get("campaign_id") == FAMILY_ID)
        for route in routes
    ):
        raise ValueError("GapCVP route authority was present in the exact historical intake snapshot")


def main() -> None:
    validate_record(load_record())
    validate_repository_guards()
    print(
        "OTP-H-GAPCVP successor intake validation: PASS; immutable intake route nonauthority "
        "is scoped to its exact historical protected-base snapshot; later live route evolution is validated separately"
    )


if __name__ == "__main__":
    main()
