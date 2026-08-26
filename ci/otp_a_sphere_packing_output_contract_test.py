from __future__ import annotations
import copy, importlib.util, json, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"ci"))
P=ROOT/"ci/otp_a_sphere_packing_output_contract.py"
spec=importlib.util.spec_from_file_location("v",P); v=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(v)
R=json.loads((ROOT/"governance/result_family_output_contracts/OTP-A-SPHERE-PACKING.json").read_text())
S=json.loads((ROOT/"schemas/otp_a_sphere_packing_output_contract.schema.json").read_text())
F=json.loads((ROOT/"schemas/otp_a_sphere_packing_qualified_output.schema.json").read_text())
class T(unittest.TestCase):
 def e(self,r=None,s=None,f=None): return v.validation_errors(R if r is None else r,S if s is None else s,F if f is None else f)
 def test_baseline(self): self.assertEqual([],self.e())
 def test_output_insertion(self):
  r=copy.deepcopy(R); r["state"]["cert_output"]={"x":1}; r["state"]["may_issue_output"]=True; self.assertTrue(self.e(r))
 def test_route_transition(self):
  r=copy.deepcopy(R); r["state"]["route_state"]="qualified"; self.assertTrue(self.e(r))
 def test_target_inflation(self):
  r=copy.deepcopy(R); r["output_scope"]["encoded_targets"].append("Other.target"); self.assertTrue(self.e(r))
 def test_classification_collapse(self):
  r=copy.deepcopy(R); r["output_scope"]["classifications"][1]=r["output_scope"]["classifications"][0]; self.assertTrue(self.e(r))
 def test_decimal_inflation(self):
  r=copy.deepcopy(R); r["state"]["manuscript_decimal_precision_attributed"]=True; self.assertTrue(self.e(r))
 def test_normalization_erasure(self):
  r=copy.deepcopy(R); r["state"]["scale_normalization_boundary_required"]=False; self.assertTrue(self.e(r))
 def test_little_o_strengthening(self):
  r=copy.deepcopy(R); r["state"]["little_o_strengthened"]=True; self.assertTrue(self.e(r))
 def test_composite_verbatim_inflation(self):
  r=copy.deepcopy(R); r["state"]["composite_is_single_verbatim_source_theorem"]=True; self.assertTrue(self.e(r))
 def test_proof_promotion(self):
  r=copy.deepcopy(R); r["future_certificate"]["mathematical_target_proved"]=True; self.assertTrue(self.e(r))
 def test_aggregate(self):
  r=copy.deepcopy(R); r["state"]["aggregate_output"]=True; self.assertTrue(self.e(r))
 def test_squash_permission(self):
  r=copy.deepcopy(R); r["publication_protocol"]["squash_merge_prohibited"]=False; self.assertTrue(self.e(r))
 def test_route_first(self):
  r=copy.deepcopy(R); r["publication_protocol"]["route_first_ordering_prohibited"]=False; self.assertTrue(self.e(r))
 def test_axiom_drift(self):
  r=copy.deepcopy(R); r["qualification_semantics"]["permitted_axioms"].append("sorryAx"); self.assertTrue(self.e(r))
 def test_top_level_schema_opened(self):
  s=copy.deepcopy(S); s["additionalProperties"]=True; self.assertTrue(self.e(s=s))
 def test_nested_schema_opened(self):
  s=copy.deepcopy(S); s["properties"]["protected_authority"]["properties"]["adjudication"]["additionalProperties"]=True; self.assertTrue(self.e(s=s))
 def test_nested_authority_injection(self):
  r=copy.deepcopy(R); r["protected_authority"]["adjudication"]["invented_authority"]=True; self.assertTrue(self.e(r))
 def test_nested_control_plan_injection(self):
  r=copy.deepcopy(R); r["protected_authority"]["control_plan"]["waive_review"]=True; self.assertTrue(self.e(r))
 def test_publication_protocol_injection(self):
  r=copy.deepcopy(R); r["publication_protocol"]["squash_if_convenient"]=True; self.assertTrue(self.e(r))
 def test_execution_gate_injection(self):
  r=copy.deepcopy(R); r["execution_gate"]["self_approve"]=True; self.assertTrue(self.e(r))
 def test_qualification_extra_field(self):
  r=copy.deepcopy(R); r["qualification_semantics"]["unbounded_scope"]=True; self.assertTrue(self.e(r))
 def test_future_schema_opened(self):
  f=copy.deepcopy(F); f["properties"]["qualification"]["additionalProperties"]=True; self.assertTrue(self.e(f=f))
 def test_future_target_inflation_schema(self):
  f=copy.deepcopy(F); f["properties"]["encoded_targets"]["const"].append("Other.target"); self.assertTrue(self.e(f=f))
 def test_future_proof_promotion_schema(self):
  f=copy.deepcopy(F); f["properties"]["state"]["properties"]["mathematical_target_proved"]["const"]=True; self.assertTrue(self.e(f=f))
if __name__=="__main__": unittest.main()
