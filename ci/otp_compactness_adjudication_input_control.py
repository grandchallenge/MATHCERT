#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, json, subprocess, sys
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/'governance/result_family_adjudication_execution_inputs/OTP-J1-COMPACTNESS.json'
SCHEMA=ROOT/'schemas/openai_ten_proofs_compactness_adjudication_execution_input.schema.json'
ROUTES=ROOT/'governance/certification_routes.json'
ADJ=ROOT/'governance/result_family_adjudications/OTP-J1-COMPACTNESS.json'
CERT=ROOT/'certificates/formal_sources/MC-OTP-J1-COMPACTNESS-001.json'
AUTHORIZED_HEAD='28db9aad66381ff4f8b68a48c18090fa5c5b843b'
AUTHORIZED_BLOB='c9d8b31579e2bfdb93f99ff74d14f73a2fb603d7'
TARGETS=['CompactnessConjecture.quantitativeCompactnessCounterexample','CompactnessConjecture.compactnessCounterexample_bigO','CompactnessConjecture.not_erdos_180']
DISPOSITIONS=['adjudication_clear_encoded_targets_only','adjudication_not_clear','defer_insufficient_evidence']
PINS={
'governance/result_family_adjudication_contracts/OTP-J1-COMPACTNESS.json':'4288cf2199603ffc90d897062a575a5865326d70',
'governance/result_family_construction_evidence/OTP-J1-COMPACTNESS.json':'872cdf678412d63df22d1244b3b5c13185f29571',
'evidence/openai_ten_proofs/compactness_construction/source_authority.json':'148ff82af760bba80c7d16a3a35c58d490dadc95',
'evidence/openai_ten_proofs/compactness_construction/reconstruction.json':'ed79d855016a1e642d361e9162ed2b70d267b800',
'governance/certification_routes.json':'aa460c1310a7c81b64b88013b7aa4cfdc056f37b'}
def load(p): return json.loads(p.read_text(encoding='utf-8'))
def req(c,m):
 if not c: raise ValueError(m)
def blob(p): return subprocess.check_output(['git','hash-object',str(p)],cwd=ROOT,text=True).strip()
def ancestor(a): return subprocess.run(['git','merge-base','--is-ancestor',a,'HEAD'],cwd=ROOT).returncode==0
def validate_record(r,check_repository=True):
 es=sorted(Draft202012Validator(load(SCHEMA)).iter_errors(r),key=lambda e:list(e.path))
 if es: raise ValueError('schema validation failed: '+'; '.join(e.message for e in es[:4]))
 req(r['protected_base']=='ad80e83ceb6dd1ac980d4c2c02cd07b11b8c3d90','protected base drift')
 req(r['contract']['contract_id']=='MC-OTP-ADJUDICATION-CONTRACT-J1-COMPACTNESS' and r['contract']['git_blob_sha1']==PINS['governance/result_family_adjudication_contracts/OTP-J1-COMPACTNESS.json'],'contract drift')
 req(r['encoded_targets']==TARGETS,'target drift'); req(r['decision_contract']['admissible_dispositions']==DISPOSITIONS and r['decision_contract']['disposition_at_input_stage'] is None,'decision input drift')
 e=r['protected_evidence']; req(e['record_git_blob_sha1']==PINS['governance/result_family_construction_evidence/OTP-J1-COMPACTNESS.json'] and e['source_manifest_git_blob_sha1']==PINS['evidence/openai_ten_proofs/compactness_construction/source_authority.json'] and e['reconstruction_git_blob_sha1']==PINS['evidence/openai_ten_proofs/compactness_construction/reconstruction.json'],'protected evidence drift')
 s=r['current_source']; req(s['expected_bytes']==2487031 and s['expected_sha256']=='ebc561ab5c53dbd240e17a8fdb6fffeb648591eca85dbfc7466f563638f8c566' and s['whole_document_equivalence_between_revisions']=='not_established','source drift/inflation')
 x=r['execution_recipe']; req(x['human_steward_authorization_required'] and x['authorization_must_name_contract_and_exact_head'] and not x['execution_authorized'] and x['authorization'] is None and x['fresh_source_reacquisition_required'] and x['fresh_isolated_replay_required'] and x['publication_must_be_descendant_of_authorized_input_head'],'execution recipe weakened')
 req(r['required_state']=={'adjudication':None,'aggregate_adjudication':False,'aggregate_output':False,'cert_output':None,'mathematical_target_proved':False,'may_adjudicate':False,'may_promote_claim':False,'route_state':'submitted'},'input-stage state inflation')
 req(r['review_gate']['recorded_review'] is None and not r['preserved_limitations']['proof_body_compared_in_full'] and not r['preserved_limitations']['aggregate_openai_ten_proofs_authority'],'input authority inflation')
 if not check_repository:return
 req(blob(INPUT)==AUTHORIZED_BLOB,'frozen execution input bytes changed'); req(ancestor(AUTHORIZED_HEAD),'HEAD not descendant of authorized input')
 for rel,exp in PINS.items(): req(blob(ROOT/rel)==exp,f'protected blob drift: {rel}')
 route=[q for q in load(ROUTES)['routes'] if q.get('route_id')=='MC-ROUTE-OTP-J1-COMPACTNESS']; req(len(route)==1 and route[0].get('intake_status')=='submitted' and route[0].get('cert_output') is None and route[0].get('target_claim_ids')==TARGETS,'live route mutated')
 if ADJ.exists():
  a=load(ADJ); auth=a.get('authority',{}).get('human_steward_execution_authorization',{})
  req(auth.get('comment_id')==5302142079 and auth.get('authorized_input_head')==AUTHORIZED_HEAD,'adjudication lacks exact Human Steward authorization')
 req(not CERT.exists(),'Compactness certificate exists without output authority')
def self_test(base):
 muts=[lambda r:r['encoded_targets'].pop(),lambda r:r['current_source'].__setitem__('expected_sha256','0'*64),lambda r:r['contract'].__setitem__('contract_id','OTHER'),lambda r:r['decision_contract'].__setitem__('disposition_at_input_stage','adjudication_clear_encoded_targets_only'),lambda r:r['execution_recipe'].__setitem__('authorization_must_name_contract_and_exact_head',False),lambda r:r['required_state'].__setitem__('route_state','qualified'),lambda r:r['required_state'].__setitem__('cert_output',{}),lambda r:r['required_state'].__setitem__('mathematical_target_proved',True),lambda r:r['review_gate'].__setitem__('recorded_review',{'state':'APPROVED'}),lambda r:r.__setitem__('unexpected',True)]
 for i,m in enumerate(muts,1):
  q=copy.deepcopy(base);m(q)
  try:validate_record(q,False)
  except Exception:continue
  raise ValueError(f'mutation {i} incorrectly accepted')
def main():
 p=argparse.ArgumentParser();p.add_argument('--self-test',action='store_true');a=p.parse_args()
 try:
  r=load(INPUT);validate_record(r); self_test(r) if a.self_test else None
 except Exception as e: print(f'Compactness adjudication input control failed: {e}',file=sys.stderr);return 1
 print('validated frozen Compactness adjudication execution input and authorized descendant state')
 if a.self_test: print('Compactness adjudication input mutation suite passed')
 return 0
if __name__=='__main__':raise SystemExit(main())
