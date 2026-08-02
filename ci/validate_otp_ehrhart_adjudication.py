#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import types
from pathlib import Path
from typing import Any

import otp_ehrhart_candidate_control as candidate_control

ROOT = Path(__file__).resolve().parents[1]
BASE_COMMIT = "64e042ddb1147338ad7868a2847715fe7c1c079d"
SNAPSHOT_COMMIT = "686a48bb49015e4b8558bbc83d182f21f8b9e097"
SOURCE_PATH = "ci/validate_otp_ehrhart_adjudication.py"
ROUTES_PATH = "governance/certification_routes.json"


def git(*args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args], cwd=ROOT, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=False,
    )


def ensure_commit(commit: str) -> None:
    shallow = git("rev-parse", "--is-shallow-repository")
    if shallow.returncode == 0 and shallow.stdout.decode().strip() == "true":
        result = git("fetch", "--no-tags", "--unshallow", "origin")
        if result.returncode != 0:
            raise RuntimeError("unable to unshallow adjudication history")
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
    source = git_show(BASE_COMMIT, SOURCE_PATH).decode("utf-8")
    module = types.ModuleType("protected_otp_ehrhart_adjudication")
    module.__file__ = str(ROOT / SOURCE_PATH)
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    return module


def snapshot_routes() -> dict[str, Any]:
    return json.loads(git_show(SNAPSHOT_COMMIT, ROUTES_PATH))


def validation_errors(
    *,
    record: dict[str, Any] | None = None,
    schema: dict[str, Any] | None = None,
    routes: dict[str, Any] | None = None,
    candidate_errors: list[str] | None = None,
    authority_blobs: dict[str, str] | None = None,
    evidence_files: dict[str, bytes] | None = None,
    certificate_present: bool | None = None,
) -> list[str]:
    try:
        base = protected_module()
        route_data = snapshot_routes() if routes is None else routes
    except RuntimeError as exc:
        return [str(exc)]
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as handle:
        json.dump(route_data, handle, indent=2)
        handle.write("\n")
        route_file = Path(handle.name)
    original_candidate_routes = candidate_control.ROUTES
    try:
        candidate_control.ROUTES = route_file
        base.ROUTES = route_file
        return base.validation_errors(
            record=record,
            schema=schema,
            routes=route_data,
            candidate_errors=candidate_errors,
            authority_blobs=authority_blobs,
            evidence_files=evidence_files,
            certificate_present=certificate_present,
        )
    finally:
        candidate_control.ROUTES = original_candidate_routes
        route_file.unlink(missing_ok=True)


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"OTP-F-EHRHART adjudication validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print("validated protected OTP-F-EHRHART adjudication against its exact submitted-route snapshot; successor output is governed separately")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
