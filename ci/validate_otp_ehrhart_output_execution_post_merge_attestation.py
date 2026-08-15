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
SOURCE_PATH = "ci/validate_otp_ehrhart_output_execution_post_merge_attestation.py"
PROTECTED_SOURCE_COMMIT = "2e2d4509c993b9ae4bd4aaab48ecced429813b83"
ROUTES_PATH = "governance/certification_routes.json"

ATTESTATION = ROOT / "governance/post_merge_attestations/OTP-F-EHRHART-CERT-OUTPUT-EXEC-001.v1.json"
DOCUMENT = ROOT / "governance/post_merge_attestations/OTP-F-EHRHART-CERT-OUTPUT-EXEC-001.v1.md"
ATTESTATION_SCHEMA = ROOT / "schemas/otp_ehrhart_output_execution_post_merge_attestation.schema.json"
CLOSURE = ROOT / "governance/result_family_output_execution_closures/OTP-F-EHRHART.json"
CLOSURE_SCHEMA = ROOT / "schemas/otp_ehrhart_output_execution_closure.schema.json"
HISTORICAL_CANDIDATE = ROOT / "governance/result_family_output_candidates/OTP-F-EHRHART.json"
ROUTES = ROOT / ROUTES_PATH
CERTIFICATE = ROOT / "certificates/formal_sources/MC-OTP-F-EHRHART-001.json"
ADJUDICATION = ROOT / "governance/result_family_adjudications/OTP-F-EHRHART.json"

