#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any
from jsonschema import Draft202012Validator

import validate_otp_j2_route_target_successor as j2

ROOT=Path(__file__).resolve().parents[1]
RECORD=ROOT/"governance/result_family_construction_evidence/OTP-J1-COMPACTNESS.json"
SCHEMA=ROOT/"schemas/openai_ten_proofs_compactness_construction_evidence.schema.json"
SOURCE=ROOT/"evidence/openai_ten_proofs/compactness_construction/source_authority.json"
RECONSTRUCTION=ROOT/"evidence/openai_ten_proofs/compactness_construction/reconstruction.json"
ROUTES=ROOT/"governance/certification_routes.json"
PREDECESSOR=ROOT/"governance/result_family_evidence_refreshes/OTP-J1-COMPACTNESS.json"
CONTRACT=ROOT/"governance/result_family_adjudication_contracts/OTP-J1-COMPACTNESS.json"

BASE="78225ddee5cd85844edded20d157f5ee36859473"
PREDECESSOR_MERGE="5fd92fdd9a17349ac7b804da706f34557cba4137"
PREDECESSOR_BLOB="2d263779147d44d29b6b2e23e2135c947907266e"
CONTRACT_COMMIT="9f5ec626306092a352aa5ba8d9920b6ddb11b8bb"
CONTRACT_BLOB="4288cf2199603ffc90d897062a575a5865326d70"
ROUTE_BLOB="aa460c1310a7c81b64b88013b7aa4cfdc056f37b"
SUCCESSOR_ROUTE_BLOB="bc4640661443f1b3de213aaa82a333a4fdb6849b"
SOURCE_BLOB="148ff82af760bba80c7d16a3a35c58d490dadc95"
RECON_BLOB="ed79d855016a1e642d361e9162ed2b70d267b800"
CURRENT_BYTES=2487031
CURRENT_SHA="ebc561ab5c53dbd240e17a8fdb6fffeb648591eca85dbfc7466f563638f8c566"
PRIOR_BYTES=2266371
PRIOR_SHA="64b900d5fae6fe22f2ae1b8e3b712d20055194a6c81cf343a2455e5898ac7dd6"
HISTORICAL_BYTES=2266052
HISTORICAL_SHA="f318c6508c9d49ef876a5a26cd73928705f96c07bb43e92a0cb35bd3f666ea53"
AUTH_COMMENT=5301501772
ROUTE_ID="MC-ROUTE-OTP-J1-COMPACTNESS"
TARGETS=["CompactnessConjecture.quantitativeCompactnessCounterexample","CompactnessConjecture.compactnessCounterexample_bigO","CompactnessConjecture.not_erdos_180"]
BOUNDARY={"route_state":"submitted","may_adjudicate":False,"adjudication":None,"cert_output":None,"mathematical_target_proved":False,"may_promote_claim":False,"aggregate_adjudication":False,"aggregate_output":False}
SUCCESSOR_OUTPUT={"repository":"grandchallenge/MATHCERT","commit_sha":"9fba5a8e918028ecc2b4d72abc00b3b72a5194f5","path":"certificates/formal_sources/MC-OTP-J1-COMPACTNESS-001.json","digest_algorithm":"git_blob_sha1","digest":"88531e28951854961e86eec0517356999a391759"}

SPEC=importlib.util.spec_from_file_location("compactness_verify",ROOT/"ci/verify_otp_compactness_construction_evidence.py")
assert SPEC and SPEC.loader
VERIFIER=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(VERIFIER)


def load(path:Path)->Any:return json.loads(path.read_text(encoding="utf-8"))
def blob_sha(path:Path)->str:
    b=path.read_bytes()
    return hashlib.sha1(f"blob {len(b)}\0".encode()+b,usedforsecurity=False).hexdigest()
