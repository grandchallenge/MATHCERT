#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "governance" / "pre_route_candidates" / "OPENAI_TEN_PROOFS_WP06_ROUTE_REGISTRATIONS.json"
ROUTES = ROOT / "governance" / "certification_routes.json"
PROPOSAL_REG = ROOT / "governance" / "pre_route_candidates" / "OPENAI_TEN_PROOFS_WP05_ROUTE_PROPOSALS.json"
SCHEMA = ROOT / "schemas" / "openai_ten_proofs_route_registration_registry.schema.json"
TRANSITION = ROOT / "governance" / "result_family_output_candidates" / "staged_route_transitions" / "OTP-F-EHRHART.json"
CONTENT_COMMIT = "24d99cbdcd6da33ae2404c0f6034d503498d9a4b"
COMPACTNESS_CONTENT_COMMIT = "9fba5a8e918028ecc2b4d72abc00b3b72a5194f5"
COMPACTNESS_OUTPUT = {
    "repository": "grandchallenge/MATHCERT",
    "commit_sha": COMPACTNESS_CONTENT_COMMIT,
    "path": "certificates/formal_sources/MC-OTP-J1-COMPACTNESS-001.json",
    "digest_algorithm": "git_blob_sha1",
    "digest": "88531e28951854961e86eec0517356999a391759",
}
COMPACTNESS_HISTORICAL_BOUNDARY = "This registered route is limited to the exact corrected Compactness family targets and recorded current-revision theorem locus. It does not independently certify the explicit construction beyond the encoded targets, compare the proof body in full, adjudicate or prove the source theorem, issue a Cert output, or create an aggregate ten-proofs route."
COMPACTNESS_HISTORICAL_BLOCKERS = [
    "No MATHCERT adjudication has been authorized or recorded.",
    "The explicit construction is not independently certified beyond the encoded existential targets.",
    "Whole-document manuscript equivalence and full proof-body comparison remain unestablished.",
]
COMPACTNESS_HISTORICAL_REOPENING = [
    "Update this route only through a separately authorized, exact-head reviewed MATHCERT adjudication or authority-repin operation."
]
EXPECTED_FAMILIES = ["OTP-F-EHRHART", "OTP-J1-COMPACTNESS", "OTP-J2-TWO-DEGENERATE"]
EXPECTED_PROPOSALS = {
    "OTP-F-EHRHART": "7b069a003c84ef285259108076a55338fab0bc7f",
    "OTP-J1-COMPACTNESS": "2e541ca5882873ee1c756814642994361b10c78c",
    "OTP-J2-TWO-DEGENERATE": "0692ac15c19328532bdcd3e73b3c8c4371647ac6",
}
EXPECTED_ROUTE_BLOB = "b5541045591f8589130b1577c50d51d70c3b4337"
EXPECTED_PROPOSAL_REGISTRY_BLOB = "1883b29ec888ffc487c65b76b35cfcb122f47e51"
EXPECTED_BEFORE_BLOB = "5b3e8d48b9f6c5b03ed3dc439bf9e43876e017b1"
EXPECTED_PROPOSAL_MERGE = "e8d1e34509e640d82902ad0195560740b52bec0e"
EXPECTED_PACKET_DIGESTS = {
    "OTP-F-EHRHART": "4653985d4980113514266c3c421804437bacb019",
    "OTP-J1-COMPACTNESS": "2d9c6e555a03b71eb33c476321e7f2d311ed168f",
    "OTP-J2-TWO-DEGENERATE": "0d226492bf13e13bc1a437be01104db3d4c96f79",
}
EXPECTED_CLAIMS = {
    "OTP-F-EHRHART": [
        "Ehrhart.Volume.ehrhart_volume_inequality_for_sets",
        "Ehrhart.SimplexVolume.exists_centeredBody_sharp",
        "Ehrhart.SimplexVolume.barycenter_centeredSimplex",
        "Ehrhart.SimplexVolume.normalizedVolume_centeredSimplex",
    ],
    "OTP-J1-COMPACTNESS": [
        "CompactnessConjecture.quantitativeCompactnessCounterexample",
        "CompactnessConjecture.compactnessCounterexample_bigO",
        "CompactnessConjecture.not_erdos_180",
    ],
    "OTP-J2-TWO-DEGENERATE": [
        "TwoDegenerateGraphs.twoDegenerateExtremalCounterexample",
        "TwoDegenerateGraphs.not_erdos_146",
    ],
}
PROVIDER = {
    "repository": "grandchallenge/MATHFORGE",
    "commit_sha": "0ea98866de3066e6a44ea1ca2cf93ade8a9e1c15",
    "path": "provider_manifests/OPENAI-TEN-PROOFS-001.json",
    "digest_algorithm": "git_blob_sha1",
    "digest": "fe1dab478e4ef9d6ddfe1b94a289fe7b51f58472",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(data)}\0".encode() + data,
        usedforsecurity=False,
    ).hexdigest()


