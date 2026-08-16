from __future__ import annotations
import copy,importlib.util,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
S=importlib.util.spec_from_file_location("reg",ROOT/"ci/validate_openai_ten_proofs_route_registrations_with_j2_successor.py");assert S and S.loader
M=importlib.util.module_from_spec(S);S.loader.exec_module(M)
class RouteRegistrationTests(unittest.TestCase):
 def setUp(self):
  self.r=json.loads(M.REG.read_text());self.routes=json.loads(M.ROUTES.read_text());self.preg=json.loads(M.PROPOSAL_REG.read_text());self.pb={f:M.blob(ROOT/f"governance/result_family_route_proposals/{f}.json") for f in M.EXPECTED_FAMILIES};self.rb=M.EXPECTED_ROUTE_BLOB;self.prb=M.blob(M.PROPOSAL_REG)
 def errors(self,**k):return M.validation_errors(receipt=copy.deepcopy(k.get("receipt",self.r)),routes=copy.deepcopy(k.get("routes",self.routes)),proposal_registry=copy.deepcopy(k.get("proposal_registry",self.preg)),proposal_blobs=copy.deepcopy(k.get("proposal_blobs",self.pb)),routes_blob=k.get("routes_blob",self.rb),proposal_registry_blob=k.get("proposal_registry_blob",self.prb))
 def historical_compactness_routes(self):
  routes=copy.deepcopy(self.routes);r=next(x for x in routes["routes"] if x["campaign_id"]=="OTP-J1-COMPACTNESS");r["intake_status"]="submitted";r["cert_output"]=None;r["claim_boundary"]=M.COMPACTNESS_HISTORICAL_BOUNDARY;r["blockers"]=copy.deepcopy(M.COMPACTNESS_HISTORICAL_BLOCKERS);r["reopening_conditions"]=copy.deepcopy(M.COMPACTNESS_HISTORICAL_REOPENING);return routes
 def test_current(self):self.assertEqual(self.errors(),[])
 def test_historical_compactness_snapshot_passes(self):self.assertEqual(self.errors(routes=self.historical_compactness_routes()),[])
 def test_unrelated_uc_route_evolution_is_permitted(self):
  routes=copy.deepcopy(self.routes);next(x for x in routes["routes"] if x["campaign_id"]=="UC-001")["reopening_conditions"].append("unrelated evolution");self.assertEqual(self.errors(routes=routes),[])
 def test_missing_registration(self):
  r=copy.deepcopy(self.r);r["registrations"]=r["registrations"][:-1];self.assertTrue(self.errors(receipt=r))
 def test_extra_family(self):
  r=copy.deepcopy(self.r);x=copy.deepcopy(r["registrations"][0]);x["result_family"]="OTP-A-SPHERE-PACKING";r["registrations"].append(x);self.assertTrue(self.errors(receipt=r))
 def test_proposal_drift(self):
  r=copy.deepcopy(self.r);r["registrations"][0]["proposal"]["digest"]="0"*40;self.assertTrue(self.errors(receipt=r))
 def test_route_registry_blob_drift(self):self.assertTrue(self.errors(routes_blob="0"*40))
 def test_packet_substitution(self):
  r=copy.deepcopy(self.r);r["registrations"][1]["intake_packet"]["digest"]="0"*40;self.assertTrue(self.errors(receipt=r))
 def test_state_promotion(self):
  r=copy.deepcopy(self.r);r["registrations"][2]["intake_status"]="qualified";r["registrations"][2]["cert_output"]={"forged":True};self.assertTrue(self.errors(receipt=r))
 def test_adjudication_enable(self):
  r=copy.deepcopy(self.r);r["registrations"][0]["may_adjudicate"]=True;self.assertTrue(self.errors(receipt=r))
 def test_proof_promotion(self):
  r=copy.deepcopy(self.r);r["registrations"][1]["mathematical_target_proved"]=True;self.assertTrue(self.errors(receipt=r))
 def test_aggregate_route(self):
  routes=copy.deepcopy(self.routes);x=copy.deepcopy(routes["routes"][-1]);x["campaign_id"]="OPENAI-TEN-PROOFS-001";x["route_id"]="MC-ROUTE-OPENAI-TEN-PROOFS-001";routes["routes"].append(x);self.assertTrue(self.errors(routes=routes))
 def test_route_omission(self):
  routes=copy.deepcopy(self.routes);routes["routes"]=[x for x in routes["routes"] if x["campaign_id"]!="OTP-F-EHRHART"];self.assertTrue(self.errors(routes=routes))
 def test_compactness_output_substitution(self):
  routes=copy.deepcopy(self.routes);next(x for x in routes["routes"] if x["campaign_id"]=="OTP-J1-COMPACTNESS")["cert_output"]["digest"]="0"*40;self.assertTrue(any("live successor output identity drift" in x for x in self.errors(routes=routes)))
 def test_compactness_invalid_state(self):
  routes=copy.deepcopy(self.routes);next(x for x in routes["routes"] if x["campaign_id"]=="OTP-J1-COMPACTNESS")["intake_status"]="ready";self.assertTrue(any("live successor route is not qualified" in x for x in self.errors(routes=routes)))
 def test_compactness_boundary_weakening(self):
  routes=copy.deepcopy(self.routes);next(x for x in routes["routes"] if x["campaign_id"]=="OTP-J1-COMPACTNESS")["claim_boundary"]="qualified";self.assertTrue(any("live successor boundary missing" in x for x in self.errors(routes=routes)))
 def test_output_insertion_into_historical_snapshot(self):
  routes=self.historical_compactness_routes();next(x for x in routes["routes"] if x["campaign_id"]=="OTP-J1-COMPACTNESS")["cert_output"]={"forged":True};self.assertTrue(self.errors(routes=routes))
 def test_j2_state_regression_is_rejected(self):
  routes=copy.deepcopy(self.routes);r=next(x for x in routes["routes"] if x["campaign_id"]=="OTP-J2-TWO-DEGENERATE");r["intake_status"]="submitted";r["cert_output"]=None;self.assertTrue(self.errors(routes=routes))
 def test_j2_output_substitution_is_rejected(self):
  routes=copy.deepcopy(self.routes);r=next(x for x in routes["routes"] if x["campaign_id"]=="OTP-J2-TWO-DEGENERATE");r["cert_output"]["digest"]="0"*40;self.assertTrue(any("output identity drift" in x.lower() for x in self.errors(routes=routes)))
 def test_j2_mixed_target_successor_is_rejected(self):
  routes=copy.deepcopy(self.routes);next(x for x in routes["routes"] if x["campaign_id"]=="OTP-J2-TWO-DEGENERATE")["target_claim_ids"]=["TwoDegenerateGraphs.mathcert_sourceFaithfulTwoDegenerateExtremalCounterexample","TwoDegenerateGraphs.not_erdos_146"];self.assertTrue(self.errors(routes=routes))
 def test_limit_removal(self):
  r=copy.deepcopy(self.r);r["preserved_limitations"]["proof_bodies_compared_in_full"]=True;self.assertTrue(self.errors(receipt=r))
 def test_blocker_removal(self):
  r=copy.deepcopy(self.r);r["preserved_limitations"]["blocked_repair_lanes"]=["OTP-C-PERMANENT"];self.assertTrue(self.errors(receipt=r))
 def test_claim_boundary_weakening(self):
  r=copy.deepcopy(self.r);r["claim_boundary"]="registered";self.assertTrue(self.errors(receipt=r))
if __name__=="__main__":unittest.main()
