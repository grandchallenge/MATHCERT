#!/usr/bin/env python3
from __future__ import annotations
import base64, hashlib, io, json, subprocess, sys, tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RECORD=ROOT/"governance/result_family_replay_evidence_successors/OTP-H-GAPCVP.json"
SCHEMA=ROOT/"schemas/openai_ten_proofs_gapcvp_replay_evidence.schema.json"
ROUTES=ROOT/"governance/certification_routes.json"
BUNDLE=ROOT/"evidence/openai_ten_proofs_successors/h-gapcvp.tar.gz.b64"
WP=ROOT/"governance/result_family_work_package_successors/OTP-H-GAPCVP-CERT-WP-001.json"
EXPECTED_WP_BLOB="0f811d163f0d36b028cf6539963e2cf278517137"
PRODUCER_HEAD="6c45cc5a83361d4cb622dd795992be16b22fb4fb"
FAMILY="OTP-H-GAPCVP"
REQUIRED_MEMBERS=['environment-manifest.json','source-identity-report.txt','family-replay-log.txt','target-and-promise-export-report.json','comparator-result.json','lean-kernel-result.json','nanoda-result.json','theorem-axiom-report.json','semantic-concordance-attestation.json','promise-nonvacuity-attestation.json','toolchain-identity-report.json','trust-boundary-scan.txt','independent-review-attestation.json','evidence-summary.json']

def load(p): return json.loads(p.read_text(encoding="utf-8"))
def git(*args): return subprocess.run(["git","-C",str(ROOT),*args],text=True,capture_output=True)
def find_family_route(node):
    if isinstance(node,dict):
        if node.get("route_id")=="MC-ROUTE-OTP-H-GAPCVP" or node.get("campaign_id")==FAMILY: return True
        return any(find_family_route(v) for v in node.values())
    if isinstance(node,list): return any(find_family_route(v) for v in node)
    return False

def validation_errors(record=None,schema=None,bundle_text=None,check_repo=True):
    record=load(RECORD) if record is None else record; schema=load(SCHEMA) if schema is None else schema
    errors=[]
    if schema.get("additionalProperties") is not False: errors.append("schema must remain closed")
    if schema.get("required")!=list(record.keys()): errors.append("schema required-key drift")
    props=schema.get("properties",{})
    if set(props)!=set(record): errors.append("schema property drift")
    for k,v in record.items():
        if props.get(k,{}).get("const")!=v: errors.append(f"schema const drift: {k}")
    try:
        raw=base64.b64decode((BUNDLE.read_text() if bundle_text is None else bundle_text).strip(),validate=True)
    except Exception as e:
        errors.append(f"bundle base64 invalid: {e}"); return errors
    rb=record.get("repository_bundle",{})
    if len(raw)!=rb.get("decoded_bytes"): errors.append("bundle byte-length drift")
    if hashlib.sha256(raw).hexdigest()!=rb.get("decoded_sha256"): errors.append("bundle sha256 drift")
    try:
        tf=tarfile.open(fileobj=io.BytesIO(raw),mode="r:gz"); names=set(tf.getnames())
        for name in REQUIRED_MEMBERS:
            if name not in names: errors.append(f"missing retained artifact: {name}")
        summary=json.load(tf.extractfile("evidence-summary.json")); review=json.load(tf.extractfile("independent-review-attestation.json"))
        if summary.get("mathcert_head")!=PRODUCER_HEAD or summary.get("result_family")!=FAMILY: errors.append("producer summary identity drift")
        if summary.get("targets")!=record.get("target_scope",{}).get("lean_theorems"): errors.append("producer target drift")
        if summary.get("promises")!=record.get("target_scope",{}).get("promise_interfaces"): errors.append("producer promise drift")
        for k,e in (("solution_build","pass"),("comparator","accept"),("lean_default_kernel","accept"),("nanoda","accept"),("theorem_axioms","permitted_only"),("trust_boundary_scan","clear")):
            if summary.get(k)!=e: errors.append(f"producer acceptance drift: {k}")
        for k in ("route_proposed","route_registered","may_adjudicate","mathematical_target_proved","aggregate_authority","may_promote_claim"):
            if summary.get(k) is not False: errors.append(f"producer authority inflation: {k}")
        if summary.get("cert_output") is not None or summary.get("adjudication") is not None: errors.append("producer output/adjudication inflation")
        if review!={"state":"pending_final_evidence_head_review","approval_recorded":False,"review_must_bind_final_evidence_head":True,"predeclared_approval_prohibited":True}: errors.append("producer review gate drift")
    except Exception as e: errors.append(f"bundle content invalid: {e}")
    if record.get("producer_replay",{}).get("independent_review_attestation")!="pending_final_evidence_head_review": errors.append("review prematurely recorded")
    rs=record.get("route_state",{})
    if any(rs.get(k) is not False for k in ("route_proposed","route_registered","may_adjudicate","mathematical_target_proved","aggregate_authority","may_promote_claim")): errors.append("route-state authority inflation")
    if rs.get("adjudication") is not None or rs.get("cert_output") is not None or rs.get("certification_route_registry_entry") is not None: errors.append("route-state object inflation")
    if check_repo:
        p=git("rev-parse","HEAD:governance/result_family_work_package_successors/OTP-H-GAPCVP-CERT-WP-001.json")
        if p.returncode or p.stdout.strip()!=EXPECTED_WP_BLOB: errors.append("protected work-package blob drift")
        a=git("merge-base","--is-ancestor",PRODUCER_HEAD,"HEAD")
        if a.returncode: errors.append("producer replay head is not ancestor of final candidate")
        if find_family_route(load(ROUTES)): errors.append("family route exists during replay-evidence stage")
    return errors

def main():
    e=validation_errors()
    if e: print("\n".join(e),file=sys.stderr); return 1
    print("validated H retained replay evidence: exact producer bundle, zero route/output authority, final-head replay/review still required")
    return 0
if __name__=="__main__": raise SystemExit(main())
