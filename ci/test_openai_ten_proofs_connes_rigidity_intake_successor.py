from __future__ import annotations
import copy, importlib.util, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("validator",ROOT/"ci/validate_openai_ten_proofs_connes_rigidity_intake_successor.py")
assert SPEC and SPEC.loader
MODULE=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(MODULE)
class ConnesRigidityIntakeSuccessorTests(unittest.TestCase):
    def setUp(self): self.record=MODULE.load_json(MODULE.RECORD)
    def errors(self,record=None,*,legacy_file_exists=False): return MODULE.validation_errors(copy.deepcopy(self.record if record is None else record),legacy_file_exists=legacy_file_exists)
    def test_current_record_passes(self): self.assertEqual(self.errors(),[])
    def test_producer_drift_rejected(self):
        x=copy.deepcopy(self.record); x["authority"]["producer_packet"]["digest"]="0"*40; self.assertTrue(self.errors(x))
    def test_predecessor_name_inflation_rejected(self):
        x=copy.deepcopy(self.record); x["target_scope"]["lean_theorems"].append("ConnesRigidity2.fake"); self.assertTrue(self.errors(x))
    def test_mathlib_pin_drift_rejected(self):
        x=copy.deepcopy(self.record); x["authority"]["official_subject"]["mathlib_finite_generation_commit"]="0"*40; self.assertTrue(self.errors(x))
    def test_route_registration_rejected(self):
        x=copy.deepcopy(self.record); x["state"]["route_registered"]=True; self.assertTrue(self.errors(x))
    def test_historical_namespace_insertion_rejected(self): self.assertTrue(self.errors(legacy_file_exists=True))
if __name__=="__main__": unittest.main()
