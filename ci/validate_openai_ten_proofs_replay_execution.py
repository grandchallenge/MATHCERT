#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'governance/pre_route_candidates/OPENAI_TEN_PROOFS_WP03_REPLAY_EXECUTION.json';ROUTES=ROOT/'governance/certification_routes.json';WP=ROOT/'governance/pre_route_candidates/OPENAI_TEN_PROOFS_WP02_WORK_PACKAGES.json'
def load(p):return json.loads(p.read_text())
def blob(p):d=p.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d,usedforsecurity=False).hexdigest()
def validation_errors(record=None,routes_blob=None,wp_blob=None):
 r=load(R) if record is None else record;e=[];expected={'state':'formal_replay_completed_pending_source_revision_and_specialist_review','submitted_family_count':3,'completed_family_count':3,'evidence_bundle_count':3,'proposed_route_count':0,'registered_route_count':0,'adjudication_count':0,'cert_output_count':0,'mathematical_target_proved_count':0}
 if r.get('execution_state')!=expected:e.append('completion state drift')
 if r.get('source_revision',{}).get('current_revision_semantic_concordance')!='blocked_pending_forge_audit':e.append('source block removed')
 if r.get('route_controls')!={'global_route_registry_modified':False,'aggregate_route_prohibited':True,'may_adjudicate':False,'may_promote_claim':False}:e.append('route controls drift')
 if (routes_blob or blob(ROUTES))!='5b3e8d48b9f6c5b03ed3dc439bf9e43876e017b1':e.append('routes changed')
 if (wp_blob or blob(WP))!='997f38fb60ef4d3a43801916113a8e2f1ae34264':e.append('work packages changed')
 return e
def main():
 e=validation_errors()
 if e:print('\n'.join(e),file=sys.stderr);return 1
 print('validated completed three-family replay execution with three evidence bundles, blocked source concordance, zero routes, and zero adjudication');return 0
if __name__=='__main__':raise SystemExit(main())
