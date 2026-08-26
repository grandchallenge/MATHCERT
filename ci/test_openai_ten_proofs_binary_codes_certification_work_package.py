#!/usr/bin/env python3
from __future__ import annotations
import copy, json
import validate_openai_ten_proofs_binary_codes_certification_work_package as v

def mutate(base,path,value):
 out=copy.deepcopy(base); cur=out
 for k in path[:-1]: cur=cur[k]
 cur[path[-1]]=value; return out
def reject(label,record):
 if not v.validation_errors(record=record): raise AssertionError(f'{label}: mutation was accepted')
def main():
 base=json.loads(v.RECORD_PATH.read_text(encoding='utf-8'))
 if v.validation_errors(): raise AssertionError('canonical B1 work package does not validate')
 reject('source root drift',mutate(base,('authority','official_subject','commit'),'0'*40))
 reject('Solve packet drift',mutate(base,('authority','producer_packet','digest'),'0'*40))
 reject('Forge semantic drift',mutate(base,('authority','forge_semantic','digest'),'0'*40))
 swapped=copy.deepcopy(base); swapped['target_scope']['lean_theorems'][0],swapped['target_scope']['lean_theorems'][1]=swapped['target_scope']['lean_theorems'][1],swapped['target_scope']['lean_theorems'][0]; reject('target reorder',swapped)
 cls=copy.deepcopy(base); cls['target_scope']['classifications'][1]='source_faithful_exact_projection'; reject('positive-margin classification inflation',cls)
 q=copy.deepcopy(base); q['target_scope']['mandatory_qualifications'].pop(0); reject('positive-margin qualification erasure',q)
 q=copy.deepcopy(base); q['target_scope']['mandatory_qualifications'].pop(1); reject('sInf minimizer bridge erasure',q)
 nv=copy.deepcopy(base); nv['target_scope']['nonvacuity']['evidence'].pop(); reject('nonvacuity erasure',nv)
 ax=copy.deepcopy(base); ax['execution_contract']['permitted_axioms'].append('sorryAx'); reject('axiom inflation',ax)
 agg=copy.deepcopy(base); agg['execution_contract']['deterministic_commands'][1]='lake build All'; reject('aggregate replay substitution',agg)
 for field,value in [('route_registered',True),('may_adjudicate',True),('adjudication',{'state':'qualified'}),('cert_output',{'certificate':'invented'}),('mathematical_target_proved',True),('aggregate_authority',True),('may_promote_claim',True)]: reject(f'authority inflation {field}',mutate(base,('route_state',field),value))
 extra=copy.deepcopy(base); extra['new_authority']=True; reject('schema openness',extra)
 if not v.validation_errors(routes_blob_override='0'*40): raise AssertionError('historical work-package route snapshot blob drift accepted')
 inflated={'routes':[{'route_id':v.FUTURE_ROUTE_ID,'campaign_id':v.FAMILY_ID}]}
 if not v.validation_errors(historical_routes_override=inflated): raise AssertionError('historical B1 route authority inflation accepted')
 clean={'routes':[{'route_id':'OTHER','campaign_id':'OTHER'}]}
 clean_errors=v.validation_errors(historical_routes_override=clean)
 if any('historical work-package route snapshot' in e or 'route authority was present' in e for e in clean_errors): raise AssertionError('clean historical route snapshot rejected')
 if not v.validation_errors(predecessor_blob_override='0'*40): raise AssertionError('H predecessor drift accepted')
 if not v.validation_errors(intake_blob_override='0'*40): raise AssertionError('B1 intake drift accepted')
 print('OTP-B1-BINARY-CODES work-package adversarial mutation suite: PASS')
if __name__=='__main__': main()
