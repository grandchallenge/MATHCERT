#!/usr/bin/env python3
"""Regression tests for claim-ledger rejection paths."""
from __future__ import annotations

import tempfile
from pathlib import Path

import yaml

from validate_ledgers import validate


def write_ledger(path: Path, claims: list[dict]) -> None:
    path.write_text(yaml.safe_dump({"claims": claims}), encoding="utf-8")


def valid_claim(claim_id: str) -> dict:
    return {
        "claim_id": claim_id,
        "claim_text": "test claim",
        "claim_class": "HEURISTIC",
        "support_type": "HEURISTIC_ARGUMENT",
        "status": "DRAFT",
        "promotion_condition": "Replace with a checked result.",
        "source_or_artifact": [],
    }


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        invalid_class = root / "invalid_class.yaml"
        claim = valid_claim("TEST-C001")
        claim["claim_class"] = "NOT_A_CLASS"
        write_ledger(invalid_class, [claim])
        assert validate(invalid_class, {}) == 1

        duplicate = root / "duplicate.yaml"
        write_ledger(duplicate, [valid_claim("TEST-C002")])
        assert validate(duplicate, {"TEST-C002": root / "first.yaml"}) == 1

        missing_artifact = root / "missing_artifact.yaml"
        claim = valid_claim("TEST-C003")
        claim["source_or_artifact"] = ["does/not/exist.txt"]
        write_ledger(missing_artifact, [claim])
        assert validate(missing_artifact, {}) == 1

    print("Ledger validator rejection tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
