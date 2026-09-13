#!/usr/bin/env bash
set -Eeuo pipefail
if (($#!=1)); then echo "usage: $0 OUTPUT_DIR" >&2; exit 64; fi
out="$1"; root="$(cd "$(dirname "$0")/.." && pwd)"; upstream="$root/upstream"; forge="$root/forge"; solve="$root/solve"; mkdir -p "$out"; out="$(cd "$out" && pwd)"
wp="governance/result_family_work_package_successors/OTP-G-QUANTUM-PARALLEL-REPETITION-CERT-WP-001.json"; wp_commit="5bed0523102195bafe9dcd63103f960d47159f2b"; wp_blob="fcd9291b9286a07c977efdf48d71e75de4c90a1e"
up_commit="94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6"; up_tree="174289e4d4958cb0509874e6e53400e098213de7"; config="ComparatorChallenges/G_QuantumParallelRepetition.json"; config_blob="c7dd59e9df9ae5d90b35f76a9d958943d8e94770"; challenge="ComparatorChallenges/G_QuantumParallelRepetition.lean"; challenge_blob="8257e7726643a8f8c08c7e91584e003ab204c589"; solution="QuantumParallelRepetition.lean"; solution_blob="887c4378f124a5d81a3f2624b6dc34867ec409c4"
forge_commit="f0a40146cca7fd39c5724ed5be033ee9092625ac"; forge_path="sources/OPENAI-TEN-PROOFS-001/semantic/OTP-G-QUANTUM-PARALLEL-REPETITION/audit_record.json"; forge_blob="bfcbee0fd6174b8856b17c3d56ee320f27c18ec6"; solve_commit="4f384b510a557292ce999f02baacec45c534888a"; packet="work_packages/OPENAI_TEN_PROOFS_WP00/result_family_handoff_successors/OTP-G-QUANTUM-PARALLEL-REPETITION.json"; packet_blob="95f73528d78c24f09aba7c93ac0c601bb3ee515e"
pdf_sha="ebc561ab5c53dbd240e17a8fdb6fffeb648591eca85dbfc7466f563638f8c566"; pdf_bytes="2487031"
targets=(QuantumParallelRepetition.distributionUniformExponential QuantumParallelRepetition.standardQuantumParallelRepetition)
assert_eq(){ [[ "$1" == "$2" ]] || { echo "$3 mismatch: expected $2 found $1" >&2; exit 1; }; }; blob(){ git -C "$1" rev-parse "HEAD:$2"; }
assert_eq "$(git -C "$root" rev-parse "$wp_commit:$wp")" "$wp_blob" "work package historical blob"; assert_eq "$(git -C "$root" rev-parse "HEAD:$wp")" "$wp_blob" "work package current blob"
assert_eq "$(git -C "$upstream" rev-parse HEAD)" "$up_commit" "upstream commit"; assert_eq "$(git -C "$upstream" rev-parse 'HEAD^{tree}')" "$up_tree" "upstream tree"; assert_eq "$(blob "$upstream" "$config")" "$config_blob" "config blob"; assert_eq "$(blob "$upstream" "$challenge")" "$challenge_blob" "challenge blob"; assert_eq "$(blob "$upstream" "$solution")" "$solution_blob" "solution blob"
assert_eq "$(git -C "$forge" rev-parse HEAD)" "$forge_commit" "Forge commit"; assert_eq "$(blob "$forge" "$forge_path")" "$forge_blob" "Forge audit blob"; assert_eq "$(git -C "$solve" rev-parse HEAD)" "$solve_commit" "Solve commit"; assert_eq "$(blob "$solve" "$packet")" "$packet_blob" "Solve packet blob"
WP="$root/$wp" CFG="$upstream/$config" ROUTES="$root/governance/certification_routes.json" python3 - <<'PY'
import json,os
wp=json.load(open(os.environ['WP'])); cfg=json.load(open(os.environ['CFG'])); routes=json.load(open(os.environ['ROUTES']))
t=['QuantumParallelRepetition.distributionUniformExponential','QuantumParallelRepetition.standardQuantumParallelRepetition']
assert wp['target_scope']['lean_theorems']==t; assert cfg['theorem_names']==t; assert cfg['permitted_axioms']==['propext','Quot.sound','Classical.choice']; assert cfg['enable_nanoda'] is True
r=next(x for x in routes['routes'] if x.get('campaign_id')=='OTP-G-QUANTUM-PARALLEL-REPETITION'); assert r['intake_status']=='qualified' and r['target_claim_ids']==t
qs=wp['target_scope']['mandatory_qualifications']; assert any('independent finite local dimensions' in q for q in qs); assert any('supremum' in q for q in qs); assert any('exponent 13' in q for q in qs); assert any('empty-answer' in q for q in qs)
PY
curl --fail --location --silent --show-error --retry 3 https://cdn.openai.com/pdf/ten-proofs-oai.pdf -o "$out/source.pdf"; assert_eq "$(stat -c '%s' "$out/source.pdf")" "$pdf_bytes" "source bytes"; assert_eq "$(sha256sum "$out/source.pdf"|cut -d' ' -f1)" "$pdf_sha" "source sha"; rm "$out/source.pdf"
if grep -nE '\b(sorry|admit)\b|^[[:space:]]*(axiom|unsafe)[[:space:]]' "$upstream/$solution" > "$out/trust-boundary-scan.txt"; then echo "solution trust-boundary violation" >&2; exit 1; fi; echo 'solution placeholder/custom-axiom/unsafe scan: clear' > "$out/trust-boundary-scan.txt"
(cd "$upstream" && lake build QuantumParallelRepetition) 2>&1 | tee "$out/solution-build.log"
ax="$upstream/MATHCERTGReplayAxioms.lean"; { echo 'import QuantumParallelRepetition'; for x in "${targets[@]}"; do echo "#check $x"; echo "#print axioms $x"; done; } > "$ax"; (cd "$upstream" && lake env lean "$(basename "$ax")") 2>&1 | tee "$out/theorem-axioms.log"; rm "$ax"
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
json.dump({'schema_version':'1.0.0','evidence_id':'MC-OTP-G-QUANTUM-PARALLEL-REPETITION-EXACT-HEAD-REPLAY-001','result_family':'OTP-G-QUANTUM-PARALLEL-REPETITION','mathcert_head':os.environ['HEAD'],'target_count':2,'targets':os.environ['TARGETS'].splitlines(),'source_pdf_identity':'exact_2026_08_06_bytes_reacquired','solution_build':'pass','theorem_axioms':'permitted_only','comparator':'accept','lean_default_kernel':'accept','nanoda':'accept','trust_boundary_scan':'clear','mathematical_target_proved':False,'aggregate_authority':False},open(os.environ['OUT'],'w'),indent=2)
PY
(cd "$out" && sha256sum solution-build.log theorem-axioms.log theorem-axiom-report.json comparator.log trust-boundary-scan.txt evidence-summary.json | LC_ALL=C sort > SHA256SUMS)
tar --sort=name --mtime='UTC 1970-01-01' --owner=0 --group=0 --numeric-owner -C "$out" -cf - SHA256SUMS solution-build.log theorem-axioms.log theorem-axiom-report.json comparator.log trust-boundary-scan.txt evidence-summary.json | gzip -n > "$out/bundle.tar.gz"; sha256sum "$out/bundle.tar.gz" | tee "$out/bundle.sha256"; echo OTP_G_QUANTUM_PARALLEL_REPETITION_EXACT_HEAD_REPLAY_ACCEPT
