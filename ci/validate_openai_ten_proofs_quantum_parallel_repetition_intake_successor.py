#!/usr/bin/env python3
"""Validate the bounded OTP-G quantum-parallel-repetition intake successor."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "governance/result_family_intake_successors/OTP-G-QUANTUM-PARALLEL-REPETITION.json"
SCHEMA = ROOT / "schemas/openai_ten_proofs_quantum_parallel_repetition_result_family_intake_successor.schema.json"
LEGACY_DIR = ROOT / "governance/result_family_intakes"
LEGACY_VALIDATOR = ROOT / "ci/validate_openai_ten_proofs_result_family_intakes.py"
EXPECTED_LEGACY_VALIDATOR_BLOB = "e0a16870c45aadc2b2a323159df595da489384f7"
FAMILY_ID = "OTP-G-QUANTUM-PARALLEL-REPETITION"
EXPECTED_CANONICAL_SHA256 = "547d13a4f73afa740b1a2ba83aafd529e60b1d2555489e1df91ba4daf7683829"


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
    errors = [f"schema: {error.json_path}: {error.message}" for error in sorted(Draft202012Validator(schema).iter_errors(record), key=lambda e: list(e.path))]
    if canonical_sha256(record) != EXPECTED_CANONICAL_SHA256:
        errors.append("quantum parallel repetition successor intake exact content drift")
    if git_blob_sha1(LEGACY_VALIDATOR) != EXPECTED_LEGACY_VALIDATOR_BLOB:
        errors.append("historical result-family intake validator changed")
    exists = (LEGACY_DIR / f"{FAMILY_ID}.json").exists() if legacy_file_exists is None else legacy_file_exists
    if exists:
        errors.append("quantum parallel repetition successor inserted into frozen historical intake namespace")
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("OTP-G quantum parallel repetition successor intake: PASS; exact two-target scope and zero route/output authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
