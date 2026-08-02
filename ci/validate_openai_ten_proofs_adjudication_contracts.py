#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import openai_ten_proofs_adjudication_contracts_data as D


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data, usedforsecurity=False).hexdigest()


def open_objects(value: Any, pointer: str = "") -> list[str]:
    out: list[str] = []
    if isinstance(value, dict):
        if value.get("type") == "object" and value.get("additionalProperties") is not False:
            out.append(pointer or "/")
        for key, child in value.items():
            out.extend(open_objects(child, f"{pointer}/{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            out.extend(open_objects(child, f"{pointer}/{index}"))
    return out


def defaults() -> tuple[dict[str, dict[str, Any]], dict[str, Any], dict[str, Any]]:
    return ({fam: load(D.CONTRACT_DIR / f"{fam}.json") for fam in D.FAMILIES}, load(D.REGISTRY), load(D.ROUTES))


def validation_errors(*, contracts=None, registry=None, routes=None, contract_schema=None, registry_schema=None, contract_blobs=None, registry_blob=None, route_blob=None, receipt_blob=None, attestation_blob=None, document_blob=None, local_blobs=None, executed_present=None) -> list[str]:
    errors: list[str] = []
    if contracts is None or registry is None or routes is None:
        dc, dr, drr = defaults()
        contracts = dc if contracts is None else contracts
        registry = dr if registry is None else registry
        routes = drr if routes is None else routes
    contract_schema = load(D.CONTRACT_SCHEMA) if contract_schema is None else contract_schema
    registry_schema = load(D.REGISTRY_SCHEMA) if registry_schema is None else registry_schema
    contract_blobs = {fam: blob(D.CONTRACT_DIR / f"{fam}.json") for fam in D.FAMILIES} if contract_blobs is None else contract_blobs
    registry_blob = blob(D.REGISTRY) if registry_blob is None else registry_blob
    route_blob = blob(D.ROUTES) if route_blob is None else route_blob
    receipt_blob = blob(D.RECEIPT) if receipt_blob is None else receipt_blob
    attestation_blob = blob(D.ATTESTATION) if attestation_blob is None else attestation_blob
    document_blob = blob(D.ATTESTATION_DOCUMENT) if document_blob is None else document_blob
    executed_present = any(p.exists() for p in D.EXECUTED_PATHS) if executed_present is None else executed_present
    if local_blobs is None:
        local_blobs = {}
        for fam in D.FAMILIES:
            authority = D.expected_authority(fam)
            local_blobs[fam] = {key: blob(D.ROOT / authority[key]["path"]) for key in ("cert_intake", "cert_work_package", "replay_evidence", "repository_bundle", "route_proposal")}

    for name, schema in (("contract", contract_schema), ("registry", registry_schema)):
        opened = open_objects(schema)
        if opened:
            errors.append(f"{name} schema contains open objects: {opened}")
    if set(contracts) != set(D.FAMILIES):
        errors.append("contract family membership drift")

    for fam in D.FAMILIES:
        expected, record = D.EXPECTED[fam], contracts.get(fam, {})
        if set(record) != D.TOP_KEYS:
            errors.append(f"{fam}: top-level field drift")
        identity = [record.get(k) for k in ("schema_version", "record_type", "contract_id", "candidate_id", "result_family", "route_id", "contract_state", "tracker_issue")]
        if identity != ["1.0.0", "openai_ten_proofs_result_family_adjudication_contract", expected["contract_id"], "OPENAI-TEN-PROOFS-001", fam, expected["route_id"], "design_only", "https://github.com/grandchallenge/MATHCERT/issues/60"]:
            errors.append(f"{fam}: identity or design-only state drift")
        if contract_blobs.get(fam) != D.CONTRACT_BLOBS[fam]:
            errors.append(f"{fam}: contract blob drift")
        authority = record.get("authority", {})
        if set(authority) != D.AUTH_KEYS:
            errors.append(f"{fam}: authority field drift")
        for key, value in D.expected_authority(fam).items():
            if authority.get(key) != value:
                errors.append(f"{fam}: authority drift at {key}")
        route_registration = authority.get("route_registration", {})
        if route_registration.get("reviewed_head") != "4b9930d8785867bd1c59f4848795cb2b7b960dcf" or route_registration.get("merge_commit") != "cec85b13f5be48439e02fbbfedcf7ca1d839c097" or route_registration.get("non_author_review") != {"reviewer": "jimsteeg", "state": "APPROVED", "submitted_at": "2026-08-02T05:21:21Z"}:
            errors.append(f"{fam}: route-registration authority drift")
        if route_registration.get("registration_receipt", {}).get("digest") != D.RECEIPT_BLOB or route_registration.get("registered_route_registry", {}).get("digest") != D.ROUTE_REGISTRY_BLOB:
            errors.append(f"{fam}: registration artifact drift")
        attestation = authority.get("post_merge_attestation", {})
        if attestation.get("reviewed_head") != "14c7384ab009f3b62bada1f091657096767d8845" or attestation.get("merge_commit") != "64b103923959b02a1b29dd37569eca6e53abd902" or attestation.get("non_author_review") != {"reviewer": "jimsteeg", "state": "APPROVED", "submitted_at": "2026-08-02T05:54:00Z"}:
            errors.append(f"{fam}: attestation authority drift")
        if attestation.get("manifest", {}).get("digest") != D.ATTESTATION_BLOB or attestation.get("verbatim_document", {}).get("digest") != D.ATTESTATION_DOCUMENT_BLOB:
            errors.append(f"{fam}: attestation artifact drift")
        if authority.get("implementation_authorization") != {"tracker_issue": "https://github.com/grandchallenge/MATHCERT/issues/60", "comment_id": 5155876676, "scope": "design_only_adjudication_contracts"}:
            errors.append(f"{fam}: implementation authorization drift")

        scope = record.get("route_scope", {})
        if scope.get("registered_route_state") != "submitted" or scope.get("target_claim_ids") != expected["targets"]:
            errors.append(f"{fam}: route or target scope drift")
        source_text = f"{scope.get('source_theorem', '')} {scope.get('normalized_statement', '')}"
        if not all(token in source_text for token in expected["source_tokens"]):
            errors.append(f"{fam}: source locus drift")
        exclusions = " ".join(scope.get("scope_exclusions", [])).lower()
        if not all(token.lower() in exclusions for token in expected["exclusion_tokens"]):
            errors.append(f"{fam}: exclusion weakened")

        decision = record.get("decision_contract", {})
        if decision.get("admissible_dispositions") != D.DISPOSITIONS:
            errors.append(f"{fam}: disposition drift")
        if [item.get("evidence_id") for item in decision.get("required_evidence", []) if isinstance(item, dict)] != D.EVIDENCE_IDS:
            errors.append(f"{fam}: evidence plan drift")
        if set(decision.get("family_obligations", {})) != {"semantic_concordance", "nonvacuity", "construction_and_interpretation", "source_concordance"}:
            errors.append(f"{fam}: obligation field drift")
        boundary = str(decision.get("family_boundary", "")).lower()
        if not all(token.lower() in boundary for token in expected["boundary_tokens"]):
            errors.append(f"{fam}: family boundary weakened")
        reviewer = record.get("reviewer_requirements", {})
        if reviewer.get("minimum_binding_non_author_reviewers") != 1 or reviewer.get("required_review_state") != "APPROVED" or reviewer.get("review_must_bind_exact_execution_head") is not True or not any(expected["competence"] in item for item in reviewer.get("competence", [])) or len(reviewer.get("independence", [])) < 3:
            errors.append(f"{fam}: reviewer requirements weakened")
        gate = record.get("execution_gate", {})
        gate_keys = ("separate_human_steward_authorization_required", "authorization_must_name_contract_and_exact_execution_head", "exact_head_cert_checks_required", "exact_head_gcl_conformance_required", "fresh_non_author_approval_required", "protected_merge_required", "head_change_requires_revalidation_and_reapproval")
        if not all(gate.get(key) is True for key in gate_keys) or gate.get("design_merge_effect") != "contract_admitted_design_only_no_adjudication":
            errors.append(f"{fam}: execution gate weakened")
        if record.get("state") != D.STATE:
            errors.append(f"{fam}: adjudication/output/proof inflation")
        if record.get("preserved_limitations") != D.LIMITS:
            errors.append(f"{fam}: limitation drift")
        claim = str(record.get("claim_boundary", ""))
        if not all(token in claim for token in ("does not adjudicate or prove", "Cert output", "aggregate", "commercial claims")):
            errors.append(f"{fam}: claim boundary weakened")
        for key in ("cert_intake", "cert_work_package", "replay_evidence", "repository_bundle", "route_proposal"):
            if local_blobs.get(fam, {}).get(key) != D.expected_authority(fam)[key]["digest"]:
                errors.append(f"{fam}: local blob drift at {key}")

    if registry_blob != D.REGISTRY_BLOB:
        errors.append("registry blob drift")
    if registry.get("registry_id") != "MC-OPENAI-TEN-PROOFS-WP07-ADJUDICATION-CONTRACTS" or registry.get("tracker_issue") != "https://github.com/grandchallenge/MATHCERT/issues/60":
        errors.append("registry identity drift")
    if registry.get("state") != {"contract_count": 3, "design_only_contract_count": 3, "may_adjudicate_count": 0, "adjudication_count": 0, "cert_output_count": 0, "mathematical_target_proved_count": 0, "aggregate_adjudication_count": 0}:
        errors.append("registry state inflation")
    references = registry.get("contracts", [])
    if [item.get("result_family") for item in references] != D.FAMILIES:
        errors.append("registry family membership drift")
    for item in references:
        fam = item.get("result_family")
        if fam in D.CONTRACT_BLOBS and (item.get("contract", {}).get("digest") != D.CONTRACT_BLOBS[fam] or item.get("route_id") != D.EXPECTED[fam]["route_id"] or item.get("contract_state") != "design_only" or item.get("may_adjudicate") is not False or item.get("adjudication") is not None or item.get("cert_output") is not None or item.get("mathematical_target_proved") is not False or item.get("may_promote_claim") is not False):
            errors.append(f"{fam}: registry authority inflation")
    if registry.get("preserved_limitations") != D.REGISTRY_LIMITS:
        errors.append("registry limitation drift")
    controls = registry.get("controls", {})
    for key in ("contracts_outside_executed_adjudication_registry", "registered_routes_unchanged", "aggregate_adjudication_prohibited", "family_expansion_prohibited", "source_scope_weakening_prohibited"):
        if controls.get(key) is not True:
            errors.append(f"registry control disabled: {key}")
    for key in ("may_adjudicate", "may_issue_cert_output", "may_mark_target_proved", "may_promote_claim"):
        if controls.get(key) is not False:
            errors.append(f"registry authority inflated: {key}")
    activation = registry.get("activation", {})
    if activation.get("later_execution_requires_separate_human_steward_authorization") is not True or activation.get("head_change_requires_revalidation_and_reapproval") is not True or "before merge" not in str(activation.get("condition", "")):
        errors.append("registry activation gate weakened")
    if not all(token in str(registry.get("claim_boundary", "")) for token in ("does not execute an adjudication", "Cert output", "aggregate", "commercial claims")):
        errors.append("registry claim boundary weakened")

    for actual, expected, name in ((route_blob, D.ROUTE_REGISTRY_BLOB, "route registry"), (receipt_blob, D.RECEIPT_BLOB, "registration receipt"), (attestation_blob, D.ATTESTATION_BLOB, "attestation manifest"), (document_blob, D.ATTESTATION_DOCUMENT_BLOB, "attestation document")):
        if actual != expected:
            errors.append(f"{name} blob drift")
    if executed_present:
        errors.append("executed adjudication artifact exists")
    route_map = {item.get("campaign_id"): item for item in routes.get("routes", []) if isinstance(item, dict)}
    if {key for key in route_map if isinstance(key, str) and key.startswith("OTP-")} != set(D.FAMILIES) or "OPENAI-TEN-PROOFS-001" in route_map:
        errors.append("route family or aggregate membership drift")
    for fam in D.FAMILIES:
        route = route_map.get(fam, {})
        if route.get("route_id") != D.EXPECTED[fam]["route_id"] or route.get("intake_status") != "submitted" or route.get("target_claim_ids") != D.EXPECTED[fam]["targets"] or route.get("cert_output") is not None or not any("adjudication" in str(item).lower() for item in route.get("blockers", [])):
            errors.append(f"{fam}: protected route state drift")
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"adjudication contract design validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print("validated three design-only OTP adjudication contracts and zero adjudication, output, proof, or aggregate authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
