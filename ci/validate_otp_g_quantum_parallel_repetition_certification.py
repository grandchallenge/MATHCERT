#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ADJUDICATION = ROOT / "governance/result_family_adjudications/OTP-G-QUANTUM-PARALLEL-REPETITION.json"
CONTRACT = ROOT / "governance/result_family_output_contracts/OTP-G-QUANTUM-PARALLEL-REPETITION.json"
CERTIFICATE = ROOT / "certificates/formal_sources/MC-OTP-G-QUANTUM-PARALLEL-REPETITION-001.json"
WORK_PACKAGE = ROOT / "governance/result_family_work_package_successors/OTP-G-QUANTUM-PARALLEL-REPETITION-CERT-WP-001.json"
INTAKE = ROOT / "governance/result_family_intake_successors/OTP-G-QUANTUM-PARALLEL-REPETITION.json"
ROUTES = ROOT / "governance/certification_routes.json"

FAMILY = "OTP-G-QUANTUM-PARALLEL-REPETITION"
ROUTE_ID = "MC-ROUTE-OTP-G-QUANTUM-PARALLEL-REPETITION"
CONTENT_COMMIT = "5bed0523102195bafe9dcd63103f960d47159f2b"
CERTIFICATE_BLOB = "4c7e5f091ddead5913733810933fa5f60f4dc11b"
ADJUDICATION_BLOB = "e36344cc99c01b09651c84ea40de9c0dfe180777"
CONTRACT_BLOB = "63c6151a0cd055aa4de595db29a58a9a1d2f46c3"
WORK_PACKAGE_BLOB = "fcd9291b9286a07c977efdf48d71e75de4c90a1e"
INTAKE_BLOB = "b191a8064fda990edaa3f0b291afe801716587ff"
TARGETS = [
    "QuantumParallelRepetition.distributionUniformExponential",
    "QuantumParallelRepetition.standardQuantumParallelRepetition",
]
CLASSIFICATIONS = [
    "source_faithful_exact_coordinate_projection_of_theorem_1_1",
    "source_faithful_consequence_on_source_domain_with_formal_empty_answer_extension",
]
QUALIFICATIONS = [
    "Alice and Bob may have independent finite local dimensions; no common-dimension restriction is introduced.",
    "entangledValue is a supremum, with no optimizer-attainment assumption.",
    "The quantitative target preserves exponent 13, the exact epsilon + log(|A||B|) denominator, positive soundness gap, and n>=1 scope.",
    "The qualitative target is source-faithful only on the manuscript nonempty-answer domain; empty-answer cases are formal-only.",
    "No whole-chapter semantic equivalence or proof-body comparison is transferred.",
]


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def blob(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(f"blob {len(payload)}\0".encode() + payload, usedforsecurity=False).hexdigest()


def validation_errors(*, adjudication: Any | None = None, contract: Any | None = None,
                      certificate: Any | None = None, work_package: Any | None = None,
                      intake: Any | None = None, routes: Any | None = None,
                      local_blobs: dict[str, str] | None = None,
                      check_history: bool = True) -> list[str]:
    records = {
        "adjudication": load(ADJUDICATION) if adjudication is None else adjudication,
        "contract": load(CONTRACT) if contract is None else contract,
        "certificate": load(CERTIFICATE) if certificate is None else certificate,
        "work_package": load(WORK_PACKAGE) if work_package is None else work_package,
        "intake": load(INTAKE) if intake is None else intake,
        "routes": load(ROUTES) if routes is None else routes,
    }
    hashes = {"adjudication": blob(ADJUDICATION), "contract": blob(CONTRACT),
              "certificate": blob(CERTIFICATE), "work_package": blob(WORK_PACKAGE),
              "intake": blob(INTAKE)}
    if local_blobs:
        hashes.update(local_blobs)
    errors: list[str] = []
    for key, expected in {"adjudication": ADJUDICATION_BLOB, "contract": CONTRACT_BLOB,
                          "certificate": CERTIFICATE_BLOB, "work_package": WORK_PACKAGE_BLOB,
                          "intake": INTAKE_BLOB}.items():
        if hashes.get(key) != expected:
            errors.append(f"{key} blob drift")
    if check_history:
        if subprocess.run(["git", "merge-base", "--is-ancestor", CONTENT_COMMIT, "HEAD"], cwd=ROOT).returncode:
            errors.append("certificate-content commit is not an ancestor of route transition")
        changed = subprocess.check_output(["git", "diff", "--name-only", f"{CONTENT_COMMIT}..HEAD"], cwd=ROOT, text=True).splitlines()
        if "certificates/formal_sources/MC-OTP-G-QUANTUM-PARALLEL-REPETITION-001.json" in changed:
            errors.append("certificate changed after certificate-content commit")

    adj, contract, cert, wp, intake_record, routes_record = (
        records["adjudication"], records["contract"], records["certificate"],
        records["work_package"], records["intake"], records["routes"],
    )
    for label, record in (("adjudication", adj), ("contract", contract), ("certificate", cert)):
        if record.get("result_family") != FAMILY or record.get("route_id") != ROUTE_ID:
            errors.append(f"{label} identity drift")
    for label, record in (("adjudication", adj), ("certificate", cert)):
        if record.get("encoded_targets") != TARGETS or record.get("classifications") != CLASSIFICATIONS:
            errors.append(f"{label} target or classification drift")
    if adj.get("mandatory_qualifications") != QUALIFICATIONS:
        errors.append("adjudication qualification drift")
    if adj.get("decision", {}).get("disposition") != "adjudication_clear_protected_two_targets_only":
        errors.append("adjudication disposition drift")
    for key in ("fresh_exact_head_G_replay_required", "exact_head_cert_gcl_and_routing_required",
                "fresh_non_author_quantum_information_Lean_specialist_approval_required",
                "expected_head_protected_merge_required", "protected_main_readback_required",
                "head_change_requires_revalidation_and_reapproval"):
        if adj.get("binding_gate", {}).get(key) is not True:
            errors.append(f"binding gate removed: {key}")
    if contract.get("output_scope", {}).get("encoded_targets") != TARGETS or contract.get("output_scope", {}).get("classifications") != CLASSIFICATIONS:
        errors.append("output contract scope drift")
    for key in ("certificate_content_commit_first", "route_transition_commit_must_descend_from_certificate_content_commit",
                "cert_output_commit_sha_must_equal_certificate_content_commit", "cert_output_digest_must_equal_certificate_blob",
                "certificate_must_not_name_its_own_containing_commit", "squash_merge_prohibited",
                "rebase_merge_prohibited", "partial_state_on_protected_main_prohibited"):
        if contract.get("publication_protocol", {}).get(key) is not True:
            errors.append(f"publication control removed: {key}")
    qualification = cert.get("qualification", {})
    if qualification.get("disposition") != "qualified_protected_two_targets_only" or qualification.get("mandatory_qualifications") != QUALIFICATIONS:
        errors.append("certificate qualification drift")
    if qualification.get("permitted_axioms") != ["propext", "Quot.sound", "Classical.choice"]:
        errors.append("certificate permitted-axiom drift")
    if cert.get("state") != {"mathematical_target_proved": False, "aggregate_authority": False, "may_promote_claim": False}:
        errors.append("certificate authority inflation")
    if wp.get("target_scope", {}).get("lean_theorems") != TARGETS or wp.get("target_scope", {}).get("classifications") != CLASSIFICATIONS:
        errors.append("work-package scope drift")
    if wp.get("target_scope", {}).get("mandatory_qualifications") != QUALIFICATIONS:
        errors.append("work-package qualification drift")
    if intake_record.get("target_scope", {}).get("lean_theorems") != TARGETS:
        errors.append("protected intake target drift")
    route = next((item for item in routes_record.get("routes", []) if item.get("campaign_id") == FAMILY), None)
    expected_output = {"repository": "grandchallenge/MATHCERT", "commit_sha": CONTENT_COMMIT,
                       "path": "certificates/formal_sources/MC-OTP-G-QUANTUM-PARALLEL-REPETITION-001.json",
                       "digest_algorithm": "git_blob_sha1", "digest": CERTIFICATE_BLOB}
    if not route:
        errors.append("qualified G route missing")
    else:
        if route.get("route_id") != ROUTE_ID or route.get("intake_status") != "qualified":
            errors.append("qualified G route state drift")
        if route.get("target_claim_ids") != TARGETS:
            errors.append("qualified G route target drift")
        if route.get("cert_output") != expected_output:
            errors.append("qualified G route output identity drift")
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("validated OTP-G restricted two-target adjudication, certificate-first publication, and qualified route")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
