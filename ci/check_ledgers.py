#!/usr/bin/env python3
"""Run claim-ledger validation over discovered instance files, not schemas."""
from __future__ import annotations

import sys
import hashlib
from pathlib import Path

import validate_ledgers as module

# Exact non-authoritative Solve fixture from protected b9906e0d150e232efed1a5e4fbd2f5081609ab56.
# Its complete bundle is independently exercised by the receiving-gate canary.
# No directory-wide fixture exemption and no production claim exemption exist.
CANARY_PATH = module.PACKAGE_ROOT / "contracts/chaidez_solve/tests/fixtures/external_catalog_promotion/solve/work_packages/CANARY/claim_ledger.json"
CANARY_SHA256 = "d4e87ab68c260bb80bacff1969279b6b5a8c0d42350f74c8c6f4b5524d661de3"


def ledger_files() -> list[Path]:
    files = []
    for path in module.discover_ledgers():
        if path.name.endswith(".schema.json"):
            continue
        if path == CANARY_PATH:
            if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != CANARY_SHA256:
                raise ValueError("non-authoritative ledger fixture identity drift")
            continue
        files.append(path)
    return files


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
