#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import validate_openai_ten_proofs_adjudication_contracts as design
import validate_openai_ten_proofs_route_registrations_with_j2_successor as route_registration

ROOT = Path(__file__).resolve().parents[1]
ADJUDICATION_DIR = ROOT / "governance/result_family_adjudications"
CERT_DIR = ROOT / "certificates/openai_ten_proofs"
FULL_FORMULA_ADJUDICATION = ADJUDICATION_DIR / "OTP-C-PERMANENT-FULL-FORMULA.json"
CIRCUIT_ADJUDICATION = ADJUDICATION_DIR / "OTP-C-PERMANENT-CIRCUIT.json"
EXPECTED_FULL_FORMULA_ADJUDICATION_BLOB = "2b5f0cd02b53365a8504a325594a7fc366682db0"
EXPECTED_CIRCUIT_ADJUDICATION_BLOB = "6d984e4595da02648d3db110ba1ff6a1a268e4ae"
FULL_FORMULA_TARGETS = [
    "PermanentFormulaLowerBound.permanent_divisionFree_formula_lower_bound",
    "PermanentFormulaLowerBound.permanent_rational_formula_lower_bound",
]
CIRCUIT_TARGETS = [
    "PermanentRollout.permanent_circuit_loglog_lower_bound",
    "PermanentRollout.permanent_circuit_loglog_bigOmega",
    "PermanentRollout.permanent_complexity_ratio_tendsto_atTop",
]
ALLOWED_ADJUDICATIONS = {
    "OTP-F-EHRHART.json",
    "OTP-C-PERMANENT.json",
    "OTP-C-PERMANENT-FULL-FORMULA.json",
    "OTP-C-PERMANENT-CIRCUIT.json",
    "OTP-J1-COMPACTNESS.json",
    "OTP-J2-TWO-DEGENERATE.json",
}


def git_blob_sha1(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload,
        usedforsecurity=False,
    ).hexdigest()


def design_routes_snapshot() -> dict:
    return route_registration.registration_snapshot(design.load(design.D.ROUTES))


def validate_full_formula_candidate() -> list[str]:
    errors: list[str] = []
    if not FULL_FORMULA_ADJUDICATION.is_file():
        return ["missing governed full-formula candidate adjudication"]
    if git_blob_sha1(FULL_FORMULA_ADJUDICATION) != EXPECTED_FULL_FORMULA_ADJUDICATION_BLOB:
        return ["full-formula candidate adjudication blob drift"]
    record = json.loads(FULL_FORMULA_ADJUDICATION.read_text(encoding="utf-8"))
    if record.get("route_id") != "MC-ROUTE-OTP-C-PERMANENT-FULL-FORMULA":
        errors.append("full-formula adjudication route drift")
    if record.get("state") != "candidate_disposition_pending_exact_head_gates_review_and_protected_merge":
        errors.append("full-formula adjudication state inflation")
    if record.get("disposition") != "adjudication_clear_encoded_targets_only":
        errors.append("full-formula adjudication disposition drift")
    if record.get("encoded_targets") != FULL_FORMULA_TARGETS:
        errors.append("full-formula adjudication target drift")
    basis = record.get("basis", {})
    if basis.get("fresh_exact_head_replay_required") is not True:
        errors.append("full-formula adjudication fresh replay gate removed")
    if basis.get("fresh_non_author_specialist_review_required") is not True:
        errors.append("full-formula adjudication specialist review gate removed")
    judgment = record.get("judgment", {})
    if judgment.get("mathematical_target_proved") is not False:
        errors.append("full-formula adjudication mathematical proof promotion")
    if judgment.get("claim_promotion_authorized") is not False:
        errors.append("full-formula adjudication claim-promotion inflation")
    if judgment.get("aggregate_authority") is not False:
        errors.append("full-formula adjudication aggregate-authority inflation")
    return errors


