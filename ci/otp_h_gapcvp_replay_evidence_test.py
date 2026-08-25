from __future__ import annotations
import copy, importlib.util, json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"ci/otp_h_gapcvp_replay_evidence.py"
s=importlib.util.spec_from_file_location("v",P); v=importlib.util.module_from_spec(s); assert s and s.loader; s.loader.exec_module(v)
R=json.loads((ROOT/"governance/result_family_replay_evidence_successors/OTP-H-GAPCVP.json").read_text()); S=json.loads((ROOT/"schemas/openai_ten_proofs_gapcvp_replay_evidence.schema.json").read_text())
class T(unittest.TestCase):
 def e(self,r=None,s=None,b=None): return v.validation_errors(R if r is None else r,S if s is None else s,b,False)
 def test_baseline(self): self.assertEqual([],self.e())
 def test_target_drift(self):
  r=copy.deepcopy(R); r["target_scope"]["lean_theorems"][0]="Other.target"; self.assertTrue(self.e(r=r))
 def test_promise_drift(self):
  r=copy.deepcopy(R); r["target_scope"]["promise_interfaces"][0]="Other.promise"; self.assertTrue(self.e(r=r))
 def test_gap_drift(self):
  r=copy.deepcopy(R); r["target_scope"]["gap_factors"][0]="constant-400"; self.assertTrue(self.e(r=r))
 def test_proof_promotion(self):
  r=copy.deepcopy(R); r["route_state"]["mathematical_target_proved"]=True; self.assertTrue(self.e(r=r))
 def test_route_inflation(self):
  r=copy.deepcopy(R); r["route_state"]["route_proposed"]=True; self.assertTrue(self.e(r=r))
 def test_review_fabrication(self):
  r=copy.deepcopy(R); r["producer_replay"]["independent_review_attestation"]="approved"; self.assertTrue(self.e(r=r))
 def test_bundle_hash_drift(self):
  r=copy.deepcopy(R); r["repository_bundle"]["decoded_sha256"]="0"*64; self.assertTrue(self.e(r=r))
 def test_bundle_corruption(self): self.assertTrue(self.e(b="AAAA"))
 def test_open_schema(self):
  s=copy.deepcopy(S); s["additionalProperties"]=True; self.assertTrue(self.e(s=s))
if __name__=="__main__": unittest.main()
