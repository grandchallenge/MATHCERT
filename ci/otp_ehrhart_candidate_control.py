#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "governance/result_family_execution_candidates/OTP-F-EHRHART.json"
MANIFEST = ROOT / "governance/result_family_execution_candidate_manifests/OTP-F-EHRHART.json"
CANDIDATE_SCHEMA = ROOT / "schemas/openai_ten_proofs_ehrhart_execution_candidate.schema.json"
MANIFEST_SCHEMA = ROOT / "schemas/openai_ten_proofs_ehrhart_execution_candidate_manifest.schema.json"
CONTRACT = ROOT / "governance/result_family_adjudication_contracts/OTP-F-EHRHART.json"
DESIGN_REGISTRY = ROOT / "governance/adjudication_design/OPENAI_TEN_PROOFS_WP07_ADJUDICATION_CONTRACTS.json"
ROUTES = ROOT / "governance/certification_routes.json"
LEGACY_CARRIER = ROOT / "evidence/openai_ten_proofs/ehrhart-refresh.zip.b64"
EXECUTED = [
    ROOT / "governance/result_family_adjudications/OTP-F-EHRHART.json",
    ROOT / "certificates/openai_ten_proofs/OTP-F-EHRHART.json",
]
TARGETS = [
    "Ehrhart.Volume.ehrhart_volume_inequality_for_sets",
    "Ehrhart.SimplexVolume.exists_centeredBody_sharp",
    "Ehrhart.SimplexVolume.barycenter_centeredSimplex",
    "Ehrhart.SimplexVolume.normalizedVolume_centeredSimplex",
]
EXPECTED_BLOBS = {
    "contract": "6e1c210d82440210da71fd661daffe986df81f03",
    "design_registry": "7a4aa7ca4f016020fccd0b9d4e73e1c5af12d03f",
    "route_registry": "b5541045591f8589130b1577c50d51d70c3b4337",
}
EXPECTED_EVIDENCE = {
    "axiom-check.json": "theorem_axiom_report",
    "challenge-build.log": "challenge_boundary_replay",
    "comparator.log": "comparator_and_kernel_replay",
    "environment.txt": "toolchain_and_workflow_identity",
    "solution-build.log": "solution_replay_and_trust_scan",
    "source-identities.txt": "content_addressed_authority_chain",
    "source-locus-theorem-1.1.txt": "source_statement_concordance",
    "source-revision-report.txt": "source_reacquisition_receipt",
    "theorem-axioms.log": "human_readable_axiom_report",
    "trust-boundary-scan.txt": "placeholder_unsafe_custom_axiom_scan",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def blob(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data, usedforsecurity=False).hexdigest()


def defaults() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    return load(CANDIDATE), load(MANIFEST), load(ROUTES), load(CANDIDATE_SCHEMA), load(MANIFEST_SCHEMA)


def validation_errors(
    *,
    candidate: dict[str, Any] | None = None,
    manifest: dict[str, Any] | None = None,
    routes: dict[str, Any] | None = None,
    candidate_schema: dict[str, Any] | None = None,
    manifest_schema: dict[str, Any] | None = None,
    evidence_files: dict[str, bytes] | None = None,
    authority_blobs: dict[str, str] | None = None,
    executed_present: bool | None = None,
    legacy_carrier_present: bool | None = None,
) -> list[str]:
    dc, dm, dr, dcs, dms = defaults()
    candidate = copy.deepcopy(dc if candidate is None else candidate)
    manifest = copy.deepcopy(dm if manifest is None else manifest)
    routes = copy.deepcopy(dr if routes is None else routes)
    candidate_schema = copy.deepcopy(dcs if candidate_schema is None else candidate_schema)
    manifest_schema = copy.deepcopy(dms if manifest_schema is None else manifest_schema)
    authority_blobs = authority_blobs or {
        "contract": blob(CONTRACT),
        "design_registry": blob(DESIGN_REGISTRY),
        "route_registry": blob(ROUTES),
    }
    errors: list[str] = []

    for name, expected in EXPECTED_BLOBS.items():
        if authority_blobs.get(name) != expected:
            errors.append(f"{name} blob drift")

    for name, record, schema in (
        ("candidate", candidate, candidate_schema),
        ("manifest", manifest, manifest_schema),
    ):
        if schema.get("type") != "object" or schema.get("additionalProperties") is not False:
            errors.append(f"{name} schema is not closed")
        if set(schema.get("required", [])) != set(record):
            errors.append(f"{name} schema required-field drift")
        if set(schema.get("properties", {})) != set(record):
            errors.append(f"{name} schema property-membership drift")
        try:
            jsonschema.Draft202012Validator(schema).validate(record)
        except Exception as exc:
            errors.append(f"{name} schema validation failed: {exc}")

    identity = (
        candidate.get("candidate_id"), candidate.get("result_family"), candidate.get("route_id"),
        candidate.get("contract_id"), candidate.get("candidate_state"), candidate.get("tracker_issue"),
    )
    if identity != (
        "MC-OTP-F-EHRHART-EXECUTION-CANDIDATE-001", "OTP-F-EHRHART", "MC-ROUTE-OTP-F-EHRHART",
        "MC-OTP-ADJUDICATION-CONTRACT-F-EHRHART", "evidence_prepared",
        "https://github.com/grandchallenge/MATHCERT/issues/62",
    ):
        errors.append("candidate identity/state drift")

    expected_authority = {
        "design_merge_commit": "9f5ec626306092a352aa5ba8d9920b6ddb11b8bb",
        "contract_blob": EXPECTED_BLOBS["contract"],
        "design_registry_blob": EXPECTED_BLOBS["design_registry"],
        "registered_route_registry_blob": EXPECTED_BLOBS["route_registry"],
        "source_revision_audit_commit": "a498ef40b7652b55bf121b5682604e259b8d3073",
        "source_revision_audit_blob": "80d473b1b545fd9ca05fc5200bcf70ff5f9fcb05",
        "semantic_record_blob": "a3dc4de4c38a80b7aec1fae6506b08e14d2e58bb",
        "implementation_authorization_comment_id": 5156109106,
    }
    if candidate.get("authority") != expected_authority:
        errors.append("candidate authority drift")

    generation = candidate.get("generation", {})
    artifact = generation.get("artifact", {})
    if (
        generation.get("repository") != "grandchallenge/MATHCERT"
        or generation.get("pull_request") != 63
        or generation.get("generation_head") != "f83e35f352a4b66d225c86e2837e48ab98e0d530"
        or generation.get("workflow_checkout_sha") != "00a5d65bb43fd925432706d3f063d0fe92f93772"
        or generation.get("workflow_run_id") != 30737697106
        or generation.get("job_id") != 91469396219
        or artifact != {
            "id": 8830320201,
            "name": "otp-ehrhart-evidence-refresh",
            "bytes": 16546,
            "sha256": "7a433f6b7d4b9b641ae6ad1b3e42c5c40e57d53922fb758286e38a92ca8e69fb",
            "retention_role": "raw_workflow_evidence_authority",
        }
    ):
        errors.append("workflow generation authority drift")

    if candidate.get("encoded_targets") != TARGETS:
        errors.append("encoded target drift")
    expected_replay = {
        "clean_room": True,
        "isolated_family_replay": True,
        "aggregate_all_import_used": False,
        "lean_version": "4.32.0",
        "challenge_build": "pass",
        "solution_build": "pass",
        "comparator": "pass",
        "lean_kernel": "accept",
        "nanoda": "accept",
        "theorem_axiom_report": "permitted_only",
        "trust_boundary_scan": "clear",
    }
    if candidate.get("replay") != expected_replay:
        errors.append("replay state drift")

    source = candidate.get("source_reacquisition", {})
    if (
        source.get("sha256") != "64b900d5fae6fe22f2ae1b8e3b712d20055194a6c81cf343a2455e5898ac7dd6"
        or source.get("bytes") != 2266371
        or source.get("relation") != "byte_identical_to_forge_source_revision_audit_subject"
        or source.get("locus", {}).get("repository_extract") != "evidence/openai_ten_proofs/ehrhart_refresh/source-locus-theorem-1.1.txt"
        or source.get("whole_document_byte_equivalence") != "not_established_between_all_revisions"
        or source.get("whole_document_semantic_equivalence") != "not_established"
        or source.get("proof_body_compared_in_full") is not False
    ):
        errors.append("source identity/scope drift")
    if candidate.get("statement_concordance", {}).get("equality_case_classification") != "excluded":
        errors.append("equality-case classification inflation")
    if candidate.get("construction_interpretation", {}).get("classification_or_uniqueness_inference") is not False:
        errors.append("construction interpretation inflation")
    if candidate.get("nonvacuity", {}).get("witnesses") != [TARGETS[1], TARGETS[3]]:
        errors.append("nonvacuity witness drift")

    expected_state = {
        "route_state": "submitted",
        "may_adjudicate": False,
        "adjudication": None,
        "cert_output": None,
        "mathematical_target_proved": False,
        "may_promote_claim": False,
        "aggregate_adjudication": False,
    }
    if candidate.get("state") != expected_state:
        errors.append("adjudication/output/proof/route authority inflation")
    if candidate.get("review_state") != {
        "fresh_non_author_specialist_review_required": True,
        "specialist_review": None,
        "status": "pending_exact_head_non_author_specialist_review",
    }:
        errors.append("specialist review gate drift")
    if candidate.get("execution_authorization") != {
        "separate_human_steward_authorization_required": True,
        "must_name_contract_and_exact_candidate_head": True,
        "authorization": None,
    }:
        errors.append("execution authorization gate drift")

    candidate_ref = manifest.get("candidate_record", {})
    if candidate_ref != {
        "repository": "grandchallenge/MATHCERT",
        "path": "governance/result_family_execution_candidates/OTP-F-EHRHART.json",
        "address_mode": "exact_pr_head",
        "head_change_requires_revalidation": True,
    }:
        errors.append("manifest candidate reference drift")
    if manifest.get("governing_contract", {}).get("digest") != EXPECTED_BLOBS["contract"]:
        errors.append("manifest contract digest drift")
    raw = manifest.get("raw_workflow_artifact", {})
    if raw != {
        "generation_head": "f83e35f352a4b66d225c86e2837e48ab98e0d530",
        "workflow_run_id": 30737697106,
        "job_id": 91469396219,
        "artifact_id": 8830320201,
        "name": "otp-ehrhart-evidence-refresh",
        "bytes": 16546,
        "digest_algorithm": "sha256",
        "digest": "7a433f6b7d4b9b641ae6ad1b3e42c5c40e57d53922fb758286e38a92ca8e69fb",
        "role": "raw_workflow_evidence_authority",
    }:
        errors.append("raw workflow artifact authority drift")

    repository_evidence = manifest.get("repository_evidence", {})
    listed = repository_evidence.get("files", [])
    listed_map = {Path(item.get("path", "")).name: item.get("role") for item in listed if isinstance(item, dict)}
    if (
        repository_evidence.get("root") != "evidence/openai_ten_proofs/ehrhart_refresh"
        or repository_evidence.get("format") != "curated_selected_files"
        or repository_evidence.get("file_count") != 10
        or repository_evidence.get("byte_identity_to_raw_artifact_not_claimed") is not True
        or listed_map != EXPECTED_EVIDENCE
    ):
        errors.append("repository evidence membership/boundary drift")
    if candidate.get("repository_evidence") != {
        "root": "evidence/openai_ten_proofs/ehrhart_refresh",
        "format": "curated_selected_files",
        "manifest": "governance/result_family_execution_candidate_manifests/OTP-F-EHRHART.json",
        "file_count": 10,
        "raw_artifact_is_authoritative": True,
        "repository_files_are_review_extracts": True,
    }:
        errors.append("candidate repository evidence boundary drift")

    if evidence_files is None:
        evidence_files = {}
        for item in listed:
            path = ROOT / item.get("path", "")
            if path.is_file():
                evidence_files[path.name] = path.read_bytes()
    if set(evidence_files) != set(EXPECTED_EVIDENCE):
        errors.append("retained evidence file membership drift")
    if any(not data for data in evidence_files.values()):
        errors.append("empty retained evidence file")

    try:
        axiom = json.loads(evidence_files["axiom-check.json"])
        if axiom.get("permitted") != ["Classical.choice", "Quot.sound", "propext"]:
            errors.append("permitted axiom set drift")
        if [row.get("theorem") for row in axiom.get("reports", [])] != TARGETS:
            errors.append("theorem axiom membership drift")
        if any(row.get("unexpected") for row in axiom.get("reports", [])):
            errors.append("unexpected axiom admitted")
        comparator = evidence_files["comparator.log"].decode(errors="replace").lower()
        if not all(token in comparator for token in ("nanoda kernel: accept", "lean default kernel: accept", "comparator disposition: pass")):
            errors.append("comparator evidence drift")
        trust = evidence_files["trust-boundary-scan.txt"].decode(errors="replace").lower()
        if "scan: clear" not in trust or "aggregate all.lean import scan: clear" not in trust:
            errors.append("trust boundary evidence drift")
        locus = evidence_files["source-locus-theorem-1.1.txt"].decode(errors="replace").lower()
        if not all(token in locus for token in ("theorem 1.1", "translated dilation", "we do not determine whether these are the only equality cases")):
            errors.append("source theorem-locus evidence drift")
        identities = evidence_files["source-identities.txt"].decode(errors="replace")
        if not all(value in identities for value in EXPECTED_BLOBS.values()):
            errors.append("retained authority-chain evidence drift")
    except Exception as exc:
        errors.append(f"retained evidence semantic failure: {exc}")

    expected_controls = {
        "candidate_state": "evidence_prepared",
        "route_state": "submitted",
        "may_adjudicate": False,
        "may_issue_cert_output": False,
        "may_mark_target_proved": False,
        "may_promote_claim": False,
        "aggregate_adjudication_prohibited": True,
        "equality_case_classification_prohibited": True,
        "other_family_execution_prohibited": True,
    }
    if manifest.get("controls") != expected_controls:
        errors.append("manifest controls weakened")
    activation = manifest.get("activation", {})
    if (
        activation.get("head_change_requires_revalidation_and_reapproval") is not True
        or activation.get("later_adjudication_requires_separate_human_steward_authorization") is not True
        or activation.get("effect") != "ehrhart_evidence_candidate_admitted_no_adjudication_no_output"
    ):
        errors.append("manifest activation gate weakened")

    route = next((row for row in routes.get("routes", []) if row.get("campaign_id") == "OTP-F-EHRHART"), {})
    if (
        route.get("route_id") != "MC-ROUTE-OTP-F-EHRHART"
        or route.get("intake_status") != "submitted"
        or route.get("target_claim_ids") != TARGETS
        or route.get("cert_output") is not None
        or not any("adjudication" in str(blocker).lower() for blocker in route.get("blockers", []))
    ):
        errors.append("protected route state drift")

    executed_present = any(path.exists() for path in EXECUTED) if executed_present is None else executed_present
    if executed_present:
        errors.append("executed adjudication or Cert output artifact exists")
    legacy_carrier_present = LEGACY_CARRIER.exists() if legacy_carrier_present is None else legacy_carrier_present
    if legacy_carrier_present:
        errors.append("superseded archive carrier exists")
    for boundary in (candidate.get("claim_boundary", ""), manifest.get("claim_boundary", "")):
        if not all(token in boundary for token in ("does not adjudicate or prove", "Cert output", "equality", "aggregate", "commercial claims")):
            errors.append("claim boundary weakened")
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"Ehrhart execution-candidate validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print("validated content-addressed OTP-F-EHRHART evidence candidate with zero adjudication, output, proof, route, or aggregate authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
