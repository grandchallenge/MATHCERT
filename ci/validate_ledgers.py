#!/usr/bin/env python3
"""Validate MATHCERT and provider claim ledgers without format blind spots."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

REQUIRED = {
    "claim_id",
    "claim_text",
    "claim_class",
    "support_type",
    "status",
    "source_or_artifact",
    "promotion_condition",
}
PACKAGE_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = PACKAGE_ROOT.parent
SCHEMA_ROOT = next(
    path
    for path in (
        WORKSPACE_ROOT / "MATH-PROGRAMME",
        WORKSPACE_ROOT,
        PACKAGE_ROOT,
    )
    if (path / "schemas" / "claim_ledger.schema.json").exists()
)
ARTIFACT_ROOT = WORKSPACE_ROOT if (WORKSPACE_ROOT / "MATHCERT").exists() else PACKAGE_ROOT
SCHEMA = json.loads(
    (SCHEMA_ROOT / "schemas" / "claim_ledger.schema.json").read_text(encoding="utf-8")
)
ITEM_SCHEMA = SCHEMA["properties"]["claims"]["items"]["properties"]
ENUM_FIELDS = {key: set(value["enum"]) for key, value in ITEM_SCHEMA.items() if "enum" in value}


def load_graph_refs() -> set[str]:
    graph_path = WORKSPACE_ROOT / "MATH-PROGRAMME" / "knowledge_graph" / "union_closed.json"
    if graph_path.exists():
        graph = json.loads(graph_path.read_text(encoding="utf-8"))
        return {node["node_id"] for node in graph["nodes"]}
    contract = json.loads(
        (PACKAGE_ROOT / "contracts" / "classification_discovery_refs.json").read_text(encoding="utf-8")
    )
    return set(contract["knowledge_graph_refs"])


ALLOWED_GRAPH_REFS = load_graph_refs()


def load_ledger(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(text)
    return yaml.safe_load(text)


def is_url(value: str) -> bool:
    return urlparse(value).scheme in {"http", "https"}


def artifact_exists(value: str) -> bool:
    path = Path(value)
    return (
        is_url(value)
        or (ARTIFACT_ROOT / path).exists()
        or (PACKAGE_ROOT / path).exists()
        or (path.parts and path.parts[0] == "MATHCERT" and (PACKAGE_ROOT / Path(*path.parts[1:])).exists())
    )


def is_mathcert_ledger(path: Path) -> bool:
    try:
        path.resolve().relative_to(PACKAGE_ROOT.resolve())
        return True
    except ValueError:
        return False


def validate_foundation_profile(data: dict, path: Path) -> int:
    errors = 0
    if data.get("foundation_doctrine_version") != 1:
        print(f"{path}: foundation_doctrine_version must be 1")
        return 1
    profile = data.get("foundational_profile")
    if not isinstance(profile, dict):
        print(f"{path}: foundational_profile must be present for foundation-aware ledgers")
        return 1
    for field in (
        "carrier_type", "carrier_description", "ambient_structure",
        "admissible_operations", "regularity", "axiom_profile",
        "witness_policy", "pathology_risk",
    ):
        if field not in profile:
            print(f"{path}: foundational_profile missing {field}")
            errors += 1
    axiom_profile = profile.get("axiom_profile")
    if isinstance(axiom_profile, dict) and axiom_profile.get("choice_usage") == "unknown":
        print(f"{path}: foundational_profile.axiom_profile.choice_usage must not be unknown")
        errors += 1
    pathology_risk = profile.get("pathology_risk")
    if isinstance(pathology_risk, dict) and pathology_risk.get("level") == "unknown":
        print(f"{path}: foundational_profile.pathology_risk.level must not be unknown")
        errors += 1
    return errors


def validate_foundation_certificate(path: Path, index: int, claim: dict) -> int:
    errors = 0
    certificate = claim.get("foundation_certificate")
    claim_id = claim.get("claim_id", f"index-{index}")
    if not isinstance(certificate, dict):
        print(f"{path}:{index}: {claim_id} missing foundation_certificate")
        return 1
    if certificate.get("statement_id") != claim_id:
        print(f"{path}:{index}: foundation_certificate.statement_id must match {claim_id}")
        errors += 1
    if not str(certificate.get("foundational_profile_ref", "")).strip():
        print(f"{path}:{index}: foundation_certificate.foundational_profile_ref must not be empty")
        errors += 1
    if certificate.get("ambient_structure_confirmed") is not True:
        print(f"{path}:{index}: foundation_certificate.ambient_structure_confirmed must be true")
        errors += 1
    regularity = certificate.get("regularity_confirmed")
    if not isinstance(regularity, dict) or regularity.get("status") not in {"confirmed", "not_applicable"}:
        print(f"{path}:{index}: foundation_certificate.regularity_confirmed.status must be confirmed or not_applicable")
        errors += 1
    boundary = certificate.get("checker_boundary")
    if not isinstance(boundary, dict):
        print(f"{path}:{index}: foundation_certificate.checker_boundary must be present")
        errors += 1
    else:
        if boundary.get("machine_check_status") not in {"checked", "partially_checked", "not_applicable"}:
            print(f"{path}:{index}: invalid checker machine_check_status")
            errors += 1
        if boundary.get("checker") in {None, "", "none", "unknown"}:
            print(f"{path}:{index}: foundation_certificate.checker_boundary.checker must be explicit")
            errors += 1
        if not str(boundary.get("replay_command", "")).strip():
            print(f"{path}:{index}: foundation_certificate.checker_boundary.replay_command must not be empty")
            errors += 1
    verdict = certificate.get("verdict")
    if not isinstance(verdict, dict) or verdict.get("status") not in {
        "certified", "provisionally_certified", "human_audited"
    }:
        print(f"{path}:{index}: foundation_certificate.verdict.status must be explicit")
        errors += 1
    return errors


def validate_provider_claim(path: Path, index: int, claim: dict, seen_ids: dict[str, Path]) -> int:
    errors = 0
    for field in ("claim_id", "statement", "status"):
        if not str(claim.get(field, "")).strip():
            print(f"{path}:{index}: provider claim missing {field}")
            errors += 1
    claim_id = str(claim.get("claim_id", ""))
    if claim_id:
        if claim_id in seen_ids:
            print(f"{path}:{index}: duplicate claim_id {claim_id}; first seen in {seen_ids[claim_id]}")
            errors += 1
        else:
            seen_ids[claim_id] = path
    return errors


def validate_mathcert_claim(
    path: Path, index: int, claim: dict, seen_ids: dict[str, Path], foundation_aware: bool
) -> int:
    errors = 0
    missing = REQUIRED - set(claim)
    if missing:
        print(f"{path}:{index}: missing {sorted(missing)}")
        return 1
    claim_id = claim["claim_id"]
    if claim_id in seen_ids:
        print(f"{path}:{index}: duplicate claim_id {claim_id}; first seen in {seen_ids[claim_id]}")
        errors += 1
    else:
        seen_ids[claim_id] = path
    for field, allowed in ENUM_FIELDS.items():
        if field in claim and claim[field] not in allowed:
            print(f"{path}:{index}: invalid {field} {claim[field]!r}")
            errors += 1
    if not str(claim["promotion_condition"]).strip():
        print(f"{path}:{index}: promotion_condition must not be empty")
        errors += 1
    artifacts = claim["source_or_artifact"]
    if not isinstance(artifacts, list) or not artifacts:
        print(f"{path}:{index}: source_or_artifact must be a nonempty list")
        errors += 1
    else:
        for artifact in artifacts:
            if not isinstance(artifact, str) or not artifact.strip():
                print(f"{path}:{index}: artifact entries must be nonempty strings")
                errors += 1
            elif not artifact_exists(artifact):
                print(f"{path}:{index}: missing artifact {artifact}")
                errors += 1
    for graph_ref in claim.get("knowledge_graph_refs", []):
        if graph_ref not in ALLOWED_GRAPH_REFS:
            print(f"{path}:{index}: unresolved knowledge_graph_ref {graph_ref}")
            errors += 1
    if (
        foundation_aware
        and is_mathcert_ledger(path)
        and claim.get("status") in {"CHECKED", "CERTIFIED"}
        and claim.get("claim_class") != "SUPERSEDED"
    ):
        errors += validate_foundation_certificate(path, index, claim)
    return errors


def validate(path: Path, seen_ids: dict[str, Path]) -> int:
    data = load_ledger(path)
    if not isinstance(data, dict) or not isinstance(data.get("claims"), list):
        print(f"{path}: expected a top-level claims list")
        return 1
    claims = data["claims"]
    if not claims:
        print(f"{path}: claims list must not be empty")
        return 1
    errors = 0
    foundation_aware = "foundation_doctrine_version" in data
    if foundation_aware:
        errors += validate_foundation_profile(data, path)
    for index, claim in enumerate(claims):
        if not isinstance(claim, dict):
            print(f"{path}:{index}: expected a mapping")
            errors += 1
            continue
        if REQUIRED.issubset(claim):
            errors += validate_mathcert_claim(path, index, claim, seen_ids, foundation_aware)
        elif {"claim_id", "statement", "status"}.issubset(claim):
            errors += validate_provider_claim(path, index, claim, seen_ids)
        else:
            print(f"{path}:{index}: unrecognized claim-ledger record shape")
            errors += 1
    return errors


def discover_ledgers(roots: list[Path] | None = None) -> list[Path]:
    if roots is None:
        roots = [PACKAGE_ROOT]
        solve_ledgers = WORKSPACE_ROOT / "MATHSOLVE" / "campaign_ledgers"
        if solve_ledgers.exists():
            roots.append(solve_ledgers)
    files: set[Path] = set()
    patterns = ("*claim*ledger*.yaml", "*claim*ledger*.yml", "*claim*ledger*.json")
    for root in roots:
        if not root.exists():
            continue
        for pattern in patterns:
            files.update(path for path in root.rglob(pattern) if ".lake" not in path.parts)
    return sorted(files)


def main() -> int:
    files = discover_ledgers()
    if not files:
        print("No claim ledgers found; certification coverage is invalid.", file=sys.stderr)
        return 1
    seen_ids: dict[str, Path] = {}
    errors = sum(validate(path, seen_ids) for path in files)
    if errors:
        print(f"Ledger validation failed with {errors} errors")
        return 1
    suffixes = sorted({path.suffix.lower() for path in files})
    print(f"Validated {len(files)} claim ledger(s) across {', '.join(suffixes)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
