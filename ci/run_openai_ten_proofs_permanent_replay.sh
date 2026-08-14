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

expected_cert_wp_merge="4b5d9e81afea50b5b51b4e390065f52275c886cd"
expected_work_package_blob="f3000340c2699ec819acbcd223c1ee4c63af1cc8"
work_package_path="governance/result_family_work_package_successors/OTP-C-PERMANENT-CERT-WP01.json"
expected_forge_commit="60f6e06c957139447bf5943eed731941b22ac608"
expected_semantic_blob="3e04bd16bd8a91eaf9b6702de89fcdcc72f61099"
semantic_path="sources/OPENAI-TEN-PROOFS-001/semantic/OTP-C-PERMANENT/semantic_audit_record.json"
expected_witness_blob="e756c8476bac1795f3fb8ca0b7235d3a4a5c59ea"
witness_path="sources/OPENAI-TEN-PROOFS-001/semantic/OTP-C-PERMANENT/PermanentFormulaNonvacuity.lean"
expected_solve_commit="90f8a8544e546a603b34c9b27b2d6a4a68e06de8"
expected_packet_blob="a993c530880021930a2b468e76235b91122ca854"
packet_path="work_packages/OPENAI_TEN_PROOFS_WP00/result_family_handoffs/OTP-C-PERMANENT.json"

archive_url="https://github.com/grandchallenge/MATHFORGE/releases/download/otp-c-permanent-source-e62211d2-candidate-001/openai-ten-proofs-e62211d2.tar"
expected_archive_sha256="3022e62ffbed8f5f74d232034a703dc645e6b301879dff1e87df72979914294f"
expected_archive_bytes="21022720"
expected_historical_commit="e62211d28e3a9131950c89caa6542cfe5eff3bca"
expected_historical_tree="2f8e7ac5ae7f157b6b1de636c2c343b1c7a7e365"
expected_lean_version="4.32.0"
expected_mathlib_commit="81a5d257c8e410db227a6665ed08f64fea08e997"
expected_comparator_commit="07bc4ea40f2266dcb861820a2ec1fa3244ed307f"
expected_lean4checker_commit="b7398199245524275543dec6113229c9bb4902e5"
expected_lean4export_commit="4e7915201d3f9f04470d9eae002fa695f7cdc589"
expected_landrun_commit="811cfff51ceaf3d9843708aa6d22e9b84ccac8b4"
expected_nanoda_commit="ddfac2bf5a7b56cb46e141494427ff3dd55963c7"

config="ComparatorChallenges/C_PermanentFormulaLowerBound.json"
solution_module="Permanent"
challenge_module="ComparatorChallenges.C_PermanentFormulaLowerBound"
challenge_file="$upstream/ComparatorChallenges/C_PermanentFormulaLowerBound.lean"
solution_file="$upstream/Permanent.lean"

