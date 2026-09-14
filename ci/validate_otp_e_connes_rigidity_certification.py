#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
ADJUDICATION=ROOT/"governance/result_family_adjudications/OTP-E-CONNES-RIGIDITY.json";CONTRACT=ROOT/"governance/result_family_output_contracts/OTP-E-CONNES-RIGIDITY.json";CERTIFICATE=ROOT/"certificates/formal_sources/MC-OTP-E-CONNES-RIGIDITY-001.json";WORK_PACKAGE=ROOT/"governance/result_family_work_package_successors/OTP-E-CONNES-RIGIDITY-CERT-WP-001.json";INTAKE=ROOT/"governance/result_family_intake_successors/OTP-E-CONNES-RIGIDITY.json";ROUTES=ROOT/"governance/certification_routes.json"
FAMILY="OTP-E-CONNES-RIGIDITY";ROUTE_ID="MC-ROUTE-OTP-E-CONNES-RIGIDITY";CONTENT_COMMIT="22d9ca44a64ec71aa4a0b77d87b55017ccf9949a"
CERTIFICATE_BLOB="e135e4d7cd4eb752b25e1a940f970f224465191e";ADJUDICATION_BLOB="3b8e476821590b62c16183fbd577d5db87e4aa3a";CONTRACT_BLOB="4fccf54bc3d35642ddf074f24b0624c13e2f8154";WORK_PACKAGE_BLOB="00400006cfa7d7dde1b04b8e8564c53f61a46450";INTAKE_BLOB="8ec4bbee975ab1da957cd4f03f1d63aaf34a32fc"
TARGETS=["ConnesRigidity.exists_nonisomorphic_propertyT_icc_groups_with_isomorphic_factors","ConnesRigidity.exists_infinite_pairwise_nonisomorphic_propertyT_icc_groups_with_isomorphic_factors"]
CLASSIFICATIONS=["source_faithful_two_group_consequence_with_structured_factor_isomorphism","source_faithful_theorem_1_2_projection_with_derived_pairwise_factor_transitivity"]
QUALIFICATIONS=["Only current ConnesRigidity.* declarations are authoritative; no identity or downstream authority is inferred from predecessor ConnesRigidity2.* names.","TracialGroupFactorEquiv is a source-construction-faithful spatial/tracial refinement, not verbatim Theorem 1.2 or Corollary 5.10 wording.","The formal projection-supremum normality predicate is not claimed equivalent to every analytic notion of normality.","The infinite target's all-pairs Gamma factor isomorphism is a derived symmetry/transitivity consequence through Lambda, not a separately printed source clause.","The property-(T) universe scope and finite-generation predicate remain exactly as protected by the Forge audit.","No whole-chapter semantic equivalence or proof-body comparison is transferred."]
def load(p:Path)->Any:return json.loads(p.read_text(encoding="utf-8"))
def blob(p:Path)->str:
 b=p.read_bytes();return hashlib.sha1(f"blob {len(b)}\0".encode()+b,usedforsecurity=False).hexdigest()
