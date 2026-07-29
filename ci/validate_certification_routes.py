#!/usr/bin/env python3
"""Validate the machine-readable MATHCERT campaign route registry."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "governance" / "certification_routes.json"
SCHEMA_PATH = ROOT / "schemas" / "certification_route_registry.schema.json"

EXPECTED_CAMPAIGNS = {
    "UC-001", "NS-CI-001", "HC-001", "BSD-001",
    "PNP-001", "RH-001", "YM-001", "OZ-001",
}
EXPECTED_SOLVE_COMMIT = "68bbe0ae63c454b0dc63bedd0bc9f5501f8d5c03"
EXPECTED_TRACKERS = {
    "UC-001": 25, "NS-CI-001": 19, "HC-001": 23, "BSD-001": 26,
    "PNP-001": 27, "RH-001": 28, "YM-001": 29, "OZ-001": 30,
}
ADJUDICATED_STATES = {"certified", "qualified", "rejected", "proof_debt"}
POSITIVE_STATES = {"certified", "qualified"}
ALL_STATES = {"pending", "ready", "submitted"} | ADJUDICATED_STATES
ALGORITHMS = {"git_blob_sha1", "git_tree_sha1", "sha256"}
TOP_KEYS = {
    "schema_version", "registry_id", "provider_repository",
    "provider_base_commit", "programme_issue", "routes",
}
ROUTE_KEYS = {
    "route_id", "campaign_id", "tracker_issue", "source_manifest",
    "intake_status", "intake_packet", "target_claim_ids",
    "requested_modalities", "claim_boundary", "cert_output",
    "blockers", "reopening_conditions",
}
ARTIFACT_KEYS = {"repository", "commit_sha", "path", "digest_algorithm", "digest"}
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def artifact_errors(artifact: Any, label: str) -> list[str]:
    if not isinstance(artifact, dict):
        return [f"{label}: expected an artifact object"]
    errors: list[str] = []
    missing = ARTIFACT_KEYS - set(artifact)
    unknown = set(artifact) - ARTIFACT_KEYS
    if missing:
        errors.append(f"{label}: missing fields {sorted(missing)}")
    if unknown:
        errors.append(f"{label}: unknown fields {sorted(unknown)}")
    repository = str(artifact.get("repository", ""))
    if "/" not in repository:
        errors.append(f"{label}: repository must use owner/name form")
    if not HEX40.fullmatch(str(artifact.get("commit_sha", ""))):
        errors.append(f"{label}: commit_sha must be 40 lowercase hexadecimal characters")
    if not str(artifact.get("path", "")).strip():
        errors.append(f"{label}: path must not be empty")
    algorithm = artifact.get("digest_algorithm")
    digest = str(artifact.get("digest", ""))
    if algorithm not in ALGORITHMS:
        errors.append(f"{label}: unsupported digest algorithm {algorithm!r}")
    elif algorithm in {"git_blob_sha1", "git_tree_sha1"} and not HEX40.fullmatch(digest):
        errors.append(f"{label}: {algorithm} digest must be 40 lowercase hexadecimal characters")
    elif algorithm == "sha256" and not HEX64.fullmatch(digest):
        errors.append(f"{label}: sha256 digest must be 64 lowercase hexadecimal characters")
    if artifact.get("digest") == artifact.get("commit_sha"):
        errors.append(f"{label}: artifact digest must not be substituted with the repository commit")
    return errors


def route_errors(
    registry_path: Path = REGISTRY_PATH,
    schema_path: Path = SCHEMA_PATH,
) -> list[str]:
    instance = load_json(registry_path)
    load_json(schema_path)
    errors: list[str] = []
    if not isinstance(instance, dict):
        return [f"{registry_path}: registry must be a JSON object"]
    missing_top = TOP_KEYS - set(instance)
    unknown_top = set(instance) - TOP_KEYS
    if missing_top:
        errors.append(f"{registry_path}: missing top-level fields {sorted(missing_top)}")
    if unknown_top:
        errors.append(f"{registry_path}: unknown top-level fields {sorted(unknown_top)}")
    if instance.get("schema_version") != "1.0.0":
        errors.append(f"{registry_path}: schema_version must be 1.0.0")
    if instance.get("registry_id") != "MC-CERTIFICATION-ROUTES":
        errors.append(f"{registry_path}: registry_id must be MC-CERTIFICATION-ROUTES")
    if instance.get("provider_repository") != "grandchallenge/MATHCERT":
        errors.append(f"{registry_path}: provider_repository must be grandchallenge/MATHCERT")
    if not HEX40.fullmatch(str(instance.get("provider_base_commit", ""))):
        errors.append(f"{registry_path}: provider_base_commit must be a full commit SHA")

    raw_routes = instance.get("routes")
    if not isinstance(raw_routes, list) or not raw_routes:
        return errors + [f"{registry_path}: routes must be a nonempty array"]
    routes = [route for route in raw_routes if isinstance(route, dict)]
    if len(routes) != len(raw_routes):
        errors.append(f"{registry_path}: every route must be an object")
    ids = [str(route.get("campaign_id", "")) for route in routes]
    route_ids = [str(route.get("route_id", "")) for route in routes]
    actual = set(ids)

    for missing in sorted(EXPECTED_CAMPAIGNS - actual):
        errors.append(f"MATHCERT routes: governed campaign is uncovered: {missing}")
    for unknown in sorted(actual - EXPECTED_CAMPAIGNS):
        errors.append(f"MATHCERT routes: unrecognized campaign: {unknown}")
    for duplicate in sorted({value for value in ids if ids.count(value) > 1}):
        errors.append(f"MATHCERT routes: duplicate campaign_id {duplicate}")
    for duplicate in sorted({value for value in route_ids if route_ids.count(value) > 1}):
        errors.append(f"MATHCERT routes: duplicate route_id {duplicate}")

    seen_claims: dict[str, str] = {}
    for route in routes:
        campaign_id = str(route.get("campaign_id", ""))
        missing = ROUTE_KEYS - set(route)
        unknown = set(route) - ROUTE_KEYS
        if missing:
            errors.append(f"MATHCERT routes: {campaign_id} missing fields {sorted(missing)}")
        if unknown:
            errors.append(f"MATHCERT routes: {campaign_id} unknown fields {sorted(unknown)}")
        if route.get("route_id") != f"MC-ROUTE-{campaign_id}":
            errors.append(f"MATHCERT routes: {campaign_id} route_id is not canonical")

        expected_issue = EXPECTED_TRACKERS.get(campaign_id)
        expected_tracker = (
            f"https://github.com/grandchallenge/MATHCERT/issues/{expected_issue}"
            if expected_issue is not None else None
        )
        if expected_tracker and route.get("tracker_issue") != expected_tracker:
            errors.append(
                f"MATHCERT routes: {campaign_id} tracker drift; expected {expected_tracker}"
            )

        source = route.get("source_manifest")
        errors.extend(artifact_errors(source, f"{campaign_id}.source_manifest"))
        if isinstance(source, dict):
            if source.get("repository") != "grandchallenge/MATHSOLVE":
                errors.append(f"MATHCERT routes: {campaign_id} source must be MATHSOLVE")
            if source.get("commit_sha") != EXPECTED_SOLVE_COMMIT:
                errors.append(
                    f"MATHCERT routes: {campaign_id} Solve commit drift; "
                    f"expected {EXPECTED_SOLVE_COMMIT}"
                )
            expected_path = f"campaign_manifests/{campaign_id}.json"
            if source.get("path") != expected_path:
                errors.append(
                    f"MATHCERT routes: {campaign_id} source path drift; expected {expected_path}"
                )

        status = route.get("intake_status")
        packet = route.get("intake_packet")
        output = route.get("cert_output")
        if status not in ALL_STATES:
            errors.append(f"MATHCERT routes: {campaign_id} invalid intake_status {status!r}")
        elif status == "pending":
            if packet is not None or output is not None:
                errors.append(f"MATHCERT routes: {campaign_id} pending route must not carry packet/output")
            if not route.get("blockers"):
                errors.append(f"MATHCERT routes: {campaign_id} pending route must name blockers")
        elif status in {"ready", "submitted"}:
            if packet is None:
                errors.append(f"MATHCERT routes: {campaign_id} {status} route lacks intake packet")
            else:
                errors.extend(artifact_errors(packet, f"{campaign_id}.intake_packet"))
            if output is not None:
                errors.append(
                    f"MATHCERT routes: {campaign_id} {status} is intake-only and must not carry Cert output"
                )
        elif status in ADJUDICATED_STATES:
            if packet is None:
                errors.append(f"MATHCERT routes: {campaign_id} adjudication lacks intake packet")
            else:
                errors.extend(artifact_errors(packet, f"{campaign_id}.intake_packet"))
            if output is None:
                errors.append(f"MATHCERT routes: {campaign_id} adjudication lacks MATHCERT output")
            else:
                errors.extend(artifact_errors(output, f"{campaign_id}.cert_output"))
                if isinstance(output, dict) and output.get("repository") != "grandchallenge/MATHCERT":
                    errors.append(f"MATHCERT routes: {campaign_id} disposition output must be in MATHCERT")

        claims = route.get("target_claim_ids")
        if not isinstance(claims, list) or len(claims) != len(set(claims)):
            errors.append(f"MATHCERT routes: {campaign_id} target_claim_ids must be a unique array")
            claims = []
        for claim_id in claims:
            if claim_id in seen_claims:
                errors.append(
                    f"MATHCERT routes: duplicate target claim {claim_id}; "
                    f"first registered by {seen_claims[claim_id]}"
                )
            else:
                seen_claims[claim_id] = campaign_id

        if status in POSITIVE_STATES and not claims:
            errors.append(
                f"MATHCERT routes: {campaign_id} positive disposition must identify target claims"
            )
        if not str(route.get("claim_boundary", "")).strip():
            errors.append(f"MATHCERT routes: {campaign_id} claim_boundary must not be empty")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=REGISTRY_PATH)
    parser.add_argument("--schema", type=Path, default=SCHEMA_PATH)
    args = parser.parse_args(argv)
    errors = route_errors(args.registry, args.schema)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"MATHCERT route validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print(
        "validated MATHCERT route portfolio, exact Solve manifest identities, "
        "intake/adjudication separation, claim uniqueness, and artifact identities"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
