from __future__ import annotations
import copy,importlib.util,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];S=importlib.util.spec_from_file_location("m",ROOT/"ci/validate_openai_ten_proofs_certification_work_packages.py");M=importlib.util.module_from_spec(S);S.loader.exec_module(M)
class T(unittest.TestCase):
 def setUp(self):self.r=json.loads(M.REGISTRY_PATH.read_text());self.p={p.stem.replace("-CERT-WP01",""):json.loads(p.read_text()) for p in M.PACKAGE_DIR.glob("*.json")};self.b={p.stem.replace("-CERT-WP01",""):M.blob(p) for p in M.PACKAGE_DIR.glob("*.json")}
 def errors(self,**k):return M.validation_errors(registry=copy.deepcopy(k.get("registry",self.r)),packages=copy.deepcopy(k.get("packages",self.p)),package_blobs=copy.deepcopy(k.get("blobs",self.b)))
 def test_current(self):self.assertEqual(self.errors(),[])
 def test_missing(self):p=copy.deepcopy(self.p);p.pop("OTP-F-EHRHART");self.assertTrue(self.errors(packages=p))
 def test_intake_drift(self):p=copy.deepcopy(self.p);p["OTP-J1-COMPACTNESS"]["authority"]["intake_record"]["digest"]="0"*40;self.assertTrue(self.errors(packages=p))
 def test_tracker_drift(self):p=copy.deepcopy(self.p);p["OTP-J2-TWO-DEGENERATE"]["tracker_issue"]="bad";self.assertTrue(self.errors(packages=p))
 def test_execution_disable(self):p=copy.deepcopy(self.p);p["OTP-F-EHRHART"]["execution"]["allowed"]=False;self.assertTrue(self.errors(packages=p))
 def test_aggregate_dependency(self):p=copy.deepcopy(self.p);p["OTP-J1-COMPACTNESS"]["execution"]["aggregate_import_required"]=True;self.assertTrue(self.errors(packages=p))
 def test_historical_route_inflation(self):p=copy.deepcopy(self.p);p["OTP-J2-TWO-DEGENERATE"]["route_state"]["may_adjudicate"]=True;self.assertTrue(self.errors(packages=p))
 def test_blob_drift(self):b=copy.deepcopy(self.b);b["OTP-J2-TWO-DEGENERATE"]="0"*40;self.assertTrue(self.errors(blobs=b))
 def test_registry_inflation(self):r=copy.deepcopy(self.r);r["execution_state"]["adjudication_count"]=1;self.assertTrue(self.errors(registry=r))
 def test_blocker_removal(self):r=copy.deepcopy(self.r);r["blocked_repair_lanes"]=["OTP-C-PERMANENT"];self.assertTrue(self.errors(registry=r))
if __name__=="__main__":unittest.main()
