#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
ADJUDICATION=ROOT/"governance/result_family_adjudications/OTP-D-NON-SOFIC.json"
CONTRACT=ROOT/"governance/result_family_output_contracts/OTP-D-NON-SOFIC.json"
CERTIFICATE=ROOT/"certificates/formal_sources/MC-OTP-D-NON-SOFIC-001.json"
WORK_PACKAGE=ROOT/"governance/result_family_work_package_successors/OTP-D-NON-SOFIC-CERT-WP-001.json"
INTAKE=ROOT/"governance/result_family_intake_successors/OTP-D-NON-SOFIC.json"
ROUTES=ROOT/"governance/certification_routes.json"
FAMILY="OTP-D-NON-SOFIC"; ROUTE_ID="MC-ROUTE-OTP-D-NON-SOFIC"
CONTENT_COMMIT="14746625f2f7599c5390da87fa3be42a04502c86"
CERTIFICATE_BLOB="354da3dbf396daed15509013b4b6f7515e72ab4f"
ADJUDICATION_BLOB="97907820d9a012f58518640e36599ea963efccb4"
CONTRACT_BLOB="8c0e1457b23d2cc81a9c69e888321c724ae4c91c"
WORK_PACKAGE_BLOB="b9f771cdde300070ba79f851e7cea7c3ede37a6f"
INTAKE_BLOB="f1578fca3e9a3a5fd95777d0f331b39ef6e99524"
TARGETS=["SoficGroups.SourceTopLevelCompressionFinal.exists_finitelyPresented_nonsofic_group"]
CLASSIFICATIONS=["derived_finitely_presented_nonsofic_consequence_of_source_nonsofic_construction"]
QUALIFICATIONS=[
 "Chapter 3 Theorem 1.1 does not itself state existence of a finitely presented nonsofic group.",
 "The finitely presented witness is a derived formal consequence constructed from a finite failed sofic approximation test.",
 "The source obstruction carrier is related through the proved EL_D(R)/EL_9(R) equivalence and is not definitionally the full unit group.",
 "Group.IsFinitelyPresented remains pinned to Mathlib commit 81a5d257c8e410db227a6665ed08f64fea08e997.",
 "No whole-chapter semantic equivalence or proof-body comparison is transferred."]
def load(path:Path)->Any:return json.loads(path.read_text(encoding="utf-8"))
def blob(path:Path)->str:
 p=path.read_bytes();return hashlib.sha1(f"blob {len(p)}\0".encode()+p,usedforsecurity=False).hexdigest()
