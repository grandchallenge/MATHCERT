#!/usr/bin/env python3
"""Validate exact MATHCERT campaign routes and intake/adjudication boundaries."""
from __future__ import annotations
import json,re,sys
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
REGISTRY_PATH=ROOT/"governance"/"certification_routes.json";SCHEMA_PATH=ROOT/"schemas"/"certification_route_registry.schema.json"
EXPECTED={
"UC-001":{"tracker":"https://github.com/grandchallenge/MATHCERT/issues/25","source":{"repository":"grandchallenge/MATHSOLVE","commit_sha":"916f3434abcce29098ba7508a3b457a461461193","path":"campaign_manifests/UC-001.json","digest_algorithm":"git_blob_sha1","digest":"55629c3004b8bffc35fc0fa6f5fbc711ff48aa3c"},"state":"ready","packet":{"repository":"grandchallenge/MATHSOLVE","commit_sha":"916f3434abcce29098ba7508a3b457a461461193","path":"cert_handoffs/UC-001.json","digest_algorithm":"git_blob_sha1","digest":"8369bc21e45be6af71d2a0cdb0c5ab3cb5313bfb"},"output":None},
"NS-CI-001":{"tracker":"https://github.com/grandchallenge/MATHCERT/issues/19","source":{"repository":"grandchallenge/MATHSOLVE","commit_sha":"916f3434abcce29098ba7508a3b457a461461193","path":"campaign_manifests/NS-CI-001.json","digest_algorithm":"git_blob_sha1","digest":"fcdd10f96b19c218ba700deb452b7da7f6b9b975"},"state":"qualified","packet":{"repository":"grandchallenge/MATHSOLVE","commit_sha":"916f3434abcce29098ba7508a3b457a461461193","path":"cert_handoffs/NS-CI-001.json","digest_algorithm":"git_blob_sha1","digest":"40cad99646829fe40edf9c616074514407e49dee"},"output":{"repository":"grandchallenge/MATHCERT","commit_sha":"b1aa08001eb8537be8e204c3866aefd5f898252e","path":"certificates/formal_sources/MC-FC-WP00-NS-CI-001.json","digest_algorithm":"git_blob_sha1","digest":"6047ad774957974a6c2aa86bae72b51841e774a4"}},
"HC-001":{"tracker":"https://github.com/grandchallenge/MATHCERT/issues/23","source":{"repository":"grandchallenge/MATHSOLVE","commit_sha":"916f3434abcce29098ba7508a3b457a461461193","path":"campaign_manifests/HC-001.json","digest_algorithm":"git_blob_sha1","digest":"48e3a0c22299147fe48cb4288cda813d7cffdcb4"},"state":"ready","packet":{"repository":"grandchallenge/MATHSOLVE","commit_sha":"916f3434abcce29098ba7508a3b457a461461193","path":"cert_handoffs/HC-001.json","digest_algorithm":"git_blob_sha1","digest":"0c154af2e577e4367f9f5d0aeac5e15f9420172c"},"output":None},
"BSD-001":{"tracker":"https://github.com/grandchallenge/MATHCERT/issues/26","source":{"repository":"grandchallenge/MATHSOLVE","commit_sha":"916f3434abcce29098ba7508a3b457a461461193","path":"campaign_manifests/BSD-001.json","digest_algorithm":"git_blob_sha1","digest":"3fb3b07400915d90047a06a353537cf2e1593b9e"},"state":"pending","packet":None,"output":None},
"PNP-001":{"tracker":"https://github.com/grandchallenge/MATHCERT/issues/27","source":{"repository":"grandchallenge/MATHSOLVE","commit_sha":"916f3434abcce29098ba7508a3b457a461461193","path":"campaign_manifests/PNP-001.json","digest_algorithm":"git_blob_sha1","digest":"6ecdfa0714828518878ccaf2cdc65756a5955186"},"state":"pending","packet":None,"output":None},
"RH-001":{"tracker":"https://github.com/grandchallenge/MATHCERT/issues/28","source":{"repository":"grandchallenge/MATHSOLVE","commit_sha":"916f3434abcce29098ba7508a3b457a461461193","path":"campaign_manifests/RH-001.json","digest_algorithm":"git_blob_sha1","digest":"4ce2c5bcdc7bc1d0d63f7b2244898c8a651d5f64"},"state":"qualified","packet":{"repository":"grandchallenge/MATHSOLVE","commit_sha":"916f3434abcce29098ba7508a3b457a461461193","path":"cert_handoffs/RH-001.json","digest_algorithm":"git_blob_sha1","digest":"7304f185bd817bb67b77540513dc01d05f6fcd3a"},"output":{"repository":"grandchallenge/MATHCERT","commit_sha":"b1aa08001eb8537be8e204c3866aefd5f898252e","path":"certificates/formal_sources/MC-FC-WP00-RH-001.json","digest_algorithm":"git_blob_sha1","digest":"3668bbf792d994a6d8919101417f2f3cad342cdc"}},
"YM-001":{"tracker":"https://github.com/grandchallenge/MATHCERT/issues/29","source":{"repository":"grandchallenge/MATHSOLVE","commit_sha":"916f3434abcce29098ba7508a3b457a461461193","path":"campaign_manifests/YM-001.json","digest_algorithm":"git_blob_sha1","digest":"733d11811d0226fa2b2467965c3655a7d0fad963"},"state":"pending","packet":None,"output":None},
"OZ-001":{"tracker":"https://github.com/grandchallenge/MATHCERT/issues/30","source":{"repository":"grandchallenge/MATHSOLVE","commit_sha":"916f3434abcce29098ba7508a3b457a461461193","path":"campaign_manifests/OZ-001.json","digest_algorithm":"git_blob_sha1","digest":"8b3164ab88a35ec9fba69013b44056573e846bfe"},"state":"pending","packet":None,"output":None}}
for fam,digest in {"OTP-F-EHRHART":"4653985d4980113514266c3c421804437bacb019","OTP-J1-COMPACTNESS":"2d9c6e555a03b71eb33c476321e7f2d311ed168f","OTP-J2-TWO-DEGENERATE":"0d226492bf13e13bc1a437be01104db3d4c96f79"}.items():EXPECTED[fam]={"tracker":"https://github.com/grandchallenge/MATHCERT/issues/55","source":{"repository":"grandchallenge/MATHFORGE","commit_sha":"0ea98866de3066e6a44ea1ca2cf93ade8a9e1c15","path":"provider_manifests/OPENAI-TEN-PROOFS-001.json","digest_algorithm":"git_blob_sha1","digest":"fe1dab478e4ef9d6ddfe1b94a289fe7b51f58472"},"state":"submitted","packet":{"repository":"grandchallenge/MATHSOLVE","commit_sha":"443daf537dc7e4ee34ab43aeb01508d9177816ab","path":f"work_packages/OPENAI_TEN_PROOFS_WP00/result_family_handoffs/{fam}.json","digest_algorithm":"git_blob_sha1","digest":digest},"output":None}
ADJUDICATED={"certified","qualified","rejected","proof_debt"};INTAKE_ONLY={"ready","submitted"};ALL_STATES={"pending"}|INTAKE_ONLY|ADJUDICATED
HEX40=re.compile(r"^[0-9a-f]{40}$");HEX64=re.compile(r"^[0-9a-f]{64}$");ARTIFACT_KEYS={"repository","commit_sha","path","digest_algorithm","digest"};ROUTE_KEYS={"route_id","campaign_id","tracker_issue","source_manifest","intake_status","intake_packet","target_claim_ids","requested_modalities","claim_boundary","cert_output","blockers","reopening_conditions"}
def load_json(path:Path)->Any:return json.loads(path.read_text(encoding="utf-8"))
def artifact_errors(v:Any,label:str)->list[str]:
 e=[]
 if not isinstance(v,dict):return [f"{label}: expected an artifact object"]
 if set(v)!=ARTIFACT_KEYS:e.append(f"{label}: artifact fields drift")
 c=str(v.get("commit_sha",""));d=str(v.get("digest",""));a=v.get("digest_algorithm")
 if "/" not in str(v.get("repository","")):e.append(f"{label}: repository must use owner/name form")
 if not HEX40.fullmatch(c):e.append(f"{label}: invalid commit_sha")
 if not str(v.get("path","")).strip():e.append(f"{label}: empty path")
 if a in {"git_blob_sha1","git_tree_sha1"} and not HEX40.fullmatch(d):e.append(f"{label}: invalid Git digest")
 elif a=="sha256" and not HEX64.fullmatch(d):e.append(f"{label}: invalid SHA-256 digest")
 elif a not in {"git_blob_sha1","git_tree_sha1","sha256"}:e.append(f"{label}: unsupported digest algorithm")
 if d==c:e.append(f"{label}: artifact digest must not be substituted with the repository commit")
 return e
