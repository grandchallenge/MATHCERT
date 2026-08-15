#!/usr/bin/env python3
from __future__ import annotations

import base64, hashlib, io, json, subprocess, sys, zipfile
from pathlib import Path
from typing import Any
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
PATHS={
 'record':ROOT/'governance/result_family_evidence_refreshes/OTP-J1-COMPACTNESS.json',
 'schema':ROOT/'schemas/openai_ten_proofs_compactness_evidence_refresh.schema.json',
 'candidate':ROOT/'governance/result_family_evidence_refresh_execution_candidates/OTP-J1-COMPACTNESS.json',
 'contract':ROOT/'governance/result_family_adjudication_contracts/OTP-J1-COMPACTNESS.json',
 'prior':ROOT/'governance/result_family_replay_evidence/OTP-J1-COMPACTNESS.json',
 'routes':ROOT/'governance/certification_routes.json',
 'bundle':ROOT/'evidence/openai_ten_proofs/compactness_refresh/refresh_bundle.zip.b64',
}
BASE='150344d25b50895203c59f4193a8e97bb1cbbf81'
EXEC='4711fbc2d3232cd2ccddbc85f032fda5c6a92b7f'
CAND_COMMIT='73dfe0152744e59cbf579d3b203d85fc746371b8'
RUN=30774901934; JOB=91568431665; ART=8841786605; SIZE=8035
ART_SHA='d0f1fadda05b7d58e6ddd13fbe40b1e2ebb7da388e8c4afe86a7fbdd962e14c4'
BLOBS={'candidate':'074709d53f8e0fd672913b5890711d9093948e21','contract':'4288cf2199603ffc90d897062a575a5865326d70','prior':'5fe635510a0d2aa05da641e342078cf8b2b34aa6','routes':'0487c3ebf702229741f16a544d68af25cf994e41','bundle':'de6b19210889b3230b42cc0720b4f0439e4bd9e5'}
THEOREMS=['CompactnessConjecture.quantitativeCompactnessCounterexample','CompactnessConjecture.compactnessCounterexample_bigO','CompactnessConjecture.not_erdos_180']
WITNESSES=THEOREMS[:2]; AXIOMS=['Classical.choice','Quot.sound','propext']
FAMILIES=[{'result_family':'OTP-F-EHRHART','route_state':'qualified','adjudication_count':1,'cert_output_count':1},{'result_family':'OTP-J1-COMPACTNESS','route_state':'submitted','adjudication_count':0,'cert_output_count':0},{'result_family':'OTP-J2-TWO-DEGENERATE','route_state':'submitted','adjudication_count':0,'cert_output_count':0}]
FILES={'SHA256SUMS','authority-receipt.json','axiom-check.json','challenge-build.log','comparator.log','environment.txt','evidence-summary.json','solution-build.log','source-identities.txt','source-revision-report.txt','theorem-axioms.log','trust-boundary-scan.txt'}


