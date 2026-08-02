#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'governance/result_family_route_proposals';R=ROOT/'governance/pre_route_candidates/OPENAI_TEN_PROOFS_WP05_ROUTE_PROPOSALS.json';G=ROOT/'governance/certification_routes.json'
S=[ROOT/'schemas/openai_ten_proofs_route_proposal.schema.json',ROOT/'schemas/openai_ten_proofs_route_proposal_registry.schema.json']
RB='5b3e8d48b9f6c5b03ed3dc439bf9e43876e017b1';TRACK='https://github.com/grandchallenge/MATHCERT/issues/53'
MER={'solve_handoff_merge':'443daf537dc7e4ee34ab43aeb01508d9177816ab','forge_semantic_merge':'cb0a203c36a9ef33270d62ab369df7bc27d3b242','cert_intake_merge':'d99d2625ee838945087a91a50923cddc2dcc8d85','cert_work_package_merge':'677a58a126145977581050bcb5d12d5b6a99fb51','cert_replay_evidence_merge':'563c29c9687aad1bd06330436e3056cce7745c93'}
SUB={'repository':'openai/ten-proofs','commit':'e62211d28e3a9131950c89caa6542cfe5eff3bca','tree':'2f8e7ac5ae7f157b6b1de636c2c343b1c7a7e365','archive_sha256':'3022e62ffbed8f5f74d232034a703dc645e6b301879dff1e87df72979914294f'}
AUD={'repository':'grandchallenge/MATHFORGE','commit_sha':'a498ef40b7652b55bf121b5682604e259b8d3073','path':'sources/OPENAI-TEN-PROOFS-001/source_revision_audits/OTP-TRANCHE-001.json','digest_algorithm':'git_blob_sha1','digest':'80d473b1b545fd9ca05fc5200bcf70ff5f9fcb05'}
MAN={'repository':'grandchallenge/MATHFORGE','commit_sha':'0ea98866de3066e6a44ea1ca2cf93ade8a9e1c15','path':'provider_manifests/OPENAI-TEN-PROOFS-001.json','digest_algorithm':'git_blob_sha1','digest':'fe1dab478e4ef9d6ddfe1b94a289fe7b51f58472'}
E={
'OTP-F-EHRHART':('F-EHRHART','4653985d4980113514266c3c421804437bacb019','a3dc4de4c38a80b7aec1fae6506b08e14d2e58bb','1c6a5f349803bba09b000ceb3f8a53ee3038ca48','056149e7a659fb6b24b7d7389a3dcd68bb581bcd','d17d36d02f6505060f5a9e5f1f71f3c323fa1af8','ehrhart','346eebb415609e6e66a9cb04510b7ba4994cf309','22fcaad533db94c03569439bb41fcda68618386826abd3aa624bbf90e9345adb',8,'Theorem 1.1',219,218),
'OTP-J1-COMPACTNESS':('J1-COMPACTNESS','2d9c6e555a03b71eb33c476321e7f2d311ed168f','659396358d0d999c00011645f72602f30ccf6b0e','d08eec02d7ee44f3bc2692cf7949c70d8e0f2bbf','d80cade6d99c7ca54f4384a68e178b2f4335a8b2','5fe635510a0d2aa05da641e342078cf8b2b34aa6','compactness','0f2a8918e669734ab89ece34b3f6dc60774552e2','852d0fa51a328199e6aeaf67a51fdd384ab30ec62ef6a7e28c5e22e597b3a99b',10,'Theorem 1.1',236,235),
'OTP-J2-TWO-DEGENERATE':('J2-TWO-DEGENERATE','0d226492bf13e13bc1a437be01104db3d4c96f79','7bd168c46921f64364b20021b6315d68f0fde7d0','6e9cfee8f988e357aabdd53e2883220d170b7e60','dbbc4ab59f21b3f5cb2f313c51f754b9b306389c','215ce18b4139159c89d167ab11cab6c35d5a38ff','two-degenerate','14d050b03ccc9891f8c3e5ec4f522aa5aa00b8aa','b3efb532152677dd84c0872071a9d2aa061ea56b9a8a7d9175c6382766f27ed4',10,'Theorem 1.2',236,235)}
PK={'schema_version','record_type','proposal_id','candidate_id','result_family','requested_route_id','proposal_state','tracker_issue','authority','source_scope','evidence_disposition','route_controls','activation','claim_boundary'}
AK={'official_subject','solve_handoff_merge','producer_packet','forge_semantic_merge','semantic_record','cert_intake_merge','cert_intake','cert_work_package_merge','cert_work_package','cert_replay_evidence_merge','replay_evidence','repository_bundle','source_revision_audit','provider_manifest'}
SK={'source_theorem','current_revision_locus','normalized_statement','lean_theorems','nonvacuity_witnesses','scope_exclusions'}
D={'kernel_replay':'clear','lean_kernel':'accept','nanoda':'accept','theorem_axiom_report':'permitted_only','trust_boundary_scan':'clear','source_semantic':'clear','nonvacuity':'clear','current_revision_locus':'clear','whole_document_byte_equivalence':'not_established','whole_document_semantic_equivalence':'not_established','proof_body_compared_in_full':False}
C={'global_registered_route_registry_modified':False,'route_registry_entry':None,'may_register_route':False,'may_adjudicate':False,'cert_output':None,'mathematical_target_proved':False,'may_promote_claim':False,'aggregate_route':False,'aggregate_adjudication':False}
A={'condition':'exact-head Cert checks, GCL conformance, non-author APPROVED specialist review, explicit exact-head Human Steward disposition, and protected MATHCERT merge','head_change_requires_reapproval':True,'effect':'route_proposal_admitted_no_registration_no_adjudication'}
def load(p):return json.loads(p.read_text())
def blob(p):
 b=p.read_bytes();return hashlib.sha1(f'blob {len(b)}\0'.encode()+b,usedforsecurity=False).hexdigest()
