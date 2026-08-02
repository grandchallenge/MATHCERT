#!/usr/bin/env python3
"""Validate the exact bounded UC-001 restricted qualification."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CERT_PATH = ROOT / "certificates" / "union_closed" / "MC-UC-WP04-QUAL-001.json"
SCHEMA_PATH = ROOT / "schemas" / "uc_restricted_qualification.schema.json"
ROUTES_PATH = ROOT / "governance" / "certification_routes.json"
REPLAY_PATH = ROOT / "MathCert" / "FormalSources" / "UCRestrictedReplay.lean"

CERT_BLOB = "265c185d6b2b2970dc675729efa3fc4860f29204"
CERT_COMMIT = "214c4f4d7962883bb10172db84d5162dde2e5c4e"
CLAIMS = {
    "UC-WP02-L002": (
        "LEAN_FORMALIZATION",
        "qualified_restricted_theorem",
        "MathCert/Domains/UnionClosed/SingletonCase.lean",
        "76a707e7e05f6648a08dbe68a0e28b03361e4e0e",
    ),
    "UC-WP04-L001": (
        "LEAN_FORMALIZATION",
        "qualified_restricted_theorem",
        "MathCert/Domains/UnionClosed/TwoElementCase.lean",
        "3caf5a7f2c0a2399970ed260f49daa01b3eb2ca4",
    ),
    "UC-WP01-C004": (
        "EXACT_RATIONAL_CERTIFICATE",
        "qualified_finite_range_only",
        "certificates/exact/union_closed_n_le_4.json",
        "c8b5ea50021aeef647a7a6e5e25fba54aac1e050",
    ),
}
LOCAL_BASE_COMMIT = "4e5c02416a6dd66c52d9da87c5229ecf61673372"
SOLVE_COMMIT = "916f3434abcce29098ba7508a3b457a461461193"
TOP_KEYS = {
    "schema_version", "certificate_id", "campaign_id", "route_id",
    "solve_provider", "qualified_claims", "cert_replay", "axiom_report",
    "placeholder_inventory", "finite_range", "mathematical_target_proved",
    "disposition", "unresolved_obligations", "claim_boundary",
}
ARTIFACT_KEYS = {"repository", "commit_sha", "path", "digest_algorithm", "digest"}
HEX40 = re.compile(r"^[0-9a-f]{40}$")


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload,
        usedforsecurity=False,
    ).hexdigest()


def artifact_errors(value: Any, label: str) -> list[str]:
    found: list[str] = []
    if not isinstance(value, dict):
        return [f"{label}: expected artifact object"]
    if set(value) != ARTIFACT_KEYS:
        found.append(f"{label}: artifact fields drift")
    if value.get("digest_algorithm") != "git_blob_sha1":
        found.append(f"{label}: digest algorithm drift")
    if not HEX40.fullmatch(str(value.get("commit_sha", ""))):
        found.append(f"{label}: invalid commit identity")
    if not HEX40.fullmatch(str(value.get("digest", ""))):
        found.append(f"{label}: invalid blob identity")
    return found


def errors(root: Path = ROOT) -> list[str]:
    cert_path = root / CERT_PATH.relative_to(ROOT)
    schema_path = root / SCHEMA_PATH.relative_to(ROOT)
    routes_path = root / ROUTES_PATH.relative_to(ROOT)
    replay_path = root / REPLAY_PATH.relative_to(ROOT)
    try:
        cert = load(cert_path)
        schema = load(schema_path)
        routes = load(routes_path)
    except (OSError, json.JSONDecodeError) as exc:
        return [f"UC qualification load failed: {exc}"]

    found: list[str] = []
    if schema.get("$id") != "https://grandchallenge.ai/schemas/uc_restricted_qualification.schema.json":
        found.append("UC qualification schema identity drift")
    if schema.get("additionalProperties") is not False:
        found.append("UC qualification schema must remain closed")
    if set(cert) != TOP_KEYS:
        found.append("UC qualification fields drift")
    if cert.get("schema_version") != "1.0.0" or cert.get("certificate_id") != "MC-UC-WP04-QUAL-001":
        found.append("UC qualification identity drift")
    if cert.get("campaign_id") != "UC-001" or cert.get("route_id") != "MC-ROUTE-UC-001":
        found.append("UC campaign or route identity drift")
    if git_blob(cert_path) != CERT_BLOB:
        found.append("UC qualification certificate blob drift")

    provider = cert.get("solve_provider", {})
    if provider.get("repository") != "grandchallenge/MATHSOLVE" or provider.get("merge_commit") != SOLVE_COMMIT:
        found.append("UC Solve provider drift")
    expected_provider = {
        "manifest": (SOLVE_COMMIT, "campaign_manifests/UC-001.json", "55629c3004b8bffc35fc0fa6f5fbc711ff48aa3c"),
        "handoff": (SOLVE_COMMIT, "cert_handoffs/UC-001.json", "8369bc21e45be6af71d2a0cdb0c5ab3cb5313bfb"),
        "claim_ledger": ("2a0124051d67b4db63a75f5cc592a02b7553a2c2", "campaign_ledgers/UC-001/claim_ledger.json", "05c5b58f603a923fd6e66b44411ffd7c53559d55"),
        "proof_obligations": ("7d8ebdddc74b231b2405465259d0b799e6d8f3a0", "campaign_ledgers/UC-001/proof_obligation_dag.json", "5cc706c23636dadd83ab859246c412918c605f15"),
    }
    for name, (commit, path, digest) in expected_provider.items():
        item = provider.get(name)
        found.extend(artifact_errors(item, f"solve_provider.{name}"))
        if not isinstance(item, dict) or (
            item.get("repository"), item.get("commit_sha"), item.get("path"), item.get("digest")
        ) != ("grandchallenge/MATHSOLVE", commit, path, digest):
            found.append(f"solve_provider.{name}: exact authority drift")

    claims = cert.get("qualified_claims")
    if not isinstance(claims, list) or len(claims) != 3:
        found.append("UC qualification must contain exactly three claims")
        claims = []
    claim_map = {item.get("claim_id"): item for item in claims if isinstance(item, dict)}
    if set(claim_map) != set(CLAIMS):
        found.append("UC qualified claim set drift")
    if "UC-FRANKL" in claim_map:
        found.append("universal Frankl claim cannot be qualified")
    for claim_id, (modality, disposition, path, digest) in CLAIMS.items():
        item = claim_map.get(claim_id, {})
        if item.get("modality") != modality or item.get("disposition") != disposition:
            found.append(f"{claim_id}: modality or disposition drift")
        evidence = item.get("evidence")
        found.extend(artifact_errors(evidence, f"{claim_id}.evidence"))
        if not isinstance(evidence, dict) or (
            evidence.get("repository"), evidence.get("commit_sha"), evidence.get("path"), evidence.get("digest")
        ) != ("grandchallenge/MATHCERT", LOCAL_BASE_COMMIT, path, digest):
            found.append(f"{claim_id}: evidence identity drift")
        local = root / path
        if not local.is_file() or git_blob(local) != digest:
            found.append(f"{claim_id}: local evidence blob mismatch")

    replay = cert.get("cert_replay", {})
    if (
        replay.get("repository"), replay.get("source_commit"), replay.get("module"),
        replay.get("module_blob"), replay.get("lean_toolchain")
    ) != (
        "grandchallenge/MATHCERT", "bac9913978443dd38fb08901a641fcd99c38383f",
        "MathCert/FormalSources/UCRestrictedReplay.lean",
        "663c0100c7c78c1cf41cce0a2ef271aaa262e274",
        "leanprover/lean4:v4.29.1",
    ):
        found.append("UC Lean replay identity drift")
    if not replay_path.is_file() or git_blob(replay_path) != "663c0100c7c78c1cf41cce0a2ef271aaa262e274":
        found.append("UC Lean replay blob mismatch")
    replay_text = replay_path.read_text(encoding="utf-8") if replay_path.is_file() else ""
    for token in (
        "theorem singletonTarget", "theorem twoElementTarget",
        "#print axioms singletonTarget", "#print axioms twoElementTarget",
    ):
        if token not in replay_text:
            found.append(f"UC Lean replay missing token: {token}")
    if re.search(r"\b(sorry|admit)\b", replay_text):
        found.append("UC Lean replay contains a proof placeholder")

    exact_cert = replay.get("exact_certificate")
    exact_checker = replay.get("exact_replay_checker")
    for label, value, path, digest in (
        ("exact_certificate", exact_cert, "certificates/exact/union_closed_n_le_4.json", "c8b5ea50021aeef647a7a6e5e25fba54aac1e050"),
        ("exact_replay_checker", exact_checker, "ci/replay_certificates.py", "e54d45a64d3060e07db236c5c86469d904abd477"),
    ):
        found.extend(artifact_errors(value, f"cert_replay.{label}"))
        if not isinstance(value, dict) or (
            value.get("repository"), value.get("commit_sha"), value.get("path"), value.get("digest")
        ) != ("grandchallenge/MATHCERT", LOCAL_BASE_COMMIT, path, digest):
            found.append(f"cert_replay.{label}: exact identity drift")
        local = root / path
        if not local.is_file() or git_blob(local) != digest:
            found.append(f"cert_replay.{label}: local blob mismatch")

    exact_data = load(root / "certificates/exact/union_closed_n_le_4.json")
    results = exact_data.get("results", [])
    if [item.get("universe_size") for item in results] != [0, 1, 2, 3, 4]:
        found.append("UC finite certificate range drift")
    if any(item.get("frankl_violations") != 0 for item in results):
        found.append("UC finite certificate contains a violation")
    if cert.get("finite_range") != {"max_universe_size": 4, "frankl_violations": 0, "exact_replay": True}:
        found.append("UC finite qualification range inflation")

    if set(cert.get("axiom_report", {}).get("kernel_axioms", [])) != {"Classical.choice", "Quot.sound", "propext"}:
        found.append("UC kernel axiom boundary drift")
    if cert.get("axiom_report", {}).get("imported_domain_axioms") or cert.get("axiom_report", {}).get("unexpected_axioms"):
        found.append("UC qualification admits domain or unexpected axioms")
    if cert.get("placeholder_inventory") != {"sorry_count": 0, "admit_count": 0}:
        found.append("UC placeholder inventory drift")
    if cert.get("mathematical_target_proved") is not False:
        found.append("Frankl mathematical target must remain unproved")
    if cert.get("disposition") != "qualified_restricted_claims_only":
        found.append("UC qualification disposition inflation")
    if set(cert.get("unresolved_obligations", [])) != {"UC-P04", "UC-FRANKL"}:
        found.append("UC unresolved universal obligations drift")
    boundary = str(cert.get("claim_boundary", ""))
    for token in ("does not prove Frankl's conjecture", "universal bridge"):
        if token not in boundary:
            found.append(f"UC claim boundary missing token: {token}")

    route_map = {item.get("campaign_id"): item for item in routes.get("routes", [])}
    route = route_map.get("UC-001", {})
    if route.get("intake_status") != "qualified":
        found.append("UC route is not qualified")
    if route.get("target_claim_ids") != ["UC-WP02-L002", "UC-WP04-L001", "UC-WP01-C004"]:
        found.append("UC route target set drift")
    output = route.get("cert_output", {})
    if not isinstance(output, dict) or (
        output.get("repository"), output.get("commit_sha"), output.get("path"), output.get("digest")
    ) != (
        "grandchallenge/MATHCERT", CERT_COMMIT,
        "certificates/union_closed/MC-UC-WP04-QUAL-001.json", CERT_BLOB,
    ):
        found.append("UC route output identity drift")
    blockers = " ".join(route.get("blockers", []))
    for token in ("UC-FRANKL", "UC-P04", "n <= 4"):
        if token not in blockers:
            found.append(f"UC route blockers missing token: {token}")

    return found


def main() -> int:
    found = errors()
    if found:
        print("\n".join(found), file=sys.stderr)
        print(f"UC restricted qualification failed with {len(found)} error(s)", file=sys.stderr)
        return 1
    print("validated UC-001 restricted theorem and n <= 4 qualification while preserving Frankl and UC-P04 as open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
