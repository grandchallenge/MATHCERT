from __future__ import annotations

import contextlib
import json
from pathlib import Path
from unittest.mock import patch

FULL_FORMULA_NAME = "OTP-C-PERMANENT-FULL-FORMULA.json"
EXPECTED_FULL_FORMULA_BLOB = "2ffd6c8b760e80d32344ea2e21fa8d3378104992"
FULL_FORMULA_TARGETS = [
    "PermanentFormulaLowerBound.permanent_divisionFree_formula_lower_bound",
    "PermanentFormulaLowerBound.permanent_rational_formula_lower_bound",
]
# Historical compatibility aliases consumed by the existing mutation suite.
SUCCESSOR_NAME = FULL_FORMULA_NAME
EXPECTED_SUCCESSOR_BLOB = EXPECTED_FULL_FORMULA_BLOB
EXPECTED_TARGETS = FULL_FORMULA_TARGETS

CIRCUIT_NAME = "OTP-C-PERMANENT-CIRCUIT.json"
EXPECTED_CIRCUIT_BLOB = "c5449d45d230143835bd7695755df256b215ad06"
CIRCUIT_TARGETS = [
    "PermanentRollout.permanent_circuit_loglog_lower_bound",
    "PermanentRollout.permanent_circuit_loglog_bigOmega",
    "PermanentRollout.permanent_complexity_ratio_tendsto_atTop",
]


def git_blob_sha1(path: Path) -> str:
    import hashlib
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data, usedforsecurity=False).hexdigest()


def successor_errors(root: Path, proposal_dir: Path) -> list[str]:
    errors: list[str] = []
    members = sorted(p.name for p in proposal_dir.glob("*.json"))
    expected_members = sorted([CIRCUIT_NAME, FULL_FORMULA_NAME, "OTP-C-PERMANENT.json"])
    if members != expected_members:
        errors.append(f"route-proposal successor membership drift: {members}")
        return errors

    full_formula = proposal_dir / FULL_FORMULA_NAME
    if git_blob_sha1(full_formula) != EXPECTED_FULL_FORMULA_BLOB:
        errors.append("full-formula route-proposal blob drift")
    else:
        record = json.loads(full_formula.read_text(encoding="utf-8"))
        if record.get("requested_route_id") != "MC-ROUTE-OTP-C-PERMANENT-FULL-FORMULA":
            errors.append("full-formula requested route id drift")
        contract = record.get("route_contract", {})
        if contract.get("initial_intake_status") != "submitted" or contract.get("cert_output_initial") is not None:
            errors.append("full-formula route proposal authority inflation")
        if contract.get("target_claim_ids") != FULL_FORMULA_TARGETS:
            errors.append("full-formula route proposal target drift")
        projection = record.get("source_projection", {})
        expected_projection = {
            "coefficient_field": "complex",
            "dimension_threshold": 32,
            "log_base": 2,
            "division_free": {"variable_leaves":128,"total_leaves":128,"vertices":128,"internal_gates":256},
            "rational": {"variable_leaves":192,"total_leaves":192,"vertices":192,"internal_gates":384},
            "formula_target_count": 2,
            "circuit_target_count": 0,
            "historical_pdf_byte_equivalence": False,
        }
        if projection != expected_projection:
            errors.append("full-formula route proposal source projection drift")
        predecessor = record.get("preserved_predecessor", {})
        if predecessor != {
            "route_id": "MC-ROUTE-OTP-C-PERMANENT-FORMULA",
            "certificate_id": "MC-OTP-C-PERMANENT-QUAL-001",
            "mutable": False,
        }:
            errors.append("full-formula proposal predecessor protection drift")

    circuit = proposal_dir / CIRCUIT_NAME
    if git_blob_sha1(circuit) != EXPECTED_CIRCUIT_BLOB:
        errors.append("circuit route-proposal blob drift")
    else:
        record = json.loads(circuit.read_text(encoding="utf-8"))
        if record.get("requested_route_id") != "MC-ROUTE-OTP-C-PERMANENT-CIRCUIT":
            errors.append("circuit requested route id drift")
        contract = record.get("route_contract", {})
        if contract.get("initial_route_state") != "submitted" or contract.get("cert_output_initial") is not None:
            errors.append("circuit route proposal authority inflation")
        if contract.get("target_claim_ids") != CIRCUIT_TARGETS:
            errors.append("circuit route proposal target drift")
        if contract.get("mathematical_target_proved") is not False or contract.get("aggregate_output") is not False:
            errors.append("circuit route proposal proof/aggregate authority inflation")
        authority = record.get("authority", {})
        if authority != {
            "forge_semantic_blob": "d47a50df90174ed03669b11b8469dc1c0788a1ea",
            "solve_packet_blob": "f8443c47cee03890ca52af3e0cd39f1a54b5fc71",
            "overlay_json_blob": "1c2aad24890425ef82f8e45fa654de32dc0e2659",
            "overlay_lean_blob": "18fc438580bab2bc003d4d3cfd9fa283da421b04",
        }:
            errors.append("circuit route proposal authority identity drift")
        projection = record.get("source_projection", {})
        expected_projection = {
            "coefficient_field": "complex",
            "model": "division_free_arithmetic_circuit_dag",
            "input_gates": ["matrix_variable", "arbitrary_complex_scalar"],
            "arithmetic_gates": ["add", "sub", "mul"],
            "division_allowed": False,
            "fanout_reuse_allowed": True,
            "size_counts_arithmetic_gates_only": True,
            "input_gates_counted": False,
            "dimension_threshold": 65536,
            "finite_bound_denominator": 144,
            "finite_bound": "n^2 * (log_2(log_2 n) - 3) / 144 <= circuitComplexity(permanent_n)",
            "bigomega_consequence": "circuitComplexity(permanent_n) = Omega(n^2 log_2 log_2 n)",
            "ratio_divergence_consequence": "circuitComplexity(permanent_n) / n^2 tends to +infinity",
            "historical_pdf_byte_equivalence": False,
        }
        if projection != expected_projection:
            errors.append("circuit route proposal source projection drift")

    return errors


@contextlib.contextmanager
def historical_membership_view(proposal_dir: Path):
    original_glob = Path.glob

    def filtered_glob(self: Path, pattern: str):
        values = list(original_glob(self, pattern))
        if self == proposal_dir and pattern == "*.json":
            values = [p for p in values if p.name not in {FULL_FORMULA_NAME, CIRCUIT_NAME}]
        return iter(values)

    with patch.object(Path, "glob", filtered_glob):
        yield
