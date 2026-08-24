#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "governance/result_family_output_contracts/OTP-A-SPHERE-PACKING.json"
SCHEMA = ROOT / "schemas/otp_a_sphere_packing_output_contract.schema.json"
FUTURE_SCHEMA = ROOT / "schemas/otp_a_sphere_packing_qualified_output.schema.json"
ROUTES = ROOT / "governance/certification_routes.json"
ADJUDICATION = ROOT / "governance/result_family_adjudications/OTP-A-SPHERE-PACKING.json"
TARGETS = ["PackingBounds.FullMain.exact_limit","PackingBounds.FullMain.exact_binary_exponent","PackingBounds.PackingBridge.sphere_packing_sharp_asymptotic_upper","PackingBounds.sharpFullCohnElkiesManuscriptConclusions"]
CLASSES = ["direct_source_theorem_projection_modulo_proved_full_radial_equivalence","derived_base_two_logarithmic_consequence","source_faithful_displayed_consequence_with_proved_scale_normalization","source_faithful_derived_composite_certificate"]
QUALIFICATIONS = ["The ten-field composite is not one manuscript-verbatim theorem.","The 30-decimal base-two exponent enclosure is a formal numerical consequence, not manuscript-authored precision.","Positive-rescaling invariance and unit-separation supremum equivalence remain required for the packing bridge.","The explicit little-o witness is a normal form only and is not a stronger asymptotic-rate claim.","No whole-chapter or full proof-body equivalence is established."]
def load(path: Path): return json.loads(path.read_text(encoding="utf-8"))
def recursive_closure_errors(schema, path="$", seen=None):
    if seen is None: seen=set()
    errors=[]
    if not isinstance(schema,dict): return errors
    ident=id(schema)
    if ident in seen: return errors
    seen.add(ident)
    if schema.get("type")=="object":
        if schema.get("additionalProperties") is not False: errors.append(f"open object schema at {path}")
        for key,value in schema.get("properties",{}).items(): errors += recursive_closure_errors(value,f"{path}.properties.{key}",seen)
    for combiner in ("allOf","anyOf","oneOf"):
        for i,value in enumerate(schema.get(combiner,[])): errors += recursive_closure_errors(value,f"{path}.{combiner}[{i}]",seen)
    for key in ("items","not","if","then","else"):
        value=schema.get(key)
        if isinstance(value,dict): errors += recursive_closure_errors(value,f"{path}.{key}",seen)
    return errors
