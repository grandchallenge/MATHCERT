#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/"governance"/"pre_route_candidates"/"OPENAI_TEN_PROOFS_WP06_ROUTE_REGISTRATIONS.json"
ROUTES=ROOT/"governance"/"certification_routes.json"
PROPOSAL_REG=ROOT/"governance"/"pre_route_candidates"/"OPENAI_TEN_PROOFS_WP05_ROUTE_PROPOSALS.json"
SCHEMA=ROOT/"schemas"/"openai_ten_proofs_route_registration_registry.schema.json"
EXPECTED_FAMILIES=["OTP-F-EHRHART","OTP-J1-COMPACTNESS","OTP-J2-TWO-DEGENERATE"]
EXPECTED_PROPOSALS={"OTP-F-EHRHART":"7b069a003c84ef285259108076a55338fab0bc7f","OTP-J1-COMPACTNESS":"2e541ca5882873ee1c756814642994361b10c78c","OTP-J2-TWO-DEGENERATE":"0692ac15c19328532bdcd3e73b3c8c4371647ac6"}
EXPECTED_ROUTE_BLOB="b5541045591f8589130b1577c50d51d70c3b4337"
EXPECTED_PROPOSAL_REGISTRY_BLOB="1883b29ec888ffc487c65b76b35cfcb122f47e51"
EXPECTED_BEFORE_BLOB="5b3e8d48b9f6c5b03ed3dc439bf9e43876e017b1"
EXPECTED_PROPOSAL_MERGE="e8d1e34509e640d82902ad0195560740b52bec0e"
EXPECTED_PACKET_DIGESTS={"OTP-F-EHRHART":"4653985d4980113514266c3c421804437bacb019","OTP-J1-COMPACTNESS":"2d9c6e555a03b71eb33c476321e7f2d311ed168f","OTP-J2-TWO-DEGENERATE":"0d226492bf13e13bc1a437be01104db3d4c96f79"}
EXPECTED_CLAIMS={"OTP-F-EHRHART":["Ehrhart.Volume.ehrhart_volume_inequality_for_sets","Ehrhart.SimplexVolume.exists_centeredBody_sharp","Ehrhart.SimplexVolume.barycenter_centeredSimplex","Ehrhart.SimplexVolume.normalizedVolume_centeredSimplex"],"OTP-J1-COMPACTNESS":["CompactnessConjecture.quantitativeCompactnessCounterexample","CompactnessConjecture.compactnessCounterexample_bigO","CompactnessConjecture.not_erdos_180"],"OTP-J2-TWO-DEGENERATE":["TwoDegenerateGraphs.twoDegenerateExtremalCounterexample","TwoDegenerateGraphs.not_erdos_146"]}
PROVIDER={"repository":"grandchallenge/MATHFORGE","commit_sha":"0ea98866de3066e6a44ea1ca2cf93ade8a9e1c15","path":"provider_manifests/OPENAI-TEN-PROOFS-001.json","digest_algorithm":"git_blob_sha1","digest":"fe1dab478e4ef9d6ddfe1b94a289fe7b51f58472"}
def load(p:Path)->Any:return json.loads(p.read_text(encoding="utf-8"))
def blob(p:Path)->str:
 b=p.read_bytes();return hashlib.sha1(f"blob {len(b)}\0".encode()+b,usedforsecurity=False).hexdigest()
def closed_schema(v:Any)->list[str]:
 e=[]
 def walk(x,p=""):
  if isinstance(x,dict):
   if x.get("type")=="object" and x.get("additionalProperties") is not False:e.append(p or "/")
   for k,y in x.items():walk(y,p+"/"+k)
  elif isinstance(x,list):
   for i,y in enumerate(x):walk(y,p+f"/{i}")
 walk(v);return e
