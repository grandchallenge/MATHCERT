#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "ci/validate_otp_j2_adjudication_input.py"
spec = importlib.util.spec_from_file_location("j2input", MODULE)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def main() -> int:
    base = mod.load(mod.INPUT)
    baseline = mod.compatibility_errors(base)
    if baseline:
        raise AssertionError("baseline invalid: " + "; ".join(baseline))

    mutations = []
    def add(label, fn):
        value = copy.deepcopy(base)
        fn(value)
        mutations.append((label, value))

    add("target removal", lambda r: r["encoded_targets"].pop())
    add("historical target live insertion", lambda r: r["encoded_targets"].append(r["historical_predecessor_targets"][0]))
    add("target substitution", lambda r: r["encoded_targets"].__setitem__(0, r["historical_predecessor_targets"][0]))
    add("route transition", lambda r: r["required_state"].__setitem__("route_state", "qualified"))
    add("Cert output insertion", lambda r: r["required_state"].__setitem__("cert_output", {}))
    add("proof promotion", lambda r: r["required_state"].__setitem__("mathematical_target_proved", True))
    add("aggregate adjudication", lambda r: r["required_state"].__setitem__("aggregate_adjudication", True))
    add("coloring source attribution", lambda r: r["required_state"].__setitem__("stronger_coloring_property_source_authorized", True))
    add("coloring certification", lambda r: r["required_state"].__setitem__("stronger_coloring_property_certified", True))
    add("pre-adjudication", lambda r: r["decision_contract"].__setitem__("disposition_at_input_stage", "adjudication_clear_source_faithful_targets_only"))
    add("Human Steward gate reinsertion", lambda r: r["execution_recipe"].__setitem__("separate_human_steward_authorization_required", True))
    add("contract authority removal", lambda r: r["execution_recipe"].__setitem__("execution_authorized_by_protected_contract", False))
    add("intervention boundary weakening", lambda r: r["execution_recipe"].__setitem__("human_steward_intervention_required_only_for_control_plan_change", False))
    add("contract substitution", lambda r: r["contract"].__setitem__("git_blob_sha1", "0" * 40))
    add("route successor substitution", lambda r: r["route_target_successor"].__setitem__("git_blob_sha1", "0" * 40))
    add("evidence substitution", lambda r: r["protected_evidence"].__setitem__("record_git_blob_sha1", "0" * 40))
    add("source substitution", lambda r: r["current_source"].__setitem__("expected_sha256", "0" * 64))
    add("formal subject substitution", lambda r: r["formal_subject"].__setitem__("commit", "0" * 40))
    add("route snapshot substitution", lambda r: r["route_snapshot"].__setitem__("registry_git_blob_sha1", "0" * 40))
    add("review prepopulation", lambda r: r["review_gate"].__setitem__("recorded_review", {"state":"APPROVED"}))
    add("whole-document inflation", lambda r: r["preserved_limitations"].__setitem__("whole_document_semantic_equivalence", "established"))
    add("proof-body inflation", lambda r: r["preserved_limitations"].__setitem__("proof_body_compared_in_full", True))
    add("entropy formalization inflation", lambda r: r["preserved_limitations"].__setitem__("source_internal_entropy_lemmas_reformalized", True))
    add("unknown field", lambda r: r.__setitem__("unexpected", True))

    for label, value in mutations:
        errors = mod.validation_errors(value, check_repository=False)
        if not errors:
            raise AssertionError(f"mutation accepted: {label}")
    print(f"J2 adjudication input mutation suite rejected {len(mutations)} adversarial changes; live output successor validated separately")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
