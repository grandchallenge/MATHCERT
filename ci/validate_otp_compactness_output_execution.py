#!/usr/bin/env python3
from __future__ import annotations

import copy, hashlib, json, subprocess, sys
from pathlib import Path
from typing import Any
from jsonschema import Draft202012Validator

import validate_otp_j2_route_target_successor as j2

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "governance/result_family_output_candidates/OTP-J1-COMPACTNESS.json"
SCHEMA = ROOT / "schemas/otp_compactness_output_execution.schema.json"
CERT = ROOT / "certificates/formal_sources/MC-OTP-J1-COMPACTNESS-001.json"
STAGED_CERT = ROOT / "governance/result_family_output_candidates/staged_certificates/MC-OTP-J1-COMPACTNESS-001.json"
STAGED_ROUTE = ROOT / "governance/result_family_output_candidates/staged_route_transitions/OTP-J1-COMPACTNESS.json"
CERT_SCHEMA = ROOT / "schemas/otp_compactness_qualified_output.schema.json"
CONTRACT = ROOT / "governance/result_family_output_contracts/OTP-J1-COMPACTNESS.json"
ADJ = ROOT / "governance/result_family_adjudications/OTP-J1-COMPACTNESS.json"
ROUTES = ROOT / "governance/certification_routes.json"
BASE = "85b8ee7cbb43e8494b88b1acc998a21ee4f99f23"
CONTENT = "9fba5a8e918028ecc2b4d72abc00b3b72a5194f5"
ROUTE = "53a4df433e7d44255a32a433d9c5e213c2732f19"
CERT_PATH = "certificates/formal_sources/MC-OTP-J1-COMPACTNESS-001.json"
ROUTES_PATH = "governance/certification_routes.json"
ROUTE_ID = "MC-ROUTE-OTP-J1-COMPACTNESS"
TARGETS = ["CompactnessConjecture.quantitativeCompactnessCounterexample", "CompactnessConjecture.compactnessCounterexample_bigO", "CompactnessConjecture.not_erdos_180"]
EXPECTED = {
  "record":"80bbfdc2a60d110c47b9049676484c39a74d1f84",
  "schema":"aa0edc3f01a9b1edf7f3650ff55a1d9383c669fb",
  "certificate":"88531e28951854961e86eec0517356999a391759",
  "staged_route":"1aef6ba851dff92bfb929c1851942099fdec07de",
  "contract":"45aa4a9ec32f56982fc2b5ef5515d53063d5c82b",
  "adjudication":"175fb2d04c80de405655654d9024ffa6eb1f3b46",
  "certificate_schema":"1a96dc9e4e1fe0aabdf82067a829076ce25acff0",
  "routes_before":"aa460c1310a7c81b64b88013b7aa4cfdc056f37b",
  "routes_after":"bc4640661443f1b3de213aaa82a333a4fdb6849b",
}
EXPECTED_OUTPUT = {"repository":"grandchallenge/MATHCERT","commit_sha":CONTENT,"path":CERT_PATH,"digest_algorithm":"git_blob_sha1","digest":EXPECTED["certificate"]}

