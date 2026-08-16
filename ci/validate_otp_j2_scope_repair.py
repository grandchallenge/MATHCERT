#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "governance/result_family_scope_repairs/OTP-J2-TWO-DEGENERATE.json"
SCHEMA = ROOT / "schemas/openai_ten_proofs_j2_scope_repair.schema.json"
ROUTES = ROOT / "governance/certification_routes.json"
OVERLAY_REL = "evidence/openai_ten_proofs/two_degenerate_scope_repair/SourceFaithfulProjection.lean"
OVERLAY = ROOT / OVERLAY_REL

EXPECTED_ROUTE_REGISTRY_BLOB = "bc4640661443f1b3de213aaa82a333a4fdb6849b"
EXPECTED_OVERLAY_BLOB = "ac1ec20e95d6acbcd1c3a111afe28bca92a43377"
EXPECTED_HISTORICAL_BLOBS = {
    "governance/result_family_intakes/OTP-J2-TWO-DEGENERATE.json": "6e9cfee8f988e357aabdd53e2883220d170b7e60",
    "governance/result_family_work_packages/OTP-J2-TWO-DEGENERATE-CERT-WP01.json": "dbbc4ab59f21b3f5cb2f313c51f754b9b306389c",
    "governance/result_family_replay_evidence/OTP-J2-TWO-DEGENERATE.json": "215ce18b4139159c89d167ab11cab6c35d5a38ff",
    "governance/result_family_route_proposals/OTP-J2-TWO-DEGENERATE.json": "0692ac15c19328532bdcd3e73b3c8c4371647ac6",
    "governance/result_family_adjudication_contracts/OTP-J2-TWO-DEGENERATE.json": "2bb9d70b931ea0a07487664c112644f990527760",
}
EXPECTED_REGISTERED_TARGETS = [
    "TwoDegenerateGraphs.twoDegenerateExtremalCounterexample",
    "TwoDegenerateGraphs.not_erdos_146",
]
EXPECTED_FUTURE_SCOPE = [
    "TwoDegenerateGraphs.mathcert_sourceFaithfulTwoDegenerateExtremalCounterexample",
    "TwoDegenerateGraphs.mathcert_sourceFaithfulNotErdos146",
]
EXPECTED_SOURCE_SHA256 = "ebc561ab5c53dbd240e17a8fdb6fffeb648591eca85dbfc7466f563638f8c566"
EXPECTED_SOURCE_BYTES = 2487031
EXPECTED_FORMAL_COMMIT = "94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6"
EXPECTED_FORMAL_TREE = "174289e4d4958cb0509874e6e53400e098213de7"
EXPECTED_LAKE_MANIFEST_BLOB = "046e8de7f46832fbf092e3fb815efae01e4a2129"
EXPECTED_CONFIG_BLOB = "d8a542b5ce620b686cb24a6756360e76c5d2b1c1"
EXPECTED_CHALLENGE_BLOB = "dd22ce141dd0a860ecdccfda291c0f3a480a1d70"
EXPECTED_SOLUTION_BLOB = "0e973d50014e8c800af597ef699ef29b81e42fc6"
EXPECTED_AUTH_COMMENT = 5305021852


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def repository_blob_sha1(rel: str) -> str:
    if (ROOT / ".git").exists():
        proc = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", f"HEAD:{rel}"],
            check=True,
            capture_output=True,
            text=True,
        )
        return proc.stdout.strip()
    return git_blob_sha1(ROOT / rel)


def find_route(node: Any, route_id: str) -> dict[str, Any] | None:
    if isinstance(node, dict):
        if node.get("route_id") == route_id:
            return node
        for value in node.values():
            found = find_route(value, route_id)
            if found is not None:
                return found
    elif isinstance(node, list):
        for value in node:
            found = find_route(value, route_id)
            if found is not None:
                return found
    return None


def route_targets(route: dict[str, Any]) -> list[str] | None:
    for key in ("target_claim_ids", "target_theorems", "target_ids", "lean_theorems", "targets"):
        value = route.get(key)
        if isinstance(value, list) and all(isinstance(x, str) for x in value):
            return value
    for value in route.values():
        if isinstance(value, dict):
            result = route_targets(value)
            if result is not None:
                return result
    return None


