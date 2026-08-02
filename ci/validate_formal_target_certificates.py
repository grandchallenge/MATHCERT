#!/usr/bin/env python3
"""Validate restricted formal-source qualification certificates."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
CERT_DIR = ROOT / "certificates" / "formal_sources"
SCHEMA_PATH = ROOT / "schemas" / "formal_target_certificate.schema.json"
EHRHART_SCHEMA_PATH = ROOT / "schemas" / "otp_ehrhart_qualified_output.schema.json"
REGISTRY_PATH = ROOT / "governance" / "certification_routes.json"
SOLVE_COMMIT = "916f3434abcce29098ba7508a3b457a461461193"
MATHLIB_COMMIT = "5e932f97dd25535344f80f9dd8da3aab83df0fe6"
REPLAY_COMMIT = "89371038b5d3fe526387a9767a48ac5bd6e527b1"
REPLAY_BLOB = "c807eaa8a79c470d52b2d06223b539fe8f79787d"
LEGACY_FILES = {
    "RH-001": "MC-FC-WP00-RH-001.json",
    "NS-CI-001": "MC-FC-WP00-NS-CI-001.json",
}
EHRHART_FILE = "MC-OTP-F-EHRHART-001.json"
EXPECTED_FILES = set(LEGACY_FILES.values()) | {EHRHART_FILE}
EXPECTED_DOMAIN_AXIOMS = {
    "RH-001": set(),
    "NS-CI-001": {
        "MathSolve.FormalConjectures.NS.IsUnforcedLerayHopfSolution",
        "MathSolve.FormalConjectures.NS.MixedNormFiniteOnZeroT",
        "MathSolve.FormalConjectures.NS.PositiveClayWholeSpaceAlternative",
    },
}
EXPECTED_CONCORDANCE = {"RH-001": True, "NS-CI-001": False}
EXPECTED_OUTPUT_BLOBS = {
    "RH-001": "3668bbf792d994a6d8919101417f2f3cad342cdc",
    "NS-CI-001": "6047ad774957974a6c2aa86bae72b51841e774a4",
    "OTP-F-EHRHART": "27a855c949b67e71372c7f0d6601d80125d33968",
}
EXPECTED_EHRHART_TARGETS = [
    "Ehrhart.Volume.ehrhart_volume_inequality_for_sets",
    "Ehrhart.SimplexVolume.exists_centeredBody_sharp",
    "Ehrhart.SimplexVolume.barycenter_centeredSimplex",
    "Ehrhart.SimplexVolume.normalizedVolume_centeredSimplex",
]
EXPECTED_TOP_KEYS = {
    "schema_version", "certificate_id", "campaign_id", "solve_provider",
    "cert_replay", "source_identity_verified", "extraction_replayed",
    "target_declaration_elaborated", "concordance_theorem_kernel_checked",
    "axiom_report", "sorry_inventory", "mathematical_target_proved",
    "disposition", "claim_boundary",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload,
        usedforsecurity=False,
    ).hexdigest()


def certificate_errors(
    directory: Path = CERT_DIR,
    schema_path: Path = SCHEMA_PATH,
    registry_path: Path = REGISTRY_PATH,
    root: Path = ROOT,
    ehrhart_schema_path: Path = EHRHART_SCHEMA_PATH,
) -> list[str]:
    schema = load_json(schema_path)
    ehrhart_schema = load_json(ehrhart_schema_path)
    found: list[str] = []
    if schema.get("$id") != "https://grandchallenge.ai/schemas/formal_target_certificate.schema.json":
        found.append("formal target certificate schema identity drift")
    if ehrhart_schema.get("$id") != "https://grandchallenge.ai/schemas/otp_ehrhart_qualified_output.schema.json":
        found.append("Ehrhart qualification schema identity drift")
    if ehrhart_schema.get("additionalProperties") is not False:
        found.append("Ehrhart qualification schema must remain closed")
    paths = sorted(directory.glob("*.json"))
    actual = {path.name for path in paths}
    for missing in sorted(EXPECTED_FILES - actual):
        found.append(f"missing formal target certificate: {missing}")
    for unknown in sorted(actual - EXPECTED_FILES):
        found.append(f"unregistered formal target certificate: {unknown}")

    for path in paths:
        data = load_json(path)
        if path.name == EHRHART_FILE:
            for error in Draft202012Validator(ehrhart_schema).iter_errors(data):
                found.append(f"{path}: Ehrhart schema violation: {error.message}")
            if data.get("certificate_id") != "MC-OTP-F-EHRHART-QUAL-001":
                found.append(f"{path}: certificate identity drift")
            if data.get("result_family") != "OTP-F-EHRHART" or data.get("route_id") != "MC-ROUTE-OTP-F-EHRHART":
                found.append(f"{path}: family/route identity drift")
            if data.get("encoded_targets") != EXPECTED_EHRHART_TARGETS:
                found.append(f"{path}: encoded target scope drift")
            qualification = data.get("qualification", {})
            if qualification.get("disposition") != "qualified_encoded_targets_only":
                found.append(f"{path}: disposition inflation")
            if qualification.get("source_theorem_mathematically_proved") is not False:
                found.append(f"{path}: mathematical target must remain unproved")
            if qualification.get("equality_case_classification") != "excluded":
                found.append(f"{path}: equality-case inflation")
            if data.get("axiom_report") != {
                "kernel_axioms": ["Classical.choice", "Quot.sound", "propext"],
                "imported_domain_axioms": [],
                "unexpected_axioms": [],
            }:
                found.append(f"{path}: axiom boundary drift")
            if data.get("trust_boundary") != {
                "solution_placeholder_count": 0,
                "unsafe_declaration_count": 0,
                "custom_axiom_count": 0,
            }:
                found.append(f"{path}: trust-boundary drift")
            if data.get("state") != {
                "route_state": "qualified",
                "cert_output_inserted": True,
                "mathematical_target_proved": False,
                "may_promote_claim": False,
                "aggregate_output": False,
            }:
                found.append(f"{path}: state inflation")
            if git_blob_sha1(path) != EXPECTED_OUTPUT_BLOBS["OTP-F-EHRHART"]:
                found.append(f"{path}: certificate blob identity drift")
            continue

        if set(data) != EXPECTED_TOP_KEYS:
            found.append(f"{path}: certificate fields drift")
        campaign = str(data.get("campaign_id", ""))
        if LEGACY_FILES.get(campaign) != path.name:
            found.append(f"{path}: campaign/file identity drift")
        if data.get("schema_version") != "1.0.0" or data.get("certificate_id") != f"MC-FC-WP00-{campaign}":
            found.append(f"{path}: certificate identity drift")
        provider = data.get("solve_provider", {})
        if provider.get("repository") != "grandchallenge/MATHSOLVE" or provider.get("merge_commit") != SOLVE_COMMIT:
            found.append(f"{path}: MATHSOLVE merge drift")
        replay = data.get("cert_replay", {})
        if replay.get("source_commit") != REPLAY_COMMIT or replay.get("module_blob") != REPLAY_BLOB:
            found.append(f"{path}: Cert replay identity drift")
        if replay.get("mathlib_commit") != MATHLIB_COMMIT or replay.get("lean_toolchain") != "leanprover/lean4:v4.29.1":
            found.append(f"{path}: target toolchain drift")
        for flag in ("source_identity_verified", "extraction_replayed", "target_declaration_elaborated"):
            if data.get(flag) is not True:
                found.append(f"{path}: {flag} must be true")
        if data.get("concordance_theorem_kernel_checked") is not EXPECTED_CONCORDANCE.get(campaign):
            found.append(f"{path}: concordance disposition drift")
        axiom_report = data.get("axiom_report", {})
        if set(axiom_report.get("kernel_axioms", [])) != {"Classical.choice", "Quot.sound", "propext"}:
            found.append(f"{path}: kernel axiom set drift")
        if set(axiom_report.get("imported_domain_axioms", [])) != EXPECTED_DOMAIN_AXIOMS.get(campaign):
            found.append(f"{path}: imported domain axiom set drift")
        if axiom_report.get("unexpected_axioms"):
            found.append(f"{path}: unexpected axiom admitted")
        if data.get("mathematical_target_proved") is not False:
            found.append(f"{path}: mathematical target must remain unproved")
        if data.get("disposition") != "qualified_interface_only":
            found.append(f"{path}: disposition inflation")
        if data.get("sorry_inventory") != {"sorry_count": 0, "admit_count": 0}:
            found.append(f"{path}: proof-placeholder inventory drift")
        if not str(data.get("claim_boundary", "")).strip():
            found.append(f"{path}: empty claim boundary")
        if git_blob_sha1(path) != EXPECTED_OUTPUT_BLOBS.get(campaign):
            found.append(f"{path}: certificate blob identity drift")

    registry = load_json(registry_path)
    route_map = {route.get("campaign_id"): route for route in registry.get("routes", [])}
    route_files = dict(LEGACY_FILES)
    route_files["OTP-F-EHRHART"] = EHRHART_FILE
    for campaign, filename in route_files.items():
        route = route_map.get(campaign, {})
        if route.get("intake_status") != "qualified":
            found.append(f"{campaign}: route is not qualified")
        output = route.get("cert_output", {})
        expected_path = f"certificates/formal_sources/{filename}"
        if output.get("path") != expected_path or output.get("digest") != EXPECTED_OUTPUT_BLOBS[campaign]:
            found.append(f"{campaign}: route output identity drift")
    if route_map.get("OTP-F-EHRHART", {}).get("cert_output", {}).get("commit_sha") != "7b79b459422951cc6e36feda34c8a6e3d615ef17":
        found.append("OTP-F-EHRHART: certificate-content commit pointer drift")

    replay_path = root / "MathCert/FormalSources/RHNSReplay.lean"
    replay_text = replay_path.read_text(encoding="utf-8") if replay_path.exists() else ""
    for token in (
        "theorem targetConcordance",
        "theorem targetInterface",
        "theorem bridgeInterface",
        "#print axioms RH.targetConcordance",
        "#print axioms NS.targetInterface",
        "#print axioms NS.bridgeInterface",
    ):
        if token not in replay_text:
            found.append(f"Cert replay missing token: {token}")
    if re.search(r"\b(sorry|admit)\b", replay_text):
        found.append("Cert replay contains a proof placeholder")
    if "PositiveClayWholeSpaceAlternative →\n        MathSolve.FormalConjectures.NS.UniversalCriticalIntegrability" in replay_text:
        found.append("Cert replay contains a reverse Clay implication")
    lakefile = (root / "lakefile.lean").read_text(encoding="utf-8")
    manifest = (root / "lake-manifest.json").read_text(encoding="utf-8")
    for token, label in ((SOLVE_COMMIT, "MATHSOLVE"), (MATHLIB_COMMIT, "mathlib")):
        if token not in lakefile or token not in manifest:
            found.append(f"{label} lock missing from Lake files")
    return found


def main() -> int:
    found = certificate_errors()
    if found:
        print("\n".join(found), file=sys.stderr)
        print(f"formal target certificate validation failed with {len(found)} error(s)", file=sys.stderr)
        return 1
    print("validated RH, NS-CI, and OTP-F-EHRHART restricted qualifications with exact output identities and unproved-target invariants")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