def route_errors(registry_path:Path=REGISTRY_PATH,schema_path:Path=SCHEMA_PATH)->list[str]:
 data=load_json(registry_path);schema=load_json(schema_path);e=[]
 if schema.get("additionalProperties") is not False:e.append("route schema must remain closed")
 if not isinstance(data,dict):return ["registry must be an object"]
 if data.get("schema_version")!="1.0.0" or data.get("registry_id")!="MC-CERTIFICATION-ROUTES":e.append("registry identity drift")
 if data.get("provider_repository")!="grandchallenge/MATHCERT":e.append("provider repository drift")
 if not HEX40.fullmatch(str(data.get("provider_base_commit",""))):e.append("provider_base_commit must be a full SHA")
 routes=data.get("routes")
 if not isinstance(routes,list):return e+["routes must be an array"]
 route_map={r.get("campaign_id"):r for r in routes if isinstance(r,dict)}
 for x in sorted(set(EXPECTED)-set(route_map)):e.append(f"governed campaign is uncovered: {x}")
 for x in sorted(set(route_map)-set(EXPECTED)):e.append(f"unrecognized campaign: {x}")
 if len(route_map)!=len(routes):e.append("campaign route uniqueness drift")
 claims={}
 for cid,exp in EXPECTED.items():
  r=route_map.get(cid)
  if not isinstance(r,dict):continue
  if set(r)!=ROUTE_KEYS:e.append(f"{cid}: route fields drift")
  if r.get("route_id")!=f"MC-ROUTE-{cid}":e.append(f"{cid}: route_id is not canonical")
  if r.get("tracker_issue")!=exp["tracker"]:e.append(f"{cid}: tracker drift")
  src=r.get("source_manifest");e.extend(artifact_errors(src,f"{cid}.source_manifest"))
  if src!=exp["source"]:e.append(f"{cid}: manifest identity drift")
  state=r.get("intake_status")
  if state not in ALL_STATES or state!=exp["state"]:e.append(f"{cid}: governed intake state drift")
  pkt=r.get("intake_packet");out=r.get("cert_output")
  if state=="pending":
   if pkt is not None or out is not None:e.append(f"{cid}: pending route must not carry packet/output")
  else:
   e.extend(artifact_errors(pkt,f"{cid}.intake_packet"))
   if pkt!=exp["packet"]:e.append(f"{cid}: packet identity drift")
   if state in INTAKE_ONLY and out is not None:e.append(f"{cid}: {state} is intake-only and must not carry Cert output")
   if state in ADJUDICATED:
    e.extend(artifact_errors(out,f"{cid}.cert_output"))
    if out!=exp["output"]:e.append(f"{cid}: output identity drift")
  ids=r.get("target_claim_ids")
  if not isinstance(ids,list) or not ids or len(ids)!=len(set(ids)):e.append(f"{cid}: target_claim_ids must be a unique nonempty list");ids=[]
  for claim in ids:
   if claim in claims:e.append(f"duplicate target claim {claim}; first registered by {claims[claim]}")
   claims[claim]=cid
  if not str(r.get("claim_boundary","")).strip():e.append(f"{cid}: empty claim boundary")
  if not isinstance(r.get("blockers"),list) or not r["blockers"]:e.append(f"{cid}: blockers required")
  if not isinstance(r.get("reopening_conditions"),list) or not r["reopening_conditions"]:e.append(f"{cid}: reopening conditions required")
 otp={"OTP-F-EHRHART","OTP-J1-COMPACTNESS","OTP-J2-TWO-DEGENERATE"}
 if {cid for cid,r in route_map.items() if str(r.get("route_id","")).startswith("MC-ROUTE-OTP-")}!=otp:e.append("OTP route membership drift")
 if "OPENAI-TEN-PROOFS-001" in route_map:e.append("aggregate ten-proofs route prohibited")
 return e
def main()->int:
 e=route_errors()
 if e:print("\n".join(e),file=sys.stderr);return 1
 print("validated eleven exact routes, including three submitted OTP family routes, with zero OTP adjudications or outputs");return 0
if __name__=="__main__":raise SystemExit(main())
