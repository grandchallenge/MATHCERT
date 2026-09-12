#!/usr/bin/env python3
"""Validate exact MATHCERT campaign routes and intake/adjudication boundaries."""
from __future__ import annotations
import hashlib,json,re,sys
from pathlib import Path
from typing import Any
import jsonschema
ROOT=Path(__file__).resolve().parents[1]
REGISTRY_PATH=ROOT/"governance"/"certification_routes.json";SCHEMA_PATH=ROOT/"schemas"/"certification_route_registry.schema.json"
def art(repo,commit,path,digest):return {"repository":repo,"commit_sha":commit,"path":path,"digest_algorithm":"git_blob_sha1","digest":digest}
SOLVE="916f3434abcce29098ba7508a3b457a461461193"
EXPECTED={
"UC-001":{"tracker":"https://github.com/grandchallenge/MATHCERT/issues/25","source":art("grandchallenge/MATHSOLVE",SOLVE,"campaign_manifests/UC-001.json","55629c3004b8bffc35fc0fa6f5fbc711ff48aa3c"),"state":"qualified","packet":art("grandchallenge/MATHSOLVE",SOLVE,"cert_handoffs/UC-001.json","8369bc21e45be6af71d2a0cdb0c5ab3cb5313bfb"),"output":art("grandchallenge/MATHCERT","214c4f4d7962883bb10172db84d5162dde2e5c4e","certificates/union_closed/MC-UC-WP04-QUAL-001.json","265c185d6b2b2970dc675729efa3fc4860f29204")},
"NS-CI-001":{"tracker":"https://github.com/grandchallenge/MATHCERT/issues/19","source":art("grandchallenge/MATHSOLVE",SOLVE,"campaign_manifests/NS-CI-001.json","fcdd10f96b19c218ba700deb452b7da7f6b9b975"),"state":"qualified","packet":art("grandchallenge/MATHSOLVE",SOLVE,"cert_handoffs/NS-CI-001.json","40cad99646829fe40edf9c616074514407e49dee"),"output":art("grandchallenge/MATHCERT","b1aa08001eb8537be8e204c3866aefd5f898252e","certificates/formal_sources/MC-FC-WP00-NS-CI-001.json","6047ad774957974a6c2aa86bae72b51841e774a4")},
"HC-001":{"tracker":"https://github.com/grandchallenge/MATHCERT/issues/23","source":art("grandchallenge/MATHSOLVE",SOLVE,"campaign_manifests/HC-001.json","48e3a0c22299147fe48cb4288cda813d7cffdcb4"),"state":"qualified","packet":art("grandchallenge/MATHSOLVE",SOLVE,"cert_handoffs/HC-001.json","0c154af2e577e4367f9f5d0aeac5e15f9420172c"),"output":art("grandchallenge/MATHCERT","fdc33903593b6bc4a021ad7158f3533f50da8705","certificates/hodge/MC-HC-WP00-QUAL-001.json","38830b24464f148a53f0a0a3e47e97d307fadf23")},
"BSD-001":{"tracker":"https://github.com/grandchallenge/MATHCERT/issues/26","source":art("grandchallenge/MATHSOLVE",SOLVE,"campaign_manifests/BSD-001.json","3fb3b07400915d90047a06a353537cf2e1593b9e"),"state":"pending","packet":None,"output":None},
"PNP-001":{"tracker":"https://github.com/grandchallenge/MATHCERT/issues/27","source":art("grandchallenge/MATHSOLVE",SOLVE,"campaign_manifests/PNP-001.json","6ecdfa0714828518878ccaf2cdc65756a5955186"),"state":"pending","packet":None,"output":None},
"RH-001":{"tracker":"https://github.com/grandchallenge/MATHCERT/issues/28","source":art("grandchallenge/MATHSOLVE",SOLVE,"campaign_manifests/RH-001.json","4ce2c5bcdc7bc1d0d63f7b2244898c8a651d5f64"),"state":"qualified","packet":art("grandchallenge/MATHSOLVE",SOLVE,"cert_handoffs/RH-001.json","7304f185bd817bb67b77540513dc01d05f6fcd3a"),"output":art("grandchallenge/MATHCERT","b1aa08001eb8537be8e204c3866aefd5f898252e","certificates/formal_sources/MC-FC-WP00-RH-001.json","3668bbf792d994a6d8919101417f2f3cad342cdc")},
"YM-001":{"tracker":"https://github.com/grandchallenge/MATHCERT/issues/29","source":art("grandchallenge/MATHSOLVE",SOLVE,"campaign_manifests/YM-001.json","733d11811d0226fa2b2467965c3655a7d0fad963"),"state":"pending","packet":None,"output":None},
"OZ-001":{"tracker":"https://github.com/grandchallenge/MATHCERT/issues/30","source":art("grandchallenge/MATHSOLVE",SOLVE,"campaign_manifests/OZ-001.json","8b3164ab88a35ec9fba69013b44056573e846bfe"),"state":"pending","packet":None,"output":None}}
PROVIDER=art("grandchallenge/MATHFORGE","0ea98866de3066e6a44ea1ca2cf93ade8a9e1c15","provider_manifests/OPENAI-TEN-PROOFS-001.json","fe1dab478e4ef9d6ddfe1b94a289fe7b51f58472")
PACKETS={"OTP-F-EHRHART":"4653985d4980113514266c3c421804437bacb019","OTP-J1-COMPACTNESS":"2d9c6e555a03b71eb33c476321e7f2d311ed168f","OTP-J2-TWO-DEGENERATE":"0d226492bf13e13bc1a437be01104db3d4c96f79"}
for fam,digest in PACKETS.items():EXPECTED[fam]={"tracker":"https://github.com/grandchallenge/MATHCERT/issues/55","source":PROVIDER,"state":"submitted","packet":art("grandchallenge/MATHSOLVE","443daf537dc7e4ee34ab43aeb01508d9177816ab",f"work_packages/OPENAI_TEN_PROOFS_WP00/result_family_handoffs/{fam}.json",digest),"output":None}
EXPECTED["OTP-F-EHRHART"]["state"]="qualified";EXPECTED["OTP-F-EHRHART"]["output"]=art("grandchallenge/MATHCERT","24d99cbdcd6da33ae2404c0f6034d503498d9a4b","certificates/formal_sources/MC-OTP-F-EHRHART-001.json","27a855c949b67e71372c7f0d6601d80125d33968")
EXPECTED["OTP-J1-COMPACTNESS"]["state"]="qualified";EXPECTED["OTP-J1-COMPACTNESS"]["output"]=art("grandchallenge/MATHCERT","9fba5a8e918028ecc2b4d72abc00b3b72a5194f5","certificates/formal_sources/MC-OTP-J1-COMPACTNESS-001.json","88531e28951854961e86eec0517356999a391759")
EXPECTED["OTP-J2-TWO-DEGENERATE"]["state"]="qualified";EXPECTED["OTP-J2-TWO-DEGENERATE"]["output"]=art("grandchallenge/MATHCERT","24cff6e55709c067c7f966c1a533255af707bec0","certificates/formal_sources/MC-OTP-J2-TWO-DEGENERATE-001.json","308a2eb7087fb24a07a6ae8c93a83b593468d2f7")
EXPECTED["OTP-C-PERMANENT"]={
 "route_id":"MC-ROUTE-OTP-C-PERMANENT-FORMULA",
 "tracker":"https://github.com/grandchallenge/MATHCERT/issues/101",
 "source":art("grandchallenge/MATHFORGE","60f6e06c957139447bf5943eed731941b22ac608","sources/OPENAI-TEN-PROOFS-001/semantic/OTP-C-PERMANENT/semantic_audit_record.json","3e04bd16bd8a91eaf9b6702de89fcdcc72f61099"),
 "state":"qualified",
 "packet":art("grandchallenge/MATHSOLVE","90f8a8544e546a603b34c9b27b2d6a4a68e06de8","work_packages/OPENAI_TEN_PROOFS_WP00/result_family_handoffs/OTP-C-PERMANENT.json","a993c530880021930a2b468e76235b91122ca854"),
 "output":art("grandchallenge/MATHCERT","1344220f0f61f9e637c5b1fc668c0a0eb7ab4133","certificates/formal_sources/MC-OTP-C-PERMANENT-001.json","ad10c427270cb1c747ebcacbc5c37e4c1ed1df04")}
