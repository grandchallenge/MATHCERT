#!/usr/bin/env python3
"""Audit MATHCERT workflow and CI control reachability."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_PREFIXES = ("audit_", "check_", "replay_", "test_", "validate_")
REGISTERED_EXECUTABLE_PREFIXES = ("build_", "verify_")
PLATFORM_MANIFEST = "governance/certification_platform_lane.json"
PLATFORM_WORKFLOW_PATH_LISTS = ("shared_platform_paths", "lane_support_paths")
SCOPE_TOKEN = "check_certification_platform_lane.py --certification-scope"


def errors(root: Path = ROOT) -> list[str]:
    registry = json.loads(
        (root / "governance" / "ci_control_registry.json").read_text(encoding="utf-8")
    )
    found: list[str] = []
    records = {
        str(item.get("path")): item
        for item in registry.get("controls", [])
        if isinstance(item, dict)
    }
    discovered = {
        f"ci/{path.name}"
        for path in (root / "ci").glob("*.py")
        if path.name.startswith(CANONICAL_PREFIXES)
    }

    workflow = (root / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    workflow_controls: set[str] = set()
    declared_unregistered: set[str] = set()
    platform_manifest_path = root / PLATFORM_MANIFEST
    if platform_manifest_path.exists():
        platform_manifest = json.loads(platform_manifest_path.read_text(encoding="utf-8"))
        declared_platform_paths: set[str] = set()
        for key in PLATFORM_WORKFLOW_PATH_LISTS:
            declared_platform_paths.update(
                str(path)
                for path in platform_manifest.get(key, [])
                if isinstance(path, str)
            )
        # A declared platform control already present in the CI registry remains a
        # canonical-runner control. Only declared controls that are otherwise
        # unregistered may be admitted as workflow-level preflight controls, and
        # then only when ci.yml reaches them directly.
        declared_unregistered = (discovered - set(records)).intersection(declared_platform_paths)
        workflow_controls = {
            path for path in declared_unregistered if path in workflow
        }
        for path in sorted(declared_unregistered - workflow_controls):
            found.append(f"platform workflow control is not reached by .github/workflows/ci.yml: {path}")

    for path in sorted(discovered - set(records) - declared_unregistered):
        found.append(f"unregistered CI control: {path}")

    for relative, record in sorted(records.items()):
        path = root / relative
        if not path.exists():
            found.append(f"registered CI control is missing: {relative}")
            continue
        name = path.name
        if not name.startswith(CANONICAL_PREFIXES + REGISTERED_EXECUTABLE_PREFIXES):
            found.append(f"registered CI control has unsupported executable prefix: {relative}")

    texts: dict[str, str] = {}
    for relative in registry.get("orchestrators", []):
        path = root / relative
        if not path.exists():
            found.append(f"missing orchestrator: {relative}")
        else:
            texts[relative] = path.read_text(encoding="utf-8")

    direct = {path for path, record in records.items() if record.get("mode") == "direct"}
    for path in sorted(direct):
        for orchestrator, text in texts.items():
            if path not in text:
                found.append(f"{path} is not reached by {orchestrator}")
    for path, record in records.items():
        mode = record.get("mode")
        if mode == "library":
            if record.get("exercised_by") not in direct:
                found.append(f"{path}: library checker lacks a direct exercising test")
        elif mode != "direct":
            found.append(f"{path}: unknown control mode {mode!r}")

    for orchestrator in ("ci/check_lean.sh", "ci/check_lean.ps1"):
        text = texts.get(orchestrator, "")
        if SCOPE_TOKEN not in text:
            found.append(f"canonical orchestrator lacks context-aware certification scope: {orchestrator}")
        if "FULL_ESTATE" not in text or "MATHCERT_CONTEXT_SKIP" not in text:
            found.append(f"canonical orchestrator lacks fail-closed full-estate/scoped execution markers: {orchestrator}")

    required = (
        "runs-on: ubuntu-24.04",
        'python-version: "3.13"',
        "permissions:\n  contents: read",
        "timeout-minutes:",
        "concurrency:",
        "cancel-in-progress: true",
        "requirements-ci.txt",
        "workflow_dispatch:",
    )
    for token in required:
        if token not in workflow:
            found.append(f"workflow policy token is missing: {token}")
    for line in workflow.splitlines():
        stripped = line.strip()
        if not stripped.startswith("- uses:"):
            continue
        reference = stripped.split("@", 1)
        if len(reference) != 2:
            found.append(f"workflow action lacks commit identity: {stripped}")
            continue
        sha = reference[1].split()[0]
        if len(sha) != 40 or any(char not in "0123456789abcdef" for char in sha):
            found.append(f"workflow action is not pinned by full commit SHA: {stripped}")
    return found


def main() -> int:
    found = errors()
    if found:
        print("\n".join(found), file=sys.stderr)
        print(f"CI reachability audit failed with {len(found)} error(s)", file=sys.stderr)
        return 1
    print("validated pinned workflow policy, context-aware/full-estate orchestration, and reachability of every registered runner or declared workflow-level MATHCERT control")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
