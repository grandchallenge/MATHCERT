#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import validate_openai_ten_proofs_adjudication_contracts as design

ROOT = Path(__file__).resolve().parents[1]
ADJUDICATION_DIR = ROOT / "governance/result_family_adjudications"
CERT_DIR = ROOT / "certificates/openai_ten_proofs"
ALLOWED_ADJUDICATIONS = {"OTP-F-EHRHART.json"}


def validation_errors() -> list[str]:
    errors = design.validation_errors(
        executed_present=False,
        route_blob=design.D.ROUTE_REGISTRY_BLOB,
    )
    actual_adjudications = {
        path.name for path in ADJUDICATION_DIR.glob("*.json") if path.is_file()
    } if ADJUDICATION_DIR.is_dir() else set()
    if actual_adjudications != ALLOWED_ADJUDICATIONS:
        errors.append(
            "separately governed adjudication membership drift: "
            f"expected {sorted(ALLOWED_ADJUDICATIONS)}, got {sorted(actual_adjudications)}"
        )
    actual_outputs = {
        path.name for path in CERT_DIR.glob("*.json") if path.is_file()
    } if CERT_DIR.is_dir() else set()
    if actual_outputs:
        errors.append(f"unauthorized OTP Cert output artifacts exist: {sorted(actual_outputs)}")
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(
            f"successor-aware adjudication design validation failed with {len(errors)} error(s)",
            file=sys.stderr,
        )
        return 1
    print(
        "validated three immutable design-only OTP adjudication contracts, exactly one separately governed Ehrhart adjudication record, and zero Cert outputs"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
