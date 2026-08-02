#!/usr/bin/env bash
set -euo pipefail

if (($# != 5)); then
  echo "usage: $0 FAMILY CONFIG SOLUTION_MODULE CHALLENGE_MODULE OUTPUT_DIR" >&2
  exit 64
fi

family="$1"
config="$2"
solution_module="$3"
challenge_module="$4"
output_dir="$5"

root="$(cd "$(dirname "$0")/.." && pwd)"
upstream="$root/upstream"
forge="$root/forge"
solve="$root/solve"
mkdir -p "$output_dir"
output_dir="$(cd "$output_dir" && pwd)"

expected_upstream_commit="e62211d28e3a9131950c89caa6542cfe5eff3bca"
expected_upstream_tree="2f8e7ac5ae7f157b6b1de636c2c343b1c7a7e365"
expected_forge_commit="cb0a203c36a9ef33270d62ab369df7bc27d3b242"
expected_solve_commit="443daf537dc7e4ee34ab43aeb01508d9177816ab"
expected_cert_wp_merge="677a58a126145977581050bcb5d12d5b6a99fb51"
expected_manuscript_sha="f318c6508c9d49ef876a5a26cd73928705f96c07bb43e92a0cb35bd3f666ea53"
expected_reasoning_sha="13b95999f060c0be2142089cfb8b17b75e9231c3c1f3fa0980445ff1b35f0b3b"

case "$family" in
  OTP-F-EHRHART)
    semantic_path="sources/OPENAI-TEN-PROOFS-001/semantic_audits/OTP-F-EHRHART.json"
    semantic_blob="a3dc4de4c38a80b7aec1fae6506b08e14d2e58bb"
    packet_path="work_packages/OPENAI_TEN_PROOFS_WP00/result_family_handoffs/OTP-F-EHRHART.json"
    packet_blob="4653985d4980113514266c3c421804437bacb019"
    intake_path="governance/result_family_intakes/OTP-F-EHRHART.json"
    intake_blob="1c6a5f349803bba09b000ceb3f8a53ee3038ca48"
    work_package_path="governance/result_family_work_packages/OTP-F-EHRHART-CERT-WP01.json"
    work_package_blob="056149e7a659fb6b24b7d7389a3dcd68bb581bcd"
    source_theorem="Chapter 8, Theorem 1.1, parsed P219 L18214-L18229"
    theorem_names=(
      Ehrhart.Volume.ehrhart_volume_inequality_for_sets
      Ehrhart.SimplexVolume.exists_centeredBody_sharp
      Ehrhart.SimplexVolume.barycenter_centeredSimplex
      Ehrhart.SimplexVolume.normalizedVolume_centeredSimplex
    )
    witness_names=(
      Ehrhart.SimplexVolume.exists_centeredBody_sharp
      Ehrhart.SimplexVolume.normalizedVolume_centeredSimplex
    )
    exclusions=(
      "No uniqueness or classification of all equality cases is submitted."
      "A successful replay does not by itself adjudicate or prove the mathematical theorem."
    )
    ;;
  OTP-J1-COMPACTNESS)
    semantic_path="sources/OPENAI-TEN-PROOFS-001/semantic_audits/OTP-J1-COMPACTNESS.json"
    semantic_blob="659396358d0d999c00011645f72602f30ccf6b0e"
    packet_path="work_packages/OPENAI_TEN_PROOFS_WP00/result_family_handoffs/OTP-J1-COMPACTNESS.json"
    packet_blob="2d9c6e555a03b71eb33c476321e7f2d311ed168f"
    intake_path="governance/result_family_intakes/OTP-J1-COMPACTNESS.json"
    intake_blob="d08eec02d7ee44f3bc2692cf7949c70d8e0f2bbf"
    work_package_path="governance/result_family_work_packages/OTP-J1-COMPACTNESS-CERT-WP01.json"
    work_package_blob="d80cade6d99c7ca54f4384a68e178b2f4335a8b2"
    source_theorem="Chapter 10, Theorem 1.1, parsed P236 L19757-L19791"
    theorem_names=(
      CompactnessConjecture.quantitativeCompactnessCounterexample
      CompactnessConjecture.compactnessCounterexample_bigO
      CompactnessConjecture.not_erdos_180
    )
    witness_names=(
      CompactnessConjecture.quantitativeCompactnessCounterexample
      CompactnessConjecture.compactnessCounterexample_bigO
    )
    exclusions=(
      "The explicit combinatorial construction is not independently submitted beyond the checked existential targets."
      "No historical compactness formulation outside the corrected cyclic-family statement is submitted."
      "A successful replay does not by itself adjudicate or prove the mathematical theorem."
    )
    ;;
  OTP-J2-TWO-DEGENERATE)
    semantic_path="sources/OPENAI-TEN-PROOFS-001/semantic_audits/OTP-J2-TWO-DEGENERATE.json"
    semantic_blob="7bd168c46921f64364b20021b6315d68f0fde7d0"
    packet_path="work_packages/OPENAI_TEN_PROOFS_WP00/result_family_handoffs/OTP-J2-TWO-DEGENERATE.json"
    packet_blob="0d226492bf13e13bc1a437be01104db3d4c96f79"
    intake_path="governance/result_family_intakes/OTP-J2-TWO-DEGENERATE.json"
    intake_blob="6e9cfee8f988e357aabdd53e2883220d170b7e60"
    work_package_path="governance/result_family_work_packages/OTP-J2-TWO-DEGENERATE-CERT-WP01.json"
    work_package_blob="dbbc4ab59f21b3f5cb2f313c51f754b9b306389c"
    source_theorem="Chapter 10, Theorem 1.2, parsed P236-P237 L19792-L19822"
    theorem_names=(
      TwoDegenerateGraphs.twoDegenerateExtremalCounterexample
      TwoDegenerateGraphs.not_erdos_146
    )
    witness_names=(
      TwoDegenerateGraphs.twoDegenerateExtremalCounterexample
    )
    exclusions=(
      "The additional coloring-side degree property is not attributed to source Theorem 1.2."
      "The underlying probabilistic or combinatorial construction is not independently submitted beyond the checked existential theorem."
      "A successful replay does not by itself adjudicate or prove the mathematical theorem."
    )
    ;;
  *)
    echo "unknown family: $family" >&2
    exit 64
    ;;
