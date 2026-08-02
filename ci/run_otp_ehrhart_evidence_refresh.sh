#!/usr/bin/env bash
set -euo pipefail

if (($# != 1)); then
  echo "usage: $0 OUTPUT_DIR" >&2
  exit 64
fi

root="$(cd "$(dirname "$0")/.." && pwd)"
output_dir="$1"
mkdir -p "$output_dir"
output_dir="$(cd "$output_dir" && pwd)"

expected_design_merge="9f5ec626306092a352aa5ba8d9920b6ddb11b8bb"
expected_contract_blob="6e1c210d82440210da71fd661daffe986df81f03"
expected_design_registry_blob="7a4aa7ca4f016020fccd0b9d4e73e1c5af12d03f"
expected_route_registry_blob="b5541045591f8589130b1577c50d51d70c3b4337"
expected_source_audit_commit="a498ef40b7652b55bf121b5682604e259b8d3073"
expected_source_audit_blob="80d473b1b545fd9ca05fc5200bcf70ff5f9fcb05"
expected_semantic_blob="a3dc4de4c38a80b7aec1fae6506b08e14d2e58bb"
authorization_comment_id="5156109106"
admitted_manuscript_sha="f318c6508c9d49ef876a5a26cd73928705f96c07bb43e92a0cb35bd3f666ea53"
observed_manuscript_sha="64b900d5fae6fe22f2ae1b8e3b712d20055194a6c81cf343a2455e5898ac7dd6"

assert_eq() {
  if [[ "$1" != "$2" ]]; then
    echo "$3 mismatch: expected $2, found $1" >&2
    exit 1
  fi
}

assert_eq "$(git -C "$root" rev-parse "$expected_design_merge:governance/result_family_adjudication_contracts/OTP-F-EHRHART.json")" "$expected_contract_blob" "Ehrhart contract blob"
assert_eq "$(git -C "$root" rev-parse "$expected_design_merge:governance/adjudication_design/OPENAI_TEN_PROOFS_WP07_ADJUDICATION_CONTRACTS.json")" "$expected_design_registry_blob" "design registry blob"
assert_eq "$(git -C "$root" rev-parse "$expected_design_merge:governance/certification_routes.json")" "$expected_route_registry_blob" "registered route registry blob"
assert_eq "$(git -C "$root/forge-audit" rev-parse HEAD)" "$expected_source_audit_commit" "Forge source-audit commit"
assert_eq "$(git -C "$root/forge-audit" rev-parse 'HEAD:sources/OPENAI-TEN-PROOFS-001/source_revision_audits/OTP-TRANCHE-001.json')" "$expected_source_audit_blob" "Forge source-audit blob"
assert_eq "$(git -C "$root/forge" rev-parse 'HEAD:sources/OPENAI-TEN-PROOFS-001/semantic_audits/OTP-F-EHRHART.json')" "$expected_semantic_blob" "Forge Ehrhart semantic blob"

chmod +x "$root/ci/run_openai_ten_proofs_family_replay.sh"
"$root/ci/run_openai_ten_proofs_family_replay.sh" \
  OTP-F-EHRHART \
  ComparatorChallenges/F_EhrhartVolumeInequality.json \
  EhrhartVolumeInequality \
  ComparatorChallenges.F_EhrhartVolumeInequality \
  "$output_dir"

current_sha="$(sha256sum "$output_dir/manuscript.pdf" | cut -d' ' -f1)"
current_bytes="$(stat -c '%s' "$output_dir/manuscript.pdf")"
if [[ "$current_sha" == "$observed_manuscript_sha" ]]; then
  source_relation="byte_identical_to_forge_source_revision_audit_subject"
  source_authority="MF-OTP-SOURCE-REVISION-AUDIT-001"
elif [[ "$current_sha" == "$admitted_manuscript_sha" ]]; then
  source_relation="byte_identical_to_admitted_semantic_audit_subject"
  source_authority="MF-OTP-SEMANTIC-WP01-EHRHART"
else
  echo "source revision is not covered by the admitted semantic or source-revision authorities" >&2
  exit 1
fi

pdftotext -f 218 -l 221 -layout "$output_dir/manuscript.pdf" "$output_dir/source-locus-pages-218-221.txt"
[[ -s "$output_dir/source-locus-pages-218-221.txt" ]] || { echo "source-locus extraction is empty" >&2; exit 1; }

export OTP_REFRESH_CURRENT_SHA="$current_sha"
export OTP_REFRESH_CURRENT_BYTES="$current_bytes"
export OTP_REFRESH_SOURCE_RELATION="$source_relation"
export OTP_REFRESH_SOURCE_AUTHORITY="$source_authority"
export OTP_REFRESH_AUTH_COMMENT_ID="$authorization_comment_id"
export OTP_REFRESH_DESIGN_MERGE="$expected_design_merge"
export OTP_REFRESH_CONTRACT_BLOB="$expected_contract_blob"
export OTP_REFRESH_DESIGN_REGISTRY_BLOB="$expected_design_registry_blob"
export OTP_REFRESH_ROUTE_REGISTRY_BLOB="$expected_route_registry_blob"
export OTP_REFRESH_SOURCE_AUDIT_COMMIT="$expected_source_audit_commit"
export OTP_REFRESH_SOURCE_AUDIT_BLOB="$expected_source_audit_blob"
export OTP_REFRESH_SEMANTIC_BLOB="$expected_semantic_blob"

python3 - "$output_dir" <<'PY'
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

out = Path(sys.argv[1])

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def git_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data, usedforsecurity=False).hexdigest()

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
    files.append({
        "name": name,
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "git_blob_sha1": git_blob(path),
    })

trust = (out / "trust-boundary-scan.txt").read_text(encoding="utf-8", errors="replace").lower()
for forbidden in ("sorry", "unsafe declaration", "custom axiom"):
    if forbidden in trust and "no " + forbidden not in trust:
        raise SystemExit(f"trust-boundary scan is not clear: {forbidden}")

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
        "mathcert_candidate_head": os.environ.get("MATHCERT_HEAD_SHA", "unknown"),
        "workflow_checkout_sha": os.environ.get("MATHCERT_WORKFLOW_SHA", os.environ.get("GITHUB_SHA", "unknown")),
    },
    "encoded_targets": [
        "Ehrhart.Volume.ehrhart_volume_inequality_for_sets",
        "Ehrhart.SimplexVolume.exists_centeredBody_sharp",
        "Ehrhart.SimplexVolume.barycenter_centeredSimplex",
        "Ehrhart.SimplexVolume.normalizedVolume_centeredSimplex",
    ],
    "replay": {
        "clean_room": True,
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
        "locus": {
            "chapter": 8,
            "theorem": "Theorem 1.1",
            "pdf_page_index": 219,
            "printed_page": 218,
            "extracted_context": "source-locus-pages-218-221.txt",
        },
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
        "witnesses": [
            "Ehrhart.SimplexVolume.exists_centeredBody_sharp",
            "Ehrhart.SimplexVolume.normalizedVolume_centeredSimplex",
        ],
        "checked_obligations": [
            "positive_dimension",
            "full_dimensional_compact_convex_body",
            "centered_body_witness",
            "normalized_volume_sharpness_witness",
        ],
    },
    "construction_interpretation": {
        "state": "candidate_clear_pending_non_author_specialist_review",
        "admitted_witness": "(n+1)Delta_n-(1,...,1)",
        "effect": "sharpness_witness_only",
        "classification_or_uniqueness_inference": False,
    },
    "review_state": {
        "fresh_non_author_specialist_review_required": True,
        "specialist_review": None,
        "status": "pending_exact_head_non_author_specialist_review",
    },
    "execution_authorization": {
        "separate_human_steward_authorization_required": True,
        "must_name_contract_and_exact_candidate_head": True,
        "authorization": None,
    },
    "state": {
        "route_state": "submitted",
        "may_adjudicate": False,
        "adjudication": None,
        "cert_output": None,
        "mathematical_target_proved": False,
        "may_promote_claim": False,
        "aggregate_adjudication": False,
    },
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

candidate_path = out / "execution-candidate.json"
candidate_path.write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n", encoding="utf-8")

manifest_files = []
for path in sorted(p for p in out.iterdir() if p.is_file() and p.name not in {"manuscript.pdf", "reasoning-walkthroughs.pdf", "SHA256SUMS"}):
    manifest_files.append({
        "name": path.name,
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "git_blob_sha1": git_blob(path),
    })
manifest = {
    "schema_version": "1.0.0",
    "record_type": "openai_ten_proofs_ehrhart_evidence_bundle_manifest",
    "candidate_id": candidate["candidate_id"],
    "candidate_state": candidate["candidate_state"],
    "files": manifest_files,
}
(out / "bundle-manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

lines = []
for path in sorted(p for p in out.iterdir() if p.is_file() and p.name not in {"manuscript.pdf", "reasoning-walkthroughs.pdf", "SHA256SUMS"}):
    lines.append(f"{sha256(path)}  {path.name}")
(out / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")
PY

rm -f "$output_dir/manuscript.pdf" "$output_dir/reasoning-walkthroughs.pdf"

echo "prepared non-adjudicated OTP-F-EHRHART execution-candidate evidence at $output_dir"
