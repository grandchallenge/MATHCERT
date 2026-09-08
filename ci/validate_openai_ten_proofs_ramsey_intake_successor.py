#!/usr/bin/env python3
"""Validate the bounded OTP-I-RAMSEY MATHCERT intake successor."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "governance/result_family_intake_successors/OTP-I-RAMSEY.json"
SCHEMA = ROOT / "schemas/openai_ten_proofs_ramsey_result_family_intake_successor.schema.json"
LEGACY_DIR = ROOT / "governance/result_family_intakes"
LEGACY_VALIDATOR = ROOT / "ci/validate_openai_ten_proofs_result_family_intakes.py"
EXPECTED_LEGACY_VALIDATOR_BLOB = "e0a16870c45aadc2b2a323159df595da489384f7"
HISTORICAL_PROTECTED_BASE = "ea19147af0efc086a723d4f4d6c89d7365519aba"
FAMILY_ID = "OTP-I-RAMSEY"
EXPECTED_CANONICAL_SHA256 = "acefe4ebdfb00db63735e9744ec64701b5c662332bc9e032aed4e9ce4ad5aaef"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data, usedforsecurity=False).hexdigest()


def canonical_sha256(data: Any) -> str:
    payload = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def validation_errors(data: dict[str, Any] | None = None, *, legacy_file_exists: bool | None = None) -> list[str]:
    record = load_json(RECORD) if data is None else data
    schema = load_json(SCHEMA)
    errors = [
        f"schema: {error.json_path}: {error.message}"
        for error in sorted(Draft202012Validator(schema).iter_errors(record), key=lambda e: list(e.path))
    ]
    if canonical_sha256(record) != EXPECTED_CANONICAL_SHA256:
        errors.append("Ramsey successor intake exact content drift")
    if git_blob_sha1(LEGACY_VALIDATOR) != EXPECTED_LEGACY_VALIDATOR_BLOB:
        errors.append("historical result-family intake validator changed")
    exists = (LEGACY_DIR / f"{FAMILY_ID}.json").exists() if legacy_file_exists is None else legacy_file_exists
    if exists:
        errors.append("Ramsey successor inserted into frozen historical intake namespace")
    raw = subprocess.check_output(
        ["git", "show", f"{HISTORICAL_PROTECTED_BASE}:governance/certification_routes.json"],
        cwd=ROOT,
        text=True,
    )
    routes = json.loads(raw).get("routes", [])
    if any(isinstance(route, dict) and (route.get("campaign_id") == FAMILY_ID or FAMILY_ID in str(route.get("route_id", ""))) for route in routes):
        errors.append("Ramsey route authority existed at the exact historical intake base")
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("OTP-I-RAMSEY successor intake: PASS; exact four-target scope, frozen historical registry, zero route/output authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
