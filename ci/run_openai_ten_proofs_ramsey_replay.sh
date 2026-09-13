#!/usr/bin/env bash
set -Eeuo pipefail
if (($#!=1)); then echo "usage: $0 OUTPUT_DIR" >&2; exit 64; fi
out="$1"; root="$(cd "$(dirname "$0")/.." && pwd)"; upstream="$root/upstream"; forge="$root/forge"; solve="$root/solve"; mkdir -p "$out"; out="$(cd "$out" && pwd)"
wp="governance/result_family_work_package_successors/OTP-I-RAMSEY-CERT-WP-001.json"; wp_commit="18578b7f6917fec0bca4f9b5ea17fbb9541794e6"; wp_blob="2925af4dc5db8b5cb751cf986803048f849a9a8b"
up_commit="94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6"; up_tree="174289e4d4958cb0509874e6e53400e098213de7"; config="ComparatorChallenges/I_MulticolorTriangleRamsey.json"; config_blob="ce67db0653e18a2de68f471c00b9f892b789f806"; challenge="ComparatorChallenges/I_MulticolorTriangleRamsey.lean"; challenge_blob="6a9e42d686720f4b74ddc2001006b0b7a20f11aa"; solution="MulticolorTriangleRamsey.lean"; solution_blob="24b55f531a4d36347cd2277b1b9c7d784d91ae35"
forge_commit="dbf3b099331a1807c4d3036e7a6a406711ea7cf3"; forge_path="sources/OPENAI-TEN-PROOFS-001/semantic/OTP-I-RAMSEY/audit_record.json"; forge_blob="a7c014fb623b66355ef5d6260e5b994d99d67a6d"; solve_commit="a5b9488a4095a6669c9c242d59225c5735100123"; packet="work_packages/OPENAI_TEN_PROOFS_WP00/result_family_handoff_successors/OTP-I-RAMSEY.json"; packet_blob="14e0909cd5e704d3a9b6b35c218fae6a44ae2013"
pdf_sha="ebc561ab5c53dbd240e17a8fdb6fffeb648591eca85dbfc7466f563638f8c566"; pdf_bytes="2487031"
targets=(ErdosProblems.MulticolourTriangleRamsey.erdos_183 ErdosProblems.MulticolourTriangleRamsey.erdos_problem_183_explicit ErdosProblems.MulticolourTriangleRamsey.triangleRamseyNumber_log_sharp_coefficients ErdosProblems.MulticolourTriangleRamsey.triangleRamseyNumber_log_isTheta)
assert_eq(){ [[ "$1" == "$2" ]] || { echo "$3 mismatch: expected $2 found $1" >&2; exit 1; }; }; blob(){ git -C "$1" rev-parse "HEAD:$2"; }
assert_eq "$(git -C "$root" rev-parse "$wp_commit:$wp")" "$wp_blob" "work package historical blob"; assert_eq "$(git -C "$root" rev-parse "HEAD:$wp")" "$wp_blob" "work package current blob"
assert_eq "$(git -C "$upstream" rev-parse HEAD)" "$up_commit" "upstream commit"; assert_eq "$(git -C "$upstream" rev-parse 'HEAD^{tree}')" "$up_tree" "upstream tree"; assert_eq "$(blob "$upstream" "$config")" "$config_blob" "config blob"; assert_eq "$(blob "$upstream" "$challenge")" "$challenge_blob" "challenge blob"; assert_eq "$(blob "$upstream" "$solution")" "$solution_blob" "solution blob"
assert_eq "$(git -C "$forge" rev-parse HEAD)" "$forge_commit" "Forge commit"; assert_eq "$(blob "$forge" "$forge_path")" "$forge_blob" "Forge audit blob"; assert_eq "$(git -C "$solve" rev-parse HEAD)" "$solve_commit" "Solve commit"; assert_eq "$(blob "$solve" "$packet")" "$packet_blob" "Solve packet blob"
WP="$root/$wp" CFG="$upstream/$config" ROUTES="$root/governance/certification_routes.json" python3 - <<'PY'
import json,os
wp=json.load(open(os.environ['WP'])); cfg=json.load(open(os.environ['CFG'])); routes=json.load(open(os.environ['ROUTES']))
t=['ErdosProblems.MulticolourTriangleRamsey.erdos_183','ErdosProblems.MulticolourTriangleRamsey.erdos_problem_183_explicit','ErdosProblems.MulticolourTriangleRamsey.triangleRamseyNumber_log_sharp_coefficients','ErdosProblems.MulticolourTriangleRamsey.triangleRamseyNumber_log_isTheta']
assert wp['target_scope']['lean_theorems']==t; assert cfg['theorem_names']==t; assert cfg['permitted_axioms']==['propext','Quot.sound','Classical.choice']; assert cfg['enable_nanoda'] is True
r=next(x for x in routes['routes'] if x.get('campaign_id')=='OTP-I-RAMSEY'); assert r['intake_status']=='qualified' and r['target_claim_ids']==t
qs=wp['target_scope']['mandatory_qualifications']; assert any('1/(6*exp 38)' in q for q in qs); assert any('Filter-Theta' in q for q in qs); assert any('sInf' in q for q in qs)
PY
curl --fail --location --silent --show-error --retry 3 https://cdn.openai.com/pdf/ten-proofs-oai.pdf -o "$out/source.pdf"; assert_eq "$(stat -c '%s' "$out/source.pdf")" "$pdf_bytes" "source bytes"; assert_eq "$(sha256sum "$out/source.pdf"|cut -d' ' -f1)" "$pdf_sha" "source sha"; rm "$out/source.pdf"
if grep -nE '\b(sorry|admit)\b|^[[:space:]]*(axiom|unsafe)[[:space:]]' "$upstream/$solution" > "$out/trust-boundary-scan.txt"; then echo "solution trust-boundary violation" >&2; exit 1; fi; echo 'solution placeholder/custom-axiom/unsafe scan: clear' > "$out/trust-boundary-scan.txt"
(cd "$upstream" && lake build MulticolorTriangleRamsey) 2>&1 | tee "$out/solution-build.log"
ax="$upstream/MATHCERTIReplayAxioms.lean"; { echo 'import MulticolorTriangleRamsey'; for x in "${targets[@]}"; do echo "#check $x"; echo "#print axioms $x"; done; } > "$ax"; (cd "$upstream" && lake env lean "$(basename "$ax")") 2>&1 | tee "$out/theorem-axioms.log"; rm "$ax"
THEOREMS="$(printf '%s\n' "${targets[@]}")" LOG="$out/theorem-axioms.log" REPORT="$out/theorem-axiom-report.json" python3 - <<'PY'
import json,os,re
s=open(os.environ['LOG']).read(); allowed={'propext','Classical.choice','Quot.sound'}; rs=[]
for t in os.environ['THEOREMS'].splitlines():
 m=re.search(r"'"+re.escape(t)+r"' depends on axioms:\s*\[(.*?)\]",s,re.S); assert m,t; a={x.strip() for x in m.group(1).replace('\n',' ').split(',') if x.strip()}; assert not(a-allowed),(t,a-allowed); rs.append({'theorem':t,'axioms':sorted(a)})
json.dump({'permitted':sorted(allowed),'reports':rs},open(os.environ['REPORT'],'w'),indent=2)
PY
(cd "$upstream" && lake exe comparator "$config") 2>&1 | tee "$out/comparator.log"; grep -Fq 'Nanoda kernel accepts the solution' "$out/comparator.log"; grep -Fq 'Lean default kernel accepts the solution' "$out/comparator.log"; grep -Fq 'Your solution is okay!' "$out/comparator.log"
TARGETS="$(printf '%s\n' "${targets[@]}")" OUT="$out/evidence-summary.json" HEAD="${MATHCERT_HEAD_SHA:-unknown}" python3 - <<'PY'
import json,os
json.dump({'schema_version':'1.0.0','evidence_id':'MC-OTP-I-RAMSEY-EXACT-HEAD-REPLAY-001','result_family':'OTP-I-RAMSEY','mathcert_head':os.environ['HEAD'],'target_count':4,'targets':os.environ['TARGETS'].splitlines(),'source_pdf_identity':'exact_2026_08_06_bytes_reacquired','solution_build':'pass','theorem_axioms':'permitted_only','comparator':'accept','lean_default_kernel':'accept','nanoda':'accept','trust_boundary_scan':'clear','mathematical_target_proved':False,'aggregate_authority':False},open(os.environ['OUT'],'w'),indent=2)
PY
(cd "$out" && sha256sum solution-build.log theorem-axioms.log theorem-axiom-report.json comparator.log trust-boundary-scan.txt evidence-summary.json | LC_ALL=C sort > SHA256SUMS)
tar --sort=name --mtime='UTC 1970-01-01' --owner=0 --group=0 --numeric-owner -C "$out" -cf - SHA256SUMS solution-build.log theorem-axioms.log theorem-axiom-report.json comparator.log trust-boundary-scan.txt evidence-summary.json | gzip -n > "$out/bundle.tar.gz"; sha256sum "$out/bundle.tar.gz" | tee "$out/bundle.sha256"; echo OTP_I_RAMSEY_EXACT_HEAD_REPLAY_ACCEPT