def validation_errors(receipt=None,routes=None,proposal_registry=None,proposal_blobs=None,routes_blob=None,proposal_registry_blob=None)->list[str]:
 e=[];receipt=load(REG) if receipt is None else receipt;routes=load(ROUTES) if routes is None else routes;proposal_registry=load(PROPOSAL_REG) if proposal_registry is None else proposal_registry
 proposal_blobs={fam:blob(ROOT/f"governance/result_family_route_proposals/{fam}.json") for fam in EXPECTED_FAMILIES} if proposal_blobs is None else proposal_blobs
 routes_blob=EXPECTED_ROUTE_BLOB if routes_blob is None else routes_blob;proposal_registry_blob=blob(PROPOSAL_REG) if proposal_registry_blob is None else proposal_registry_blob
 if closed_schema(load(SCHEMA)):e.append("registration schema contains open object")
 if not isinstance(receipt,dict):return ["registration receipt must be an object"]
 if set(receipt)!={"schema_version","record_type","record_id","candidate_id","tracker_issue","authority","state","registrations","preserved_limitations","route_controls","activation","claim_boundary"}:e.append("registration receipt fields drift")
 if (receipt.get("schema_version"),receipt.get("record_type"),receipt.get("record_id"),receipt.get("candidate_id"),receipt.get("tracker_issue"))!=("1.0.0","openai_ten_proofs_route_registration_registry","MC-OPENAI-TEN-PROOFS-WP06-ROUTE-REGISTRATIONS","OPENAI-TEN-PROOFS-001","https://github.com/grandchallenge/MATHCERT/issues/55"):e.append("registration receipt identity drift")
 a=receipt.get("authority",{})
 if a.get("proposal_pr_head")!="7b27d49c63dd126e6a18b80b340c71276bd71c84" or a.get("proposal_merge")!=EXPECTED_PROPOSAL_MERGE:e.append("proposal merge authority drift")
 if a.get("proposal_review")!={"reviewer":"jimsteeg","state":"APPROVED","submitted_at":"2026-08-02T04:16:37Z"}:e.append("proposal review authority drift")
 exp_pr={"repository":"grandchallenge/MATHCERT","commit_sha":EXPECTED_PROPOSAL_MERGE,"path":"governance/pre_route_candidates/OPENAI_TEN_PROOFS_WP05_ROUTE_PROPOSALS.json","digest_algorithm":"git_blob_sha1","digest":EXPECTED_PROPOSAL_REGISTRY_BLOB}
 if a.get("proposal_registry")!=exp_pr:e.append("proposal registry authority drift")
 if a.get("registered_route_registry_before_blob")!=EXPECTED_BEFORE_BLOB:e.append("prior route registry identity drift")
 if a.get("registered_route_registry_blob")!=EXPECTED_ROUTE_BLOB or routes_blob!=EXPECTED_ROUTE_BLOB:e.append("registered route registry blob drift")
 if proposal_registry_blob!=EXPECTED_PROPOSAL_REGISTRY_BLOB:e.append("proposal registry blob drift")
 if proposal_registry.get("state",{}).get("proposal_count")!=3:e.append("proposal registry count drift")
 regs=receipt.get("registrations")
 if not isinstance(regs,list) or len(regs)!=3:return e+["expected exactly three registrations"]
 byfam={r.get("result_family"):r for r in regs if isinstance(r,dict)}
 if set(byfam)!=set(EXPECTED_FAMILIES):e.append("registration family membership drift")
 route_map={r.get("campaign_id"):r for r in routes.get("routes",[]) if isinstance(r,dict)}
 otp_ids={r.get("route_id") for c,r in route_map.items() if str(c).startswith("OTP-")}
 if otp_ids!={f"MC-ROUTE-{f}" for f in EXPECTED_FAMILIES}:e.append("global OTP route membership drift")
 if "OPENAI-TEN-PROOFS-001" in route_map:e.append("aggregate route inserted")
 for fam in EXPECTED_FAMILIES:
  rec=byfam.get(fam,{});route=route_map.get(fam,{});rid=f"MC-ROUTE-{fam}"
  if rec.get("route_id")!=rid:e.append(f"{fam}: route identity drift")
  prop={"repository":"grandchallenge/MATHCERT","commit_sha":EXPECTED_PROPOSAL_MERGE,"path":f"governance/result_family_route_proposals/{fam}.json","digest_algorithm":"git_blob_sha1","digest":EXPECTED_PROPOSALS[fam]}
  if rec.get("proposal")!=prop or proposal_blobs.get(fam)!=EXPECTED_PROPOSALS[fam]:e.append(f"{fam}: proposal identity drift")
  packet={"repository":"grandchallenge/MATHSOLVE","commit_sha":"443daf537dc7e4ee34ab43aeb01508d9177816ab","path":f"work_packages/OPENAI_TEN_PROOFS_WP00/result_family_handoffs/{fam}.json","digest_algorithm":"git_blob_sha1","digest":EXPECTED_PACKET_DIGESTS[fam]}
  if rec.get("source_manifest")!=PROVIDER or rec.get("intake_packet")!=packet:e.append(f"{fam}: source or packet authority drift")
  if rec.get("intake_status")!="submitted" or rec.get("target_claim_ids")!=EXPECTED_CLAIMS[fam]:e.append(f"{fam}: registration state or target drift")
  if any((rec.get("cert_output") is not None,rec.get("may_adjudicate") is not False,rec.get("mathematical_target_proved") is not False,rec.get("may_promote_claim") is not False)):e.append(f"{fam}: adjudication/output/proof inflation")
  if route.get("route_id")!=rid or route.get("tracker_issue")!="https://github.com/grandchallenge/MATHCERT/issues/55":e.append(f"{fam}: global route entry identity drift")
  if route.get("source_manifest")!=PROVIDER or route.get("intake_packet")!=packet:e.append(f"{fam}: global route authority drift")
  if route.get("intake_status")!="submitted" or route.get("cert_output") is not None or route.get("target_claim_ids")!=EXPECTED_CLAIMS[fam]:e.append(f"{fam}: global route state inflation")
  if not isinstance(route.get("blockers"),list) or not any("adjudication" in x.lower() for x in route["blockers"]):e.append(f"{fam}: adjudication blocker missing")
 state={"proposal_count":3,"registered_route_count":3,"submitted_route_count":3,"adjudication_count":0,"cert_output_count":0,"mathematical_target_proved_count":0,"aggregate_route_count":0}
 if receipt.get("state")!=state:e.append("registration state inflation")
 lim={"whole_document_byte_equivalence":"not_established","whole_document_semantic_equivalence":"not_established","proof_bodies_compared_in_full":False,"unexamined_result_family_count":9,"blocked_repair_lanes":["OTP-C-PERMANENT","OTP-H-GAPCVP"],"all_lean_state":"failed_namespace_collision"}
 if receipt.get("preserved_limitations")!=lim:e.append("preserved limitation drift")
 ctl={"registration_scope":"exact_three_result_families","may_adjudicate":False,"may_issue_cert_output":False,"may_mark_target_proved":False,"aggregate_route_prohibited":True,"may_promote_claim":False}
 if receipt.get("route_controls")!=ctl:e.append("registration authority inflation")
 act=receipt.get("activation",{})
 if act.get("head_change_requires_reapproval") is not True or act.get("effect")!="three_routes_registered_no_adjudication_no_outputs":e.append("activation drift")
 claim=str(receipt.get("claim_boundary",""))
 if not all(x in claim for x in ("does not adjudicate","Cert output","aggregate")):e.append("claim boundary weakened")
 return e
def main()->int:
 e=validation_errors()
 if e:print("\n".join(e),file=sys.stderr);print(f"route registration validation failed with {len(e)} error(s)",file=sys.stderr);return 1
 print("validated three registered submitted OTP routes, exact proposal authority, and zero adjudication/output/proof authority");return 0
if __name__=="__main__":raise SystemExit(main())
