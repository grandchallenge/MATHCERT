#!/usr/bin/env python3
from __future__ import annotations
import copy, importlib.util, json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'ci/validate_otp_compactness_evidence_refresh.py'
S=importlib.util.spec_from_file_location('validate_otp_compactness_evidence_refresh',P); assert S and S.loader
M=importlib.util.module_from_spec(S); S.loader.exec_module(M)

class CompactnessEvidenceRefreshTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.base=M.defaults()
 def args(self):return copy.deepcopy(self.base)
 def rejected(self,mutate,token):
  a=self.args();mutate(a);e=M.validation_errors(**a);self.assertTrue(any(token in x for x in e),e)
 def test_valid(self):self.assertEqual(M.validation_errors(**self.args()),[])
 def test_contract_substitution(self):self.rejected(lambda a:a['record']['authority']['design_contract'].__setitem__('digest','0'*40),'protected authority chain drift')
 def test_route_promotion(self):self.rejected(lambda a:a['record']['current_state'].__setitem__('route_state','qualified'),'schema violation')
 def test_adjudication_insertion(self):self.rejected(lambda a:a.__setitem__('other_adjudication_present',True),'Compactness adjudication inserted')
 def test_output_candidate(self):self.rejected(lambda a:a.__setitem__('output_candidate_present',True),'Compactness output candidate inserted')
 def test_execution_head_substitution(self):self.rejected(lambda a:a['record']['execution'].__setitem__('execution_head','0'*40),'record execution receipt drift')
 def test_artifact_digest_substitution(self):self.rejected(lambda a:a['record']['execution']['artifact'].__setitem__('sha256','0'*64),'workflow artifact receipt drift')
 def test_bundle_mutation(self):self.rejected(lambda a:a.__setitem__('decoded_bundle',a['decoded_bundle']+b'x'),'decoded evidence bundle digest drift')
 def test_theorem_membership_drift(self):
  def m(a):
   x=json.loads(a['bundle_files']['evidence-summary.json']);x['targets']['theorem_names'].pop();a['bundle_files']['evidence-summary.json']=(json.dumps(x)+'\n').encode()
  self.rejected(m,'fresh replay theorem membership drift')
 def test_unexpected_axiom(self):
  def m(a):
   x=json.loads(a['bundle_files']['axiom-check.json']);x['reports'][0]['unexpected']=['Bad.axiom'];a['bundle_files']['axiom-check.json']=(json.dumps(x)+'\n').encode()
  self.rejected(m,'unexpected theorem axiom report')
 def test_source_locus_inflation(self):self.rejected(lambda a:a['record']['source_statement'].__setitem__('current_revision_locus_concordance','whole_document_clear'),'schema violation')
 def test_construction_inflation(self):self.rejected(lambda a:a['record']['obligation_review']['explicit_construction_nonvacuity'].__setitem__('status','clear'),'explicit-construction nonvacuity boundary drift')
 def test_asymptotic_inflation(self):self.rejected(lambda a:a['record']['obligation_review']['asymptotic_interpretation'].__setitem__('status','clear'),'asymptotic interpretation boundary drift')
 def test_adjudication_readiness(self):self.rejected(lambda a:a['record']['disposition'].__setitem__('ready_to_request_adjudication',True),'adjudication readiness inflation')
 def test_blocker_removal(self):self.rejected(lambda a:a['record']['disposition'].__setitem__('blockers',[]),'required blockers were removed')
 def test_claim_boundary_weakening(self):self.rejected(lambda a:a['record'].__setitem__('claim_boundary','No claims.'),'claim boundary missing token')
 def test_protected_blob_drift(self):self.rejected(lambda a:a['blobs'].__setitem__('routes','0'*40),'protected blob drift: routes')
 def test_execution_ancestry_failure(self):self.rejected(lambda a:a['receipt'].__setitem__('exec_head',False),'Git receipt drift')
 def test_forge_authority_drift(self):
  def m(a):
   x=json.loads(a['bundle_files']['authority-receipt.json']);x['forge']['semantic_commit']='0'*40;a['bundle_files']['authority-receipt.json']=(json.dumps(x)+'\n').encode()
  self.rejected(m,'Forge authority receipt drift')
 def test_checksum_manifest_drift(self):
  def m(a):a['bundle_files']['comparator.log']+=b'x'
  self.rejected(m,'bundle checksum drift: comparator.log')

if __name__=='__main__':unittest.main()
