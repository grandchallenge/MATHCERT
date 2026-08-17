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
EXPECTED_FULL_FORMULA_ADJUDICATION_BLOB = "2b5f0cd02b53365a8504a325594a7fc366682db0"
FULL_FORMULA_TARGETS = [
    "PermanentFormulaLowerBound.permanent_divisionFree_formula_lower_bound",
    "PermanentFormulaLowerBound.permanent_rational_formula_lower_bound",
]
ALLOWED_ADJUDICATIONS = {
    "OTP-F-EHRHART.json",
    "OTP-C-PERMANENT.json",
    "OTP-C-PERMANENT-FULL-FORMULA.json",
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
        "snapshots, including the explicit J2 source-faithful route successor, the exact bounded "
        "Permanent full-formula candidate adjudication with replay/review gates intact, the separately "
        "governed historical adjudication records, and no legacy OTP output artifact"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
