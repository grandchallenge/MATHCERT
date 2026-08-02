#!/usr/bin/env python3
"""Execute the closed schema for the UC-001 restricted qualification."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
CERT_PATH = ROOT / "certificates" / "union_closed" / "MC-UC-WP04-QUAL-001.json"
SCHEMA_PATH = ROOT / "schemas" / "uc_restricted_qualification.schema.json"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def errors(cert_path: Path = CERT_PATH, schema_path: Path = SCHEMA_PATH) -> list[str]:
    try:
        certificate = load(cert_path)
        schema = load(schema_path)
    except (OSError, json.JSONDecodeError) as exc:
        return [f"UC schema load failed: {exc}"]
    return [
        f"{error.json_path}: {error.message}"
        for error in sorted(
            Draft202012Validator(schema).iter_errors(certificate),
            key=lambda item: list(item.path),
        )
    ]


def main() -> int:
    found = errors()
    if found:
        print("\n".join(found), file=sys.stderr)
        print(f"UC restricted qualification schema failed with {len(found)} error(s)", file=sys.stderr)
        return 1
    print("validated closed UC-001 restricted qualification schema")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
