#!/usr/bin/env python3
from __future__ import annotations
import hashlib,importlib.util,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PACKAGE_DIR=ROOT/"governance"/"result_family_work_packages";REGISTRY_PATH=ROOT/"governance"/"pre_route_candidates"/"OPENAI_TEN_PROOFS_WP02_WORK_PACKAGES.json"
EXPECTED={"OTP-F-EHRHART":{"blob":"056149e7a659fb6b24b7d7389a3dcd68bb581bcd","tracker":"https://github.com/grandchallenge/MATHCERT/issues/48","route":"MC-ROUTE-OTP-F-EHRHART","intake":"1c6a5f349803bba09b000ceb3f8a53ee3038ca48"},"OTP-J1-COMPACTNESS":{"blob":"d80cade6d99c7ca54f4384a68e178b2f4335a8b2","tracker":"https://github.com/grandchallenge/MATHCERT/issues/49","route":"MC-ROUTE-OTP-J1-COMPACTNESS","intake":"d08eec02d7ee44f3bc2692cf7949c70d8e0f2bbf"},"OTP-J2-TWO-DEGENERATE":{"blob":"dbbc4ab59f21b3f5cb2f313c51f754b9b306389c","tracker":"https://github.com/grandchallenge/MATHCERT/issues/50","route":"MC-ROUTE-OTP-J2-TWO-DEGENERATE","intake":"6e9cfee8f988e357aabdd53e2883220d170b7e60"}}
EXPECTED_REGISTRY_BLOB="997f38fb60ef4d3a43801916113a8e2f1ae34264"
def load(p):return json.loads(p.read_text())
def blob(p):
 b=p.read_bytes();return hashlib.sha1(f"blob {len(b)}\0".encode()+b,usedforsecurity=False).hexdigest()
def registration_errors():
 s=importlib.util.spec_from_file_location("reg",ROOT/"ci/validate_openai_ten_proofs_route_registrations_with_j2_successor.py");assert s and s.loader;m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m.validation_errors()
def validation_errors(registry=None,packages=None,package_blobs=None,**_):
 e=[];registry=load(REGISTRY_PATH) if registry is None else registry
 packages={p.stem.replace("-CERT-WP01",""):load(p) for p in PACKAGE_DIR.glob("*.json")} if packages is None else packages
 package_blobs={p.stem.replace("-CERT-WP01",""):blob(p) for p in PACKAGE_DIR.glob("*.json")} if package_blobs is None else package_blobs
 if set(packages)!=set(EXPECTED):e.append("work package membership drift")
 for fam,x in EXPECTED.items():
  r=packages.get(fam)
  if not isinstance(r,dict):continue
  if r.get("result_family")!=fam or r.get("tracker_issue")!=x["tracker"] or r.get("status")!="authorized_after_protected_mathcert_merge":e.append(f"{fam}: identity/status drift")
  au=r.get("authority",{});ir=au.get("intake_record",{})
  if ir.get("digest")!=x["intake"] or au.get("cert_intake_merge")!="d99d2625ee838945087a91a50923cddc2dcc8d85":e.append(f"{fam}: intake authority drift")
  ex=r.get("execution",{})
  if ex.get("allowed") is not True or ex.get("aggregate_import_required") is not False or ex.get("specialist_review_required") is not True:e.append(f"{fam}: execution control drift")
  rs=r.get("route_state",{})
  if rs.get("requested_route_id")!=x["route"] or rs.get("certification_route_registry_entry") is not None or rs.get("may_adjudicate") is not False or rs.get("mathematical_target_proved") is not False:e.append(f"{fam}: historical work-package route state drift")
  if package_blobs.get(fam)!=x["blob"]:e.append(f"{fam}: work package blob drift")
 if blob(REGISTRY_PATH)!=EXPECTED_REGISTRY_BLOB:e.append("work-package registry blob drift")
 if registry.get("execution_state")!={"authorized_work_package_count":3,"executing_count":0,"evidence_bundle_count":0,"proposed_route_count":0,"registered_route_count":0,"adjudication_count":0,"cert_output_count":0,"mathematical_target_proved_count":0}:e.append("historical work-package state drift")
 if registry.get("blocked_repair_lanes")!=["OTP-C-PERMANENT","OTP-H-GAPCVP"]:e.append("blocked repair lanes drift")
 if registration_errors():e.append("current route-registration authority invalid")
 return e
def main():
 e=validation_errors()
 if e:print("\n".join(e),file=sys.stderr);return 1
 print("validated immutable three-family work packages and their separately governed current route registrations, including the explicit J2 source-faithful successor");return 0
if __name__=="__main__":raise SystemExit(main())
