#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "ci/validate_otp_j2_adjudication.py"
spec = importlib.util.spec_from_file_location("j2adj", MODULE)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def main() -> int:
    base = mod.load(mod.RECORD)
    baseline = mod.validation_errors(base, check_repository=True)
    if baseline:
        raise AssertionError("baseline invalid: " + "; ".join(baseline))

    cases = []
    def add(label, fn):
        value = copy.deepcopy(base)
        fn(value)
        cases.append((label, value))

    add("target removal", lambda r: r["encoded_targets"].pop())
    add("historical target insertion", lambda r: r["encoded_targets"].append(r["historical_predecessor_targets"][0]))
    add("disposition inflation", lambda r: r["decision"].__setitem__("disposition", "adjudication_clear_all_openai_ten_proofs"))
    add("scope inflation", lambda r: r["decision"].__setitem__("scope", "aggregate"))
    add("coloring exclusion removal", lambda r: r["decision"].__setitem__("stronger_coloring_property_excluded", False))
    add("runtime head substitution", lambda r: r["fresh_execution"].__setitem__("execution_head", "0" * 40))
    add("runtime run substitution", lambda r: r["fresh_execution"].__setitem__("workflow_run_id", 1))
    add("runtime job substitution", lambda r: r["fresh_execution"].__setitem__("replay_job_id", 1))
    add("artifact substitution", lambda r: r["fresh_execution"].__setitem__("artifact_id", 1))
    add("artifact digest substitution", lambda r: r["fresh_execution"].__setitem__("artifact_sha256", "0" * 64))
    add("Lean rejection", lambda r: r["fresh_execution"].__setitem__("lean_kernel", "reject"))
    add("Nanoda rejection", lambda r: r["fresh_execution"].__setitem__("nanoda", "reject"))
    add("Comparator rejection", lambda r: r["fresh_execution"].__setitem__("comparator", "fail"))
    add("nonvacuity removal", lambda r: r["fresh_execution"].__setitem__("nonvacuity", "not_checked"))
    add("axiom inflation", lambda r: r["fresh_execution"]["theorem_axioms"].append("sorryAx"))
    add("source substitution", lambda r: r["source_assessment"].__setitem__("current_sha256", "0" * 64))
    add("coloring source attribution", lambda r: r["source_assessment"].__setitem__("stronger_coloring_property_source_authorized", True))
    add("construction gap", lambda r: r["construction_assessment"].__setitem__("substantive_mathematical_gap_found", True))
    add("entropy overclaim", lambda r: r["construction_assessment"].__setitem__("source_internal_entropy_lemmas_reformalized", True))
    add("route transition", lambda r: r["state"].__setitem__("route_state", "qualified"))
    add("Cert output insertion", lambda r: r["state"].__setitem__("cert_output", {}))
    add("output authority insertion", lambda r: r["state"].__setitem__("may_issue_output", True))
    add("proof promotion", lambda r: r["state"].__setitem__("mathematical_target_proved", True))
    add("aggregate adjudication", lambda r: r["state"].__setitem__("aggregate_adjudication", True))
    add("aggregate output", lambda r: r["state"].__setitem__("aggregate_output", True))
    add("redundant Human Steward gate", lambda r: r["authority"]["protected_contract"].__setitem__("separate_human_steward_authorization_required", True))
    add("contract substitution", lambda r: r["authority"]["protected_contract"].__setitem__("git_blob_sha1", "0" * 40))
    add("input substitution", lambda r: r["authority"]["execution_input"].__setitem__("git_blob_sha1", "0" * 40))
    add("route successor substitution", lambda r: r["authority"]["route_target_successor"].__setitem__("git_blob_sha1", "0" * 40))
    add("evidence substitution", lambda r: r["authority"]["protected_evidence"].__setitem__("record_git_blob_sha1", "0" * 40))
    add("review prepopulation", lambda r: r["review_gate"].__setitem__("recorded_review", {"state":"APPROVED"}))
    add("proof body overclaim", lambda r: r["source_assessment"].__setitem__("proof_body_compared_in_full", True))
    add("aggregate authority limitation removed", lambda r: r["preserved_limitations"].__setitem__("aggregate_openai_ten_proofs_authority", True))
    add("unknown field", lambda r: r.__setitem__("unexpected", True))

    for label, value in cases:
        errors = mod.validation_errors(value, check_repository=False)
        if not errors:
            raise AssertionError(f"mutation accepted: {label}")
    print(f"J2 adjudication mutation suite rejected {len(cases)} adversarial changes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
