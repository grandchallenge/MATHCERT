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
AD = ROOT / "governance/result_family_adjudications/OTP-B1-BINARY-CODES.json"
ADJUDICATION = AD
CONTRACT = ROOT / "governance/result_family_output_contracts/OTP-B1-BINARY-CODES.json"
CERTIFICATE = ROOT / "certificates/formal_sources/MC-OTP-B1-BINARY-CODES-001.json"
ROUTES = ROOT / route_state.ROUTES_REL
REPLAY = ROOT / "governance/result_family_replay_evidence_successors/OTP-B1-BINARY-CODES.json"
WORK_PACKAGE = ROOT / "governance/result_family_work_package_successors/OTP-B1-BINARY-CODES-CERT-WP-001.json"

FAMILY = "OTP-B1-BINARY-CODES"
ROUTE_ID = "MC-ROUTE-OTP-B1-BINARY-CODES"
CERTIFICATE_ID = "MC-OTP-B1-BINARY-CODES-QUAL-001"
CERTIFICATE_CONTENT_COMMIT = "b773fa35a801808ec233f3871fd13d74c9833498"
CERTIFICATE_BLOB = "9e209b10ae814f79635735e6a3d5ee5821082c93"
ADJUDICATION_BLOB = "08a8b3b24185b29114e6c652213b9c2c913b4f1b"
CONTRACT_BLOB = "89b504e2dda11389611f089ac3d9d01ac4d419dd"
REPLAY_BLOB = "fd669ae6cfc39110560656c2123d5d4449200830"
WORK_PACKAGE_BLOB = "19e1eaf5e24ce212bb020c8c40d4177ff5b4f8f9"

