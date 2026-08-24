#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / "upstream"
FAMILIES={"OTP-H-GAPCVP":{"work_package":"governance/result_family_work_package_successors/OTP-H-GAPCVP-CERT-WP-001.json"},"OTP-B1-BINARY-CODES":{"work_package":"governance/result_family_work_package_successors/OTP-B1-BINARY-CODES-CERT-WP-001.json"},"OTP-B2-SPHERICAL-CODES":{"work_package":"governance/result_family_work_package_successors/OTP-B2-SPHERICAL-CODES-CERT-WP-001.json"}}
def fail(msg:str)->None: raise SystemExit(msg)
def sha256(path:Path)->str:
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
 return h.hexdigest()
def git_head(path:Path)->str:return subprocess.check_output(['git','-C',str(path),'rev-parse','HEAD'],text=True).strip()
def git_blob(path:Path,rel:str)->str:return subprocess.check_output(['git','-C',str(path),'rev-parse',f'HEAD:{rel}'],text=True).strip()
def write_json(path:Path,obj:object)->None:path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n',encoding='utf-8')
def main()->int:
 if len(sys.argv)!=3 or sys.argv[1] not in FAMILIES: fail('usage: otp_finalize_family_replay_evidence.py FAMILY OUTPUT_DIR')
 family=sys.argv[1];out=Path(sys.argv[2]).resolve()
 if not out.is_dir(): fail(f'missing replay output directory: {out}')
 wp=json.loads((ROOT/FAMILIES[family]['work_package']).read_text());subject=wp['authority']['official_subject'];toolchain=wp['toolchain'];scope=wp['target_scope'];execution=wp['execution_contract']
 comparator_log=out/'comparator.log';axiom_report=out/'theorem-axiom-report.json';summary_path=out/'evidence-summary.json'
 for required in (comparator_log,out/'solution-build.log',axiom_report,summary_path,out/'trust-boundary-scan.txt',out/'source-identity-report.txt'):
  if not required.exists():fail(f'missing replay artifact before finalization: {required.name}')
 text=comparator_log.read_text(errors='replace')
 for marker in ('Nanoda kernel accepts the solution','Lean default kernel accepts the solution','Your solution is okay!'):
  if marker not in text:fail(f'missing Comparator success marker: {marker}')
 if git_head(UPSTREAM)!=subject['commit']:fail('formal subject commit drift')
 if subprocess.check_output(['git','-C',str(UPSTREAM),'rev-parse','HEAD^{tree}'],text=True).strip()!=subject['tree']:fail('formal subject tree drift')
 for key,rel in (('config_blob',subject['config_path']),('challenge_blob',subject['challenge_path']),('solution_blob',subject['solution_path']),('lake_manifest_blob','lake-manifest.json'),('lean_toolchain_blob','lean-toolchain')):
  if git_blob(UPSTREAM,rel)!=subject[key]:fail(f'formal subject blob drift: {rel}')
 checks={UPSTREAM/'.lake/packages/mathlib':toolchain['mathlib_commit'],UPSTREAM/'.lake/packages/Comparator':toolchain['comparator_commit'],UPSTREAM/'.lake/packages/Lean4Checker':toolchain['lean4checker_commit'],ROOT/'lean4export-src':toolchain['lean4export_commit'],ROOT/'nanoda-src':toolchain['nanoda_commit'],ROOT/'landrun-src':toolchain['landrun_commit']};observed={}
 for path,expected in checks.items():
  if not path.exists():fail(f'missing pinned tool source: {path.name}')
  actual=git_head(path)
  if actual!=expected:fail(f'tool source identity drift: {path.name}: {actual} != {expected}')
  observed[path.name]=actual
 lean_line=subprocess.check_output(['lean','--version'],text=True).splitlines()[0];lean_version=toolchain['lean'].split(':v',1)[1]
 if lean_version not in lean_line or toolchain['lean_commit'] not in lean_line:fail(f'Lean identity drift: {lean_line}')
 hp={'landrun':Path(os.environ.get('COMPARATOR_LANDRUN_REAL','')),'lean4export':Path(os.environ.get('COMPARATOR_LEAN4EXPORT','')),'nanoda_bin':Path(os.environ.get('COMPARATOR_NANODA','')),'landrun_argv_adapter':Path(os.environ.get('COMPARATOR_LANDRUN',''))};hs={}
 for key,path in hp.items():
  if not str(path) or not path.is_file():fail(f'missing helper binary/path for {key}')
  actual=sha256(path);expected=toolchain['observed_helper_sha256'][key]
  if actual!=expected:fail(f'helper SHA-256 drift for {key}: {actual} != {expected}')
  hs[key]=actual
 cfg=json.loads((UPSTREAM/subject['config_path']).read_text());targets=scope['lean_theorems']
 if cfg.get('theorem_names')!=targets:fail('Comparator target export/order drift')
 if cfg.get('permitted_axioms')!=execution['permitted_axioms']:fail('Comparator permitted-axiom drift')
 if cfg.get('enable_nanoda') is not True:fail('Nanoda disabled in Comparator configuration')
 ax=json.loads(axiom_report.read_text())
 if any(r.get('unexpected') for r in ax.get('reports',[])) or len(ax.get('reports',[]))!=len(targets):fail('theorem axiom report drift')
 write_json(out/'environment-manifest.json',{'result_family':family,'mathcert_head':os.environ.get('MATHCERT_HEAD_SHA','unknown'),'runner_os':os.environ.get('RUNNER_OS','unknown'),'runner_arch':os.environ.get('RUNNER_ARCH','unknown'),'image_os':os.environ.get('ImageOS','unknown'),'image_version':os.environ.get('ImageVersion','unknown'),'lean':lean_line,'formal_subject_commit':subject['commit'],'formal_subject_tree':subject['tree'],'tool_source_commits':observed,'helper_sha256':hs})
 write_json(out/'toolchain-identity-report.json',{'state':'exact_pinned_identity_verified','lean':toolchain['lean'],'lean_commit':toolchain['lean_commit'],'mathlib_commit':toolchain['mathlib_commit'],'comparator_commit':toolchain['comparator_commit'],'lean4checker_commit':toolchain['lean4checker_commit'],'lean4export_commit':toolchain['lean4export_commit'],'nanoda_commit':toolchain['nanoda_commit'],'landrun_commit':toolchain['landrun_commit'],'observed_helper_sha256':hs})
 export={'state':'exact_export_order_verified','target_count':len(targets),'targets':targets,'comparator_config':subject['config_path'],'config_exact_match':True}
 if family=='OTP-H-GAPCVP':export.update({'promise_count':len(scope['promise_interfaces']),'promises':scope['promise_interfaces']});write_json(out/'target-and-promise-export-report.json',export)
 else:write_json(out/'target-export-report.json',export)
 write_json(out/'comparator-result.json',{'state':'accept','marker':'Your solution is okay!'});write_json(out/'lean-kernel-result.json',{'state':'accept','marker':'Lean default kernel accepts the solution'});write_json(out/'nanoda-result.json',{'state':'accept','marker':'Nanoda kernel accepts the solution'})
 write_json(out/'semantic-concordance-attestation.json',{'state':'bound_to_protected_forge_semantic_authority','forge':wp['authority']['forge_semantic'],'source_loci':scope.get('source_loci',[]),'classifications':scope['classifications'],'mandatory_qualifications':scope['mandatory_qualifications'],'independent_source_reclassification_performed':False,'whole_chapter_equivalence':False,'full_proof_body_equivalence':False})
 non='promise-nonvacuity-attestation.json' if family=='OTP-H-GAPCVP' else 'nonvacuity-attestation.json';write_json(out/non,{'state':scope['nonvacuity']['state'],'protected_nonvacuity':scope['nonvacuity'],'new_nonvacuity_claim_added':False})
 if family=='OTP-B1-BINARY-CODES':write_json(out/'minimizer-attainment-attestation.json',{'state':'protected_bridge_bound','requirement':'Lean sInf representation of M2 remains source-equivalent only through the protected exact minimizer existence and attainment proof on the target domain.','evidence':[x for x in scope['nonvacuity']['evidence'] if 'minim' in x.lower() or 'mrrw' in x.lower()],'bridge_erasure':False})
 elif family=='OTP-B2-SPHERICAL-CODES':
  write_json(out/'hierarchy-domain-attestation.json',{'state':'protected_domains_bound','qualification':'Hierarchy, interlacing and localization domains remain bound to the protected current-root semantic/nonvacuity audit.','nonvacuity_evidence':scope['nonvacuity']['evidence'],'domain_drift':False})
  write_json(out/'numerical-strengthening-attestation.json',{'state':'formal_strengthening_only','target':targets[-1],'manuscript_printed_statement':'0.39661+o(1)','formal_exact_eventual_bound':'0.39661','manuscript_verbatim_precision_attributed':False,'predecessor_seven_target_authority_transferred':False})
 summary=json.loads(summary_path.read_text());summary.update({'evidence_artifact_set_complete_for_runtime_replay':True,'exact_toolchain_identity':'verified','helper_binary_identity':'verified','independent_review_attestation':'pending_final_evidence_head_review'});write_json(summary_path,summary)
 (out/'family-replay-log.txt').write_text(f"result_family={family}\nmathcert_head={os.environ.get('MATHCERT_HEAD_SHA','unknown')}\nsolution_build=pass\ncomparator=accept\nlean_default_kernel=accept\nnanoda=accept\nexact_toolchain_identity=verified\nhelper_binary_identity=verified\nroute_proposed=false\nroute_registered=false\nmay_adjudicate=false\ncert_output=null\nmathematical_target_proved=false\naggregate_authority=false\nmay_promote_claim=false\n")
 for name in ('SHA256SUMS','bundle.tar.gz','bundle.sha256'):
  p=out/name
  if p.exists():p.unlink()
 files=sorted(p for p in out.iterdir() if p.is_file());(out/'SHA256SUMS').write_text(''.join(f'{sha256(p)}  {p.name}\n' for p in files));names=[p.name for p in sorted(out.iterdir()) if p.is_file() and p.name not in {'bundle.tar.gz','bundle.sha256'}]
 tar=subprocess.Popen(['tar','--sort=name','--mtime=UTC 1970-01-01','--owner=0','--group=0','--numeric-owner','-C',str(out),'-cf','-',*names],stdout=subprocess.PIPE)
 with (out/'bundle.tar.gz').open('wb') as fh:gz=subprocess.run(['gzip','-n'],stdin=tar.stdout,stdout=fh)
 assert tar.stdout is not None;tar.stdout.close();trc=tar.wait()
 if trc!=0 or gz.returncode!=0:fail('deterministic evidence bundle construction failed')
 (out/'bundle.sha256').write_text(f"{sha256(out/'bundle.tar.gz')}  bundle.tar.gz\n");print(f'{family}: COMPLETE_RUNTIME_EVIDENCE_SET__FINAL_HEAD_REVIEW_STILL_REQUIRED');return 0
if __name__=='__main__':raise SystemExit(main())
