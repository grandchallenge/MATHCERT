#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import types
from pathlib import Path
from typing import Any

import validate_otp_permanent_execution_candidate as candidate_control

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = "ci/validate_otp_permanent_adjudication.py"
ROUTES_PATH = "governance/certification_routes.json"
PROTECTED_SOURCE_COMMIT = "e1deff40163730d61b974a8fdbee1d15466a23b9"
ROUTE_SNAPSHOT_COMMIT = "685faa7730b7147ba70ae0d0bb5fdd916b68c1a7"

EXPECTED_BLOBS = {
    "contract": "f9429395e7026f838ad6994b8f908a86506cfe06",
    "design_registry": "2af852600796e35afe034bbaf9b9e13950055a29",
    "candidate": "c9c764d6bffa580ff5a0f2229350b093ec5a3694",
    "candidate_manifest": "5b9ba2b7d2caf00063c38d4a9d8ccbfed334a4b8",
    "route_registry": "4b7f98414958999c8404e30a4a7c0a2a104578da",
}


def git(*args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(["git", *args], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def ensure_commit(commit: str) -> None:
    shallow = git("rev-parse", "--is-shallow-repository")
    if shallow.returncode == 0 and shallow.stdout.decode().strip() == "true":
        result = git("fetch", "--no-tags", "--unshallow", "origin")
        if result.returncode != 0:
            raise RuntimeError("unable to unshallow Permanent adjudication history")
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
    source = git_show(PROTECTED_SOURCE_COMMIT, SOURCE_PATH).decode("utf-8")
    module = types.ModuleType("protected_otp_permanent_adjudication")
    module.__file__ = str(ROOT / SOURCE_PATH)
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    return module


def snapshot_routes() -> dict[str, Any]:
    return json.loads(git_show(ROUTE_SNAPSHOT_COMMIT, ROUTES_PATH))


def defaults() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    base = protected_module()
    return base.load(base.RECORD), base.load(base.SCHEMA), snapshot_routes()


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
        historical_routes = snapshot_routes() if routes is None else routes
    except RuntimeError as exc:
        return [str(exc)]
    if candidate_errors is None:
        candidate_errors = candidate_control.validation_errors()
    return base.validation_errors(
        record=record,
        schema=schema,
        routes=historical_routes,
        candidate_errors=candidate_errors,
        authority_blobs=dict(EXPECTED_BLOBS) if authority_blobs is None else authority_blobs,
        evidence_files=evidence_files,
        certificate_present=False if certificate_present is None else certificate_present,
    )


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"OTP-C-PERMANENT adjudication validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print("validated protected OTP-C-PERMANENT adjudication against its exact submitted-route snapshot; restricted output is governed by the successor contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
