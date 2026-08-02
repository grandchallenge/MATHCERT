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


def artifact(repository: str, commit: str, path: str, digest: str) -> dict[str, str]:
    return {
        "repository": repository,
        "commit_sha": commit,
        "path": path,
        "digest_algorithm": "git_blob_sha1",
        "digest": digest,
    }


SOLVE = "916f3434abcce29098ba7508a3b457a461461193"
EXPECTED: dict[str, dict[str, Any]] = {
    "UC-001": {
        "tracker": "https://github.com/grandchallenge/MATHCERT/issues/25",
        "source": artifact("grandchallenge/MATHSOLVE", SOLVE, "campaign_manifests/UC-001.json", "55629c3004b8bffc35fc0fa6f5fbc711ff48aa3c"),
        "state": "qualified",
        "packet": artifact("grandchallenge/MATHSOLVE", SOLVE, "cert_handoffs/UC-001.json", "8369bc21e45be6af71d2a0cdb0c5ab3cb5313bfb"),
        "output": artifact("grandchallenge/MATHCERT", "214c4f4d7962883bb10172db84d5162dde2e5c4e", "certificates/union_closed/MC-UC-WP04-QUAL-001.json", "265c185d6b2b2970dc675729efa3fc4860f29204"),
    },
    "NS-CI-001": {
        "tracker": "https://github.com/grandchallenge/MATHCERT/issues/19",
        "source": artifact("grandchallenge/MATHSOLVE", SOLVE, "campaign_manifests/NS-CI-001.json", "fcdd10f96b19c218ba700deb452b7da7f6b9b975"),
        "state": "qualified",
        "packet": artifact("grandchallenge/MATHSOLVE", SOLVE, "cert_handoffs/NS-CI-001.json", "40cad99646829fe40edf9c616074514407e49dee"),
        "output": artifact("grandchallenge/MATHCERT", "b1aa08001eb8537be8e204c3866aefd5f898252e", "certificates/formal_sources/MC-FC-WP00-NS-CI-001.json", "6047ad774957974a6c2aa86bae72b51841e774a4"),
    },
    "HC-001": {
        "tracker": "https://github.com/grandchallenge/MATHCERT/issues/23",
        "source": artifact("grandchallenge/MATHSOLVE", SOLVE, "campaign_manifests/HC-001.json", "48e3a0c22299147fe48cb4288cda813d7cffdcb4"),
        "state": "ready",
        "packet": artifact("grandchallenge/MATHSOLVE", SOLVE, "cert_handoffs/HC-001.json", "0c154af2e577e4367f9f5d0aeac5e15f9420172c"),
        "output": None,
    },
    "BSD-001": {
        "tracker": "https://github.com/grandchallenge/MATHCERT/issues/26",
        "source": artifact("grandchallenge/MATHSOLVE", SOLVE, "campaign_manifests/BSD-001.json", "3fb3b07400915d90047a06a353537cf2e1593b9e"),
        "state": "pending",
        "packet": None,
        "output": None,
    },
    "PNP-001": {
        "tracker": "https://github.com/grandchallenge/MATHCERT/issues/27",
        "source": artifact("grandchallenge/MATHSOLVE", SOLVE, "campaign_manifests/PNP-001.json", "6ecdfa0714828518878ccaf2cdc65756a5955186"),
        "state": "pending",
        "packet": None,
        "output": None,
    },
    "RH-001": {
        "tracker": "https://github.com/grandchallenge/MATHCERT/issues/28",
        "source": artifact("grandchallenge/MATHSOLVE", SOLVE, "campaign_manifests/RH-001.json", "4ce2c5bcdc7bc1d0d63f7b2244898c8a651d5f64"),
        "state": "qualified",
        "packet": artifact("grandchallenge/MATHSOLVE", SOLVE, "cert_handoffs/RH-001.json", "7304f185bd817bb67b77540513dc01d05f6fcd3a"),
        "output": artifact("grandchallenge/MATHCERT", "b1aa08001eb8537be8e204c3866aefd5f898252e", "certificates/formal_sources/MC-FC-WP00-RH-001.json", "3668bbf792d994a6d8919101417f2f3cad342cdc"),
    },
    "YM-001": {
        "tracker": "https://github.com/grandchallenge/MATHCERT/issues/29",
        "source": artifact("grandchallenge/MATHSOLVE", SOLVE, "campaign_manifests/YM-001.json", "733d11811d0226fa2b2467965c3655a7d0fad963"),
        "state": "pending",
        "packet": None,
        "output": None,
    },
    "OZ-001": {
        "tracker": "https://github.com/grandchallenge/MATHCERT/issues/30",
        "source": artifact("grandchallenge/MATHSOLVE", SOLVE, "campaign_manifests/OZ-001.json", "8b3164ab88a35ec9fba69013b44056573e846bfe"),
        "state": "pending",
        "packet": None,
        "output": None,
    },
}