def validation_errors(record=None, schema=None, future_schema=None):
    r=load(RECORD) if record is None else record; s=load(SCHEMA) if schema is None else schema; fs=load(FUTURE_SCHEMA) if future_schema is None else future_schema; routes=load(ROUTES); adjudication=load(ADJUDICATION); errors=[]
    errors += recursive_closure_errors(s)
    errors += [f"future {x}" for x in recursive_closure_errors(fs)]
    errors += [f"schema: {e.message}" for e in Draft202012Validator(s).iter_errors(r)]
    if fs.get("properties",{}).get("encoded_targets",{}).get("const") != TARGETS: errors.append("future qualification schema target drift")
    if fs.get("properties",{}).get("classifications",{}).get("const") != CLASSES: errors.append("future qualification schema classification drift")
    fq=fs.get("properties",{}).get("qualification",{}).get("properties",{})
    if fq.get("disposition",{}).get("const") != "qualified_protected_four_targets_only": errors.append("future qualification schema disposition drift")
    if fq.get("mandatory_qualifications",{}).get("const") != QUALIFICATIONS: errors.append("future qualification schema qualification drift")
    fst=fs.get("properties",{}).get("state",{}).get("properties",{})
    for key in ("mathematical_target_proved","aggregate_authority","may_promote_claim"):
        if fst.get(key,{}).get("const") is not False: errors.append(f"future qualification schema authority inflation: {key}")
    if r.get("contract_id") != "MC-OTP-A-SPHERE-PACKING-OUTPUT-CONTRACT-001": errors.append("contract identity drift")
    if r.get("contract_state") != "design_only": errors.append("premature contract activation")
    pa=r.get("protected_authority",{}); a=pa.get("adjudication",{})
    if pa.get("mathcert_main_at_design_open") != "10d3f5ccd69f45e39ce23d758801bde8c6040401": errors.append("protected design base drift")
    if pa.get("route_registry_git_blob_sha1") != "b9bb0dc9e18856f50a88162df37c20c034327439": errors.append("route registry identity drift")
    if (a.get("git_blob_sha1"),a.get("disposition")) != ("3e0b34dbc74fdbe123f551d559e4f93fc1901c48","adjudication_clear_protected_four_targets_only"): errors.append("adjudication authority drift")
    if adjudication.get("decision",{}).get("disposition") != "adjudication_clear_protected_four_targets_only": errors.append("live adjudication disposition mismatch")
    if adjudication.get("state",{}).get("route_state") != "submitted" or adjudication.get("state",{}).get("cert_output") is not None: errors.append("live A route/output state no longer design-compatible")
    if r.get("output_scope",{}).get("encoded_targets") != TARGETS: errors.append("target scope/order drift")
    if r.get("output_scope",{}).get("classifications") != CLASSES: errors.append("classification drift")
    q=r.get("qualification_semantics",{}); f=r.get("future_certificate",{}); p=r.get("publication_protocol",{}); st=r.get("state",{})
    if q.get("permitted_disposition") != "qualified_protected_four_targets_only": errors.append("future disposition inflation")
    if q.get("mandatory_qualifications") != QUALIFICATIONS: errors.append("mandatory qualification drift")
    if q.get("permitted_axioms") != ["propext","Quot.sound","Classical.choice"]: errors.append("axiom drift")
    if (f.get("certificate_id"),f.get("disposition"),f.get("mathematical_target_proved")) != ("MC-OTP-A-SPHERE-PACKING-QUAL-001","qualified_protected_four_targets_only",False): errors.append("future certificate drift")
    for key in ("certificate_content_commit_first","route_transition_commit_must_descend_from_certificate_content_commit","route_transition_must_change_only_a_route_semantics","route_transition_must_preserve_exact_target_set","route_transition_must_insert_exactly_one_cert_output","certificate_must_not_name_its_own_containing_commit","squash_merge_prohibited","rebase_merge_prohibited","route_first_ordering_prohibited","partial_state_on_protected_main_prohibited"):
        if p.get(key) is not True: errors.append(f"publication protection weakened: {key}")
    if p.get("protected_merge_method") != "merge": errors.append("non ancestry-preserving merge permitted")
    expected={"route_state":"submitted","cert_output":None,"mathematical_target_proved":False,"may_issue_output":False,"may_promote_claim":False,"aggregate_output":False,"manuscript_decimal_precision_attributed":False,"scale_normalization_boundary_required":True,"little_o_strengthened":False,"composite_is_single_verbatim_source_theorem":False}
    if st != expected: errors.append("design-only zero-authority state drift")
    route=[x for x in routes.get("routes",[]) if x.get("route_id")=="MC-ROUTE-OTP-A-SPHERE-PACKING"]
    if len(route)!=1 or route[0].get("intake_status") != "submitted" or route[0].get("cert_output") is not None: errors.append("live A route is not submitted/null")
    boundary=str(r.get("claim_boundary",""))
    for token in ("does not issue a certificate","30-decimal","normalization boundary","little-o","aggregate OpenAI Ten Proofs authority","squash"):
        if token not in boundary: errors.append(f"claim boundary missing {token}")
    return errors
def main():
    e=validation_errors()
    if e: print("\n".join(e),file=sys.stderr); return 1
    print("validated A sphere-packing design-only restricted-output contract and recursively closed future qualification schema"); return 0
if __name__ == "__main__": raise SystemExit(main())
