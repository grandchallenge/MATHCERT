#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ADJUDICATION = ROOT / "governance/result_family_adjudications/OTP-I-RAMSEY.json"
CONTRACT = ROOT / "governance/result_family_output_contracts/OTP-I-RAMSEY.json"
CERTIFICATE = ROOT / "certificates/formal_sources/MC-OTP-I-RAMSEY-001.json"
WORK_PACKAGE = ROOT / "governance/result_family_work_package_successors/OTP-I-RAMSEY-CERT-WP-001.json"
INTAKE = ROOT / "governance/result_family_intake_successors/OTP-I-RAMSEY.json"
ROUTES = ROOT / "governance/certification_routes.json"

FAMILY = "OTP-I-RAMSEY"
ROUTE_ID = "MC-ROUTE-OTP-I-RAMSEY"
CONTENT_COMMIT = "18578b7f6917fec0bca4f9b5ea17fbb9541794e6"
CERTIFICATE_BLOB = "34e45c5dd08a3bb19fc27bc1f7da4ec71b3e1d31"
ADJUDICATION_BLOB = "87f28ab459651045068a03cac948bb2e8b2f0d8f"
CONTRACT_BLOB = "870bb25044a5e703ef96036252ab2275b7c831b3"
WORK_PACKAGE_BLOB = "2925af4dc5db8b5cb751cf986803048f849a9a8b"
INTAKE_BLOB = "e9302a671ebdb041fed3ad4bf5097b5deb78fb64"
TARGETS = [
    "ErdosProblems.MulticolourTriangleRamsey.erdos_183",
    "ErdosProblems.MulticolourTriangleRamsey.erdos_problem_183_explicit",
    "ErdosProblems.MulticolourTriangleRamsey.triangleRamseyNumber_log_sharp_coefficients",
    "ErdosProblems.MulticolourTriangleRamsey.triangleRamseyNumber_log_isTheta",
]
CLASSIFICATIONS = [
    "source_faithful_exact_projection_of_displayed_consequence_4",
    "formal_explicit_constant_strengthening_plus_source_faithful_divergence",
    "source_faithful_epsilonized_logarithmic_reformulation",
    "source_faithful_logarithmic_reformulation_of_printed_theta",
]
QUALIFICATIONS = [
    "The manuscript does not specify the explicit constant 1/(6*exp 38); it is formal strengthening provenance only.",
    "The epsilon logarithmic coefficients are source-faithful natural-log reformulations, not verbatim source text.",
    "Filter-Theta is a source-faithful reformulation of printed R_k(3)=k^{Theta(k)}.",
    "Least-Ramsey-number semantics rely on the protected nonempty forcing set and sInf realization evidence.",
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
        if "certificates/formal_sources/MC-OTP-I-RAMSEY-001.json" in changed:
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
    if adj.get("decision", {}).get("disposition") != "adjudication_clear_protected_four_targets_only":
        errors.append("adjudication disposition drift")
    for key in ("fresh_exact_head_I_replay_required", "exact_head_cert_gcl_and_routing_required",
                "fresh_non_author_ramsey_combinatorics_Lean_specialist_approval_required",
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
    if qualification.get("disposition") != "qualified_protected_four_targets_only" or qualification.get("mandatory_qualifications") != QUALIFICATIONS:
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
                       "path": "certificates/formal_sources/MC-OTP-I-RAMSEY-001.json",
                       "digest_algorithm": "git_blob_sha1", "digest": CERTIFICATE_BLOB}
    if not route:
        errors.append("qualified I route missing")
    else:
        if route.get("route_id") != ROUTE_ID or route.get("intake_status") != "qualified":
            errors.append("qualified I route state drift")
        if route.get("target_claim_ids") != TARGETS:
            errors.append("qualified I route target drift")
        if route.get("cert_output") != expected_output:
            errors.append("qualified I route output identity drift")
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("validated OTP-I restricted four-target adjudication, certificate-first publication, and qualified route")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