theorem_names=(
  PermanentFormulaLowerBound.permanent_divisionFree_formula_logarithmic_lower_bound
  PermanentFormulaLowerBound.permanent_rational_formula_logarithmic_lower_bound
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

assert_eq "$(git -C "$root" rev-parse "$expected_cert_wp_merge:$work_package_path")" "$expected_work_package_blob" "Cert work-package blob"
assert_eq "$(git -C "$forge" rev-parse HEAD)" "$expected_forge_commit" "Forge commit"
assert_eq "$(git_blob "$forge" "$semantic_path")" "$expected_semantic_blob" "Forge semantic record blob"
assert_eq "$(git_blob "$forge" "$witness_path")" "$expected_witness_blob" "Forge nonvacuity witness blob"
assert_eq "$(git -C "$solve" rev-parse HEAD)" "$expected_solve_commit" "Solve commit"
assert_eq "$(git_blob "$solve" "$packet_path")" "$expected_packet_blob" "Solve packet blob"

for required in "$upstream/lean-toolchain" "$upstream/lake-manifest.json" "$upstream/$config" "$challenge_file" "$solution_file"; do
  [[ -f "$required" ]] || { echo "missing replay input: $required" >&2; exit 1; }
done

# Protected family-file identities from the source-reassertion record.
assert_eq "$(sha_file "$solution_file")" "3bd469c20bc2277a13be3f9353ce47ad0c2070a330355daa78a9e59f1ca1d3c6" "Permanent.lean SHA-256"
assert_eq "$(sha_file "$challenge_file")" "fc97578bcbb072ff82383e4c903107130ba3dd1a2209235ab32270c7df37f83d" "challenge SHA-256"
assert_eq "$(sha_file "$upstream/$config")" "f80482f4a163041e036e26bb687690559cc36504e347b0ea3df0d626cfb965bb" "Comparator config SHA-256"
assert_eq "$(sha_file "$upstream/lean-toolchain")" "2773c517aa90b66ea8a2c52bddddf84393157797f8341be0df45294fff7fd32e" "lean-toolchain SHA-256"
assert_eq "$(sha_file "$upstream/lake-manifest.json")" "a6faf8302fe77f77f499446c27b8829b1af8dbc7847298b682556baa2a0b135e" "lake-manifest SHA-256"

assert_eq "$(git -C "$upstream/.lake/packages/mathlib" rev-parse HEAD)" "$expected_mathlib_commit" "mathlib commit"
assert_eq "$(git -C "$upstream/.lake/packages/Comparator" rev-parse HEAD)" "$expected_comparator_commit" "Comparator commit"
assert_eq "$(git -C "$upstream/.lake/packages/Lean4Checker" rev-parse HEAD)" "$expected_lean4checker_commit" "Lean4Checker commit"
assert_eq "$(git -C "$root/tools/lean4export" rev-parse HEAD)" "$expected_lean4export_commit" "lean4export commit"
assert_eq "$(git -C "$root/tools/landrun" rev-parse HEAD)" "$expected_landrun_commit" "Landrun commit"
assert_eq "$(git -C "$root/tools/nanoda" rev-parse HEAD)" "$expected_nanoda_commit" "Nanoda commit"

WORK_PACKAGE="$root/$work_package_path" CONFIG_PATH="$upstream/$config" python3 - <<'PY'
import json, os
from pathlib import Path
wp = json.loads(Path(os.environ["WORK_PACKAGE"]).read_text())
assert wp["result_family"] == "OTP-C-PERMANENT"
assert wp["execution"]["aggregate_import_required"] is False
assert wp["execution"]["comparator_config"] == "ComparatorChallenges/C_PermanentFormulaLowerBound.json"
assert wp["execution"]["solution_module"] == "Permanent"
assert wp["execution"]["challenge_module"] == "ComparatorChallenges.C_PermanentFormulaLowerBound"
sp = wp["target_scope"]["source_projection"]
assert sp == {
    "formula_target_count": 2,
    "circuit_target_count": 0,
    "coefficient_field": "complex",
    "dimension_threshold": 32,
    "log_base": 2,
    "division_free_variable_leaf_constant": 128,
    "division_free_source_gate_constant": 256,
    "rational_variable_leaf_constant": 192,
    "rational_source_gate_constant": 384,
    "gate_bounds_in_work_package": False,
    "total_leaves_vertices_in_work_package": False,
    "historical_pdf_byte_equivalence": False,
}
assert wp["route_state"]["certification_route_registry_entry"] is None
assert wp["route_state"]["proposed_route_record"] is None
assert wp["route_state"]["cert_output"] is None
assert wp["route_state"]["mathematical_target_proved"] is False
cfg = json.loads(Path(os.environ["CONFIG_PATH"]).read_text())
text = json.dumps(cfg)
for name in [
    "permanent_divisionFree_formula_logarithmic_lower_bound",
    "permanent_rational_formula_logarithmic_lower_bound",
]:
    assert name in text, name
for forbidden in ["permanent_circuit_loglog_lower_bound", "internalGateCount", "vertexCount"]:
    assert forbidden not in text, forbidden
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
echo "challenge placeholders: Comparator boundary only; not solution evidence" >> "$scan_log"
echo "aggregate All import scan: clear" >> "$scan_log"

{
  echo "family=OTP-C-PERMANENT"
  echo "mathcert_head_sha=${MATHCERT_HEAD_SHA:-unknown}"
  echo "workflow_checkout_sha=${MATHCERT_WORKFLOW_SHA:-${GITHUB_SHA:-unknown}}"
  echo "runner_image=${ImageOS:-unknown}-${ImageVersion:-unknown}"
  echo "uname=$(uname -a)"
  echo "lean=$lean_version_line"
  echo "lake=$(lake --version | head -n1)"
  echo "upstream_historical_commit=$expected_historical_commit"
  echo "upstream_historical_tree=$expected_historical_tree"
  echo "protected_archive_sha256=$expected_archive_sha256"
  echo "protected_archive_bytes=$expected_archive_bytes"
  echo "mathlib_commit=$(git -C "$upstream/.lake/packages/mathlib" rev-parse HEAD)"
  echo "comparator_commit=$(git -C "$upstream/.lake/packages/Comparator" rev-parse HEAD)"
  echo "lean4checker_commit=$(git -C "$upstream/.lake/packages/Lean4Checker" rev-parse HEAD)"
  echo "lean4export_commit=$(git -C "$root/tools/lean4export" rev-parse HEAD)"
  echo "landrun_commit=$(git -C "$root/tools/landrun" rev-parse HEAD)"
  echo "nanoda_commit=$(git -C "$root/tools/nanoda" rev-parse HEAD)"
  echo "landrun_binary_sha256=$(sha_file "${COMPARATOR_LANDRUN_REAL}")"
  echo "landrun_adapter_sha256=$(sha_file "${COMPARATOR_LANDRUN}")"
  echo "lean4export_binary_sha256=$(sha_file "${COMPARATOR_LEAN4EXPORT}")"
  echo "nanoda_binary_sha256=$(sha_file "${COMPARATOR_NANODA}")"
} > "$output_dir/environment.txt"

{
  echo "archive_url=$archive_url"
  echo "archive_asset_id=514295009"
  echo "archive_release_id=370507312"
  echo "archive_release_tag=otp-c-permanent-source-e62211d2-candidate-001"
  echo "archive_sha256=$expected_archive_sha256"
  echo "archive_bytes=$expected_archive_bytes"
  echo "historical_commit=$expected_historical_commit"
  echo "historical_tree=$expected_historical_tree"
  echo "solution_sha256=$(sha_file "$solution_file")"
  echo "challenge_sha256=$(sha_file "$challenge_file")"
  echo "config_sha256=$(sha_file "$upstream/$config")"
  echo "lean_toolchain_sha256=$(sha_file "$upstream/lean-toolchain")"
  echo "lake_manifest_sha256=$(sha_file "$upstream/lake-manifest.json")"
  echo "forge_commit=$expected_forge_commit"
  echo "semantic_record_blob=$expected_semantic_blob"
  echo "nonvacuity_witness_blob=$expected_witness_blob"
  echo "solve_commit=$expected_solve_commit"
  echo "producer_packet_blob=$expected_packet_blob"
  echo "cert_work_package_merge=$expected_cert_wp_merge"
  echo "cert_work_package_blob=$expected_work_package_blob"
} > "$output_dir/source-identities.txt"

cd "$upstream"
start_utc="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
lake build "$solution_module" 2>&1 | tee "$output_dir/solution-build.log"
lake build "$challenge_module" 2>&1 | tee "$output_dir/challenge-build.log"

axiom_file="MATHCERTPermanentReplayAxioms.lean"
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

# Compiler elaboration of the exact protected witness file is authoritative. The
# source is namespace-scoped, so text-presence checks use the bare declaration
# identifiers rather than incorrectly requiring fully qualified source text.
lake env lean "$forge/$witness_path" 2>&1 | tee "$output_dir/nonvacuity-replay.log"
grep -Fq "permanent_divisionFree_formula_nonvacuous" "$forge/$witness_path"
grep -Fq "permanent_rational_formula_nonvacuous" "$forge/$witness_path"

grep -Fq "version 4.32.0" <(lean --version)
lake exe comparator "$config" 2>&1 | tee "$output_dir/comparator.log"
end_utc="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
grep -Fq "Lean default kernel accepts the solution" "$output_dir/comparator.log"
grep -Fq "Nanoda kernel accepts the solution" "$output_dir/comparator.log"
grep -Fq "Your solution is okay!" "$output_dir/comparator.log"

FAMILY="OTP-C-PERMANENT" START_UTC="$start_utc" END_UTC="$end_utc" CONFIG="$config" SOLUTION_MODULE="$solution_module" CHALLENGE_MODULE="$challenge_module" THEOREMS="$(printf '%s\n' "${theorem_names[@]}")" WITNESSES="$(printf '%s\n' "${witness_names[@]}")" OUTPUT_DIR="$output_dir" MATHCERT_HEAD_SHA="${MATHCERT_HEAD_SHA:-unknown}" WORKFLOW_SHA="${MATHCERT_WORKFLOW_SHA:-${GITHUB_SHA:-unknown}}" python3 - <<'PY'
import hashlib, json, os
from pathlib import Path
out = Path(os.environ["OUTPUT_DIR"])
lines = lambda name: [x for x in os.environ[name].splitlines() if x]
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
files = {p.name: {"sha256": sha(p), "bytes": p.stat().st_size} for p in sorted(out.iterdir()) if p.is_file()}
record = {
  "schema_version": "1.0.0",
  "record_type": "openai_ten_proofs_permanent_cert_replay_execution_evidence",
  "result_family": os.environ["FAMILY"],
  "execution": {
    "start_utc": os.environ["START_UTC"],
    "end_utc": os.environ["END_UTC"],
    "mathcert_head_sha": os.environ["MATHCERT_HEAD_SHA"],
    "workflow_checkout_sha": os.environ["WORKFLOW_SHA"],
    "clean_room_runner": True,
    "isolated_family_replay": True,
    "aggregate_all_import_used": False,
  },
  "source_authority": {
    "historical_repository": "openai/ten-proofs",
    "historical_commit": "e62211d28e3a9131950c89caa6542cfe5eff3bca",
    "historical_tree": "2f8e7ac5ae7f157b6b1de636c2c343b1c7a7e365",
    "gcl_archive_release_id": 370507312,
    "gcl_archive_asset_id": 514295009,
    "gcl_archive_sha256": "3022e62ffbed8f5f74d232034a703dc645e6b301879dff1e87df72979914294f",
    "gcl_archive_bytes": 21022720,
  },
  "targets": {
    "config": os.environ["CONFIG"],
    "challenge_module": os.environ["CHALLENGE_MODULE"],
    "solution_module": os.environ["SOLUTION_MODULE"],
    "theorem_names": lines("THEOREMS"),
    "nonvacuity_witnesses": lines("WITNESSES"),
  },
  "results": {
    "solution_build": "pass",
    "challenge_build": "pass",
    "comparator": "pass",
    "lean_kernel": "accept",
    "nanoda": "accept",
    "nonvacuity_replay": "pass",
    "theorem_axiom_report": "permitted_only",
    "trust_boundary_scan": "clear",
    "semantic_concordance": "protected_predecessor_reconfirmed",
  },
  "source_projection": {
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
  },
  "route_state": {
    "requested_future_route_id": "MC-ROUTE-OTP-C-PERMANENT-FORMULA",
    "proposed_route_record": None,
    "registered_route": None,
    "may_adjudicate": False,
    "cert_output": None,
    "mathematical_target_proved": False,
    "may_promote_claim": False,
  },
  "files": files,
}
(out / "evidence-summary.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
PY

find "$output_dir" -maxdepth 1 -type f -not -name 'SHA256SUMS' -print0 | sort -z | xargs -0 sha256sum > "$output_dir/SHA256SUMS"
echo "PERMANENT_FORMULA_CERT_REPLAY_EXECUTION_CLEAR"
