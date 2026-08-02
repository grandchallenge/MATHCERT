#!/usr/bin/env python3
from __future__ import annotations
import base64,hashlib,importlib.util,io,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];RECORD_ROOT=ROOT/"governance/result_family_replay_evidence";REGISTRY=ROOT/"governance/pre_route_candidates/OPENAI_TEN_PROOFS_WP04_REPLAY_EVIDENCE.json"
EXPECTED={"OTP-F-EHRHART":{"record":"d17d36d02f6505060f5a9e5f1f71f3c323fa1af8","bundle":"ehrhart","bundle_blob":"346eebb415609e6e66a9cb04510b7ba4994cf309","sha":"22fcaad533db94c03569439bb41fcda68618386826abd3aa624bbf90e9345adb"},"OTP-J1-COMPACTNESS":{"record":"5fe635510a0d2aa05da641e342078cf8b2b34aa6","bundle":"compactness","bundle_blob":"0f2a8918e669734ab89ece34b3f6dc60774552e2","sha":"852d0fa51a328199e6aeaf67a51fdd384ab30ec62ef6a7e28c5e22e597b3a99b"},"OTP-J2-TWO-DEGENERATE":{"record":"215ce18b4139159c89d167ab11cab6c35d5a38ff","bundle":"two-degenerate","bundle_blob":"14d050b03ccc9891f8c3e5ec4f522aa5aa00b8aa","sha":"b3efb532152677dd84c0872071a9d2aa061ea56b9a8a7d9175c6382766f27ed4"}}
def load(p):return json.loads(p.read_text())
def blob_bytes(b):return hashlib.sha1(f"blob {len(b)}\0".encode()+b,usedforsecurity=False).hexdigest()
def blob(p):return blob_bytes(p.read_bytes())
def decode_base64(data):return base64.b64decode(b"".join(data.split()),validate=True)
def registration_errors():
 s=importlib.util.spec_from_file_location("reg",ROOT/"ci/validate_openai_ten_proofs_route_registrations.py");m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m.validation_errors()
def validation_errors(records=None,registry=None,record_blobs=None,bundle_bytes=None,**_):
 e=[];records={p.stem:load(p) for p in RECORD_ROOT.glob("*.json")} if records is None else records;registry=load(REGISTRY) if registry is None else registry;record_blobs={p.stem:blob(p) for p in RECORD_ROOT.glob("*.json")} if record_blobs is None else record_blobs
 if set(records)!=set(EXPECTED):e.append("evidence membership drift")
 for fam,x in EXPECTED.items():
  r=records.get(fam)
  if not isinstance(r,dict):continue
  if record_blobs.get(fam)!=x["record"]:e.append(f"{fam}: evidence record blob drift")
  rs=r.get("replay_results",{})
  if not all((rs.get("comparator")=="pass",rs.get("lean_kernel")=="accept",rs.get("nanoda")=="accept",rs.get("theorem_axiom_report")=="permitted_only",rs.get("trust_boundary_scan")=="clear")):e.append(f"{fam}: replay result drift")
  if r.get("source_revision",{}).get("current_revision_semantic_concordance")!="blocked_pending_forge_audit":e.append(f"{fam}: historical source-revision state drift")
  route=r.get("route_state",{})
  if route!={"proposed_route":None,"registered_route":None,"may_adjudicate":False,"cert_output":None,"mathematical_target_proved":False,"may_promote_claim":False}:e.append(f"{fam}: historical evidence route state drift")
  path=ROOT/f'evidence/openai_ten_proofs/{x["bundle"]}.zip.b64';encoded=path.read_bytes() if bundle_bytes is None else bundle_bytes.get(fam,b"")
  if blob_bytes(encoded)!=x["bundle_blob"]:e.append(f"{fam}: repository bundle blob drift")
  try:
   decoded=decode_base64(encoded)
   if hashlib.sha256(decoded).hexdigest()!=x["sha"]:e.append(f"{fam}: decoded bundle SHA drift")
   z=zipfile.ZipFile(io.BytesIO(decoded));names=set(z.namelist())
   if not {"evidence-summary.json","environment.txt","comparator.log","axiom-check.json","theorem-axioms.log","trust-boundary-scan.txt"}.issubset(names):e.append(f"{fam}: evidence bundle inventory incomplete")
  except Exception:e.append(f"{fam}: bundle decode failure")
 state={"formal_replay_clear_count":3,"evidence_bundle_count":3,"specialist_review_count":0,"current_revision_semantic_concordance_clear_count":0,"proposed_route_count":0,"registered_route_count":0,"adjudication_count":0,"cert_output_count":0,"mathematical_target_proved_count":0}
 if registry.get("state")!=state:e.append("historical evidence registry state drift")
 if registration_errors():e.append("current route-registration authority invalid")
 return e
def main():
 e=validation_errors()
 if e:print("\n".join(e),file=sys.stderr);return 1
 print("validated immutable replay evidence bundles and separately governed current route registrations");return 0
if __name__=="__main__":raise SystemExit(main())
