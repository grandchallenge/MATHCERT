from __future__ import annotations
import copy,importlib.util,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('validate_openai_ten_proofs_route_proposals',ROOT/'ci/validate_openai_ten_proofs_route_proposals.py')
assert SPEC and SPEC.loader
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)
class RouteProposalTests(unittest.TestCase):
 def setUp(self):
  self.p={x.stem:json.loads(x.read_text()) for x in sorted(M.P.glob('*.json'))};self.r=json.loads(M.R.read_text());self.g=json.loads(M.G.read_text());self.b={}
  for x in M.E.values():
   _,_,_,_,_,_,slug,_,_,_,_,_,_=x
  for fam,x in M.E.items():
   slug,pb,sb,ib,wb,eb,bslug,bb,bsha,ch,th,pp,pr=x
   for path in (f'governance/result_family_intakes/{fam}.json',f'governance/result_family_work_packages/{fam}-CERT-WP01.json',f'governance/result_family_replay_evidence/{fam}.json',f'evidence/openai_ten_proofs/{bslug}.zip.b64'):
    self.b[path]=M.blob(ROOT/path)
 def errors(self,**kw):return M.validation_errors(proposals=copy.deepcopy(kw.get('proposals',self.p)),registry=copy.deepcopy(kw.get('registry',self.r)),routes=copy.deepcopy(kw.get('routes',self.g)),local_blobs=copy.deepcopy(kw.get('local_blobs',self.b)))
 def test_current_passes(self):self.assertEqual(self.errors(),[])
 def test_missing_family(self):
  p=copy.deepcopy(self.p);p.pop('OTP-F-EHRHART');self.assertTrue(self.errors(proposals=p))
 def test_family_inflation(self):
  p=copy.deepcopy(self.p);p['OTP-A-SPHERE-PACKING']=copy.deepcopy(p['OTP-F-EHRHART']);self.assertTrue(self.errors(proposals=p))
 def test_route_state_inflation(self):
  p=copy.deepcopy(self.p);p['OTP-F-EHRHART']['proposal_state']='registered';self.assertTrue(self.errors(proposals=p))
 def test_global_route_insertion(self):
  g=copy.deepcopy(self.g);g['routes'].append({'route_id':'MC-ROUTE-OTP-F-EHRHART'});self.assertTrue(self.errors(routes=g))
 def test_adjudication_output_inflation(self):
  p=copy.deepcopy(self.p);c=p['OTP-J1-COMPACTNESS']['route_controls'];c['may_adjudicate']=True;c['cert_output']={'forged':True};self.assertTrue(self.errors(proposals=p))
 def test_proof_promotion(self):
  p=copy.deepcopy(self.p);p['OTP-J2-TWO-DEGENERATE']['route_controls']['mathematical_target_proved']=True;self.assertTrue(self.errors(proposals=p))
 def test_aggregate_route(self):
  p=copy.deepcopy(self.p);p['OTP-F-EHRHART']['route_controls']['aggregate_route']=True;self.assertTrue(self.errors(proposals=p))
 def test_whole_document_inflation(self):
  p=copy.deepcopy(self.p);p['OTP-J1-COMPACTNESS']['evidence_disposition']['whole_document_semantic_equivalence']='established';self.assertTrue(self.errors(proposals=p))
 def test_full_proof_claim(self):
  p=copy.deepcopy(self.p);p['OTP-J2-TWO-DEGENERATE']['evidence_disposition']['proof_body_compared_in_full']=True;self.assertTrue(self.errors(proposals=p))
 def test_audit_blob_drift(self):
  p=copy.deepcopy(self.p);p['OTP-F-EHRHART']['authority']['source_revision_audit']['digest']='0'*40;self.assertTrue(self.errors(proposals=p))
 def test_manifest_drift(self):
  p=copy.deepcopy(self.p);p['OTP-F-EHRHART']['authority']['provider_manifest']['commit_sha']='0'*40;self.assertTrue(self.errors(proposals=p))
 def test_semantic_drift(self):
  p=copy.deepcopy(self.p);p['OTP-J1-COMPACTNESS']['authority']['semantic_record']['digest']='0'*40;self.assertTrue(self.errors(proposals=p))
 def test_bundle_substitution(self):
  p=copy.deepcopy(self.p);p['OTP-J2-TWO-DEGENERATE']['authority']['repository_bundle']['decoded_sha256']='0'*64;self.assertTrue(self.errors(proposals=p))
 def test_local_intake_drift(self):
  b=copy.deepcopy(self.b);b['governance/result_family_intakes/OTP-F-EHRHART.json']='0'*40;self.assertTrue(self.errors(local_blobs=b))
 def test_local_work_package_drift(self):
  b=copy.deepcopy(self.b);b['governance/result_family_work_packages/OTP-J1-COMPACTNESS-CERT-WP01.json']='0'*40;self.assertTrue(self.errors(local_blobs=b))
 def test_local_evidence_drift(self):
  b=copy.deepcopy(self.b);b['governance/result_family_replay_evidence/OTP-J2-TWO-DEGENERATE.json']='0'*40;self.assertTrue(self.errors(local_blobs=b))
 def test_exclusion_removal(self):
  p=copy.deepcopy(self.p);p['OTP-J2-TWO-DEGENERATE']['source_scope']['scope_exclusions']=['narrow only'];self.assertTrue(self.errors(proposals=p))
 def test_registry_count_inflation(self):
  r=copy.deepcopy(self.r);r['state']['registered_route_count']=3;self.assertTrue(self.errors(registry=r))
 def test_registry_blob_drift(self):
  r=copy.deepcopy(self.r);r['proposals'][0]['digest']='0'*40;self.assertTrue(self.errors(registry=r))
if __name__=='__main__':unittest.main()
