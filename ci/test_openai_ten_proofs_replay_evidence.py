from __future__ import annotations
import copy,importlib.util,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];S=importlib.util.spec_from_file_location('v',ROOT/'ci/validate_openai_ten_proofs_replay_evidence.py');assert S and S.loader;M=importlib.util.module_from_spec(S);S.loader.exec_module(M)
class T(unittest.TestCase):
 def setUp(self):self.r={p.stem:json.loads(p.read_text()) for p in M.RECORD_ROOT.glob('*.json')};self.g=json.loads(M.REGISTRY.read_text());self.e=json.loads(M.EXECUTION.read_text());self.routes=json.loads(M.ROUTES.read_text())
 def errors(self,**k):return M.validation_errors(records=copy.deepcopy(k.get('records',self.r)),registry=copy.deepcopy(k.get('registry',self.g)),execution=copy.deepcopy(k.get('execution',self.e)),routes=copy.deepcopy(k.get('routes',self.routes)))
 def test_current(self):self.assertEqual(self.errors(),[])
 def test_missing(self):r=copy.deepcopy(self.r);r.pop('OTP-F-EHRHART');self.assertTrue(self.errors(records=r))
 def test_artifact_drift(self):r=copy.deepcopy(self.r);r['OTP-J1-COMPACTNESS']['execution_authority']['artifact']['sha256']='0'*64;self.assertTrue(self.errors(records=r))
 def test_bundle_drift(self):r=copy.deepcopy(self.r);r['OTP-J2-TWO-DEGENERATE']['repository_bundle']['decoded_sha256']='0'*64;self.assertTrue(self.errors(records=r))
 def test_route_inflation(self):r=copy.deepcopy(self.r);r['OTP-F-EHRHART']['route_state']['may_adjudicate']=True;self.assertTrue(self.errors(records=r))
 def test_review_forgery(self):r=copy.deepcopy(self.r);r['OTP-J1-COMPACTNESS']['review_state']['specialist_review']={'reviewer':'author'};self.assertTrue(self.errors(records=r))
 def test_registry_inflation(self):r=copy.deepcopy(self.g);r['state']['registered_route_count']=3;self.assertTrue(self.errors(registry=r))
 def test_execution_regression(self):r=copy.deepcopy(self.e);r['execution_state']['completed_family_count']=0;self.assertTrue(self.errors(execution=r))
 def test_route_registration(self):r=copy.deepcopy(self.routes);r['routes'].append({'route_id':'MC-ROUTE-OTP-F-EHRHART'});self.assertTrue(self.errors(routes=r))
if __name__=='__main__':unittest.main()
