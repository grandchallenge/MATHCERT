#!/usr/bin/env python3
"""Validate the corrected UC-001 stale provider-identity exclusion and repair gate."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
RECORD_PATH = ROOT / "governance" / "UC-001_PROVIDER_IDENTITY_EXCLUSION.json"
SCHEMA_PATH = ROOT / "schemas" / "uc_provider_identity_exclusion.schema.json"
CERT_PATH = ROOT / "certificates" / "union_closed" / "MC-UC-WP04-QUAL-001.json"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def errors(
    record_path: Path = RECORD_PATH,
    schema_path: Path = SCHEMA_PATH,
    cert_path: Path = CERT_PATH,
) -> list[str]:
    try:
        record = load(record_path)
        schema = load(schema_path)
        certificate = load(cert_path)
    except (OSError, json.JSONDecodeError) as exc:
        return [f"UC provider exclusion load failed: {exc}"]

    found = [
        f"{error.json_path}: {error.message}"
        for error in sorted(
            Draft202012Validator(schema).iter_errors(record),
            key=lambda item: list(item.path),
        )
    ]
    if schema.get("additionalProperties") is not False:
        found.append("UC provider exclusion schema must remain closed")

    excluded = record.get("excluded_artifact", {})
    correction = record.get("correction_history", {})
    if excluded.get("recorded_digest") == excluded.get("observed_digest"):
        found.append("UC provider exclusion must record a real identity mismatch")
    if correction.get("corrected_recorded_digest") != excluded.get("recorded_digest"):
        found.append("corrected recorded digest is not the live exclusion value")
    if correction.get("corrected_observed_digest") != excluded.get("observed_digest"):
        found.append("corrected observed digest is not the live exclusion value")
    if correction.get("superseded_recorded_digest") == excluded.get("recorded_digest"):
        found.append("superseded recorded digest was not actually corrected")
    if correction.get("superseded_observed_digest") == excluded.get("observed_digest"):
        found.append("superseded observed digest was not actually corrected")
    if correction.get("qualification_unchanged") is not True:
        found.append("provider identity correction cannot alter the qualification")

    if record.get("source_manifest") != certificate.get("solve_provider", {}).get("manifest"):
        found.append("UC provider exclusion source manifest is not the qualified manifest")
    excluded_path = excluded.get("path")
    evidence_paths = {
        item.get("evidence", {}).get("path")
        for item in certificate.get("qualified_claims", [])
        if isinstance(item, dict)
    }
    if excluded_path in evidence_paths:
        found.append("excluded provider artifact cannot support a qualified claim")
    repair = record.get("downstream_repair", {})
    if repair.get("required") is not True or repair.get("closure_blocked_until_repair") is not True:
        found.append("downstream Solve repair must remain mandatory and closure-blocking")
    if (repair.get("repository"), repair.get("issue")) != ("grandchallenge/MATHSOLVE", 1):
        found.append("UC provider exclusion repair target drift")
    if record.get("status") != "open_repair_required":
        found.append("UC provider identity exclusion cannot close before protected Solve repair")
    boundary = str(record.get("claim_boundary", ""))
    for token in ("does not weaken", "does not", "downstream closure requires"):
        if token not in boundary:
            found.append(f"UC provider exclusion boundary missing token: {token}")
    return found


def main() -> int:
    found = errors()
    if found:
        print("\n".join(found), file=sys.stderr)
        print(f"UC provider identity exclusion failed with {len(found)} error(s)", file=sys.stderr)
        return 1
    print(
        "validated corrected stale UC README exclusion, explicit correction history, "
        "and mandatory downstream MATHSOLVE repair gate"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