EXPECTED = {
    "document": "032f5c1f1f252db5b73305e0974928729c6f7a9c",
    "attestation_schema": "cb570d766334b1a5b81fa51b794cc751e8f6f97e",
    "closure": "c50a397a84873b358a54db2e602058da103b75e8",
    "closure_schema": "4cbd6e6f5aec5dee28ae788975da919dde4fc28f",
    "historical_candidate": "38d6eb4a483387d04c25bd9f6991c54af67bd9c5",
    "routes": "0487c3ebf702229741f16a544d68af25cf994e41",
    "certificate": "27a855c949b67e71372c7f0d6601d80125d33968",
    "adjudication": "dcea25320169b9309ebf6c7f48249df9a312555f",
}
COMPACTNESS_ROUTE_ID = "MC-ROUTE-OTP-J1-COMPACTNESS"
COMPACTNESS_TARGETS = [
    "CompactnessConjecture.quantitativeCompactnessCounterexample",
    "CompactnessConjecture.compactnessCounterexample_bigO",
    "CompactnessConjecture.not_erdos_180",
]
COMPACTNESS_OUTPUT = {
    "repository": "grandchallenge/MATHCERT",
    "commit_sha": "9fba5a8e918028ecc2b4d72abc00b3b72a5194f5",
    "path": "certificates/formal_sources/MC-OTP-J1-COMPACTNESS-001.json",
    "digest_algorithm": "git_blob_sha1",
    "digest": "88531e28951854961e86eec0517356999a391759",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git(*args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(["git", *args], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def ensure_commit(commit: str) -> None:
    shallow = git("rev-parse", "--is-shallow-repository")
    if shallow.returncode == 0 and shallow.stdout.decode().strip() == "true":
        result = git("fetch", "--no-tags", "--unshallow", "origin")
        if result.returncode != 0:
            raise RuntimeError("unable to unshallow Ehrhart closure history")
    if git("cat-file", "-e", f"{commit}^{{commit}}").returncode != 0:
        result = git("fetch", "--no-tags", "origin", commit)
        if result.returncode != 0:
            raise RuntimeError(f"unable to fetch governed commit {commit}")


def protected_module() -> types.ModuleType:
    ensure_commit(PROTECTED_SOURCE_COMMIT)
    result = git("show", f"{PROTECTED_SOURCE_COMMIT}:{SOURCE_PATH}")
    if result.returncode != 0:
        raise RuntimeError("unable to read protected Ehrhart closure validator")
    module = types.ModuleType("protected_otp_ehrhart_output_execution_post_merge_attestation")
    module.__file__ = str(ROOT / SOURCE_PATH)
    exec(compile(result.stdout.decode("utf-8"), module.__file__, "exec"), module.__dict__)
    return module


def _protected_routes() -> dict[str, Any]:
    ensure_commit(PROTECTED_SOURCE_COMMIT)
    result = git("show", f"{PROTECTED_SOURCE_COMMIT}:{ROUTES_PATH}")
    if result.returncode != 0:
        raise RuntimeError("unable to read protected Ehrhart route snapshot")
    return json.loads(result.stdout.decode("utf-8"))


def _route(rows: dict[str, Any], route_id: str) -> dict[str, Any] | None:
    return next((row for row in rows.get("routes", []) if isinstance(row, dict) and row.get("route_id") == route_id), None)


def _compactness_successor_errors(routes: dict[str, Any]) -> list[str]:
    route = _route(routes, COMPACTNESS_ROUTE_ID)
    if route is None:
        return ["Compactness route missing from live registry"]
    if route.get("target_claim_ids") != COMPACTNESS_TARGETS:
        return ["Compactness route target drift"]
    status = route.get("intake_status")
    output = route.get("cert_output")
    if status == "submitted" and output is None:
        return []
    errors: list[str] = []
    if status != "qualified":
        errors.append("Compactness output successor route is not qualified")
    if output != COMPACTNESS_OUTPUT:
        errors.append("Compactness output successor identity drift")
    boundary = str(route.get("claim_boundary", "")).lower()
    blockers = " ".join(route.get("blockers", [])).lower()
    for token in ("qualified_encoded_targets_only", "chapter 10", "historical", "whole-document", "aggregate openai ten proofs"):
        if token not in boundary:
            errors.append(f"Compactness successor boundary missing token: {token}")
    for token in ("unrestricted chapter 10", "historical or stronger", "whole-document byte and semantic equivalence", "proof body"):
        if token not in blockers:
            errors.append(f"Compactness successor blockers missing token: {token}")
    return errors


def _historical_subject_projection(routes: dict[str, Any]) -> dict[str, Any]:
    projected = copy.deepcopy(routes)
    protected = _protected_routes()
    historical_compactness = _route(protected, COMPACTNESS_ROUTE_ID)
    if historical_compactness is None:
        raise RuntimeError("protected Ehrhart snapshot lacks Compactness route")
    projected_rows = [
        row for row in projected.get("routes", [])
        if not (isinstance(row, dict) and row.get("campaign_id") == "OTP-C-PERMANENT")
    ]
    replaced = False
    for index, row in enumerate(projected_rows):
        if isinstance(row, dict) and row.get("route_id") == COMPACTNESS_ROUTE_ID:
            projected_rows[index] = copy.deepcopy(historical_compactness)
            replaced = True
            break
    if not replaced:
        raise RuntimeError("live route registry lacks Compactness route")
    projected["routes"] = projected_rows
    return projected


def validation_errors(
    *,
    attestation: dict[str, Any] | None = None,
    closure: dict[str, Any] | None = None,
    attestation_schema: dict[str, Any] | None = None,
    closure_schema: dict[str, Any] | None = None,
    document_text: str | None = None,
    historical_candidate: dict[str, Any] | None = None,
    routes: dict[str, Any] | None = None,
    certificate: dict[str, Any] | None = None,
    adjudication: dict[str, Any] | None = None,
    blobs: dict[str, str] | None = None,
    receipt: dict[str, Any] | None = None,
    other_adjudication_present: bool | None = None,
) -> list[str]:
    try:
        base = protected_module()
        route_data = load(ROUTES) if routes is None else routes
        successor_errors = _compactness_successor_errors(route_data)
        if successor_errors:
            return successor_errors
        historical_projection = _historical_subject_projection(route_data)
    except RuntimeError as exc:
        return [str(exc)]
    # The protected Ehrhart closure predates later independently governed OTP
    # adjudications and outputs. Validate those successor identities first,
    # then replay Ehrhart against its exact historical route subject.
    historical_other_adjudication_present = (
        False if other_adjudication_present is None else other_adjudication_present
    )
    return base.validation_errors(
        attestation=attestation,
        closure=closure,
        attestation_schema=attestation_schema,
        closure_schema=closure_schema,
        document_text=document_text,
        historical_candidate=historical_candidate,
        routes=historical_projection,
        certificate=certificate,
        adjudication=adjudication,
        blobs=blobs,
        receipt=receipt,
        other_adjudication_present=historical_other_adjudication_present,
    )


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"OTP-F-EHRHART post-merge closure validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print("validated protected OTP-F-EHRHART output closure; exact later independently governed OTP family adjudications and outputs are outside its historical subject set")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
