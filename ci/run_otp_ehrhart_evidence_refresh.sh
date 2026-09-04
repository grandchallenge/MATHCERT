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
source_successor_merge="275f435eaf519ada3f0afa4bf8e77cfd0c8fcbb3"
source_successor_path="sources/OPENAI-TEN-PROOFS-001/pdf_source_successors/OTP-SOURCE-PDF-SUCCESSOR-002.json"
source_successor_blob="02d1748abed36717afba46451330be165c076737"
source_successor_sha="ebc561ab5c53dbd240e17a8fdb6fffeb648591eca85dbfc7466f563638f8c566"
source_successor_bytes="2487031"
authorization_comment_id="5156109106"
admitted_manuscript_sha="f318c6508c9d49ef876a5a26cd73928705f96c07bb43e92a0cb35bd3f666ea53"
observed_manuscript_sha="64b900d5fae6fe22f2ae1b8e3b712d20055194a6c81cf343a2455e5898ac7dd6"
manuscript_url="https://cdn.openai.com/pdf/ten-proofs-oai.pdf"

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
assert_eq "$(git -C "$root/forge-source-successor" rev-parse HEAD)" "$source_successor_merge" "Forge source-successor protected merge"
assert_eq "$(git -C "$root/forge-source-successor" rev-parse "HEAD:$source_successor_path")" "$source_successor_blob" "Forge source-successor blob"

refresh_pdf="$output_dir/manuscript-refresh.pdf"
curl --fail --location --retry 3 --silent --show-error "$manuscript_url" -o "$refresh_pdf"
current_sha="$(sha256sum "$refresh_pdf" | cut -d' ' -f1)"
current_bytes="$(stat -c '%s' "$refresh_pdf")"

if [[ "$current_sha" == "$source_successor_sha" && "$current_bytes" == "$source_successor_bytes" ]]; then
  pdftotext -f 218 -l 221 -layout "$refresh_pdf" "$output_dir/source-locus-pages-218-221.txt"
  [[ -s "$output_dir/source-locus-pages-218-221.txt" ]] || { echo "source-locus extraction is empty" >&2; exit 1; }
  cat > "$output_dir/source-successor-readback.txt" <<EOF
state=HISTORICAL_EHRHART_REFRESH_SUPERSEDED_BY_PROTECTED_SOURCE_SUCCESSOR
source_url=$manuscript_url
source_sha256=$current_sha
source_bytes=$current_bytes
source_successor_repository=grandchallenge/MATHFORGE
source_successor_merge=$source_successor_merge
source_successor_path=$source_successor_path
source_successor_blob=$source_successor_blob
execution_candidate_created=false
certification_route_changed=false
adjudication_created=false
cert_output_created=false
mathematical_target_proved=false
EOF
  rm -f "$refresh_pdf"
  echo "HISTORICAL_EHRHART_REFRESH_SUPERSEDED_BY_PROTECTED_SOURCE_SUCCESSOR__NO_AUTHORITY_CHANGE"
  exit 0
fi

chmod +x "$root/ci/run_openai_ten_proofs_family_replay.sh"
"$root/ci/run_openai_ten_proofs_family_replay.sh" \
  OTP-F-EHRHART \
  ComparatorChallenges/F_EhrhartVolumeInequality.json \
  EhrhartVolumeInequality \
  ComparatorChallenges.F_EhrhartVolumeInequality \
  "$output_dir"

if [[ "$current_sha" == "$observed_manuscript_sha" ]]; then
  source_relation="byte_identical_to_forge_source_revision_audit_subject"
  source_authority="MF-OTP-SOURCE-REVISION-AUDIT-001"
elif [[ "$current_sha" == "$admitted_manuscript_sha" ]]; then
  source_relation="byte_identical_to_admitted_semantic_audit_subject"
  source_authority="MF-OTP-SEMANTIC-WP01-EHRHART"
else
  echo "source revision is not covered by the historical semantic/source-revision authorities or the protected source successor" >&2
  exit 1
fi

pdftotext -f 218 -l 221 -layout "$refresh_pdf" "$output_dir/source-locus-pages-218-221.txt"
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

python3 "$root/ci/build_otp_ehrhart_execution_candidate.py" "$output_dir"
rm -f "$refresh_pdf"

echo "prepared non-adjudicated OTP-F-EHRHART execution-candidate evidence at $output_dir"