esac

assert_eq() {
  local actual="$1" expected="$2" label="$3"
  if [[ "$actual" != "$expected" ]]; then
    echo "$label mismatch: expected $expected, found $actual" >&2
    exit 1
  fi
}

git_blob() {
  local repo="$1" path="$2"
  git -C "$repo" rev-parse "HEAD:$path"
}

assert_eq "$(git -C "$upstream" rev-parse HEAD)" "$expected_upstream_commit" "upstream commit"
assert_eq "$(git -C "$upstream" rev-parse 'HEAD^{tree}')" "$expected_upstream_tree" "upstream tree"
assert_eq "$(git -C "$forge" rev-parse HEAD)" "$expected_forge_commit" "Forge commit"
assert_eq "$(git -C "$solve" rev-parse HEAD)" "$expected_solve_commit" "Solve commit"
assert_eq "$(git_blob "$forge" "$semantic_path")" "$semantic_blob" "semantic record blob"
assert_eq "$(git_blob "$solve" "$packet_path")" "$packet_blob" "Solve packet blob"
assert_eq "$(git -C "$root" rev-parse "$expected_cert_wp_merge:$intake_path")" "$intake_blob" "Cert intake blob"
assert_eq "$(git -C "$root" rev-parse "$expected_cert_wp_merge:$work_package_path")" "$work_package_blob" "Cert work-package blob"

config_path="$upstream/$config"
challenge_file="$upstream/${challenge_module//./\/}.lean"
solution_file="$upstream/${solution_module//./\/}.lean"
for required in "$config_path" "$challenge_file" "$solution_file"; do
  [[ -f "$required" ]] || { echo "missing replay input: $required" >&2; exit 1; }
done

curl --fail --location --retry 3 --silent --show-error \
  https://cdn.openai.com/pdf/ten-proofs-oai.pdf -o "$output_dir/manuscript.pdf"
curl --fail --location --retry 3 --silent --show-error \
  https://cdn.openai.com/pdf/reasoning-walkthroughs.pdf -o "$output_dir/reasoning-walkthroughs.pdf"
