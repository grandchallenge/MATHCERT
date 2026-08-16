#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "governance/result_family_construction_evidence/OTP-J2-TWO-DEGENERATE.json"
SCHEMA = ROOT / "schemas/openai_ten_proofs_j2_source_faithful_evidence.schema.json"
ROUTES = ROOT / "governance/certification_routes.json"
SOURCE = ROOT / "evidence/openai_ten_proofs/two_degenerate_construction/source_authority.json"
RECON = ROOT / "evidence/openai_ten_proofs/two_degenerate_construction/reconstruction.json"
LEDGER = ROOT / "evidence/openai_ten_proofs/two_degenerate_construction/proof_dependency_ledger.json"
PROJECTION = ROOT / "evidence/openai_ten_proofs/two_degenerate_scope_repair/SourceFaithfulProjection.lean"

EXPECTED = {
    "route_blob": "bc4640661443f1b3de213aaa82a333a4fdb6849b",
    "scope_repair_blob": "5884bc57ba4e9c1d4576b96793f7e78009223b15",
    "source_blob": "221c46be31ef4b77cfc46780cfaa8e3a0440cf8c",
    "recon_blob": "3905455458f247b768353bc0b082ecbf7c8dd0ff",
    "ledger_blob": "0d81c00d9d190e92ed6f30de867e940bc03b2237",
    "projection_blob": "ac1ec20e95d6acbcd1c3a111afe28bca92a43377",
    "source_sha256": "ebc561ab5c53dbd240e17a8fdb6fffeb648591eca85dbfc7466f563638f8c566",
    "source_bytes": 2487031,
    "theorem_locus": "Chapter 10, Theorem 1.2, current official PDF P240-P241 / printed pp236-237",
    "construction_locus": "Chapter 10 sections 6-8 and proof of Theorem 1.2, current official PDF P248-P251 / printed pp244-248",
}
HISTORICAL_TARGETS = [
    "TwoDegenerateGraphs.twoDegenerateExtremalCounterexample",
    "TwoDegenerateGraphs.not_erdos_146",
]
EVIDENCE_SUBJECTS = [
    "TwoDegenerateGraphs.mathcert_sourceFaithfulTwoDegenerateExtremalCounterexample",
    "TwoDegenerateGraphs.mathcert_sourceFaithfulNotErdos146",
]


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def repo_blob(rel: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", f"HEAD:{rel}"],
        capture_output=True, text=True, check=True,
    )
    return proc.stdout.strip()


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


def route_targets(route: dict[str, Any]) -> list[str] | None:
    for key in ("target_claim_ids", "target_theorems", "target_ids", "lean_theorems", "targets"):
        value = route.get(key)
        if isinstance(value, list) and all(isinstance(x, str) for x in value):
            return value
    for value in route.values():
        if isinstance(value, dict):
            hit = route_targets(value)
            if hit is not None:
                return hit
    return None


