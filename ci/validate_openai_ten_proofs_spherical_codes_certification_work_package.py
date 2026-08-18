#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, json, sys
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
RECORD_PATH=ROOT/'governance/result_family_work_package_successors/OTP-B2-SPHERICAL-CODES-CERT-WP-001.json'
SCHEMA_PATH=ROOT/'schemas/openai_ten_proofs_spherical_codes_certification_work_package.schema.json'
INTAKE_PATH=ROOT/'governance/result_family_intake_successors/OTP-B2-SPHERICAL-CODES.json'
PREDECESSOR_WP=ROOT/'governance/result_family_work_package_successors/OTP-B1-BINARY-CODES-CERT-WP-001.json'
ROUTES=ROOT/'governance/certification_routes.json'
EXPECTED_RECORD_BLOB='50dc2c9c5bc8aad49f22414536102cef0e82ce20'
EXPECTED_INTAKE_BLOB='8b74bd90d703eb1903a0a7a84387867a5df7b4e3'
EXPECTED_PREDECESSOR_WP_BLOB='19e1eaf5e24ce212bb020c8c40d4177ff5b4f8f9'
EXPECTED_ROUTES_BLOB='2d17473b4731aa9d9c630b1e7777ad4bd794d993'
FUTURE_ROUTE_ID='MC-ROUTE-OTP-B2-SPHERICAL-CODES'
TARGETS=['MetricCodes.Johnson.main_binary_theorem','MetricCodes.Spherical.HigherHierarchy.main_general','MetricCodes.Spherical.HigherHierarchy.strict_hierarchy','MetricCodes.Spherical.HigherHierarchy.NumericalMaximum.eventually_kissingNumber_lt_published']
CLASSES=['source_faithful_exact_projection','source_faithful_structured_projection','source_faithful_structured_projection','formal_strengthening_entailing_source_asymptotic_numerical_statement']
QUALS=['The predecessor seven-target spherical surface transfers no authority to this successor intake.','The exact eventual 0.39661 target is not attributed to the manuscript verbatim.',"The source's printed numerical statement is 0.39661+o(1); the exact eventual 0.39661 inequality is a formal strengthening.",'Hierarchy, interlacing and localization domains remain bound to the protected current-root semantic/nonvacuity audit.','Forge replay and semantic admission do not independently certify proof correctness.']
NONVAC=['Binary parameter domain is inhabited, for example delta=1/4.','Spherical parameter domain is inhabited, for example s=1/2.','For positive dimension, a singleton unit-vector code witnesses that the spherical-code carrier is inhabited; this is a semantic witness construction, not a separately replayed Lean theorem.','The hierarchy includes r=0. Taking a0=1 and the empty b-family satisfies Interlacing; Gamma=sqrt(2)/3, so at s=1/2 one has 2*sqrt(2)/3>1/2 and the strict feasibility domain is inhabited.','The Sidelnikov localization interval Icc 0 s is inhabited for s=1/2 because it contains 0.','The numerical target uses a genuine atTop eventual quantifier and is not vacuous through an empty dimension domain.']

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
 if (blob(RECORD_PATH) if record_blob_override is None else record_blob_override)!=EXPECTED_RECORD_BLOB: errors.append('B2 work-package record blob drift')
 if (blob(INTAKE_PATH) if intake_blob_override is None else intake_blob_override)!=EXPECTED_INTAKE_BLOB: errors.append('protected B2 intake drift')
 if (blob(PREDECESSOR_WP) if predecessor_blob_override is None else predecessor_blob_override)!=EXPECTED_PREDECESSOR_WP_BLOB: errors.append('protected B1 predecessor work-package drift')
 if (blob(ROUTES) if routes_blob_override is None else routes_blob_override)!=EXPECTED_ROUTES_BLOB: errors.append('certification route registry changed during work-package-only operation')
 ie=imported(ROOT/'ci/validate_openai_ten_proofs_spherical_codes_intake_successor.py','b2_intake')
 if ie: errors.append('protected B2 intake validation failed: '+'; '.join(ie))
 pe=imported(ROOT/'ci/validate_openai_ten_proofs_binary_codes_certification_work_package.py','b1_wp')
 if pe: errors.append('protected B1 predecessor work-package validation failed: '+'; '.join(pe))
 a=r.get('authority',{})
 if a.get('protected_mathcert_base')!='83a8951a89a72a892d5fdc132d6a22e508d6cdc2': errors.append('protected MATHCERT base drift')
 if a.get('cert_intake_merge')!='9d3af5503f06e1a564562a49ce9f5b439a3d9364': errors.append('B2 intake merge drift')
 if a.get('intake_record',{}).get('digest')!=EXPECTED_INTAKE_BLOB: errors.append('B2 intake binding drift')
 if a.get('producer_packet',{}).get('digest')!='0266c9a431ca4a8e84989913fc626a5086496da6': errors.append('Solve producer packet drift')
 if a.get('forge_semantic',{}).get('digest')!='394d1211757d3fc2bc61b238e914b37245967635': errors.append('Forge semantic record drift')
 o=a.get('official_subject',{})
 if o.get('commit')!='94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6' or o.get('tree')!='174289e4d4958cb0509874e6e53400e098213de7': errors.append('official source root/tree drift')
 ex=r.get('execution_contract',{})
 if ex.get('deterministic_commands')!=['lake exe cache get','lake build MetricCodes','lake exe comparator ComparatorChallenges/B_SphericalCodes.json']: errors.append('deterministic replay command drift')
 if ex.get('expected_outputs')!=['Nanoda kernel accepts the solution','Lean default kernel accepts the solution','Your solution is okay!','OTP_SUCCESSOR_COMPARATOR=ACCEPT']: errors.append('expected replay-output drift')
 if ex.get('permitted_axioms')!=['propext','Quot.sound','Classical.choice']: errors.append('permitted-axiom boundary drift')
 if ex.get('expected_exported_target_count')!=4: errors.append('export-count drift')
 if ex.get('challenge_sorry_warning_count')!=4 or ex.get('challenge_sorry_warnings_are_not_solution_authority') is not True: errors.append('challenge-hole boundary drift')
 s=r.get('target_scope',{})
 if s.get('predecessor_seven_target_surface_authorized') is not False: errors.append('predecessor seven-target spherical authority inflation')
 if s.get('lean_theorems')!=TARGETS: errors.append('B2 target membership/order drift')
 if s.get('classifications')!=CLASSES: errors.append('B2 classification drift')
 if s.get('mandatory_qualifications')!=QUALS: errors.append('B2 mandatory qualification drift')
 if s.get('nonvacuity',{}).get('evidence')!=NONVAC: errors.append('B2 nonvacuity evidence drift')
 if [x.get('theorem') for x in s.get('target_acceptance',[])]!=TARGETS: errors.append('B2 target-acceptance alignment drift')
 if s.get('target_acceptance',[{},{},{},{}])[3].get('semantic_requirement')!='formal_strengthening_entailing_source_asymptotic_numerical_statement': errors.append('exact 0.39661 strengthening classification inflation')
 route=r.get('route_state',{})
 zero={'certification_route_registry_entry':None,'route_registered':False,'may_adjudicate':False,'adjudication':None,'cert_output':None,'mathematical_target_proved':False,'aggregate_authority':False,'may_promote_claim':False}
 if any(route.get(k)!=v for k,v in zero.items()): errors.append('B2 route/adjudication/output/proof authority inflation')
 if FUTURE_ROUTE_ID in [x.get('route_id') for x in load(ROUTES).get('routes',[]) if isinstance(x,dict)]: errors.append('future B2 route already registered')
 return errors

def main():
 e=validation_errors()
 if e: print('\n'.join(e),file=sys.stderr); return 1
 print('OTP-B2-SPHERICAL-CODES executable certification work package validation: PASS; later replay only, no predecessor-seven-target/route/adjudication/output/proof/aggregate authority created'); return 0
if __name__=='__main__': raise SystemExit(main())
