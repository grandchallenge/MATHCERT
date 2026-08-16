#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
out="${1:-$root/evidence/j2-adjudication-runtime}"
mkdir -p "$out"
out="$(cd "$out" && pwd)"

python3 "$root/ci/validate_otp_j2_adjudication_input.py" > "$out/input-validation.txt"
python3 "$root/ci/test_otp_j2_adjudication_input.py" > "$out/input-mutations.txt"
python3 "$root/ci/validate_otp_j2_route_target_successor.py" > "$out/route-successor-validation.txt"
python3 "$root/ci/validate_otp_j2_scope_repair_with_successor.py" > "$out/scope-repair-compatibility.txt"
python3 "$root/ci/validate_otp_j2_source_faithful_evidence_with_successor.py" > "$out/evidence-compatibility.txt"

"$root/ci/run_otp_j2_evidence_refresh_replay.sh" "$out/fresh-evidence"

python3 - "$root" "$out" <<'PY'
import json
import os
import subprocess
import sys
from pathlib import Path

root = Path(sys.argv[1])
out = Path(sys.argv[2])
formal = json.loads((out / "fresh-evidence/formal-replay/replay-summary.json").read_text(encoding="utf-8"))
evidence = json.loads((out / "fresh-evidence/evidence-summary.json").read_text(encoding="utf-8"))
input_record = json.loads((root / "governance/result_family_adjudication_execution_inputs/OTP-J2-TWO-DEGENERATE.json").read_text(encoding="utf-8"))

def repo_blob(rel: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), "rev-parse", f"HEAD:{rel}"], text=True).strip()

head = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
expected_head = os.environ.get("MATHCERT_HEAD_SHA")
if expected_head and head != expected_head:
    raise SystemExit(f"literal-head mismatch: {head} != {expected_head}")

assert formal["current_manuscript_sha256"] == "ebc561ab5c53dbd240e17a8fdb6fffeb648591eca85dbfc7466f563638f8c566"
assert formal["upstream_commit"] == "94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6"
assert formal["upstream_tree"] == "174289e4d4958cb0509874e6e53400e098213de7"
assert formal["lean_kernel"] == "accept"
assert formal["nanoda_registered_targets"] == "accept"
assert formal["source_faithful_projection"] == "accept"
assert formal["dependency_separation"] == "accept"
assert formal["source_attribution_of_coloring_conjunct"] is False
assert evidence["substantive_mathematical_gap_found"] is False
assert evidence["stronger_coloring_property_source_attributed"] is False
assert evidence["stronger_coloring_property_certified"] is False

summary = {
    "schema_version": "1.0.0",
    "operation_id": "OTP-J2-TWO-DEGENERATE-ADJUDICATION-EXECUTION-001",
    "result_family": "OTP-J2-TWO-DEGENERATE",
    "execution_head": head,
    "execution_input_git_blob_sha1": repo_blob("governance/result_family_adjudication_execution_inputs/OTP-J2-TWO-DEGENERATE.json"),
    "contract_git_blob_sha1": repo_blob("governance/result_family_adjudication_contract_successors/OTP-J2-TWO-DEGENERATE.json"),
    "route_successor_git_blob_sha1": repo_blob("governance/result_family_route_target_successors/OTP-J2-TWO-DEGENERATE.json"),
    "route_registry_git_blob_sha1": repo_blob("governance/certification_routes.json"),
    "current_source_sha256": formal["current_manuscript_sha256"],
    "formal_subject_commit": formal["upstream_commit"],
    "formal_subject_tree": formal["upstream_tree"],
    "targets": input_record["encoded_targets"],
    "authority_integrity": "clear",
    "source_statement_concordance": "clear_for_exact_source_faithful_theorem_1_2_core",
    "construction_and_extremal_interpretation": "clear_under_protected_independent_reconstruction_and_fresh_machine_reverification",
    "nonvacuity": "clear_both_source_faithful_declarations_accept_and_refutation_uses_source_core_only",
    "comparator": "pass_derivation_carrier_only",
    "lean_kernel": "accept",
    "nanoda": "accept",
    "source_faithful_projection": "accept",
    "dependency_separation": "accept",
    "theorem_axioms": "permitted_only",
    "trust_boundary": "clear",
    "stronger_coloring_property_source_authorized": False,
    "stronger_coloring_property_certified": False,
    "route_state": "submitted",
    "cert_output": None,
    "mathematical_target_proved": False,
    "aggregate_authority": False,
    "adjudication_readiness": "clear_for_adjudication_clear_source_faithful_targets_only",
    "adjudication_record_written_by_replay": False,
    "claim_boundary": "Fresh execution evidence only; publication of an adjudication still requires a content-addressed adjudication record, exact-head machine gates, fresh non-author APPROVED review, protected merge, and protected-main readback."
}
(out / "adjudication-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY

find "$out" -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > "$out/SHA256SUMS"
echo "J2 source-faithful adjudication replay complete; evidence supports adjudication readiness only; no output or route transition created"