def validation_errors(record: dict[str, Any] | None = None, routes: dict[str, Any] | None = None, check_files: bool = True) -> list[str]:
    errors: list[str] = []
    record = load(RECORD) if record is None else record
    routes = load(ROUTES) if routes is None else routes
    schema = load(SCHEMA)

    try:
        Draft202012Validator.check_schema(schema)
    except Exception as exc:
        errors.append(f"invalid J2 evidence schema: {exc}")
    else:
        for err in sorted(Draft202012Validator(schema).iter_errors(record), key=lambda e: list(e.path)):
            where = ".".join(str(x) for x in err.path) or "$"
            errors.append(f"schema violation at {where}: {err.message}")

    exact_top = {
        "record_type": "openai_ten_proofs_j2_source_faithful_construction_evidence",
        "evidence_id": "MC-OTP-J2-TWO-DEGENERATE-SOURCE-FAITHFUL-EVIDENCE-001",
        "operation_id": "OTP-J2-TWO-DEGENERATE-CERT-EVIDENCE-REFRESH-001",
        "candidate_id": "OPENAI-TEN-PROOFS-001",
        "result_family": "OTP-J2-TWO-DEGENERATE",
        "route_id": "MC-ROUTE-OTP-J2-TWO-DEGENERATE",
        "tracker_issue": "https://github.com/grandchallenge/MATHCERT/issues/122",
    }
    for key, value in exact_top.items():
        if record.get(key) != value:
            errors.append(f"{key} drift")

    if record.get("evidence_subjects") != EVIDENCE_SUBJECTS:
        errors.append("source-faithful evidence subject drift")
    if record.get("historical_registered_targets") != HISTORICAL_TARGETS:
        errors.append("historical registered target drift")

    authority = record.get("authority", {})
    if authority.get("protected_base") != "2106840fe2daf8b2492f52473465f531e7e2ef21":
        errors.append("protected base drift")
    if authority.get("path_a_authorization", {}).get("comment_id") != 5305021852:
        errors.append("Path A authorization substitution")
    if authority.get("scope_repair", {}).get("digest") != EXPECTED["scope_repair_blob"]:
        errors.append("scope repair authority drift")
    for field, expected in (
        ("route_registry", EXPECTED["route_blob"]),
        ("source_authority", EXPECTED["source_blob"]),
        ("reconstruction", EXPECTED["recon_blob"]),
        ("proof_dependency_ledger", EXPECTED["ledger_blob"]),
        ("source_faithful_projection", EXPECTED["projection_blob"]),
    ):
        if authority.get(field, {}).get("digest") != expected:
            errors.append(f"{field} identity drift")

    source = record.get("source_assessment", {})
    if source.get("current_official_source_sha256") != EXPECTED["source_sha256"] or source.get("current_official_source_bytes") != EXPECTED["source_bytes"]:
        errors.append("current official source identity drift")
    if source.get("theorem_locus") != EXPECTED["theorem_locus"]:
        errors.append("Theorem 1.2 source locus drift")
    if source.get("construction_locus") != EXPECTED["construction_locus"]:
        errors.append("Theorem 1.2 construction locus drift")
    if source.get("statement_concordance") != "clear_for_source_faithful_projection_only":
        errors.append("source-faithful statement-concordance boundary drift")
    if source.get("stronger_coloring_property_source_authorized") is not False:
        errors.append("stronger coloring property source-authorized")
    if source.get("whole_document_equivalence") != "not_established" or source.get("proof_body_compared_in_full") is not False:
        errors.append("source equivalence/proof-body overclaim")

    construction = record.get("construction_assessment", {})
    if construction.get("substantive_mathematical_gap_found") is not False:
        errors.append("clear candidate records a substantive mathematical gap")
    if construction.get("source_internal_entropy_lemmas_reformalized") is not False:
        errors.append("entropy lemma formalization overclaim")
    for key in ("fixed_graph_construction", "parameter_window_nonempty", "exponent_bridge", "extremal_interpretation"):
        if not isinstance(construction.get(key), str) or "independently_reconstructed" not in construction.get(key, ""):
            errors.append(f"construction evidence missing: {key}")

    state = record.get("required_state", {})
    expected_state = {
        "route_state": "submitted",
        "live_route_target_list_changed": False,
        "may_adjudicate": False,
        "adjudication": None,
        "cert_output": None,
        "mathematical_target_proved": False,
        "may_promote_claim": False,
        "aggregate_authority": False,
    }
    if state != expected_state:
        errors.append("required fail-closed state drift")

    limits = record.get("preserved_limitations", {})
    for key in ("stronger_coloring_property_certified", "historical_records_rewritten", "other_result_family_modified", "aggregate_openai_ten_proofs_authority"):
        if limits.get(key) is not False:
            errors.append(f"preserved limitation weakened: {key}")

    route = find_route(routes, "MC-ROUTE-OTP-J2-TWO-DEGENERATE")
    if route is None:
        errors.append("live J2 route missing")
    else:
        status = route.get("intake_status", route.get("route_state", route.get("status")))
        if status != "submitted":
            errors.append("live J2 route is not submitted")
        if route.get("cert_output") is not None:
            errors.append("live J2 route gained cert output")
        if route_targets(route) != HISTORICAL_TARGETS:
            errors.append("live J2 target list changed during evidence operation")

    runtime = record.get("fresh_runtime_replay", {})
    disposition = record.get("disposition", {})
    cstate = record.get("candidate_state")
    if cstate == "evidence_prepared_pending_fresh_runtime_replay":
        if runtime.get("status") != "pending":
            errors.append("pending candidate has non-pending runtime status")
        for key in ("workflow_run_id", "artifact_id", "artifact_sha256", "execution_head", "comparator", "lean_kernel", "nanoda", "source_faithful_projection", "dependency_separation", "theorem_axiom_report", "trust_scan"):
            if runtime.get(key) is not None:
                errors.append(f"pending candidate prepopulates runtime field: {key}")
        if disposition.get("evidence_disposition") != "PENDING_FRESH_EXACT_HEAD_RUNTIME_REPLAY" or disposition.get("ready_for_route_target_successor") is not False:
            errors.append("pending disposition drift")
    elif cstate == "evidence_complete_ready_for_route_target_successor":
        expected_runtime = {
            "status": "clear", "comparator": "pass_derivation_carrier_only", "lean_kernel": "accept",
            "nanoda": "accept", "source_faithful_projection": "accept", "dependency_separation": "accept",
            "theorem_axiom_report": "permitted_only", "trust_scan": "clear",
        }
        for key, expected in expected_runtime.items():
            if runtime.get(key) != expected:
                errors.append(f"final runtime field drift: {key}")
        if not isinstance(runtime.get("workflow_run_id"), int) or not isinstance(runtime.get("artifact_id"), int):
            errors.append("final runtime provenance incomplete")
        if not isinstance(runtime.get("artifact_sha256"), str) or len(runtime.get("artifact_sha256", "")) != 64:
            errors.append("final runtime artifact digest missing")
        if not isinstance(runtime.get("execution_head"), str) or len(runtime.get("execution_head", "")) != 40:
            errors.append("final execution head missing")
        if disposition.get("evidence_disposition") != "J2_SOURCE_FAITHFUL_EVIDENCE_COMPLETE_READY_FOR_ROUTE_TARGET_SUCCESSOR" or disposition.get("ready_for_route_target_successor") is not True:
            errors.append("final evidence disposition drift")
        if disposition.get("adjudication_authorized") is not False:
            errors.append("final evidence candidate improperly authorizes adjudication")
    else:
        errors.append("unknown candidate state")

    if check_files:
        for rel, expected in (
            ("governance/certification_routes.json", EXPECTED["route_blob"]),
            ("evidence/openai_ten_proofs/two_degenerate_construction/source_authority.json", EXPECTED["source_blob"]),
            ("evidence/openai_ten_proofs/two_degenerate_construction/reconstruction.json", EXPECTED["recon_blob"]),
            ("evidence/openai_ten_proofs/two_degenerate_construction/proof_dependency_ledger.json", EXPECTED["ledger_blob"]),
            ("evidence/openai_ten_proofs/two_degenerate_scope_repair/SourceFaithfulProjection.lean", EXPECTED["projection_blob"]),
        ):
            if repo_blob(rel) != expected:
                errors.append(f"repository object identity drift: {rel}")

    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("validated J2 source-faithful construction/evidence candidate with unchanged submitted route and no adjudication/output authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
