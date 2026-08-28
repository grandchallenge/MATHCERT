#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

import certification_route_state as state

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "governance/certification_route_state_consumers.json"
TOKEN = "certification_routes"
EXTENSIONS = {".py", ".sh", ".ps1"}
SKIP_PARTS = {".git", ".lake", "__pycache__"}
ALLOWED_CLASSES = {"HISTORICAL_SNAPSHOT", "CURRENT_STATE", "TRANSITION_STATE", "INVARIANT"}
ROUTES_REL = "governance/certification_routes.json"
WORKFLOW_DIR_REL = Path(".github/workflows")
WORKFLOW_EXTENSIONS = {".yml", ".yaml"}
EXECUTOR_REL = "ci/certification_route_state.py"
PYTHON_INVOCATION = re.compile(
    r"(?<![A-Za-z0-9_.-])(?:python|python3|py)(?:\.exe)?\s+"
    r"(?P<path>ci/[A-Za-z0-9_./-]+\.py)(?![A-Za-z0-9_.-])"
)
BASH_INVOCATION = re.compile(
    r"(?m)(?:^\s*|(?:&&|\|\||;)\s*)(?:bash\s+)?(?:\./)?"
    r"(?P<path>ci/[A-Za-z0-9_./-]+\.sh)(?![A-Za-z0-9_.-])"
)
POWERSHELL_INVOCATION = re.compile(
    r"(?im)(?:^\s*|(?:&&|\|\||;)\s*)"
    r"(?:(?:pwsh|powershell)(?:\.exe)?(?:\s+-File)?\s+|&\s*)?(?:\./)?"
    r"(?P<path>ci/[A-Za-z0-9_./-]+\.ps1)(?![A-Za-z0-9_.-])"
)
WRAPPED_PYTHON = re.compile(
    rf"(?:python|python3|py)(?:\.exe)?\s+{re.escape(EXECUTOR_REL)}\s+exec\s+"
    r"(?P<path>ci/[A-Za-z0-9_./-]+\.py)(?![A-Za-z0-9_.-])"
)
WRAPPED_BASH = re.compile(
    rf"(?:python|python3|py)(?:\.exe)?\s+{re.escape(EXECUTOR_REL)}\s+exec-bash\s+"
    r"(?P<path>ci/[A-Za-z0-9_./-]+\.sh)(?![A-Za-z0-9_.-])"
)
WRAPPED_POWERSHELL = re.compile(
    rf"(?:python|python3|py)(?:\.exe)?\s+{re.escape(EXECUTOR_REL)}\s+exec-pwsh\s+"
    r"(?P<path>ci/[A-Za-z0-9_./-]+\.ps1)(?![A-Za-z0-9_.-])"
)


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


def _workflow_run_strings(node: Any) -> list[str]:
    runs: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "run" and isinstance(value, str):
                runs.append(value)
            else:
                runs.extend(_workflow_run_strings(value))
    elif isinstance(node, list):
        for value in node:
            runs.extend(_workflow_run_strings(value))
    return runs


def workflow_run_commands(root: Path = ROOT) -> list[tuple[str, str]]:
    workflow_dir = root / WORKFLOW_DIR_REL
    if not workflow_dir.exists():
        return []
    commands: list[tuple[str, str]] = []
    for path in sorted(workflow_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in WORKFLOW_EXTENSIONS:
            continue
        rel = path.relative_to(root).as_posix()
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        for run in _workflow_run_strings(payload):
            commands.append((rel, run))
    return commands


def _workflow_invocations(command: str) -> list[tuple[str, bool]]:
    wrapped_python = {m.group("path") for m in WRAPPED_PYTHON.finditer(command)}
    wrapped_bash = {m.group("path") for m in WRAPPED_BASH.finditer(command)}
    wrapped_powershell = {m.group("path") for m in WRAPPED_POWERSHELL.finditer(command)}
    found: set[tuple[str, bool]] = {
        *((path, True) for path in wrapped_python),
        *((path, True) for path in wrapped_bash),
        *((path, True) for path in wrapped_powershell),
    }
    for pattern in (PYTHON_INVOCATION, BASH_INVOCATION, POWERSHELL_INVOCATION):
        for match in pattern.finditer(command):
            path = match.group("path")
            if path == EXECUTOR_REL:
                continue
            wrapped = (
                path in wrapped_python
                or path in wrapped_bash
                or path in wrapped_powershell
            )
            found.add((path, wrapped))
    return sorted(found)


def workflow_state_bypass_errors(
    root: Path,
    manifest: dict[str, Any],
    *,
    edges: set[tuple[str, str]] | None = None,
) -> list[str]:
    edges = state.dependency_edges(root) if edges is None else edges
    errors: list[str] = []
    for workflow, command in workflow_run_commands(root):
        for consumer, wrapped in _workflow_invocations(command):
            row = state.effective_classification_for(
                consumer, manifest, root=root, edges=edges
            )
            if row is None or row.get("classification") != "HISTORICAL_SNAPSHOT":
                continue
            if wrapped:
                continue
            errors.append(
                "workflow historical certification-route consumer bypasses state executor: "
                f"{workflow}: {consumer}"
            )
    return sorted(set(errors))


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

    edges = state.dependency_edges(root)
    closure = state.dependency_closure(discovered, root, edges)
    for path in sorted(closure):
        try:
            row = state.effective_classification_for(
                path, manifest, root=root, edges=edges
            )
        except Exception as exc:
            errors.append(str(exc))
            continue
        if row is None:
            errors.append(f"unclassified transitive certification-route consumer: {path}")

    errors.extend(workflow_state_bypass_errors(root, manifest, edges=edges))
    return errors


def coverage_counts(
    root: Path = ROOT, manifest_path: Path = MANIFEST
) -> tuple[int, int, int]:
    direct = discover_consumers(root)
    edges = state.dependency_edges(root)
    closure = state.dependency_closure(direct, root, edges)
    manifest = load_manifest(manifest_path)
    workflow_historical_invocations = 0
    for _, command in workflow_run_commands(root):
        for consumer, _ in _workflow_invocations(command):
            row = state.effective_classification_for(
                consumer, manifest, root=root, edges=edges
            )
            if row is not None and row.get("classification") == "HISTORICAL_SNAPSHOT":
                workflow_historical_invocations += 1
    return len(direct), len(closure), workflow_historical_invocations


def main() -> int:
    errors = validation_errors()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    direct_count, closure_count, workflow_count = coverage_counts()
    print(
        "MC-CERTIFICATION-STATE-ARCHITECTURE-STABILIZATION-001: PASS "
        f"classified_direct_consumers={direct_count} "
        f"classified_dependency_closure={closure_count} "
        f"historical_workflow_invocations={workflow_count} "
        "unclassified=0 ambiguous=0 historical_snapshots_verified=true "
        "workflow_entrypoints_routed=true"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
