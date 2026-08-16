#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "ci/validate_otp_j2_source_faithful_evidence.py"
spec = importlib.util.spec_from_file_location("j2ev", MODULE)
assert spec and spec.loader
j2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(j2)


def reject(label: str, record: dict, routes: dict) -> None:
    if not j2.validation_errors(record, routes, check_files=False):
        raise AssertionError(f"mutation accepted: {label}")


def mutate_route(routes: dict, key: str, value) -> dict:
    result = copy.deepcopy(routes)
    route = j2.find_route(result, "MC-ROUTE-OTP-J2-TWO-DEGENERATE")
    assert route is not None
    route[key] = value
    return result


def main() -> int:
    record = j2.load(j2.RECORD)
    routes = j2.load(j2.ROUTES)
    baseline = j2.validation_errors(record, routes, check_files=True)
    if baseline:
        raise AssertionError("baseline invalid:\n" + "\n".join(baseline))

    cases: list[tuple[str, dict, dict]] = []
    def add(label: str, mutator):
        m = copy.deepcopy(record); mutator(m); cases.append((label, m, routes))

    add("source substitution", lambda m: m["source_assessment"].__setitem__("current_official_source_sha256", "0" * 64))
    add("theorem locus drift", lambda m: m["source_assessment"].__setitem__("theorem_locus", "Chapter 10 Theorem 1.1"))
    add("coloring source attribution", lambda m: m["source_assessment"].__setitem__("stronger_coloring_property_source_authorized", True))
    add("coloring certification", lambda m: m["preserved_limitations"].__setitem__("stronger_coloring_property_certified", True))
    add("target inflation", lambda m: m["evidence_subjects"].append("OtherFamily.target"))
    add("historical target rewrite", lambda m: m["historical_registered_targets"].__setitem__(0, m["evidence_subjects"][0]))
    add("authority substitution", lambda m: m["authority"]["scope_repair"].__setitem__("digest", "0" * 40))
    add("source artifact substitution", lambda m: m["authority"]["source_authority"].__setitem__("digest", "0" * 40))
    add("reconstruction substitution", lambda m: m["authority"]["reconstruction"].__setitem__("digest", "0" * 40))
    add("parameter evidence removal", lambda m: m["construction_assessment"].__setitem__("parameter_window_nonempty", "absent"))
    add("exponent evidence removal", lambda m: m["construction_assessment"].__setitem__("exponent_bridge", "absent"))
    add("construction gap insertion", lambda m: m["construction_assessment"].__setitem__("substantive_mathematical_gap_found", True))
    add("proof body overclaim", lambda m: m["source_assessment"].__setitem__("proof_body_compared_in_full", True))
    add("entropy formalization overclaim", lambda m: m["construction_assessment"].__setitem__("source_internal_entropy_lemmas_reformalized", True))
    add("premature adjudication", lambda m: m["required_state"].__setitem__("may_adjudicate", True))
    add("output insertion", lambda m: m["required_state"].__setitem__("cert_output", "certificate.json"))
    add("proof promotion", lambda m: m["required_state"].__setitem__("mathematical_target_proved", True))
    add("aggregate insertion", lambda m: m["required_state"].__setitem__("aggregate_authority", True))
    add("runtime prepopulation", lambda m: m["fresh_runtime_replay"].__setitem__("workflow_run_id", 1))
    add("premature clear disposition", lambda m: m["disposition"].__setitem__("ready_for_route_target_successor", True))

    cases.append(("route transition", record, mutate_route(routes, "intake_status", "qualified")))
    cases.append(("route output insertion", record, mutate_route(routes, "cert_output", {"path": "x"})))
    cases.append(("silent route-target successor", record, mutate_route(routes, "target_claim_ids", j2.EVIDENCE_SUBJECTS)))

    for label, candidate, route_value in cases:
        reject(label, candidate, route_value)

    print(f"J2 source-faithful evidence mutation suite rejected {len(cases)} adversarial changes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