EXPECTED["OTP-A-SPHERE-PACKING"]={
 "tracker":"https://github.com/grandchallenge/MATHCERT/issues/158",
 "source":art("grandchallenge/MATHFORGE","706d0291370bf3f14aa37be0823e33d06f7343b0","sources/OPENAI-TEN-PROOFS-001/semantic/OTP-A-SPHERE-PACKING-COMPOSITE/audit_record.json","b2e309ad96e750651fc7149a6bad54c6bf99015b"),
 "state":"qualified",
 "packet":art("grandchallenge/MATHSOLVE","c19735edf4c16ac9765bb66c7209bbf11bf1312e","work_packages/OPENAI_TEN_PROOFS_WP00/result_family_handoff_successors/OTP-A-SPHERE-PACKING.json","9e3b46972bf01ac3d24c6a0ae5f522799335ecd1"),
 "output":art("grandchallenge/MATHCERT","1815f1b4010122e5bef0438f84da0b06204ba487","certificates/formal_sources/MC-OTP-A-SPHERE-PACKING-001.json","534e98ad2f00406fc869ea137f802f8cf504798a")}
EXPECTED["OTP-H-GAPCVP"]={
 "tracker":"https://github.com/grandchallenge/MATHCERT/issues/190",
 "source":art("grandchallenge/MATHFORGE","b9dda1a5b958fd1be37a26324a025013a39584c1","sources/OPENAI-TEN-PROOFS-001/semantic/OTP-H-GAPCVP/audit_record.json","673f541fbb552d307cc226c51d2f0fd2916b328d"),
 "state":"qualified",
 "packet":art("grandchallenge/MATHSOLVE","e42c48dfe6a83eb19f398ba114f61fd700694ce5","work_packages/OPENAI_TEN_PROOFS_WP00/result_family_handoff_successors/OTP-H-GAPCVP.json","0dd2b38e40a126a1a2a2d57989038f788b8e40e4"),
 "output":art("grandchallenge/MATHCERT","669e50b7394b7a6cc8b4ede3d8d85efb923f9044","certificates/formal_sources/MC-OTP-H-GAPCVP-001.json","88b24b5e850676d89267467ea05e21d6dddca9d0")}
