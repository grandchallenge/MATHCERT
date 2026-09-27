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
EXPECTED_MATHSOLVE_COMMIT = "b9906e0d150e232efed1a5e4fbd2f5081609ab56"
EXPECTED_MATHSOLVE_BLOB = "e61732d9c732eaa8ecd26067d6561d1ce0b1a779"
EXPECTED_CHAIDEZ_COMMIT = "861479cb599df01f6e9cafc8647fdefe56249d29"
EXPECTED_CHAIDEZ_BLOB = "29e12c793d116c6c3af121c04486c5daa6c09e1e"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validation_errors(instance: dict[str, Any] | None = None) -> list[str]:
    policy = instance if instance is not None else load(POLICY)
    errors = [error.message for error in Draft202012Validator(load(SCHEMA), format_checker=FormatChecker()).iter_errors(policy)]
    programme = policy.get("programme_authority", {})
    solve = policy.get("mathsolve_authority", {})
    chaidez = policy.get("chaidez_authority", {})
    if (programme.get("commit"), programme.get("git_blob_sha1")) != (EXPECTED_PROGRAMME_COMMIT, EXPECTED_PROGRAMME_BLOB):
        errors.append("Programme catalog authority identity drift")
    if (solve.get("commit"), solve.get("git_blob_sha1")) != (EXPECTED_MATHSOLVE_COMMIT, EXPECTED_MATHSOLVE_BLOB):
        errors.append("MATHSOLVE intake authority identity drift")
    if (chaidez.get("commit"), chaidez.get("git_blob_sha1")) != (EXPECTED_CHAIDEZ_COMMIT, EXPECTED_CHAIDEZ_BLOB):
        errors.append("Programme Chaidez authority identity drift")
    if policy.get("direct_catalog_intake") is not False:
        errors.append("direct catalog certification intake is forbidden")
    if any(value is not False for value in policy.get("forbidden_inferences", {}).values()):
        errors.append("catalog assurance was inflated into certification authority")
    handoff = policy.get("required_handoff", {})
    for field in ("chaidez_promotion_dossier_provenance", "trust_quartet_consistent", "named_proof_debt_preserved"):
        if handoff.get(field) is not True:
            errors.append(f"required_handoff.{field} must be true")
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
