#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import validate_openai_ten_proofs_sphere_packing_route_registration as sphere

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "governance/result_family_output_contracts/OTP-A-SPHERE-PACKING.json"
SCHEMA = ROOT / "schemas/otp_a_sphere_packing_output_contract.schema.json"
FUTURE_SCHEMA = ROOT / "schemas/otp_a_sphere_packing_qualified_output.schema.json"
ROUTES = ROOT / "governance/certification_routes.json"
ADJUDICATION = ROOT / "governance/result_family_adjudications/OTP-A-SPHERE-PACKING.json"
CERTIFICATE = ROOT / "certificates/formal_sources/MC-OTP-A-SPHERE-PACKING-001.json"

BASE_COMMIT = "8297da39e847bf1e4de4d3b2ce2fc7b8597fee84"
CONTENT_COMMIT = "1815f1b4010122e5bef0438f84da0b06204ba487"
ROUTE_COMMIT = "5600f30aaf28f01d5989cdc8883426c6602a0c79"
CERT_PATH = "certificates/formal_sources/MC-OTP-A-SPHERE-PACKING-001.json"
ROUTES_PATH = "governance/certification_routes.json"
CERT_BLOB = "534e98ad2f00406fc869ea137f802f8cf504798a"
ROUTES_BEFORE_BLOB = "b9bb0dc9e18856f50a88162df37c20c034327439"
ROUTES_AFTER_BLOB = "4d5c8e3f2b33d5148d98e7057991e167938c75bb"
TARGETS = [
    "PackingBounds.FullMain.exact_limit",
    "PackingBounds.FullMain.exact_binary_exponent",
    "PackingBounds.PackingBridge.sphere_packing_sharp_asymptotic_upper",
    "PackingBounds.sharpFullCohnElkiesManuscriptConclusions",
]
CLASSES = [
    "direct_source_theorem_projection_modulo_proved_full_radial_equivalence",
    "derived_base_two_logarithmic_consequence",
    "source_faithful_displayed_consequence_with_proved_scale_normalization",
    "source_faithful_derived_composite_certificate",
]
QUALIFICATIONS = [
    "The ten-field composite is not one manuscript-verbatim theorem.",
    "The 30-decimal base-two exponent enclosure is a formal numerical consequence, not manuscript-authored precision.",
    "Positive-rescaling invariance and unit-separation supremum equivalence remain required for the packing bridge.",
    "The explicit little-o witness is a normal form only and is not a stronger asymptotic-rate claim.",
    "No whole-chapter or full proof-body equivalence is established.",
]
EXPECTED_OUTPUT = {
    "repository": "grandchallenge/MATHCERT",
    "commit_sha": CONTENT_COMMIT,
    "path": CERT_PATH,
    "digest_algorithm": "git_blob_sha1",
    "digest": CERT_BLOB,
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_bytes(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data, usedforsecurity=False).hexdigest()


def git_blob(path: Path) -> str:
    return git_blob_bytes(path.read_bytes())


def git(*args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(["git", *args], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def ensure_history() -> None:
    shallow = git("rev-parse", "--is-shallow-repository")
    if shallow.returncode == 0 and shallow.stdout.decode().strip() == "true":
        result = git("fetch", "--no-tags", "--unshallow", "origin")
        if result.returncode != 0:
            raise RuntimeError("unable to unshallow A output execution history")
    for commit in (BASE_COMMIT, CONTENT_COMMIT, ROUTE_COMMIT):
        if git("cat-file", "-e", f"{commit}^{{commit}}").returncode != 0:
            result = git("fetch", "--no-tags", "origin", commit)
            if result.returncode != 0:
                raise RuntimeError(f"unable to fetch governed A output commit {commit}")


def object_bytes(commit: str, path: str) -> bytes | None:
    result = git("show", f"{commit}:{path}")
    return result.stdout if result.returncode == 0 else None


def object_blob(commit: str, path: str) -> str | None:
    data = object_bytes(commit, path)
    return git_blob_bytes(data) if data is not None else None


def object_json(commit: str, path: str) -> Any | None:
    data = object_bytes(commit, path)
    return json.loads(data.decode("utf-8")) if data is not None else None


def parent(commit: str) -> str:
    result = git("rev-parse", f"{commit}^")
    return result.stdout.decode().strip() if result.returncode == 0 else ""


def is_ancestor(ancestor: str, descendant: str) -> bool:
    return git("merge-base", "--is-ancestor", ancestor, descendant).returncode == 0


def commit_files(commit: str) -> list[str]:
    result = git("diff-tree", "--no-commit-id", "--name-only", "-r", commit)
    return [x for x in result.stdout.decode().splitlines() if x] if result.returncode == 0 else []


def history_receipt() -> dict[str, Any]:
    ensure_history()
    head = git("rev-parse", "HEAD").stdout.decode().strip()
    return {
        "head": head,
        "base_is_ancestor": is_ancestor(BASE_COMMIT, head),
        "content_parent": parent(CONTENT_COMMIT),
        "route_parent": parent(ROUTE_COMMIT),
        "content_is_ancestor_of_route": is_ancestor(CONTENT_COMMIT, ROUTE_COMMIT),
        "content_is_ancestor_of_head": is_ancestor(CONTENT_COMMIT, head),
        "route_is_ancestor_of_head": is_ancestor(ROUTE_COMMIT, head),
        "certificate_at_base": object_blob(BASE_COMMIT, CERT_PATH),
        "certificate_at_content": object_blob(CONTENT_COMMIT, CERT_PATH),
        "certificate_at_route": object_blob(ROUTE_COMMIT, CERT_PATH),
        "certificate_at_head": object_blob(head, CERT_PATH),
        "routes_at_content": object_blob(CONTENT_COMMIT, ROUTES_PATH),
        "routes_at_route": object_blob(ROUTE_COMMIT, ROUTES_PATH),
        "routes_at_head": object_blob(head, ROUTES_PATH),
        "routes_json_at_content": object_json(CONTENT_COMMIT, ROUTES_PATH),
        "routes_json_at_route": object_json(ROUTE_COMMIT, ROUTES_PATH),
        "content_files": commit_files(CONTENT_COMMIT),
        "route_files": commit_files(ROUTE_COMMIT),
    }


def recursive_closure_errors(schema: Any, path: str = "$", seen: set[int] | None = None) -> list[str]:
    if seen is None: seen=set()
    errors: list[str] = []
    if not isinstance(schema, dict): return errors
    ident=id(schema)
    if ident in seen: return errors
    seen.add(ident)
    if schema.get("type") == "object":
        if schema.get("additionalProperties") is not False: errors.append(f"open object schema at {path}")
        for key,value in schema.get("properties",{}).items(): errors += recursive_closure_errors(value,f"{path}.properties.{key}",seen)
    for combiner in ("allOf","anyOf","oneOf"):
        for i,value in enumerate(schema.get(combiner,[])): errors += recursive_closure_errors(value,f"{path}.{combiner}[{i}]",seen)
    for key in ("items","not","if","then","else"):
        value=schema.get(key)
        if isinstance(value,dict): errors += recursive_closure_errors(value,f"{path}.{key}",seen)
    return errors


def route_by_id(routes: dict[str, Any], route_id: str) -> dict[str, Any]:
    return next((r for r in routes.get("routes", []) if isinstance(r,dict) and r.get("route_id")==route_id), {})


def history_errors(history: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key,message in {
        "base_is_ancestor":"protected A output-contract merge is not ancestor of final head",
        "content_is_ancestor_of_route":"certificate-content commit does not precede route transition",
        "content_is_ancestor_of_head":"certificate-content commit is not ancestor of final head",
        "route_is_ancestor_of_head":"route-transition commit is not ancestor of final head",
    }.items():
        if history.get(key) is not True: errors.append(message)
    if history.get("content_parent") != BASE_COMMIT: errors.append("certificate-content commit is not directly based on protected output-contract merge")
    if history.get("route_parent") != CONTENT_COMMIT: errors.append("route-transition commit is not direct descendant of certificate-content commit")
    if history.get("certificate_at_base") is not None: errors.append("certificate existed before certificate-content commit")
    for key in ("certificate_at_content","certificate_at_route","certificate_at_head"):
        if history.get(key) != CERT_BLOB: errors.append(f"certificate bytes not preserved: {key}")
    if history.get("routes_at_content") != ROUTES_BEFORE_BLOB: errors.append("route registry changed in certificate-content commit")
    if history.get("routes_at_route") != ROUTES_AFTER_BLOB: errors.append("A route-transition registry bytes drift")
    if history.get("routes_at_head") != ROUTES_AFTER_BLOB: errors.append("A route registry changed after route-transition commit")
    if history.get("content_files") != [CERT_PATH]: errors.append("certificate-content commit scope drift")
    if history.get("route_files") != [ROUTES_PATH]: errors.append("route-transition commit scope drift")
    before = history.get("routes_json_at_content") or {}
    after = history.get("routes_json_at_route") or {}
    if {k:v for k,v in before.items() if k!="routes"} != {k:v for k,v in after.items() if k!="routes"}: errors.append("non-route registry metadata changed in route transition")
    b_rows = before.get("routes", []) if isinstance(before.get("routes", []),list) else []
    a_rows = after.get("routes", []) if isinstance(after.get("routes", []),list) else []
    if len(b_rows) != len(a_rows): errors.append("route count changed during A output transition")
    b_map={r.get("route_id"):r for r in b_rows if isinstance(r,dict)}; a_map={r.get("route_id"):r for r in a_rows if isinstance(r,dict)}
    if set(b_map) != set(a_map): errors.append("route membership changed during A output transition")
    for rid in sorted(set(b_map)|set(a_map)):
        if rid != sphere.ROUTE_ID and b_map.get(rid) != a_map.get(rid): errors.append(f"non-A route semantics changed: {rid}")
    b_a=b_map.get(sphere.ROUTE_ID,{}); a_a=a_map.get(sphere.ROUTE_ID,{})
    for key in ("route_id","campaign_id","tracker_issue","source_manifest","intake_packet","target_claim_ids","requested_modalities"):
        if b_a.get(key) != a_a.get(key): errors.append(f"A route immutable field changed: {key}")
    if b_a.get("intake_status") != "submitted" or b_a.get("cert_output") is not None: errors.append("A pre-output route state drift")
    if a_a.get("intake_status") != "qualified" or a_a.get("cert_output") != EXPECTED_OUTPUT: errors.append("A qualified route/output transition drift")
    allowed={"intake_status","claim_boundary","cert_output","blockers","reopening_conditions"}
    keys=set(b_a)|set(a_a)
    for key in keys-allowed:
        if b_a.get(key) != a_a.get(key): errors.append(f"A route transition changed unauthorized field: {key}")
    return errors


def validation_errors(record=None, schema=None, future_schema=None, routes=None, certificate=None, history=None, check_history: bool = True) -> list[str]:
    r=load(RECORD) if record is None else record
    s=load(SCHEMA) if schema is None else schema
    fs=load(FUTURE_SCHEMA) if future_schema is None else future_schema
    routes=load(ROUTES) if routes is None else routes
    adjudication=load(ADJUDICATION)
    errors: list[str] = []
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
    if r.get("contract_state") != "design_only": errors.append("historical contract activation")
    pa=r.get("protected_authority",{}); a=pa.get("adjudication",{})
    if pa.get("mathcert_main_at_design_open") != "10d3f5ccd69f45e39ce23d758801bde8c6040401": errors.append("protected design base drift")
    if pa.get("route_registry_git_blob_sha1") != ROUTES_BEFORE_BLOB: errors.append("route registry authority drift")
    if (a.get("git_blob_sha1"),a.get("disposition")) != ("3e0b34dbc74fdbe123f551d559e4f93fc1901c48","adjudication_clear_protected_four_targets_only"): errors.append("adjudication authority drift")
    if adjudication.get("decision",{}).get("disposition") != "adjudication_clear_protected_four_targets_only": errors.append("protected adjudication disposition mismatch")
    if adjudication.get("state",{}).get("route_state") != "submitted" or adjudication.get("state",{}).get("cert_output") is not None: errors.append("historical adjudication record was retroactively output-mutated")
    if r.get("output_scope",{}).get("encoded_targets") != TARGETS: errors.append("target scope/order drift")
    if r.get("output_scope",{}).get("classifications") != CLASSES: errors.append("classification drift")
    q=r.get("qualification_semantics",{}); f=r.get("future_certificate",{}); p=r.get("publication_protocol",{}); st=r.get("state",{})
    if q.get("permitted_disposition") != "qualified_protected_four_targets_only" or q.get("mandatory_qualifications") != QUALIFICATIONS: errors.append("qualification semantics drift")
    if q.get("permitted_axioms") != ["propext","Quot.sound","Classical.choice"]: errors.append("axiom drift")
    if (f.get("certificate_id"),f.get("disposition"),f.get("mathematical_target_proved")) != ("MC-OTP-A-SPHERE-PACKING-QUAL-001","qualified_protected_four_targets_only",False): errors.append("future certificate drift")
    for key in ("certificate_content_commit_first","route_transition_commit_must_descend_from_certificate_content_commit","route_transition_must_change_only_a_route_semantics","route_transition_must_preserve_exact_target_set","route_transition_must_insert_exactly_one_cert_output","certificate_must_not_name_its_own_containing_commit","squash_merge_prohibited","rebase_merge_prohibited","route_first_ordering_prohibited","partial_state_on_protected_main_prohibited"):
        if p.get(key) is not True: errors.append(f"publication protection weakened: {key}")
    if p.get("protected_merge_method") != "merge": errors.append("non ancestry-preserving merge permitted")
    expected={"route_state":"submitted","cert_output":None,"mathematical_target_proved":False,"may_issue_output":False,"may_promote_claim":False,"aggregate_output":False,"manuscript_decimal_precision_attributed":False,"scale_normalization_boundary_required":True,"little_o_strengthened":False,"composite_is_single_verbatim_source_theorem":False}
    if st != expected: errors.append("historical design-only zero-authority state drift")
    route_blob = git_blob(ROUTES) if routes is None or routes == load(ROUTES) else None
    errors.extend(sphere.live_successor_errors(routes, route_blob))
    live_route=sphere.find_route(routes)
    if live_route.get("intake_status") == "qualified":
        if certificate is None:
            if not CERTIFICATE.exists(): errors.append("qualified A route lacks certificate file")
            else: certificate=load(CERTIFICATE)
        if certificate is not None:
            errors.extend(f"certificate schema: {e.message}" for e in Draft202012Validator(fs).iter_errors(certificate))
            if certificate.get("encoded_targets") != TARGETS or certificate.get("classifications") != CLASSES: errors.append("live certificate target/classification drift")
            if certificate.get("qualification",{}).get("disposition") != "qualified_protected_four_targets_only" or certificate.get("qualification",{}).get("mandatory_qualifications") != QUALIFICATIONS: errors.append("live certificate qualification drift")
            cstate=certificate.get("state",{})
            if any(cstate.get(k) is not False for k in ("mathematical_target_proved","aggregate_authority","may_promote_claim")): errors.append("live certificate authority inflation")
            if CERTIFICATE.exists() and git_blob(CERTIFICATE) != CERT_BLOB: errors.append("live certificate blob drift")
            text=json.dumps(certificate,sort_keys=True)
            if CONTENT_COMMIT in text or ROUTE_COMMIT in text: errors.append("certificate improperly names publication commit identity")
        if check_history:
            try: history=history_receipt() if history is None else history
            except RuntimeError as exc: return errors+[str(exc)]
            errors.extend(history_errors(history))
    elif CERTIFICATE.exists():
        errors.append("certificate exists while A route is not qualified")
    boundary=str(r.get("claim_boundary",""))
    for token in ("does not issue a certificate","30-decimal","normalization boundary","little-o","aggregate OpenAI Ten Proofs authority","squash"):
        if token not in boundary: errors.append(f"claim boundary missing {token}")
    return errors


def main() -> int:
    e=validation_errors()
    if e:
        print("\n".join(e),file=sys.stderr)
        return 1
    state=sphere.find_route(load(ROUTES)).get("intake_status")
    if state == "qualified":
        print("validated A restricted-output contract plus exact certificate-content -> route-transition publication ancestry and zero proof/aggregate promotion")
    else:
        print("validated A sphere-packing design-only restricted-output contract and recursively closed future qualification schema")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
