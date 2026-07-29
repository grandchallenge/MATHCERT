#!/usr/bin/env python3
"""Run claim-ledger validation over discovered instance files, not schemas."""
from __future__ import annotations

import sys
from pathlib import Path

import validate_ledgers as module


def ledger_files() -> list[Path]:
    return [path for path in module.discover_ledgers() if not path.name.endswith(".schema.json")]


def main() -> int:
    files = ledger_files()
    if not files:
        print("No claim-ledger instances found; certification coverage is invalid.", file=sys.stderr)
        return 1
    seen_ids: dict[str, Path] = {}
    errors = sum(module.validate(path, seen_ids) for path in files)
    if errors:
        print(f"Ledger validation failed with {errors} errors", file=sys.stderr)
        return 1
    suffixes = sorted({path.suffix.lower() for path in files})
    print(f"Validated {len(files)} claim-ledger instance(s) across {', '.join(suffixes)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
