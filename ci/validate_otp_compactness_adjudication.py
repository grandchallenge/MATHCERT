#!/usr/bin/env python3
from __future__ import annotations

import base64, hashlib, io, json, subprocess, sys, zipfile
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / 'governance/result_family_adjudications/OTP-J1-COMPACTNESS.json'
SCHEMA = ROOT / 'schemas/openai_ten_proofs_compactness_adjudication.schema.json'
BUNDLE = ROOT / 'evidence/openai_ten_proofs/compactness_adjudication.zip.b64'
INPUT = ROOT / 'governance/result_family_adjudication_execution_inputs/OTP-J1-COMPACTNESS.json'
ROUTES = ROOT / 'governance/certification_routes.json'
CERTIFICATE = ROOT / 'certificates/formal_sources/MC-OTP-J1-COMPACTNESS-001.json'
AUTHORIZED_INPUT_HEAD = '28db9aad66381ff4f8b68a48c18090fa5c5b843b'
AUTHORIZED_INPUT_BLOB = 'c9d8b31579e2bfdb93f99ff74d14f73a2fb603d7'
TARGETS = ['CompactnessConjecture.quantitativeCompactnessCounterexample','CompactnessConjecture.compactnessCounterexample_bigO','CompactnessConjecture.not_erdos_180']
EXPECTED_BLOBS = {
 'governance/result_family_adjudication_contracts/OTP-J1-COMPACTNESS.json':'4288cf2199603ffc90d897062a575a5865326d70',
 'governance/result_family_construction_evidence/OTP-J1-COMPACTNESS.json':'872cdf678412d63df22d1244b3b5c13185f29571',
 'evidence/openai_ten_proofs/compactness_construction/source_authority.json':'148ff82af760bba80c7d16a3a35c58d490dadc95',
 'evidence/openai_ten_proofs/compactness_construction/reconstruction.json':'ed79d855016a1e642d361e9162ed2b70d267b800',
 'governance/certification_routes.json':'aa460c1310a7c81b64b88013b7aa4cfdc056f37b',
}
EXPECTED_FILES = {
 'SHA256SUMS':'789cf36fb51ed97ed81765a969f0283ed726ac68e12677745a44cfeb47bdca82',
 'axiom-check.json':'a73c7b01fe00f52624c109dececaac4d8f35779d0ab005b25e3517e0f1d85a8a',
 'challenge-build.log':'665730c8bdad0399fafcbef574feb200bd6d179afa0356b493bfb6543dca1f7f',
 'comparator.log':'70073ae75b8748cda6dba69161c13f38641dc2af2e14a8360ec94a1b54dad31e',
 'environment.txt':'9225f0fd30eabab93c26fe29c676697a8294944dfa17c239585dc57a026420b5',
 'evidence-summary.json':'2a09d2fa51903b7dbf13c64ac29a6d0993979499780f85d265e54932e3d5abe6',
 'solution-build.log':'ae1e9d97bf81d334c66a08e8d2791d333646eb5d0bf39bd3e48ff0651272d6f3',
 'source-identities.txt':'2d27ed2c84ebae6c2be86bbfd8072bfa92d311025fc91ec6fef5c789108f5f9b',
 'source-revision-report.txt':'c2ab4982c2ec4f6ad11d2b202bfb20b10170476f3e8c9c1e4de182876bea519d',
 'theorem-axioms.log':'25ac1bc67334c2e783e5957dc9ef65a4643cc29c3d240fa34c68b227fc0b94fe',
 'trust-boundary-scan.txt':'9ee8979d7ab41bd2710ca04c310533bafdf0f5e8e1303ca17bf1a0c5c3e0e61c',
}

def load(path: Path): return json.loads(path.read_text(encoding='utf-8'))
def require(c: bool, m: str):
    if not c: raise ValueError(m)
def git_blob(path: Path) -> str:
    return subprocess.check_output(['git','hash-object',str(path)],cwd=ROOT,text=True).strip()
def is_ancestor(a: str) -> bool:
    return subprocess.run(['git','merge-base','--is-ancestor',a,'HEAD'],cwd=ROOT).returncode == 0