def load(p:Path)->Any:return json.loads(p.read_text(encoding='utf-8'))
def git(*a:str):return subprocess.run(['git',*a],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
def ensure(c:str)->None:
 r=git('cat-file','-e',f'{c}^{{commit}}')
 if r.returncode==0:return
 if git('rev-parse','--is-shallow-repository').stdout.strip()=='true':git('fetch','--no-tags','--unshallow','origin')
 else:git('fetch','--no-tags','origin',c)
 if git('cat-file','-e',f'{c}^{{commit}}').returncode:raise RuntimeError(f'unable to fetch governed commit {c}')
def blob(c:str,p:Path)->str:
 ensure(c); r=git('rev-parse',f'{c}:{p.relative_to(ROOT).as_posix()}')
 if r.returncode:raise RuntimeError(f'unable to resolve {p} at {c}')
 return r.stdout.strip()
def ancestor(a:str,b:str)->bool:ensure(a);ensure(b);return git('merge-base','--is-ancestor',a,b).returncode==0

def decode(payload:bytes)->tuple[bytes,dict[str,bytes]]:
 raw=base64.b64decode(payload.strip(),validate=True)
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  names=z.namelist()
  if len(names)!=len(set(names)) or any(n.startswith('/') or '..' in Path(n).parts for n in names):raise ValueError('unsafe or duplicate bundle member')
  return raw,{n:z.read(n) for n in names if not n.endswith('/')}

def closure(x:Any,loc='$')->list[str]:
 out=[]
 if isinstance(x,dict):
  if x.get('type')=='object' and x.get('additionalProperties') is not False:out.append(f'schema object is not closed at {loc}')
  for k,v in x.items():out+=closure(v,f'{loc}.{k}')
 elif isinstance(x,list):
  for i,v in enumerate(x):out+=closure(v,f'{loc}[{i}]')
 return out

def parse(fs:dict[str,bytes],name:str)->dict[str,Any]:
 v=json.loads(fs[name].decode());
 if not isinstance(v,dict):raise ValueError(f'{name} must contain an object')
 return v

def defaults()->dict[str,Any]:
 enc=PATHS['bundle'].read_bytes(); raw,fs=decode(enc)
 historical_blobs={k:blob('HEAD',PATHS[k]) for k in ('candidate','contract','prior','bundle')}
 historical_blobs['routes']=blob(BASE,PATHS['routes'])
 return {'record':load(PATHS['record']),'schema':load(PATHS['schema']),'candidate':load(PATHS['candidate']),'contract':load(PATHS['contract']),'prior':load(PATHS['prior']),'routes':load(PATHS['routes']),'decoded_bundle':raw,'bundle_files':fs,
 'blobs':historical_blobs,
 'receipt':{'base_exec':ancestor(BASE,EXEC),'exec_head':ancestor(EXEC,'HEAD'),'cand_head':ancestor(CAND_COMMIT,'HEAD'),'cand_commit_blob':blob(CAND_COMMIT,PATHS['candidate'])},
 'other_adjudication_present':(ROOT/'governance/result_family_adjudications/OTP-J1-COMPACTNESS.json').exists(),
 'output_candidate_present':(ROOT/'governance/result_family_output_candidates/OTP-J1-COMPACTNESS.json').exists()}

def validation_errors(*,record=None,schema=None,candidate=None,contract=None,prior=None,routes=None,decoded_bundle=None,bundle_files=None,blobs=None,receipt=None,other_adjudication_present=None,output_candidate_present=None)->list[str]:
 d=defaults(); loc=locals(); vals={k:(d[k] if loc[k] is None else loc[k]) for k in d}; record=vals['record'];schema=vals['schema'];candidate=vals['candidate'];contract=vals['contract'];prior=vals['prior'];routes=vals['routes'];decoded_bundle=vals['decoded_bundle'];bundle_files=vals['bundle_files'];blobs=vals['blobs'];receipt=vals['receipt'];other_adjudication_present=vals['other_adjudication_present'];output_candidate_present=vals['output_candidate_present']
 e=closure(schema)
 try:e += [f'schema violation: {x.message}' for x in Draft202012Validator(schema).iter_errors(record)]
 except Exception as x:e.append(f'schema is invalid: {x}')
 for k,v in BLOBS.items():
  if blobs.get(k)!=v:e.append(f'protected blob drift: {k}')
 if receipt!={'base_exec':True,'exec_head':True,'cand_head':True,'cand_commit_blob':BLOBS['candidate']}:e.append('Git receipt drift')
 if (ROOT/'.github/workflows/otp-compactness-evidence-refresh-replay.yml').exists():e.append('temporary replay workflow remains in final candidate')
 auth=record.get('authority',{})
 exact_auth={
  'protected_base':BASE,'implementation_authorization':{'comment_id':5161082831,'author':'jimsteeg','scope':'evidence_refresh_only_no_adjudication'},
  'official_subject':{'repository':'openai/ten-proofs','commit':'e62211d28e3a9131950c89caa6542cfe5eff3bca','tree':'2f8e7ac5ae7f157b6b1de636c2c343b1c7a7e365','archive_sha256':'3022e62ffbed8f5f74d232034a703dc645e6b301879dff1e87df72979914294f'},
  'forge_source_revision_audit':{'repository':'grandchallenge/MATHFORGE','commit_sha':'a498ef40b7652b55bf121b5682604e259b8d3073','path':'sources/OPENAI-TEN-PROOFS-001/source_revision_audits/OTP-TRANCHE-001.json','digest_algorithm':'git_blob_sha1','digest':'80d473b1b545fd9ca05fc5200bcf70ff5f9fcb05'},
  'forge_semantic_record':{'repository':'grandchallenge/MATHFORGE','commit_sha':'cb0a203c36a9ef33270d62ab369df7bc27d3b242','path':'sources/OPENAI-TEN-PROOFS-001/semantic_audits/OTP-J1-COMPACTNESS.json','digest_algorithm':'git_blob_sha1','digest':'659396358d0d999c00011645f72602f30ccf6b0e'},
  'solve_producer_packet':{'repository':'grandchallenge/MATHSOLVE','commit_sha':'443daf537dc7e4ee34ab43aeb01508d9177816ab','path':'work_packages/OPENAI_TEN_PROOFS_WP00/result_family_handoffs/OTP-J1-COMPACTNESS.json','digest_algorithm':'git_blob_sha1','digest':'2d9c6e555a03b71eb33c476321e7f2d311ed168f'},
  'design_contract':{'repository':'grandchallenge/MATHCERT','commit_sha':'9f5ec626306092a352aa5ba8d9920b6ddb11b8bb','path':'governance/result_family_adjudication_contracts/OTP-J1-COMPACTNESS.json','digest_algorithm':'git_blob_sha1','digest':BLOBS['contract']},
  'prior_replay_evidence':{'repository':'grandchallenge/MATHCERT','commit_sha':'563c29c9687aad1bd06330436e3056cce7745c93','path':'governance/result_family_replay_evidence/OTP-J1-COMPACTNESS.json','digest_algorithm':'git_blob_sha1','digest':BLOBS['prior']},
  'route_registry':{'repository':'grandchallenge/MATHCERT','commit_sha':BASE,'path':'governance/certification_routes.json','digest_algorithm':'git_blob_sha1','digest':BLOBS['routes']},
  'execution_candidate':{'repository':'grandchallenge/MATHCERT','commit_sha':CAND_COMMIT,'path':'governance/result_family_evidence_refresh_execution_candidates/OTP-J1-COMPACTNESS.json','digest_algorithm':'git_blob_sha1','digest':BLOBS['candidate']}}
 if auth!=exact_auth:e.append('protected authority chain drift')
 if blob('9f5ec626306092a352aa5ba8d9920b6ddb11b8bb',PATHS['contract'])!=BLOBS['contract']:e.append('historical design-contract blob drift')
 if blob('563c29c9687aad1bd06330436e3056cce7745c93',PATHS['prior'])!=BLOBS['prior']:e.append('historical prior-replay blob drift')
 if blob(BASE,PATHS['routes'])!=BLOBS['routes']:e.append('protected route-registry blob drift')
 ce=candidate.get('execution',{})
 if ce.get('state')!='artifact_ingested_evidence_refresh_nonadjudicative':e.append('execution candidate is not closed by artifact ingestion')
 if ce.get('execution_head')!=EXEC:e.append('execution candidate head drift')
 if ce.get('artifact')!={'id':ART,'name':'otp-compactness-refresh-evidence','bytes':SIZE,'sha256':ART_SHA}:e.append('execution candidate artifact receipt drift')
 boundary={'route_state':'submitted','may_adjudicate':False,'adjudication':None,'cert_output':None,'mathematical_target_proved':False,'may_promote_claim':False,'aggregate_output':False}
 if candidate.get('required_state')!=boundary:e.append('execution candidate state boundary drift')
 if contract.get('contract_id')!='MC-OTP-ADJUDICATION-CONTRACT-J1-COMPACTNESS' or contract.get('contract_state')!='design_only':e.append('design contract identity or state drift')
 cs=contract.get('state',{})
 if cs.get('may_adjudicate') is not False or cs.get('adjudication') is not None:e.append('design contract prematurely adjudicates')
 if cs.get('cert_output') is not None or cs.get('mathematical_target_proved') is not False:e.append('design contract output or proof promotion')
 if prior.get('evidence_id')!='MC-OTP-EVIDENCE-J1-COMPACTNESS' or prior.get('route_state',{}).get('may_adjudicate') is not False:e.append('prior replay identity or boundary drift')
 if len(decoded_bundle)!=SIZE or hashlib.sha256(decoded_bundle).hexdigest()!=ART_SHA:e.append('decoded evidence bundle digest drift')
 ex=record.get('execution',{}); art=ex.get('artifact',{})
 if art!={'id':ART,'name':'otp-compactness-refresh-evidence','bytes':SIZE,'sha256':ART_SHA}:e.append('workflow artifact receipt drift')
 if (ex.get('execution_head'),ex.get('workflow_run_id'),ex.get('job_id'))!=(EXEC,RUN,JOB):e.append('record execution receipt drift')
 rb=ex.get('repository_bundle',{})
 if (rb.get('encoded_git_blob_sha1'),rb.get('decoded_bytes'),rb.get('decoded_sha256'))!=(BLOBS['bundle'],SIZE,ART_SHA):e.append('repository bundle receipt drift')
 if set(bundle_files)!=FILES:e.append('evidence bundle file membership drift')
 sums={}
 for line in bundle_files.get('SHA256SUMS',b'').decode(errors='replace').splitlines():
  p=line.split('  ',1)
  if len(p)==2:sums[p[1]]=p[0]
  else:e.append('invalid SHA256SUMS line')
 for n,p in bundle_files.items():
  if n!='SHA256SUMS' and sums.get(n)!=hashlib.sha256(p).hexdigest():e.append(f'bundle checksum drift: {n}')
 actual=[{'name':n,'bytes':len(p),'sha256':hashlib.sha256(p).hexdigest()} for n,p in sorted(bundle_files.items())]
 if rb.get('files')!=actual:e.append('repository bundle file inventory drift')
 try:summary=parse(bundle_files,'evidence-summary.json');axioms=parse(bundle_files,'axiom-check.json');authority=parse(bundle_files,'authority-receipt.json')
 except Exception as x:e.append(str(x));summary={};axioms={};authority={}
 sx=summary.get('execution',{})
 if summary.get('result_family')!='OTP-J1-COMPACTNESS' or sx.get('mathcert_head_sha')!=EXEC or sx.get('isolated_family_replay') is not True or sx.get('aggregate_all_import_used') is not False:e.append('fresh replay identity or isolation drift')
 results={'challenge_build':'pass','challenge_placeholders':'expected_comparator_boundary','solution_build':'pass','comparator':'pass','lean_kernel':'accept','nanoda':'accept','theorem_axiom_report':'permitted_only','trust_boundary_scan':'clear','source_revision_concordance':'blocked_pending_forge_audit'}
 if summary.get('results')!=results:e.append('fresh replay result drift')
 if summary.get('targets',{}).get('theorem_names')!=THEOREMS:e.append('fresh replay theorem membership drift')
 if summary.get('targets',{}).get('nonvacuity_witnesses')!=WITNESSES:e.append('fresh replay nonvacuity witness drift')
 if summary.get('source_revision',{}).get('current_revision_semantic_concordance')!='pending':e.append('raw replay source-revision status was retrospectively rewritten')
 if axioms.get('permitted')!=AXIOMS or [x.get('theorem') for x in axioms.get('reports',[])]!=THEOREMS:e.append('theorem axiom report membership drift')
 for x in axioms.get('reports',[]):
  if x.get('axioms')!=AXIOMS or x.get('unexpected')!=[]:e.append('unexpected theorem axiom report')
 if authority.get('mathcert_execution_head')!=EXEC or authority.get('official_subject')!={'commit':'e62211d28e3a9131950c89caa6542cfe5eff3bca','tree':'2f8e7ac5ae7f157b6b1de636c2c343b1c7a7e365'}:e.append('authority receipt identity drift')
 af=authority.get('forge',{}); so=authority.get('solve',{})
 if af.get('semantic_commit')!='cb0a203c36a9ef33270d62ab369df7bc27d3b242' or af.get('source_revision_commit')!='a498ef40b7652b55bf121b5682604e259b8d3073' or af.get('semantic_record',{}).get('blob')!='659396358d0d999c00011645f72602f30ccf6b0e' or af.get('source_revision_audit',{}).get('blob')!='80d473b1b545fd9ca05fc5200bcf70ff5f9fcb05':e.append('Forge authority receipt drift')
 if so.get('commit')!='443daf537dc7e4ee34ab43aeb01508d9177816ab' or so.get('producer_packet',{}).get('blob')!='2d9c6e555a03b71eb33c476321e7f2d311ed168f':e.append('Solve authority receipt drift')
 if authority.get('source_locus')!={'chapter':10,'theorem':'Theorem 1.1','pdf_page_index':236,'printed_page':235} or authority.get('current_revision_locus_concordance')!='clear_after_protected_forge_activation':e.append('source-locus receipt drift')
 if authority.get('whole_document_byte_equivalence')!='not_established' or authority.get('whole_document_semantic_equivalence')!='not_established' or authority.get('proof_body_compared_in_full') is not False:e.append('whole-document or proof-body limitation drift')
 rm={x.get('campaign_id'):x for x in routes.get('routes',[])}; cr=rm.get('OTP-J1-COMPACTNESS',{})
 if cr.get('intake_status')!='submitted':e.append('Compactness route state inflation')
 if cr.get('cert_output') is not None:e.append('Compactness Cert output inserted')
 if other_adjudication_present:e.append('Compactness adjudication inserted')
 if output_candidate_present:e.append('Compactness output candidate inserted')
 state=record.get('current_state',{})
 if state.get('families')!=FAMILIES:e.append('OTP family state drift')
 for k,v in boundary.items():
  if state.get(k)!=v:e.append(f'current state drift: {k}')
 review=record.get('obligation_review',{})
 for k in ('corrected_cyclic_family_formulation','finite_graph_orientation_and_embeddings','connectedness_and_bipartiteness','cyclicity_and_family_nonemptiness','exponents','finite_family_uniform_constant_interpretation'):
  if review.get(k,{}).get('status')!='clear_from_protected_semantic_and_fresh_replay_evidence':e.append(f'obligation status drift: {k}')
 if review.get('explicit_construction_nonvacuity',{}).get('status')!='encoded_nonvacuity_clear_source_construction_not_independently_certified':e.append('explicit-construction nonvacuity boundary drift')
 if review.get('asymptotic_interpretation',{}).get('status')!='not_independently_certified':e.append('asymptotic interpretation boundary drift')
 disp=record.get('disposition',{})
 if disp.get('ready_to_request_adjudication') is not False:e.append('adjudication readiness inflation')
 if disp.get('construction_and_interpretation')!='not_independently_certified':e.append('construction/interpretation disposition drift')
 if len(disp.get('blockers',[]))<2:e.append('required blockers were removed')
 cb=str(record.get('claim_boundary',''))
 for t in ('does not adjudicate or qualify Compactness','explicit combinatorial construction','asymptotic interpretation','mathematical_target_proved','whole-document','aggregate ten-proofs authority','commercial claims'):
  if t not in cb:e.append(f'claim boundary missing token: {t}')
 return e

def main()->int:
 try:e=validation_errors()
 except Exception as x:print(f'Compactness evidence-refresh validation failed: {x}',file=sys.stderr);return 1
 if e:print('\n'.join(e),file=sys.stderr);print(f'Compactness evidence-refresh validation failed with {len(e)} error(s)',file=sys.stderr);return 1
 print('validated non-adjudicative Compactness evidence refresh; construction and asymptotic interpretation remain open');return 0
if __name__=='__main__':raise SystemExit(main())
