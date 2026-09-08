from __future__ import annotations
import copy,json,shutil,tempfile,unittest
from pathlib import Path
import validate_certification_routes as module
class CertificationRouteTests(unittest.TestCase):
 def load_registry(self):return module.load_json(module.REGISTRY_PATH)
 def errors(self,payload):
  h=tempfile.NamedTemporaryFile("w",suffix=".json",delete=False,encoding="utf-8")
  with h:json.dump(payload,h,indent=2);h.write("\n")
  p=Path(h.name)
  try:return module.route_errors(p)
  finally:p.unlink(missing_ok=True)
 def test_current_registry_passes(self):self.assertEqual([],module.route_errors())
 def test_missing_campaign_fails(self):
  d=self.load_registry();d["routes"]=d["routes"][:-1];self.assertTrue(any("uncovered" in x for x in self.errors(d)))
 def test_wrong_hodge_tracker_fails(self):
  d=self.load_registry();next(r for r in d["routes"] if r["campaign_id"]=="HC-001")["tracker_issue"]="https://github.com/grandchallenge/MATHCERT/issues/24";self.assertTrue(any("tracker drift" in x for x in self.errors(d)))
 def test_qualified_without_packet_fails(self):
  d=self.load_registry();next(r for r in d["routes"] if r["campaign_id"]=="UC-001")["intake_packet"]=None;self.assertTrue(self.errors(d))
 def test_pending_route_cannot_claim_packet(self):
  d=self.load_registry();r=next(r for r in d["routes"] if r["campaign_id"]=="OZ-001");r["intake_packet"]=copy.deepcopy(d["routes"][0]["intake_packet"]);self.assertTrue(any("pending route" in x for x in self.errors(d)))
 def test_compactness_output_pointer_drift_fails(self):
  d=self.load_registry();r=next(r for r in d["routes"] if r["campaign_id"]=="OTP-J1-COMPACTNESS");r["cert_output"]["digest"]="0"*40;self.assertTrue(any("output identity drift" in x for x in self.errors(d)))
 def test_compactness_cannot_return_to_submitted(self):
  d=self.load_registry();r=next(r for r in d["routes"] if r["campaign_id"]=="OTP-J1-COMPACTNESS");r["intake_status"]="submitted";r["cert_output"]=None;self.assertTrue(any("governed intake state drift" in x for x in self.errors(d)))
 def test_uc_cannot_return_to_ready(self):
  d=self.load_registry();next(r for r in d["routes"] if r["campaign_id"]=="UC-001")["intake_status"]="ready";self.assertTrue(any("governed intake state drift" in x for x in self.errors(d)))
 def test_ehrhart_output_pointer_drift_fails(self):
  d=self.load_registry();next(r for r in d["routes"] if r["campaign_id"]=="OTP-F-EHRHART")["cert_output"]["commit_sha"]="0"*40;self.assertTrue(any("output identity drift" in x for x in self.errors(d)))
 def test_ehrhart_cannot_return_to_submitted(self):
  d=self.load_registry();r=next(r for r in d["routes"] if r["campaign_id"]=="OTP-F-EHRHART");r["intake_status"]="submitted";r["cert_output"]=None;self.assertTrue(any("governed intake state drift" in x for x in self.errors(d)))
 def test_commit_cannot_substitute_digest(self):
  d=self.load_registry();s=d["routes"][0]["source_manifest"];s["digest"]=s["commit_sha"];self.assertTrue(any("must not be substituted" in x for x in self.errors(d)))
 def test_duplicate_claim_fails(self):
  d=self.load_registry();d["routes"][1]["target_claim_ids"].append("UC-WP02-L002");self.assertTrue(any("duplicate target claim" in x for x in self.errors(d)))
 def test_manifest_digest_drift_fails(self):
  d=self.load_registry();d["routes"][0]["source_manifest"]["digest"]="0"*40;self.assertTrue(any("manifest identity drift" in x for x in self.errors(d)))
 def test_otp_packet_drift_fails(self):
  d=self.load_registry();next(r for r in d["routes"] if r["campaign_id"]=="OTP-J1-COMPACTNESS")["intake_packet"]["digest"]="0"*40;self.assertTrue(any("packet identity drift" in x for x in self.errors(d)))
 def test_j2_cannot_return_to_submitted(self):
  d=self.load_registry();r=next(r for r in d["routes"] if r["campaign_id"]=="OTP-J2-TWO-DEGENERATE");r["intake_status"]="submitted";r["cert_output"]=None;self.assertTrue(any("governed intake state drift" in x for x in self.errors(d)))
 def test_j2_output_pointer_drift_fails(self):
  d=self.load_registry();r=next(r for r in d["routes"] if r["campaign_id"]=="OTP-J2-TWO-DEGENERATE");r["cert_output"]["digest"]="0"*40;self.assertTrue(any("output identity drift" in x for x in self.errors(d)))
 def test_a_cannot_return_to_submitted(self):
  d=self.load_registry();r=next(r for r in d["routes"] if r["campaign_id"]=="OTP-A-SPHERE-PACKING");r["intake_status"]="submitted";r["cert_output"]=None;self.assertTrue(any("governed intake state drift" in x for x in self.errors(d)))
 def test_a_output_pointer_drift_fails(self):
  d=self.load_registry();r=next(r for r in d["routes"] if r["campaign_id"]=="OTP-A-SPHERE-PACKING");r["cert_output"]["digest"]="0"*40;self.assertTrue(any("output identity drift" in x for x in self.errors(d)))
 def test_a_packet_drift_fails(self):
  d=self.load_registry();next(r for r in d["routes"] if r["campaign_id"]=="OTP-A-SPHERE-PACKING")["intake_packet"]["digest"]="0"*40;self.assertTrue(any("packet identity drift" in x for x in self.errors(d)))
 def test_a_manifest_drift_fails(self):
  d=self.load_registry();next(r for r in d["routes"] if r["campaign_id"]=="OTP-A-SPHERE-PACKING")["source_manifest"]["digest"]="0"*40;self.assertTrue(any("manifest identity drift" in x for x in self.errors(d)))
 def test_h_must_remain_submitted(self):
  d=self.load_registry();r=next(r for r in d["routes"] if r["campaign_id"]=="OTP-H-GAPCVP");r["intake_status"]="qualified";self.assertTrue(any("governed intake state drift" in x for x in self.errors(d)))
 def test_h_submitted_route_cannot_carry_output(self):
  d=self.load_registry();r=next(r for r in d["routes"] if r["campaign_id"]=="OTP-H-GAPCVP");r["cert_output"]=copy.deepcopy(next(x for x in d["routes"] if x["campaign_id"]=="OTP-A-SPHERE-PACKING")["cert_output"]);self.assertTrue(any("intake-only" in x for x in self.errors(d)))
 def test_h_packet_drift_fails(self):
  d=self.load_registry();next(r for r in d["routes"] if r["campaign_id"]=="OTP-H-GAPCVP")["intake_packet"]["digest"]="0"*40;self.assertTrue(any("packet identity drift" in x for x in self.errors(d)))
 def test_h_manifest_drift_fails(self):
  d=self.load_registry();next(r for r in d["routes"] if r["campaign_id"]=="OTP-H-GAPCVP")["source_manifest"]["digest"]="0"*40;self.assertTrue(any("manifest identity drift" in x for x in self.errors(d)))
 def test_b1_must_remain_submitted(self):
  d=self.load_registry();r=next(r for r in d["routes"] if r["campaign_id"]=="OTP-B1-BINARY-CODES");r["intake_status"]="qualified";self.assertTrue(any("governed intake state drift" in x for x in self.errors(d)))
 def test_b1_submitted_route_cannot_carry_output(self):
  d=self.load_registry();r=next(r for r in d["routes"] if r["campaign_id"]=="OTP-B1-BINARY-CODES");r["cert_output"]=copy.deepcopy(next(x for x in d["routes"] if x["campaign_id"]=="OTP-A-SPHERE-PACKING")["cert_output"]);self.assertTrue(any("intake-only" in x for x in self.errors(d)))
 def test_b1_packet_drift_fails(self):
  d=self.load_registry();next(r for r in d["routes"] if r["campaign_id"]=="OTP-B1-BINARY-CODES")["intake_packet"]["digest"]="0"*40;self.assertTrue(any("packet identity drift" in x for x in self.errors(d)))
 def test_b1_manifest_drift_fails(self):
  d=self.load_registry();next(r for r in d["routes"] if r["campaign_id"]=="OTP-B1-BINARY-CODES")["source_manifest"]["digest"]="0"*40;self.assertTrue(any("manifest identity drift" in x for x in self.errors(d)))
 def test_aggregate_route_fails(self):
  d=self.load_registry();r=copy.deepcopy(next(r for r in d["routes"] if r["campaign_id"]=="OTP-F-EHRHART"));r["campaign_id"]="OPENAI-TEN-PROOFS-001";r["route_id"]="MC-ROUTE-OPENAI-TEN-PROOFS-001";d["routes"].append(r);self.assertTrue(self.errors(d))
