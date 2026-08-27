#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "governance/certification_route_state_consumers.json"
TOKEN = "certification_routes"
EXTENSIONS = {".py", ".sh", ".ps1"}
SKIP_PARTS = {".git", ".lake", "__pycache__"}
ALLOWED_CLASSES = {"HISTORICAL_SNAPSHOT", "CURRENT_STATE", "TRANSITION_STATE", "INVARIANT"}
ROUTES_REL = "governance/certification_routes.json"


def discover_consumers(root: Path = ROOT) -> set[str]:
    found: set[str] = set()
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in EXTENSIONS:
            continue
        rel_parts = path.relative_to(root).parts
        if any(part in SKIP_PARTS for part in rel_parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if TOKEN in text:
            found.add(path.relative_to(root).as_posix())
    return found


def load_manifest(path: Path = MANIFEST) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def blob_at(root: Path, commit: str, rel: str = ROUTES_REL) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", f"{commit}:{rel}"], text=True
    ).strip()


def validation_errors(
    root: Path = ROOT,
    manifest_path: Path = MANIFEST,
    *,
    check_git: bool = True,
) -> list[str]:
    errors: list[str] = []
    manifest = load_manifest(manifest_path)
    classified: dict[str, dict[str, Any]] = {}
    for row in manifest.get("consumers", []):
        path = row.get("path")
        if not isinstance(path, str) or not path:
            errors.append("classification with empty path")
            continue
        if path in classified:
            errors.append(f"duplicate classification: {path}")
            continue
        classified[path] = row
        cls = row.get("classification")
        if cls not in ALLOWED_CLASSES:
            errors.append(f"unknown classification: {path}: {cls}")
            continue
        if cls == "HISTORICAL_SNAPSHOT":
            commit = row.get("snapshot_commit")
            expected = row.get("snapshot_blob")
            if not isinstance(commit, str) or not commit:
                errors.append(f"historical consumer missing snapshot_commit: {path}")
            if not isinstance(expected, str) or not expected:
                errors.append(f"historical consumer missing snapshot_blob: {path}")
            if check_git and isinstance(commit, str) and commit and isinstance(expected, str) and expected:
                try:
                    actual = blob_at(root, commit)
                except Exception as exc:
                    errors.append(f"historical snapshot unavailable: {path}: {exc}")
                else:
                    if actual != expected:
                        errors.append(f"historical snapshot drift: {path}: {actual} != {expected}")
        elif "snapshot_commit" in row or "snapshot_blob" in row:
            errors.append(f"non-historical consumer has snapshot identity: {path}")

    discovered = discover_consumers(root)
    for path in sorted(discovered - set(classified)):
        errors.append(f"unclassified direct certification-route consumer: {path}")
    for path in sorted(set(classified) - discovered):
        errors.append(f"stale classification without direct token consumer: {path}")
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    discovered = discover_consumers(ROOT)
    print(
        "MC-CERTIFICATION-STATE-ARCHITECTURE-STABILIZATION-001: PASS "
        f"classified_direct_consumers={len(discovered)} unclassified=0 historical_snapshots_verified=true"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
