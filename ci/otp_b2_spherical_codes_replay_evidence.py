#!/usr/bin/env python3
from __future__ import annotations
import base64, hashlib, io, json, subprocess, sys, tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RECORD=ROOT/"governance/result_family_replay_evidence_successors/OTP-B2-SPHERICAL-CODES.json"
SCHEMA=ROOT/"schemas/openai_ten_proofs_spherical_codes_replay_evidence.schema.json"
ROUTES=ROOT/"governance/certification_routes.json"
BUNDLE=ROOT/"evidence/openai_ten_proofs_successors/b2-spherical-codes.tar.gz.b64"
WP=ROOT/"governance/result_family_work_package_successors/OTP-B2-SPHERICAL-CODES-CERT-WP-001.json"
EXPECTED_WP_BLOB="50dc2c9c5bc8aad49f22414536102cef0e82ce20"
PRODUCER_HEAD="a7106f64664e11141e82eb0d5402bd2e85a381b5"
FAMILY="OTP-B2-SPHERICAL-CODES"
REQUIRED_MEMBERS=['environment-manifest.json', 'source-identity-report.txt', 'family-replay-log.txt', 'target-export-report.json', 'comparator-result.json', 'lean-kernel-result.json', 'nanoda-result.json', 'theorem-axiom-report.json', 'semantic-concordance-attestation.json', 'nonvacuity-attestation.json', 'hierarchy-domain-attestation.json', 'numerical-strengthening-attestation.json', 'trust-boundary-scan.txt', 'independent-review-attestation.json', 'evidence-summary.json']

def load(p): return json.loads(p.read_text(encoding="utf-8"))
def git(*args): return subprocess.run(["git","-C",str(ROOT),*args],text=True,capture_output=True)
def find_family_route(node):
    if isinstance(node,dict):
        if node.get("route_id")=="MC-ROUTE-OTP-B2-SPHERICAL-CODES" or node.get("campaign_id")==FAMILY: return True
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
        p=git("rev-parse",f"HEAD:governance/result_family_work_package_successors/OTP-B2-SPHERICAL-CODES-CERT-WP-001.json")
        if p.returncode or p.stdout.strip()!=EXPECTED_WP_BLOB: errors.append("protected work-package blob drift")
        a=git("merge-base","--is-ancestor",PRODUCER_HEAD,"HEAD")
        if a.returncode: errors.append("producer replay head is not ancestor of final candidate")
        if find_family_route(load(ROUTES)): errors.append("family route exists during replay-evidence stage")
    return errors

def main():
    e=validation_errors()
    if e: print("\n".join(e),file=sys.stderr); return 1
    print("validated B2 retained replay evidence: exact producer bundle, zero route/output authority, final-head replay/review still required")
    return 0
if __name__=="__main__": raise SystemExit(main())
