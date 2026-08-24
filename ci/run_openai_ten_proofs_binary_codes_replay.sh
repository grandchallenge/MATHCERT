#!/usr/bin/env bash
set -Eeuo pipefail
if (($#!=1)); then echo "usage: $0 OUTPUT_DIR" >&2; exit 64; fi
out="$1"; root="$(cd "$(dirname "$0")/.." && pwd)"; upstream="$root/upstream"; forge="$root/forge"; solve="$root/solve"; mkdir -p "$out"; out="$(cd "$out" && pwd)"
wp="governance/result_family_work_package_successors/OTP-B1-BINARY-CODES-CERT-WP-001.json"; wp_merge="83a8951a89a72a892d5fdc132d6a22e508d6cdc2"; wp_blob="19e1eaf5e24ce212bb020c8c40d4177ff5b4f8f9"
up_commit="94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6"; up_tree="174289e4d4958cb0509874e6e53400e098213de7"; config="ComparatorChallenges/B_BinaryCodes.json"; config_blob="b530b77972c83396c1f2aed2deccda3a12fb6cab"; challenge="ComparatorChallenges/B_BinaryCodes.lean"; challenge_blob="c9e93b1944e6806802068cf593fa6557e4267bb1"; solution="MetricCodes.lean"; solution_blob="51628c0db81bd6cb9a79777fa601306c9d64cbc5"
forge_commit="24a1fa0f020ee9cc7fbe2e7aea4cd840268ca748"; forge_path="sources/OPENAI-TEN-PROOFS-001/semantic/OTP-B1-BINARY-CODES/audit_record.json"; forge_blob="0ab4d973bc046084e9d2dc6c7552ab5428d7412d"; solve_commit="7858f1350439e6324bdee149931bdb7661098729"; packet="work_packages/OPENAI_TEN_PROOFS_WP00/result_family_handoff_successors/OTP-B1-BINARY-CODES.json"; packet_blob="1847dd7a17cda51cb02f017766c59d372811fb12"
pdf_sha="ebc561ab5c53dbd240e17a8fdb6fffeb648591eca85dbfc7466f563638f8c566"; pdf_bytes="2487031"
targets=(MetricCodes.Hamming.binaryRate_lt_classicalRate MetricCodes.Hamming.exists_binaryRate_improvement MetricCodes.Johnson.binaryRate_le_combinedVariationalRate MetricCodes.MRRW.strict_mrrw2 MetricCodes.Johnson.binaryRate_lt_mrrw MetricCodes.Johnson.exists_binaryRate_mrrw_improvement)
assert_eq(){ [[ "$1" == "$2" ]] || { echo "$3 mismatch: expected $2 found $1" >&2; exit 1; }; }; blob(){ git -C "$1" rev-parse "HEAD:$2"; }
assert_eq "$(git -C "$root" rev-parse "$wp_merge:$wp")" "$wp_blob" "work package historical blob"; assert_eq "$(git -C "$root" rev-parse "HEAD:$wp")" "$wp_blob" "work package current blob"
assert_eq "$(git -C "$upstream" rev-parse HEAD)" "$up_commit" "upstream commit"; assert_eq "$(git -C "$upstream" rev-parse 'HEAD^{tree}')" "$up_tree" "upstream tree"; assert_eq "$(blob "$upstream" "$config")" "$config_blob" "config blob"; assert_eq "$(blob "$upstream" "$challenge")" "$challenge_blob" "challenge blob"; assert_eq "$(blob "$upstream" "$solution")" "$solution_blob" "solution blob"
assert_eq "$(git -C "$forge" rev-parse HEAD)" "$forge_commit" "Forge commit"; assert_eq "$(blob "$forge" "$forge_path")" "$forge_blob" "Forge audit blob"; assert_eq "$(git -C "$solve" rev-parse HEAD)" "$solve_commit" "Solve commit"; assert_eq "$(blob "$solve" "$packet")" "$packet_blob" "Solve packet blob"
WP="$root/$wp" CFG="$upstream/$config" ROUTES="$root/governance/certification_routes.json" python3 - <<'PY'
import json,os
wp=json.load(open(os.environ['WP'])); cfg=json.load(open(os.environ['CFG'])); routes=json.load(open(os.environ['ROUTES']))
t=['MetricCodes.Hamming.binaryRate_lt_classicalRate','MetricCodes.Hamming.exists_binaryRate_improvement','MetricCodes.Johnson.binaryRate_le_combinedVariationalRate','MetricCodes.MRRW.strict_mrrw2','MetricCodes.Johnson.binaryRate_lt_mrrw','MetricCodes.Johnson.exists_binaryRate_mrrw_improvement']
assert wp['target_scope']['lean_theorems']==t; assert wp['execution_contract']['deterministic_commands']==['lake exe cache get','lake build MetricCodes','lake exe comparator ComparatorChallenges/B_BinaryCodes.json']; assert wp['execution_contract']['permitted_axioms']==['propext','Quot.sound','Classical.choice']; assert wp['execution_contract']['challenge_sorry_warning_count']==6; assert cfg['theorem_names']==t and cfg['permitted_axioms']==['propext','Quot.sound','Classical.choice'] and cfg['enable_nanoda'] is True
assert not any(r.get('campaign_id')=='OTP-B1-BINARY-CODES' for r in routes['routes'])
assert any('derived certificate normal forms' in q for q in wp['target_scope']['mandatory_qualifications']); assert wp['target_scope']['nonvacuity']['state']
PY
curl --fail --location --silent --show-error --retry 3 https://cdn.openai.com/pdf/ten-proofs-oai.pdf -o "$out/source.pdf"; assert_eq "$(stat -c '%s' "$out/source.pdf")" "$pdf_bytes" "source bytes"; assert_eq "$(sha256sum "$out/source.pdf"|cut -d' ' -f1)" "$pdf_sha" "source sha"; rm "$out/source.pdf"
if grep -nE '\b(sorry|admit)\b|^[[:space:]]*(axiom|unsafe)[[:space:]]' "$upstream/$solution" > "$out/trust-boundary-scan.txt"; then echo "solution trust-boundary violation" >&2; exit 1; fi; echo 'solution placeholder/custom-axiom/unsafe scan: clear' > "$out/trust-boundary-scan.txt"
(cd "$upstream" && lake build MetricCodes) 2>&1 | tee "$out/solution-build.log"
ax="$upstream/MATHCERTB1ReplayAxioms.lean"; { echo 'import MetricCodes'; for x in "${targets[@]}"; do echo "#check $x"; echo "#print axioms $x"; done; } > "$ax"; (cd "$upstream" && lake env lean "$(basename "$ax")") 2>&1 | tee "$out/theorem-axioms.log"; rm "$ax"
THEOREMS="$(printf '%s\n' "${targets[@]}")" LOG="$out/theorem-axioms.log" REPORT="$out/theorem-axiom-report.json" python3 - <<'PY'
import json,os,re
s=open(os.environ['LOG']).read(); allowed={'propext','Quot.sound','Classical.choice'}; rs=[]
for t in os.environ['THEOREMS'].splitlines():
 m=re.search(r"'"+re.escape(t)+r"' depends on axioms:\s*\[(.*?)\]",s,re.S); assert m,t; a={x.strip() for x in m.group(1).replace('\n',' ').split(',') if x.strip()}; assert not(a-allowed),(t,a-allowed); rs.append({'theorem':t,'axioms':sorted(a)})
json.dump({'permitted':sorted(allowed),'reports':rs},open(os.environ['REPORT'],'w'),indent=2)
PY
(cd "$upstream" && lake exe comparator "$config") 2>&1 | tee "$out/comparator.log"; grep -Fq 'Nanoda kernel accepts the solution' "$out/comparator.log"; grep -Fq 'Lean default kernel accepts the solution' "$out/comparator.log"; grep -Fq 'Your solution is okay!' "$out/comparator.log"
TARGETS="$(printf '%s\n' "${targets[@]}")" OUT="$out/evidence-summary.json" HEAD="${MATHCERT_HEAD_SHA:-unknown}" python3 - <<'PY'
import json,os
obj={'schema_version':'1.0.0','evidence_id':'MC-OTP-B1-BINARY-CODES-REPLAY-EVIDENCE-001','result_family':'OTP-B1-BINARY-CODES','mathcert_head':os.environ['HEAD'],'target_count':6,'targets':os.environ['TARGETS'].splitlines(),'source_pdf_identity':'exact_2026_08_06_bytes_reacquired','solution_build':'pass','theorem_axioms':'permitted_only','comparator':'accept','lean_default_kernel':'accept','nanoda':'accept','trust_boundary_scan':'clear','semantic_concordance':'bound_to_protected_forge_record_with_derived_normal_form_and_minimizer_attainment_boundaries','nonvacuity':'bound_to_protected_current_root_evidence','route_proposed':False,'route_registered':False,'may_adjudicate':False,'adjudication':None,'cert_output':None,'mathematical_target_proved':False,'aggregate_authority':False,'may_promote_claim':False,'disposition':'B1_EXACT_REPLAY_EVIDENCE_COMPLETE_READY_FOR_SEPARATE_ROUTE_PROPOSAL'}; json.dump(obj,open(os.environ['OUT'],'w'),indent=2)
PY
cat > "$out/source-identity-report.txt" <<EOF
source_pdf_bytes=$pdf_bytes
source_pdf_sha256=$pdf_sha
formal_root=$up_commit
formal_tree=$up_tree
config_blob=$config_blob
challenge_blob=$challenge_blob
solution_blob=$solution_blob
work_package_merge=$wp_merge
work_package_blob=$wp_blob
forge_commit=$forge_commit
forge_blob=$forge_blob
solve_commit=$solve_commit
solve_packet_blob=$packet_blob
EOF
(cd "$out" && sha256sum solution-build.log theorem-axioms.log theorem-axiom-report.json comparator.log trust-boundary-scan.txt evidence-summary.json source-identity-report.txt | LC_ALL=C sort > SHA256SUMS)
tar --sort=name --mtime='UTC 1970-01-01' --owner=0 --group=0 --numeric-owner -C "$out" -cf - SHA256SUMS solution-build.log theorem-axioms.log theorem-axiom-report.json comparator.log trust-boundary-scan.txt evidence-summary.json source-identity-report.txt | gzip -n > "$out/bundle.tar.gz"; sha256sum "$out/bundle.tar.gz" | tee "$out/bundle.sha256"; echo B1_EXACT_REPLAY_EVIDENCE_COMPLETE_READY_FOR_SEPARATE_ROUTE_PROPOSAL