def validation_errors(*,adjudication:Any|None=None,contract:Any|None=None,certificate:Any|None=None,work_package:Any|None=None,intake:Any|None=None,routes:Any|None=None,local_blobs:dict[str,str]|None=None,check_history:bool=True)->list[str]:
 r={"adjudication":load(ADJUDICATION) if adjudication is None else adjudication,"contract":load(CONTRACT) if contract is None else contract,"certificate":load(CERTIFICATE) if certificate is None else certificate,"work_package":load(WORK_PACKAGE) if work_package is None else work_package,"intake":load(INTAKE) if intake is None else intake,"routes":load(ROUTES) if routes is None else routes};h={"adjudication":blob(ADJUDICATION),"contract":blob(CONTRACT),"certificate":blob(CERTIFICATE),"work_package":blob(WORK_PACKAGE),"intake":blob(INTAKE)};h.update(local_blobs or {});e=[]
 for k,x in {"adjudication":ADJUDICATION_BLOB,"contract":CONTRACT_BLOB,"certificate":CERTIFICATE_BLOB,"work_package":WORK_PACKAGE_BLOB,"intake":INTAKE_BLOB}.items():
  if h.get(k)!=x:e.append(f"{k} blob drift")
 if check_history:
  if subprocess.run(["git","merge-base","--is-ancestor",CONTENT_COMMIT,"HEAD"],cwd=ROOT).returncode:e.append("certificate-content commit is not an ancestor of route transition")
  if "certificates/formal_sources/MC-OTP-E-CONNES-RIGIDITY-001.json" in subprocess.check_output(["git","diff","--name-only",f"{CONTENT_COMMIT}..HEAD"],cwd=ROOT,text=True).splitlines():e.append("certificate changed after certificate-content commit")
 adj,con,cert,wp,intake_record,routes_record=(r[x] for x in ("adjudication","contract","certificate","work_package","intake","routes"))
 for label,x in (("adjudication",adj),("contract",con),("certificate",cert)):
  if x.get("result_family")!=FAMILY or x.get("route_id")!=ROUTE_ID:e.append(f"{label} identity drift")
 for label,x in (("adjudication",adj),("certificate",cert)):
  if x.get("encoded_targets")!=TARGETS or x.get("classifications")!=CLASSIFICATIONS:e.append(f"{label} target or classification drift")
 if adj.get("mandatory_qualifications")!=QUALIFICATIONS:e.append("adjudication qualification drift")
 if adj.get("decision",{}).get("disposition")!="adjudication_clear_protected_two_targets_only":e.append("adjudication disposition drift")
 for k in ("fresh_exact_head_E_replay_required","exact_head_cert_gcl_and_routing_required","fresh_non_author_operator_algebra_group_theory_Lean_specialist_approval_required","expected_head_protected_merge_required","protected_main_readback_required","head_change_requires_revalidation_and_reapproval"):
  if adj.get("binding_gate",{}).get(k) is not True:e.append(f"binding gate removed: {k}")
 if con.get("output_scope",{}).get("encoded_targets")!=TARGETS or con.get("output_scope",{}).get("classifications")!=CLASSIFICATIONS:e.append("output contract scope drift")
 for k in ("certificate_content_commit_first","route_transition_commit_must_descend_from_certificate_content_commit","cert_output_commit_sha_must_equal_certificate_content_commit","cert_output_digest_must_equal_certificate_blob","certificate_must_not_name_its_own_containing_commit","squash_merge_prohibited","rebase_merge_prohibited","partial_state_on_protected_main_prohibited"):
  if con.get("publication_protocol",{}).get(k) is not True:e.append(f"publication control removed: {k}")
 q=cert.get("qualification",{})
 if q.get("disposition")!="qualified_protected_two_targets_only" or q.get("mandatory_qualifications")!=QUALIFICATIONS:e.append("certificate qualification drift")
 if q.get("permitted_axioms")!=["propext","Quot.sound","Classical.choice"]:e.append("certificate permitted-axiom drift")
 if cert.get("state")!={"mathematical_target_proved":False,"aggregate_authority":False,"may_promote_claim":False}:e.append("certificate authority inflation")
 if wp.get("target_scope",{}).get("lean_theorems")!=TARGETS or wp.get("target_scope",{}).get("classifications")!=CLASSIFICATIONS:e.append("work-package scope drift")
 if wp.get("target_scope",{}).get("mandatory_qualifications")!=QUALIFICATIONS:e.append("work-package qualification drift")
 if intake_record.get("target_scope",{}).get("lean_theorems")!=TARGETS:e.append("protected intake target drift")
 route=next((x for x in routes_record.get("routes",[]) if x.get("campaign_id")==FAMILY),None);expected={"repository":"grandchallenge/MATHCERT","commit_sha":CONTENT_COMMIT,"path":"certificates/formal_sources/MC-OTP-E-CONNES-RIGIDITY-001.json","digest_algorithm":"git_blob_sha1","digest":CERTIFICATE_BLOB}
 if not route:e.append("qualified E route missing")
 else:
  if route.get("route_id")!=ROUTE_ID or route.get("intake_status")!="qualified":e.append("qualified E route state drift")
  if route.get("target_claim_ids")!=TARGETS:e.append("qualified E route target drift")
  if route.get("cert_output")!=expected:e.append("qualified E route output identity drift")
 return e
def main()->int:
 e=validation_errors()
 if e:print("\n".join(e),file=sys.stderr);return 1
 print("validated OTP-E restricted two-target adjudication, certificate-first publication, and qualified route");return 0
if __name__=="__main__":raise SystemExit(main())
