from __future__ import annotations

import hashlib
from pathlib import Path

SUCCESSOR_NAME = "OTP-C-PERMANENT-FULL-FORMULA.json"
EXPECTED_SUCCESSOR_BLOB = "e234a4bcf55353ed6519e54a41d479b51d93c82c"


def git_blob_sha1(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload,
        usedforsecurity=False,
    ).hexdigest()


def membership_errors(root: Path, historical_expected: set[str]) -> list[str]:
    errors: list[str] = []
    historical_dir = root / "governance/result_family_output_contracts"
    successor_dir = root / "governance/result_family_output_contract_successors"
    shadow = historical_dir / SUCCESSOR_NAME
    canonical = successor_dir / SUCCESSOR_NAME

    actual_historical = {p.name for p in historical_dir.glob("*.json")}
    expected_historical = set(historical_expected) | {SUCCESSOR_NAME}
    if actual_historical != expected_historical:
        errors.append(
            "output-contract membership drift beyond the single governed full-formula successor: "
            f"expected {sorted(expected_historical)}, found {sorted(actual_historical)}"
        )

    actual_successors = {p.name for p in successor_dir.glob("*.json")} if successor_dir.exists() else set()
    if actual_successors != {SUCCESSOR_NAME}:
        errors.append(
            "output-contract successor membership drift: "
            f"expected only {SUCCESSOR_NAME}, found {sorted(actual_successors)}"
        )

    for label, path in (("historical compatibility shadow", shadow), ("canonical successor", canonical)):
        if not path.exists():
            errors.append(f"missing {label}: {path.relative_to(root).as_posix()}")
            continue
        blob = git_blob_sha1(path)
        if blob != EXPECTED_SUCCESSOR_BLOB:
            errors.append(
                f"{label} blob drift: expected {EXPECTED_SUCCESSOR_BLOB}, found {blob}"
            )

    if shadow.exists() and canonical.exists() and shadow.read_bytes() != canonical.read_bytes():
        errors.append("historical compatibility shadow differs from canonical successor contract")

    return errors