EXPECTED["OTP-B1-BINARY-CODES"]={
 "tracker":"https://github.com/grandchallenge/MATHCERT/issues/205",
 "source":art("grandchallenge/MATHFORGE","24a1fa0f020ee9cc7fbe2e7aea4cd840268ca748","sources/OPENAI-TEN-PROOFS-001/semantic/OTP-B1-BINARY-CODES/audit_record.json","0ab4d973bc046084e9d2dc6c7552ab5428d7412d"),
 "state":"qualified",
 "packet":art("grandchallenge/MATHSOLVE","7858f1350439e6324bdee149931bdb7661098729","work_packages/OPENAI_TEN_PROOFS_WP00/result_family_handoff_successors/OTP-B1-BINARY-CODES.json","1847dd7a17cda51cb02f017766c59d372811fb12"),
 "output":art("grandchallenge/MATHCERT","b773fa35a801808ec233f3871fd13d74c9833498","certificates/formal_sources/MC-OTP-B1-BINARY-CODES-001.json","9e209b10ae814f79635735e6a3d5ee5821082c93")}
ADJUDICATED={"certified","qualified","rejected","proof_debt"};INTAKE_ONLY={"ready","submitted"};ALL_STATES={"pending"}|INTAKE_ONLY|ADJUDICATED
HEX40=re.compile(r"^[0-9a-f]{40}$");HEX64=re.compile(r"^[0-9a-f]{64}$");ARTIFACT_KEYS={"repository","commit_sha","path","digest_algorithm","digest"};ROUTE_KEYS={"route_id","campaign_id","tracker_issue","source_manifest","intake_status","intake_packet","target_claim_ids","requested_modalities","claim_boundary","cert_output","blockers","reopening_conditions"}
HC_CERT_PATH=Path("certificates/hodge/MC-HC-WP00-QUAL-001.json")
HC_CERT_COMMIT="fdc33903593b6bc4a021ad7158f3533f50da8705";HC_CERT_BLOB="38830b24464f148a53f0a0a3e47e97d307fadf23";HC_RECORD_COMMIT="599230f994d7cf98c448fb99b185a802e336269f"
HC_RECORDS={"HC-C001":("c6bf64e8d2b716be54ef86798e120b2a67c64ad6","qualified_statement_identity"),"HC-C002":("e16e64f0168d06ae508e5ae0956942a6b68211b3","qualified_definition_level_equivalence"),"HC-C003":("ce3f3885ac7bbcb09ac5777653c4ebbccc2a4cb8","qualified_conditional_low_dimension_reduction")}
HC_MUTATIONS={"coefficient_Q_to_Z","rational_Hodge_class_to_arbitrary_complex_pp_class","smooth_projective_to_compact_Kahler","Chow_cycle_to_motivated_or_topological_object","rational_generation_to_effective_irreducible_representative","universal_to_sampled_or_very_general_quantifier","algebraic_to_Hodge_implication_reversed_as_definition"}
def load_json(path:Path)->Any:return json.loads(path.read_text(encoding="utf-8"))
def git_blob(path:Path)->str:
 payload=path.read_bytes();return hashlib.sha1(f"blob {len(payload)}\0".encode("ascii")+payload,usedforsecurity=False).hexdigest()
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
 if d==c:e.append(f"{label}: artifact digest must not be substituted with repository commit")
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
  if r.get("route_id")!=exp.get("route_id",f"MC-ROUTE-{cid}"):e.append(f"{cid}: route_id is not canonical")
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
 otp={"OTP-F-EHRHART","OTP-J1-COMPACTNESS","OTP-J2-TWO-DEGENERATE","OTP-C-PERMANENT","OTP-A-SPHERE-PACKING","OTP-H-GAPCVP","OTP-B1-BINARY-CODES"}
 if {cid for cid,r in route_map.items() if str(r.get("route_id","")).startswith("MC-ROUTE-OTP-")}!=otp:e.append("OTP route membership drift")
 if "OPENAI-TEN-PROOFS-001" in route_map:e.append("aggregate ten-proofs route prohibited")
 return e