assert_eq "$(sha256sum "$output_dir/manuscript.pdf" | cut -d' ' -f1)" "$expected_manuscript_sha" "manuscript SHA-256"
assert_eq "$(sha256sum "$output_dir/reasoning-walkthroughs.pdf" | cut -d' ' -f1)" "$expected_reasoning_sha" "reasoning-notes SHA-256"

{
  echo "family=$family"
  echo "github_sha=${GITHUB_SHA:-unknown}"
  echo "runner_image=${ImageOS:-unknown}-${ImageVersion:-unknown}"
  echo "uname=$(uname -a)"
  echo "lean=$(lean --version | head -n1)"
  echo "lake=$(lake --version | head -n1)"
  echo "go=$(go version)"
  echo "rustc=$(rustc --version)"
  echo "cargo=$(cargo --version)"
  echo "upstream_commit=$(git -C "$upstream" rev-parse HEAD)"
  echo "upstream_tree=$(git -C "$upstream" rev-parse 'HEAD^{tree}')"
  echo "mathlib_commit=$(git -C "$upstream/.lake/packages/mathlib" rev-parse HEAD)"
  echo "comparator_commit=$(git -C "$upstream/.lake/packages/Comparator" rev-parse HEAD)"
  echo "lean4checker_commit=$(git -C "$upstream/.lake/packages/Comparator/.lake/packages/Lean4Checker" rev-parse HEAD)"
  echo "lean4export_commit=$(git -C "$root/tools/lean4export" rev-parse HEAD)"
  echo "landrun_commit=811cfff51ceaf3d9843708aa6d22e9b84ccac8b4d"
  echo "nanoda_commit=$(git -C "$root/tools/nanoda" rev-parse HEAD)"
  echo "landrun_binary_sha256=$(sha256sum "${COMPARATOR_LANDRUN_REAL}" | cut -d' ' -f1)"
  echo "landrun_adapter_sha256=$(sha256sum "${COMPARATOR_LANDRUN}" | cut -d' ' -f1)"
  echo "lean4export_binary_sha256=$(sha256sum "${COMPARATOR_LEAN4EXPORT}" | cut -d' ' -f1)"
  echo "nanoda_binary_sha256=$(sha256sum "${COMPARATOR_NANODA}" | cut -d' ' -f1)"
} > "$output_dir/environment.txt"

