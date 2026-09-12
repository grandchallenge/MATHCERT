#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import certification_route_state as route_state

ROOT = Path(__file__).resolve().parents[1]
ADJUDICATION = ROOT / "governance/result_family_adjudications/OTP-H-GAPCVP.json"
CONTRACT = ROOT / "governance/result_family_output_contracts/OTP-H-GAPCVP.json"
CERTIFICATE = ROOT / "certificates/formal_sources/MC-OTP-H-GAPCVP-001.json"
ROUTES = ROOT / route_state.ROUTES_REL
REPLAY = ROOT / "governance/result_family_replay_evidence_successors/OTP-H-GAPCVP.json"
WORK_PACKAGE = ROOT / "governance/result_family_work_package_successors/OTP-H-GAPCVP-CERT-WP-001.json"

FAMILY = "OTP-H-GAPCVP"
ROUTE_ID = "MC-ROUTE-OTP-H-GAPCVP"
CERTIFICATE_ID = "MC-OTP-H-GAPCVP-QUAL-001"
CERTIFICATE_CONTENT_COMMIT = "669e50b7394b7a6cc8b4ede3d8d85efb923f9044"
ADJUDICATION_BLOB = "c28768a2840050548f25ec92ef46f9b355b5cadb"
CONTRACT_BLOB = "1bcffa57c9e07dc0a224f13c84e9ec0597429b92"
CERTIFICATE_BLOB = "88b24b5e850676d89267467ea05e21d6dddca9d0"
REPLAY_BLOB = "a12f2c553b71f4daec9255e1f254f48a21f439c3"
WORK_PACKAGE_BLOB = "0f811d163f0d36b028cf6539963e2cf278517137"

TARGETS = [
    "GapCVP.Comparator.gapCVP400IsNPHard",
    "GapCVP.Comparator.binaryNearestCodewordIsNPHard",
    "GapCVP.Comparator.binarySyndromeDecodingIsNPHard",
    "GapCVP.Comparator.finitePNormGapCVPIsNPHard",
]
PROMISES = [
    "GapCVP.Comparator.gapCVP400Promise",
    "GapCVP.Comparator.binaryNearestCodewordPromise",
    "GapCVP.Comparator.binarySyndromeDecodingPromise",
    "GapCVP.Comparator.finitePGapCVPPromise",
]
CLASSIFICATIONS = [
    "source_faithful_restricted_consequence_integer_target",
    "source_faithful_up_to_generator_orientation",
    "source_faithful_restricted_consequence_consistent_syndrome",
    "source_faithful_fixed_rational_p_consequence",
]
GAPS = ["n^(1/400)", "n^(1/200)", "n^(1/200)", "n^(1/(200p))"]


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data, usedforsecurity=False).hexdigest()


def is_ancestor(ancestor: str, descendant: str = "HEAD") -> bool:
    return subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    ).returncode == 0


