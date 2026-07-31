#!/usr/bin/env python3
"""Validate restricted RH and NS-CI target-interface certificates."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CERT_DIR = ROOT / "certificates" / "formal_sources"
SCHEMA_PATH = ROOT / "schemas" / "formal_target_certificate.schema.json"
REGISTRY_PATH = ROOT / "governance" / "certification_routes.json"
SOLVE_COMMIT = "916f3434abcce29098ba7508a3b457a461461193"
MATHLIB_COMMIT = "5e932f97dd25535344f80f9dd8da3aab83df0fe6"
REPLAY_COMMIT = "89371038b5d3fe526387a9767a48ac5bd6e527b1"
REPLAY_BLOB = "c807eaa8a79c470d52b2d06223b539fe8f79787d"
EXPECTED_FILES = {
    "RH-001": "MC-FC-WP00-RH-001.json",
    "NS-CI-001": "MC-FC-WP00-NS-CI-001.json",
}
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
}
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
) -> list[str]:
    schema = load_json(schema_path)
    found: list[str] = []
    if schema.get("$id") != "https://grandchallenge.ai/schemas/formal_target_certificate.schema.json":
        found.append("formal target certificate schema identity drift")
    paths = sorted(directory.glob("*.json"))
    actual = {path.name for path in paths}
    expected = set(EXPECTED_FILES.values())
    for missing in sorted(expected - actual):
        found.append(f"missing formal target certificate: {missing}")
    for unknown in sorted(actual - expected):
        found.append(f"unregistered formal target certificate: {unknown}")
    for path in paths:
        data = load_json(path)
        if set(data) != EXPECTED_TOP_KEYS:
            found.append(f"{path}: certificate fields drift")
        campaign = str(data.get("campaign_id", ""))
        if EXPECTED_FILES.get(campaign) != path.name:
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
        domain_axioms = set(axiom_report.get("imported_domain_axioms", []))
        if domain_axioms != EXPECTED_DOMAIN_AXIOMS.get(campaign):
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
    for campaign, filename in EXPECTED_FILES.items():
        route = route_map.get(campaign, {})
        if route.get("intake_status") != "qualified":
            found.append(f"{campaign}: route is not qualified")
        output = route.get("cert_output", {})
        expected_path = f"certificates/formal_sources/{filename}"
        if output.get("path") != expected_path or output.get("digest") != EXPECTED_OUTPUT_BLOBS[campaign]:
            found.append(f"{campaign}: route output identity drift")
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
    print("validated RH and NS-CI restricted interface qualifications, exact provider and replay identities, axiom boundaries, and unproved-target invariants")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