def load(p: Path) -> Any: return json.loads(p.read_text(encoding="utf-8"))
def blob_bytes(data: bytes) -> str: return hashlib.sha1(f"blob {len(data)}\0".encode()+data, usedforsecurity=False).hexdigest()
def blob(p: Path) -> str: return blob_bytes(p.read_bytes())
def git(*args: str): return subprocess.run(["git",*args], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
def ensure_history():
    if git("rev-parse","--is-shallow-repository").stdout.decode().strip()=="true":
        if git("fetch","--no-tags","--unshallow","origin").returncode: raise RuntimeError("unable to unshallow Compactness output history")
    for c in (BASE,CONTENT,ROUTE):
        if git("cat-file","-e",f"{c}^{{commit}}").returncode and git("fetch","--no-tags","origin",c).returncode: raise RuntimeError(f"unable to fetch governed commit {c}")
def obj(commit: str, path: str) -> bytes|None:
    r=git("show",f"{commit}:{path}"); return r.stdout if r.returncode==0 else None
def obj_blob(commit: str, path: str) -> str|None:
    x=obj(commit,path); return blob_bytes(x) if x is not None else None
def obj_json(commit: str, path: str):
    x=obj(commit,path); return json.loads(x.decode()) if x is not None else None
def parent(c: str) -> str:
    r=git("rev-parse",f"{c}^"); return r.stdout.decode().strip() if r.returncode==0 else ""
def ancestor(a: str,b: str)->bool: return git("merge-base","--is-ancestor",a,b).returncode==0
def files(c: str)->list[str]:
    r=git("diff-tree","--no-commit-id","--name-only","-r",c); return r.stdout.decode().splitlines() if r.returncode==0 else []
def route_of(routes): return next((r for r in routes.get("routes",[]) if r.get("route_id")==ROUTE_ID),{})
def others(routes): return [r for r in routes.get("routes",[]) if r.get("route_id")!=ROUTE_ID]
def receipt():
    ensure_history(); head=git("rev-parse","HEAD").stdout.decode().strip()
    return {"head":head,"base_ancestor":ancestor(BASE,head),"content_parent":parent(CONTENT),"route_parent":parent(ROUTE),"content_route":ancestor(CONTENT,ROUTE),"content_head":ancestor(CONTENT,head),"route_head":ancestor(ROUTE,head),"cert_base":obj_blob(BASE,CERT_PATH),"cert_content":obj_blob(CONTENT,CERT_PATH),"cert_route":obj_blob(ROUTE,CERT_PATH),"cert_head":obj_blob(head,CERT_PATH),"routes_content":obj_blob(CONTENT,ROUTES_PATH),"routes_route":obj_blob(ROUTE,ROUTES_PATH),"routes_head":obj_blob(head,ROUTES_PATH),"json_content":obj_json(CONTENT,ROUTES_PATH),"json_route":obj_json(ROUTE,ROUTES_PATH),"content_files":files(CONTENT),"route_files":files(ROUTE)}

def j2_predecessor_snapshot(routes: dict[str, Any]) -> dict[str, Any]:
    snapshot = copy.deepcopy(routes)
    predecessor = j2.blob_json(j2.PREDECESSOR_ROUTE_BLOB)
    old = j2.find_route(predecessor)
    if old is None:
        return snapshot
    for index, route in enumerate(snapshot.get("routes", [])):
        if isinstance(route, dict) and route.get("route_id") == j2.ROUTE_ID:
            if route.get("target_claim_ids") == j2.NEW_TARGETS:
                snapshot["routes"][index] = copy.deepcopy(old)
            break
    return snapshot

def validation_errors(*, record=None, schema=None, certificate=None, staged_certificate=None, staged_route=None, routes=None, history=None, blobs=None):
    record=load(RECORD) if record is None else record; schema=load(SCHEMA) if schema is None else schema
    certificate=load(CERT) if certificate is None else certificate; staged_certificate=load(STAGED_CERT) if staged_certificate is None else staged_certificate
    staged_route=load(STAGED_ROUTE) if staged_route is None else staged_route; live_routes=load(ROUTES) if routes is None else routes
    j2_errors=j2.validation_errors(routes=copy.deepcopy(live_routes), check_files=False)
    successor_active=not j2_errors and j2.find_route(live_routes).get("target_claim_ids")==j2.NEW_TARGETS
    routes=j2_predecessor_snapshot(live_routes) if successor_active else live_routes
    if history is None:
        try: history=receipt()
        except RuntimeError as e: return [str(e)]
        if successor_active:
            history=copy.deepcopy(history); history["routes_head"]=EXPECTED["routes_after"]
    blobs=blobs or {"record":blob(RECORD),"schema":blob(SCHEMA),"certificate":blob(CERT),"staged_certificate":blob(STAGED_CERT),"staged_route":blob(STAGED_ROUTE),"contract":blob(CONTRACT),"adjudication":blob(ADJ),"certificate_schema":blob(CERT_SCHEMA),"routes_after":EXPECTED["routes_after"] if successor_active else blob(ROUTES)}
    e=list(j2_errors)
    if schema.get("additionalProperties") is not False: e.append("execution schema must remain closed")
    e += [f"execution schema violation: {x.message}" for x in Draft202012Validator(schema).iter_errors(record)]
    for k in ("record","schema","certificate","staged_route","contract","adjudication","certificate_schema","routes_after"):
        if blobs.get(k)!=EXPECTED[k]: e.append(f"{k} blob drift")
    if blobs.get("staged_certificate")!=EXPECTED["certificate"]: e.append("staged certificate blob drift")
    e += [f"certificate schema violation: {x.message}" for x in Draft202012Validator(load(CERT_SCHEMA)).iter_errors(certificate)]
    if certificate!=staged_certificate: e.append("live certificate differs from staged certificate")
    if certificate.get("encoded_targets")!=TARGETS: e.append("certificate target drift")
    if certificate.get("qualification",{}).get("disposition")!="qualified_encoded_targets_only": e.append("certificate disposition drift")
    if any(certificate.get("state",{}).get(k) is not False for k in ("mathematical_target_proved","may_promote_claim","aggregate_output")): e.append("certificate authority inflation")
    if CONTENT in CERT.read_text() or ROUTE in CERT.read_text(): e.append("certificate improperly names publication commits")
    r=route_of(routes)
    if r.get("intake_status")!="qualified" or r.get("cert_output")!=EXPECTED_OUTPUT: e.append("Compactness route output identity drift")
    if r.get("target_claim_ids")!=TARGETS: e.append("Compactness route target drift")
    boundary=str(r.get("claim_boundary","")).lower(); blockers=" ".join(r.get("blockers",[])).lower()
    for token in ("qualified_encoded_targets_only","chapter 10","historical","whole-document","aggregate openai ten proofs"):
        if token not in boundary: e.append(f"route boundary missing {token}")
    for token in ("unrestricted chapter 10","historical or stronger","whole-document byte and semantic equivalence","proof body"):
        if token not in blockers: e.append(f"route blockers missing {token}")
    t=staged_route.get("route_transition",{})
    if t.get("from")!="submitted" or t.get("to")!="qualified" or t.get("certificate_content_commit")!=CONTENT or t.get("route_transition_commit")!=ROUTE or t.get("cert_output")!=EXPECTED_OUTPUT: e.append("staged route transition drift")
    if record.get("execution_commits",{}).get("certificate_content_commit")!=CONTENT or record.get("execution_commits",{}).get("route_transition_commit")!=ROUTE: e.append("execution commit identity drift")
    b=record.get("branch_execution_state",{})
    if b.get("route_state")!="qualified" or b.get("cert_output")!=EXPECTED_OUTPUT: e.append("branch execution state drift")
    if any(b.get(k) is not False for k in ("mathematical_target_proved","may_promote_claim","aggregate_output")): e.append("branch authority inflation")
    if record.get("review_gate",{}).get("recorded_review") is not None: e.append("review prepopulation")
    g=record.get("publication_gate",{})
    for k in ("exact_head_cert_checks_required","exact_head_gcl_conformance_required","linux_windows_output_validation_required","codeql_no_new_alerts_required","fresh_non_author_specialist_approval_required","human_steward_intervention_required_only_for_control_plan_change","squash_merge_prohibited","rebase_merge_prohibited","expected_head_required","certificate_content_commit_must_remain_ancestor","route_transition_commit_must_remain_ancestor","protected_main_atomic_publication_required","partial_protected_main_state_prohibited","head_change_requires_revalidation_and_reapproval"):
        if g.get(k) is not True: e.append(f"publication gate disabled: {k}")
    if g.get("separate_human_steward_authorization_required") is not False or g.get("protected_merge_method")!="merge": e.append("publication authority/method drift")
    for k,msg in (("base_ancestor","protected base not ancestor"),("content_route","certificate commit does not precede route"),("content_head","certificate commit not ancestor of head"),("route_head","route commit not ancestor of head")):
        if history.get(k) is not True: e.append(msg)
    if history.get("content_parent")!=BASE or history.get("route_parent")!=CONTENT: e.append("publication commits are not direct certificate-first chain")
    if history.get("cert_base") is not None: e.append("certificate existed at protected base")
    for k in ("cert_content","cert_route","cert_head"):
        if history.get(k)!=EXPECTED["certificate"]: e.append(f"certificate bytes drift: {k}")
    if history.get("routes_content")!=EXPECTED["routes_before"] or history.get("routes_route")!=EXPECTED["routes_after"] or history.get("routes_head")!=EXPECTED["routes_after"]: e.append("route registry publication bytes drift")
    if history.get("content_files")!=[CERT_PATH] or history.get("route_files")!=[ROUTES_PATH]: e.append("publication commit file scope drift")
    before=history.get("json_content") or {}; after=history.get("json_route") or {}
    if others(before)!=others(after): e.append("non-Compactness route changed in route-transition commit")
    rb,ra=route_of(before),route_of(after)
    if rb.get("intake_status")!="submitted" or rb.get("cert_output") is not None: e.append("pre-transition Compactness route not submitted/null")
    if ra.get("intake_status")!="qualified" or ra.get("cert_output")!=EXPECTED_OUTPUT: e.append("post-transition Compactness route not qualified/exact-output")
    return e

def main():
    e=validation_errors()
    if e:
        print("\n".join(e),file=sys.stderr); print(f"OTP-J1-COMPACTNESS output execution failed with {len(e)} error(s)",file=sys.stderr); return 1
    print(f"validated certificate-first OTP-J1-COMPACTNESS restricted output execution across explicit J2 route successor: content {CONTENT}, route {ROUTE}"); return 0
if __name__=="__main__": raise SystemExit(main())
