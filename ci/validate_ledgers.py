#!/usr/bin/env python3
"""Validate claim ledgers against the programme vocabulary and artifact trail."""
from __future__ import annotations
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

try:
    import yaml
except Exception as exc:
    print("PyYAML is required for ledger validation", file=sys.stderr)
    raise

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


def validate(path: Path, seen_ids: dict[str, Path]) -> int:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("claims"), list):
        print(f"{path}: expected a top-level claims list")
        return 1
    claims = data["claims"]
    errors = 0
    for i, claim in enumerate(claims):
        if not isinstance(claim, dict):
            print(f"{path}:{i}: expected a mapping")
            errors += 1
            continue
        missing = REQUIRED - set(claim)
        if missing:
            print(f"{path}:{i}: missing {sorted(missing)}")
            errors += 1
            continue
        claim_id = claim["claim_id"]
        if claim_id in seen_ids:
            print(f"{path}:{i}: duplicate claim_id {claim_id}; first seen in {seen_ids[claim_id]}")
            errors += 1
        else:
            seen_ids[claim_id] = path
        for field, allowed in ENUM_FIELDS.items():
            if field in claim and claim[field] not in allowed:
                print(f"{path}:{i}: invalid {field} {claim[field]!r}")
                errors += 1
        if not str(claim["promotion_condition"]).strip():
            print(f"{path}:{i}: promotion_condition must not be empty")
            errors += 1
        artifacts = claim["source_or_artifact"]
        if not isinstance(artifacts, list) or not artifacts:
            print(f"{path}:{i}: source_or_artifact must be a nonempty list")
            errors += 1
            continue
        for artifact in artifacts:
            if not isinstance(artifact, str) or not artifact.strip():
                print(f"{path}:{i}: artifact entries must be nonempty strings")
                errors += 1
                continue
            if not artifact_exists(artifact):
                print(f"{path}:{i}: missing artifact {artifact}")
                errors += 1
        for graph_ref in claim.get("knowledge_graph_refs", []):
            if graph_ref not in ALLOWED_GRAPH_REFS:
                print(f"{path}:{i}: unresolved knowledge_graph_ref {graph_ref}")
                errors += 1
    return errors


def main() -> int:
    roots = (
        [PACKAGE_ROOT]
        if ARTIFACT_ROOT == PACKAGE_ROOT
        else [
            ARTIFACT_ROOT / "templates",
            ARTIFACT_ROOT / "MATHSOLVE",
            ARTIFACT_ROOT / "MATHCERT",
        ]
    )
    files = []
    for root in roots:
        if root.exists():
            files.extend(root.rglob("*claim*ledger*.yaml"))
    if not files:
        print("No claim ledgers found; nothing to validate.")
        return 0
    seen_ids: dict[str, Path] = {}
    errors = sum(validate(p, seen_ids) for p in files)
    if errors:
        print(f"Ledger validation failed with {errors} errors")
        return 1
    print(f"Validated {len(files)} claim ledger(s)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