for family, digest in {
    "OTP-F-EHRHART": "4653985d4980113514266c3c421804437bacb019",
    "OTP-J1-COMPACTNESS": "2d9c6e555a03b71eb33c476321e7f2d311ed168f",
    "OTP-J2-TWO-DEGENERATE": "0d226492bf13e13bc1a437be01104db3d4c96f79",
}.items():
    EXPECTED[family] = {
        "tracker": "https://github.com/grandchallenge/MATHCERT/issues/55",
        "source": artifact("grandchallenge/MATHFORGE", "0ea98866de3066e6a44ea1ca2cf93ade8a9e1c15", "provider_manifests/OPENAI-TEN-PROOFS-001.json", "fe1dab478e4ef9d6ddfe1b94a289fe7b51f58472"),
        "state": "submitted",
        "packet": artifact("grandchallenge/MATHSOLVE", "443daf537dc7e4ee34ab43aeb01508d9177816ab", f"work_packages/OPENAI_TEN_PROOFS_WP00/result_family_handoffs/{family}.json", digest),
        "output": None,
    }

ADJUDICATED = {"certified", "qualified", "rejected", "proof_debt"}
INTAKE_ONLY = {"ready", "submitted"}
ALL_STATES = {"pending"} | INTAKE_ONLY | ADJUDICATED
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
ARTIFACT_KEYS = {"repository", "commit_sha", "path", "digest_algorithm", "digest"}
ROUTE_KEYS = {
    "route_id", "campaign_id", "tracker_issue", "source_manifest",
    "intake_status", "intake_packet", "target_claim_ids",
    "requested_modalities", "claim_boundary", "cert_output", "blockers",
    "reopening_conditions",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def artifact_errors(value: Any, label: str) -> list[str]:
    found: list[str] = []
    if not isinstance(value, dict):
        return [f"{label}: expected an artifact object"]
    if set(value) != ARTIFACT_KEYS:
        found.append(f"{label}: artifact fields drift")
    commit = str(value.get("commit_sha", ""))
    digest = str(value.get("digest", ""))
    algorithm = value.get("digest_algorithm")
    if "/" not in str(value.get("repository", "")):
        found.append(f"{label}: repository must use owner/name form")
    if not HEX40.fullmatch(commit):
        found.append(f"{label}: invalid commit_sha")
    if not str(value.get("path", "")).strip():
        found.append(f"{label}: empty path")
    if algorithm in {"git_blob_sha1", "git_tree_sha1"} and not HEX40.fullmatch(digest):
        found.append(f"{label}: invalid Git digest")
    elif algorithm == "sha256" and not HEX64.fullmatch(digest):
        found.append(f"{label}: invalid SHA-256 digest")
    elif algorithm not in {"git_blob_sha1", "git_tree_sha1", "sha256"}:
        found.append(f"{label}: unsupported digest algorithm")
    if digest == commit:
        found.append(f"{label}: artifact digest must not be substituted with the repository commit")
    return found


def route_errors(
    registry_path: Path = REGISTRY_PATH,
    schema_path: Path = SCHEMA_PATH,
) -> list[str]:
    data = load_json(registry_path)
    schema = load_json(schema_path)
    found: list[str] = []
    if schema.get("additionalProperties") is not False:
        found.append("route schema must remain closed")
    if not isinstance(data, dict):
        return ["registry must be an object"]
    if data.get("schema_version") != "1.0.0" or data.get("registry_id") != "MC-CERTIFICATION-ROUTES":
        found.append("registry identity drift")
    if data.get("provider_repository") != "grandchallenge/MATHCERT":
        found.append("provider repository drift")
    if not HEX40.fullmatch(str(data.get("provider_base_commit", ""))):
        found.append("provider_base_commit must be a full SHA")
    routes = data.get("routes")
    if not isinstance(routes, list):
        return found + ["routes must be an array"]
    route_map = {route.get("campaign_id"): route for route in routes if isinstance(route, dict)}
    for campaign in sorted(set(EXPECTED) - set(route_map)):
        found.append(f"governed campaign is uncovered: {campaign}")
    for campaign in sorted(set(route_map) - set(EXPECTED)):
        found.append(f"unrecognized campaign: {campaign}")
    if len(route_map) != len(routes):
        found.append("campaign route uniqueness drift")

    claims: dict[str, str] = {}
    for campaign, expected in EXPECTED.items():
        route = route_map.get(campaign)
        if not isinstance(route, dict):
            continue
        if set(route) != ROUTE_KEYS:
            found.append(f"{campaign}: route fields drift")
        if route.get("route_id") != f"MC-ROUTE-{campaign}":
            found.append(f"{campaign}: route_id is not canonical")
        if route.get("tracker_issue") != expected["tracker"]:
            found.append(f"{campaign}: tracker drift")
        source = route.get("source_manifest")
        found.extend(artifact_errors(source, f"{campaign}.source_manifest"))
        if source != expected["source"]:
            found.append(f"{campaign}: manifest identity drift")
        state = route.get("intake_status")
        if state not in ALL_STATES or state != expected["state"]:
            found.append(f"{campaign}: governed intake state drift")
        packet = route.get("intake_packet")
        output = route.get("cert_output")
        if state == "pending":
            if packet is not None or output is not None:
                found.append(f"{campaign}: pending route must not carry packet/output")
        else:
            found.extend(artifact_errors(packet, f"{campaign}.intake_packet"))
            if packet != expected["packet"]:
                found.append(f"{campaign}: packet identity drift")
            if state in INTAKE_ONLY and output is not None:
                found.append(f"{campaign}: {state} is intake-only and must not carry Cert output")
            if state in ADJUDICATED:
                found.extend(artifact_errors(output, f"{campaign}.cert_output"))
                if output != expected["output"]:
                    found.append(f"{campaign}: output identity drift")
        identifiers = route.get("target_claim_ids")
        if not isinstance(identifiers, list) or not identifiers or len(identifiers) != len(set(identifiers)):
            found.append(f"{campaign}: target_claim_ids must be a unique nonempty list")
            identifiers = []
        for claim in identifiers:
            if claim in claims:
                found.append(f"duplicate target claim {claim}; first registered by {claims[claim]}")
            claims[claim] = campaign
        if not str(route.get("claim_boundary", "")).strip():
            found.append(f"{campaign}: empty claim boundary")
        if not isinstance(route.get("blockers"), list) or not route["blockers"]:
            found.append(f"{campaign}: blockers required")
        if not isinstance(route.get("reopening_conditions"), list) or not route["reopening_conditions"]:
            found.append(f"{campaign}: reopening conditions required")

    otp = {"OTP-F-EHRHART", "OTP-J1-COMPACTNESS", "OTP-J2-TWO-DEGENERATE"}
    if {campaign for campaign, route in route_map.items() if str(route.get("route_id", "")).startswith("MC-ROUTE-OTP-")} != otp:
        found.append("OTP route membership drift")
    if "OPENAI-TEN-PROOFS-001" in route_map:
        found.append("aggregate ten-proofs route prohibited")
    return found


def main() -> int:
    found = route_errors()
    if found:
        print("\n".join(found), file=sys.stderr)
        return 1
    print("validated eleven exact routes, including bounded UC qualification and three submitted OTP family routes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