def validate_circuit_candidate() -> list[str]:
    errors: list[str] = []
    if not CIRCUIT_ADJUDICATION.is_file():
        return ["missing governed circuit candidate adjudication"]
    if git_blob_sha1(CIRCUIT_ADJUDICATION) != EXPECTED_CIRCUIT_ADJUDICATION_BLOB:
        return ["circuit candidate adjudication blob drift"]
    record = json.loads(CIRCUIT_ADJUDICATION.read_text(encoding="utf-8"))
    if record.get("route_id") != "MC-ROUTE-OTP-C-PERMANENT-CIRCUIT":
        errors.append("circuit adjudication route drift")
    if record.get("state") != "candidate_disposition_pending_exact_head_gates_review_and_protected_merge":
        errors.append("circuit adjudication state inflation")
    if record.get("disposition") != "adjudication_clear_encoded_targets_only":
        errors.append("circuit adjudication disposition drift")
    if record.get("encoded_targets") != CIRCUIT_TARGETS:
        errors.append("circuit adjudication target drift")
    basis = record.get("basis", {})
    if basis.get("fresh_exact_head_replay_required") is not True:
        errors.append("circuit adjudication fresh replay gate removed")
    if basis.get("fresh_non_author_specialist_review_required") is not True:
        errors.append("circuit adjudication specialist review gate removed")
    projection = record.get("source_projection", {})
    if projection.get("coefficient_field") != "complex":
        errors.append("circuit coefficient field drift")
    if projection.get("model") != "division_free_arithmetic_circuit_dag":
        errors.append("circuit model drift")
    if projection.get("division_allowed") is not False:
        errors.append("circuit division enabled")
    if projection.get("fanout_reuse_allowed") is not True:
        errors.append("circuit fanout reuse removed")
    if projection.get("size_counts_arithmetic_gates_only") is not True or projection.get("input_gates_counted") is not False:
        errors.append("circuit size accounting drift")
    if projection.get("dimension_threshold") != 65536 or projection.get("finite_bound_denominator") != 144:
        errors.append("circuit threshold/denominator drift")
    judgment = record.get("judgment", {})
    for key in ("mathematical_target_proved", "claim_promotion_authorized", "formula_targets_certified", "other_family_outputs_authorized", "aggregate_authority", "historical_pdf_byte_equivalence"):
        if judgment.get(key) is not False:
            errors.append(f"circuit adjudication authority inflation: {key}")
    return errors


def validation_errors() -> list[str]:
    errors = design.validation_errors(
        routes=design_routes_snapshot(),
        executed_present=False,
        route_blob=design.D.ROUTE_REGISTRY_BLOB,
    )
    actual_adjudications = {
        path.name for path in ADJUDICATION_DIR.glob("*.json") if path.is_file()
    } if ADJUDICATION_DIR.is_dir() else set()
    if actual_adjudications != ALLOWED_ADJUDICATIONS:
        errors.append(
            "separately governed adjudication membership drift: "
            f"expected {sorted(ALLOWED_ADJUDICATIONS)}, got {sorted(actual_adjudications)}"
        )
    errors += validate_full_formula_candidate()
    errors += validate_circuit_candidate()
    actual_outputs = {
        path.name for path in CERT_DIR.glob("*.json") if path.is_file()
    } if CERT_DIR.is_dir() else set()
    if actual_outputs:
        errors.append(f"unauthorized legacy OTP Cert output artifacts exist: {sorted(actual_outputs)}")
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(
            f"successor-aware adjudication design validation failed with {len(errors)} error(s)",
            file=sys.stderr,
        )
        return 1
    print(
        "validated immutable design-only adjudication contracts against their historical registration "
        "snapshots, including J2, the protected Permanent full-formula successor, the bounded Permanent "
        "circuit candidate adjudication with exact model/replay/review gates intact, the separately governed "
        "historical adjudication records, and no legacy OTP output artifact"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
