#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

import validate_openai_ten_proofs_sphere_packing_route_registration as sphere_registration

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "governance/result_family_adjudications/OTP-J2-TWO-DEGENERATE.json"
SCHEMA = ROOT / "schemas/openai_ten_proofs_j2_adjudication.schema.json"
ROUTES = ROOT / "governance/certification_routes.json"

TARGETS = [
    "TwoDegenerateGraphs.mathcert_sourceFaithfulTwoDegenerateExtremalCounterexample",
    "TwoDegenerateGraphs.mathcert_sourceFaithfulNotErdos146",
]
OUTPUT_CONTRACT_MERGE = "d1f0d69e145029e8b7bc29c0ec60543f7db29272"
OUTPUT_CERTIFICATE_COMMIT = "24cff6e55709c067c7f966c1a533255af707bec0"
OUTPUT_ROUTE_COMMIT = "15559390e2489ae73d872f389a9601c7412b77ed"
OUTPUT_CERTIFICATE_BLOB = "308a2eb7087fb24a07a6ae8c93a83b593468d2f7"
OUTPUT_CERTIFICATE_PATH = "certificates/formal_sources/MC-OTP-J2-TWO-DEGENERATE-001.json"
OUTPUT_CERT = {
    "repository": "grandchallenge/MATHCERT",
    "commit_sha": OUTPUT_CERTIFICATE_COMMIT,
    "path": OUTPUT_CERTIFICATE_PATH,
    "digest_algorithm": "git_blob_sha1",
    "digest": OUTPUT_CERTIFICATE_BLOB,
}
EXPECTED = {
    "record_blob": "87286722951770b3383de2eedba30f2b53e0dabc",
    "input_blob": "bd18b84bc257b7f06b875a6cf5fa4c038eb7c3cd",
    "contract_blob": "1feaeac515beb792c5552bc795826bd999f4e535",
    "successor_blob": "5b72e13448cdbea88e0f2cf1e637c2d787b297a6",
    "historical_route_blob": "eb2ad35f73ec1f7a29c7432aa9e5ad299116dbfe",
    "live_route_blob": "2d17473b4731aa9d9c630b1e7777ad4bd794d993",
    "a_registration_route_blob": "b9bb0dc9e18856f50a88162df37c20c034327439",
    "evidence_blob": "e1bc1f04daf28b04a85e92e605732f466ab1e2d6",
    "runtime_head": "863447a7b6abeeee6b113e27057730036318ea0f",
    "runtime_run": 31928781876,
    "runtime_job": 95120424098,
    "runtime_artifact": 9258729796,
    "runtime_artifact_sha256": "eca8e392bc620e5da0e7e709dfd0733a9797a679cc520ec69e38312851868853",
}
OBJECTS = {
    "governance/result_family_adjudications/OTP-J2-TWO-DEGENERATE.json": EXPECTED["record_blob"],
    "governance/result_family_adjudication_execution_inputs/OTP-J2-TWO-DEGENERATE.json": EXPECTED["input_blob"],
    "governance/result_family_adjudication_contract_successors/OTP-J2-TWO-DEGENERATE.json": EXPECTED["contract_blob"],
    "governance/result_family_route_target_successors/OTP-J2-TWO-DEGENERATE.json": EXPECTED["successor_blob"],
    "governance/result_family_construction_evidence/OTP-J2-TWO-DEGENERATE.json": EXPECTED["evidence_blob"],
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(ROOT), *args], text=True, capture_output=True, check=check)


def repo_blob(rel: str) -> str:
    return git("rev-parse", f"HEAD:{rel}").stdout.strip()


def commit_blob(commit: str, rel: str) -> str:
    return git("rev-parse", f"{commit}:{rel}").stdout.strip()


def is_ancestor(sha: str) -> bool:
    return git("merge-base", "--is-ancestor", sha, "HEAD", check=False).returncode == 0