def art(repo,commit,path,digest):return {'repository':repo,'commit_sha':commit,'path':path,'digest_algorithm':'git_blob_sha1','digest':digest}
def closed_schema(v):
 out=[]
 def w(x,p=''):
  if isinstance(x,dict):
   if x.get('type')=='object' and x.get('additionalProperties') is not False:out.append(p)
   for k,y in x.items():w(y,p+'/'+k)
  elif isinstance(x,list):
   for i,y in enumerate(x):w(y,p+'/'+str(i))
 w(v);return out
def validation_errors(proposals=None,registry=None,routes=None,local_blobs=None):
 e=[]
 for s in S:
  if closed_schema(load(s)):e.append(f'{s.name}: open object schema')
 proposals={x.stem:load(x) for x in P.glob('*.json')} if proposals is None else proposals
 registry=load(R) if registry is None else registry;routes=load(G) if routes is None else routes
 if set(proposals)!=set(E):e.append('proposal membership drift')
 refs=[];requested=set()
 for fam,x in E.items():
  slug,pb,sb,ib,wb,eb,bslug,bb,bsha,ch,th,pp,pr=x;q=proposals.get(fam)
  if not isinstance(q,dict):continue
  if set(q)!=PK:e.append(f'{fam}: fields drift')
  pid=f'MC-OTP-ROUTE-PROPOSAL-{slug}';rid=f'MC-ROUTE-OTP-{slug}';requested.add(rid)
  if (q.get('schema_version'),q.get('record_type'),q.get('proposal_id'),q.get('candidate_id'),q.get('result_family'),q.get('requested_route_id'),q.get('proposal_state'),q.get('tracker_issue'))!=('1.0.0','openai_ten_proofs_result_family_route_proposal',pid,'OPENAI-TEN-PROOFS-001',fam,rid,'proposed_only',TRACK):e.append(f'{fam}: proposal identity/state drift')
  au=q.get('authority',{})
  if set(au)!=AK or au.get('official_subject')!=SUB:e.append(f'{fam}: authority shape/subject drift')
  for k,v in MER.items():
   if au.get(k)!=v:e.append(f'{fam}: {k} drift')
  sp=f'work_packages/OPENAI_TEN_PROOFS_WP00/result_family_handoffs/{fam}.json';sem=f'sources/OPENAI-TEN-PROOFS-001/semantic_audits/{fam}.json';ip=f'governance/result_family_intakes/{fam}.json';wp=f'governance/result_family_work_packages/{fam}-CERT-WP01.json';ep=f'governance/result_family_replay_evidence/{fam}.json';bp=f'evidence/openai_ten_proofs/{bslug}.zip.b64'
  expected={'producer_packet':art('grandchallenge/MATHSOLVE',MER['solve_handoff_merge'],sp,pb),'semantic_record':art('grandchallenge/MATHFORGE',MER['forge_semantic_merge'],sem,sb),'cert_intake':art('grandchallenge/MATHCERT',MER['cert_intake_merge'],ip,ib),'cert_work_package':art('grandchallenge/MATHCERT',MER['cert_work_package_merge'],wp,wb),'replay_evidence':art('grandchallenge/MATHCERT',MER['cert_replay_evidence_merge'],ep,eb)}
  for k,v in expected.items():
   if au.get(k)!=v:e.append(f'{fam}: {k} drift')
  bun=art('grandchallenge/MATHCERT',MER['cert_replay_evidence_merge'],bp,bb);bun['decoded_sha256']=bsha
  if au.get('repository_bundle')!=bun:e.append(f'{fam}: bundle drift')
  if au.get('source_revision_audit')!=AUD or au.get('provider_manifest')!=MAN:e.append(f'{fam}: Forge revision authority drift')
  actual={p:blob(ROOT/p) for p in (ip,wp,ep,bp)} if local_blobs is None else local_blobs
  for p,h in ((ip,ib),(wp,wb),(ep,eb),(bp,bb)):
   if actual.get(p)!=h:e.append(f'{fam}: local blob drift {p}')
  sc=q.get('source_scope',{});intake=load(ROOT/ip).get('target_scope',{})
  if set(sc)!=SK:e.append(f'{fam}: source scope fields drift')
  for k in ('source_theorem','normalized_statement','lean_theorems','nonvacuity_witnesses'):
   if sc.get(k)!=intake.get(k):e.append(f'{fam}: protected intake scope drift {k}')
  if sc.get('current_revision_locus')!={'chapter':ch,'theorem':th,'pdf_page_index':pp,'printed_page':pr,'concordance':'clear_at_recorded_locus'}:e.append(f'{fam}: current-revision locus drift')
  ex=sc.get('scope_exclusions',[])
  token={'OTP-F-EHRHART':'classification','OTP-J1-COMPACTNESS':'construction','OTP-J2-TWO-DEGENERATE':'coloring'}[fam]
  if not isinstance(ex,list) or not any(token in str(z) for z in ex):e.append(f'{fam}: family exclusion removed')
  if q.get('evidence_disposition')!=D:e.append(f'{fam}: evidence inflation')
  if q.get('route_controls')!=C:e.append(f'{fam}: route/adjudication/output/proof inflation')
  if q.get('activation')!=A:e.append(f'{fam}: activation drift')
  claim=str(q.get('claim_boundary',''))
  if not all(z in claim for z in ('does not register','adjudicate','Cert output','aggregate')):e.append(f'{fam}: claim boundary drift')
  path=P/f'{fam}.json'
  if path.is_file():refs.append({'result_family':fam,'proposal_id':pid,'requested_route_id':rid,'path':str(path.relative_to(ROOT)),'digest_algorithm':'git_blob_sha1','digest':blob(path)})
 if blob(G)!=RB:e.append('registered-route registry changed')
 if requested & {str(z.get('route_id','')) for z in routes.get('routes',[]) if isinstance(z,dict)}:e.append('OTP route registered prematurely')
 if registry.get('authority')!={'cert_replay_evidence_merge':MER['cert_replay_evidence_merge'],'forge_source_revision_audit_merge':AUD['commit_sha'],'forge_provider_manifest_merge':MAN['commit_sha'],'source_revision_audit_blob':AUD['digest'],'provider_manifest_blob':MAN['digest'],'global_registered_route_registry_blob':RB}:e.append('registry authority drift')
 if registry.get('proposals')!=refs:e.append('registry proposal refs drift')
 if registry.get('state')!={'proposal_count':3,'registered_route_count':0,'adjudication_count':0,'cert_output_count':0,'mathematical_target_proved_count':0,'aggregate_route_count':0}:e.append('registry state inflation')
 if registry.get('blocked_repair_lanes')!=['OTP-C-PERMANENT','OTP-H-GAPCVP'] or registry.get('unexamined_result_family_count')!=9:e.append('blocked/unexamined state drift')
 if registry.get('aggregate_integration')!={'all_lean_state':'failed_namespace_collision','reopens_family_replay':False,'creates_route':False,'creates_adjudication':False}:e.append('All.lean boundary drift')
 if registry.get('route_controls')!={'global_registered_route_registry_modified':False,'proposal_registry_separate':True,'may_register_route':False,'may_adjudicate':False,'may_issue_cert_output':False,'may_mark_target_proved':False,'aggregate_route_prohibited':True,'may_promote_claim':False}:e.append('registry authority inflation')
 if registry.get('activation')!={'condition':A['condition'],'head_change_requires_reapproval':True,'effect':'three_route_proposals_admitted_no_registration_no_adjudication'}:e.append('registry activation drift')
 return e
def main():
 e=validation_errors()
 if e:print('\n'.join(e),file=sys.stderr);print(f'route proposal validation failed with {len(e)} error(s)',file=sys.stderr);return 1
 print('validated three proposed-only OTP family routes, exact content-addressed evidence, unchanged registered routes, and zero adjudication/output/proof authority');return 0
if __name__=='__main__':raise SystemExit(main())
