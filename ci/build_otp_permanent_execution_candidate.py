#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data, usedforsecurity=False).hexdigest()


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} OUTPUT_DIR", file=sys.stderr)
        return 64

    out = Path(sys.argv[1])
    required = [
        "axiom-check.json",
        "challenge-build.log",
        "comparator.log",
        "environment.txt",
        "evidence-summary.json",
        "nonvacuity-replay.log",
        "solution-build.log",
        "source-identities.txt",
        "theorem-axioms.log",
        "trust-boundary-scan.txt",
    ]
    files = []
    for name in required:
        path = out / name
        if not path.is_file():
            raise SystemExit(f"missing replay evidence file: {name}")
        if name != "nonvacuity-replay.log" and path.stat().st_size == 0:
            raise SystemExit(f"empty replay evidence file: {name}")
        files.append({
            "name": name,
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
            "git_blob_sha1": git_blob(path),
        })

    expected_targets = [
        "PermanentFormulaLowerBound.permanent_divisionFree_formula_logarithmic_lower_bound",
        "PermanentFormulaLowerBound.permanent_rational_formula_logarithmic_lower_bound",
    ]
    expected_witnesses = [
        "PermanentFormulaLowerBound.Nonvacuity.permanent_divisionFree_formula_nonvacuous",
        "PermanentFormulaLowerBound.Nonvacuity.permanent_rational_formula_nonvacuous",
    ]
    expected_projection = {
        "formula_target_count": 2,
        "circuit_target_count": 0,
        "coefficient_field": "complex",
        "dimension_threshold": 32,
        "log_base": 2,
        "division_free_variable_leaf_constant": 128,
        "rational_variable_leaf_constant": 192,
        "gate_bounds_in_replay": False,
        "total_leaves_vertices_in_replay": False,
        "historical_pdf_byte_equivalence": False,
    }
    expected_results = {
        "solution_build": "pass",
        "challenge_build": "pass",
        "comparator": "pass",
        "lean_kernel": "accept",
        "nanoda": "accept",
        "nonvacuity_replay": "pass",
        "theorem_axiom_report": "permitted_only",
        "trust_boundary_scan": "clear",
        "semantic_concordance": "protected_predecessor_reconfirmed",
    }

    summary = json.loads((out / "evidence-summary.json").read_text(encoding="utf-8"))
    if summary.get("record_type") != "openai_ten_proofs_permanent_cert_replay_execution_evidence":
        raise SystemExit("unexpected replay evidence record type")
    if summary.get("result_family") != "OTP-C-PERMANENT":
        raise SystemExit("result-family drift")
    if summary.get("targets", {}).get("theorem_names") != expected_targets:
        raise SystemExit("target drift")
    if summary.get("targets", {}).get("nonvacuity_witnesses") != expected_witnesses:
        raise SystemExit("nonvacuity witness drift")
    if summary.get("source_projection") != expected_projection:
        raise SystemExit("source projection drift")
    if summary.get("results") != expected_results:
        raise SystemExit("replay result drift")
    execution = summary.get("execution", {})
    if execution.get("clean_room_runner") is not True or execution.get("isolated_family_replay") is not True:
        raise SystemExit("replay is not clean-room isolated")
    if execution.get("aggregate_all_import_used") is not False:
        raise SystemExit("aggregate All import used")

    axiom_report = json.loads((out / "axiom-check.json").read_text(encoding="utf-8"))
    if axiom_report.get("permitted") != ["Classical.choice", "Quot.sound", "propext"]:
        raise SystemExit("permitted axiom set drift")
    reports = axiom_report.get("reports", [])
    if [item.get("theorem") for item in reports] != expected_targets:
        raise SystemExit("theorem axiom report target drift")
    if any(item.get("unexpected") for item in reports):
        raise SystemExit("unexpected theorem axiom detected")

    trust = (out / "trust-boundary-scan.txt").read_text(encoding="utf-8", errors="replace")
    for marker in [
        "solution/witness placeholder and unsafe/custom-axiom scan: clear",
        "aggregate All import scan: clear",
    ]:
        if marker not in trust:
            raise SystemExit(f"missing trust-boundary marker: {marker}")

    comparator = (out / "comparator.log").read_text(encoding="utf-8", errors="replace")
    if "Your solution is okay!" not in comparator:
        raise SystemExit("Comparator acceptance marker missing")

    candidate = {
        "schema_version": "1.0.0",
        "record_type": "openai_ten_proofs_permanent_execution_candidate",
        "candidate_id": "MC-OTP-C-PERMANENT-EXECUTION-CANDIDATE-001",
        "result_family": "OTP-C-PERMANENT",
        "route_id": "MC-ROUTE-OTP-C-PERMANENT-FORMULA",
        "contract_id": "MC-OTP-ADJUDICATION-CONTRACT-C-PERMANENT-FORMULA",
        "candidate_state": "evidence_prepared",
        "tracker_issue": "https://github.com/grandchallenge/MATHCERT/issues/105",
        "authority": {
            "design_reviewed_head": "00670367973730bc1136c650583dccab6cbfa9eb",
            "design_review_id": 4942843996,
            "design_merge_commit": "67d78a99942df2c864f51728d741118d64bba183",
            "contract_blob": "f9429395e7026f838ad6994b8f908a86506cfe06",
            "design_registry_blob": "2af852600796e35afe034bbaf9b9e13950055a29",
            "registered_route_registry_blob": "4b7f98414958999c8404e30a4a7c0a2a104578da",
            "forge_semantic_merge": "60f6e06c957139447bf5943eed731941b22ac608",
            "solve_handoff_merge": "90f8a8544e546a603b34c9b27b2d6a4a68e06de8",
            "cert_intake_merge": "59e678a5692c873cb7b12b8913231bf520571f51",
            "cert_work_package_merge": "4b5d9e81afea50b5b51b4e390065f52275c886cd",
            "cert_replay_evidence_merge": "7f42194bfcfb5b28f2bdb1f5b3203650a6b5ff15",
            "retained_evidence_manifest_blob": "cbc185bd0cd182fddd3127d8373ae7a74f6389dd",
            "retained_evidence_manifest_sha256": "351ab107342d2fe72220098ae6e5dc600653e9b181119c99805182270559f969",
            "mathcert_evidence_generation_head": execution.get("mathcert_head_sha", os.environ.get("MATHCERT_HEAD_SHA", "unknown")),
            "workflow_checkout_sha": execution.get("workflow_checkout_sha", os.environ.get("MATHCERT_WORKFLOW_SHA", os.environ.get("GITHUB_SHA", "unknown"))),
        },
        "encoded_targets": expected_targets,
        "source_projection": expected_projection,
        "replay": {
            "clean_room": True,
            "isolated_family_replay": True,
            "aggregate_all_import_used": False,
            "lean_version": "4.32.0",
            "solution_build": "pass",
            "challenge_build": "pass",
            "comparator": "pass",
            "lean_kernel": "accept",
            "nanoda": "accept",
            "nonvacuity_replay": "pass",
            "theorem_axiom_report": "permitted_only",
            "trust_boundary_scan": "clear",
            "files": files,
        },
        "statement_concordance": {
            "state": "candidate_clear_pending_non_author_specialist_review",
            "scope": "two_encoded_variable_leaf_formula_targets_only",
            "coefficient_field": "complex",
            "dimension_threshold": 32,
            "log_base": 2,
            "division_free_variable_leaf_constant": 128,
            "rational_variable_leaf_constant": 192,
            "circuit_gate_total_size_inference": False,
        },
        "nonvacuity": {
            "state": "candidate_clear_pending_non_author_specialist_review",
            "witnesses": expected_witnesses,
            "replay": "pass",
        },
        "retained_evidence_integrity": {
            "manifest_blob": "cbc185bd0cd182fddd3127d8373ae7a74f6389dd",
            "manifest_sha256": "351ab107342d2fe72220098ae6e5dc600653e9b181119c99805182270559f969",
            "state": "reconfirmed",
        },
        "review_state": {
            "fresh_non_author_specialist_review_required": True,
            "specialist_review": None,
            "status": "pending_exact_head_non_author_specialist_review",
        },
        "control_plan": {
            "routine_stage_progression_without_human_steward_intervention": True,
            "human_steward_intervention_required_only_for_control_plan_change": True,
            "control_plan_change_requested": False,
            "conformance": "within_admitted_contract",
        },
        "state": {
            "route_state": "submitted",
            "may_adjudicate": False,
            "adjudication": None,
            "cert_output": None,
            "mathematical_target_proved": False,
            "may_issue_output": False,
            "may_promote_claim": False,
            "aggregate_adjudication": False,
        },
        "preserved_limitations": {
            "circuit_targets_in_scope": False,
            "gate_bounds_in_scope": False,
            "total_size_consequences_in_scope": False,
            "historical_pdf_byte_equivalence": "not_established",
            "aggregate_openai_ten_proofs_authority": False,
        },
        "claim_boundary": "This evidence-prepared Permanent execution candidate does not adjudicate or prove either theorem, issue a Cert output, alter the submitted route, certify circuit complexity, certify 256/384 gate bounds or total-size consequences, establish historical admitted-PDF byte equivalence, create aggregate authority, or authorize mathematical truth, novelty, priority, publication, patentability, product, or commercial claims. Routine progression may continue under the admitted control plan; Human Steward intervention is required only if that control plan changes.",
    }
    (out / "execution-candidate.json").write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    manifest_files = []
    for path in sorted(p for p in out.iterdir() if p.is_file() and p.name not in {"SHA256SUMS", "bundle-manifest.json"}):
        manifest_files.append({
            "name": path.name,
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
            "git_blob_sha1": git_blob(path),
        })
    manifest = {
        "schema_version": "1.0.0",
        "record_type": "openai_ten_proofs_permanent_execution_candidate_manifest",
        "candidate_id": candidate["candidate_id"],
        "candidate_state": candidate["candidate_state"],
        "files": manifest_files,
    }
    (out / "bundle-manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = []
    for path in sorted(p for p in out.iterdir() if p.is_file() and p.name != "SHA256SUMS"):
        lines.append(f"{sha256(path)}  {path.name}")
    (out / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("built non-adjudicated OTP-C-PERMANENT execution candidate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
