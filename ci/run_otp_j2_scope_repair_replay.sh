#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
upstream="$root/upstream-j2"
out="${1:-$root/evidence/j2-scope-repair-runtime}"
mkdir -p "$out"
out="$(cd "$out" && pwd)"

expected_commit="94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6"
expected_tree="174289e4d4958cb0509874e6e53400e098213de7"
expected_manifest_blob="046e8de7f46832fbf092e3fb815efae01e4a2129"
expected_config_blob="d8a542b5ce620b686cb24a6756360e76c5d2b1c1"
expected_challenge_blob="dd22ce141dd0a860ecdccfda291c0f3a480a1d70"
expected_solution_blob="0e973d50014e8c800af597ef699ef29b81e42fc6"
expected_projection_blob="ac1ec20e95d6acbcd1c3a111afe28bca92a43377"
expected_source_sha="ebc561ab5c53dbd240e17a8fdb6fffeb648591eca85dbfc7466f563638f8c566"
expected_source_bytes="2487031"

fail() { echo "$*" >&2; exit 1; }
assert_eq() { [[ "$1" == "$2" ]] || fail "$3 mismatch: expected $2, got $1"; }
blob() { git -C "$upstream" rev-parse "HEAD:$1"; }
local_git_blob() {
  python3 - "$1" <<'PY'
import hashlib, sys
from pathlib import Path
p = Path(sys.argv[1])
data = p.read_bytes()
print(hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest())
PY
}

[[ -d "$upstream/.git" ]] || fail "missing exact upstream checkout at $upstream"
assert_eq "$(git -C "$upstream" rev-parse HEAD)" "$expected_commit" "upstream commit"
assert_eq "$(git -C "$upstream" rev-parse 'HEAD^{tree}')" "$expected_tree" "upstream tree"
assert_eq "$(blob lake-manifest.json)" "$expected_manifest_blob" "lake manifest blob"
assert_eq "$(blob ComparatorChallenges/J_TwoDegenerateGraphs.json)" "$expected_config_blob" "Comparator config blob"
assert_eq "$(blob ComparatorChallenges/J_TwoDegenerateGraphs.lean)" "$expected_challenge_blob" "challenge blob"
assert_eq "$(blob CompactnessAndDegeneracy.lean)" "$expected_solution_blob" "solution blob"
assert_eq "$(local_git_blob "$root/evidence/openai_ten_proofs/two_degenerate_scope_repair/SourceFaithfulProjection.lean")" "$expected_projection_blob" "MATHCERT projection blob"
lean --version | grep -Fq "version 4.32.0" || fail "Lean 4.32.0 required"

curl --fail --location --retry 3 --silent --show-error \
  https://cdn.openai.com/pdf/ten-proofs-oai.pdf -o "$out/ten-proofs-oai.pdf"
assert_eq "$(sha256sum "$out/ten-proofs-oai.pdf" | cut -d' ' -f1)" "$expected_source_sha" "current manuscript SHA-256"
assert_eq "$(stat -c '%s' "$out/ten-proofs-oai.pdf")" "$expected_source_bytes" "current manuscript byte count"

solution="$upstream/CompactnessAndDegeneracy.lean"
challenge="$upstream/ComparatorChallenges/J_TwoDegenerateGraphs.lean"
scan="$out/trust-scan.txt"
: > "$scan"
if grep -nE '\b(sorry|admit)\b|^[[:space:]]*(axiom|opaque|unsafe)[[:space:]]' "$solution" >> "$scan"; then
  fail "solution placeholder/unsafe/custom-axiom scan failed"
fi
if grep -nE '^[[:space:]]*import[[:space:]]+All([[:space:]]|$)' "$solution" "$challenge" >> "$scan"; then
  fail "aggregate All import detected"
fi
echo "solution placeholder/unsafe/custom-axiom scan: clear" >> "$scan"
echo "aggregate All import scan: clear" >> "$scan"

