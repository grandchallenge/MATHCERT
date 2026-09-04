from __future__ import annotations
import copy,json,tempfile,unittest
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
if __name__=="__main__":unittest.main()