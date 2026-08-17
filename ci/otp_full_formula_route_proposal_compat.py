from __future__ import annotations

import contextlib
import json
from pathlib import Path
from unittest.mock import patch

SUCCESSOR_NAME = "OTP-C-PERMANENT-FULL-FORMULA.json"
EXPECTED_SUCCESSOR_BLOB = "2ffd6c8b760e80d32344ea2e21fa8d3378104992"
EXPECTED_TARGETS = [
    "PermanentFormulaLowerBound.permanent_divisionFree_formula_lower_bound",
    "PermanentFormulaLowerBound.permanent_rational_formula_lower_bound",
]


def git_blob_sha1(path: Path) -> str:
    import hashlib
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data, usedforsecurity=False).hexdigest()


def successor_errors(root: Path, proposal_dir: Path) -> list[str]:
    errors: list[str] = []
    members = sorted(p.name for p in proposal_dir.glob("*.json"))
    if members != [SUCCESSOR_NAME, "OTP-C-PERMANENT.json"]:
        errors.append(f"route-proposal successor membership drift: {members}")
        return errors
    successor = proposal_dir / SUCCESSOR_NAME
    if git_blob_sha1(successor) != EXPECTED_SUCCESSOR_BLOB:
        errors.append("full-formula route-proposal blob drift")
        return errors
    record = json.loads(successor.read_text(encoding="utf-8"))
    if record.get("requested_route_id") != "MC-ROUTE-OTP-C-PERMANENT-FULL-FORMULA":
        errors.append("full-formula requested route id drift")
    contract = record.get("route_contract", {})
    if contract.get("initial_intake_status") != "submitted" or contract.get("cert_output_initial") is not None:
        errors.append("full-formula route proposal authority inflation")
    if contract.get("target_claim_ids") != EXPECTED_TARGETS:
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
    return errors


@contextlib.contextmanager
def historical_membership_view(proposal_dir: Path):
    original_glob = Path.glob

    def filtered_glob(self: Path, pattern: str):
        values = list(original_glob(self, pattern))
        if self == proposal_dir and pattern == "*.json":
            values = [p for p in values if p.name != SUCCESSOR_NAME]
        return iter(values)

    with patch.object(Path, "glob", filtered_glob):
        yield
