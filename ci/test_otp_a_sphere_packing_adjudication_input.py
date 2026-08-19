#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "ci/validate_otp_a_sphere_packing_adjudication_input.py"
spec = importlib.util.spec_from_file_location("ainput", MODULE)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def main() -> int:
    base = mod.load(mod.INPUT)
    baseline = mod.validation_errors(base)
    if baseline:
        raise AssertionError("baseline invalid: " + "; ".join(baseline))

    mutations = []
    def add(label, fn):
        value = copy.deepcopy(base)
        fn(value)
        mutations.append((label, value))

    add("target removal", lambda r: r["encoded_targets"].pop())
    add("target substitution", lambda r: r["encoded_targets"].__setitem__(0, "PackingBounds.fake"))
    add("classification swap", lambda r: r["classifications"].__setitem__(0, r["classifications"][1]))
    add("classification removal", lambda r: r["classifications"].pop())
    add("route transition", lambda r: r["required_state"].__setitem__("route_state", "qualified"))
    add("pre-adjudication", lambda r: r["decision_contract"].__setitem__("disposition_at_input_stage", "adjudication_clear_protected_four_targets_only"))
    add("Cert output insertion", lambda r: r["required_state"].__setitem__("cert_output", {}))
    add("proof promotion", lambda r: r["required_state"].__setitem__("mathematical_target_proved", True))
    add("claim promotion", lambda r: r["required_state"].__setitem__("may_promote_claim", True))
    add("aggregate adjudication", lambda r: r["required_state"].__setitem__("aggregate_adjudication", True))
    add("aggregate output", lambda r: r["required_state"].__setitem__("aggregate_output", True))
    add("decimal provenance inflation", lambda r: r["required_state"].__setitem__("manuscript_decimal_precision_attributed", True))
    add("normalization erasure", lambda r: r["required_state"].__setitem__("scale_normalization_boundary_required", False))
    add("composite verbatim inflation", lambda r: r["required_state"].__setitem__("composite_is_single_verbatim_source_theorem", True))
    add("whole chapter inflation", lambda r: r["required_state"].__setitem__("whole_chapter_equivalence_established", True))
    add("full proof body inflation", lambda r: r["required_state"].__setitem__("full_proof_body_equivalence_established", True))
    add("axiom drift", lambda r: r["permitted_axioms"].append("Classical.propComplete"))
    add("nonvacuity weakening", lambda r: r.__setitem__("nonvacuity_state", "unknown"))
    add("Human Steward gate reinsertion", lambda r: r["execution_recipe"].__setitem__("separate_human_steward_authorization_required", True))
    add("contract authority removal", lambda r: r["execution_recipe"].__setitem__("execution_authorized_by_protected_contract", False))
    add("intervention boundary weakening", lambda r: r["execution_recipe"].__setitem__("human_steward_intervention_required_only_for_control_plan_change", False))
    add("contract substitution", lambda r: r["contract"].__setitem__("git_blob_sha1", "0" * 40))
    add("design registry substitution", lambda r: r["design_registry"].__setitem__("git_blob_sha1", "0" * 40))
    add("registration substitution", lambda r: r["protected_registration"].__setitem__("route_registry_git_blob_sha1", "0" * 40))
    add("replay substitution", lambda r: r["protected_evidence"].__setitem__("replay_record_git_blob_sha1", "0" * 40))
    add("Forge composite substitution", lambda r: r["protected_evidence"]["forge_composite"].__setitem__("git_blob_sha1", "0" * 40))
    add("Forge bridge substitution", lambda r: r["protected_evidence"]["forge_bridge"].__setitem__("git_blob_sha1", "0" * 40))
    add("source substitution", lambda r: r["current_source"].__setitem__("expected_sha256", "0" * 64))
    add("formal subject substitution", lambda r: r["formal_subject"].__setitem__("commit", "0" * 40))
    add("review prepopulation", lambda r: r["review_gate"].__setitem__("recorded_review", {"state":"APPROVED"}))
    add("little-o strengthening", lambda r: r["preserved_limitations"].__setitem__("little_o_strengthened", True))
    add("other family mutation", lambda r: r["preserved_limitations"].__setitem__("other_result_families_modified", True))
    add("unknown field", lambda r: r.__setitem__("unexpected", True))

    for label, value in mutations:
        errors = mod.validation_errors(value, check_repository=False)
        if not errors:
            raise AssertionError(f"mutation accepted: {label}")
    print(f"A adjudication input mutation suite rejected {len(mutations)} adversarial changes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
