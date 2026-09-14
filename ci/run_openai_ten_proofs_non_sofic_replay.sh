#!/usr/bin/env bash
set -Eeuo pipefail
if (($#!=1)); then echo "usage: $0 OUTPUT_DIR" >&2; exit 64; fi
out="$1"; root="$(cd "$(dirname "$0")/.." && pwd)"; upstream="$root/upstream"; forge="$root/forge"; solve="$root/solve"; mkdir -p "$out"; out="$(cd "$out" && pwd)"
wp="governance/result_family_work_package_successors/OTP-D-NON-SOFIC-CERT-WP-001.json"; wp_commit="14746625f2f7599c5390da87fa3be42a04502c86"; wp_blob="b9f771cdde300070ba79f851e7cea7c3ede37a6f"
up_commit="94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6"; up_tree="174289e4d4958cb0509874e6e53400e098213de7"; config="ComparatorChallenges/D_NonSoficGroup.json"; config_blob="af023106a83552d7fafb4f0d122f121a095f802c"; challenge="ComparatorChallenges/D_NonSoficGroup.lean"; challenge_blob="158d97224fbd51c203ff07a2f74041ffa2c6013b"; solution="NonSoficGroup.lean"; solution_blob="dd1f8e63960300c8674fcd491007d2a628fbc6fe"
forge_commit="081928fceaca9606af4920559f8b79d5e40225a7"; forge_path="sources/OPENAI-TEN-PROOFS-001/semantic/OTP-D-NON-SOFIC/audit_record.json"; forge_blob="a9a5a2d56fceda6ebddf0c729d97c7cbeaf0d48b"; solve_commit="0ec6136d41ae1acd547e041ee8ca60de0d57effd"; packet="work_packages/OPENAI_TEN_PROOFS_WP00/result_family_handoff_successors/OTP-D-NON-SOFIC.json"; packet_blob="dfbd560c1340987b23874063c67d1e850dd48a52"
pdf_sha="ebc561ab5c53dbd240e17a8fdb6fffeb648591eca85dbfc7466f563638f8c566"; pdf_bytes="2487031"; target="SoficGroups.SourceTopLevelCompressionFinal.exists_finitelyPresented_nonsofic_group"
assert_eq(){ [[ "$1" == "$2" ]] || { echo "$3 mismatch: expected $2 found $1" >&2; exit 1; }; }; blob(){ git -C "$1" rev-parse "HEAD:$2"; }
assert_eq "$(git -C "$root" rev-parse "$wp_commit:$wp")" "$wp_blob" "work package historical blob"; assert_eq "$(git -C "$root" rev-parse "HEAD:$wp")" "$wp_blob" "work package current blob"
assert_eq "$(git -C "$upstream" rev-parse HEAD)" "$up_commit" "upstream commit"; assert_eq "$(git -C "$upstream" rev-parse 'HEAD^{tree}')" "$up_tree" "upstream tree"; assert_eq "$(blob "$upstream" "$config")" "$config_blob" "config blob"; assert_eq "$(blob "$upstream" "$challenge")" "$challenge_blob" "challenge blob"; assert_eq "$(blob "$upstream" "$solution")" "$solution_blob" "solution blob"
assert_eq "$(git -C "$forge" rev-parse HEAD)" "$forge_commit" "Forge commit"; assert_eq "$(blob "$forge" "$forge_path")" "$forge_blob" "Forge audit blob"; assert_eq "$(git -C "$solve" rev-parse HEAD)" "$solve_commit" "Solve commit"; assert_eq "$(blob "$solve" "$packet")" "$packet_blob" "Solve packet blob"
WP="$root/$wp" CFG="$upstream/$config" ROUTES="$root/governance/certification_routes.json" python3 - <<'PY'
import json,os
t=['SoficGroups.SourceTopLevelCompressionFinal.exists_finitelyPresented_nonsofic_group'];wp=json.load(open(os.environ['WP']));cfg=json.load(open(os.environ['CFG']));routes=json.load(open(os.environ['ROUTES']))
assert wp['target_scope']['lean_theorems']==t;assert cfg['theorem_names']==t;assert cfg['permitted_axioms']==['propext','Quot.sound','Classical.choice'];assert cfg['enable_nanoda'] is True
r=next(x for x in routes['routes'] if x.get('campaign_id')=='OTP-D-NON-SOFIC');assert r['intake_status']=='qualified' and r['target_claim_ids']==t
q=wp['target_scope']['mandatory_qualifications'];assert any('does not itself state' in x for x in q);assert any('derived formal consequence' in x for x in q);assert any('EL_D(R)/EL_9(R)' in x for x in q);assert any('81a5d257' in x for x in q)
PY
curl --fail --location --silent --show-error --retry 3 https://cdn.openai.com/pdf/ten-proofs-oai.pdf -o "$out/source.pdf"; assert_eq "$(stat -c '%s' "$out/source.pdf")" "$pdf_bytes" "source bytes"; assert_eq "$(sha256sum "$out/source.pdf"|cut -d' ' -f1)" "$pdf_sha" "source sha"; rm "$out/source.pdf"
if grep -nE '\b(sorry|admit)\b|^[[:space:]]*(axiom|unsafe)[[:space:]]' "$upstream/$solution" > "$out/trust-boundary-scan.txt"; then echo "solution trust-boundary violation" >&2; exit 1; fi; echo 'solution placeholder/custom-axiom/unsafe scan: clear' > "$out/trust-boundary-scan.txt"
(cd "$upstream" && lake build NonSoficGroup) 2>&1 | tee "$out/solution-build.log"
ax="$upstream/MATHCERTDReplayAxioms.lean"; { echo 'import NonSoficGroup'; echo "#check $target"; echo "#print axioms $target"; } > "$ax"; (cd "$upstream" && lake env lean "$(basename "$ax")") 2>&1 | tee "$out/theorem-axioms.log"; rm "$ax"
THEOREM="$target" LOG="$out/theorem-axioms.log" REPORT="$out/theorem-axiom-report.json" python3 - <<'PY'
import json,os,re
s=open(os.environ['LOG']).read();t=os.environ['THEOREM'];m=re.search(r"'"+re.escape(t)+r"' depends on axioms:\s*\[(.*?)\]",s,re.S);assert m,t;a={x.strip() for x in m.group(1).replace('\n',' ').split(',') if x.strip()};allowed={'propext','Classical.choice','Quot.sound'};assert not(a-allowed),(t,a-allowed);json.dump({'permitted':sorted(allowed),'reports':[{'theorem':t,'axioms':sorted(a)}]},open(os.environ['REPORT'],'w'),indent=2)
PY
(cd "$upstream" && lake exe comparator "$config") 2>&1 | tee "$out/comparator.log"; grep -Fq 'Nanoda kernel accepts the solution' "$out/comparator.log"; grep -Fq 'Lean default kernel accepts the solution' "$out/comparator.log"; grep -Fq 'Your solution is okay!' "$out/comparator.log"
TARGET="$target" OUT="$out/evidence-summary.json" HEAD="${MATHCERT_HEAD_SHA:-unknown}" python3 - <<'PY'
import json,os
json.dump({'schema_version':'1.0.0','evidence_id':'MC-OTP-D-NON-SOFIC-EXACT-HEAD-REPLAY-001','result_family':'OTP-D-NON-SOFIC','mathcert_head':os.environ['HEAD'],'target_count':1,'targets':[os.environ['TARGET']],'source_pdf_identity':'exact_2026_08_06_bytes_reacquired','solution_build':'pass','theorem_axioms':'permitted_only','comparator':'accept','lean_default_kernel':'accept','nanoda':'accept','trust_boundary_scan':'clear','mathematical_target_proved':False,'aggregate_authority':False},open(os.environ['OUT'],'w'),indent=2)
PY
(cd "$out" && sha256sum solution-build.log theorem-axioms.log theorem-axiom-report.json comparator.log trust-boundary-scan.txt evidence-summary.json | LC_ALL=C sort > SHA256SUMS); tar --sort=name --mtime='UTC 1970-01-01' --owner=0 --group=0 --numeric-owner -C "$out" -cf - SHA256SUMS solution-build.log theorem-axioms.log theorem-axiom-report.json comparator.log trust-boundary-scan.txt evidence-summary.json | gzip -n > "$out/bundle.tar.gz"; sha256sum "$out/bundle.tar.gz" | tee "$out/bundle.sha256"; echo OTP_D_NON_SOFIC_EXACT_HEAD_REPLAY_ACCEPT
