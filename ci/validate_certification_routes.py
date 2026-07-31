#!/usr/bin/env python3
"""Validate exact MATHCERT campaign routes and intake/adjudication boundaries."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "governance" / "certification_routes.json"
SCHEMA_PATH = ROOT / "schemas" / "certification_route_registry.schema.json"
EXPECTED_SOLVE_COMMIT = "90b3ee6eb12e9224737f09a56dd4578f6baed750"
EXPECTED_TRACKERS = {"UC-001":25,"NS-CI-001":19,"HC-001":23,"BSD-001":26,"PNP-001":27,"RH-001":28,"YM-001":29,"OZ-001":30}
EXPECTED_MANIFESTS = {"UC-001":"55629c3004b8bffc35fc0fa6f5fbc711ff48aa3c","NS-CI-001":"35f7cd6ccf0e27f199571189fcb34a3f8adc31d7","HC-001":"48e3a0c22299147fe48cb4288cda813d7cffdcb4","BSD-001":"3fb3b07400915d90047a06a353537cf2e1593b9e","PNP-001":"6ecdfa0714828518878ccaf2cdc65756a5955186","RH-001":"0b58fa0ed35907eddf89062069793987b3b03f2e","YM-001":"733d11811d0226fa2b2467965c3655a7d0fad963","OZ-001":"8b3164ab88a35ec9fba69013b44056573e846bfe"}
EXPECTED_READY_PACKETS = {"UC-001":"8369bc21e45be6af71d2a0cdb0c5ab3cb5313bfb","NS-CI-001":"58b10636bd614e91e6c35900b9f5fb68e7f88afb","HC-001":"0c154af2e577e4367f9f5d0aeac5e15f9420172c"}
EXPECTED_STATES = {cid:("ready" if cid in EXPECTED_READY_PACKETS else "pending") for cid in EXPECTED_MANIFESTS}
ADJUDICATED_STATES = {"certified","qualified","rejected","proof_debt"}
POSITIVE_STATES = {"certified","qualified"}
ALL_STATES = {"pending","ready","submitted"} | ADJUDICATED_STATES
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
ARTIFACT_KEYS = {"repository","commit_sha","path","digest_algorithm","digest"}
ROUTE_KEYS = {"route_id","campaign_id","tracker_issue","source_manifest","intake_status","intake_packet","target_claim_ids","requested_modalities","claim_boundary","cert_output","blockers","reopening_conditions"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def artifact_errors(value: Any, label: str) -> list[str]:
    if not isinstance(value, dict):
        return [f"{label}: expected an artifact object"]
    errors: list[str] = []
    if set(value) != ARTIFACT_KEYS:
        errors.append(f"{label}: artifact fields drift")
    commit = str(value.get("commit_sha", ""))
    digest = str(value.get("digest", ""))
    algorithm = value.get("digest_algorithm")
    if "/" not in str(value.get("repository", "")):
        errors.append(f"{label}: repository must use owner/name form")
    if not HEX40.fullmatch(commit):
        errors.append(f"{label}: invalid commit_sha")
    if not str(value.get("path", "")).strip():
        errors.append(f"{label}: empty path")
    if algorithm in {"git_blob_sha1","git_tree_sha1"} and not HEX40.fullmatch(digest):
        errors.append(f"{label}: invalid Git digest")
    elif algorithm == "sha256" and not HEX64.fullmatch(digest):
        errors.append(f"{label}: invalid SHA-256 digest")
    elif algorithm not in {"git_blob_sha1","git_tree_sha1","sha256"}:
        errors.append(f"{label}: unsupported digest algorithm")
    if digest == commit:
        errors.append(f"{label}: artifact digest must not be substituted with the repository commit")
    return errors


def route_errors(registry_path: Path = REGISTRY_PATH, schema_path: Path = SCHEMA_PATH) -> list[str]:
    data = load_json(registry_path)
    load_json(schema_path)
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["registry must be an object"]
    if data.get("schema_version") != "1.0.0" or data.get("registry_id") != "MC-CERTIFICATION-ROUTES":
        errors.append("registry identity drift")
    if data.get("provider_repository") != "grandchallenge/MATHCERT":
        errors.append("provider repository drift")
    if not HEX40.fullmatch(str(data.get("provider_base_commit", ""))):
        errors.append("provider_base_commit must be a full SHA")
    routes = data.get("routes")
    if not isinstance(routes, list):
        return errors + ["routes must be an array"]
    route_map = {r.get("campaign_id"):r for r in routes if isinstance(r, dict)}
    missing_campaigns = set(EXPECTED_MANIFESTS) - set(route_map)
    unknown_campaigns = set(route_map) - set(EXPECTED_MANIFESTS)
    for cid in sorted(missing_campaigns):
        errors.append(f"governed campaign is uncovered: {cid}")
    for cid in sorted(unknown_campaigns):
        errors.append(f"unrecognized campaign: {cid}")
    if len(route_map) != len(routes):
        errors.append("campaign route uniqueness drift")
    seen_claims: dict[str,str] = {}
    for cid, route in route_map.items():
        if cid not in EXPECTED_MANIFESTS:
            continue
        if set(route) != ROUTE_KEYS:
            errors.append(f"{cid}: route fields drift")
        if route.get("route_id") != f"MC-ROUTE-{cid}":
            errors.append(f"{cid}: route_id is not canonical")
        expected_tracker = f"https://github.com/grandchallenge/MATHCERT/issues/{EXPECTED_TRACKERS[cid]}"
        if route.get("tracker_issue") != expected_tracker:
            errors.append(f"{cid}: tracker drift; expected {expected_tracker}")
        source = route.get("source_manifest")
        errors.extend(artifact_errors(source, f"{cid}.source_manifest"))
        if isinstance(source, dict):
            if source.get("repository") != "grandchallenge/MATHSOLVE" or source.get("commit_sha") != EXPECTED_SOLVE_COMMIT:
                errors.append(f"{cid}: Solve commit drift")
            if source.get("path") != f"campaign_manifests/{cid}.json":
                errors.append(f"{cid}: manifest path drift")
            if source.get("digest") != EXPECTED_MANIFESTS[cid]:
                errors.append(f"{cid}: manifest identity drift")
        status = route.get("intake_status")
        packet = route.get("intake_packet")
        output = route.get("cert_output")
        if status not in ALL_STATES or status != EXPECTED_STATES[cid]:
            errors.append(f"{cid}: governed intake state drift")
        if status == "pending":
            if packet is not None or output is not None:
                errors.append(f"{cid}: pending route must not carry packet/output")
            if not route.get("blockers"):
                errors.append(f"{cid}: pending route requires blockers")
        elif status in {"ready","submitted"}:
            if packet is None:
                errors.append(f"{cid}: {status} route lacks intake packet")
            else:
                errors.extend(artifact_errors(packet, f"{cid}.intake_packet"))
                if packet.get("repository") != "grandchallenge/MATHSOLVE" or packet.get("commit_sha") != EXPECTED_SOLVE_COMMIT:
                    errors.append(f"{cid}: packet commit drift")
                if packet.get("path") != f"cert_handoffs/{cid}.json" or packet.get("digest") != EXPECTED_READY_PACKETS.get(cid):
                    errors.append(f"{cid}: packet identity drift")
            if output is not None:
                errors.append(f"{cid}: {status} is intake-only and must not carry Cert output")
        elif status in ADJUDICATED_STATES:
            if packet is None:
                errors.append(f"{cid}: adjudication lacks intake packet")
            if output is None:
                errors.append(f"{cid}: adjudication lacks MATHCERT output")
        claims = route.get("target_claim_ids")
        if not isinstance(claims, list) or len(claims) != len(set(claims)):
            errors.append(f"{cid}: target_claim_ids must be unique")
            claims = []
        for claim in claims:
            if claim in seen_claims:
                errors.append(f"duplicate target claim {claim}; first registered by {seen_claims[claim]}")
            seen_claims[claim] = cid
        if status in POSITIVE_STATES and not claims:
            errors.append(f"{cid}: positive disposition lacks target claims")
        if not str(route.get("claim_boundary", "")).strip():
            errors.append(f"{cid}: empty claim boundary")
    return errors


def main() -> int:
    errors = route_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("validated eight exact Solve manifests, three ready intake packets, five pending routes, and zero MATHCERT adjudications")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())