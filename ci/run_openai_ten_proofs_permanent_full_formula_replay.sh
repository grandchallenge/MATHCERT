#!/usr/bin/env bash
set -euo pipefail

if (($# != 1)); then
  echo "usage: $0 OUTPUT_DIR" >&2
  exit 64
fi

output_dir="$1"
root="$(cd "$(dirname "$0")/.." && pwd)"
upstream="$root/upstream"
forge="$root/forge"
solve="$root/solve"
mkdir -p "$output_dir"
output_dir="$(cd "$output_dir" && pwd)"

work_package_path="governance/result_family_work_package_successors/OTP-C-PERMANENT-FULL-FORMULA-CERT-WP01.json"
expected_work_package_blob="770dd679bbf08d77fa790fac6befef73080982ce"
expected_forge_commit="26309b3aa1ce21e8d74683235de76b491f62f17c"
semantic_path="sources/OPENAI-TEN-PROOFS-001/semantic/OTP-C-PERMANENT-FULL-FORMULA-CONSEQUENCES/audit_record.json"
expected_semantic_blob="520bdaa3bba075e411f7a0a2b8422e9c9d42c818"
witness_path="sources/OPENAI-TEN-PROOFS-001/semantic/OTP-C-PERMANENT/PermanentFormulaNonvacuity.lean"
expected_witness_blob="e756c8476bac1795f3fb8ca0b7235d3a4a5c59ea"
overlay_json_path="sources/OPENAI-TEN-PROOFS-001/target_overlays/OTP-C-PERMANENT-FULL-FORMULA-CONSEQUENCES/GCL_C_PermanentFormulaFullConsequences.json"
overlay_lean_path="sources/OPENAI-TEN-PROOFS-001/target_overlays/OTP-C-PERMANENT-FULL-FORMULA-CONSEQUENCES/GCL_C_PermanentFormulaFullConsequences.lean"
expected_overlay_json_blob="ad102cacd81736f154437826ddefff1cef648f13"
expected_overlay_lean_blob="8846ebdbae05e31d7d69f0e751a677e927023e48"
expected_solve_commit="bebc35818c6d3b79ddc7e348c9bffd328279cd24"
packet_path="work_packages/OPENAI_TEN_PROOFS_WP00/result_family_handoffs/OTP-C-PERMANENT-FULL-FORMULA.json"
expected_packet_blob="8755a1067963e5b46555872cb46025fff2625295"

expected_historical_commit="e62211d28e3a9131950c89caa6542cfe5eff3bca"
expected_historical_tree="2f8e7ac5ae7f157b6b1de636c2c343b1c7a7e365"
expected_archive_sha256="3022e62ffbed8f5f74d232034a703dc645e6b301879dff1e87df72979914294f"
expected_archive_bytes="21022720"
expected_lean_version="4.32.0"
expected_mathlib_commit="81a5d257c8e410db227a6665ed08f64fea08e997"
expected_comparator_commit="07bc4ea40f2266dcb861820a2ec1fa3244ed307f"
expected_lean4checker_commit="b7398199245524275543dec6113229c9bb4902e5"
expected_lean4export_commit="4e7915201d3f9f04470d9eae002fa695f7cdc589"
expected_landrun_commit="811cfff51ceaf3d9843708aa6d22e9b84ccac8b4"
expected_nanoda_commit="ddfac2bf5a7b56cb46e141494427ff3dd55963c7"

config="ComparatorChallenges/C_PermanentFormulaLowerBound.json"
challenge_file="$upstream/ComparatorChallenges/C_PermanentFormulaLowerBound.lean"
solution_file="$upstream/Permanent.lean"
solution_module="Permanent"
challenge_module="ComparatorChallenges.C_PermanentFormulaLowerBound"

theorem_names=(
  PermanentFormulaLowerBound.permanent_divisionFree_formula_lower_bound
  PermanentFormulaLowerBound.permanent_rational_formula_lower_bound
)
witness_names=(
  PermanentFormulaLowerBound.Nonvacuity.permanent_divisionFree_formula_nonvacuous
  PermanentFormulaLowerBound.Nonvacuity.permanent_rational_formula_nonvacuous
)

assert_eq() {
  if [[ "$1" != "$2" ]]; then
    echo "$3 mismatch: expected $2, found $1" >&2
    exit 1
  fi
}
git_blob() { git -C "$1" rev-parse "HEAD:$2"; }
sha_file() { sha256sum "$1" | cut -d' ' -f1; }

lean_version_line="$(lean --version | head -n1)"
[[ "$lean_version_line" == *"version $expected_lean_version"* ]] || {
  echo "Lean toolchain mismatch: expected $expected_lean_version, found $lean_version_line" >&2
  exit 1
}

assert_eq "$(git -C "$root" rev-parse "HEAD:$work_package_path")" "$expected_work_package_blob" "Cert work-package blob"
assert_eq "$(git -C "$forge" rev-parse HEAD)" "$expected_forge_commit" "Forge commit"
assert_eq "$(git_blob "$forge" "$semantic_path")" "$expected_semantic_blob" "Forge semantic record blob"
assert_eq "$(git_blob "$forge" "$witness_path")" "$expected_witness_blob" "Forge nonvacuity witness blob"
assert_eq "$(git_blob "$forge" "$overlay_json_path")" "$expected_overlay_json_blob" "Forge overlay JSON blob"
assert_eq "$(git_blob "$forge" "$overlay_lean_path")" "$expected_overlay_lean_blob" "Forge overlay Lean blob"
assert_eq "$(git -C "$solve" rev-parse HEAD)" "$expected_solve_commit" "Solve commit"
assert_eq "$(git_blob "$solve" "$packet_path")" "$expected_packet_blob" "Solve packet blob"

for required in "$upstream/lean-toolchain" "$upstream/lake-manifest.json" "$upstream/$config" "$challenge_file" "$solution_file"; do
  [[ -f "$required" ]] || { echo "missing replay input: $required" >&2; exit 1; }
done

# Verify immutable source bytes before the protected overlay is copied into the
# disposable clean-room working tree.
assert_eq "$(sha_file "$solution_file")" "3bd469c20bc2277a13be3f9353ce47ad0c2070a330355daa78a9e59f1ca1d3c6" "Permanent.lean SHA-256"
assert_eq "$(sha_file "$challenge_file")" "fc97578bcbb072ff82383e4c903107130ba3dd1a2209235ab32270c7df37f83d" "pre-overlay challenge SHA-256"
assert_eq "$(sha_file "$upstream/$config")" "f80482f4a163041e036e26bb687690559cc36504e347b0ea3df0d626cfb965bb" "pre-overlay Comparator config SHA-256"
assert_eq "$(sha_file "$upstream/lean-toolchain")" "2773c517aa90b66ea8a2c52bddddf84393157797f8341be0df45294fff7fd32e" "lean-toolchain SHA-256"
assert_eq "$(sha_file "$upstream/lake-manifest.json")" "a6faf8302fe77f77f499446c27b8829b1af8dbc7847298b682556baa2a0b135e" "lake-manifest SHA-256"

assert_eq "$(git -C "$upstream/.lake/packages/mathlib" rev-parse HEAD)" "$expected_mathlib_commit" "mathlib commit"
assert_eq "$(git -C "$upstream/.lake/packages/Comparator" rev-parse HEAD)" "$expected_comparator_commit" "Comparator commit"
assert_eq "$(git -C "$upstream/.lake/packages/Lean4Checker" rev-parse HEAD)" "$expected_lean4checker_commit" "Lean4Checker commit"
assert_eq "$(git -C "$root/tools/lean4export" rev-parse HEAD)" "$expected_lean4export_commit" "lean4export commit"
assert_eq "$(git -C "$root/tools/landrun" rev-parse HEAD)" "$expected_landrun_commit" "Landrun commit"
assert_eq "$(git -C "$root/tools/nanoda" rev-parse HEAD)" "$expected_nanoda_commit" "Nanoda commit"

# Content-addressed Forge overlay: overwrite only the disposable challenge slot.
cp "$forge/$overlay_lean_path" "$challenge_file"
cp "$forge/$overlay_json_path" "$upstream/$config"
assert_eq "$(sha_file "$challenge_file")" "$(sha_file "$forge/$overlay_lean_path")" "overlay Lean copy"
assert_eq "$(sha_file "$upstream/$config")" "$(sha_file "$forge/$overlay_json_path")" "overlay JSON copy"

WORK_PACKAGE="$root/$work_package_path" OVERLAY_CONFIG="$upstream/$config" python3 - <<'PY'
import json, os
from pathlib import Path
wp = json.loads(Path(os.environ["WORK_PACKAGE"]).read_text())
assert wp["surface_id"] == "OTP-C-PERMANENT-FULL-FORMULA"
assert wp["route_state"]["route_registered"] is False
assert wp["route_state"]["adjudication"] is None
assert wp["route_state"]["cert_output"] is None
assert wp["route_state"]["mathematical_target_proved"] is False
assert wp["execution"]["aggregate_import_required"] is False
sp = wp["target_scope"]["source_projection"]
assert sp == {
  "coefficient_field": "complex", "dimension_threshold": 32, "log_base": 2,
  "division_free": {"variable_leaves":128,"total_leaves":128,"vertices":128,"internal_gates":256},
  "rational": {"variable_leaves":192,"total_leaves":192,"vertices":192,"internal_gates":384},
  "formula_target_count": 2, "circuit_target_count": 0,
  "historical_pdf_byte_equivalence": False,
}
cfg = json.loads(Path(os.environ["OVERLAY_CONFIG"]).read_text())
assert cfg["challenge_module"] == "ComparatorChallenges.C_PermanentFormulaLowerBound"
assert cfg["solution_module"] == "Permanent"
assert cfg["theorem_names"] == [
  "PermanentFormulaLowerBound.permanent_divisionFree_formula_lower_bound",
  "PermanentFormulaLowerBound.permanent_rational_formula_lower_bound",
]
assert cfg["enable_nanoda"] is True
PY

scan_log="$output_dir/trust-boundary-scan.txt"
: > "$scan_log"
if grep -nE '\b(sorry|admit)\b|^[[:space:]]*(axiom|unsafe)[[:space:]]' "$solution_file" "$forge/$witness_path" >> "$scan_log"; then
  echo "prohibited solution or witness declaration/placeholder detected" >&2
  cat "$scan_log" >&2
  exit 1
fi
if grep -nE '^[[:space:]]*import[[:space:]]+All([[:space:]]|$)' "$solution_file" "$challenge_file" "$forge/$witness_path" >> "$scan_log"; then
  echo "hidden aggregate All dependency detected" >&2
  cat "$scan_log" >&2
  exit 1
fi
echo "solution/witness placeholder and unsafe/custom-axiom scan: clear" >> "$scan_log"
echo "overlay challenge placeholders: permitted challenge boundary only; never solution evidence" >> "$scan_log"
echo "aggregate All import scan: clear" >> "$scan_log"

{
  echo "family=OTP-C-PERMANENT"
  echo "surface=OTP-C-PERMANENT-FULL-FORMULA"
  echo "mathcert_head_sha=${MATHCERT_HEAD_SHA:-unknown}"
  echo "workflow_checkout_sha=${MATHCERT_WORKFLOW_SHA:-${GITHUB_SHA:-unknown}}"
  echo "lean=$lean_version_line"
  echo "upstream_historical_commit=$expected_historical_commit"
  echo "upstream_historical_tree=$expected_historical_tree"
  echo "protected_archive_sha256=$expected_archive_sha256"
  echo "protected_archive_bytes=$expected_archive_bytes"
  echo "forge_commit=$expected_forge_commit"
  echo "semantic_record_blob=$expected_semantic_blob"
  echo "overlay_json_blob=$expected_overlay_json_blob"
  echo "overlay_lean_blob=$expected_overlay_lean_blob"
  echo "solve_commit=$expected_solve_commit"
  echo "producer_packet_blob=$expected_packet_blob"
  echo "work_package_blob=$expected_work_package_blob"
} > "$output_dir/environment.txt"

cd "$upstream"
start_utc="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
lake build "$solution_module" 2>&1 | tee "$output_dir/solution-build.log"
lake build "$challenge_module" 2>&1 | tee "$output_dir/challenge-build.log"

axiom_file="MATHCERTPermanentFullFormulaReplayAxioms.lean"
{
  echo "import $solution_module"
  for theorem in "${theorem_names[@]}"; do echo "#print axioms $theorem"; done
} > "$axiom_file"
lake env lean "$axiom_file" 2>&1 | tee "$output_dir/theorem-axioms.log"
rm -f "$axiom_file"

THEOREMS="$(printf '%s\n' "${theorem_names[@]}")" AXIOM_LOG="$output_dir/theorem-axioms.log" AXIOM_REPORT="$output_dir/axiom-check.json" python3 - <<'PY'
import json, os, re
from pathlib import Path
text = Path(os.environ["AXIOM_LOG"]).read_text(encoding="utf-8")
allowed = {"propext", "Classical.choice", "Quot.sound"}
reports = []
for theorem in [x for x in os.environ["THEOREMS"].splitlines() if x]:
    m = re.search(r"'" + re.escape(theorem) + r"' depends on axioms:\s*\[(.*?)\]", text, re.S)
    if not m:
        raise SystemExit(f"missing theorem axiom report: {theorem}")
    axioms = {x.strip() for x in m.group(1).replace("\n", " ").split(",") if x.strip()}
    unexpected = sorted(axioms - allowed)
    if unexpected:
        raise SystemExit(f"unexpected axioms for {theorem}: {unexpected}")
    reports.append({"theorem": theorem, "axioms": sorted(axioms), "unexpected": []})
Path(os.environ["AXIOM_REPORT"]).write_text(json.dumps({"permitted": sorted(allowed), "reports": reports}, indent=2) + "\n", encoding="utf-8")
PY

lake env lean "$forge/$witness_path" 2>&1 | tee "$output_dir/nonvacuity-replay.log"
grep -Fq "permanent_divisionFree_formula_nonvacuous" "$forge/$witness_path"
grep -Fq "permanent_rational_formula_nonvacuous" "$forge/$witness_path"

lake exe comparator "$config" 2>&1 | tee "$output_dir/comparator.log"
end_utc="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
grep -Fq "Lean default kernel accepts the solution" "$output_dir/comparator.log"
grep -Fq "Nanoda kernel accepts the solution" "$output_dir/comparator.log"
grep -Fq "Your solution is okay!" "$output_dir/comparator.log"

START_UTC="$start_utc" END_UTC="$end_utc" OUTPUT_DIR="$output_dir" MATHCERT_HEAD_SHA="${MATHCERT_HEAD_SHA:-unknown}" WORKFLOW_SHA="${MATHCERT_WORKFLOW_SHA:-${GITHUB_SHA:-unknown}}" python3 - <<'PY'
import hashlib, json, os
from pathlib import Path
out = Path(os.environ["OUTPUT_DIR"])
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
files = {p.name: {"sha256": sha(p), "bytes": p.stat().st_size} for p in sorted(out.iterdir()) if p.is_file()}
record = {
  "schema_version":"1.0.0",
  "record_type":"openai_ten_proofs_permanent_full_formula_cert_replay_execution_evidence",
  "result_family":"OTP-C-PERMANENT",
  "surface_id":"OTP-C-PERMANENT-FULL-FORMULA",
  "execution": {
    "start_utc":os.environ["START_UTC"], "end_utc":os.environ["END_UTC"],
    "mathcert_head_sha":os.environ["MATHCERT_HEAD_SHA"],
    "workflow_checkout_sha":os.environ["WORKFLOW_SHA"],
    "clean_room_runner":True, "isolated_family_replay":True,
    "protected_overlay_ephemeral":True, "aggregate_all_import_used":False,
  },
  "targets":[
    "PermanentFormulaLowerBound.permanent_divisionFree_formula_lower_bound",
    "PermanentFormulaLowerBound.permanent_rational_formula_lower_bound",
  ],
  "results": {
    "solution_build":"pass", "challenge_build":"pass", "comparator":"pass",
    "lean_kernel":"accept", "nanoda":"accept", "nonvacuity_replay":"pass",
    "theorem_axiom_report":"permitted_only", "trust_boundary_scan":"clear",
  },
  "source_projection": {
    "coefficient_field":"complex", "dimension_threshold":32, "log_base":2,
    "division_free":{"variable_leaves":128,"total_leaves":128,"vertices":128,"internal_gates":256},
    "rational":{"variable_leaves":192,"total_leaves":192,"vertices":192,"internal_gates":384},
    "formula_target_count":2, "circuit_target_count":0,
    "historical_pdf_byte_equivalence":False,
  },
  "state": {"mathematical_target_proved":False,"aggregate_authority":False},
  "files":files,
}
(out / "evidence-summary.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
PY
find "$output_dir" -maxdepth 1 -type f -not -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > "$output_dir/SHA256SUMS"
echo "PERMANENT_FULL_FORMULA_CERT_REPLAY_EXECUTION_CLEAR"
