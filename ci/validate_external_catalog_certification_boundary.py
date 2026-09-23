#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "governance" / "external_catalog_certification_boundary.json"
SCHEMA = ROOT / "schemas" / "external_catalog_certification_boundary.schema.json"
EXPECTED_PROGRAMME_COMMIT = "4b78daac0b85298957b52e34687423e5442b5e51"
EXPECTED_PROGRAMME_BLOB = "8544fcd383e68a1ca0acd060e56bb0e7d0fe16a0"
EXPECTED_MATHSOLVE_COMMIT = "cea3853b04dac1b419e2232b38fab893d1b4a633"
EXPECTED_MATHSOLVE_BLOB = "1873313a8742293524cc92ade0f9e7248a9d59d9"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validation_errors(instance: dict[str, Any] | None = None) -> list[str]:
    policy = instance if instance is not None else load(POLICY)
    errors = [error.message for error in Draft202012Validator(load(SCHEMA), format_checker=FormatChecker()).iter_errors(policy)]
    programme = policy.get("programme_authority", {})
    solve = policy.get("mathsolve_authority", {})
    if (programme.get("commit"), programme.get("git_blob_sha1")) != (EXPECTED_PROGRAMME_COMMIT, EXPECTED_PROGRAMME_BLOB):
        errors.append("Programme catalog authority identity drift")
    if (solve.get("commit"), solve.get("git_blob_sha1")) != (EXPECTED_MATHSOLVE_COMMIT, EXPECTED_MATHSOLVE_BLOB):
        errors.append("MATHSOLVE intake authority identity drift")
    if policy.get("direct_catalog_intake") is not False:
        errors.append("direct catalog certification intake is forbidden")
    if any(value is not False for value in policy.get("forbidden_inferences", {}).values()):
        errors.append("catalog assurance was inflated into certification authority")
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("validated direct-catalog rejection and separate exact-claim MATHSOLVE-to-MATHCERT certification boundary")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
