import copy,importlib.util,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];S=importlib.util.spec_from_file_location('v',ROOT/'ci/validate_openai_ten_proofs_replay_execution.py');M=importlib.util.module_from_spec(S);S.loader.exec_module(M)
class T(unittest.TestCase):
 def setUp(self):self.r=json.loads(M.R.read_text())
 def test_current(self):self.assertEqual(M.validation_errors(),[])
 def test_regression(self):r=copy.deepcopy(self.r);r['execution_state']['completed_family_count']=0;self.assertTrue(M.validation_errors(record=r))
 def test_route(self):r=copy.deepcopy(self.r);r['execution_state']['registered_route_count']=3;self.assertTrue(M.validation_errors(record=r))
 def test_source(self):r=copy.deepcopy(self.r);r['source_revision']['current_revision_semantic_concordance']='clear';self.assertTrue(M.validation_errors(record=r))
 def test_route_blob(self):self.assertTrue(M.validation_errors(routes_blob='0'*40))
 def test_wp_blob(self):self.assertTrue(M.validation_errors(wp_blob='0'*40))
if __name__=='__main__':unittest.main()
