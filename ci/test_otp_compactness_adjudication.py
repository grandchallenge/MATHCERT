#!/usr/bin/env python3
from __future__ import annotations
import copy, importlib.util, json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('control',ROOT/'ci/validate_otp_compactness_adjudication.py')
control=importlib.util.module_from_spec(SPEC); assert SPEC.loader; SPEC.loader.exec_module(control)
BASE=json.loads((ROOT/'governance/result_family_adjudications/OTP-J1-COMPACTNESS.json').read_text())
RAW=__import__('base64').b64decode((ROOT/'evidence/openai_ten_proofs/compactness_adjudication.zip.b64').read_text())
class T(unittest.TestCase):
 def reject(self,fn):
  r=copy.deepcopy(BASE); fn(r)
  with self.assertRaises(Exception): control.validate_record(r,check_repository=False,bundle_bytes=RAW)
 def test_baseline(self): control.validate_record(copy.deepcopy(BASE),check_repository=True,bundle_bytes=RAW)
 def test_target_omission(self): self.reject(lambda r:r['encoded_targets'].pop())
 def test_other_family_target(self): self.reject(lambda r:r['encoded_targets'].append('TwoDegenerateGraphs.not_erdos_146'))
 def test_disposition_inflation(self): self.reject(lambda r:r['decision'].__setitem__('disposition','qualified'))
 def test_authorization_head_substitution(self): self.reject(lambda r:r['authority']['human_steward_execution_authorization'].__setitem__('authorized_input_head','0'*40))
 def test_authorization_comment_substitution(self): self.reject(lambda r:r['authority']['human_steward_execution_authorization'].__setitem__('comment_id',1))
 def test_mirror_commit_substitution(self): self.reject(lambda r:r['execution']['transport_recovery'].__setitem__('mirror_commit','0'*40))
 def test_mirror_role_inflation(self): self.reject(lambda r:r['execution']['transport_recovery'].__setitem__('mirror_role','new_subject_authority'))
 def test_source_drift(self): self.reject(lambda r:r['source_assessment'].__setitem__('current_sha256','0'*64))
 def test_whole_document_inflation(self): self.reject(lambda r:r['source_assessment'].__setitem__('whole_document_semantic_equivalence','established'))
 def test_proof_body_inflation(self): self.reject(lambda r:r['evidence_assessment'].__setitem__('proof_body_compared_in_full',True))
 def test_route_transition(self): self.reject(lambda r:r['state'].__setitem__('route_state','qualified'))
 def test_output_insertion(self): self.reject(lambda r:r['state'].__setitem__('cert_output',{}))
 def test_proof_promotion(self): self.reject(lambda r:r['state'].__setitem__('mathematical_target_proved',True))
 def test_aggregate_adjudication(self): self.reject(lambda r:r['state'].__setitem__('aggregate_adjudication',True))
 def test_review_prepopulation(self): self.reject(lambda r:r['review_gate'].__setitem__('recorded_review',{'state':'APPROVED'}))
 def test_extra_field(self): self.reject(lambda r:r.__setitem__('unexpected',True))
 def test_bundle_corruption(self):
  with self.assertRaises(Exception): control.validate_record(copy.deepcopy(BASE),check_repository=False,bundle_bytes=RAW[:-1]+b'0')
if __name__=='__main__': unittest.main()