def validation_errors(*,adjudication:Any|None=None,contract:Any|None=None,certificate:Any|None=None,work_package:Any|None=None,intake:Any|None=None,routes:Any|None=None,local_blobs:dict[str,str]|None=None,check_history:bool=True)->list[str]:
 records={"adjudication":load(ADJUDICATION) if adjudication is None else adjudication,"contract":load(CONTRACT) if contract is None else contract,"certificate":load(CERTIFICATE) if certificate is None else certificate,"work_package":load(WORK_PACKAGE) if work_package is None else work_package,"intake":load(INTAKE) if intake is None else intake,"routes":load(ROUTES) if routes is None else routes}
 hashes={"adjudication":blob(ADJUDICATION),"contract":blob(CONTRACT),"certificate":blob(CERTIFICATE),"work_package":blob(WORK_PACKAGE),"intake":blob(INTAKE)}
 if local_blobs:hashes.update(local_blobs)
 errors=[]
 for key,expected in {"adjudication":ADJUDICATION_BLOB,"contract":CONTRACT_BLOB,"certificate":CERTIFICATE_BLOB,"work_package":WORK_PACKAGE_BLOB,"intake":INTAKE_BLOB}.items():
  if hashes.get(key)!=expected:errors.append(f"{key} blob drift")
 if check_history:
  if subprocess.run(["git","merge-base","--is-ancestor",CONTENT_COMMIT,"HEAD"],cwd=ROOT).returncode:errors.append("certificate-content commit is not an ancestor of route transition")
  changed=subprocess.check_output(["git","diff","--name-only",f"{CONTENT_COMMIT}..HEAD"],cwd=ROOT,text=True).splitlines()
  if "certificates/formal_sources/MC-OTP-D-NON-SOFIC-001.json" in changed:errors.append("certificate changed after certificate-content commit")
 adj,con,cert,wp,intake_record,routes_record=(records[x] for x in ("adjudication","contract","certificate","work_package","intake","routes"))
 for label,record in (("adjudication",adj),("contract",con),("certificate",cert)):
  if record.get("result_family")!=FAMILY or record.get("route_id")!=ROUTE_ID:errors.append(f"{label} identity drift")
 for label,record in (("adjudication",adj),("certificate",cert)):
  if record.get("encoded_targets")!=TARGETS or record.get("classifications")!=CLASSIFICATIONS:errors.append(f"{label} target or classification drift")
 if adj.get("mandatory_qualifications")!=QUALIFICATIONS:errors.append("adjudication qualification drift")
 if adj.get("decision",{}).get("disposition")!="adjudication_clear_protected_single_derived_target_only":errors.append("adjudication disposition drift")
 for key in ("fresh_exact_head_D_replay_required","exact_head_cert_gcl_and_routing_required","fresh_non_author_geometric_group_theory_Lean_specialist_approval_required","expected_head_protected_merge_required","protected_main_readback_required","head_change_requires_revalidation_and_reapproval"):
  if adj.get("binding_gate",{}).get(key) is not True:errors.append(f"binding gate removed: {key}")
 if con.get("output_scope",{}).get("encoded_targets")!=TARGETS or con.get("output_scope",{}).get("classifications")!=CLASSIFICATIONS:errors.append("output contract scope drift")
 for key in ("certificate_content_commit_first","route_transition_commit_must_descend_from_certificate_content_commit","cert_output_commit_sha_must_equal_certificate_content_commit","cert_output_digest_must_equal_certificate_blob","certificate_must_not_name_its_own_containing_commit","squash_merge_prohibited","rebase_merge_prohibited","partial_state_on_protected_main_prohibited"):
  if con.get("publication_protocol",{}).get(key) is not True:errors.append(f"publication control removed: {key}")
 q=cert.get("qualification",{})
 if q.get("disposition")!="qualified_protected_single_derived_target_only" or q.get("mandatory_qualifications")!=QUALIFICATIONS:errors.append("certificate qualification drift")
 if q.get("permitted_axioms")!=["propext","Classical.choice","Quot.sound"]:errors.append("certificate permitted-axiom drift")
 if cert.get("state")!={"mathematical_target_proved":False,"aggregate_authority":False,"may_promote_claim":False}:errors.append("certificate authority inflation")
 if wp.get("target_scope",{}).get("lean_theorems")!=TARGETS or wp.get("target_scope",{}).get("classifications")!=CLASSIFICATIONS:errors.append("work-package scope drift")
 if wp.get("target_scope",{}).get("mandatory_qualifications")!=QUALIFICATIONS:errors.append("work-package qualification drift")
 if intake_record.get("target_scope",{}).get("lean_theorems")!=TARGETS:errors.append("protected intake target drift")
 route=next((x for x in routes_record.get("routes",[]) if x.get("campaign_id")==FAMILY),None)
 expected={"repository":"grandchallenge/MATHCERT","commit_sha":CONTENT_COMMIT,"path":"certificates/formal_sources/MC-OTP-D-NON-SOFIC-001.json","digest_algorithm":"git_blob_sha1","digest":CERTIFICATE_BLOB}
 if not route:errors.append("qualified D route missing")
 else:
  if route.get("route_id")!=ROUTE_ID or route.get("intake_status")!="qualified":errors.append("qualified D route state drift")
  if route.get("target_claim_ids")!=TARGETS:errors.append("qualified D route target drift")
  if route.get("cert_output")!=expected:errors.append("qualified D route output identity drift")
 return errors
def main()->int:
 e=validation_errors()
 if e:print("\n".join(e),file=sys.stderr);return 1
 print("validated OTP-D restricted single-derived-target adjudication, certificate-first publication, and qualified route");return 0
if __name__=="__main__":raise SystemExit(main())