def closed_schema(value: Any) -> list[str]:
    errors: list[str] = []

    def walk(node: Any, path: str = "") -> None:
        if isinstance(node, dict):
            if node.get("type") == "object" and node.get("additionalProperties") is not False:
                errors.append(path or "/")
            for key, child in node.items():
                walk(child, path + "/" + key)
        elif isinstance(node, list):
            for index, child in enumerate(node):
                walk(child, path + f"/{index}")

    walk(value)
    return errors


def _compactness_successor_errors(routes: dict[str, Any]) -> list[str]:
    route = next(
        (
            row
            for row in routes.get("routes", [])
            if isinstance(row, dict) and row.get("campaign_id") == "OTP-J1-COMPACTNESS"
        ),
        None,
    )
    if route is None:
        return ["OTP-J1-COMPACTNESS: live route missing"]
    errors: list[str] = []
    if route.get("target_claim_ids") != EXPECTED_CLAIMS["OTP-J1-COMPACTNESS"]:
        errors.append("OTP-J1-COMPACTNESS: live successor target drift")
    status = route.get("intake_status")
    output = route.get("cert_output")
    if status == "submitted" and output is None:
        return errors
    if status != "qualified":
        errors.append("OTP-J1-COMPACTNESS: live successor route is not qualified")
    if output != COMPACTNESS_OUTPUT:
        errors.append("OTP-J1-COMPACTNESS: live successor output identity drift")
    boundary = str(route.get("claim_boundary", "")).lower()
    blockers = " ".join(route.get("blockers", [])).lower()
    for token in (
        "qualified_encoded_targets_only",
        "chapter 10",
        "historical",
        "whole-document",
        "aggregate openai ten proofs",
    ):
        if token not in boundary:
            errors.append(f"OTP-J1-COMPACTNESS: live successor boundary missing {token}")
    for token in (
        "unrestricted chapter 10",
        "historical or stronger",
        "whole-document byte and semantic equivalence",
        "proof body",
    ):
        if token not in blockers:
            errors.append(f"OTP-J1-COMPACTNESS: live successor blockers missing {token}")
    return errors


def registration_snapshot(routes: dict[str, Any]) -> dict[str, Any]:
    """Map later governed successors back to the protected three-route registration snapshot."""
    snapshot = copy.deepcopy(routes)
    transition = load(TRANSITION)
    expected_successor = copy.deepcopy(transition["after_template"])
    expected_successor["cert_output"]["commit_sha"] = CONTENT_COMMIT
    for index, route in enumerate(snapshot.get("routes", [])):
        if route.get("campaign_id") != "OTP-F-EHRHART":
            continue
        if route == expected_successor:
            snapshot["routes"][index] = copy.deepcopy(transition["before"])
        break

    for index, route in enumerate(snapshot.get("routes", [])):
        if not isinstance(route, dict) or route.get("campaign_id") != "OTP-J1-COMPACTNESS":
            continue
        if route.get("intake_status") == "qualified":
            historical = copy.deepcopy(route)
            historical["intake_status"] = "submitted"
            historical["cert_output"] = None
            historical["claim_boundary"] = COMPACTNESS_HISTORICAL_BOUNDARY
            historical["blockers"] = copy.deepcopy(COMPACTNESS_HISTORICAL_BLOCKERS)
            historical["reopening_conditions"] = copy.deepcopy(COMPACTNESS_HISTORICAL_REOPENING)
            snapshot["routes"][index] = historical
        break

    snapshot["routes"] = [
        route for route in snapshot.get("routes", [])
        if not (isinstance(route, dict) and route.get("campaign_id") == "OTP-C-PERMANENT")
    ]
    return snapshot


