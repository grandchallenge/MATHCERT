#!/usr/bin/env python3
"""Independent EUCLID-DIOPHANTINE-E2E-002 checker.

The committed candidate is data only. This module never imports or executes
the MATHSOLVE producer.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
CANDIDATE_PATH = ROOT / "evidence/euclid_diophantine/solve_candidate.json"
RECEIPT_PATH = ROOT / "evidence/euclid_diophantine/upstream_receipt.json"
CERT_PATH = ROOT / "governance/certification_outputs/EUCLID-DIOPHANTINE-E2E-002.json"
OVERLAY_PATH = ROOT / "governance/certification_route_overlays/EUCLID-DIOPHANTINE-E2E-002.json"
SCHEMA_PATH = ROOT / "schemas/euclid_diophantine_certification.schema.json"

BLOBS = {
    "candidate": "74703b449fa861b72be1eaf89fb1c39a943183ce",
    "producer": "5f4ffaf644da47cecd50fd3013a6412eb90ca555",
    "handoff": "80a4bf5082ac9ed9459a1dbd7dbb77166e84764e",
    "manifest": "d4c3ced7eb3bbf4c3d865a847f9b701cf677cdf4",
    "claim_ledger": "e8371b64a350902d6fe16b57587a1a9de0090625",
    "proof_obligation_dag": "919dcb58683f96f87e1d0c499e11e92fb3da34bc",
    "failed_route_ledger": "2277b227d9b58f1afd678ef72dfd8bc259f9c73d",
    "resource_ledger": "4aae9e2e74ab9eb0e7d93de9c1cb9b73b770838a",
}
COMMITS = {
    "forge": "af5398a05f17789a061ab0d23c2b47f0cc952fff",
    "stage1_solve": "3a8493aa322f0e640c921b8824c4d7f88a8c057d",
    "stage1_cert": "78b69e6a3461a83f4893d61c421b1570c08a9ba6",
    "solve": "66d54d375ae4dfc148888325b6093818669e7c02",
}
STAGE1_OUTPUT = "36c62434dbd19719d990e71ddc23729f0614ace7"
HEX40 = re.compile(r"^[0-9a-f]{40}$")


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(data)}\0".encode() + data, usedforsecurity=False
    ).hexdigest()


def _expect(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def receipt_errors(r: dict[str, Any]) -> list[str]:
    e: list[str] = []
    _expect(e, r.get("campaign_id") == "EUCLID-DIOPHANTINE-E2E-002", "receipt campaign drift")
    _expect(e, r.get("programme") == {
        "issue": 238,
        "protected_stage1_closeout": "183ff2a0adfbe5bd0ffd5f2e638089b94b868c54",
        "repository": "grandchallenge/MATH-PROGRAMME",
    }, "Programme receipt drift")
    f = r.get("forge", {})
    _expect(e, f.get("merge_commit") == COMMITS["forge"], "Forge merge drift")
    _expect(e, f.get("package", {}).get("git_blob_sha1") == "e89d5b7c611aaa4a7fdea716742e993eaa283da1", "Forge package drift")
    _expect(e, f.get("provider_manifest", {}).get("git_blob_sha1") == "de9dae12cd578ee98b58e6fc1b39365f8c1e7109", "Forge manifest drift")
    s1 = r.get("protected_stage1", {})
    _expect(e, s1.get("solve_merge_commit") == COMMITS["stage1_solve"], "Stage 1 Solve drift")
    _expect(e, s1.get("cert_merge_commit") == COMMITS["stage1_cert"], "Stage 1 Cert drift")
    _expect(e, s1.get("solve_candidate", {}).get("git_blob_sha1") == "af54ae9b9a047a36767b2599ebc649fb6fdaaa52", "Stage 1 candidate drift")
    _expect(e, s1.get("certification_output", {}).get("git_blob_sha1") == STAGE1_OUTPUT, "Stage 1 output drift")
    s = r.get("solve", {})
    _expect(e, s.get("merge_commit") == COMMITS["solve"], "Stage 2 Solve merge drift")
    _expect(e, s.get("merge_parents") == [COMMITS["stage1_solve"], "d4bec98dfea28bb605b3f8c642e18dec697ee4a3"], "Stage 2 parents drift")
    for key, expected in BLOBS.items():
        _expect(e, s.get(key, {}).get("git_blob_sha1") == expected, f"Solve {key} drift")
    _expect(e, s.get("handoff", {}).get("status") == "ready", "handoff is not ready")
    return e


def candidate_errors(c: dict[str, Any]) -> list[str]:
    e: list[str] = []
    _expect(e, c.get("authority_state") == "candidate_only", "candidate authority inflation")
    _expect(e, c.get("campaign_id") == "EUCLID-DIOPHANTINE-E2E-002", "candidate campaign drift")
    scope = c.get("candidate_scope", {})
    _expect(e, scope.get("coefficient_family") == "(abs(a),abs(b)) = (252,105)", "coefficient-family drift")
    _expect(e, scope.get("arbitrary_diophantine_completeness_claimed") is False, "arbitrary completeness inflation")
    for key, value in c.get("claim_boundary", {}).items():
        if key.endswith("_claimed") or key.endswith("_accepted") or key == "theorem_certified":
            _expect(e, value is False, f"claim boundary inflation: {key}")
    _expect(e, c.get("forge_input", {}).get("commit_sha") == COMMITS["forge"], "candidate Forge drift")
    s1 = c.get("protected_stage1", {})
    _expect(e, s1.get("solve_merge_commit") == COMMITS["stage1_solve"], "candidate Stage 1 Solve drift")
    _expect(e, s1.get("cert_merge_commit") == COMMITS["stage1_cert"], "candidate Stage 1 Cert drift")
    _expect(e, s1.get("certification_output", {}).get("digest") == STAGE1_OUTPUT, "candidate Stage 1 output drift")
    _expect(e, s1.get("normalized_gcd") == 21, "protected gcd drift")
    _expect(e, s1.get("positive_bezout") == {"x": -2, "y": 5}, "protected Bezout drift")
    solver = c.get("solver", {})
    for key in ("network_used", "randomness_used", "recomputes_gcd", "timeout_or_failed_search_used_as_unsat"):
        _expect(e, solver.get(key) is False, f"solver boundary drift: {key}")

    cases = c.get("cases", [])
    if not isinstance(cases, list) or len(cases) != 2:
        return e + ["exactly two cases are required"]
    p, n = cases
    _expect(e, p.get("inputs") == {"a": 252, "b": 105, "c": 84}, "positive input drift")
    _expect(e, p.get("evidence_type") == "constructive_solution", "positive evidence drift")
    sol = p.get("constructive_solution", {})
    _expect(e, sol.get("base_bezout") == {"equation_value": 21, "x": -2, "y": 5}, "base Bezout drift")
    _expect(e, sol.get("scale_factor") == 4 and 4 * 21 == 84, "scale-factor drift")
    _expect(e, (sol.get("x"), sol.get("y"), sol.get("equation_value")) == (-8, 20, 84), "positive witness drift")
    _expect(e, 252 * sol.get("x", 0) + 105 * sol.get("y", 0) == 84, "positive equation false")
    _expect(e, p.get("divisibility_obstruction") is None, "positive obstruction injection")

    _expect(e, n.get("inputs") == {"a": 252, "b": 105, "c": 20}, "negative input drift")
    _expect(e, n.get("evidence_type") == "divisibility_obstruction", "negative evidence drift")
    _expect(e, n.get("constructive_solution") is None, "negative witness injection")
    o = n.get("divisibility_obstruction", {})
    q, r, d = o.get("quotient"), o.get("remainder"), n.get("normalized_gcd")
    if all(isinstance(x, int) for x in (q, r, d)):
        _expect(e, 20 == q * d + r, "obstruction equation false")
        _expect(e, 0 < r < d, "obstruction bound false")
        _expect(e, math.gcd(252, 105) == d, "independent gcd replay failed")
        _expect(e, 252 % d == 0 and 105 % d == 0 and 20 % d == r != 0, "divisibility obstruction false")
    else:
        e.append("obstruction fields must be integers")
    _expect(e, o.get("strict_nonzero_remainder") is True, "nonzero-remainder flag drift")
    return e


def output_errors(c: dict[str, Any]) -> list[str]:
    e: list[str] = []
    _expect(e, c.get("proposed_disposition") == "CERTIFIED_LINEAR_DIOPHANTINE_EQUIVALENCE_AND_BOUNDED_EXEMPLARS", "disposition drift")
    _expect(e, c.get("authority_state") == "candidate_certification_output_pending_protected_merge", "pre-merge authority drift")
    u = c.get("upstream", {})
    _expect(e, u.get("solve_merge_commit") == COMMITS["solve"], "output Solve merge drift")
    for key, expected in (("solve_candidate", BLOBS["candidate"]), ("solve_handoff", BLOBS["handoff"]), ("solve_manifest", BLOBS["manifest"]), ("protected_stage1_output", STAGE1_OUTPUT)):
        _expect(e, u.get(key, {}).get("git_blob_sha1") == expected, f"output {key} drift")
    _expect(e, c.get("independent_checker", {}).get("does_not_import_or_execute_solve_producer") is True, "checker independence drift")
    f = c.get("formalization", {})
    _expect(e, f.get("sorry_allowed") is False and f.get("local_axioms_allowed") is False, "formal trust inflation")
    ids = [x.get("claim_id") for x in c.get("accepted_claims", [])]
    _expect(e, ids == [f"EUCLID-DIOPHANTINE-E2E-002-C00{i}" for i in range(1, 5)], "accepted claim-set drift")
    nonclaims = " ".join(c.get("rejected_or_unclaimed", []))
    for phrase in ("arbitrary Diophantine", "timeout", "verbatim", "novel", "Book VII", "automatically activated"):
        _expect(e, phrase in nonclaims, f"missing boundary: {phrase}")
    _expect(e, c.get("protected_effect") == "none_until_exact_head_review_human_steward_disposition_and_protected_merge", "output protected-effect drift")
    return e


def overlay_errors(o: dict[str, Any]) -> list[str]:
    e: list[str] = []
    _expect(e, o.get("base_registry", {}).get("digest") == "0487c3ebf702229741f16a544d68af25cf994e41", "base route drift")
    expected_prior = ["de56bfb0544b27b6237a68ac87044d3f0ba2e445", "0ada97db2673db819104320d128bd994e892f1a4"]
    _expect(e, [x.get("digest") for x in o.get("prior_overlays", [])] == expected_prior, "prior overlay drift")
    r = o.get("route", {})
    _expect(e, r.get("route_id") == "MC-ROUTE-EUCLID-DIOPHANTINE-E2E-002", "route id drift")
    _expect(e, r.get("intake_status") == "certified", "route state drift")
    _expect(e, r.get("source_manifest", {}).get("commit_sha") == COMMITS["solve"] and r.get("source_manifest", {}).get("digest") == BLOBS["manifest"], "source manifest drift")
    _expect(e, r.get("intake_packet", {}).get("commit_sha") == COMMITS["solve"] and r.get("intake_packet", {}).get("digest") == BLOBS["handoff"], "intake packet drift")
    out = r.get("cert_output", {})
    _expect(e, HEX40.fullmatch(str(out.get("commit_sha", ""))) is not None, "output layer commit malformed")
    _expect(e, out.get("digest") == blob(CERT_PATH), "output blob drift")
    _expect(e, r.get("mathematical_target_proved") is True, "admitted theorem is not marked proved")
    for key in ("arbitrary_diophantine_completeness_proved", "historical_verbatim_equivalence_established", "novelty_or_priority_authorized", "book_vii_stage_activated"):
        _expect(e, r.get(key) is False, f"route boundary inflation: {key}")
    _expect(e, bool(r.get("blockers")), "downstream blockers missing")
    _expect(e, o.get("protected_effect") == "none_until_exact_head_review_human_steward_disposition_and_protected_merge", "overlay protected-effect drift")
    return e


def validation_errors(candidate=None, receipt=None, cert=None, overlay=None, *, verify_local_blobs=True) -> list[str]:
    candidate = load(CANDIDATE_PATH) if candidate is None else candidate
    receipt = load(RECEIPT_PATH) if receipt is None else receipt
    cert = load(CERT_PATH) if cert is None else cert
    overlay = load(OVERLAY_PATH) if overlay is None else overlay
    errors = [f"schema: {x.json_path}: {x.message}" for x in Draft202012Validator(load(SCHEMA_PATH)).iter_errors(cert)]
    if verify_local_blobs:
        _expect(errors, blob(CANDIDATE_PATH) == BLOBS["candidate"], "local candidate blob drift")
    errors += receipt_errors(receipt)
    errors += candidate_errors(candidate)
    errors += output_errors(cert)
    errors += overlay_errors(overlay)
    return errors


if __name__ == "__main__":
    failures = validation_errors()
    if failures:
        print("\n".join(failures), file=sys.stderr)
        raise SystemExit(1)
    print("validated independent linear-Diophantine certification package")
