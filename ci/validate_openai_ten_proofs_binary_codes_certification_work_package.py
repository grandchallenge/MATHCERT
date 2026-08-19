#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, json, sys
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
RECORD_PATH=ROOT/'governance/result_family_work_package_successors/OTP-B1-BINARY-CODES-CERT-WP-001.json'
SCHEMA_PATH=ROOT/'schemas/openai_ten_proofs_binary_codes_certification_work_package.schema.json'
INTAKE_PATH=ROOT/'governance/result_family_intake_successors/OTP-B1-BINARY-CODES.json'
PREDECESSOR_WP=ROOT/'governance/result_family_work_package_successors/OTP-H-GAPCVP-CERT-WP-001.json'
ROUTES=ROOT/'governance/certification_routes.json'
EXPECTED_RECORD_BLOB='19e1eaf5e24ce212bb020c8c40d4177ff5b4f8f9'
EXPECTED_INTAKE_BLOB='9ba1e66679d5d46aceef16164194147d8fac530a'
EXPECTED_PREDECESSOR_WP_BLOB='0f811d163f0d36b028cf6539963e2cf278517137'
PRE_REGISTRATION_ROUTES_BLOB='2d17473b4731aa9d9c630b1e7777ad4bd794d993'
A_REGISTRATION_ROUTES_BLOB='b9bb0dc9e18856f50a88162df37c20c034327439'
FUTURE_ROUTE_ID='MC-ROUTE-OTP-B1-BINARY-CODES'
TARGETS=['MetricCodes.Hamming.binaryRate_lt_classicalRate','MetricCodes.Hamming.exists_binaryRate_improvement','MetricCodes.Johnson.binaryRate_le_combinedVariationalRate','MetricCodes.MRRW.strict_mrrw2','MetricCodes.Johnson.binaryRate_lt_mrrw','MetricCodes.Johnson.exists_binaryRate_mrrw_improvement']
CLASSES=['source_faithful_derived_consequence','derived_positive_margin_certificate','source_faithful_exact_projection','source_faithful_exact_projection','source_faithful_derived_consequence','derived_positive_margin_certificate']
QUALS=['The two positive-margin existential targets are derived certificate normal forms, not source-printed verbatim statements.','The Lean sInf representation of M2 is source-equivalent only through the protected minimizer existence and attainment proof on the target domain.','Binary-rate logarithm base, ceiling convention, strict spectral feasibility and variational domains remain exactly as bound by the protected Forge audit.','No whole-chapter semantic equivalence or proof-body comparison is transferred by this packet.','Forge replay and semantic admission do not independently certify proof correctness.']
NONVAC=['The target parameter domain 0<delta<1/2 is inhabited, for example by delta=1/4.','Hamming.codeNumber_pos proves every finite codeNumber n d is positive using a singleton code.','Hamming.rateSet_nonempty_of_interior proves the whole-cube variational set is nonempty for every 0<delta<1/2.','Johnson.rateSet_nonempty_of_interior proves the constant-weight variational set is nonempty for every 0<delta<1/2.','MetricCodes.MRRW.exists_mrrw_minimizer proves the MRRW objective attains its minimum on [0,1-2delta].','The two positive-margin targets use explicit positive differences supplied by the strict source-faithful inequalities rather than an empty-domain implication.']

def load(p): return json.loads(p.read_text(encoding='utf-8'))
def blob(p):
 d=p.read_bytes(); return hashlib.sha1(f'blob {len(d)}\0'.encode()+d,usedforsecurity=False).hexdigest()
def imported(path,name):
 spec=importlib.util.spec_from_file_location(name,path); assert spec and spec.loader
 m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
 try:
  if hasattr(m,'validation_errors'): return list(m.validation_errors())
  m.validate_record(m.load_record()); m.validate_repository_guards(); return []
 except Exception as e: return [str(e)]