TARGETS = [
    "MetricCodes.Hamming.binaryRate_lt_classicalRate",
    "MetricCodes.Hamming.exists_binaryRate_improvement",
    "MetricCodes.Johnson.binaryRate_le_combinedVariationalRate",
    "MetricCodes.MRRW.strict_mrrw2",
    "MetricCodes.Johnson.binaryRate_lt_mrrw",
    "MetricCodes.Johnson.exists_binaryRate_mrrw_improvement",
]
CLASSIFICATIONS = [
    "source_faithful_derived_consequence",
    "derived_positive_margin_certificate",
    "source_faithful_exact_projection",
    "source_faithful_exact_projection",
    "source_faithful_derived_consequence",
    "derived_positive_margin_certificate",
]
QUALIFICATIONS = [
    "The two positive-margin existential targets are derived certificate normal forms, not source-verbatim statements.",
    "The Lean sInf representation of M2 is source-equivalent only through the protected minimizer-existence and attainment bridge on the target domain.",
    "Binary-rate logarithm base, ceiling convention, strict spectral feasibility, and variational domains remain exactly as protected by the Forge audit.",
    "No whole-chapter semantic equivalence or full proof-body comparison is established.",
]


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def blob(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(f"blob {len(payload)}\0".encode() + payload, usedforsecurity=False).hexdigest()


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
    hashes = {
        "adjudication": blob(ADJUDICATION), "contract": blob(CONTRACT),
        "certificate": blob(CERTIFICATE), "replay": blob(REPLAY),
        "work_package": blob(WORK_PACKAGE),
    }
    if local_blobs:
        hashes.update(local_blobs)
    errors: list[str] = []
    for key, expected in {
        "adjudication": ADJUDICATION_BLOB, "contract": CONTRACT_BLOB,
        "certificate": CERTIFICATE_BLOB, "replay": REPLAY_BLOB,
        "work_package": WORK_PACKAGE_BLOB,
    }.items():
        if hashes.get(key) != expected:
            errors.append(f"{key} blob drift")
    if check_history and not is_ancestor(CERTIFICATE_CONTENT_COMMIT):
        errors.append("certificate-content commit is not an ancestor of the route-transition head")
    if check_history:
        changed = subprocess.check_output(
            ["git", "diff", "--name-only", f"{CERTIFICATE_CONTENT_COMMIT}..HEAD"],
            cwd=ROOT, text=True,
        ).splitlines()
        if "certificates/formal_sources/MC-OTP-B1-BINARY-CODES-001.json" in changed:
            errors.append("certificate changed after certificate-content commit")

    if adjudication.get("adjudication_id") != "MC-OTP-B1-BINARY-CODES-ADJUDICATION-001":
        errors.append("adjudication identity drift")
    if adjudication.get("result_family") != FAMILY or adjudication.get("route_id") != ROUTE_ID:
        errors.append("adjudication family/route drift")
    if adjudication.get("encoded_targets") != TARGETS:
        errors.append("adjudication target drift")
    if adjudication.get("classifications") != CLASSIFICATIONS:
        errors.append("adjudication classification drift")
    if adjudication.get("decision", {}).get("disposition") != "adjudication_clear_protected_six_targets_only":
        errors.append("adjudication disposition drift")
    assessment = adjudication.get("evidence_assessment", {})
    for key, expected in {
        "solution_build": "pass", "comparator": "accept",
        "lean_default_kernel": "accept", "nanoda": "accept",
        "trust_boundary_scan": "clear",
        "nonvacuity": "clear_on_protected_parameter_domains",
        "minimizer_attainment": "clear_on_protected_MRRW_domain",
    }.items():
        if assessment.get(key) != expected:
            errors.append(f"adjudication evidence drift: {key}")
    gate = adjudication.get("binding_gate", {})
    for key in (
        "fresh_exact_head_B1_replay_required", "exact_head_cert_required",
        "exact_head_gcl_and_routing_required",
        "fresh_non_author_coding_theory_Lean_specialist_approval_required",
        "expected_head_protected_merge_required", "protected_main_readback_required",
        "head_change_requires_revalidation_and_reapproval",
    ):
        if gate.get(key) is not True:
            errors.append(f"binding gate removed: {key}")

    if contract.get("contract_id") != "MC-OTP-B1-BINARY-CODES-OUTPUT-CONTRACT-001":
        errors.append("output contract identity drift")
    if contract.get("output_scope", {}).get("encoded_targets") != TARGETS:
        errors.append("output contract target drift")
    if contract.get("output_scope", {}).get("classifications") != CLASSIFICATIONS:
        errors.append("output contract classification drift")
    protocol = contract.get("publication_protocol", {})
    if protocol.get("mode") != "certificate_content_commit_then_route_transition_commit":
        errors.append("publication ordering drift")
    for key in (
        "certificate_content_commit_first", "route_transition_commit_must_descend_from_certificate_content_commit",
        "cert_output_commit_sha_must_equal_certificate_content_commit",
        "cert_output_digest_must_equal_certificate_blob", "certificate_must_not_name_its_own_containing_commit",
        "squash_merge_prohibited", "rebase_merge_prohibited", "partial_state_on_protected_main_prohibited",
    ):
        if protocol.get(key) is not True:
            errors.append(f"publication control removed: {key}")

    if certificate.get("certificate_id") != CERTIFICATE_ID:
        errors.append("certificate identity drift")
    if certificate.get("result_family") != FAMILY or certificate.get("route_id") != ROUTE_ID:
        errors.append("certificate family/route drift")
    if certificate.get("encoded_targets") != TARGETS:
        errors.append("certificate target drift")
    if certificate.get("classifications") != CLASSIFICATIONS:
        errors.append("certificate classification drift")
    qualification = certificate.get("qualification", {})
    if qualification.get("disposition") != "qualified_protected_six_targets_only":
        errors.append("certificate disposition drift")
    if qualification.get("mandatory_qualifications") != QUALIFICATIONS:
        errors.append("certificate qualification drift")
    if qualification.get("permitted_axioms") != ["propext", "Quot.sound", "Classical.choice"]:
        errors.append("certificate permitted-axiom drift")
    if certificate.get("state") != {
        "mathematical_target_proved": False,
        "aggregate_authority": False,
        "may_promote_claim": False,
    }:
        errors.append("certificate authority inflation")

    route = next((item for item in routes.get("routes", []) if item.get("campaign_id") == FAMILY), None)
    if not route:
        errors.append("qualified B1 route missing")
    else:
        if route.get("route_id") != ROUTE_ID or route.get("intake_status") != "qualified":
            errors.append("B1 route state drift")
        if route.get("target_claim_ids") != TARGETS:
            errors.append("B1 route target drift")
        expected_output = {
            "repository": "grandchallenge/MATHCERT",
            "commit_sha": CERTIFICATE_CONTENT_COMMIT,
            "path": "certificates/formal_sources/MC-OTP-B1-BINARY-CODES-001.json",
            "digest_algorithm": "git_blob_sha1",
            "digest": CERTIFICATE_BLOB,
        }
        if route.get("cert_output") != expected_output:
            errors.append("B1 route output identity drift")
        boundary = route.get("claim_boundary", "")
        for phrase in ("derived certificate normal forms", "minimizer-existence and attainment bridge", "does not mark a mathematical target proved", "aggregate OpenAI Ten Proofs"):
            if phrase not in boundary:
                errors.append(f"B1 route boundary missing: {phrase}")
        if not route.get("blockers"):
            errors.append("B1 preserved limitations missing")

    if replay.get("evidence_id") != "MC-OTP-B1-BINARY-CODES-REPLAY-EVIDENCE-001":
        errors.append("protected replay identity drift")
    if replay.get("target_scope", {}).get("lean_theorems") != TARGETS:
        errors.append("protected replay target drift")
    producer = replay.get("producer_replay", {})
    for key, expected in {"solution_build": "pass", "comparator": "accept", "lean_default_kernel": "accept", "nanoda": "accept", "trust_boundary_scan": "clear", "theorem_axioms": "permitted_only"}.items():
        if producer.get(key) != expected:
            errors.append(f"protected replay result drift: {key}")
    if work_package.get("target_scope", {}).get("lean_theorems") != TARGETS:
        errors.append("protected work-package target drift")
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("validated OTP-B1 restricted six-target adjudication, certificate-first publication, and qualified route transition")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
