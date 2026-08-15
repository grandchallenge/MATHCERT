#!/usr/bin/env python3
"""Validate the bounded VGSE route overlay against its pinned historical base."""
from __future__ import annotations

import json
import subprocess
import sys
import types
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = "ci/validate_vgse_route_registration.py"
ROUTES_PATH = "governance/certification_routes.json"
PROTECTED_BASE_COMMIT = "2e2d4509c993b9ae4bd4aaab48ecced429813b83"
EXPECTED_BASE_BLOB = "4b7f98414958999c8404e30a4a7c0a2a104578da"

RECORD_PATH = ROOT / "governance" / "certification_route_overlays" / "VGSE-001.json"
SCHEMA_PATH = ROOT / "schemas" / "vgse_route_registration.schema.json"
BASE_REGISTRY_PATH = ROOT / ROUTES_PATH
DOC_PATH = ROOT / "docs" / "work_packages" / "MC-VGSE-WP00-ROUTE-001.md"


def git(*args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(["git", *args], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def ensure_commit(commit: str) -> None:
    shallow = git("rev-parse", "--is-shallow-repository")
    if shallow.returncode == 0 and shallow.stdout.decode().strip() == "true":
        result = git("fetch", "--no-tags", "--unshallow", "origin")
        if result.returncode != 0:
            raise RuntimeError("unable to unshallow VGSE route history")
    if git("cat-file", "-e", f"{commit}^{{commit}}").returncode != 0:
        result = git("fetch", "--no-tags", "origin", commit)
        if result.returncode != 0:
            raise RuntimeError(f"unable to fetch governed commit {commit}")


def git_show(commit: str, path: str) -> bytes:
    ensure_commit(commit)
    result = git("show", f"{commit}:{path}")
    if result.returncode != 0:
        raise RuntimeError(f"unable to read {path} at {commit}")
    return result.stdout


def protected_module() -> types.ModuleType:
    source = git_show(PROTECTED_BASE_COMMIT, SOURCE_PATH).decode("utf-8")
    module = types.ModuleType("protected_vgse_route_registration")
    module.__file__ = str(ROOT / SOURCE_PATH)
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    return module


def snapshot_registry() -> dict[str, Any]:
    return json.loads(git_show(PROTECTED_BASE_COMMIT, ROUTES_PATH))


def validation_errors(
    record: dict[str, Any] | None = None,
    *,
    schema: dict[str, Any] | None = None,
    base_registry: dict[str, Any] | None = None,
    base_blob: str | None = None,
    documentation: str | None = None,
) -> list[str]:
    try:
        base = protected_module()
        pinned_registry = snapshot_registry() if base_registry is None else base_registry
    except RuntimeError as exc:
        return [str(exc)]
    return base.validation_errors(
        record,
        schema=schema,
        base_registry=pinned_registry,
        base_blob=EXPECTED_BASE_BLOB if base_blob is None else base_blob,
        documentation=documentation,
    )


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"VGSE route registration failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print("validated VGSE pending route against its pinned historical base; later certification-route transitions are isolated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
