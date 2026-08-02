from __future__ import annotations
import copy,importlib.util,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];S=importlib.util.spec_from_file_location("v",ROOT/"ci/validate_openai_ten_proofs_replay_evidence.py");M=importlib.util.module_from_spec(S);S.loader.exec_module(M)
class T(unittest.TestCase):
 def setUp(self):self.r={p.stem:json.loads(p.read_text()) for p in M.RECORD_ROOT.glob("*.json")};self.g=json.loads(M.REGISTRY.read_text());self.b={p.stem:M.blob(p) for p in M.RECORD_ROOT.glob("*.json")};self.z={f:(ROOT/f'evidence/openai_ten_proofs/{x["bundle"]}.zip.b64').read_bytes() for f,x in M.EXPECTED.items()}
 def errors(self,**k):return M.validation_errors(records=copy.deepcopy(k.get("records",self.r)),registry=copy.deepcopy(k.get("registry",self.g)),record_blobs=copy.deepcopy(k.get("record_blobs",self.b)),bundle_bytes=copy.deepcopy(k.get("bundle_bytes",self.z)))
 def test_current(self):self.assertEqual(self.errors(),[])
 def test_missing(self):r=copy.deepcopy(self.r);r.pop("OTP-F-EHRHART");self.assertTrue(self.errors(records=r))
 def test_result_drift(self):r=copy.deepcopy(self.r);r["OTP-J1-COMPACTNESS"]["replay_results"]["nanoda"]="reject";self.assertTrue(self.errors(records=r))
 def test_historical_route_inflation(self):r=copy.deepcopy(self.r);r["OTP-F-EHRHART"]["route_state"]["may_adjudicate"]=True;self.assertTrue(self.errors(records=r))
 def test_source_state_drift(self):r=copy.deepcopy(self.r);r["OTP-J2-TWO-DEGENERATE"]["source_revision"]["current_revision_semantic_concordance"]="clear";self.assertTrue(self.errors(records=r))
 def test_record_blob_drift(self):b=copy.deepcopy(self.b);b["OTP-F-EHRHART"]="0"*40;self.assertTrue(self.errors(record_blobs=b))
 def test_bundle_drift(self):z=copy.deepcopy(self.z);z["OTP-J1-COMPACTNESS"]=z["OTP-J1-COMPACTNESS"][:-1];self.assertTrue(self.errors(bundle_bytes=z))
 def test_registry_inflation(self):g=copy.deepcopy(self.g);g["state"]["adjudication_count"]=1;self.assertTrue(self.errors(registry=g))
if __name__=="__main__":unittest.main()
