from __future__ import annotations
import copy,importlib.util,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];S=importlib.util.spec_from_file_location("v",ROOT/"ci/validate_openai_ten_proofs_route_proposals.py");M=importlib.util.module_from_spec(S);S.loader.exec_module(M)
class T(unittest.TestCase):
 def setUp(self):self.p={x.stem:json.loads(x.read_text()) for x in M.P.glob("*.json")};self.r=json.loads(M.R.read_text());self.b={x.stem:M.blob(x) for x in M.P.glob("*.json")};self.rb=M.blob(M.R)
 def errors(self,**k):return M.validation_errors(proposals=copy.deepcopy(k.get("proposals",self.p)),registry=copy.deepcopy(k.get("registry",self.r)),proposal_blobs=copy.deepcopy(k.get("proposal_blobs",self.b)),registry_blob=k.get("registry_blob",self.rb))
 def test_current(self):self.assertEqual(self.errors(),[])
 def test_missing(self):p=copy.deepcopy(self.p);p.pop("OTP-F-EHRHART");self.assertTrue(self.errors(proposals=p))
 def test_state_inflation(self):p=copy.deepcopy(self.p);p["OTP-F-EHRHART"]["proposal_state"]="registered";self.assertTrue(self.errors(proposals=p))
 def test_adjudication_inflation(self):p=copy.deepcopy(self.p);p["OTP-J1-COMPACTNESS"]["route_controls"]["may_adjudicate"]=True;self.assertTrue(self.errors(proposals=p))
 def test_whole_document_inflation(self):p=copy.deepcopy(self.p);p["OTP-J2-TWO-DEGENERATE"]["evidence_disposition"]["whole_document_semantic_equivalence"]="established";self.assertTrue(self.errors(proposals=p))
 def test_blob_drift(self):b=copy.deepcopy(self.b);b["OTP-F-EHRHART"]="0"*40;self.assertTrue(self.errors(proposal_blobs=b))
 def test_registry_inflation(self):r=copy.deepcopy(self.r);r["state"]["registered_route_count"]=3;self.assertTrue(self.errors(registry=r))
 def test_registry_blob_drift(self):self.assertTrue(self.errors(registry_blob="0"*40))
if __name__=="__main__":unittest.main()
