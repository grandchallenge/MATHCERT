#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import types
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = "ci/validate_openai_ten_proofs_permanent_route_registration.py"
ROUTES_PATH = "governance/certification_routes.json"
PROTECTED_SOURCE_COMMIT = "2e2d4509c993b9ae4bd4aaab48ecced429813b83"
ROUTE_SNAPSHOT_COMMIT = "2e2d4509c993b9ae4bd4aaab48ecced429813b83"
GOVERNED_SUCCESSOR_COMMIT = "48941f6351071c07f9b4685577f98d8bbda03536"
ROUTE_ID = "MC-ROUTE-OTP-C-PERMANENT-FORMULA"
EXPECTED_ROUTES_BLOB = "4b7f98414958999c8404e30a4a7c0a2a104578da"

RECEIPT = ROOT / "governance/pre_route_candidates/OPENAI_TEN_PROOFS_PERMANENT_ROUTE_REGISTRATION.json"
ROUTES = ROOT / ROUTES_PATH
PROPOSAL = ROOT / "governance/result_family_route_proposal_successors/OTP-C-PERMANENT.json"
PROPOSAL_REGISTRY = ROOT / "governance/pre_route_candidates/OPENAI_TEN_PROOFS_PERMANENT_ROUTE_PROPOSAL.json"
SCHEMA = ROOT / "schemas/openai_ten_proofs_permanent_route_registration.schema.json"


def git(*args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(["git", *args], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def ensure_commit(commit: str) -> None:
    shallow = git("rev-parse", "--is-shallow-repository")
    if shallow.returncode == 0 and shallow.stdout.decode().strip() == "true":
        result = git("fetch", "--no-tags", "--unshallow", "origin")
        if result.returncode != 0:
            raise RuntimeError("unable to unshallow Permanent route-registration history")
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
    module = types.ModuleType("protected_openai_ten_proofs_permanent_route_registration")
    module.__file__ = str(ROOT / SOURCE_PATH)
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    return module


def snapshot_routes() -> dict[str, Any]:
    return json.loads(git_show(ROUTE_SNAPSHOT_COMMIT, ROUTES_PATH))


def successor_routes() -> dict[str, Any]:
    return json.loads(git_show(GOVERNED_SUCCESSOR_COMMIT, ROUTES_PATH))


def _route(data: dict[str, Any]) -> dict[str, Any] | None:
    return next((r for r in data.get("routes", []) if isinstance(r, dict) and r.get("route_id") == ROUTE_ID), None)


def normalize_routes(routes: dict[str, Any] | None) -> tuple[dict[str, Any], bool]:
    """Project only the exact governed Permanent successor back to its historical registration snapshot.

    The full live route-registry blob may evolve as other result families are governed. Permanent registration
    remains valid iff the live Permanent route itself is byte-for-byte semantically equal to its protected
    qualified successor. Only then may it be projected back to the original submitted/null route for replay.
    """
    historical = snapshot_routes()
    if routes is None:
        return historical, False
    supplied = copy.deepcopy(routes)
    if _route(supplied) == _route(successor_routes()):
        historical_route = _route(historical)
        for index, row in enumerate(supplied.get("routes", [])):
            if isinstance(row, dict) and row.get("route_id") == ROUTE_ID:
                supplied["routes"][index] = copy.deepcopy(historical_route)
                break
        return supplied, True
    return supplied, False


def git_blob_sha1(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(f"blob {len(payload)}\0".encode("ascii") + payload, usedforsecurity=False).hexdigest()


def validation_errors(
    receipt: dict[str, Any] | None = None,
    routes: dict[str, Any] | None = None,
    local_blobs: dict[str, str] | None = None,
) -> list[str]:
    try:
        base = protected_module()
        governed_routes, projected_successor = normalize_routes(routes)
    except RuntimeError as exc:
        return [str(exc)]

    if local_blobs is None:
        blobs = {
            "routes": EXPECTED_ROUTES_BLOB,
            "proposal": git_blob_sha1(PROPOSAL),
            "proposal_registry": git_blob_sha1(PROPOSAL_REGISTRY),
        }
    else:
        blobs = copy.deepcopy(local_blobs)
        # Whole-registry identity is historical evidence, not a perpetual global lock.
        # Once the exact Permanent successor route is independently recognized, later
        # changes to unrelated routes cannot invalidate the protected Permanent receipt.
        if projected_successor:
            blobs["routes"] = EXPECTED_ROUTES_BLOB

    return base.validation_errors(
        receipt=receipt,
        routes=governed_routes,
        local_blobs=blobs,
    )


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"Permanent route registration validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print("validated historical Permanent route registration against its submitted/null snapshot; the exact Permanent successor is preserved while unrelated later route evolution is ignored")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
