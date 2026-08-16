#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import validate_otp_j2_route_target_successor as successor
import validate_otp_j2_source_faithful_evidence as historical

ROOT = Path(__file__).resolve().parents[1]


def predecessor_routes() -> dict:
    proc = subprocess.run(
        ["git", "-C", str(ROOT), "cat-file", "blob", successor.PREDECESSOR_ROUTE_BLOB],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(proc.stdout)


def validation_errors() -> list[str]:
    record = historical.load(historical.RECORD)
    errors = historical.validation_errors(record, predecessor_routes(), check_files=False)
    if successor.repo_blob("governance/result_family_construction_evidence/OTP-J2-TWO-DEGENERATE.json") != successor.EVIDENCE_BLOB:
        errors.append("protected completed J2 evidence record was rewritten")
    errors.extend(successor.validation_errors())
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"successor-aware J2 evidence compatibility failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print(
        "validated immutable completed J2 source-faithful evidence against its protected predecessor-route "
        "snapshot and separately validated the explicit live route-target successor"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