def validation_errors(
    record: dict[str, Any] | None = None,
    routes: dict[str, Any] | None = None,
    overlay_text: str | None = None,
    check_files: bool = True,
) -> list[str]:
    errors: list[str] = []
    record = load(RECORD) if record is None else record
    routes = load(ROUTES) if routes is None else routes
    overlay_text = OVERLAY.read_text(encoding="utf-8") if overlay_text is None else overlay_text

    schema = load(SCHEMA)
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as exc:
        errors.append(f"invalid closed J2 scope-repair schema: {exc}")
    else:
        for err in sorted(Draft202012Validator(schema).iter_errors(record), key=lambda e: list(e.path)):
            location = ".".join(str(part) for part in err.path) or "$"
            errors.append(f"schema violation at {location}: {err.message}")

    exact = {
        "record_type": "openai_ten_proofs_result_family_scope_repair",
        "operation_id": "OTP-J2-TWO-DEGENERATE-SCOPE-REPAIR-001",
        "candidate_id": "OPENAI-TEN-PROOFS-001",
        "result_family": "OTP-J2-TWO-DEGENERATE",
        "route_id": "MC-ROUTE-OTP-J2-TWO-DEGENERATE",
        "repair_path": "path_a_source_faithful_projection",
        "status": "implementation_candidate_no_route_effect",
    }
    for key, expected in exact.items():
        if record.get(key) != expected:
            errors.append(f"{key} drift: expected {expected!r}, got {record.get(key)!r}")

    auth = record.get("authority", {})
    hs = auth.get("human_steward_authorization", {})
    if hs.get("comment_id") != EXPECTED_AUTH_COMMENT:
        errors.append("Human Steward authorization comment drift")
    if hs.get("decision") != "path_a_source_faithful_certification_target_repair":
        errors.append("Path A decision drift")
    if auth.get("protected_base") != "76c818cbabc4bc320d5865d2f896bbd17cba8a4e":
        errors.append("protected base drift")
    if auth.get("route_registry", {}).get("digest") != EXPECTED_ROUTE_REGISTRY_BLOB:
        errors.append("protected route-registry authority drift")

    source = record.get("current_source", {})
    if source.get("sha256") != EXPECTED_SOURCE_SHA256 or source.get("bytes") != EXPECTED_SOURCE_BYTES:
        errors.append("current manuscript identity drift")
    unauthorized = source.get("not_source_authorized", [])
    if len(unauthorized) != 1 or "two-coloring" not in unauthorized[0]:
        errors.append("stronger coloring-side source exclusion missing or weakened")

    formal = record.get("current_formal_subject", {})
    if formal.get("commit") != EXPECTED_FORMAL_COMMIT or formal.get("tree") != EXPECTED_FORMAL_TREE:
        errors.append("current formal subject identity drift")
    if formal.get("lake_manifest", {}).get("digest") != EXPECTED_LAKE_MANIFEST_BLOB:
        errors.append("current lake-manifest identity drift")
    if formal.get("comparator_config", {}).get("digest") != EXPECTED_CONFIG_BLOB:
        errors.append("J2 Comparator config identity drift")
    if formal.get("challenge", {}).get("digest") != EXPECTED_CHALLENGE_BLOB:
        errors.append("current J2 challenge identity drift")
    if formal.get("challenge", {}).get("historical_stronger_target") != EXPECTED_REGISTERED_TARGETS[0]:
        errors.append("historical stronger target identity drift")
    if formal.get("solution", {}).get("digest") != EXPECTED_SOLUTION_BLOB:
        errors.append("current J2 solution identity drift")

    if record.get("historical_registered_targets") != EXPECTED_REGISTERED_TARGETS:
        errors.append("historical registered target set drift")
    treatment = record.get("historical_target_treatment", {})
    required_false = [
        "route_target_identity_changed",
        "historical_stronger_declaration_rewritten",
        "stronger_coloring_conjunct_source_attributed",
        "stronger_coloring_conjunct_certification_authorized",
    ]
    for key in required_false:
        if treatment.get(key) is not False:
            errors.append(f"historical target treatment must keep {key}=false")

    projection = record.get("source_faithful_projection", {})
    artifact = projection.get("overlay_artifact", {})
    if artifact.get("digest") != EXPECTED_OVERLAY_BLOB:
        errors.append("source-faithful projection artifact identity drift")
    if projection.get("future_certification_scope") != EXPECTED_FUTURE_SCOPE:
        errors.append("source-faithful future scope drift")
    if projection.get("registered_route_mutation_required_before_adjudication") is not True:
        errors.append("future route-successor gate was weakened")
    if projection.get("may_silently_replace_registered_target_identity") is not False:
        errors.append("silent target replacement was enabled")

    dependency = record.get("dependency_audit", {})
    if dependency.get("stronger_coloring_conjunct_used") is not False:
        errors.append("dependency audit improperly uses stronger coloring conjunct")
    if dependency.get("machine_check") != "dependency_separation_theorem_reproves_refutation_from_source_faithful_core_only":
        errors.append("dependency-separation machine check drift")

    state = record.get("current_state", {})
    expected_state = {
        "route_state": "submitted",
        "may_adjudicate": False,
        "adjudication": None,
        "cert_output": None,
        "mathematical_target_proved": False,
        "may_promote_claim": False,
        "aggregate_authority": False,
    }
    if state != expected_state:
        errors.append("fail-closed J2 current state drift")

    effect = record.get("successor_effect", {})
    for key in ("route_transition", "adjudication_authorized", "cert_output_authorized"):
        if effect.get(key) is not False:
            errors.append(f"unauthorized successor effect: {key}")

    route = find_route(routes, "MC-ROUTE-OTP-J2-TWO-DEGENERATE")
    if route is None:
        errors.append("registered J2 route missing")
    else:
        status = route.get("intake_status", route.get("route_state", route.get("status")))
        if status != "submitted":
            errors.append(f"registered J2 route is not submitted: {status!r}")
        if route.get("cert_output") is not None:
            errors.append("registered J2 route gained a Cert output")
        targets = route_targets(route)
        if targets != EXPECTED_REGISTERED_TARGETS:
            errors.append(f"registered J2 route target drift: {targets!r}")

    marker = "theorem mathcert_sourceFaithfulTwoDegenerateExtremalCounterexample"
    dep_marker = "theorem mathcert_not_erdos_146_from_sourceFaithfulCore"
    if marker not in overlay_text or dep_marker not in overlay_text:
        errors.append("source-faithful overlay theorem missing")
    else:
        projection_signature = overlay_text.split(marker, 1)[1].split(":= by", 1)[0]
        if "Coloring" in projection_signature or "_hdegree" in projection_signature:
            errors.append("stronger coloring-side property leaked into projection signature")
        dependency_segment = overlay_text.split(dep_marker, 1)[1].split(
            "theorem mathcert_sourceFaithfulNotErdos146", 1
        )[0]
        if "twoDegenerateExtremalCounterexample" in dependency_segment:
            errors.append("dependency-separation theorem directly depends on stronger upstream theorem")

    if check_files:
        if not SCHEMA.is_file():
            errors.append("closed scope-repair schema missing")
        if repository_blob_sha1("governance/certification_routes.json") != EXPECTED_ROUTE_REGISTRY_BLOB:
            errors.append("route registry changed during scope-repair operation")
        if repository_blob_sha1(OVERLAY_REL) != EXPECTED_OVERLAY_BLOB:
            errors.append("source-faithful projection artifact changed after content addressing")
        for rel, expected in EXPECTED_HISTORICAL_BLOBS.items():
            path = ROOT / rel
            if not path.is_file():
                errors.append(f"historical J2 artifact missing: {rel}")
            elif repository_blob_sha1(rel) != expected:
                errors.append(f"historical J2 artifact rewritten: {rel}")

    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"J2 scope-repair validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print(
        "validated Path A J2 source-faithful projection, immutable historical J2 evidence, "
        "unchanged submitted route/no output state, complete formal identities, stronger-coloring "
        "exclusion, and dependency separation"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
