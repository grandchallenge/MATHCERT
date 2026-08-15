#!/usr/bin/env python3
"""Audit MATHCERT workflow and CI control reachability."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREFIXES = ("audit_", "build_", "check_", "replay_", "test_", "validate_", "verify_")


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
        if path.name.startswith(PREFIXES)
    }
    for path in sorted(discovered - set(records)):
        found.append(f"unregistered CI control: {path}")
    for path in sorted(set(records) - discovered):
        found.append(f"registered CI control is missing: {path}")

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

    workflow = (root / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    required = (
        "runs-on: ubuntu-24.04",
        'python-version: "3.13"',
        "permissions:\n  contents: read",
        "timeout-minutes:",
        "concurrency:",
        "cancel-in-progress: true",
        "requirements-ci.txt",
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
    print("validated pinned workflow policy and reachability of every registered MATHCERT control")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