{
  echo "config_path=$config"
  echo "config_blob=$(git_blob "$upstream" "$config")"
  echo "challenge_path=${challenge_module//./\/}.lean"
  echo "challenge_blob=$(git_blob "$upstream" "${challenge_module//./\/}.lean")"
  echo "solution_path=${solution_module//./\/}.lean"
  echo "solution_blob=$(git_blob "$upstream" "${solution_module//./\/}.lean")"
  echo "semantic_path=$semantic_path"
  echo "semantic_blob=$semantic_blob"
  echo "packet_path=$packet_path"
  echo "packet_blob=$packet_blob"
  echo "intake_path=$intake_path"
  echo "intake_blob=$intake_blob"
  echo "work_package_path=$work_package_path"
  echo "work_package_blob=$work_package_blob"
  echo "manuscript_sha256=$expected_manuscript_sha"
  echo "reasoning_notes_sha256=$expected_reasoning_sha"
} > "$output_dir/source-identities.txt"

scan_log="$output_dir/trust-boundary-scan.txt"
: > "$scan_log"
if grep -nE '\b(sorry|admit)\b|^[[:space:]]*(axiom|opaque|unsafe)[[:space:]]' "$solution_file" >> "$scan_log"; then
  echo "prohibited solution declaration or placeholder detected" >&2
  cat "$scan_log" >&2
  exit 1
fi
if grep -nE '^[[:space:]]*import[[:space:]]+All([[:space:]]|$)' "$solution_file" "$challenge_file" >> "$scan_log"; then
  echo "hidden aggregate All dependency detected" >&2
  cat "$scan_log" >&2
  exit 1
fi
echo "solution placeholder/unsafe/custom-axiom scan: clear" >> "$scan_log"
echo "aggregate All import scan: clear" >> "$scan_log"

cd "$upstream"
start_utc="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
set -o pipefail
lake build "$solution_module" 2>&1 | tee "$output_dir/solution-build.log"
lake build "$challenge_module" 2>&1 | tee "$output_dir/challenge-build.log"

axiom_file="MATHCERTReplayAxioms.lean"
{
  echo "import $solution_module"
  for theorem in "${theorem_names[@]}"; do
    echo "#print axioms $theorem"
  done
} > "$axiom_file"
lake env lean "$axiom_file" 2>&1 | tee "$output_dir/theorem-axioms.log"
rm -f "$axiom_file"

lake exe comparator "$config" 2>&1 | tee "$output_dir/comparator.log"
end_utc="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

grep -Fq "Lean default kernel accepts the solution" "$output_dir/comparator.log"
grep -Fq "Nanoda kernel accepts the solution" "$output_dir/comparator.log"
grep -Fq "Your solution is okay!" "$output_dir/comparator.log"

for theorem in "${theorem_names[@]}"; do
  grep -Fq "'$theorem' depends on axioms:" "$output_dir/theorem-axioms.log"
done
if grep -Ev "depends on axioms:|^[[:space:]]*(propext|Classical.choice|Quot.sound)[,\]]?$|^[[:space:]]*$" "$output_dir/theorem-axioms.log" \
    | grep -E "depends on axioms|axioms:" >/dev/null; then
  echo "unexpected theorem axiom report format" >&2
  exit 1
fi
for forbidden in sorryAx Lean.trustCompiler; do
  if grep -Fq "$forbidden" "$output_dir/theorem-axioms.log"; then
    echo "forbidden axiom in theorem report: $forbidden" >&2
    exit 1
  fi
done

FAMILY="$family" SOURCE_THEOREM="$source_theorem" START_UTC="$start_utc" END_UTC="$end_utc" \
CONFIG="$config" SOLUTION_MODULE="$solution_module" CHALLENGE_MODULE="$challenge_module" \
THEOREMS="$(printf '%s\n' "${theorem_names[@]}")" WITNESSES="$(printf '%s\n' "${witness_names[@]}")" \
EXCLUSIONS="$(printf '%s\n' "${exclusions[@]}")" OUTPUT_DIR="$output_dir" \
python3 - <<'PY'
import hashlib
import json
import os
from pathlib import Path

out = Path(os.environ["OUTPUT_DIR"])

def lines(name: str) -> list[str]:
    return [x for x in os.environ[name].splitlines() if x]

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

files = {}
for path in sorted(out.iterdir()):
    if path.is_file() and path.suffix != ".pdf":
        files[path.name] = {"sha256": sha(path), "bytes": path.stat().st_size}

record = {
    "schema_version": "1.0.0",
    "record_type": "openai_ten_proofs_family_replay_evidence",
    "result_family": os.environ["FAMILY"],
    "execution": {
        "start_utc": os.environ["START_UTC"],
        "end_utc": os.environ["END_UTC"],
        "github_head": os.environ.get("GITHUB_SHA", "unknown"),
        "clean_room_runner": True,
        "isolated_family_replay": True,
        "aggregate_all_import_used": False,
    },
    "targets": {
        "config": os.environ["CONFIG"],
        "challenge_module": os.environ["CHALLENGE_MODULE"],
        "solution_module": os.environ["SOLUTION_MODULE"],
        "theorem_names": lines("THEOREMS"),
        "nonvacuity_witnesses": lines("WITNESSES"),
    },
    "results": {
        "challenge_build": "pass",
        "solution_build": "pass",
        "comparator": "pass",
        "lean_kernel": "accept",
        "nanoda": "accept",
        "theorem_axiom_report": "permitted_only",
        "trust_boundary_scan": "clear",
    },
    "semantic_attestation": {
        "source_theorem": os.environ["SOURCE_THEOREM"],
        "scope_exclusions": lines("EXCLUSIONS"),
        "status": "pending_exact_head_non_author_specialist_review",
    },
    "route_state": {
        "proposed_route": None,
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

find "$output_dir" -maxdepth 1 -type f -not -name '*.pdf' -print0 \
  | sort -z | xargs -0 sha256sum > "$output_dir/SHA256SUMS"
rm -f "$output_dir/manuscript.pdf" "$output_dir/reasoning-walkthroughs.pdf"

echo "completed isolated replay for $family"
