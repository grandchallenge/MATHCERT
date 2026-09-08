#!/usr/bin/env python3
"""Validate the bounded HC-WP00 semantic and conditional qualification."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
CERT = ROOT / "certificates/hodge/MC-HC-WP00-QUAL-001.json"
SCHEMA = ROOT / "schemas/hc_wp00_qualification.schema.json"
CLAIM_SCHEMA = ROOT / "schemas/hc_claim_record.schema.json"
ROUTES = ROOT / "governance/certification_routes.json"
CERT_COMMIT = "fdc33903593b6bc4a021ad7158f3533f50da8705"
CERT_BLOB = "38830b24464f148a53f0a0a3e47e97d307fadf23"
RECORD_COMMIT = "599230f994d7cf98c448fb99b185a802e336269f"
RECORDS = {
    "HC-C001": ("c6bf64e8d2b716be54ef86798e120b2a67c64ad6", "qualified_statement_identity"),
    "HC-C002": ("e16e64f0168d06ae508e5ae0956942a6b68211b3", "qualified_definition_level_equivalence"),
    "HC-C003": ("ce3f3885ac7bbcb09ac5777653c4ebbccc2a4cb8", "qualified_conditional_low_dimension_reduction"),
}
MUTATIONS = {
    "coefficient_Q_to_Z",
    "rational_Hodge_class_to_arbitrary_complex_pp_class",
    "smooth_projective_to_compact_Kahler",
    "Chow_cycle_to_motivated_or_topological_object",
    "rational_generation_to_effective_irreducible_representative",
    "universal_to_sampled_or_very_general_quantifier",
    "algebraic_to_Hodge_implication_reversed_as_definition",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload,
        usedforsecurity=False,
    ).hexdigest()


def errors(root: Path = ROOT) -> list[str]:
    paths = {
        "cert": root / CERT.relative_to(ROOT),
        "schema": root / SCHEMA.relative_to(ROOT),
        "claim_schema": root / CLAIM_SCHEMA.relative_to(ROOT),
        "routes": root / ROUTES.relative_to(ROOT),
    }
    try:
        cert = load(paths["cert"])
        schema = load(paths["schema"])
        claim_schema = load(paths["claim_schema"])
        routes = load(paths["routes"])
    except (OSError, json.JSONDecodeError) as exc:
        return [f"HC qualification load failed: {exc}"]

    found: list[str] = []
    try:
        jsonschema.validate(cert, schema)
    except jsonschema.ValidationError as exc:
        found.append(f"HC qualification schema failure: {exc.message}")
    if schema.get("$id") != "https://grandchallenge.ai/schemas/hc_wp00_qualification.schema.json":
        found.append("HC qualification schema identity drift")
    if schema.get("additionalProperties") is not False:
        found.append("HC qualification schema must remain closed")
    if git_blob(paths["schema"]) != "b835b1255d90a21650cda5ae5e6e57a391847331":
        found.append("HC qualification schema blob drift")
    if git_blob(paths["cert"]) != CERT_BLOB:
        found.append("HC qualification certificate blob drift")

    if (cert.get("certificate_id"), cert.get("campaign_id"), cert.get("route_id")) != (
        "MC-HC-WP00-QUAL-001", "HC-001", "MC-ROUTE-HC-001"
    ):
        found.append("HC qualification identity drift")

    provider = cert.get("solve_provider", {})
    expected_provider = {
        "manifest": ("916f3434abcce29098ba7508a3b457a461461193", "campaign_manifests/HC-001.json", "48e3a0c22299147fe48cb4288cda813d7cffdcb4"),
        "handoff": ("916f3434abcce29098ba7508a3b457a461461193", "cert_handoffs/HC-001.json", "0c154af2e577e4367f9f5d0aeac5e15f9420172c"),
        "work_package": ("8c56729cb8a747296f2be5eeab93d2cde999e4bc", "work_packages/HC_WP00.md", "195d2a281f75493f5db1a81f2270e16aeead259d"),
        "claim_ledger": ("16edb1df66d1e1835754ec1e7a1faa93231675b9", "campaign_ledgers/HC-001/claim_ledger.json", "ed0216ea6dd1859effe926b8c501d8dc156e897a"),
        "proof_obligations": ("e067c1b0f9eeb8a08b12a9fd9f6281e792a19e2b", "campaign_ledgers/HC-001/proof_obligation_dag.json", "99394c33bf91fe433713fffb1f48c01e08237f6b"),
    }
    if provider.get("repository") != "grandchallenge/MATHSOLVE" or provider.get("merge_commit") != "916f3434abcce29098ba7508a3b457a461461193":
        found.append("HC Solve provider identity drift")
    for key, expected in expected_provider.items():
        item = provider.get(key, {})
        actual = (item.get("commit_sha"), item.get("path"), item.get("digest"))
        if item.get("repository") != "grandchallenge/MATHSOLVE" or actual != expected:
            found.append(f"HC Solve {key} authority drift")

    refs = {Path(item.get("path", "")).stem: item for item in cert.get("claim_records", []) if isinstance(item, dict)}
    if set(refs) != set(RECORDS):
        found.append("HC claim-record set drift")
    records: dict[str, dict[str, Any]] = {}
    for claim_id, (digest, _) in RECORDS.items():
        relative = Path(f"certificates/hodge/claim_records/{claim_id}.json")
        path = root / relative
        try:
            record = load(path)
            jsonschema.validate(record, claim_schema)
            records[claim_id] = record
        except (OSError, json.JSONDecodeError, jsonschema.ValidationError) as exc:
            found.append(f"{claim_id}: claim record invalid: {exc}")
            continue
        if git_blob(path) != digest:
            found.append(f"{claim_id}: claim record blob drift")
        ref = refs.get(claim_id, {})
        if (ref.get("repository"), ref.get("commit_sha"), ref.get("path"), ref.get("digest")) != (
            "grandchallenge/MATHCERT", RECORD_COMMIT, relative.as_posix(), digest
        ):
            found.append(f"{claim_id}: claim record authority drift")

    common = {
        "base_field": "C", "geometric_category": "smooth_projective_variety",
        "smoothness": "smooth", "properness_profile": "projective", "coefficient_ring": "Q",
    }
    for claim_id, record in records.items():
        for key, value in common.items():
            if record.get(key) != value:
                found.append(f"{claim_id}: semantic {key} drift")
    if records.get("HC-C001", {}).get("quantifier_scope") != "every_variety_every_class":
        found.append("HC-C001: universal quantifier drift")
    if records.get("HC-C001", {}).get("input_class_predicate") != "alpha is rational and its complexification has Hodge type (p,p)":
        found.append("HC-C001: rationality predicate drift")
    if records.get("HC-C002", {}).get("implication_direction") != "equivalence":
        found.append("HC-C002: equivalence direction drift")
    if "effectivity" not in records.get("HC-C002", {}).get("claims_not_made", []):
        found.append("HC-C002: effectivity boundary removed")
    if records.get("HC-C003", {}).get("dimension_scope") != "dim X <= 3" or records.get("HC-C003", {}).get("status") != "CONDITIONAL":
        found.append("HC-C003: conditional dimension boundary drift")

    claims = {item.get("claim_id"): item for item in cert.get("adjudicated_claims", []) if isinstance(item, dict)}
    if set(claims) != set(RECORDS):
        found.append("HC adjudicated claim set drift")
    for claim_id, (_, disposition) in RECORDS.items():
        item = claims.get(claim_id, {})
        if item.get("modality") != "SEMANTIC_REPLAY" or item.get("disposition") != disposition or item.get("kernel_checked") is not False:
            found.append(f"{claim_id}: bounded disposition drift")

    sources = {item.get("source_id"): item for item in cert.get("external_sources", []) if isinstance(item, dict)}
    if set(sources) != {"CLAY-DELIGNE-HODGE", "CLAY-HODGE-STATUS"}:
        found.append("HC independent source set drift")
    if sources.get("CLAY-DELIGNE-HODGE", {}).get("url") != "https://www.claymath.org/wp-content/uploads/2022/06/hodge.pdf":
        found.append("HC official statement source drift")
    if sources.get("CLAY-HODGE-STATUS", {}).get("url") != "https://www.claymath.org/millennium/hodge-conjecture/":
        found.append("HC official status source drift")

    replay = cert.get("replay", {})
    if set(replay.get("semantic_mutations_rejected", [])) != MUTATIONS:
        found.append("HC semantic mutation coverage drift")
    if replay.get("lean_formalization_available") is not False or replay.get("kernel_checked_claims") != []:
        found.append("HC formalization boundary inflated")
    for key in ("mathematical_target_proved", "full_hodge_conjecture_proved", "restricted_target_selected"):
        if cert.get(key) is not False:
            found.append(f"HC {key} must remain false")
    if cert.get("disposition") != "qualified_semantic_and_conditional_interface_only":
        found.append("HC disposition inflation")
    unresolved = " ".join(cert.get("unresolved_obligations", []))
    for token in ("universal", "dimension-four", "restricted", "formalization", "specialist"):
        if token not in unresolved:
            found.append(f"HC unresolved obligations missing token: {token}")
    boundary = str(cert.get("claim_boundary", ""))
    for token in ("does not prove the Hodge conjecture", "Lean/kernel proof", "claim-promotion"):
        if token not in boundary:
            found.append(f"HC claim boundary missing token: {token}")

    route = next((item for item in routes.get("routes", []) if item.get("campaign_id") == "HC-001"), {})
    if route.get("intake_status") != "qualified" or route.get("target_claim_ids") != ["HC-C001", "HC-C002", "HC-C003"]:
        found.append("HC route state or target set drift")
    output = route.get("cert_output", {})
    if (output.get("repository"), output.get("commit_sha"), output.get("path"), output.get("digest")) != (
        "grandchallenge/MATHCERT", CERT_COMMIT, "certificates/hodge/MC-HC-WP00-QUAL-001.json", CERT_BLOB
    ):
        found.append("HC route output identity drift")
    blockers = " ".join(route.get("blockers", []))
    for token in ("full Hodge", "dimension-four", "restricted target", "specialist"):
        if token not in blockers:
            found.append(f"HC route blockers missing token: {token}")
    return found


def main() -> int:
    found = errors()
    if found:
        print("\n".join(found), file=sys.stderr)
        print(f"HC-WP00 qualification failed with {len(found)} error(s)", file=sys.stderr)
        return 1
    print("validated HC-WP00 statement identity and conditional dimension-at-most-three interface without certifying the Hodge conjecture")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
