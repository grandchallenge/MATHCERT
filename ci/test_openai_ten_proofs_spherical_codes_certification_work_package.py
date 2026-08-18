#!/usr/bin/env python3
from __future__ import annotations
import copy, json
import validate_openai_ten_proofs_spherical_codes_certification_work_package as v

def mutate(base,path,value):
 out=copy.deepcopy(base); cur=out
 for k in path[:-1]: cur=cur[k]
 cur[path[-1]]=value; return out
def reject(label,record):
 if not v.validation_errors(record=record): raise AssertionError(f'{label}: mutation was accepted')
def main():
 base=json.loads(v.RECORD_PATH.read_text(encoding='utf-8'))
 if v.validation_errors(): raise AssertionError('canonical B2 work package does not validate')
 reject('source root drift',mutate(base,('authority','official_subject','commit'),'0'*40))
 reject('Solve packet drift',mutate(base,('authority','producer_packet','digest'),'0'*40))
 reject('Forge semantic drift',mutate(base,('authority','forge_semantic','digest'),'0'*40))
 swapped=copy.deepcopy(base); swapped['target_scope']['lean_theorems'][0],swapped['target_scope']['lean_theorems'][1]=swapped['target_scope']['lean_theorems'][1],swapped['target_scope']['lean_theorems'][0]; reject('target reorder',swapped)
 pred=copy.deepcopy(base); pred['target_scope']['predecessor_seven_target_surface_authorized']=True; reject('predecessor seven-target authority inflation',pred)
 cls=copy.deepcopy(base); cls['target_scope']['classifications'][3]='source_faithful_exact_projection'; reject('exact 0.39661 source classification inflation',cls)
 q=copy.deepcopy(base); q['target_scope']['mandatory_qualifications'].pop(0); reject('predecessor noninheritance qualification erasure',q)
 q=copy.deepcopy(base); q['target_scope']['mandatory_qualifications'].pop(1); reject('exact 0.39661 non-verbatim qualification erasure',q)
 q=copy.deepcopy(base); q['target_scope']['mandatory_qualifications'].pop(2); reject('0.39661 plus o1 strengthening boundary erasure',q)
 q=copy.deepcopy(base); q['target_scope']['mandatory_qualifications'].pop(3); reject('hierarchy/interlacing/localization qualification erasure',q)
 nv=copy.deepcopy(base); nv['target_scope']['nonvacuity']['evidence'].pop(); reject('nonvacuity erasure',nv)
 ax=copy.deepcopy(base); ax['execution_contract']['permitted_axioms'].append('sorryAx'); reject('axiom inflation',ax)
 holes=copy.deepcopy(base); holes['execution_contract']['challenge_sorry_warning_count']=7; reject('predecessor challenge-hole surface substitution',holes)
 agg=copy.deepcopy(base); agg['execution_contract']['deterministic_commands'][1]='lake build All'; reject('aggregate replay substitution',agg)
 for field,value in [('route_registered',True),('may_adjudicate',True),('adjudication',{'state':'qualified'}),('cert_output',{'certificate':'invented'}),('mathematical_target_proved',True),('aggregate_authority',True),('may_promote_claim',True)]: reject(f'authority inflation {field}',mutate(base,('route_state',field),value))
 extra=copy.deepcopy(base); extra['new_authority']=True; reject('schema openness',extra)
 if not v.validation_errors(routes_blob_override='0'*40): raise AssertionError('route registry drift accepted')
 if not v.validation_errors(predecessor_blob_override='0'*40): raise AssertionError('B1 predecessor drift accepted')
 if not v.validation_errors(intake_blob_override='0'*40): raise AssertionError('B2 intake drift accepted')
 print('OTP-B2-SPHERICAL-CODES work-package adversarial mutation suite: PASS')
if __name__=='__main__': main()
