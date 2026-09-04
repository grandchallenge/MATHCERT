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

FULL_ESTATE_SCOPE = "FULL_ESTATE"
FAMILY_MARKERS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("OTP-B2-SPHERICAL-CODES", ("otp-b2-spherical-codes", "otp_b2_spherical_codes", "spherical-codes", "spherical_codes")),
    ("OTP-B1-BINARY-CODES", ("otp-b1-binary-codes", "otp_b1_binary_codes", "binary-codes", "binary_codes")),
    ("OTP-H-GAPCVP", ("otp-h-gapcvp", "otp_h_gapcvp", "gapcvp")),
    ("OTP-C-PERMANENT", ("otp-c-permanent", "otp_c_permanent", "permanent")),
    ("OTP-J1-COMPACTNESS", ("otp-j1-compactness", "otp_j1_compactness", "compactness")),
    ("OTP-F-EHRHART", ("otp-f-ehrhart", "otp_f_ehrhart", "ehrhart")),
    ("OTP-J2-TWO-DEGENERATE", ("otp-j2-two-degenerate", "otp_j2_two_degenerate", "otp_j2", "two-degenerate", "two_degenerate")),
    ("OTP-A-SPHERE-PACKING", ("otp-a-sphere-packing", "otp_a_sphere_packing", "sphere-packing", "sphere_packing")),
)
GLOBAL_FAMILY_TRANSITION_PATHS = {
    "governance/certification_routes.json",
    "governance/ci_control_registry.json",
}


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, object]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "control_id",
        "platform_branch_prefix",
        "shared_platform_paths",
        "stateful_shared_validator_paths",
        "stateful_workflow_paths",
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
    stateful_validators = {str(path) for path in manifest["stateful_shared_validator_paths"]}  # type: ignore[index]
    stateful_workflows = {str(path) for path in manifest["stateful_workflow_paths"]}  # type: ignore[index]
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
        allowed = platform_only | stateful_validators | stateful_workflows | support
        outside = sorted(path for path in paths if path not in allowed)
        if outside:
            errors.append(
                "certification-platform lane contains non-platform payload: "
                + ", ".join(outside)
            )

    return errors


def family_for_path(path: str) -> str | None:
    normalized = path.lower()
    for family, markers in FAMILY_MARKERS:
        if any(marker in normalized for marker in markers):
            return family
    return None


def certification_scope(
    branch: str,
    changed_paths: Iterable[str],
    manifest: dict[str, object],
) -> str:
    """Return one exact family scope or fail closed to FULL_ESTATE.

    Family-scoped execution is allowed only when every non-global changed path
    is unambiguously attributable to one result family. Platform branches,
    unknown paths, zero-family changes, and multi-family changes run the full
    certification estate.
    """
    if branch.startswith(str(manifest["platform_branch_prefix"])):
        return FULL_ESTATE_SCOPE

    neutral = GLOBAL_FAMILY_TRANSITION_PATHS | {
        str(path) for path in manifest["stateful_shared_validator_paths"]  # type: ignore[index]
    }
    families: set[str] = set()
    for raw in sorted({str(path) for path in changed_paths if str(path)}):
        if raw in neutral:
            continue
        family = family_for_path(raw)
        if family is None:
            return FULL_ESTATE_SCOPE
        families.add(family)
        if len(families) > 1:
            return FULL_ESTATE_SCOPE

    if len(families) != 1:
        return FULL_ESTATE_SCOPE
    return next(iter(families))


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


def current_certification_scope(manifest: dict[str, object]) -> str:
    if os.environ.get("MC_CERT_FORCE_FULL") == "1":
        return FULL_ESTATE_SCOPE
    event = os.environ.get("GITHUB_EVENT_NAME", "")
    branch = os.environ.get("GITHUB_HEAD_REF", "")
    base_ref = os.environ.get("GITHUB_BASE_REF", "")
    if event != "pull_request" or not branch or not base_ref:
        return FULL_ESTATE_SCOPE
    paths = changed_paths_for_pull_request(base_ref)
    return certification_scope(branch, paths, manifest)


def main() -> int:
    try:
        manifest = load_manifest()
        if len(sys.argv) == 2 and sys.argv[1] == "--certification-scope":
            print(current_certification_scope(manifest))
            return 0

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

        scope = certification_scope(branch, paths, manifest)
        print(
            "MC-PLATFORM-LANE-001: PASS "
            f"branch={branch} changed_paths={len(paths)} certification_scope={scope}"
        )
        return 0
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        print(f"MC-PLATFORM-LANE-001: guard failure: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
