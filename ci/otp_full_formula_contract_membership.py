from __future__ import annotations

import hashlib
from pathlib import Path

FULL_FORMULA_NAME = "OTP-C-PERMANENT-FULL-FORMULA.json"
EXPECTED_FULL_FORMULA_BLOB = "e234a4bcf55353ed6519e54a41d479b51d93c82c"
CIRCUIT_NAME = "OTP-C-PERMANENT-CIRCUIT.json"
EXPECTED_CIRCUIT_BLOB = "0481f5539d8a9bd72fbb3644ba8481a672eb1d7a"
A_SPHERE_NAME = "OTP-A-SPHERE-PACKING.json"
EXPECTED_A_SPHERE_BLOB = "9ebd8182f1af652c404756d956e004868336b3d6"
B1_BINARY_CODES_NAME = "OTP-B1-BINARY-CODES.json"
EXPECTED_B1_BINARY_CODES_BLOB = "89b504e2dda11389611f089ac3d9d01ac4d419dd"
H_GAPCVP_NAME = "OTP-H-GAPCVP.json"
EXPECTED_H_GAPCVP_BLOB = "1bcffa57c9e07dc0a224f13c84e9ec0597429b92"
B2_SPHERICAL_CODES_NAME = "OTP-B2-SPHERICAL-CODES.json"
EXPECTED_B2_SPHERICAL_CODES_BLOB = "ac5ca772fad30e6f8508b5ddb88484ce754b2e87"
I_RAMSEY_NAME = "OTP-I-RAMSEY.json"
EXPECTED_I_RAMSEY_BLOB = "870bb25044a5e703ef96036252ab2275b7c831b3"
G_QUANTUM_PARALLEL_REPETITION_NAME = "OTP-G-QUANTUM-PARALLEL-REPETITION.json"
EXPECTED_G_QUANTUM_PARALLEL_REPETITION_BLOB = "63c6151a0cd055aa4de595db29a58a9a1d2f46c3"
D_NON_SOFIC_NAME = "OTP-D-NON-SOFIC.json"
EXPECTED_D_NON_SOFIC_BLOB = "8c0e1457b23d2cc81a9c69e888321c724ae4c91c"


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
    b1_binary_codes_contract = historical_dir / B1_BINARY_CODES_NAME
    h_gapcvp_contract = historical_dir / H_GAPCVP_NAME
    b2_spherical_codes_contract = historical_dir / B2_SPHERICAL_CODES_NAME
    i_ramsey_contract = historical_dir / I_RAMSEY_NAME
    g_quantum_parallel_repetition_contract = historical_dir / G_QUANTUM_PARALLEL_REPETITION_NAME
    d_non_sofic_contract = historical_dir / D_NON_SOFIC_NAME

    actual_historical = {p.name for p in historical_dir.glob("*.json")}
    expected_historical = set(historical_expected) | {FULL_FORMULA_NAME}
    if a_sphere_contract.exists():
        expected_historical.add(A_SPHERE_NAME)
    if b1_binary_codes_contract.exists():
        expected_historical.add(B1_BINARY_CODES_NAME)
    if h_gapcvp_contract.exists():
        expected_historical.add(H_GAPCVP_NAME)
    if b2_spherical_codes_contract.exists():
        expected_historical.add(B2_SPHERICAL_CODES_NAME)
    if i_ramsey_contract.exists():
        expected_historical.add(I_RAMSEY_NAME)
    if g_quantum_parallel_repetition_contract.exists():
        expected_historical.add(G_QUANTUM_PARALLEL_REPETITION_NAME)
    if d_non_sofic_contract.exists():
        expected_historical.add(D_NON_SOFIC_NAME)
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

    if b1_binary_codes_contract.exists():
        blob = git_blob_sha1(b1_binary_codes_contract)
        if blob != EXPECTED_B1_BINARY_CODES_BLOB:
            errors.append(
                "governed B1 binary-codes output contract blob drift: "
                f"expected {EXPECTED_B1_BINARY_CODES_BLOB}, found {blob}"
            )

    if h_gapcvp_contract.exists():
        blob = git_blob_sha1(h_gapcvp_contract)
        if blob != EXPECTED_H_GAPCVP_BLOB:
            errors.append(
                "governed H GapCVP output contract blob drift: "
                f"expected {EXPECTED_H_GAPCVP_BLOB}, found {blob}"
            )

    if b2_spherical_codes_contract.exists():
        blob = git_blob_sha1(b2_spherical_codes_contract)
        if blob != EXPECTED_B2_SPHERICAL_CODES_BLOB:
            errors.append(
                "governed B2 spherical-codes output contract blob drift: "
                f"expected {EXPECTED_B2_SPHERICAL_CODES_BLOB}, found {blob}"
            )

    if i_ramsey_contract.exists():
        blob = git_blob_sha1(i_ramsey_contract)
        if blob != EXPECTED_I_RAMSEY_BLOB:
            errors.append(
                "governed I Ramsey output contract blob drift: "
                f"expected {EXPECTED_I_RAMSEY_BLOB}, found {blob}"
            )

    if g_quantum_parallel_repetition_contract.exists():
        blob = git_blob_sha1(g_quantum_parallel_repetition_contract)
        if blob != EXPECTED_G_QUANTUM_PARALLEL_REPETITION_BLOB:
            errors.append(
                "governed G quantum-parallel-repetition output contract blob drift: "
                f"expected {EXPECTED_G_QUANTUM_PARALLEL_REPETITION_BLOB}, found {blob}"
            )

    if d_non_sofic_contract.exists():
        blob = git_blob_sha1(d_non_sofic_contract)
        if blob != EXPECTED_D_NON_SOFIC_BLOB:
            errors.append(
                "governed D non-sofic output contract blob drift: "
                f"expected {EXPECTED_D_NON_SOFIC_BLOB}, found {blob}"
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
