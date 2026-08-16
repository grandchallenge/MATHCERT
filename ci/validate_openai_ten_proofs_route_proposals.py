#!/usr/bin/env python3
from __future__ import annotations
import hashlib,importlib.util,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/"governance/result_family_route_proposals";R=ROOT/"governance/pre_route_candidates/OPENAI_TEN_PROOFS_WP05_ROUTE_PROPOSALS.json"
EXPECTED={"OTP-F-EHRHART":"7b069a003c84ef285259108076a55338fab0bc7f","OTP-J1-COMPACTNESS":"2e541ca5882873ee1c756814642994361b10c78c","OTP-J2-TWO-DEGENERATE":"0692ac15c19328532bdcd3e73b3c8c4371647ac6"};EXPECTED_REGISTRY_BLOB="1883b29ec888ffc487c65b76b35cfcb122f47e51"
def load(p):return json.loads(p.read_text())
def blob(p):
 b=p.read_bytes();return hashlib.sha1(f"blob {len(b)}\0".encode()+b,usedforsecurity=False).hexdigest()
def registration_errors():
 s=importlib.util.spec_from_file_location("reg",ROOT/"ci/validate_openai_ten_proofs_route_registrations_with_j2_successor.py");assert s and s.loader;m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m.validation_errors()
def validation_errors(proposals=None,registry=None,proposal_blobs=None,registry_blob=None,**_):
 e=[];proposals={p.stem:load(p) for p in P.glob("*.json")} if proposals is None else proposals;registry=load(R) if registry is None else registry;proposal_blobs={p.stem:blob(p) for p in P.glob("*.json")} if proposal_blobs is None else proposal_blobs;registry_blob=blob(R) if registry_blob is None else registry_blob
 if set(proposals)!=set(EXPECTED):e.append("proposal membership drift")
 for fam,h in EXPECTED.items():
  q=proposals.get(fam)
  if not isinstance(q,dict):continue
  if proposal_blobs.get(fam)!=h:e.append(f"{fam}: proposal blob drift")
  if q.get("result_family")!=fam or q.get("requested_route_id")!=f"MC-ROUTE-{fam}" or q.get("proposal_state")!="proposed_only":e.append(f"{fam}: proposal identity/state drift")
  ev=q.get("evidence_disposition",{})
  if ev.get("whole_document_byte_equivalence")!="not_established" or ev.get("whole_document_semantic_equivalence")!="not_established" or ev.get("proof_body_compared_in_full") is not False:e.append(f"{fam}: proposal evidence inflation")
  ctl=q.get("route_controls",{})
  if ctl.get("may_register_route") is not False or ctl.get("may_adjudicate") is not False or ctl.get("cert_output") is not None or ctl.get("mathematical_target_proved") is not False or ctl.get("aggregate_route") is not False:e.append(f"{fam}: historical proposal authority drift")
 if registry_blob!=EXPECTED_REGISTRY_BLOB:e.append("proposal registry blob drift")
 if registry.get("state")!={"proposal_count":3,"registered_route_count":0,"adjudication_count":0,"cert_output_count":0,"mathematical_target_proved_count":0,"aggregate_route_count":0}:e.append("historical proposal registry state drift")
 if registry.get("blocked_repair_lanes")!=["OTP-C-PERMANENT","OTP-H-GAPCVP"] or registry.get("unexamined_result_family_count")!=9:e.append("proposal limitations drift")
 if registration_errors():e.append("current route-registration authority invalid")
 return e
def main():
 e=validation_errors()
 if e:print("\n".join(e),file=sys.stderr);return 1
 print("validated immutable proposed-only records against J2-successor-aware separately governed registered routes");return 0
if __name__=="__main__":raise SystemExit(main())
