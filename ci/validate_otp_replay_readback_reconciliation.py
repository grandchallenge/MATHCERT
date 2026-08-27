#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "governance" / "result_family_replay_evidence_readbacks" / "OTP-H-B1-B2.json"
SCHEMA = ROOT / "schemas" / "openai_ten_proofs_replay_readback_reconciliation.schema.json"
ROUTES = ROOT / "governance" / "certification_routes.json"
ROUTE_REGISTRY_PATH = "governance/certification_routes.json"
PROTECTED_PREDECESSOR_HEAD = "99cfde542cdb044145f6620190dfb6ee9cd7a959"
PROTECTED_PREDECESSOR_ROUTE_BLOB = "4d5c8e3f2b33d5148d98e7057991e167938c75bb"
FULL_ESTATE_SCOPE = "FULL_ESTATE"
FORBIDDEN_REPLAY_ERA_ROUTES = {
    "MC-ROUTE-OTP-H-GAPCVP",
    "MC-ROUTE-OTP-B1-BINARY-CODES",
    "MC-ROUTE-OTP-B2-SPHERICAL-CODES",
}

EXPECTED = {
    "OTP-H-GAPCVP": {
        "candidate_path": "governance/result_family_replay_evidence_successors/OTP-H-GAPCVP.json",
        "candidate_blob": "a12f2c553b71f4daec9255e1f254f48a21f439c3",
        "issue": 165, "pr": 169,
        "head": "fca63848cfb1428292e4b74a4ed8980646d45aa2",
        "review": 5023763871,
        "merge": "f34f33b22292ca244956781065fdf84efe2b43f2",
        "parents": ["aa6a730394db45ca05c9a3d0a02434bc74fd8a61", "fca63848cfb1428292e4b74a4ed8980646d45aa2"],
        "runs": [32848939191, 32848939207, 32848940096, 32848939106],
        "disposition": "H_REPLAY_EVIDENCE_PROTECTED__ZERO_ROUTE_OUTPUT_AUTHORITY",
        "next": "separate_family_specific_H_route_proposal",
    },
    "OTP-B1-BINARY-CODES": {
        "candidate_path": "governance/result_family_replay_evidence_successors/OTP-B1-BINARY-CODES.json",
        "candidate_blob": "fd669ae6cfc39110560656c2123d5d4449200830",
        "issue": 166, "pr": 170,
        "head": "67f445b9a5e015083644416d96f4a10722efe032",
        "review": 5023771071,
        "merge": "d8daab1c0deec3d41ac438714e21ee752c14ac46",
        "parents": ["f34f33b22292ca244956781065fdf84efe2b43f2", "67f445b9a5e015083644416d96f4a10722efe032"],
        "runs": [32849083880, 32849083816, 32849084349, 32849083761],
        "disposition": "B1_REPLAY_EVIDENCE_PROTECTED__ZERO_ROUTE_OUTPUT_AUTHORITY",
        "next": "separate_family_specific_B1_route_proposal",
    },
    "OTP-B2-SPHERICAL-CODES": {
        "candidate_path": "governance/result_family_replay_evidence_successors/OTP-B2-SPHERICAL-CODES.json",
        "candidate_blob": "288193448eee80c041beef57059182e1abe2e33c",
        "issue": 167, "pr": 171,
        "head": "da41ab10f440b45fe53d321bc08bd3ffa8770930",
        "review": 5023775055,
        "merge": "938738844c4659b30a21d963da468ddfd1df51ad",
        "parents": ["d8daab1c0deec3d41ac438714e21ee752c14ac46", "da41ab10f440b45fe53d321bc08bd3ffa8770930"],
        "runs": [32849224700, 32849225046, 32849225863, 32849224740],
        "disposition": "B2_REPLAY_EVIDENCE_PROTECTED__ZERO_ROUTE_OUTPUT_AUTHORITY",
        "next": "separate_family_specific_B2_route_proposal",
    },
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def blob_at_head(path: str) -> str:
    return subprocess.check_output(["git", "rev-parse", f"HEAD:{path}"], cwd=ROOT, text=True).strip()


def blob_at_commit(commit: str, path: str) -> str:
    return subprocess.check_output(["git", "rev-parse", f"{commit}:{path}"], cwd=ROOT, text=True).strip()


def load_at_commit(commit: str, path: str):
    raw = subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=ROOT, text=True)
    return json.loads(raw)


def route_ids(registry: object) -> set[str]:
    if not isinstance(registry, dict):
        return set()
    return {
        str(route.get("route_id"))
        for route in registry.get("routes", [])
        if isinstance(route, dict) and route.get("route_id") is not None
    }


