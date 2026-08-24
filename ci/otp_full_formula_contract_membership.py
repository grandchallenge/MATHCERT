from __future__ import annotations

import hashlib
from pathlib import Path

FULL_FORMULA_NAME = "OTP-C-PERMANENT-FULL-FORMULA.json"
EXPECTED_FULL_FORMULA_BLOB = "e234a4bcf55353ed6519e54a41d479b51d93c82c"
CIRCUIT_NAME = "OTP-C-PERMANENT-CIRCUIT.json"
EXPECTED_CIRCUIT_BLOB = "0481f5539d8a9bd72fbb3644ba8481a672eb1d7a"
A_SPHERE_NAME = "OTP-A-SPHERE-PACKING.json"
EXPECTED_A_SPHERE_BLOB = "9ebd8182f1af652c404756d956e004868336b3d6"


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

    full_formula_shadow = historical_dir / FULL_FORMULA_NAME
    full_formula_canonical = successor_dir / FULL_FORMULA_NAME
    circuit_canonical = successor_dir / CIRCUIT_NAME
    a_sphere_contract = historical_dir / A_SPHERE_NAME

    actual_historical = {p.name for p in historical_dir.glob("*.json")}
    expected_historical = set(historical_expected) | {FULL_FORMULA_NAME}
    if a_sphere_contract.exists():
        expected_historical.add(A_SPHERE_NAME)
    if actual_historical != expected_historical:
        errors.append(
            "output-contract historical membership drift beyond governed compatibility shadows/design objects: "
            f"expected {sorted(expected_historical)}, found {sorted(actual_historical)}"
        )

    expected_successors = {FULL_FORMULA_NAME, CIRCUIT_NAME}
    actual_successors = {p.name for p in successor_dir.glob("*.json")} if successor_dir.exists() else set()
    if actual_successors != expected_successors:
        errors.append(
            "output-contract successor membership drift: "
            f"expected exactly {sorted(expected_successors)}, found {sorted(actual_successors)}"
        )

    for label, path, expected_blob in (
        ("historical full-formula compatibility shadow", full_formula_shadow, EXPECTED_FULL_FORMULA_BLOB),
        ("canonical full-formula successor", full_formula_canonical, EXPECTED_FULL_FORMULA_BLOB),
        ("canonical circuit successor", circuit_canonical, EXPECTED_CIRCUIT_BLOB),
    ):
        if not path.exists():
            errors.append(f"missing {label}: {path.relative_to(root).as_posix()}")
            continue
        blob = git_blob_sha1(path)
        if blob != expected_blob:
            errors.append(
                f"{label} blob drift: expected {expected_blob}, found {blob}"
            )

    if a_sphere_contract.exists():
        blob = git_blob_sha1(a_sphere_contract)
        if blob != EXPECTED_A_SPHERE_BLOB:
            errors.append(
                "governed A sphere-packing output-design contract blob drift: "
                f"expected {EXPECTED_A_SPHERE_BLOB}, found {blob}"
            )

    if (
        full_formula_shadow.exists()
        and full_formula_canonical.exists()
        and full_formula_shadow.read_bytes() != full_formula_canonical.read_bytes()
    ):
        errors.append("historical full-formula compatibility shadow differs from canonical successor contract")

    if (historical_dir / CIRCUIT_NAME).exists():
        errors.append("circuit successor must not create a historical output-contract compatibility shadow")

    return errors