class HCQualificationTests(unittest.TestCase):
 FILES=["certificates/hodge/MC-HC-WP00-QUAL-001.json","certificates/hodge/claim_records/HC-C001.json","certificates/hodge/claim_records/HC-C002.json","certificates/hodge/claim_records/HC-C003.json","schemas/hc_claim_record.schema.json","schemas/hc_wp00_qualification.schema.json","governance/certification_routes.json"]
 def copy(self):
  temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);root=Path(temp.name)
  for relative in self.FILES:
   target=root/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(module.ROOT/relative,target)
  return root
 def mutate(self,relative,action):
  root=self.copy();path=root/relative;value=json.loads(path.read_text(encoding="utf-8"));action(value);path.write_text(json.dumps(value,indent=2)+"\n",encoding="utf-8");return module.hc_qualification_errors(root)
 def assert_error(self,found,fragment):self.assertTrue(any(fragment in item for item in found),found)
 def test_hc_qualification_passes(self):self.assertEqual([],module.hc_qualification_errors())
 def test_hc_coefficient_mutation_fails(self):self.assert_error(self.mutate("certificates/hodge/claim_records/HC-C001.json",lambda v:v.update(coefficient_ring="Z")),"semantic coefficient_ring drift")
 def test_hc_geometry_mutation_fails(self):self.assert_error(self.mutate("certificates/hodge/claim_records/HC-C001.json",lambda v:v.update(geometric_category="compact_kahler_manifold")),"semantic geometric_category drift")
 def test_hc_rationality_loss_fails(self):self.assert_error(self.mutate("certificates/hodge/claim_records/HC-C001.json",lambda v:v.update(input_class_predicate="alpha has type (p,p)")),"rationality predicate drift")
 def test_hc_quantifier_weakening_fails(self):self.assert_error(self.mutate("certificates/hodge/claim_records/HC-C001.json",lambda v:v.update(quantifier_scope="sampled_classes")),"universal quantifier drift")
 def test_hc_implication_reversal_fails(self):self.assert_error(self.mutate("certificates/hodge/claim_records/HC-C002.json",lambda v:v.update(implication_direction="algebraic_to_Hodge")),"equivalence direction drift")
 def test_hc_effectivity_inflation_fails(self):self.assert_error(self.mutate("certificates/hodge/claim_records/HC-C002.json",lambda v:v.update(claims_not_made=["uniqueness"])),"effectivity boundary removed")
 def test_hc_dimension_inflation_fails(self):self.assert_error(self.mutate("certificates/hodge/claim_records/HC-C003.json",lambda v:v.update(dimension_scope="dim X <= 4")),"conditional dimension boundary drift")
 def test_hc_universal_proof_promotion_fails(self):self.assert_error(self.mutate("certificates/hodge/MC-HC-WP00-QUAL-001.json",lambda v:v.update(full_hodge_conjecture_proved=True)),"must remain false")
 def test_hc_kernel_claim_insertion_fails(self):
  def change(v):v["replay"].update(lean_formalization_available=True,kernel_checked_claims=["HC-C003"])
  self.assert_error(self.mutate("certificates/hodge/MC-HC-WP00-QUAL-001.json",change),"formalization boundary inflated")
 def test_hc_specialist_boundary_removal_fails(self):
  def change(v):v["unresolved_obligations"]=[item for item in v["unresolved_obligations"] if "specialist" not in item]
  self.assert_error(self.mutate("certificates/hodge/MC-HC-WP00-QUAL-001.json",change),"missing token: specialist")
 def test_hc_route_output_drift_fails(self):
  def change(v):next(item for item in v["routes"] if item["campaign_id"]=="HC-001")["cert_output"]["digest"]="0"*40
  self.assert_error(self.mutate("governance/certification_routes.json",change),"route output identity drift")
if __name__=="__main__":unittest.main()