def validation_errors(
    record=None,
    *,
    check_repo: bool = True,
    current_routes=None,
    predecessor_routes=None,
    predecessor_route_blob: str | None = None,
) -> list[str]:
    data = load(RECORD) if record is None else record
    errors: list[str] = []
    schema = load(SCHEMA)
    for error in sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path)):
        errors.append(f"schema:{'/'.join(map(str, error.path))}: {error.message}")

    if data.get("protected_predecessor", {}).get("mathcert_main") != PROTECTED_PREDECESSOR_HEAD:
        errors.append("protected predecessor MATHCERT head drift")
    if data.get("protected_predecessor", {}).get("route_registry_blob") != PROTECTED_PREDECESSOR_ROUTE_BLOB:
        errors.append("protected predecessor route-registry blob drift")

    families = {entry.get("result_family"): entry for entry in data.get("families", []) if isinstance(entry, dict)}
    if set(families) != set(EXPECTED):
        errors.append("family set must be exactly H, B1, B2")
    candidates = {entry.get("result_family"): entry for entry in data.get("historical_candidate_policy", {}).get("files", []) if isinstance(entry, dict)}
    if set(candidates) != set(EXPECTED):
        errors.append("historical candidate set must be exactly H, B1, B2")

    for family, expected in EXPECTED.items():
        entry = families.get(family, {})
        candidate = candidates.get(family, {})
        checks = {
            "tracker_issue": expected["issue"], "pull_request": expected["pr"],
            "exact_reviewed_head": expected["head"], "protected_merge": expected["merge"],
            "merge_parents": expected["parents"], "terminal_disposition": expected["disposition"],
            "next_boundary": expected["next"],
        }
        for key, value in checks.items():
            if entry.get(key) != value:
                errors.append(f"{family} {key} drift")
        review = entry.get("non_author_review", {})
        if review.get("reviewer") != "jimsteeg" or review.get("review_id") != expected["review"] or review.get("state") != "APPROVED" or review.get("commit_id") != expected["head"]:
            errors.append(f"{family} binding review drift")
        runs = entry.get("exact_head_runs", {})
        observed_runs = [runs.get("family_replay"), runs.get("cert"), runs.get("gcl"), runs.get("compatibility")]
        if observed_runs != expected["runs"]:
            errors.append(f"{family} exact-head run identities drift")
        for flag in ("route_proposed", "route_registered", "may_adjudicate", "mathematical_target_proved", "aggregate_authority"):
            if entry.get(flag) is not False:
                errors.append(f"{family} unauthorized {flag}")
        if entry.get("protected_replay_evidence") is not True or entry.get("adjudication") is not None or entry.get("cert_output") is not None:
            errors.append(f"{family} replay-only authority boundary drift")
        if candidate.get("path") != expected["candidate_path"] or candidate.get("blob") != expected["candidate_blob"]:
            errors.append(f"{family} historical candidate identity drift")

    authority = data.get("preserved_authority", {})
    if any(authority.get(key) not in (False, 0) for key in authority):
        errors.append("preserved authority contains an unauthorized positive state")

    if check_repo:
        for family, expected in EXPECTED.items():
            try:
                if blob_at_head(expected["candidate_path"]) != expected["candidate_blob"]:
                    errors.append(f"{family} historical candidate bytes changed")
                historical = load(ROOT / expected["candidate_path"])
                if historical.get("repository_admission_status") != "candidate_pending_protected_merge":
                    errors.append(f"{family} historical candidate pending-merge field was rewritten")
            except Exception as exc:
                errors.append(f"{family} historical candidate readback failed: {exc}")

        try:
            observed_predecessor_blob = (
                blob_at_commit(PROTECTED_PREDECESSOR_HEAD, ROUTE_REGISTRY_PATH)
                if predecessor_route_blob is None
                else predecessor_route_blob
            )
            if observed_predecessor_blob != PROTECTED_PREDECESSOR_ROUTE_BLOB:
                errors.append("protected predecessor route-registry bytes drift")
            historical_registry = (
                load_at_commit(PROTECTED_PREDECESSOR_HEAD, ROUTE_REGISTRY_PATH)
                if predecessor_routes is None
                else predecessor_routes
            )
            if route_ids(historical_registry) & FORBIDDEN_REPLAY_ERA_ROUTES:
                errors.append("H/B1/B2 route existed at protected replay-readback predecessor")
        except Exception as exc:
            errors.append(f"protected predecessor route-registry readback failed: {exc}")

        live_registry = load(ROUTES) if current_routes is None else current_routes
        routes = live_registry.get("routes", []) if isinstance(live_registry, dict) else []
        a = next((r for r in routes if isinstance(r, dict) and r.get("route_id") == "MC-ROUTE-OTP-A-SPHERE-PACKING"), None)
        if not a or a.get("intake_status") != "qualified" or a.get("cert_output") is None:
            errors.append("protected A restricted qualification regressed")
    return errors


def main() -> int:
    scope = os.environ.get("MC_CERT_SCOPE", "")
    if scope and scope != FULL_ESTATE_SCOPE:
        print(
            "MATHCERT_CONTEXT_SKIP=ci/validate_otp_replay_readback_reconciliation.py "
            f"family=FULL_ESTATE_ONLY active={scope}"
        )
        return 0
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("validated protected H/B1/B2 replay readback reconciliation at its exact historical predecessor; later route evolution is governed separately")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