def find_route(node: Any, route_id: str) -> dict[str, Any] | None:
    if isinstance(node, dict):
        if node.get("route_id") == route_id:
            return node
        for value in node.values():
            hit = find_route(value, route_id)
            if hit is not None:
                return hit
    elif isinstance(node, list):
        for value in node:
            hit = find_route(value, route_id)
            if hit is not None:
                return hit
    return None


def validation_errors(record: dict[str, Any] | None = None, *, check_repository: bool = True) -> list[str]:
    record = load(RECORD) if record is None else record
    errors: list[str] = []

    schema = load(SCHEMA)
    for err in Draft202012Validator(schema).iter_errors(record):
        errors.append(f"closed schema: {err.message}")

    if record.get("encoded_targets") != TARGETS:
        errors.append("adjudication target drift")
    if record.get("decision", {}).get("disposition") != "adjudication_clear_source_faithful_targets_only":
        errors.append("adjudication disposition drift")
    if record.get("decision", {}).get("scope") != "exact_two_source_faithful_targets_only":
        errors.append("adjudication scope drift")
    if record.get("decision", {}).get("stronger_coloring_property_excluded") is not True:
        errors.append("stronger coloring exclusion lost")

    authority = record.get("authority", {})
    contract = authority.get("protected_contract", {})
    if contract.get("streamlined_control_plan_applies") is not True:
        errors.append("streamlined control plan disabled")
    if contract.get("separate_human_steward_authorization_required") is not False:
        errors.append("redundant Human Steward gate reintroduced")
    if contract.get("execution_authorized_by_protected_contract") is not True:
        errors.append("protected-contract execution authority missing")
    if contract.get("human_steward_intervention_required_only_for_control_plan_change") is not True:
        errors.append("control-plan intervention boundary weakened")

    runtime = record.get("fresh_execution", {})
    expected_runtime = {
        "execution_head": EXPECTED["runtime_head"],
        "workflow_run_id": EXPECTED["runtime_run"],
        "replay_job_id": EXPECTED["runtime_job"],
        "artifact_id": EXPECTED["runtime_artifact"],
        "artifact_sha256": EXPECTED["runtime_artifact_sha256"],
        "literal_head_checkout_verified": True,
        "current_source_reacquired": True,
        "construction_reverified": True,
        "comparator": "pass_derivation_carrier_only",
        "lean_kernel": "accept",
        "nanoda": "accept",
        "source_faithful_projection": "accept",
        "dependency_separation": "accept",
        "trust_boundary": "clear",
        "input_mutations_rejected": 24,
    }
    for key, expected in expected_runtime.items():
        if runtime.get(key) != expected:
            errors.append(f"runtime provenance/result drift: {key}")
    if runtime.get("theorem_axioms") != ["propext", "Classical.choice", "Quot.sound"]:
        errors.append("theorem axiom set drift")
    if runtime.get("nonvacuity") != "clear_both_source_faithful_declarations_accept_and_refutation_uses_source_core_only":
        errors.append("nonvacuity drift")

    source = record.get("source_assessment", {})
    if source.get("current_sha256") != "ebc561ab5c53dbd240e17a8fdb6fffeb648591eca85dbfc7466f563638f8c566":
        errors.append("current source identity drift")
    if source.get("statement_concordance") != "clear_for_exact_source_faithful_theorem_1_2_core":
        errors.append("source-statement concordance drift")
    if source.get("stronger_coloring_property_source_authorized") is not False:
        errors.append("stronger coloring property source-authorized")
    if source.get("proof_body_compared_in_full") is not False:
        errors.append("proof-body overclaim")

    construction = record.get("construction_assessment", {})
    if construction.get("substantive_mathematical_gap_found") is not False:
        errors.append("positive adjudication records a substantive mathematical gap")
    if construction.get("source_internal_entropy_lemmas_reformalized") is not False:
        errors.append("entropy-lemma formalization overclaim")

    state = record.get("state", {})
    expected_state = {
        "route_state": "submitted",
        "adjudication_operation_authorized": True,
        "adjudication_authority_source": "protected_streamlined_successor_contract",
        "adjudication_recorded_on_branch": True,
        "cert_output": None,
        "mathematical_target_proved": False,
        "may_issue_output": False,
        "may_promote_claim": False,
        "stronger_coloring_property_certified": False,
        "aggregate_adjudication": False,
        "aggregate_output": False,
    }
    if state != expected_state:
        errors.append("adjudication no-output/no-route-transition state drift")

    if record.get("review_gate", {}).get("recorded_review") is not None:
        errors.append("review gate prepopulated before fresh final-head review")

    limitations = record.get("preserved_limitations", {})
    for key in (
        "historical_records_rewritten",
        "stronger_coloring_property_source_authorized",
        "stronger_coloring_property_certified",
        "proof_body_compared_in_full",
        "source_internal_entropy_lemmas_reformalized",
        "other_result_families_modified",
        "aggregate_openai_ten_proofs_authority",
        "mathematical_proof_promotion_authorized",
        "cert_output_authorized",
        "route_transition_authorized",
    ):
        if limitations.get(key) is not False:
            errors.append(f"preserved limitation weakened: {key}")

    if not check_repository:
        return errors

    for rel, expected in OBJECTS.items():
        try:
            actual = repo_blob(rel)
        except subprocess.CalledProcessError:
            errors.append(f"missing protected object: {rel}")
            continue
        if actual != expected:
            errors.append(f"protected object drift: {rel}: {actual}")

    if commit_blob(OUTPUT_CERTIFICATE_COMMIT, "governance/certification_routes.json") != EXPECTED["historical_route_blob"]:
        errors.append("historical adjudication route-registry snapshot drift")

    live_blob = repo_blob("governance/certification_routes.json")
    if live_blob == EXPECTED["live_route_blob"]:
        pass
    elif live_blob == EXPECTED["a_registration_route_blob"]:
        successor_errors = sphere_registration.validation_errors(routes=load(ROUTES))
        if successor_errors:
            errors.append("exact A registration successor is invalid: " + "; ".join(successor_errors))
    else:
        errors.append("live J2 output route-registry blob drift")

    if not is_ancestor(EXPECTED["runtime_head"]):
        errors.append("fresh execution head is not an ancestor of current publication head")
    if not is_ancestor("ca66279862dcec276d2280749e6fae45f6e1e7a0"):
        errors.append("protected route-target successor merge is not an ancestor")
    for sha, label in (
        (OUTPUT_CONTRACT_MERGE, "protected J2 output-contract merge"),
        (OUTPUT_CERTIFICATE_COMMIT, "J2 certificate-content commit"),
        (OUTPUT_ROUTE_COMMIT, "J2 route-transition commit"),
    ):
        if not is_ancestor(sha):
            errors.append(f"{label} is not an ancestor")

    route = find_route(load(ROUTES), "MC-ROUTE-OTP-J2-TWO-DEGENERATE")
    if route is None:
        errors.append("live J2 route missing")
    else:
        if route.get("intake_status") != "qualified":
            errors.append("live J2 governed output successor is not qualified")
        if route.get("target_claim_ids") != TARGETS:
            errors.append("live J2 targets drifted")
        if route.get("cert_output") != OUTPUT_CERT:
            errors.append("live J2 Cert output identity drift")
        boundary = str(route.get("claim_boundary", "")).lower()
        if "qualified_source_faithful_targets_only" not in boundary:
            errors.append("live J2 restricted qualification disposition missing from boundary")
        if "stronger coloring-side" not in boundary:
            errors.append("live J2 stronger-coloring exclusion missing")

    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(
        "validated immutable narrow J2 source-faithful adjudication at submitted/no-output state and "
        "the governed restricted output successor plus exact separately governed A registration successor"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
