#!/usr/bin/env python3
"""Validate TCM Fixture 006 pseudo-Boolean certificate artifacts.

This checker is intentionally small and integer-only. It validates the artifact
shape, replays the primal assignment value, replays the assignment dual upper
bound, and checks that the bounds meet. It is a replay checker for the fixture
certificate, not a general OPB/VeriPB implementation.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

TERM_RE = re.compile(r"([+-]?\d+)\s+x_(\d+)_(\d+)")


class CertificateError(ValueError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CertificateError(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise CertificateError(f"{path}: top-level value must be an object")
    return data


def parse_assignment_opb(path: Path) -> list[list[int]]:
    text = path.read_text(encoding="utf-8")
    objective = None
    for line in text.splitlines():
        if line.strip().startswith("max:"):
            objective = line
            break
    if objective is None:
        raise CertificateError(f"{path}: missing max objective")

    entries: dict[tuple[int, int], int] = {}
    max_row = -1
    max_col = -1
    for coeff_s, row_s, col_s in TERM_RE.findall(objective):
        row = int(row_s)
        col = int(col_s)
        coeff = int(coeff_s)
        entries[(row, col)] = coeff
        max_row = max(max_row, row)
        max_col = max(max_col, col)
    if max_row < 0 or max_col < 0:
        raise CertificateError(f"{path}: objective contains no x_i_j terms")
    if max_row != max_col:
        raise CertificateError(f"{path}: fixture expects a square assignment instance")

    n = max_row + 1
    weights = [[0 for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            key = (i, j)
            if key not in entries:
                raise CertificateError(f"{path}: missing objective coefficient for x_{i}_{j}")
            weights[i][j] = entries[key]
    return weights


def validate_witness(weights: list[list[int]], witness: dict[str, Any]) -> int:
    cols = witness.get("selected_cols")
    if not isinstance(cols, list) or not all(isinstance(c, int) for c in cols):
        raise CertificateError("primal_witness.selected_cols must be a list of integers")
    n = len(weights)
    if len(cols) != n or sorted(cols) != list(range(n)):
        raise CertificateError("witness must select exactly one distinct column per row")
    value = sum(weights[i][col] for i, col in enumerate(cols))
    if witness.get("objective") != value:
        raise CertificateError(f"witness objective mismatch: declared {witness.get('objective')}, replayed {value}")
    return value


def validate_dual(weights: list[list[int]], dual: dict[str, Any]) -> int:
    rows = dual.get("row_duals")
    cols = dual.get("col_duals")
    if not isinstance(rows, list) or not isinstance(cols, list):
        raise CertificateError("dual certificate must contain row_duals and col_duals lists")
    if not all(isinstance(x, int) for x in rows + cols):
        raise CertificateError("dual variables must be integers")
    n = len(weights)
    if len(rows) != n or len(cols) != n:
        raise CertificateError("dual variable dimensions do not match the OPB instance")
    for i in range(n):
        for j in range(n):
            if rows[i] + cols[j] < weights[i][j]:
                raise CertificateError(f"dual upper-bound violation at x_{i}_{j}")
    upper = sum(rows) + sum(cols)
    if dual.get("upper_bound") != upper:
        raise CertificateError(f"dual upper_bound mismatch: declared {dual.get('upper_bound')}, replayed {upper}")
    return upper


def validate_artifact_dir(artifact_dir: Path) -> dict[str, Any]:
    opb = artifact_dir / "instance.opb"
    witness_path = artifact_dir / "primal_witness.json"
    dual_path = artifact_dir / "pb_dual_certificate.json"
    result_card_path = artifact_dir / "result_card.json"

    for path in (opb, witness_path, dual_path, result_card_path):
        if not path.exists():
            raise CertificateError(f"missing required artifact: {path}")

    weights = parse_assignment_opb(opb)
    witness = load_json(witness_path)
    dual = load_json(dual_path)
    result_card = load_json(result_card_path)

    lower = validate_witness(weights, witness)
    upper = validate_dual(weights, dual)
    if lower != upper:
        raise CertificateError(f"certificate bounds do not meet: lower={lower}, upper={upper}")

    claim = result_card.get("claim")
    if not isinstance(claim, dict):
        raise CertificateError("result_card.claim must be an object")
    if claim.get("optimum") != lower:
        raise CertificateError(f"result_card optimum mismatch: declared {claim.get('optimum')}, replayed {lower}")

    return {
        "status": "checked",
        "problem": claim.get("problem"),
        "optimum": lower,
        "trusted_path": "integer primal witness plus integer dual upper-bound replay",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a TCM Fixture 006 PB certificate artifact directory.")
    parser.add_argument("artifact_dir", type=Path)
    parser.add_argument("--write-transcript", type=Path)
    args = parser.parse_args(argv)

    try:
        result = validate_artifact_dir(args.artifact_dir)
    except CertificateError as exc:
        message = f"PB certificate validation failed: {exc}"
        print(message, file=sys.stderr)
        if args.write_transcript:
            args.write_transcript.write_text(message + "\n", encoding="utf-8")
        return 1

    message = json.dumps(result, indent=2, sort_keys=True)
    print(message)
    if args.write_transcript:
        args.write_transcript.write_text(message + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