def git(*a:str):return subprocess.run(["git",*a],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
def historical_blob(commit:str,path:Path)->str:
    if git("cat-file","-e",f"{commit}^{{commit}}").returncode:
        git("fetch","--no-tags","origin",commit)
    r=git("rev-parse",f"{commit}:{path.relative_to(ROOT).as_posix()}")
    if r.returncode: raise RuntimeError(r.stderr.strip())
    return r.stdout.strip()
def open_objects(x:Any,loc="$")->list[str]:
    out=[]
    if isinstance(x,dict):
        if x.get("type")=="object" and x.get("additionalProperties") is not False:out.append(loc)
        for k,v in x.items():out+=open_objects(v,f"{loc}.{k}")
    elif isinstance(x,list):
        for i,v in enumerate(x):out+=open_objects(v,f"{loc}[{i}]")
    return out


def validation_errors(*,record=None,schema=None,source=None,reconstruction=None,routes=None,
                      source_blob=None,reconstruction_blob=None,route_blob=None,
                      predecessor_blob=None,contract_blob=None,
                      adjudication_present=None,output_present=None,certificate_present=None)->list[str]:
    record=load(RECORD) if record is None else record
    schema=load(SCHEMA) if schema is None else schema
    source=load(SOURCE) if source is None else source
    reconstruction=load(RECONSTRUCTION) if reconstruction is None else reconstruction
    routes=load(ROUTES) if routes is None else routes
    j2_errors=j2.validation_errors(routes=copy.deepcopy(routes),check_files=False)
    j2_successor_active=not j2_errors and j2.find_route(routes).get("target_claim_ids")==j2.NEW_TARGETS
    source_blob=blob_sha(SOURCE) if source_blob is None else source_blob
    reconstruction_blob=blob_sha(RECONSTRUCTION) if reconstruction_blob is None else reconstruction_blob
    route_blob=(SUCCESSOR_ROUTE_BLOB if j2_successor_active else blob_sha(ROUTES)) if route_blob is None else route_blob
    predecessor_blob=historical_blob(PREDECESSOR_MERGE,PREDECESSOR) if predecessor_blob is None else predecessor_blob
    contract_blob=historical_blob(CONTRACT_COMMIT,CONTRACT) if contract_blob is None else contract_blob
    adjudication_present=False if adjudication_present is None else adjudication_present
    output_present=(ROOT/"governance/result_family_output_candidates/OTP-J1-COMPACTNESS.json").exists() if output_present is None else output_present
    certificate_present=(ROOT/"certificates/formal_sources/MC-OTP-J1-COMPACTNESS-001.json").exists() if certificate_present is None else certificate_present
    successor_absent=not output_present and not certificate_present
    successor_complete=output_present and certificate_present
    e=list(j2_errors)
    if open_objects(schema):e.append("schema contains open object")
    try:
        Draft202012Validator.check_schema(schema)
        e += [f"schema violation: {x.message}" for x in Draft202012Validator(schema).iter_errors(record)]
    except Exception as x:e.append(f"schema invalid: {x}")
    if source_blob!=SOURCE_BLOB or record.get("source_authority",{}).get("manifest_digest")!=SOURCE_BLOB:e.append("source manifest digest drift")
    if reconstruction_blob!=RECON_BLOB or record.get("source_authority",{}).get("reconstruction_digest")!=RECON_BLOB:e.append("reconstruction digest drift")
    if successor_absent:
        if route_blob!=ROUTE_BLOB:e.append("route registry changed during evidence-only operation")
    elif successor_complete:
        if route_blob!=SUCCESSOR_ROUTE_BLOB:e.append("governed Compactness output successor route-registry drift")
    else:e.append("partial Compactness output successor state")
    if predecessor_blob!=PREDECESSOR_BLOB:e.append("protected predecessor blob drift")
    if contract_blob!=CONTRACT_BLOB:e.append("protected design-contract blob drift")
    a=record.get("authority",{})
    if a.get("protected_base")!=BASE:e.append("protected base drift")
    if a.get("human_steward_authorization")!={"comment_id":AUTH_COMMENT,"scope":"construction_and_asymptotic_evidence_only_no_adjudication"}:e.append("authorization receipt drift")
    if a.get("predecessor_evidence_refresh",{}).get("digest")!=PREDECESSOR_BLOB:e.append("predecessor authority drift")
    if a.get("design_contract",{}).get("digest")!=CONTRACT_BLOB:e.append("contract authority drift")
    current=source.get("current_official_revision",{})
    if (current.get("url"),current.get("expected_bytes"),current.get("expected_sha256"),current.get("page_count"),current.get("chapter"),current.get("theorem"),current.get("release_note")) != (
        "https://cdn.openai.com/pdf/ten-proofs-oai.pdf",CURRENT_BYTES,CURRENT_SHA,253,10,"Theorem 1.1","Updated August 6, 2026"):e.append("current source identity drift")
    historical=source.get("historical_source_identities",{})
    if historical.get("admitted_original") != {"bytes":HISTORICAL_BYTES,"reacquirable_exact_bytes":False,"sha256":HISTORICAL_SHA,"status":"identity_preserved_but_bytes_not_retained"}:e.append("historical admitted-source boundary drift")
    if historical.get("prior_current_observation") != {"bytes":PRIOR_BYTES,"sha256":PRIOR_SHA,"status":"protected_forge_source_revision_observation_superseded_by_current_public_release"}:e.append("prior current-observation boundary drift")
    if historical.get("whole_document_equivalence")!="not_established":e.append("whole-document equivalence inflation")
    if source.get("reacquisition_gate",{}).get("required_in_dedicated_ci") is not True:e.append("source reacquisition gate removed")
    if source.get("primary_support",{}).get("arxiv_id")!="1706.06583":e.append("primary literature identity drift")
    release=reconstruction.get("source_release",{})
    expected_release=("https://cdn.openai.com/pdf/ten-proofs-oai.pdf",CURRENT_BYTES,CURRENT_SHA,253,"Updated August 6, 2026",HISTORICAL_BYTES,HISTORICAL_SHA,False,PRIOR_BYTES,PRIOR_SHA,"not_established")
    actual_release=(release.get("current_url"),release.get("current_expected_bytes"),release.get("current_expected_sha256"),release.get("current_expected_page_count"),release.get("current_release_note"),release.get("historical_admitted_bytes"),release.get("historical_admitted_sha256"),release.get("historical_exact_bytes_reacquirable"),release.get("prior_current_observation_bytes"),release.get("prior_current_observation_sha256"),release.get("whole_document_equivalence_between_revisions"))
    if actual_release!=expected_release:e.append("reconstruction source-revision boundary drift")
    e += [f"independent verifier: {x}" for x in VERIFIER.verify(reconstruction)]
    route=next((x for x in routes.get("routes",[]) if x.get("route_id")==ROUTE_ID),None)
    if route is None:e.append("Compactness route missing")
    else:
        if route.get("target_claim_ids")!=TARGETS:e.append("Compactness target drift")
        if successor_absent:
            if route.get("intake_status")!="submitted":e.append("Compactness route promoted")
            if route.get("cert_output") is not None:e.append("Compactness route gained Cert output")
        elif successor_complete:
            if route.get("intake_status")!="qualified":e.append("Compactness output successor route is not qualified")
            if route.get("cert_output")!=SUCCESSOR_OUTPUT:e.append("Compactness output successor identity drift")
    if adjudication_present:e.append("Compactness adjudication inserted")
    if record.get("required_state")!=BOUNDARY:e.append("evidence-only state boundary drift")
    if record.get("disposition")!={"adjudication_authorized":False,"evidence_disposition":"CONSTRUCTION_EVIDENCE_COMPLETE_READY_TO_REQUEST_ADJUDICATION","next_gate":"separately_governed_compactness_adjudication_authorization_and_execution","ready_to_request_adjudication":True}:e.append("evidence disposition drift")
    assessment=record.get("evidence_assessment",{})
    for k,v in {
        "explicit_construction":"independently_reconstructed_and_machine_checked",
        "construction_invariants":"independently_reconstructed_and_machine_checked",
        "upper_bound_bridge":"independently_reconstructed_with_exact_exponent_arithmetic_machine_checked",
        "lower_bound_bridge":"independently_reconstructed_with_exact_parameter_and_growth_arithmetic_machine_checked",
        "source_to_encoded_concordance":"clear_for_exact_three_targets_at_exact_current_official_locus"}.items():
        if assessment.get(k)!=v:e.append(f"assessment drift: {k}")
    if assessment.get("proof_body_compared_in_full") is not False:e.append("proof-body inflation")
    if record.get("review_gate")!={"fresh_non_author_specialist_review_required":True,"minimum_binding_reviewers":1,"must_bind_exact_head":True,"recorded_review":None,"required_state":"APPROVED"}:e.append("review gate drift")
    limits=record.get("preserved_limitations",{})
    for k in ("historical_admitted_pdf_exact_bytes_reacquired","historical_compactness_formulations_admitted","other_result_families_modified","aggregate_openai_ten_proofs_authority","cert_output_authorized","mathematical_proof_promotion_authorized"):
        if limits.get(k) is not False:e.append(f"scope/authority inflation: {k}")
    if limits.get("prior_revision_whole_document_equivalence")!="not_established":e.append("prior-revision equivalence inflation")
    boundary=record.get("claim_boundary","").lower()
    for token in ("does not adjudicate","issue a cert output","mathematical target proved","aggregate openai ten proofs","whole-document equivalence"):
        if token not in boundary:e.append(f"claim boundary missing {token}")
    return e


def main()->int:
    e=validation_errors()
    if e:
        print("\n".join(e),file=sys.stderr); print(f"Compactness construction-evidence validation failed with {len(e)} error(s)",file=sys.stderr); return 1
    print("validated historical complete Compactness construction/asymptotic evidence at exact current official locus; explicit J2 route successor does not rewrite this stage"); return 0
if __name__=="__main__":raise SystemExit(main())