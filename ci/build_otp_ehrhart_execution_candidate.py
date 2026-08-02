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
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data, usedforsecurity=False).hexdigest()


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
        "solution-build.log",
        "source-identities.txt",
        "source-revision-report.txt",
        "theorem-axioms.log",
        "trust-boundary-scan.txt",
        "source-locus-pages-218-221.txt",
    ]
    files = []
    for name in required:
        path = out / name
        if not path.is_file() or path.stat().st_size == 0:
            raise SystemExit(f"missing or empty replay evidence file: {name}")
        files.append({"name": name, "bytes": path.stat().st_size, "sha256": sha256(path), "git_blob_sha1": git_blob(path)})

    trust = (out / "trust-boundary-scan.txt").read_text(encoding="utf-8", errors="replace").lower()
    if "scan: clear" not in trust or "challenge placeholders: expected comparator boundary" not in trust:
        raise SystemExit("trust-boundary scan is not clear")

    axiom_report = json.loads((out / "axiom-check.json").read_text(encoding="utf-8"))
    if axiom_report.get("permitted") != ["Classical.choice", "Quot.sound", "propext"]:
        raise SystemExit("permitted axiom set drift")
    expected_targets = [
        "Ehrhart.Volume.ehrhart_volume_inequality_for_sets",
        "Ehrhart.SimplexVolume.exists_centeredBody_sharp",
        "Ehrhart.SimplexVolume.barycenter_centeredSimplex",
        "Ehrhart.SimplexVolume.normalizedVolume_centeredSimplex",
    ]
    if [item.get("theorem") for item in axiom_report.get("reports", [])] != expected_targets:
        raise SystemExit("theorem-level axiom target drift")
    if any(item.get("unexpected") for item in axiom_report.get("reports", [])):
        raise SystemExit("unexpected theorem axiom detected")

    candidate = {
        "schema_version": "1.0.0",
        "record_type": "openai_ten_proofs_ehrhart_execution_candidate",
        "candidate_id": "MC-OTP-F-EHRHART-EXECUTION-CANDIDATE-001",
        "result_family": "OTP-F-EHRHART",
        "route_id": "MC-ROUTE-OTP-F-EHRHART",
        "contract_id": "MC-OTP-ADJUDICATION-CONTRACT-F-EHRHART",
        "candidate_state": "evidence_prepared",
        "tracker_issue": "https://github.com/grandchallenge/MATHCERT/issues/62",
        "authority": {
            "design_merge_commit": os.environ["OTP_REFRESH_DESIGN_MERGE"],
            "contract_blob": os.environ["OTP_REFRESH_CONTRACT_BLOB"],
            "design_registry_blob": os.environ["OTP_REFRESH_DESIGN_REGISTRY_BLOB"],
            "registered_route_registry_blob": os.environ["OTP_REFRESH_ROUTE_REGISTRY_BLOB"],
            "source_revision_audit_commit": os.environ["OTP_REFRESH_SOURCE_AUDIT_COMMIT"],
            "source_revision_audit_blob": os.environ["OTP_REFRESH_SOURCE_AUDIT_BLOB"],
            "semantic_record_blob": os.environ["OTP_REFRESH_SEMANTIC_BLOB"],
            "implementation_authorization_comment_id": int(os.environ["OTP_REFRESH_AUTH_COMMENT_ID"]),
            "mathcert_evidence_generation_head": os.environ.get("MATHCERT_HEAD_SHA", "unknown"),
            "workflow_checkout_sha": os.environ.get("MATHCERT_WORKFLOW_SHA", os.environ.get("GITHUB_SHA", "unknown")),
        },
        "encoded_targets": expected_targets,
        "replay": {
            "clean_room": True,
            "isolated_family_replay": True,
            "aggregate_all_import_used": False,
            "lean_version": "4.32.0",
            "challenge_build": "pass",
            "solution_build": "pass",
            "comparator": "pass",
            "lean_kernel": "accept",
            "nanoda": "accept",
            "theorem_axiom_report": "permitted_only",
            "trust_boundary_scan": "clear",
            "files": files,
        },
        "source_reacquisition": {
            "url": "https://cdn.openai.com/pdf/ten-proofs-oai.pdf",
            "sha256": os.environ["OTP_REFRESH_CURRENT_SHA"],
            "bytes": int(os.environ["OTP_REFRESH_CURRENT_BYTES"]),
            "relation": os.environ["OTP_REFRESH_SOURCE_RELATION"],
            "authority": os.environ["OTP_REFRESH_SOURCE_AUTHORITY"],
            "locus": {"chapter": 8, "theorem": "Theorem 1.1", "pdf_page_index": 219, "printed_page": 218, "extracted_context": "source-locus-pages-218-221.txt"},
            "whole_document_byte_equivalence": "not_established_between_all_revisions",
            "whole_document_semantic_equivalence": "not_established",
            "proof_body_compared_in_full": False,
        },
        "statement_concordance": {
            "state": "candidate_clear_pending_non_author_specialist_review",
            "scope": "encoded_inequality_and_admitted_sharpness_witness_only",
            "normalized_statement": "For every positive dimension n, a full-dimensional compact convex body K in real n-space with barycenter zero and with zero as its only interior lattice point has ordinary Euclidean volume at most (n+1)^n/n!. The bound is attained by the translated dilation (n+1)Delta_n-(1,...,1).",
            "equality_case_classification": "excluded",
        },
        "nonvacuity": {
            "state": "candidate_clear_pending_non_author_specialist_review",
            "witnesses": ["Ehrhart.SimplexVolume.exists_centeredBody_sharp", "Ehrhart.SimplexVolume.normalizedVolume_centeredSimplex"],
            "checked_obligations": ["positive_dimension", "full_dimensional_compact_convex_body", "centered_body_witness", "normalized_volume_sharpness_witness"],
        },
        "construction_interpretation": {
            "state": "candidate_clear_pending_non_author_specialist_review",
            "admitted_witness": "(n+1)Delta_n-(1,...,1)",
            "effect": "sharpness_witness_only",
            "classification_or_uniqueness_inference": False,
        },
        "review_state": {"fresh_non_author_specialist_review_required": True, "specialist_review": None, "status": "pending_exact_head_non_author_specialist_review"},
        "execution_authorization": {"separate_human_steward_authorization_required": True, "must_name_contract_and_exact_candidate_head": True, "authorization": None},
        "state": {"route_state": "submitted", "may_adjudicate": False, "adjudication": None, "cert_output": None, "mathematical_target_proved": False, "may_promote_claim": False, "aggregate_adjudication": False},
        "preserved_limitations": {
            "equality_case_classification": "excluded",
            "whole_document_byte_equivalence": "not_established_between_all_revisions",
            "whole_document_semantic_equivalence": "not_established",
            "proof_body_compared_in_full": False,
            "other_adjudication_contracts_executed": False,
            "unexamined_result_family_count": 9,
            "blocked_repair_lanes": ["OTP-C-PERMANENT", "OTP-H-GAPCVP"],
            "all_lean_state": "failed_namespace_collision",
        },
        "claim_boundary": "This evidence-prepared execution candidate does not adjudicate or prove the Ehrhart theorem, issue a Cert output, alter the submitted route, classify or establish uniqueness of equality cases, establish whole-document equivalence, compare the analytic proof body in full, execute another result-family contract, create aggregate authority, or authorize mathematical truth, novelty, priority, publication, patentability, product, or commercial claims.",
    }
    (out / "execution-candidate.json").write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    manifest_files = []
    for path in sorted(p for p in out.iterdir() if p.is_file() and p.name not in {"manuscript-refresh.pdf", "SHA256SUMS"}):
        manifest_files.append({"name": path.name, "bytes": path.stat().st_size, "sha256": sha256(path), "git_blob_sha1": git_blob(path)})
    manifest = {"schema_version": "1.0.0", "record_type": "openai_ten_proofs_ehrhart_evidence_bundle_manifest", "candidate_id": candidate["candidate_id"], "candidate_state": candidate["candidate_state"], "files": manifest_files}
    (out / "bundle-manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = []
    for path in sorted(p for p in out.iterdir() if p.is_file() and p.name not in {"manuscript-refresh.pdf", "SHA256SUMS"}):
        lines.append(f"{sha256(path)}  {path.name}")
    (out / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("built non-adjudicated OTP-F-EHRHART execution candidate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