def validation_errors(record=None,*,record_blob_override=None,intake_blob_override=None,predecessor_blob_override=None,routes_blob_override=None):
 r=load(RECORD_PATH) if record is None else record; errors=[]
 for e in Draft202012Validator(load(SCHEMA_PATH)).iter_errors(r): errors.append(f'schema: {e.message}')
 if (blob(RECORD_PATH) if record_blob_override is None else record_blob_override)!=EXPECTED_RECORD_BLOB: errors.append('B1 work-package record blob drift')
 if (blob(INTAKE_PATH) if intake_blob_override is None else intake_blob_override)!=EXPECTED_INTAKE_BLOB: errors.append('protected B1 intake drift')
 if (blob(PREDECESSOR_WP) if predecessor_blob_override is None else predecessor_blob_override)!=EXPECTED_PREDECESSOR_WP_BLOB: errors.append('protected H predecessor work-package drift')
 routes_blob=blob(ROUTES) if routes_blob_override is None else routes_blob_override
 if routes_blob not in {PRE_REGISTRATION_ROUTES_BLOB,A_REGISTRATION_ROUTES_BLOB}: errors.append('certification route registry is neither protected work-package snapshot nor exact A registration successor')
 ie=imported(ROOT/'ci/validate_openai_ten_proofs_binary_codes_intake_successor.py','b1_intake')
 if ie: errors.append('protected B1 intake validation failed: '+'; '.join(ie))
 pe=imported(ROOT/'ci/validate_openai_ten_proofs_gapcvp_certification_work_package.py','h_wp')
 if pe: errors.append('protected H predecessor work-package validation failed: '+'; '.join(pe))
 a=r.get('authority',{})
 if a.get('protected_mathcert_base')!='10e6f3ee20d7a6e89feb27aef0115fa27710d5e4': errors.append('protected MATHCERT base drift')
 if a.get('cert_intake_merge')!='5bddc3eb7d02638cf4fe959accfbfeade4964592': errors.append('B1 intake merge drift')
 if a.get('intake_record',{}).get('digest')!=EXPECTED_INTAKE_BLOB: errors.append('B1 intake binding drift')
 if a.get('producer_packet',{}).get('digest')!='1847dd7a17cda51cb02f017766c59d372811fb12': errors.append('Solve producer packet drift')
 if a.get('forge_semantic',{}).get('digest')!='0ab4d973bc046084e9d2dc6c7552ab5428d7412d': errors.append('Forge semantic record drift')
 o=a.get('official_subject',{})
 if o.get('commit')!='94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6' or o.get('tree')!='174289e4d4958cb0509874e6e53400e098213de7': errors.append('official source root/tree drift')
 ex=r.get('execution_contract',{})
 if ex.get('deterministic_commands')!=['lake exe cache get','lake build MetricCodes','lake exe comparator ComparatorChallenges/B_BinaryCodes.json']: errors.append('deterministic replay command drift')
 if ex.get('expected_outputs')!=['Nanoda kernel accepts the solution','Lean default kernel accepts the solution','Your solution is okay!','OTP_SUCCESSOR_COMPARATOR=ACCEPT']: errors.append('expected replay-output drift')
 if ex.get('permitted_axioms')!=['propext','Quot.sound','Classical.choice']: errors.append('permitted-axiom boundary drift')
 if ex.get('expected_exported_target_count')!=6: errors.append('export-count drift')
 s=r.get('target_scope',{})
 if s.get('lean_theorems')!=TARGETS: errors.append('B1 target membership/order drift')
 if s.get('classifications')!=CLASSES: errors.append('B1 classification drift')
 if s.get('mandatory_qualifications')!=QUALS: errors.append('B1 mandatory qualification drift')
 if s.get('nonvacuity',{}).get('evidence')!=NONVAC: errors.append('B1 nonvacuity evidence drift')
 if [x.get('theorem') for x in s.get('target_acceptance',[])]!=TARGETS: errors.append('B1 target-acceptance alignment drift')
 route=r.get('route_state',{})
 zero={'certification_route_registry_entry':None,'route_registered':False,'may_adjudicate':False,'adjudication':None,'cert_output':None,'mathematical_target_proved':False,'aggregate_authority':False,'may_promote_claim':False}
 if any(route.get(k)!=v for k,v in zero.items()): errors.append('B1 historical work-package route/adjudication/output/proof authority inflation')
 if FUTURE_ROUTE_ID in [x.get('route_id') for x in load(ROUTES).get('routes',[]) if isinstance(x,dict)]: errors.append('future B1 route already registered')
 return errors

def main():
 e=validation_errors()
 if e: print('\n'.join(e),file=sys.stderr); return 1
 print('OTP-B1-BINARY-CODES executable certification work package validation: PASS; immutable work-package authority preserved across exact separately governed A route registration'); return 0
if __name__=='__main__': raise SystemExit(main())