def hc_qualification_errors(root:Path=ROOT)->list[str]:
 e=[];cert_path=root/HC_CERT_PATH;schema_path=root/"schemas/hc_wp00_qualification.schema.json";claim_schema_path=root/"schemas/hc_claim_record.schema.json";routes_path=root/"governance/certification_routes.json"
 try:cert=load_json(cert_path);schema=load_json(schema_path);claim_schema=load_json(claim_schema_path);routes=load_json(routes_path)
 except (OSError,json.JSONDecodeError) as exc:return [f"HC qualification load failed: {exc}"]
 try:jsonschema.validate(cert,schema)
 except jsonschema.ValidationError as exc:e.append(f"HC qualification schema failure: {exc.message}")
 if schema.get("$id")!="https://grandchallenge.ai/schemas/hc_wp00_qualification.schema.json" or schema.get("additionalProperties") is not False:e.append("HC qualification schema identity or closure drift")
 if git_blob(schema_path)!="b835b1255d90a21650cda5ae5e6e57a391847331":e.append("HC qualification schema blob drift")
 if git_blob(cert_path)!=HC_CERT_BLOB:e.append("HC qualification certificate blob drift")
 if (cert.get("certificate_id"),cert.get("campaign_id"),cert.get("route_id"))!=("MC-HC-WP00-QUAL-001","HC-001","MC-ROUTE-HC-001"):e.append("HC qualification identity drift")
 provider=cert.get("solve_provider",{});expected_provider={"manifest":("916f3434abcce29098ba7508a3b457a461461193","campaign_manifests/HC-001.json","48e3a0c22299147fe48cb4288cda813d7cffdcb4"),"handoff":("916f3434abcce29098ba7508a3b457a461461193","cert_handoffs/HC-001.json","0c154af2e577e4367f9f5d0aeac5e15f9420172c"),"work_package":("8c56729cb8a747296f2be5eeab93d2cde999e4bc","work_packages/HC_WP00.md","195d2a281f75493f5db1a81f2270e16aeead259d"),"claim_ledger":("16edb1df66d1e1835754ec1e7a1faa93231675b9","campaign_ledgers/HC-001/claim_ledger.json","ed0216ea6dd1859effe926b8c501d8dc156e897a"),"proof_obligations":("e067c1b0f9eeb8a08b12a9fd9f6281e792a19e2b","campaign_ledgers/HC-001/proof_obligation_dag.json","99394c33bf91fe433713fffb1f48c01e08237f6b")}
 if provider.get("repository")!="grandchallenge/MATHSOLVE" or provider.get("merge_commit")!="916f3434abcce29098ba7508a3b457a461461193":e.append("HC Solve provider identity drift")
 for key,expected in expected_provider.items():
  item=provider.get(key,{})
  if (item.get("repository"),item.get("commit_sha"),item.get("path"),item.get("digest"))!=("grandchallenge/MATHSOLVE",*expected):e.append(f"HC Solve {key} authority drift")
 refs={Path(item.get("path","")).stem:item for item in cert.get("claim_records",[]) if isinstance(item,dict)}
 if set(refs)!=set(HC_RECORDS):e.append("HC claim-record set drift")
 records={}
 for claim_id,(digest,_) in HC_RECORDS.items():
  relative=Path(f"certificates/hodge/claim_records/{claim_id}.json");path=root/relative
  try:record=load_json(path);jsonschema.validate(record,claim_schema);records[claim_id]=record
  except (OSError,json.JSONDecodeError,jsonschema.ValidationError) as exc:e.append(f"{claim_id}: claim record invalid: {exc}");continue
  if git_blob(path)!=digest:e.append(f"{claim_id}: claim record blob drift")
  ref=refs.get(claim_id,{})
  if (ref.get("repository"),ref.get("commit_sha"),ref.get("path"),ref.get("digest"))!=("grandchallenge/MATHCERT",HC_RECORD_COMMIT,relative.as_posix(),digest):e.append(f"{claim_id}: claim record authority drift")
 for claim_id,record in records.items():
  for key,value in {"base_field":"C","geometric_category":"smooth_projective_variety","smoothness":"smooth","properness_profile":"projective","coefficient_ring":"Q"}.items():
   if record.get(key)!=value:e.append(f"{claim_id}: semantic {key} drift")
 if records.get("HC-C001",{}).get("quantifier_scope")!="every_variety_every_class":e.append("HC-C001: universal quantifier drift")
 if records.get("HC-C001",{}).get("input_class_predicate")!="alpha is rational and its complexification has Hodge type (p,p)":e.append("HC-C001: rationality predicate drift")
 if records.get("HC-C002",{}).get("implication_direction")!="equivalence":e.append("HC-C002: equivalence direction drift")
 if "effectivity" not in records.get("HC-C002",{}).get("claims_not_made",[]):e.append("HC-C002: effectivity boundary removed")
 if records.get("HC-C003",{}).get("dimension_scope")!="dim X <= 3" or records.get("HC-C003",{}).get("status")!="CONDITIONAL":e.append("HC-C003: conditional dimension boundary drift")
 claims={item.get("claim_id"):item for item in cert.get("adjudicated_claims",[]) if isinstance(item,dict)}
 if set(claims)!=set(HC_RECORDS):e.append("HC adjudicated claim set drift")
 for claim_id,(_,disposition) in HC_RECORDS.items():
  item=claims.get(claim_id,{})
  if item.get("modality")!="SEMANTIC_REPLAY" or item.get("disposition")!=disposition or item.get("kernel_checked") is not False:e.append(f"{claim_id}: bounded disposition drift")
 sources={item.get("source_id"):item for item in cert.get("external_sources",[]) if isinstance(item,dict)}
 if set(sources)!={"CLAY-DELIGNE-HODGE","CLAY-HODGE-STATUS"}:e.append("HC independent source set drift")
 if sources.get("CLAY-DELIGNE-HODGE",{}).get("url")!="https://www.claymath.org/wp-content/uploads/2022/06/hodge.pdf" or sources.get("CLAY-HODGE-STATUS",{}).get("url")!="https://www.claymath.org/millennium/hodge-conjecture/":e.append("HC official source authority drift")
 replay=cert.get("replay",{})
 if set(replay.get("semantic_mutations_rejected",[]))!=HC_MUTATIONS:e.append("HC semantic mutation coverage drift")
 if replay.get("lean_formalization_available") is not False or replay.get("kernel_checked_claims")!=[]:e.append("HC formalization boundary inflated")
 for key in ("mathematical_target_proved","full_hodge_conjecture_proved","restricted_target_selected"):
  if cert.get(key) is not False:e.append(f"HC {key} must remain false")
 if cert.get("disposition")!="qualified_semantic_and_conditional_interface_only":e.append("HC disposition inflation")
 unresolved=" ".join(cert.get("unresolved_obligations",[]))
 for token in ("universal","dimension-four","restricted","formalization","specialist"):
  if token not in unresolved:e.append(f"HC unresolved obligations missing token: {token}")
 boundary=str(cert.get("claim_boundary",""))
 for token in ("does not prove the Hodge conjecture","Lean/kernel proof","claim-promotion"):
  if token not in boundary:e.append(f"HC claim boundary missing token: {token}")
 route=next((item for item in routes.get("routes",[]) if item.get("campaign_id")=="HC-001"),{})
 if route.get("intake_status")!="qualified" or route.get("target_claim_ids") != ["HC-C001","HC-C002","HC-C003"]:e.append("HC route state or target set drift")
 output=route.get("cert_output",{})
 if (output.get("repository"),output.get("commit_sha"),output.get("path"),output.get("digest"))!=("grandchallenge/MATHCERT",HC_CERT_COMMIT,HC_CERT_PATH.as_posix(),HC_CERT_BLOB):e.append("HC route output identity drift")
 blockers=" ".join(route.get("blockers",[]))
 for token in ("full Hodge","dimension-four","restricted target","specialist"):
  if token not in blockers:e.append(f"HC route blockers missing token: {token}")
 return e
def main()->int:
 e=route_errors()+hc_qualification_errors()
 if e:print("\n".join(e),file=sys.stderr);return 1
 print("validated fifteen exact routes, including restricted qualified OTP-H-GAPCVP, OTP-B1-BINARY-CODES, OTP-A-SPHERE-PACKING, OTP-F-EHRHART, OTP-J1-COMPACTNESS, OTP-J2-TWO-DEGENERATE, and OTP-C-PERMANENT routes")
 return 0
if __name__=="__main__":raise SystemExit(main())