cp "$root/evidence/openai_ten_proofs/two_degenerate_scope_repair/SourceFaithfulProjection.lean" \
  "$upstream/MATHCERTJ2SourceFaithfulProjection.lean"

cd "$upstream"
lake build CompactnessAndDegeneracy 2>&1 | tee "$out/solution-build.log"
lake build ComparatorChallenges.J_TwoDegenerateGraphs 2>&1 | tee "$out/challenge-build.log"
lake env lean MATHCERTJ2SourceFaithfulProjection.lean 2>&1 | tee "$out/projection-build.log"

{
  cat MATHCERTJ2SourceFaithfulProjection.lean
  cat <<'EOF'

#print axioms TwoDegenerateGraphs.twoDegenerateExtremalCounterexample
#print axioms TwoDegenerateGraphs.not_erdos_146
#print axioms TwoDegenerateGraphs.mathcert_sourceFaithfulTwoDegenerateExtremalCounterexample
#print axioms TwoDegenerateGraphs.mathcert_sourceFaithfulNotErdos146
EOF
} > MATHCERTJ2ProjectionAndAxioms.lean
lake env lean MATHCERTJ2ProjectionAndAxioms.lean 2>&1 | tee "$out/theorem-axioms.log"
rm -f MATHCERTJ2ProjectionAndAxioms.lean

lake exe comparator ComparatorChallenges/J_TwoDegenerateGraphs.json 2>&1 | tee "$out/comparator.log"
grep -Fq "Lean default kernel accepts the solution" "$out/comparator.log"
grep -Fq "Nanoda kernel accepts the solution" "$out/comparator.log"
grep -Fq "Your solution is okay!" "$out/comparator.log"

python3 - "$out/theorem-axioms.log" <<'PY'
import re, sys
from pathlib import Path
text = Path(sys.argv[1]).read_text(encoding="utf-8")
allowed = {"propext", "Classical.choice", "Quot.sound"}
for theorem in (
    "TwoDegenerateGraphs.twoDegenerateExtremalCounterexample",
    "TwoDegenerateGraphs.not_erdos_146",
    "TwoDegenerateGraphs.mathcert_sourceFaithfulTwoDegenerateExtremalCounterexample",
    "TwoDegenerateGraphs.mathcert_sourceFaithfulNotErdos146",
):
    m = re.search(r"'" + re.escape(theorem) + r"' depends on axioms:\s*\[(.*?)\]", text, re.S)
    if not m:
        raise SystemExit(f"missing axiom report for {theorem}")
    axioms = {x.strip() for x in m.group(1).replace("\n", " ").split(",") if x.strip()}
    extra = axioms - allowed
    if extra:
        raise SystemExit(f"unexpected axioms for {theorem}: {sorted(extra)}")
PY

cat > "$out/replay-summary.json" <<EOF
{
  "schema_version": "1.0.0",
  "operation_id": "OTP-J2-TWO-DEGENERATE-SCOPE-REPAIR-001",
  "result_family": "OTP-J2-TWO-DEGENERATE",
  "upstream_commit": "$expected_commit",
  "upstream_tree": "$expected_tree",
  "lake_manifest_git_blob_sha1": "$expected_manifest_blob",
  "projection_git_blob_sha1": "$expected_projection_blob",
  "current_manuscript_sha256": "$expected_source_sha",
  "current_manuscript_bytes": $expected_source_bytes,
  "registered_target_comparator": "pass_derivation_carrier_only",
  "lean_kernel": "accept",
  "nanoda_registered_targets": "accept",
  "source_faithful_projection": "accept",
  "dependency_separation": "accept",
  "source_attribution_of_coloring_conjunct": false,
  "route_state_effect": "none",
  "adjudication_effect": "none",
  "cert_output_effect": "none"
}
EOF
rm -f "$out/ten-proofs-oai.pdf"
find "$out" -maxdepth 1 -type f ! -name 'SHA256SUMS' -print0 | sort -z | xargs -0 sha256sum > "$out/SHA256SUMS"
echo "J2 Path A source-faithful replay complete; no route/adjudication/output effect"
