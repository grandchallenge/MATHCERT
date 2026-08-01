#!/usr/bin/env python3
"""Validate OpenAI ten-proofs result-family certification work packages."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "governance" / "result_family_work_packages"
REGISTRY_PATH = (
    ROOT
    / "governance"
    / "pre_route_candidates"
    / "OPENAI_TEN_PROOFS_WP02_WORK_PACKAGES.json"
)
ROUTES_PATH = ROOT / "governance" / "certification_routes.json"

EXPECTED = {
    "OTP-F-EHRHART": {
        "work_package_id": "OTP-F-EHRHART-CERT-WP01",
        "tracker_issue": "https://github.com/grandchallenge/MATHCERT/issues/48",
        "path": "governance/result_family_work_packages/OTP-F-EHRHART-CERT-WP01.json",
        "digest": "056149e7a659fb6b24b7d7389a3dcd68bb581bcd",
        "intake_path": "governance/result_family_intakes/OTP-F-EHRHART.json",
        "intake_digest": "1c6a5f349803bba09b000ceb3f8a53ee3038ca48",
        "route_id": "MC-ROUTE-OTP-F-EHRHART",
        "source_theorem": "Chapter 8, Theorem 1.1, parsed P219 L18214-L18229",
        "lean_theorems": [
            "Ehrhart.Volume.ehrhart_volume_inequality_for_sets",
            "Ehrhart.SimplexVolume.exists_centeredBody_sharp",
            "Ehrhart.SimplexVolume.barycenter_centeredSimplex",
            "Ehrhart.SimplexVolume.normalizedVolume_centeredSimplex",
        ],
        "nonvacuity_witnesses": [
            "Ehrhart.SimplexVolume.exists_centeredBody_sharp",
            "Ehrhart.SimplexVolume.normalizedVolume_centeredSimplex",
        ],
        "family_step": "audit_source_statement_and_scope_exclusions",
    },
    "OTP-J1-COMPACTNESS": {
        "work_package_id": "OTP-J1-COMPACTNESS-CERT-WP01",
        "tracker_issue": "https://github.com/grandchallenge/MATHCERT/issues/49",
        "path": "governance/result_family_work_packages/OTP-J1-COMPACTNESS-CERT-WP01.json",
        "digest": "d80cade6d99c7ca54f4384a68e178b2f4335a8b2",
        "intake_path": "governance/result_family_intakes/OTP-J1-COMPACTNESS.json",
        "intake_digest": "d08eec02d7ee44f3bc2692cf7949c70d8e0f2bbf",
        "route_id": "MC-ROUTE-OTP-J1-COMPACTNESS",
        "source_theorem": "Chapter 10, Theorem 1.1, parsed P236 L19757-L19791",
        "lean_theorems": [
            "CompactnessConjecture.quantitativeCompactnessCounterexample",
            "CompactnessConjecture.compactnessCounterexample_bigO",
            "CompactnessConjecture.not_erdos_180",
        ],
        "nonvacuity_witnesses": [
            "CompactnessConjecture.quantitativeCompactnessCounterexample",
            "CompactnessConjecture.compactnessCounterexample_bigO",
        ],
        "family_step": "audit_corrected_cyclic_family_statement_and_graph_definitions",
    },
    "OTP-J2-TWO-DEGENERATE": {
        "work_package_id": "OTP-J2-TWO-DEGENERATE-CERT-WP01",
        "tracker_issue": "https://github.com/grandchallenge/MATHCERT/issues/50",
        "path": "governance/result_family_work_packages/OTP-J2-TWO-DEGENERATE-CERT-WP01.json",
        "digest": "dbbc4ab59f21b3f5cb2f313c51f754b9b306389c",
        "intake_path": "governance/result_family_intakes/OTP-J2-TWO-DEGENERATE.json",
        "intake_digest": "6e9cfee8f988e357aabdd53e2883220d170b7e60",
        "route_id": "MC-ROUTE-OTP-J2-TWO-DEGENERATE",
        "source_theorem": "Chapter 10, Theorem 1.2, parsed P236-P237 L19792-L19822",
        "lean_theorems": [
            "TwoDegenerateGraphs.twoDegenerateExtremalCounterexample",
            "TwoDegenerateGraphs.not_erdos_146",
        ],
        "nonvacuity_witnesses": [
            "TwoDegenerateGraphs.twoDegenerateExtremalCounterexample",
        ],
        "family_step": "audit_degeneracy_asymptotics_and_source_attribution",
    },
}
EXPECTED_FAMILIES = tuple(EXPECTED)
EXPECTED_BLOCKED = ["OTP-C-PERMANENT", "OTP-H-GAPCVP"]
EXPECTED_ROUTES_BLOB = "5b3e8d48b9f6c5b03ed3dc439bf9e43876e017b1"

TOP_KEYS = {
    "schema_version",
    "record_type",
    "work_package_id",
    "candidate_id",
    "result_family",
    "tracker_issue",
    "status",
    "authority",
    "execution",
    "target_scope",
    "route_state",
    "activation",
    "route_controls",
    "claim_boundary",
}
AUTHORITY_KEYS = {
    "cert_intake_merge",
    "cert_intake_reviewed_head",
    "cert_intake_review",
    "intake_record",
    "solve_handoff_merge",
    "forge_semantic_merge",
    "official_subject",
}
EXECUTION_KEYS = {
    "allowed",
    "isolated_family_replay_required",
    "clean_room_environment_required",
    "aggregate_import_required",
    "required_steps",
    "required_artifacts",
    "specialist_review_required",
}
TARGET_KEYS = {
    "source_theorem",
    "lean_theorems",
    "nonvacuity_witnesses",
    "scope_exclusions",
}
ROUTE_STATE_KEYS = {
    "requested_route_id",
    "certification_route_registry_entry",
    "proposed_route_record",
    "cert_output",
    "may_register_route_on_branch",
    "may_adjudicate",
    "mathematical_target_proved",
    "may_promote_claim",
}
ACTIVATION_KEYS = {"condition", "head_change_requires_reapproval", "effect"}
ROUTE_CONTROL_KEYS = {
    "result_family_only",
    "may_create_aggregate_work_package",
    "may_create_aggregate_route",
    "may_imply_certification",
    "may_imply_proof",
}
COMMON_STEPS = {
    "verify_content_addressed_authority",
    "reacquire_exact_family_sources",
    "replay_challenge_solution_and_comparator",
    "replay_named_nonvacuity_witnesses",
    "record_theorem_level_axiom_report",
    "scan_placeholders_unsafe_custom_axioms_and_hidden_dependencies",
    "obtain_exact_head_non_author_specialist_review",
}
COMMON_ARTIFACTS = {
    "environment_manifest",
    "source_identity_report",
    "family_replay_log",
    "comparator_result",
    "nonvacuity_replay_report",
    "theorem_axiom_report",
    "trust_boundary_scan",
    "independent_review_attestation",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload,
        usedforsecurity=False,
    ).hexdigest()


def check_keys(
    value: Any, expected: set[str], label: str, errors: list[str]
) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{label}: expected object")
        return {}
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        unknown = sorted(actual - expected)
        if missing:
            errors.append(f"{label}: missing keys {missing}")
        if unknown:
            errors.append(f"{label}: unknown keys {unknown}")
    return value


def validation_errors(
    registry: dict[str, Any] | None = None,
    packages: dict[str, dict[str, Any]] | None = None,
    package_blobs: dict[str, str] | None = None,
    routes: dict[str, Any] | None = None,
    routes_blob: str | None = None,
) -> list[str]:
    errors: list[str] = []
    if registry is None:
        registry = load_json(REGISTRY_PATH)
    if packages is None:
        packages = {}
        for path in sorted(PACKAGE_DIR.glob("*.json")):
            record = load_json(path)
            packages[str(record.get("result_family", path.stem))] = record
    if package_blobs is None:
        package_blobs = {}
        for path in sorted(PACKAGE_DIR.glob("*.json")):
            record = load_json(path)
            package_blobs[str(record.get("result_family", path.stem))] = git_blob_sha1(path)
    if routes is None:
        routes = load_json(ROUTES_PATH)
    if routes_blob is None:
        routes_blob = git_blob_sha1(ROUTES_PATH)

    actual = set(packages)
    expected = set(EXPECTED_FAMILIES)
    for missing in sorted(expected - actual):
        errors.append(f"OTP-CERT-WP01: missing work package {missing}")
    for unknown in sorted(actual - expected):
        errors.append(f"OTP-CERT-WP01: unexpected work package {unknown}")

    seen_ids: list[str] = []
    seen_routes: list[str] = []
    for family, expected_record in EXPECTED.items():
        package = packages.get(family)
        if not isinstance(package, dict):
            continue
        label = f"OTP-CERT-WP01: {family}"
        check_keys(package, TOP_KEYS, label, errors)
        if package.get("schema_version") != "1.0.0":
            errors.append(f"{label}: schema version drift")
        if package.get("record_type") != "openai_ten_proofs_certification_work_package":
            errors.append(f"{label}: record type drift")
        if package.get("work_package_id") != expected_record["work_package_id"]:
            errors.append(f"{label}: work-package identity drift")
        if package.get("candidate_id") != "OPENAI-TEN-PROOFS-001":
            errors.append(f"{label}: candidate identity drift")
        if package.get("result_family") != family:
            errors.append(f"{label}: result-family identity drift")
        if package.get("tracker_issue") != expected_record["tracker_issue"]:
            errors.append(f"{label}: tracker issue drift")
        if package.get("status") != "authorized_after_protected_mathcert_merge":
            errors.append(f"{label}: status drift")

        authority = check_keys(package.get("authority"), AUTHORITY_KEYS, f"{label}.authority", errors)
        if authority.get("cert_intake_merge") != "d99d2625ee838945087a91a50923cddc2dcc8d85":
            errors.append(f"{label}: Cert intake merge drift")
        if authority.get("cert_intake_reviewed_head") != "28e9300c2641e17597ff087f2b892ed214d6c90a":
            errors.append(f"{label}: Cert intake reviewed-head drift")
        review = check_keys(
            authority.get("cert_intake_review"),
            {"review_id", "reviewer", "state", "submitted_at"},
            f"{label}.authority.cert_intake_review",
            errors,
        )
        if review != {
            "review_id": 4835619680,
            "reviewer": "jimsteeg",
            "state": "APPROVED",
            "submitted_at": "2026-08-01T20:00:13Z",
        }:
            errors.append(f"{label}: Cert intake review identity drift")
        intake = check_keys(
            authority.get("intake_record"),
            {"repository", "commit_sha", "path", "digest_algorithm", "digest"},
            f"{label}.authority.intake_record",
            errors,
        )
        expected_intake = {
            "repository": "grandchallenge/MATHCERT",
            "commit_sha": "d99d2625ee838945087a91a50923cddc2dcc8d85",
            "path": expected_record["intake_path"],
            "digest_algorithm": "git_blob_sha1",
            "digest": expected_record["intake_digest"],
        }
        if intake != expected_intake:
            errors.append(f"{label}: intake record authority drift")
        if authority.get("solve_handoff_merge") != "443daf537dc7e4ee34ab43aeb01508d9177816ab":
            errors.append(f"{label}: Solve handoff merge drift")
        if authority.get("forge_semantic_merge") != "cb0a203c36a9ef33270d62ab369df7bc27d3b242":
            errors.append(f"{label}: Forge semantic merge drift")
        subject = check_keys(
            authority.get("official_subject"),
            {"repository", "commit", "tree", "archive_sha256"},
            f"{label}.authority.official_subject",
            errors,
        )
        if subject != {
            "repository": "openai/ten-proofs",
            "commit": "e62211d28e3a9131950c89caa6542cfe5eff3bca",
            "tree": "2f8e7ac5ae7f157b6b1de636c2c343b1c7a7e365",
            "archive_sha256": "3022e62ffbed8f5f74d232034a703dc645e6b301879dff1e87df72979914294f",
        }:
            errors.append(f"{label}: official subject drift")

        execution = check_keys(package.get("execution"), EXECUTION_KEYS, f"{label}.execution", errors)
        for field in (
            "allowed",
            "isolated_family_replay_required",
            "clean_room_environment_required",
            "specialist_review_required",
        ):
            if execution.get(field) is not True:
                errors.append(f"{label}: required execution control disabled: {field}")
        if execution.get("aggregate_import_required") is not False:
            errors.append(f"{label}: aggregate All.lean import made a family prerequisite")
        steps = execution.get("required_steps", [])
        if not isinstance(steps, list) or len(steps) != len(set(steps)):
            errors.append(f"{label}: required steps must be a unique list")
            steps = []
        if not COMMON_STEPS.issubset(set(steps)):
            errors.append(f"{label}: common replay steps are incomplete")
        if expected_record["family_step"] not in steps:
            errors.append(f"{label}: family-specific audit step is missing")
        artifacts = execution.get("required_artifacts", [])
        if not isinstance(artifacts, list) or len(artifacts) != len(set(artifacts)):
            errors.append(f"{label}: required artifacts must be a unique list")
            artifacts = []
        if not COMMON_ARTIFACTS.issubset(set(artifacts)):
            errors.append(f"{label}: required evidence artifacts are incomplete")

        target = check_keys(package.get("target_scope"), TARGET_KEYS, f"{label}.target_scope", errors)
        if target.get("source_theorem") != expected_record["source_theorem"]:
            errors.append(f"{label}: source theorem drift")
        if target.get("lean_theorems") != expected_record["lean_theorems"]:
            errors.append(f"{label}: Lean theorem set drift")
        if target.get("nonvacuity_witnesses") != expected_record["nonvacuity_witnesses"]:
            errors.append(f"{label}: nonvacuity witness set drift")
        exclusions = target.get("scope_exclusions")
        if not isinstance(exclusions, list) or not exclusions:
            errors.append(f"{label}: scope exclusions are missing")

        route_state = check_keys(
            package.get("route_state"), ROUTE_STATE_KEYS, f"{label}.route_state", errors
        )
        if route_state.get("requested_route_id") != expected_record["route_id"]:
            errors.append(f"{label}: requested route identity drift")
        for field in (
            "certification_route_registry_entry",
            "proposed_route_record",
            "cert_output",
        ):
            if route_state.get(field) is not None:
                errors.append(f"{label}: premature route or output state: {field}")
        for field in (
            "may_register_route_on_branch",
            "may_adjudicate",
            "mathematical_target_proved",
            "may_promote_claim",
        ):
            if route_state.get(field) is not False:
                errors.append(f"{label}: prohibited state enabled: {field}")

        activation = check_keys(
            package.get("activation"), ACTIVATION_KEYS, f"{label}.activation", errors
        )
        if not str(activation.get("condition", "")).strip():
            errors.append(f"{label}: activation condition missing")
        if activation.get("head_change_requires_reapproval") is not True:
            errors.append(f"{label}: head-change reapproval disabled")
        if (
            activation.get("effect")
            != "work_package_authorized_for_execution_no_route_no_adjudication"
        ):
            errors.append(f"{label}: activation effect drift")

        controls = check_keys(
            package.get("route_controls"),
            ROUTE_CONTROL_KEYS,
            f"{label}.route_controls",
            errors,
        )
        if controls.get("result_family_only") is not True:
            errors.append(f"{label}: result-family granularity removed")
        for field in (
            "may_create_aggregate_work_package",
            "may_create_aggregate_route",
            "may_imply_certification",
            "may_imply_proof",
        ):
            if controls.get(field) is not False:
                errors.append(f"{label}: prohibited route control enabled: {field}")
        if not str(package.get("claim_boundary", "")).strip():
            errors.append(f"{label}: claim boundary missing")
        seen_ids.append(str(package.get("work_package_id", "")))
        seen_routes.append(str(route_state.get("requested_route_id", "")))

    for duplicate in sorted({value for value in seen_ids if seen_ids.count(value) > 1}):
        errors.append(f"OTP-CERT-WP01: duplicate work-package identity {duplicate}")
    for duplicate in sorted({value for value in seen_routes if seen_routes.count(value) > 1}):
        errors.append(f"OTP-CERT-WP01: duplicate requested route identity {duplicate}")

    registry_keys = {
        "schema_version",
        "record_type",
        "registry_id",
        "candidate_id",
        "authority",
        "work_packages",
        "execution_state",
        "blocked_repair_lanes",
        "aggregate_integration",
        "route_controls",
        "claim_boundary",
    }
    check_keys(registry, registry_keys, "OTP-CERT-WP01.registry", errors)
    if registry.get("schema_version") != "1.0.0":
        errors.append("OTP-CERT-WP01: registry schema version drift")
    if registry.get("record_type") != "openai_ten_proofs_certification_work_package_registry":
        errors.append("OTP-CERT-WP01: registry type drift")
    if registry.get("registry_id") != "MC-OTP-CERT-WP01":
        errors.append("OTP-CERT-WP01: registry identity drift")
    if registry.get("candidate_id") != "OPENAI-TEN-PROOFS-001":
        errors.append("OTP-CERT-WP01: registry candidate drift")
    if registry.get("authority") != {
        "cert_intake_merge": "d99d2625ee838945087a91a50923cddc2dcc8d85",
        "cert_intake_reviewed_head": "28e9300c2641e17597ff087f2b892ed214d6c90a",
        "cert_intake_review_id": 4835619680,
    }:
        errors.append("OTP-CERT-WP01: registry authority drift")

    refs = registry.get("work_packages", [])
    if not isinstance(refs, list):
        errors.append("OTP-CERT-WP01: registry work_packages must be a list")
        refs = []
    indexed = [str(item.get("result_family", "")) for item in refs if isinstance(item, dict)]
    if indexed != list(EXPECTED_FAMILIES):
        errors.append("OTP-CERT-WP01: registry package order or membership drift")
    for item in refs:
        if not isinstance(item, dict):
            errors.append("OTP-CERT-WP01: invalid registry package reference")
            continue
        family = str(item.get("result_family", ""))
        expected_record = EXPECTED.get(family)
        if expected_record is None:
            continue
        expected_ref = {
            "result_family": family,
            "work_package_id": expected_record["work_package_id"],
            "tracker_issue": expected_record["tracker_issue"],
            "path": expected_record["path"],
            "digest_algorithm": "git_blob_sha1",
            "digest": package_blobs.get(family),
        }
        if item != expected_ref:
            errors.append(f"OTP-CERT-WP01: registry reference drift for {family}")
        if package_blobs.get(family) != expected_record["digest"]:
            errors.append(f"OTP-CERT-WP01: local package Git blob drift for {family}")

    if registry.get("execution_state") != {
        "authorized_work_package_count": 3,
        "executing_count": 0,
        "evidence_bundle_count": 0,
        "proposed_route_count": 0,
        "registered_route_count": 0,
        "adjudication_count": 0,
        "cert_output_count": 0,
        "mathematical_target_proved_count": 0,
    }:
        errors.append("OTP-CERT-WP01: execution state drift")
    if registry.get("blocked_repair_lanes") != EXPECTED_BLOCKED:
        errors.append("OTP-CERT-WP01: blocked repair lanes drift")
    aggregate = registry.get("aggregate_integration", {})
    if not isinstance(aggregate, dict):
        errors.append("OTP-CERT-WP01: aggregate integration record missing")
        aggregate = {}
    for field in (
        "reopens_family_replay",
        "reopens_semantic_gates",
        "creates_work_package",
        "creates_cert_route",
    ):
        if aggregate.get(field) is not False:
            errors.append(f"OTP-CERT-WP01: aggregate integration changed protected state: {field}")
    controls = registry.get("route_controls", {})
    if not isinstance(controls, dict):
        errors.append("OTP-CERT-WP01: registry route controls missing")
        controls = {}
    if controls.get("global_certification_route_registry_modified") is not False:
        errors.append("OTP-CERT-WP01: global route registry marked modified")
    if controls.get("aggregate_work_package") is not None:
        errors.append("OTP-CERT-WP01: aggregate work package injected")
    if controls.get("aggregate_route_prohibited") is not True:
        errors.append("OTP-CERT-WP01: aggregate route prohibition removed")
    if controls.get("result_family_granularity") is not True:
        errors.append("OTP-CERT-WP01: result-family granularity removed")
    if controls.get("may_adjudicate") is not False:
        errors.append("OTP-CERT-WP01: registry adjudication enabled")
    if controls.get("may_promote_claim") is not False:
        errors.append("OTP-CERT-WP01: registry claim promotion enabled")
    if not str(registry.get("claim_boundary", "")).strip():
        errors.append("OTP-CERT-WP01: registry claim boundary missing")

    if routes_blob != EXPECTED_ROUTES_BLOB:
        errors.append("OTP-CERT-WP01: global certification route registry changed")
    route_records = routes.get("routes", []) if isinstance(routes, dict) else []
    existing_route_ids = {
        str(item.get("route_id", ""))
        for item in route_records
        if isinstance(item, dict)
    }
    for expected_record in EXPECTED.values():
        if expected_record["route_id"] in existing_route_ids:
            errors.append(
                f"OTP-CERT-WP01: route registered prematurely: {expected_record['route_id']}"
            )
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(
            f"OpenAI ten-proofs certification work-package validation failed with {len(errors)} error(s)",
            file=sys.stderr,
        )
        return 1
    print(
        "validated three content-addressed result-family certification work packages, "
        "zero route registration, zero adjudication, zero outputs, and aggregate prohibition"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
