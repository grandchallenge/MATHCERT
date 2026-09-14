from __future__ import annotations
import copy,unittest
import validate_otp_e_connes_rigidity_certification as module
class ConnesRigidityCertificationTests(unittest.TestCase):
 def setUp(self):self.values={n:module.load(p) for n,p in {"adjudication":module.ADJUDICATION,"contract":module.CONTRACT,"certificate":module.CERTIFICATE,"work_package":module.WORK_PACKAGE,"intake":module.INTAKE,"routes":module.ROUTES}.items()}
 def errors(self,**changes):v=copy.deepcopy(self.values);v.update(changes);return module.validation_errors(**v,check_history=False)
 def test_current_candidate_passes(self):self.assertEqual([],self.errors())
 def test_target_substitution_fails(self):
  x=copy.deepcopy(self.values["certificate"]);x["encoded_targets"][0]="ConnesRigidity.fake";self.assertTrue(any("target" in e for e in self.errors(certificate=x)))
 def test_predecessor_reclassification_fails(self):
  x=copy.deepcopy(self.values["certificate"]);x["classifications"][0]="predecessor_alias";self.assertTrue(any("classification" in e for e in self.errors(certificate=x)))
 def test_proof_promotion_fails(self):
  x=copy.deepcopy(self.values["certificate"]);x["state"]["mathematical_target_proved"]=True;self.assertTrue(any("authority inflation" in e for e in self.errors(certificate=x)))
 def test_specialist_gate_removal_fails(self):
  x=copy.deepcopy(self.values["adjudication"]);x["binding_gate"]["fresh_non_author_operator_algebra_group_theory_Lean_specialist_approval_required"]=False;self.assertTrue(any("binding gate removed" in e for e in self.errors(adjudication=x)))
 def test_route_output_drift_fails(self):
  x=copy.deepcopy(self.values["routes"]);next(r for r in x["routes"] if r["campaign_id"]==module.FAMILY)["cert_output"]["digest"]="0"*40;self.assertTrue(any("output identity" in e for e in self.errors(routes=x)))
if __name__=="__main__":unittest.main()
