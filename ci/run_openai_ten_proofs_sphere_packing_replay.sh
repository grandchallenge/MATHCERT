#!/usr/bin/env bash
set -Eeuo pipefail

if (($# != 1)); then
  echo "usage: $0 OUTPUT_DIR" >&2
  exit 64
fi

output_dir="$1"
root="$(cd "$(dirname "$0")/.." && pwd)"
upstream="$root/upstream"
forge_composite="$root/forge-composite"
forge_bridge="$root/forge-bridge"
solve="$root/solve"
mkdir -p "$output_dir"
output_dir="$(cd "$output_dir" && pwd)"

family="OTP-A-SPHERE-PACKING"
tracker="https://github.com/grandchallenge/MATHCERT/issues/154"
work_package_path="governance/result_family_work_package_successors/OTP-A-SPHERE-PACKING-CERT-WP-001.json"
expected_work_package_merge="54b883bb5c6ffaf099efd7270df3519a45b13038"
expected_work_package_blob="f0c91d1959035f35843c383920dfba0b6c24b485"
expected_routes_blob="2d17473b4731aa9d9c630b1e7777ad4bd794d993"

expected_upstream_commit="94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6"
expected_upstream_tree="174289e4d4958cb0509874e6e53400e098213de7"
config="ComparatorChallenges/A_SpherePacking.json"
challenge="ComparatorChallenges/A_SpherePacking.lean"
solution="SpherePacking.lean"
expected_config_blob="46b2e7b49da43fb17a7efa88652f8ee1adc01cbe"
expected_challenge_blob="2477846e1883534837340c636fd928b091509783"
expected_solution_blob="e6117934a80142a8249356fdafa797eba030e920"
expected_lake_manifest_blob="046e8de7f46832fbf092e3fb815efae01e4a2129"
expected_lean_toolchain_blob="94b9f495baff80fd9cb44aad8f4762cb3b2066fe"

expected_forge_composite_commit="706d0291370bf3f14aa37be0823e33d06f7343b0"
composite_path="sources/OPENAI-TEN-PROOFS-001/semantic/OTP-A-SPHERE-PACKING-COMPOSITE/audit_record.json"
expected_composite_blob="b2e309ad96e750651fc7149a6bad54c6bf99015b"
expected_forge_bridge_commit="5a0cb9a7b7eef210dd0fce5c527d09b6eef3bc12"
bridge_path="sources/OPENAI-TEN-PROOFS-001/semantic/OTP-A-SPHERE-PACKING-BRIDGE/audit_record.json"
expected_bridge_blob="7858b156fc4490ecc6e3572dcf449d84dcc99f93"
expected_solve_commit="c19735edf4c16ac9765bb66c7209bbf11bf1312e"
packet_path="work_packages/OPENAI_TEN_PROOFS_WP00/result_family_handoff_successors/OTP-A-SPHERE-PACKING.json"
expected_packet_blob="9e3b46972bf01ac3d24c6a0ae5f522799335ecd1"

expected_pdf_sha256="ebc561ab5c53dbd240e17a8fdb6fffeb648591eca85dbfc7466f563638f8c566"
expected_pdf_bytes="2487031"
pdf_url="https://cdn.openai.com/pdf/ten-proofs-oai.pdf"

expected_lean_version="4.32.0"
expected_lean_commit="8c9756b28d64dab099da31a4c09229a9e6a2ef35"
expected_mathlib_commit="81a5d257c8e410db227a6665ed08f64fea08e997"
expected_comparator_commit="07bc4ea40f2266dcb861820a2ec1fa3244ed307f"
expected_lean4checker_commit="b7398199245524275543dec6113229c9bb4902e5"
expected_lean4export_commit="4e7915201d3f9f04470d9eae002fa695f7cdc589"
expected_nanoda_commit="ddfac2bf5a7b56cb46e141494427ff3dd55963c7"
expected_landrun_commit="811cfff51ceaf3d9843708aa6d22e9b84ccac8b4"
expected_landrun_sha256="a4ba9ed1b6b53f9cfd57b9fb1e4f8f3c3ab69cf6a0147764ff70303a8306f858"
expected_lean4export_sha256="e57369980b0b81228580ce08066fb9bd738e717e002673a143f4956d217266b0"
expected_nanoda_sha256="60cc30add2758abce965f122b4e85f1fdd7c23607ea67680cec6721aa2ef23f0"
expected_adapter_sha256="84d900d75bdc76c2c4168484a929e448be36fca20d093c42cac15ed923fe3f1d"

theorem_names=(
  PackingBounds.FullMain.exact_limit
  PackingBounds.FullMain.exact_binary_exponent
  PackingBounds.PackingBridge.sphere_packing_sharp_asymptotic_upper
  PackingBounds.sharpFullCohnElkiesManuscriptConclusions
)
classifications=(
  direct_source_theorem_projection_modulo_proved_full_radial_equivalence
  derived_base_two_logarithmic_consequence
  source_faithful_displayed_consequence_with_proved_scale_normalization
  source_faithful_derived_composite_certificate
)
qualifications=(
  "The ten-field composite is not a single verbatim manuscript theorem."
  "The 30-decimal base-two exponent enclosure is a formal numerical consequence of the exact alpha_* expression, not manuscript-authored precision."
  "The packing bridge relies on proved positive rescaling invariance and unit-separation supremum equivalence; declaration-name similarity is not used as authority."
  "The explicit little-o witness is a normal form of the source asymptotic and is not a stronger rate claim."
  "No whole-chapter semantic equivalence or independent proof certification is transferred by this packet."
)
nonvacuity_evidence=(
  CohnElkies.admissible_nonempty
  fullQuotientSet_eq_radial
  "SpherePacking singleton unit-separated packing witness"
  SpherePacking.upper_packing_density_le_one
  "positive-dimensional bridge quantification"
)

assert_eq() {
  if [[ "$1" != "$2" ]]; then
    echo "$3 mismatch: expected $2, found $1" >&2
    exit 1
  fi
}

git_blob() { git -C "$1" rev-parse "HEAD:$2"; }
sha_file() { sha256sum "$1" | cut -d' ' -f1; }

# Protected MATHCERT authority and no route mutation.
assert_eq "$(git -C "$root" rev-parse "$expected_work_package_merge:$work_package_path")" "$expected_work_package_blob" "protected work-package blob"
assert_eq "$(git -C "$root" rev-parse "HEAD:$work_package_path")" "$expected_work_package_blob" "current work-package blob"
assert_eq "$(git -C "$root" rev-parse HEAD:governance/certification_routes.json)" "$expected_routes_blob" "certification route registry blob"

# Exact upstream and upstream-file identities.
assert_eq "$(git -C "$upstream" rev-parse HEAD)" "$expected_upstream_commit" "upstream commit"
assert_eq "$(git -C "$upstream" rev-parse 'HEAD^{tree}')" "$expected_upstream_tree" "upstream tree"
assert_eq "$(git_blob "$upstream" "$config")" "$expected_config_blob" "Comparator config blob"
assert_eq "$(git_blob "$upstream" "$challenge")" "$expected_challenge_blob" "challenge blob"
assert_eq "$(git_blob "$upstream" "$solution")" "$expected_solution_blob" "solution blob"
assert_eq "$(git_blob "$upstream" lake-manifest.json)" "$expected_lake_manifest_blob" "lake-manifest blob"
assert_eq "$(git_blob "$upstream" lean-toolchain)" "$expected_lean_toolchain_blob" "lean-toolchain blob"

# Exact Forge and Solve authorities.
assert_eq "$(git -C "$forge_composite" rev-parse HEAD)" "$expected_forge_composite_commit" "Forge composite commit"
assert_eq "$(git_blob "$forge_composite" "$composite_path")" "$expected_composite_blob" "Forge composite semantic blob"
assert_eq "$(git -C "$forge_bridge" rev-parse HEAD)" "$expected_forge_bridge_commit" "Forge bridge commit"
assert_eq "$(git_blob "$forge_bridge" "$bridge_path")" "$expected_bridge_blob" "Forge bridge semantic blob"
assert_eq "$(git -C "$solve" rev-parse HEAD)" "$expected_solve_commit" "Solve handoff commit"
assert_eq "$(git_blob "$solve" "$packet_path")" "$expected_packet_blob" "Solve packet blob"

# Exact work-package semantic and authority state.
WORK_PACKAGE="$root/$work_package_path" CONFIG_PATH="$upstream/$config" python3 - <<'PY'
import json, os
from pathlib import Path
wp=json.loads(Path(os.environ['WORK_PACKAGE']).read_text())
cfg=json.loads(Path(os.environ['CONFIG_PATH']).read_text())
expected_targets=[
 'PackingBounds.FullMain.exact_limit',
 'PackingBounds.FullMain.exact_binary_exponent',
 'PackingBounds.PackingBridge.sphere_packing_sharp_asymptotic_upper',
 'PackingBounds.sharpFullCohnElkiesManuscriptConclusions',
]
expected_classes=[
 'direct_source_theorem_projection_modulo_proved_full_radial_equivalence',
 'derived_base_two_logarithmic_consequence',
 'source_faithful_displayed_consequence_with_proved_scale_normalization',
 'source_faithful_derived_composite_certificate',
]
expected_quals=[
 'The ten-field composite is not a single verbatim manuscript theorem.',
 'The 30-decimal base-two exponent enclosure is a formal numerical consequence of the exact alpha_* expression, not manuscript-authored precision.',
 'The packing bridge relies on proved positive rescaling invariance and unit-separation supremum equivalence; declaration-name similarity is not used as authority.',
 'The explicit little-o witness is a normal form of the source asymptotic and is not a stronger rate claim.',
 'No whole-chapter semantic equivalence or independent proof certification is transferred by this packet.',
]
expected_nonvacuity=[
 'CohnElkies.admissible_nonempty',
 'fullQuotientSet_eq_radial',
 'SpherePacking singleton unit-separated packing witness',
 'SpherePacking.upper_packing_density_le_one',
 'positive-dimensional bridge quantification',
]
assert wp['work_package_id']=='OTP-A-SPHERE-PACKING-CERT-WP-001'
assert wp['target_scope']['lean_theorems']==expected_targets
assert wp['target_scope']['classifications']==expected_classes
assert wp['target_scope']['mandatory_qualifications']==expected_quals
assert wp['target_scope']['nonvacuity']['evidence']==expected_nonvacuity
assert wp['execution_contract']['deterministic_commands']==[
 'lake exe cache get','lake build SpherePacking','lake exe comparator ComparatorChallenges/A_SpherePacking.json']
assert wp['execution_contract']['aggregate_import_required'] is False
assert wp['execution_contract']['permitted_axioms']==['propext','Quot.sound','Classical.choice']
assert cfg['theorem_names']==expected_targets
assert cfg['permitted_axioms']==['propext','Quot.sound','Classical.choice']
assert cfg['enable_nanoda'] is True
route=wp['route_state']
assert route=={
 'requested_future_route':'MC-ROUTE-OTP-A-SPHERE-PACKING',
 'certification_route_registry_entry':None,
 'route_registered':False,
 'may_adjudicate':False,
 'adjudication':None,
 'cert_output':None,
 'mathematical_target_proved':False,
 'aggregate_authority':False,
 'may_promote_claim':False,
}
PY

# Reacquire exact current official source bytes.
curl --fail --location --retry 4 --silent --show-error "$pdf_url" -o "$output_dir/ten-proofs-oai.pdf"
assert_eq "$(stat -c '%s' "$output_dir/ten-proofs-oai.pdf")" "$expected_pdf_bytes" "source PDF byte count"
assert_eq "$(sha_file "$output_dir/ten-proofs-oai.pdf")" "$expected_pdf_sha256" "source PDF SHA-256"

# Toolchain and package identities after cache preparation.
lean_version_line="$(lean --version | head -n1)"
[[ "$lean_version_line" == *"version $expected_lean_version"* ]] || { echo "Lean version mismatch: $lean_version_line" >&2; exit 1; }
[[ "$lean_version_line" == *"$expected_lean_commit"* ]] || { echo "Lean commit mismatch: $lean_version_line" >&2; exit 1; }
assert_eq "$(git -C "$upstream/.lake/packages/mathlib" rev-parse HEAD)" "$expected_mathlib_commit" "mathlib commit"
assert_eq "$(git -C "$upstream/.lake/packages/Comparator" rev-parse HEAD)" "$expected_comparator_commit" "Comparator commit"
assert_eq "$(git -C "$upstream/.lake/packages/Lean4Checker" rev-parse HEAD)" "$expected_lean4checker_commit" "Lean4Checker commit"
assert_eq "$(git -C "$root/tools/lean4export" rev-parse HEAD)" "$expected_lean4export_commit" "lean4export commit"
assert_eq "$(git -C "$root/tools/nanoda" rev-parse HEAD)" "$expected_nanoda_commit" "Nanoda commit"
assert_eq "$(git -C "$root/tools/landrun" rev-parse HEAD)" "$expected_landrun_commit" "Landrun commit"
assert_eq "$(sha_file "${COMPARATOR_LANDRUN_REAL}")" "$expected_landrun_sha256" "Landrun binary SHA-256"
assert_eq "$(sha_file "${COMPARATOR_LEAN4EXPORT}")" "$expected_lean4export_sha256" "lean4export binary SHA-256"
assert_eq "$(sha_file "${COMPARATOR_NANODA}")" "$expected_nanoda_sha256" "Nanoda binary SHA-256"
assert_eq "$(sha_file "${COMPARATOR_LANDRUN}")" "$expected_adapter_sha256" "Landrun adapter SHA-256"

# Trust-boundary scans. Challenge placeholders are expected and separately counted.
scan="$output_dir/trust-boundary-scan.txt"
: > "$scan"
if grep -nE '\b(sorry|admit)\b|^[[:space:]]*(axiom|unsafe)[[:space:]]' "$upstream/$solution" >> "$scan"; then
  echo "prohibited solution placeholder/custom-axiom/unsafe declaration detected" >&2
  cat "$scan" >&2
  exit 1
fi
if grep -nE '^[[:space:]]*import[[:space:]]+All([[:space:]]|$)' "$upstream/$solution" "$upstream/$challenge" >> "$scan"; then
  echo "aggregate All import detected" >&2
  cat "$scan" >&2
  exit 1
fi
sorry_count="$(grep -cE '^[[:space:]]*sorry[[:space:]]*$' "$upstream/$challenge" || true)"
assert_eq "$sorry_count" "4" "challenge sorry boundary count"
echo "solution placeholder/custom-axiom/unsafe scan: clear" >> "$scan"
echo "aggregate All import scan: clear" >> "$scan"
echo "challenge sorry boundary count: 4 expected; challenge placeholders are not solution authority" >> "$scan"

# Exact authorized solution build.
start_utc="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
(
  cd "$upstream"
  lake build SpherePacking
) 2>&1 | tee "$output_dir/solution-build.log"

# Exact target existence and theorem-level axiom audit.
axiom_file="$upstream/MATHCERTSpherePackingReplayAxioms.lean"
{
  echo "import SpherePacking"
  for theorem in "${theorem_names[@]}"; do
    echo "#check $theorem"
    echo "#print axioms $theorem"
  done
} > "$axiom_file"
(
  cd "$upstream"
  lake env lean "$(basename "$axiom_file")"
) 2>&1 | tee "$output_dir/theorem-axioms.log"
rm -f "$axiom_file"

THEOREMS="$(printf '%s\n' "${theorem_names[@]}")" AXIOM_LOG="$output_dir/theorem-axioms.log" AXIOM_REPORT="$output_dir/theorem-axiom-report.json" python3 - <<'PY'
import json, os, re
from pathlib import Path
text=Path(os.environ['AXIOM_LOG']).read_text(encoding='utf-8')
allowed={'propext','Classical.choice','Quot.sound'}
reports=[]
for theorem in [x for x in os.environ['THEOREMS'].splitlines() if x]:
    m=re.search(r"'"+re.escape(theorem)+r"' depends on axioms:\s*\[(.*?)\]",text,re.S)
    if not m:
        raise SystemExit(f'missing theorem axiom report: {theorem}')
    axioms={x.strip() for x in m.group(1).replace('\n',' ').split(',') if x.strip()}
    unexpected=sorted(axioms-allowed)
    if unexpected:
        raise SystemExit(f'unexpected axioms for {theorem}: {unexpected}')
    reports.append({'theorem':theorem,'axioms':sorted(axioms),'unexpected':[]})
Path(os.environ['AXIOM_REPORT']).write_text(json.dumps({'permitted':sorted(allowed),'reports':reports},indent=2)+'\n')
PY

CONFIG_PATH="$upstream/$config" TARGET_REPORT="$output_dir/target-export-report.json" python3 - <<'PY'
import json, os
from pathlib import Path
cfg=json.loads(Path(os.environ['CONFIG_PATH']).read_text())
expected=[
 'PackingBounds.FullMain.exact_limit',
 'PackingBounds.FullMain.exact_binary_exponent',
 'PackingBounds.PackingBridge.sphere_packing_sharp_asymptotic_upper',
 'PackingBounds.sharpFullCohnElkiesManuscriptConclusions',
]
assert cfg['theorem_names']==expected
Path(os.environ['TARGET_REPORT']).write_text(json.dumps({'count':4,'ordered_targets':expected,'config_exact_match':True,'lean_check_all_targets':True},indent=2)+'\n')
PY

# Exact authorized Comparator invocation. Comparator performs export plus Nanoda and Lean default-kernel checks.
(
  cd "$upstream"
  lake exe comparator "$config"
) 2>&1 | tee "$output_dir/comparator.log"
grep -Fq "Nanoda kernel accepts the solution" "$output_dir/comparator.log"
grep -Fq "Lean default kernel accepts the solution" "$output_dir/comparator.log"
grep -Fq "Your solution is okay!" "$output_dir/comparator.log"
end_utc="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

cat > "$output_dir/comparator-result.json" <<'JSON'
{
  "comparator": "accept",
  "lean_default_kernel": "accept",
  "nanoda": "accept",
  "otp_successor_comparator": "ACCEPT"
}
JSON

# Protected semantic/nonvacuity binding attestations; no new source classification is invented here.
python3 - "$output_dir/semantic-concordance-attestation.json" <<'PY'
import json,sys
out=sys.argv[1]
obj={
 'state':'bound_to_protected_forge_semantic_authority',
 'composite_blob':'b2e309ad96e750651fc7149a6bad54c6bf99015b',
 'bridge_blob':'7858b156fc4490ecc6e3572dcf449d84dcc99f93',
 'classifications':[
  'direct_source_theorem_projection_modulo_proved_full_radial_equivalence',
  'derived_base_two_logarithmic_consequence',
  'source_faithful_displayed_consequence_with_proved_scale_normalization',
  'source_faithful_derived_composite_certificate'],
 'mandatory_qualifications':[
  'The ten-field composite is not a single verbatim manuscript theorem.',
  'The 30-decimal base-two exponent enclosure is a formal numerical consequence of the exact alpha_* expression, not manuscript-authored precision.',
  'The packing bridge relies on proved positive rescaling invariance and unit-separation supremum equivalence; declaration-name similarity is not used as authority.',
  'The explicit little-o witness is a normal form of the source asymptotic and is not a stronger rate claim.',
  'No whole-chapter semantic equivalence or independent proof certification is transferred by this packet.'],
 'independent_source_reclassification_performed':False,
 'whole_chapter_equivalence':False,
 'full_proof_body_equivalence':False}
open(out,'w').write(json.dumps(obj,indent=2)+'\n')
PY

python3 - "$output_dir/nonvacuity-attestation.json" <<'PY'
import json,sys
obj={
 'state':'clear_bound_to_protected_current_root_evidence',
 'evidence':[
  'CohnElkies.admissible_nonempty',
  'fullQuotientSet_eq_radial',
  'SpherePacking singleton unit-separated packing witness',
  'SpherePacking.upper_packing_density_le_one',
  'positive-dimensional bridge quantification'],
 'authority':'protected work-package plus protected Forge composite/bridge semantic records',
 'new_nonvacuity_claim_added':False}
open(sys.argv[1],'w').write(json.dumps(obj,indent=2)+'\n')
PY

# Environment/source identity manifests.
{
  echo "family=$family"
  echo "tracker=$tracker"
  echo "mathcert_head_sha=${MATHCERT_HEAD_SHA:-unknown}"
  echo "workflow_checkout_sha=${MATHCERT_WORKFLOW_SHA:-${GITHUB_SHA:-unknown}}"
  echo "runner_image=${ImageOS:-unknown}-${ImageVersion:-unknown}"
  echo "uname=$(uname -a)"
  echo "lean=$lean_version_line"
  echo "lake=$(lake --version | head -n1)"
  echo "upstream_commit=$expected_upstream_commit"
  echo "upstream_tree=$expected_upstream_tree"
  echo "mathlib_commit=$expected_mathlib_commit"
  echo "comparator_commit=$expected_comparator_commit"
  echo "lean4checker_commit=$expected_lean4checker_commit"
  echo "lean4export_commit=$expected_lean4export_commit"
  echo "nanoda_commit=$expected_nanoda_commit"
  echo "landrun_commit=$expected_landrun_commit"
  echo "landrun_binary_sha256=$expected_landrun_sha256"
  echo "lean4export_binary_sha256=$expected_lean4export_sha256"
  echo "nanoda_binary_sha256=$expected_nanoda_sha256"
  echo "landrun_adapter_sha256=$expected_adapter_sha256"
  echo "start_utc=$start_utc"
  echo "end_utc=$end_utc"
} > "$output_dir/environment-manifest.txt"

{
  echo "source_pdf_url=$pdf_url"
  echo "source_pdf_revision=2026-08-06"
  echo "source_pdf_bytes=$expected_pdf_bytes"
  echo "source_pdf_sha256=$expected_pdf_sha256"
  echo "upstream_commit=$expected_upstream_commit"
  echo "upstream_tree=$expected_upstream_tree"
  echo "config_blob=$expected_config_blob"
  echo "challenge_blob=$expected_challenge_blob"
  echo "solution_blob=$expected_solution_blob"
  echo "lake_manifest_blob=$expected_lake_manifest_blob"
  echo "lean_toolchain_blob=$expected_lean_toolchain_blob"
  echo "work_package_merge=$expected_work_package_merge"
  echo "work_package_blob=$expected_work_package_blob"
  echo "routes_blob=$expected_routes_blob"
  echo "forge_composite_commit=$expected_forge_composite_commit"
  echo "forge_composite_blob=$expected_composite_blob"
  echo "forge_bridge_commit=$expected_forge_bridge_commit"
  echo "forge_bridge_blob=$expected_bridge_blob"
  echo "solve_commit=$expected_solve_commit"
  echo "solve_packet_blob=$expected_packet_blob"
} > "$output_dir/source-identity-report.txt"

python3 - "$output_dir/evidence-summary.json" <<PY
import json,sys
obj={
 'schema_version':'1.0.0',
 'evidence_id':'MC-OTP-A-SPHERE-PACKING-REPLAY-EVIDENCE-001',
 'result_family':'OTP-A-SPHERE-PACKING',
 'tracker_issue':'$tracker',
 'mathcert_head':'${MATHCERT_HEAD_SHA:-unknown}',
 'work_package_merge':'$expected_work_package_merge',
 'work_package_blob':'$expected_work_package_blob',
 'source_root':'$expected_upstream_commit',
 'source_tree':'$expected_upstream_tree',
 'target_count':4,
 'solution_build':'pass',
 'challenge_sorry_boundary_count':4,
 'challenge_sorry_is_solution_authority':False,
 'theorem_axioms':'permitted_only',
 'comparator':'accept',
 'lean_default_kernel':'accept',
 'nanoda':'accept',
 'trust_boundary_scan':'clear',
 'source_pdf_identity':'exact_2026_08_06_bytes_reacquired',
 'semantic_concordance':'bound_to_protected_forge_composite_and_bridge_records',
 'nonvacuity':'bound_to_protected_current_root_evidence',
 'route_proposed':False,
 'route_registered':False,
 'may_adjudicate':False,
 'cert_output':None,
 'mathematical_target_proved':False,
 'aggregate_authority':False,
 'may_promote_claim':False,
 'disposition':'A_EXACT_REPLAY_EVIDENCE_COMPLETE_READY_FOR_SEPARATE_ROUTE_PROPOSAL'}
open(sys.argv[1],'w').write(json.dumps(obj,indent=2)+'\n')
PY

# Exclude the reacquired PDF from the retained bundle: its exact hash/size are recorded, while
# repository evidence retains the replay/control receipts. Build deterministic tar.gz bytes.
rm -f "$output_dir/ten-proofs-oai.pdf"
(
  cd "$output_dir"
  sha256sum environment-manifest.txt source-identity-report.txt solution-build.log theorem-axioms.log theorem-axiom-report.json target-export-report.json comparator.log comparator-result.json semantic-concordance-attestation.json nonvacuity-attestation.json trust-boundary-scan.txt evidence-summary.json | LC_ALL=C sort > SHA256SUMS
)
parent="$(dirname "$output_dir")"
base="$(basename "$output_dir")"
tar --sort=name --mtime='UTC 1970-01-01' --owner=0 --group=0 --numeric-owner \
  --exclude='bundle.tar.gz' -C "$parent" -cf - "$base" | gzip -n > "$output_dir/bundle.tar.gz"
sha256sum "$output_dir/bundle.tar.gz" > "$output_dir/bundle.sha256"

echo "OTP_SUCCESSOR_COMPARATOR=ACCEPT"
echo "A_EXACT_REPLAY_EVIDENCE_COMPLETE_READY_FOR_SEPARATE_ROUTE_PROPOSAL"