def validation_errors(*, adjudication: Any | None = None, contract: Any | None = None,
                      certificate: Any | None = None, routes: Any | None = None,
                      replay: Any | None = None, work_package: Any | None = None,
                      local_blobs: dict[str, str] | None = None,
                      check_history: bool = True) -> list[str]:
    adjudication = load(ADJUDICATION) if adjudication is None else adjudication
    contract = load(CONTRACT) if contract is None else contract
    certificate = load(CERTIFICATE) if certificate is None else certificate
    routes = load(ROUTES) if routes is None else routes
    replay = load(REPLAY) if replay is None else replay
    work_package = load(WORK_PACKAGE) if work_package is None else work_package
    hashes = local_blobs or {
        "adjudication": blob(ADJUDICATION), "contract": blob(CONTRACT),
        "certificate": blob(CERTIFICATE), "replay": blob(REPLAY),
        "work_package": blob(WORK_PACKAGE),
    }
    errors: list[str] = []
    expected_hashes = {
        "adjudication": ADJUDICATION_BLOB, "contract": CONTRACT_BLOB,
        "certificate": CERTIFICATE_BLOB, "replay": REPLAY_BLOB,
        "work_package": WORK_PACKAGE_BLOB,
    }
    for key, expected in expected_hashes.items():
        if hashes.get(key) != expected:
            errors.append(f"{key} blob drift")

    if check_history and not is_ancestor(CERTIFICATE_CONTENT_COMMIT):
        errors.append("certificate-content commit is not an ancestor of the route transition")

    common = (adjudication, contract, certificate)
    for name, record in zip(("adjudication", "contract", "certificate"), common):
        if record.get("result_family") != FAMILY or record.get("route_id") != ROUTE_ID:
            errors.append(f"{name} family/route drift")
    if adjudication.get("encoded_targets") != TARGETS:
        errors.append("adjudication target drift")
    if adjudication.get("promise_interfaces") != PROMISES:
        errors.append("adjudication promise drift")
    if adjudication.get("classifications") != CLASSIFICATIONS:
        errors.append("adjudication classification drift")
    if adjudication.get("gap_factors") != GAPS:
        errors.append("adjudication gap-factor drift")
    decision = adjudication.get("decision", {})
    if decision.get("disposition") != "adjudication_clear_protected_four_targets_only":
        errors.append("adjudication disposition drift")
    if decision.get("does_not_mark_mathematical_target_proved") is not True:
        errors.append("adjudication proof boundary removed")
    if decision.get("does_not_totalize_outside_promise_inputs") is not True:
        errors.append("adjudication outside-promise boundary removed")
    assessment = adjudication.get("evidence_assessment", {})
    for key, expected in {
        "solution_build": "pass", "comparator": "accept",
        "lean_default_kernel": "accept", "nanoda": "accept",
        "trust_boundary_scan": "clear",
        "whole_document_equivalence": "not_established",
        "proof_body_compared_in_full": False,
    }.items():
        if assessment.get(key) != expected:
            errors.append(f"adjudication evidence drift: {key}")

    scope = contract.get("output_scope", {})
    if scope.get("encoded_targets") != TARGETS or scope.get("promise_interfaces") != PROMISES:
        errors.append("output contract target/promise drift")
    if scope.get("classifications") != CLASSIFICATIONS:
        errors.append("output contract classification drift")
    if scope.get("permitted_disposition") != "qualified_protected_four_targets_only":
        errors.append("output contract disposition drift")
    protocol = contract.get("publication_protocol", {})
    if protocol.get("mode") != "certificate_content_commit_then_route_transition_commit":
        errors.append("publication order drift")
    for key in ("certificate_content_commit_first", "route_transition_commit_must_descend_from_certificate_content_commit", "cert_output_commit_sha_must_equal_certificate_content_commit", "cert_output_digest_must_equal_certificate_blob", "squash_merge_prohibited", "rebase_merge_prohibited", "partial_state_on_protected_main_prohibited"):
        if protocol.get(key) is not True:
            errors.append(f"publication safeguard removed: {key}")

    if certificate.get("certificate_id") != CERTIFICATE_ID:
        errors.append("certificate identity drift")
    if certificate.get("encoded_targets") != TARGETS or certificate.get("promise_interfaces") != PROMISES:
        errors.append("certificate target/promise drift")
    if certificate.get("classifications") != CLASSIFICATIONS or certificate.get("gap_factors") != GAPS:
        errors.append("certificate classification/gap drift")
    qualification = certificate.get("qualification", {})
    if qualification.get("disposition") != "qualified_protected_four_targets_only":
        errors.append("certificate disposition drift")
    if qualification.get("permitted_axioms") != ["propext", "Quot.sound", "Classical.choice"]:
        errors.append("certificate axiom boundary drift")
    for name, record in (("adjudication", adjudication), ("certificate", certificate)):
        state = record.get("state", {})
        if state.get("mathematical_target_proved") is not False:
            errors.append(f"{name} mathematical target promotion")
        if state.get("may_promote_claim") is not False:
            errors.append(f"{name} claim-promotion authority")

    if replay.get("evidence_id") != "MC-OTP-H-GAPCVP-REPLAY-EVIDENCE-001":
        errors.append("replay evidence identity drift")
    if work_package.get("work_package_id") != "OTP-H-GAPCVP-CERT-WP-001":
        errors.append("work-package identity drift")
    route = next((r for r in routes.get("routes", []) if r.get("route_id") == ROUTE_ID), {})
    if route.get("campaign_id") != FAMILY or route.get("intake_status") != "qualified":
        errors.append("H route state drift")
    if route.get("target_claim_ids") != TARGETS:
        errors.append("H route target drift")
    output = route.get("cert_output", {})
    expected_output = {
        "repository": "grandchallenge/MATHCERT",
        "commit_sha": CERTIFICATE_CONTENT_COMMIT,
        "path": "certificates/formal_sources/MC-OTP-H-GAPCVP-001.json",
        "digest_algorithm": "git_blob_sha1",
        "digest": CERTIFICATE_BLOB,
    }
    if output != expected_output:
        errors.append("H route output identity drift")
    boundary = route.get("claim_boundary", "")
    for phrase in ("does not mark a mathematical target proved", "integer-target", "consistent-syndrome", "outside-promise", "fixed rational p", "aggregate OpenAI Ten Proofs authority"):
        if phrase not in boundary:
            errors.append(f"H route boundary missing: {phrase}")
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("validated OTP-H restricted four-target/four-promise adjudication, certificate-first publication, and qualified route transition")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
