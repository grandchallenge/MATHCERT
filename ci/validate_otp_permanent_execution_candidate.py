#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import subprocess
import sys
import types
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = "ci/validate_otp_permanent_execution_candidate.py"
ROUTES_PATH = "governance/certification_routes.json"
PROTECTED_SOURCE_COMMIT = "08ab265158e6165a1de59452d33d26b9e9b8fd54"
ROUTE_SNAPSHOT_COMMIT = "9406c91990a43880070d3a8bd468b4586fa94aef"
GOVERNED_SUCCESSOR_COMMIT = "48941f6351071c07f9b4685577f98d8bbda03536"
ROUTE_ID = "MC-ROUTE-OTP-C-PERMANENT-FORMULA"

CANDIDATE = ROOT / "governance/result_family_execution_candidates/OTP-C-PERMANENT.json"
MANIFEST = ROOT / "governance/result_family_execution_candidate_manifests/OTP-C-PERMANENT.json"
ROUTES = ROOT / ROUTES_PATH

EXPECTED_CONTRACT_BLOB = "f9429395e7026f838ad6994b8f908a86506cfe06"
EXPECTED_DESIGN_REGISTRY_BLOB = "2af852600796e35afe034bbaf9b9e13950055a29"
EXPECTED_ROUTES_BLOB = "4b7f98414958999c8404e30a4a7c0a2a104578da"


def git(*args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(["git", *args], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def ensure_commit(commit: str) -> None:
    shallow = git("rev-parse", "--is-shallow-repository")
    if shallow.returncode == 0 and shallow.stdout.decode().strip() == "true":
        result = git("fetch", "--no-tags", "--unshallow", "origin")
        if result.returncode != 0:
            raise RuntimeError("unable to unshallow Permanent candidate history")
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
    module = types.ModuleType("protected_otp_permanent_execution_candidate")
    module.__file__ = str(ROOT / SOURCE_PATH)
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    return module


def snapshot_routes() -> dict[str, Any]:
    return json.loads(git_show(ROUTE_SNAPSHOT_COMMIT, ROUTES_PATH))


def successor_routes() -> dict[str, Any]:
    return json.loads(git_show(GOVERNED_SUCCESSOR_COMMIT, ROUTES_PATH))


def _route(data: dict[str, Any]) -> dict[str, Any] | None:
    return next((r for r in data.get("routes", []) if isinstance(r, dict) and r.get("route_id") == ROUTE_ID), None)


def normalize_routes(routes: dict[str, Any] | None) -> dict[str, Any]:
    historical = snapshot_routes()
    if routes is None:
        return historical
    supplied = copy.deepcopy(routes)
    current = _route(supplied)
    successor = _route(successor_routes())
    if current == successor:
        historical_route = _route(historical)
        for index, row in enumerate(supplied.get("routes", [])):
            if isinstance(row, dict) and row.get("route_id") == ROUTE_ID:
                supplied["routes"][index] = copy.deepcopy(historical_route)
                break
    return supplied


def validation_errors(
    *,
    candidate: dict[str, Any] | None = None,
    manifest: dict[str, Any] | None = None,
    routes: dict[str, Any] | None = None,
    contract_blob: str | None = None,
    design_registry_blob: str | None = None,
    routes_blob: str | None = None,
) -> list[str]:
    try:
        base = protected_module()
        governed_routes = normalize_routes(routes)
    except RuntimeError as exc:
        return [str(exc)]
    return base.validation_errors(
        candidate=candidate,
        manifest=manifest,
        routes=governed_routes,
        contract_blob=EXPECTED_CONTRACT_BLOB if contract_blob is None else contract_blob,
        design_registry_blob=EXPECTED_DESIGN_REGISTRY_BLOB if design_registry_blob is None else design_registry_blob,
        routes_blob=EXPECTED_ROUTES_BLOB if routes_blob is None else routes_blob,
    )


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"Permanent execution-candidate validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print("validated historical OTP-C-PERMANENT execution candidate against its submitted-route snapshot; governed restricted-output successor is isolated separately")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
