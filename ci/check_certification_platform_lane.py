#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Iterable

_DEFAULT_ROOT = Path(__file__).resolve().parents[1]
ROOT = Path(os.environ.get("MC_PLATFORM_ROOT", str(_DEFAULT_ROOT))).resolve()
MANIFEST_PATH = Path(
    os.environ.get(
        "MC_PLATFORM_MANIFEST",
        str(ROOT / "governance" / "certification_platform_lane.json"),
    )
).resolve()


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, object]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "control_id",
        "platform_branch_prefix",
        "shared_platform_paths",
        "stateful_shared_validator_paths",
        "lane_support_paths",
    }
    missing = sorted(required - set(obj))
    if missing:
        raise ValueError(f"platform-lane manifest missing fields: {missing}")
    return obj


def evaluate(branch: str, changed_paths: Iterable[str], manifest: dict[str, object]) -> list[str]:
    paths = sorted({str(path) for path in changed_paths if str(path)})
    prefix = str(manifest["platform_branch_prefix"])
    platform_only = {str(path) for path in manifest["shared_platform_paths"]}  # type: ignore[index]
    stateful = {str(path) for path in manifest["stateful_shared_validator_paths"]}  # type: ignore[index]
    support = {str(path) for path in manifest["lane_support_paths"]}  # type: ignore[index]
    protected = platform_only | support
    protected_changes = sorted(protected.intersection(paths))
    is_platform = branch.startswith(prefix)

    errors: list[str] = []
    if protected_changes and not is_platform:
        errors.append(
            "certification-platform files may only change on "
            f"{prefix}* branches: {', '.join(protected_changes)}"
        )

    if is_platform:
        allowed = platform_only | stateful | support
        outside = sorted(path for path in paths if path not in allowed)
        if outside:
            errors.append(
                "certification-platform lane contains non-platform payload: "
                + ", ".join(outside)
            )

    return errors


def changed_paths_for_pull_request(base_ref: str) -> list[str]:
    base = f"origin/{base_ref}"
    try:
        subprocess.run(
            ["git", "rev-parse", "--verify", base],
            cwd=ROOT,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"missing {base}; canonical checkout must use fetch-depth: 0"
        ) from exc
    output = subprocess.check_output(
        ["git", "diff", "--name-only", "--diff-filter=ACMRD", f"{base}...HEAD"],
        cwd=ROOT,
        text=True,
    )
    return [line.strip() for line in output.splitlines() if line.strip()]


def main() -> int:
    try:
        manifest = load_manifest()
        event = os.environ.get("GITHUB_EVENT_NAME", "")
        branch = os.environ.get("GITHUB_HEAD_REF", "")
        base_ref = os.environ.get("GITHUB_BASE_REF", "")

        if event != "pull_request" or not branch or not base_ref:
            print("MC-PLATFORM-LANE-001: non-pull-request context; manifest valid")
            return 0

        paths = changed_paths_for_pull_request(base_ref)
        errors = evaluate(branch, paths, manifest)
        if errors:
            for error in errors:
                print(f"MC-PLATFORM-LANE-001: {error}", file=sys.stderr)
            return 1

        print(
            "MC-PLATFORM-LANE-001: PASS "
            f"branch={branch} changed_paths={len(paths)}"
        )
        return 0
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        print(f"MC-PLATFORM-LANE-001: guard failure: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
