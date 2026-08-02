#!/usr/bin/env python3
from __future__ import annotations
import base64,hashlib,io,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];RECORD_ROOT=ROOT/'governance/result_family_replay_evidence';REGISTRY=ROOT/'governance/pre_route_candidates/OPENAI_TEN_PROOFS_WP04_REPLAY_EVIDENCE.json';EXECUTION=ROOT/'governance/pre_route_candidates/OPENAI_TEN_PROOFS_WP03_REPLAY_EXECUTION.json';ROUTES=ROOT/'governance/certification_routes.json'
HEAD='a437fe81f1e84597e338cac90ed1f07e1720434d';MERGE='d0ae997e777af35d6ee051ccffbf86309acb397b';RUN=30726486167;ROUTES_BLOB='5b3e8d48b9f6c5b03ed3dc439bf9e43876e017b1'
EXPECTED={'OTP-F-EHRHART':('ehrhart',48,'OTP-F-EHRHART-CERT-WP01',91439051900,8826641842,'otp-ehrhart-evidence',7058,'22fcaad533db94c03569439bb41fcda68618386826abd3aa624bbf90e9345adb'),'OTP-J1-COMPACTNESS':('compactness',49,'OTP-J1-COMPACTNESS-CERT-WP01',91439051887,8826594510,'otp-compactness-evidence',7045,'852d0fa51a328199e6aeaf67a51fdd384ab30ec62ef6a7e28c5e22e597b3a99b'),'OTP-J2-TWO-DEGENERATE':('two-degenerate',50,'OTP-J2-TWO-DEGENERATE-CERT-WP01',91439051866,8826578658,'otp-two-degenerate-evidence',7019,'b3efb532152677dd84c0872071a9d2aa061ea56b9a8a7d9175c6382766f27ed4')}
REQUESTED={'MC-ROUTE-OTP-F-EHRHART','MC-ROUTE-OTP-J1-COMPACTNESS','MC-ROUTE-OTP-J2-TWO-DEGENERATE'}
def load(p):return json.loads(p.read_text())
def sha(b):return hashlib.sha256(b).hexdigest()
def blob_bytes(b):return hashlib.sha1(f'blob {len(b)}\0'.encode()+b,usedforsecurity=False).hexdigest()
def blob(p):return blob_bytes(p.read_bytes())
def validation_errors(records=None,registry=None,execution=None,routes=None):
 e=[];records={p.stem:load(p) for p in RECORD_ROOT.glob('*.json')} if records is None else records;registry=load(REGISTRY) if registry is None else registry;execution=load(EXECUTION) if execution is None else execution;routes=load(ROUTES) if routes is None else routes
 if set(records)!=set(EXPECTED):e.append('evidence membership drift')
 refs=[]
 for fam,x in EXPECTED.items():
  slug,issue,wp,job,aid,aname,abytes,asha=x;rec=records.get(fam)
  if not isinstance(rec,dict):continue
  auth={'repository':'grandchallenge/MATHCERT','pull_request':52,'head_sha':HEAD,'workflow_merge_sha':MERGE,'workflow_run_id':RUN,'job_id':job,'workflow_name':'OTP family replay','artifact':{'id':aid,'name':aname,'bytes':abytes,'sha256':asha}}
  if rec.get('execution_authority')!=auth or rec.get('work_package_id')!=wp:e.append(f'{fam}: authority drift')
  bpath=ROOT/f'evidence/openai_ten_proofs/{slug}.zip.b64';encoded=bpath.read_bytes() if bpath.exists() else b''
  try:decoded=base64.b64decode(encoded,validate=True);z=zipfile.ZipFile(io.BytesIO(decoded));names=sorted(z.namelist())
  except Exception:e.append(f'{fam}: bundle decode failure');continue
  bundle=rec.get('repository_bundle',{})
  if bundle.get('path')!=str(bpath.relative_to(ROOT)) or bundle.get('encoded_bytes')!=len(encoded) or bundle.get('encoded_git_blob_sha1')!=blob_bytes(encoded) or bundle.get('decoded_bytes')!=len(decoded) or bundle.get('decoded_sha256')!=sha(decoded):e.append(f'{fam}: bundle identity drift')
  actual_files=[{'name':n,'bytes':len(z.read(n)),'sha256':sha(z.read(n)),'git_blob_sha1':blob_bytes(z.read(n))} for n in names]
  if bundle.get('files')!=actual_files or len(names)!=11:e.append(f'{fam}: bundle file inventory drift')
  try:summary=json.loads(z.read('evidence-summary.json'));env=z.read('environment.txt').decode();comp=z.read('comparator.log').decode();ax=json.loads(z.read('axiom-check.json'));sums=z.read('SHA256SUMS').decode()
  except Exception:e.append(f'{fam}: bundle parse failure');continue
  if summary.get('result_family')!=fam or summary.get('execution',{}).get('mathcert_head_sha')!=HEAD or summary.get('execution',{}).get('workflow_checkout_sha')!=MERGE:e.append(f'{fam}: execution summary drift')
  results={'challenge_build':'pass','challenge_placeholders':'expected_comparator_boundary','solution_build':'pass','comparator':'pass','lean_kernel':'accept','nanoda':'accept','theorem_axiom_report':'permitted_only','trust_boundary_scan':'clear','source_revision_concordance':'blocked_pending_forge_audit'}
  if summary.get('results')!=results or rec.get('replay_results')!=results:e.append(f'{fam}: replay result drift')
  route={'proposed_route':None,'registered_route':None,'may_adjudicate':False,'cert_output':None,'mathematical_target_proved':False,'may_promote_claim':False}
  if summary.get('route_state')!=route or rec.get('route_state')!=route:e.append(f'{fam}: route inflation')
  for t in [f'mathcert_head_sha={HEAD}','Lean (version 4.32.0','mathlib_commit=81a5d257c8e410db227a6665ed08f64fea08e997','comparator_commit=07bc4ea40f2266dcb861820a2ec1fa3244ed307f','lean4checker_commit=b7398199245524275543dec6113229c9bb4902e5','lean4export_commit=4e7915201d3f9f04470d9eae002fa695f7cdc589','landrun_commit=811cfff51ceaf3d9843708aa6d22e9b84ccac8b4','nanoda_commit=ddfac2bf5a7b56cb46e141494427ff3dd55963c7']:
   if t not in env:e.append(f'{fam}: environment identity missing')
  if not all(t in comp for t in ['Lean default kernel accepts the solution','Nanoda kernel accepts the solution','Your solution is okay!']):e.append(f'{fam}: Comparator acceptance missing')
  if set(ax.get('permitted',[]))!={'propext','Classical.choice','Quot.sound'} or any(r.get('unexpected') for r in ax.get('reports',[])):e.append(f'{fam}: axiom boundary drift')
  listed={}
  for line in sums.splitlines():h,n=line.split(maxsplit=1);listed[Path(n.lstrip('*')).name]=h
  if 'SHA256SUMS' in listed:e.append(f'{fam}: self checksum')
  for n,h in listed.items():
   if n not in names or sha(z.read(n))!=h:e.append(f'{fam}: checksum drift {n}')
  if summary.get('source_revision',{}).get('current_revision_semantic_concordance')!='pending' or rec.get('source_revision',{}).get('current_revision_semantic_concordance')!='blocked_pending_forge_audit':e.append(f'{fam}: source block removed')
  if rec.get('review_state')!={'specialist_review_required':True,'specialist_review':None,'status':'pending_exact_head_non_author_specialist_review'}:e.append(f'{fam}: review drift')
  rp=RECORD_ROOT/f'{fam}.json';refs.append({'result_family':fam,'evidence_id':rec.get('evidence_id'),'path':str(rp.relative_to(ROOT)),'digest_algorithm':'git_blob_sha1','digest':blob(rp),'bundle_path':str(bpath.relative_to(ROOT)),'bundle_blob':blob(bpath),'artifact_id':aid,'artifact_sha256':asha})
 if registry.get('evidence_records')!=refs:e.append('evidence registry drift')
 state={'formal_replay_clear_count':3,'evidence_bundle_count':3,'specialist_review_count':0,'current_revision_semantic_concordance_clear_count':0,'proposed_route_count':0,'registered_route_count':0,'adjudication_count':0,'cert_output_count':0,'mathematical_target_proved_count':0}
 if registry.get('state')!=state:e.append('registry state drift')
 complete={'state':'formal_replay_completed_pending_source_revision_and_specialist_review','submitted_family_count':3,'completed_family_count':3,'evidence_bundle_count':3,'proposed_route_count':0,'registered_route_count':0,'adjudication_count':0,'cert_output_count':0,'mathematical_target_proved_count':0}
 if execution.get('execution_state')!=complete:e.append('execution completion drift')
 if blob(ROUTES)!=ROUTES_BLOB:e.append('global route registry changed')
 if REQUESTED & {str(x.get('route_id','')) for x in routes.get('routes',[]) if isinstance(x,dict)}:e.append('OTP route registered prematurely')
 return e
def main():
 e=validation_errors()
 if e:print('\n'.join(e),file=sys.stderr);print(f'replay evidence validation failed with {len(e)} error(s)',file=sys.stderr);return 1
 print('validated three repository-owned Lean 4.32.0 replay artifacts, exact checker identities, permitted axioms, blocked source concordance, zero routes, and pending specialist review');return 0
if __name__=='__main__':raise SystemExit(main())
