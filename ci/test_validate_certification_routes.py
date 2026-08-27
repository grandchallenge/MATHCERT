from __future__ import annotations
import ast,copy,json,re,tempfile,unittest
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
 def test_aggregate_route_fails(self):
  d=self.load_registry();r=copy.deepcopy(next(r for r in d["routes"] if r["campaign_id"]=="OTP-F-EHRHART"));r["campaign_id"]="OPENAI-TEN-PROOFS-001";r["route_id"]="MC-ROUTE-OPENAI-TEN-PROOFS-001";d["routes"].append(r);self.assertTrue(self.errors(d))
 def test_certification_route_consumer_inventory_diagnostic(self):
  root=Path(__file__).resolve().parents[1]
  ci=root/"ci"
  sources={}
  direct=set()
  refs=[]
  for path in sorted(ci.iterdir()):
   if not path.is_file() or path.suffix.lower() not in {".py",".sh",".ps1"}:continue
   text=path.read_text(encoding="utf-8")
   rel=str(path.relative_to(root));sources[rel]=text
   for number,line in enumerate(text.splitlines(),1):
    if "certification_routes" in line:
     direct.add(rel);refs.append(f"DIRECT|{rel}|{number}|{line.strip()}")
  module_to_path={Path(path).stem:path for path in sources if path.endswith(".py")}
  edges=set()
  for path,text in sources.items():
   imported=set()
   if path.endswith(".py"):
    try:tree=ast.parse(text)
    except SyntaxError:tree=None
    if tree is not None:
     for node in ast.walk(tree):
      if isinstance(node,ast.Import):imported.update(alias.name.split(".")[-1] for alias in node.names)
      elif isinstance(node,ast.ImportFrom) and node.module:imported.add(node.module.split(".")[-1])
   for name,target in module_to_path.items():
    if target==path:continue
    if name in imported or f"{name}.py" in text or re.search(rf"(?<![A-Za-z0-9_]){re.escape(name)}(?![A-Za-z0-9_])",text):
     edges.add((path,target))
  closure=set(direct)
  changed=True
  while changed:
   changed=False
   for parent,target in edges:
    if target in closure and parent not in closure:
     closure.add(parent);changed=True
  edge_lines=[f"EDGE|{parent}|{target}" for parent,target in sorted(edges) if target in closure and parent in closure]
  summary=[f"SUMMARY|direct={len(direct)}|closure={len(closure)}"]
  closure_lines=[f"CLOSURE|{path}" for path in sorted(closure)]
  self.fail("MC_CERTIFICATION_ROUTE_ARCHITECTURE_INVENTORY_BEGIN\n"+"\n".join(summary+sorted(refs)+closure_lines+edge_lines)+"\nMC_CERTIFICATION_ROUTE_ARCHITECTURE_INVENTORY_END")
if __name__=="__main__":unittest.main()