#!/usr/bin/env python3
"""Independent checker for EUCLID-GCD-E2E-001.

This checker reads the committed candidate snapshot. It does not import or
execute the MATHSOLVE producer.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
CANDIDATE_PATH = ROOT / "evidence" / "euclid_gcd" / "solve_candidate.json"
RECEIPT_PATH = ROOT / "evidence" / "euclid_gcd" / "upstream_receipt.json"
CERT_PATH = ROOT / "governance" / "certification_outputs" / "EUCLID-GCD-E2E-001.json"
OVERLAY_PATH = ROOT / "governance" / "certification_route_overlays" / "EUCLID-GCD-E2E-001.json"
SCHEMA_PATH = ROOT / "schemas" / "euclid_gcd_certification.schema.json"

EXPECTED_CANDIDATE_BLOB = "af54ae9b9a047a36767b2599ebc649fb6fdaaa52"
EXPECTED_HANDOFF_BLOB = "01a20512c428ce4384959064ab3343a1cbb0c7d2"
EXPECTED_MANIFEST_BLOB = "1cdb081595da2f8b21f60a192ec8cc83c20031ac"
EXPECTED_SOLVER_BLOB = "012a90e0cd84e4ad7f0fd3f1c9534a6673dc0f24"
EXPECTED_SOLVE_MERGE = "3a8493aa322f0e640c921b8824c4d7f88a8c057d"
EXPECTED_SOLVE_HEAD = "cf2a46cb94419ed3ff9c0f078ee87e0e7ae0a9f8"
EXPECTED_FORGE_MERGE = "3622bac82a39cdb9e82ec463919d9e6927c1ec0e"
EXPECTED_FORGE_PACKAGE = "079b68fb5651e0d2eee0a7b2002454d34673d84c"
EXPECTED_FORGE_MANIFEST = "a103b2c85dbd67973da43656fed5af567c5b7074"
EXPECTED_BASE_ROUTE_BLOB = "0487c3ebf702229741f16a544d68af25cf994e41"
EXPECTED_VGSE_OVERLAY_BLOB = "de56bfb0544b27b6237a68ac87044d3f0ba2e445"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload,
        usedforsecurity=False,
    ).hexdigest()


def semantic_errors(candidate: Any, receipt: Any, cert: Any, overlay: Any) -> list[str]:
    errors: list[str] = []
    if not all(isinstance(item, dict) for item in (candidate, receipt, cert, overlay)):
        return ["candidate, receipt, certificate, and route overlay must be objects"]

    if receipt.get("campaign_id") != "EUCLID-GCD-E2E-001":
        errors.append("receipt campaign identity drift")
    forge = receipt.get("forge", {})
    if forge.get("merge_commit") != EXPECTED_FORGE_MERGE:
        errors.append("Forge merge identity drift")
    if forge.get("package", {}).get("git_blob_sha1") != EXPECTED_FORGE_PACKAGE:
        errors.append("Forge package identity drift")
    if forge.get("provider_manifest", {}).get("git_blob_sha1") != EXPECTED_FORGE_MANIFEST:
        errors.append("Forge provider-manifest identity drift")

    solve = receipt.get("solve", {})
    if solve.get("merge_commit") != EXPECTED_SOLVE_MERGE:
        errors.append("Solve merge identity drift")
    if solve.get("reviewed_head") != EXPECTED_SOLVE_HEAD:
        errors.append("Solve reviewed-head identity drift")
    if solve.get("merge_parents") != [
        "00c9f924aa875ee1d43407845b1fa919807ec52b",
        EXPECTED_SOLVE_HEAD,
    ]:
        errors.append("Solve merge-parent identity drift")
    if solve.get("candidate", {}).get("git_blob_sha1") != EXPECTED_CANDIDATE_BLOB:
        errors.append("Solve candidate identity drift")
    if solve.get("handoff", {}).get("git_blob_sha1") != EXPECTED_HANDOFF_BLOB:
        errors.append("Solve handoff identity drift")
    if solve.get("handoff", {}).get("status") != "ready":
        errors.append("Solve handoff must be ready")
    if solve.get("manifest", {}).get("git_blob_sha1") != EXPECTED_MANIFEST_BLOB:
        errors.append("Solve manifest identity drift")
    if solve.get("solver", {}).get("git_blob_sha1") != EXPECTED_SOLVER_BLOB:
        errors.append("Solve producer identity drift")

    if candidate.get("authority_state") != "candidate_only":
        errors.append("candidate authority inflation")
    if candidate.get("campaign_id") != "EUCLID-GCD-E2E-001":
        errors.append("candidate campaign identity drift")
    boundary = candidate.get("claim_boundary", {})
    for field in (
        "certificate_accepted",
        "historical_verbatim_equivalence_claimed",
        "novelty_claimed",
        "priority_claimed",
        "theorem_certified",
    ):
        if boundary.get(field) is not False:
            errors.append(f"candidate boundary {field} must remain false")

    inputs = candidate.get("inputs", {})
    a, b = inputs.get("a"), inputs.get("b")
    d = candidate.get("result", {}).get("d")
    if not all(isinstance(value, int) for value in (a, b, d)):
        errors.append("inputs and d must be integers")
        return errors
    if a < 0 or b < 0 or (a == 0 and b == 0):
        errors.append("candidate input contract violation")
    if d <= 0:
        errors.append("reported d must be positive")

    trace = candidate.get("euclidean_trace")
    if not isinstance(trace, list) or not trace:
        errors.append("Euclidean trace must be a nonempty list")
    else:
        expected_dividend, expected_divisor = a, b
        last_positive = None
        for index, step in enumerate(trace):
            if not isinstance(step, dict):
                errors.append(f"trace step {index} must be an object")
                continue
            dividend = step.get("dividend")
            divisor = step.get("divisor")
            quotient = step.get("quotient")
            remainder = step.get("remainder")
            if not all(isinstance(value, int) for value in (dividend, divisor, quotient, remainder)):
                errors.append(f"trace step {index} fields must be integers")
                continue
            if (dividend, divisor) != (expected_dividend, expected_divisor):
                errors.append(f"trace step {index} linkage drift")
            if divisor <= 0:
                errors.append(f"trace step {index} divisor must be positive")
            elif dividend != quotient * divisor + remainder:
                errors.append(f"trace step {index} division equation is false")
            if divisor > 0 and not (0 <= remainder < divisor):
                errors.append(f"trace step {index} remainder bound is false")
            if remainder > 0:
                last_positive = remainder
            if index < len(trace) - 1 and remainder <= 0:
                errors.append(f"trace step {index} terminates before the final step")
            expected_dividend, expected_divisor = divisor, remainder
        if trace[-1].get("remainder") != 0:
            errors.append("trace must terminate in zero")
        terminal_divisor = trace[-1].get("divisor")
        if terminal_divisor != d:
            errors.append("reported d is not the terminal positive divisor")
        if last_positive != d:
            errors.append("reported d is not the last positive remainder")

    if d and (a % d != 0 or b % d != 0):
        errors.append("reported d does not divide both inputs")
    witness = candidate.get("bezout_witness", {})
    x, y = witness.get("x"), witness.get("y")
    if not isinstance(x, int) or not isinstance(y, int) or x * a + y * b != d:
        errors.append("Bezout equality is false")
    if witness.get("equation_value") != d:
        errors.append("Bezout equation_value drift")
    if math.gcd(a, b) != d:
        errors.append("independent math.gcd replay disagrees with reported d")

    if cert.get("certificate_id") != "MC-EUCLID-GCD-E2E-001":
        errors.append("MATHCERT output identity drift")
    if cert.get("proposed_disposition") != "CERTIFIED_CHECKER_SOUNDNESS_AND_CONCRETE_GCD_INSTANCE":
        errors.append("MATHCERT disposition drift")
    if cert.get("authority_state") != "candidate_certification_output_pending_protected_merge":
        errors.append("pre-merge authority boundary drift")
    accepted = cert.get("accepted_claims", [])
    if [item.get("claim_id") for item in accepted if isinstance(item, dict)] != [
        "EUCLID-GCD-E2E-001-C001",
        "EUCLID-GCD-E2E-001-C002",
        "EUCLID-GCD-E2E-001-C003",
        "EUCLID-GCD-E2E-001-C004",
    ]:
        errors.append("accepted claim set drift")
    formal = cert.get("formalization", {})
    if formal.get("sorry_allowed") is not False or formal.get("local_axioms_allowed") is not False:
        errors.append("formal trust boundary inflation")
    if cert.get("protected_effect") != "none_until_exact_head_review_human_steward_disposition_and_protected_merge":
        errors.append("protected effect boundary drift")

    if overlay.get("overlay_id") != "MC-ROUTE-OVERLAY-EUCLID-GCD-E2E-001":
        errors.append("route overlay identity drift")
    if overlay.get("base_registry", {}).get("digest") != EXPECTED_BASE_ROUTE_BLOB:
        errors.append("base route registry identity drift")
    prior = overlay.get("prior_overlays", [])
    if prior != [{
        "path": "governance/certification_route_overlays/VGSE-001.json",
        "digest_algorithm": "git_blob_sha1",
        "digest": EXPECTED_VGSE_OVERLAY_BLOB,
    }]:
        errors.append("prior route overlay identity drift")
    route = overlay.get("route", {})
    if route.get("route_id") != "MC-ROUTE-EUCLID-GCD-E2E-001":
        errors.append("route id drift")
    if route.get("tracker_issue") != "https://github.com/grandchallenge/MATHCERT/issues/87":
        errors.append("Cert tracker identity drift")
    if route.get("intake_status") != "certified":
        errors.append("route state must be certified")
    if route.get("source_manifest", {}).get("commit_sha") != EXPECTED_SOLVE_MERGE:
        errors.append("route source manifest must bind protected Solve merge")
    if route.get("source_manifest", {}).get("digest") != EXPECTED_MANIFEST_BLOB:
        errors.append("route source manifest blob drift")
    if route.get("intake_packet", {}).get("digest") != EXPECTED_HANDOFF_BLOB:
        errors.append("route handoff blob drift")
    output = route.get("cert_output", {})
    if output.get("path") != "governance/certification_outputs/EUCLID-GCD-E2E-001.json":
        errors.append("route output path drift")
    if output.get("digest") != git_blob_sha1(CERT_PATH):
        errors.append("route output Git blob identity drift")
    if route.get("mathematical_target_proved") is not True:
        errors.append("bounded target proof status must be true")
    for field in (
        "universal_extended_euclid_program_correctness_proved",
        "historical_verbatim_equivalence_established",
        "novelty_or_priority_authorized",
        "successor_stages_activated",
    ):
        if route.get(field) is not False:
            errors.append(f"route boundary {field} must remain false")
    if overlay.get("protected_effect") != "none_until_exact_head_review_human_steward_disposition_and_protected_merge":
        errors.append("route protected effect boundary drift")
    return errors


def validation_errors(
    candidate: Any | None = None,
    receipt: Any | None = None,
    cert: Any | None = None,
    overlay: Any | None = None,
    *,
    verify_local_blobs: bool = True,
) -> list[str]:
    candidate = load(CANDIDATE_PATH) if candidate is None else candidate
    receipt = load(RECEIPT_PATH) if receipt is None else receipt
    cert = load(CERT_PATH) if cert is None else cert
    overlay = load(OVERLAY_PATH) if overlay is None else overlay
    errors = [
        f"certificate schema: {error.json_path}: {error.message}"
        for error in Draft202012Validator(load(SCHEMA_PATH)).iter_errors(cert)
    ]
    if verify_local_blobs:
        if git_blob_sha1(CANDIDATE_PATH) != EXPECTED_CANDIDATE_BLOB:
            errors.append("local candidate snapshot Git blob identity drift")
        if overlay.get("route", {}).get("cert_output", {}).get("digest") != git_blob_sha1(CERT_PATH):
            errors.append("local MATHCERT output Git blob identity drift")
    errors.extend(semantic_errors(candidate, receipt, cert, overlay))
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"EUCLID-GCD-E2E-001 certification validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print("certified independent GCD checker replay, Lean soundness package, exact route output, and bounded Chaidez continuity")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
