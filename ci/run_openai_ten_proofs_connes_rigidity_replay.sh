#!/usr/bin/env bash
set -Eeuo pipefail
if (($#!=1)); then echo "usage: $0 OUTPUT_DIR" >&2; exit 64; fi
out="$1"; root="$(cd "$(dirname "$0")/.." && pwd)"; upstream="$root/upstream"; forge="$root/forge"; solve="$root/solve"; mkdir -p "$out"; out="$(cd "$out" && pwd)"
wp="governance/result_family_work_package_successors/OTP-E-CONNES-RIGIDITY-CERT-WP-001.json"; wp_commit="22d9ca44a64ec71aa4a0b77d87b55017ccf9949a"; wp_blob="00400006cfa7d7dde1b04b8e8564c53f61a46450"
up_commit="94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6"; up_tree="174289e4d4958cb0509874e6e53400e098213de7"; config="ComparatorChallenges/E_ConnesRigidity.json"; config_blob="f5d2964be6b1a154bc12b38a0f99f0960960a2d9"; challenge="ComparatorChallenges/E_ConnesRigidity.lean"; challenge_blob="9425edabd79319cbe2943888c6ece107bdd81dfb"; solution="ConnesRigidity.lean"; solution_blob="81cf03e3f7ccdc66815cc00c9969bcfd2341c8d6"
forge_commit="ed8a65410336489ea5646808265c44f5387bebb8"; forge_path="sources/OPENAI-TEN-PROOFS-001/semantic/OTP-E-CONNES-RIGIDITY/audit_record.json"; forge_blob="ab38a22d029bacc09d7567166b3b5e380f207f99"; solve_commit="07814c1e28855ff0314737d3666642217da095a1"; packet="work_packages/OPENAI_TEN_PROOFS_WP00/result_family_handoff_successors/OTP-E-CONNES-RIGIDITY.json"; packet_blob="a2a76e5708245bd75c293713e1925617369c48ea"
pdf_sha="ebc561ab5c53dbd240e17a8fdb6fffeb648591eca85dbfc7466f563638f8c566"; pdf_bytes="2487031"; targets=("ConnesRigidity.exists_nonisomorphic_propertyT_icc_groups_with_isomorphic_factors" "ConnesRigidity.exists_infinite_pairwise_nonisomorphic_propertyT_icc_groups_with_isomorphic_factors")
assert_eq(){ [[ "$1" == "$2" ]] || { echo "$3 mismatch: expected $2 found $1" >&2; exit 1; }; }; blob(){ git -C "$1" rev-parse "HEAD:$2"; }
assert_eq "$(git -C "$root" rev-parse "$wp_commit:$wp")" "$wp_blob" "work package historical blob"; assert_eq "$(git -C "$root" rev-parse "HEAD:$wp")" "$wp_blob" "work package current blob"
assert_eq "$(git -C "$upstream" rev-parse HEAD)" "$up_commit" "upstream commit"; assert_eq "$(git -C "$upstream" rev-parse 'HEAD^{tree}')" "$up_tree" "upstream tree"; assert_eq "$(blob "$upstream" "$config")" "$config_blob" "config blob"; assert_eq "$(blob "$upstream" "$challenge")" "$challenge_blob" "challenge blob"; assert_eq "$(blob "$upstream" "$solution")" "$solution_blob" "solution blob"
assert_eq "$(git -C "$forge" rev-parse HEAD)" "$forge_commit" "Forge commit"; assert_eq "$(blob "$forge" "$forge_path")" "$forge_blob" "Forge audit blob"; assert_eq "$(git -C "$solve" rev-parse HEAD)" "$solve_commit" "Solve commit"; assert_eq "$(blob "$solve" "$packet")" "$packet_blob" "Solve packet blob"
WP="$root/$wp" CFG="$upstream/$config" ROUTES="$root/governance/certification_routes.json" python3 - <<'PY'
import json,os
t=['ConnesRigidity.exists_nonisomorphic_propertyT_icc_groups_with_isomorphic_factors','ConnesRigidity.exists_infinite_pairwise_nonisomorphic_propertyT_icc_groups_with_isomorphic_factors'];wp=json.load(open(os.environ['WP']));cfg=json.load(open(os.environ['CFG']));routes=json.load(open(os.environ['ROUTES']))
assert wp['target_scope']['lean_theorems']==t;assert cfg['theorem_names']==t;assert cfg['permitted_axioms']==['propext','Quot.sound','Classical.choice'];assert cfg['enable_nanoda'] is True
r=next(x for x in routes['routes'] if x.get('campaign_id')=='OTP-E-CONNES-RIGIDITY');assert r['intake_status']=='qualified' and r['target_claim_ids']==t
q=wp['target_scope']['mandatory_qualifications'];assert any('ConnesRigidity2' in x for x in q);assert any('TracialGroupFactorEquiv' in x for x in q);assert any('projection-supremum' in x for x in q);assert any('through Lambda' in x for x in q);assert any('finite-generation' in x for x in q)
PY
curl --fail --location --silent --show-error --retry 3 https://cdn.openai.com/pdf/ten-proofs-oai.pdf -o "$out/source.pdf"; assert_eq "$(stat -c '%s' "$out/source.pdf")" "$pdf_bytes" "source bytes"; assert_eq "$(sha256sum "$out/source.pdf"|cut -d' ' -f1)" "$pdf_sha" "source sha"; rm "$out/source.pdf"
if grep -nE '\b(sorry|admit)\b|^[[:space:]]*(axiom|unsafe)[[:space:]]' "$upstream/$solution" > "$out/trust-boundary-scan.txt"; then echo "solution trust-boundary violation" >&2; exit 1; fi; echo 'solution placeholder/custom-axiom/unsafe scan: clear' > "$out/trust-boundary-scan.txt"
(cd "$upstream" && lake build ConnesRigidity) 2>&1 | tee "$out/solution-build.log"
ax="$upstream/MATHCERTEReplayAxioms.lean"; { echo 'import ConnesRigidity'; for target in "${targets[@]}"; do echo "#check $target"; echo "#print axioms $target"; done; } > "$ax"; (cd "$upstream" && lake env lean "$(basename "$ax")") 2>&1 | tee "$out/theorem-axioms.log"; rm "$ax"
TARGETS="$(IFS='|'; echo "${targets[*]}")" LOG="$out/theorem-axioms.log" REPORT="$out/theorem-axiom-report.json" python3 - <<'PY'
import json,os,re
s=open(os.environ['LOG']).read();ts=os.environ['TARGETS'].split('|');allowed={'propext','Classical.choice','Quot.sound'};reports=[]
for t in ts:
 m=re.search(r"'"+re.escape(t)+r"' depends on axioms:\s*\[(.*?)\]",s,re.S);assert m,t;a={x.strip() for x in m.group(1).replace('\n',' ').split(',') if x.strip()};assert not(a-allowed),(t,a-allowed);reports.append({'theorem':t,'axioms':sorted(a)})
json.dump({'permitted':sorted(allowed),'reports':reports},open(os.environ['REPORT'],'w'),indent=2)
PY
(cd "$upstream" && lake exe comparator "$config") 2>&1 | tee "$out/comparator.log"; grep -Fq 'Nanoda kernel accepts the solution' "$out/comparator.log"; grep -Fq 'Lean default kernel accepts the solution' "$out/comparator.log"; grep -Fq 'Your solution is okay!' "$out/comparator.log"
TARGETS="$(IFS='|'; echo "${targets[*]}")" OUT="$out/evidence-summary.json" HEAD="${MATHCERT_HEAD_SHA:-unknown}" python3 - <<'PY'
import json,os
ts=os.environ['TARGETS'].split('|');json.dump({'schema_version':'1.0.0','evidence_id':'MC-OTP-E-CONNES-RIGIDITY-EXACT-HEAD-REPLAY-001','result_family':'OTP-E-CONNES-RIGIDITY','mathcert_head':os.environ['HEAD'],'target_count':len(ts),'targets':ts,'source_pdf_identity':'exact_2026_08_06_bytes_reacquired','solution_build':'pass','theorem_axioms':'permitted_only','comparator':'accept','lean_default_kernel':'accept','nanoda':'accept','trust_boundary_scan':'clear','mathematical_target_proved':False,'aggregate_authority':False},open(os.environ['OUT'],'w'),indent=2)
PY
(cd "$out" && sha256sum solution-build.log theorem-axioms.log theorem-axiom-report.json comparator.log trust-boundary-scan.txt evidence-summary.json | LC_ALL=C sort > SHA256SUMS); tar --sort=name --mtime='UTC 1970-01-01' --owner=0 --group=0 --numeric-owner -C "$out" -cf - SHA256SUMS solution-build.log theorem-axioms.log theorem-axiom-report.json comparator.log trust-boundary-scan.txt evidence-summary.json | gzip -n > "$out/bundle.tar.gz"; sha256sum "$out/bundle.tar.gz" | tee "$out/bundle.sha256"; echo OTP_E_CONNES_RIGIDITY_EXACT_HEAD_REPLAY_ACCEPT