def validate_record(record: dict, *, check_repository: bool=True, bundle_bytes: bytes|None=None) -> None:
    errs=sorted(Draft202012Validator(load(SCHEMA)).iter_errors(record),key=lambda e:list(e.path))
    if errs: raise ValueError('schema validation failed: '+'; '.join(e.message for e in errs[:3]))
    require(record['encoded_targets']==TARGETS,'target drift')
    require(record['decision']['disposition']=='adjudication_clear_encoded_targets_only','disposition drift')
    require(record['authority']['human_steward_execution_authorization']['comment_id']==5302142079,'Human Steward authorization drift')
    require(record['authority']['human_steward_execution_authorization']['authorized_input_head']==AUTHORIZED_INPUT_HEAD,'authorized input drift')
    require(record['execution']['successful_execution_head']=='17c081e6a1dbde9716e9e41e9960a90d37b31fb7','successful execution head drift')
    tr=record['execution']['transport_recovery']
    require(tr['official_subject_commit']==tr['mirror_commit']=='e62211d28e3a9131950c89caa6542cfe5eff3bca','subject commit substitution')
    require(tr['official_subject_tree']==tr['mirror_tree']=='2f8e7ac5ae7f157b6b1de636c2c343b1c7a7e365','subject tree substitution')
    require(tr['mirror_role']=='byte_transport_only_no_new_subject_authority','mirror authority inflation')
    require(record['source_assessment']['current_sha256']=='ebc561ab5c53dbd240e17a8fdb6fffeb648591eca85dbfc7466f563638f8c566','current source drift')
    require(record['source_assessment']['current_bytes']==2487031,'current source byte drift')
    require(record['source_assessment']['whole_document_semantic_equivalence']=='not_established','whole-document semantic inflation')
    ev=record['evidence_assessment']
    for key,expected in [('comparator','pass'),('lean_kernel','accept'),('nanoda','accept'),('solution_build','pass'),('challenge_build','pass')]: require(ev[key]==expected,f'{key} not clear')
    require(ev['proof_body_compared_in_full'] is False,'proof body inflation')
    state=record['state']
    require(state=={'route_state':'submitted','adjudication_operation_authorized':True,'adjudication_recorded_on_branch':True,'cert_output':None,'mathematical_target_proved':False,'may_issue_output':False,'may_promote_claim':False,'aggregate_adjudication':False,'aggregate_output':False},'state inflation')
    require(record['review_gate']['recorded_review'] is None,'review prepopulation')
    raw = bundle_bytes if bundle_bytes is not None else base64.b64decode(BUNDLE.read_text(encoding='ascii'))
    require(len(raw)==7081,'retained replay byte drift')
    require(hashlib.sha256(raw).hexdigest()=='985832cb7471b9e666643466ce4dc4aa815e10c86f2123ef0d41f12ebed39e48','retained replay SHA-256 drift')
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        names=sorted(z.namelist()); require(names==sorted(EXPECTED_FILES),'retained replay file-set drift')
        for name,digest in EXPECTED_FILES.items(): require(hashlib.sha256(z.read(name)).hexdigest()==digest,f'retained replay file drift: {name}')
        summary=json.loads(z.read('evidence-summary.json'))
        require(summary['execution']['mathcert_head_sha']=='17c081e6a1dbde9716e9e41e9960a90d37b31fb7','artifact execution head drift')
        require(summary['source_revision']['status']=='current_official_revision_reacquired','source not reacquired')
        require(summary['source_revision']['current_manuscript_sha256']=='ebc561ab5c53dbd240e17a8fdb6fffeb648591eca85dbfc7466f563638f8c566','artifact source drift')
        require(summary['targets']['theorem_names']==TARGETS,'artifact target drift')
        require(summary['results']['comparator']=='pass' and summary['results']['lean_kernel']=='accept' and summary['results']['nanoda']=='accept','artifact checker failure')
        ax=json.loads(z.read('axiom-check.json'))
        require(ax['permitted']==['Classical.choice','Quot.sound','propext'],'permitted axiom set drift')
        require([x['theorem'] for x in ax['reports']]==TARGETS,'axiom theorem set drift')
        require(all(not x['unexpected'] for x in ax['reports']),'unexpected axiom')
        ids=z.read('source-identities.txt').decode()
        for token in ['config_blob=c484ab6f83edebc64c660c06d2ddb7263380084f','challenge_blob=0e9c50d24422cc1016e1621b88bece204056ce33','solution_blob=39fc24a0060b335475af960944baf6b85c3add98']: require(token in ids,f'missing formal input identity: {token}')
        comp=z.read('comparator.log').decode()
        for token in ['Nanoda kernel accepts the solution','Lean default kernel accepts the solution','Your solution is okay!']: require(token in comp,f'missing comparator acceptance: {token}')
        trust=z.read('trust-boundary-scan.txt').decode(); require('solution placeholder/unsafe/custom-axiom scan: clear' in trust and 'aggregate All import scan: clear' in trust,'trust scan drift')
    if not check_repository: return
    require(git_blob(INPUT)==AUTHORIZED_INPUT_BLOB,'frozen execution input bytes changed')
    require(is_ancestor(AUTHORIZED_INPUT_HEAD),'publication head is not descendant of authorized input')
    for rel,expected in EXPECTED_BLOBS.items(): require(git_blob(ROOT/rel)==expected,f'protected authority drift: {rel}')
    ce=load(ROOT/'governance/result_family_construction_evidence/OTP-J1-COMPACTNESS.json')
    require(ce['disposition']['evidence_disposition']=='CONSTRUCTION_EVIDENCE_COMPLETE_READY_TO_REQUEST_ADJUDICATION','construction evidence not complete')
    require(ce['evidence_assessment']['source_to_encoded_concordance']=='clear_for_exact_three_targets_at_exact_current_official_locus','construction concordance not clear')
    routes=load(ROUTES); matches=[r for r in routes['routes'] if r.get('route_id')=='MC-ROUTE-OTP-J1-COMPACTNESS']
    require(len(matches)==1,'route missing/duplicated'); route=matches[0]
    require(route.get('intake_status')=='submitted' and route.get('cert_output') is None and route.get('target_claim_ids')==TARGETS,'live route mutated')
    require(not CERTIFICATE.exists(),'Compactness certificate exists without output authority')

def main()->int:
    try: validate_record(load(RECORD))
    except Exception as exc:
        print(f'OTP-J1-COMPACTNESS adjudication validation failed: {exc}',file=sys.stderr); return 1
    print('validated bounded OTP-J1-COMPACTNESS adjudication: exact targets only, submitted route, no Cert output or proof promotion')
    return 0
if __name__=='__main__': raise SystemExit(main())
