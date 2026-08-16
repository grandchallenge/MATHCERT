#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "ci/validate_otp_j2_scope_repair.py"
spec = importlib.util.spec_from_file_location("j2_scope", MODULE)
assert spec and spec.loader
j2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(j2)
PREDECESSOR_ROUTE_BLOB = "bc4640661443f1b3de213aaa82a333a4fdb6849b"


def predecessor_routes() -> dict:
    proc = subprocess.run(
        ["git", "-C", str(ROOT), "cat-file", "blob", PREDECESSOR_ROUTE_BLOB],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(proc.stdout)


def expect_reject(label: str, record: dict, routes: dict, overlay: str) -> None:
    if not j2.validation_errors(record, routes, overlay, check_files=False):
        raise AssertionError(f"mutation accepted: {label}")


def mutate_registered_route(routes: dict, key: str, value) -> dict:
    changed = copy.deepcopy(routes)
    route = j2.find_route(changed, "MC-ROUTE-OTP-J2-TWO-DEGENERATE")
    if route is None:
        raise AssertionError("baseline J2 route missing")
    route[key] = value
    return changed


def main() -> int:
    record = j2.load(j2.RECORD)
    routes = predecessor_routes()
    overlay = j2.OVERLAY.read_text(encoding="utf-8")
    baseline = j2.validation_errors(record, routes, overlay, check_files=False)
    if baseline:
        raise AssertionError("historical predecessor baseline invalid:\n" + "\n".join(baseline))

    cases = []

    m = copy.deepcopy(record); m["current_state"]["may_adjudicate"] = True
    cases.append(("premature adjudication", m, routes, overlay))
    m = copy.deepcopy(record); m["current_state"]["cert_output"] = "inserted.json"
    cases.append(("output insertion", m, routes, overlay))
    m = copy.deepcopy(record); m["current_state"]["mathematical_target_proved"] = True
    cases.append(("proof promotion", m, routes, overlay))
    m = copy.deepcopy(record); m["current_state"]["aggregate_authority"] = True
    cases.append(("aggregate insertion", m, routes, overlay))
    m = copy.deepcopy(record); m["authority"]["human_steward_authorization"]["comment_id"] = 1
    cases.append(("authorization substitution", m, routes, overlay))
    m = copy.deepcopy(record); m["current_source"]["sha256"] = "0" * 64
    cases.append(("source substitution", m, routes, overlay))
    m = copy.deepcopy(record); m["current_source"]["not_source_authorized"] = []
    cases.append(("coloring exclusion removal", m, routes, overlay))
    m = copy.deepcopy(record); m["historical_registered_targets"].append("OtherFamily.target")
    cases.append(("family inflation", m, routes, overlay))
    m = copy.deepcopy(record); m["historical_target_treatment"]["stronger_coloring_conjunct_source_attributed"] = True
    cases.append(("stronger property source attribution", m, routes, overlay))
    m = copy.deepcopy(record); m["source_faithful_projection"]["future_certification_scope"][0] = "TwoDegenerateGraphs.twoDegenerateExtremalCounterexample"
    cases.append(("stronger target reintroduction", m, routes, overlay))
    m = copy.deepcopy(record); m["source_faithful_projection"]["may_silently_replace_registered_target_identity"] = True
    cases.append(("silent target replacement", m, routes, overlay))
    m = copy.deepcopy(record); m["source_faithful_projection"]["overlay_artifact"]["digest"] = "0" * 40
    cases.append(("projection artifact substitution", m, routes, overlay))
    m = copy.deepcopy(record); m["dependency_audit"]["stronger_coloring_conjunct_used"] = True
    cases.append(("dependency broadening", m, routes, overlay))
    m = copy.deepcopy(record); m["current_formal_subject"]["challenge"]["digest"] = "0" * 40
    cases.append(("challenge substitution", m, routes, overlay))
    m = copy.deepcopy(record); m["current_formal_subject"]["lake_manifest"]["digest"] = "0" * 40
    cases.append(("dependency-manifest substitution", m, routes, overlay))

    changed_routes = mutate_registered_route(routes, "intake_status", "qualified")
    cases.append(("route transition", record, changed_routes, overlay))
    changed_routes = mutate_registered_route(routes, "cert_output", {"path": "inserted.json"})
    cases.append(("route output insertion", record, changed_routes, overlay))
    changed_routes = mutate_registered_route(routes, "target_claim_ids", [
        "TwoDegenerateGraphs.mathcert_sourceFaithfulTwoDegenerateExtremalCounterexample",
        "TwoDegenerateGraphs.not_erdos_146",
    ])
    cases.append(("silent registered-target replacement", record, changed_routes, overlay))

    changed = overlay.replace(
        "H.IsBipartite ∧\n      IsTwoDegenerate H ∧\n      ∃ c ε",
        "H.IsBipartite ∧\n      IsTwoDegenerate H ∧\n      (∀ coloring : H.Coloring (Fin 2), True) ∧\n      ∃ c ε",
        1,
    )
    cases.append(("coloring property injected into projection", record, routes, changed))

    changed = overlay.replace(
        "intro hconjecture\n  obtain ⟨q, H, _hconnected",
        "intro hconjecture\n  have _extra := twoDegenerateExtremalCounterexample\n  obtain ⟨q, H, _hconnected",
        1,
    )
    cases.append(("stronger theorem injected into dependency proof", record, routes, changed))

    for label, r, routes_value, lean in cases:
        expect_reject(label, r, routes_value, lean)

    print(f"J2 scope-repair mutation suite rejected {len(cases)} adversarial changes against protected predecessor route snapshot")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