def validation_errors(
    receipt: Any = None,
    routes: Any = None,
    proposal_registry: Any = None,
    proposal_blobs: Any = None,
    routes_blob: Any = None,
    proposal_registry_blob: Any = None,
) -> list[str]:
    errors: list[str] = []
    receipt = load(REG) if receipt is None else receipt
    live_routes = load(ROUTES) if routes is None else routes
    errors.extend(_compactness_successor_errors(live_routes))
    routes = registration_snapshot(live_routes)
    proposal_registry = load(PROPOSAL_REG) if proposal_registry is None else proposal_registry
    proposal_blobs = (
        {
            family: blob(ROOT / f"governance/result_family_route_proposals/{family}.json")
            for family in EXPECTED_FAMILIES
        }
        if proposal_blobs is None
        else proposal_blobs
    )
    routes_blob = EXPECTED_ROUTE_BLOB if routes_blob is None else routes_blob
    proposal_registry_blob = blob(PROPOSAL_REG) if proposal_registry_blob is None else proposal_registry_blob

    if closed_schema(load(SCHEMA)):
        errors.append("registration schema contains open object")
    if not isinstance(receipt, dict):
        return ["registration receipt must be an object"]
    if set(receipt) != {
        "schema_version", "record_type", "record_id", "candidate_id",
        "tracker_issue", "authority", "state", "registrations",
        "preserved_limitations", "route_controls", "activation", "claim_boundary",
    }:
        errors.append("registration receipt fields drift")
    if (
        receipt.get("schema_version"), receipt.get("record_type"),
        receipt.get("record_id"), receipt.get("candidate_id"),
        receipt.get("tracker_issue"),
    ) != (
        "1.0.0", "openai_ten_proofs_route_registration_registry",
        "MC-OPENAI-TEN-PROOFS-WP06-ROUTE-REGISTRATIONS",
        "OPENAI-TEN-PROOFS-001",
        "https://github.com/grandchallenge/MATHCERT/issues/55",
    ):
        errors.append("registration receipt identity drift")

    authority = receipt.get("authority", {})
    if (
        authority.get("proposal_pr_head") != "7b27d49c63dd126e6a18b80b340c71276bd71c84"
        or authority.get("proposal_merge") != EXPECTED_PROPOSAL_MERGE
    ):
        errors.append("proposal merge authority drift")
    if authority.get("proposal_review") != {
        "reviewer": "jimsteeg",
        "state": "APPROVED",
        "submitted_at": "2026-08-02T04:16:37Z",
    }:
        errors.append("proposal review authority drift")
    expected_proposal_registry = {
        "repository": "grandchallenge/MATHCERT",
        "commit_sha": EXPECTED_PROPOSAL_MERGE,
        "path": "governance/pre_route_candidates/OPENAI_TEN_PROOFS_WP05_ROUTE_PROPOSALS.json",
        "digest_algorithm": "git_blob_sha1",
        "digest": EXPECTED_PROPOSAL_REGISTRY_BLOB,
    }
    if authority.get("proposal_registry") != expected_proposal_registry:
        errors.append("proposal registry authority drift")
    if authority.get("registered_route_registry_before_blob") != EXPECTED_BEFORE_BLOB:
        errors.append("prior route registry identity drift")
    if (
        authority.get("registered_route_registry_blob") != EXPECTED_ROUTE_BLOB
        or routes_blob != EXPECTED_ROUTE_BLOB
    ):
        errors.append("registered route registry blob drift")
    if proposal_registry_blob != EXPECTED_PROPOSAL_REGISTRY_BLOB:
        errors.append("proposal registry blob drift")
    if proposal_registry.get("state", {}).get("proposal_count") != 3:
        errors.append("proposal registry count drift")

    registrations = receipt.get("registrations")
    if not isinstance(registrations, list) or len(registrations) != 3:
        return errors + ["expected exactly three registrations"]
    by_family = {row.get("result_family"): row for row in registrations if isinstance(row, dict)}
    if set(by_family) != set(EXPECTED_FAMILIES):
        errors.append("registration family membership drift")
    route_map = {
        row.get("campaign_id"): row
        for row in routes.get("routes", [])
        if isinstance(row, dict)
    }
    otp_ids = {
        row.get("route_id")
        for campaign, row in route_map.items()
        if str(campaign).startswith("OTP-")
    }
    if otp_ids != {f"MC-ROUTE-{family}" for family in EXPECTED_FAMILIES}:
        errors.append("global OTP route membership drift")
    if "OPENAI-TEN-PROOFS-001" in route_map:
        errors.append("aggregate route inserted")

    for family in EXPECTED_FAMILIES:
        registration = by_family.get(family, {})
        route = route_map.get(family, {})
        route_id = f"MC-ROUTE-{family}"
        if registration.get("route_id") != route_id:
            errors.append(f"{family}: route identity drift")
        proposal = {
            "repository": "grandchallenge/MATHCERT",
            "commit_sha": EXPECTED_PROPOSAL_MERGE,
            "path": f"governance/result_family_route_proposals/{family}.json",
            "digest_algorithm": "git_blob_sha1",
            "digest": EXPECTED_PROPOSALS[family],
        }
        if registration.get("proposal") != proposal or proposal_blobs.get(family) != EXPECTED_PROPOSALS[family]:
            errors.append(f"{family}: proposal identity drift")
        packet = {
            "repository": "grandchallenge/MATHSOLVE",
            "commit_sha": "443daf537dc7e4ee34ab43aeb01508d9177816ab",
            "path": f"work_packages/OPENAI_TEN_PROOFS_WP00/result_family_handoffs/{family}.json",
            "digest_algorithm": "git_blob_sha1",
            "digest": EXPECTED_PACKET_DIGESTS[family],
        }
        if registration.get("source_manifest") != PROVIDER or registration.get("intake_packet") != packet:
            errors.append(f"{family}: source or packet authority drift")
        if registration.get("intake_status") != "submitted" or registration.get("target_claim_ids") != EXPECTED_CLAIMS[family]:
            errors.append(f"{family}: registration state or target drift")
        if any((
            registration.get("cert_output") is not None,
            registration.get("may_adjudicate") is not False,
            registration.get("mathematical_target_proved") is not False,
            registration.get("may_promote_claim") is not False,
        )):
            errors.append(f"{family}: adjudication/output/proof inflation")
        if route.get("route_id") != route_id or route.get("tracker_issue") != "https://github.com/grandchallenge/MATHCERT/issues/55":
            errors.append(f"{family}: global route entry identity drift")
        if route.get("source_manifest") != PROVIDER or route.get("intake_packet") != packet:
            errors.append(f"{family}: global route authority drift")
        if (
            route.get("intake_status") != "submitted"
            or route.get("cert_output") is not None
            or route.get("target_claim_ids") != EXPECTED_CLAIMS[family]
        ):
            errors.append(f"{family}: global route state inflation")
        if not isinstance(route.get("blockers"), list) or not any(
            "adjudication" in item.lower() for item in route["blockers"]
        ):
            errors.append(f"{family}: adjudication blocker missing")

    expected_state = {
        "proposal_count": 3,
        "registered_route_count": 3,
        "submitted_route_count": 3,
        "adjudication_count": 0,
        "cert_output_count": 0,
        "mathematical_target_proved_count": 0,
        "aggregate_route_count": 0,
    }
    if receipt.get("state") != expected_state:
        errors.append("registration state inflation")
    expected_limitations = {
        "whole_document_byte_equivalence": "not_established",
        "whole_document_semantic_equivalence": "not_established",
        "proof_bodies_compared_in_full": False,
        "unexamined_result_family_count": 9,
        "blocked_repair_lanes": ["OTP-C-PERMANENT", "OTP-H-GAPCVP"],
        "all_lean_state": "failed_namespace_collision",
    }
    if receipt.get("preserved_limitations") != expected_limitations:
        errors.append("preserved limitation drift")
    expected_controls = {
        "registration_scope": "exact_three_result_families",
        "may_adjudicate": False,
        "may_issue_cert_output": False,
        "may_mark_target_proved": False,
        "aggregate_route_prohibited": True,
        "may_promote_claim": False,
    }
    if receipt.get("route_controls") != expected_controls:
        errors.append("registration authority inflation")
    activation = receipt.get("activation", {})
    if (
        activation.get("head_change_requires_reapproval") is not True
        or activation.get("effect") != "three_routes_registered_no_adjudication_no_outputs"
    ):
        errors.append("activation drift")
    claim = str(receipt.get("claim_boundary", ""))
    if not all(token in claim for token in ("does not adjudicate", "Cert output", "aggregate")):
        errors.append("claim boundary weakened")
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"route registration validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print("validated protected three-route registration snapshot; later separately governed Ehrhart, Compactness, and Permanent successors are validated before historical projection")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
