#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "ci/validate_otp_a_sphere_packing_adjudication.py"
spec = importlib.util.spec_from_file_location("aadjudication", MODULE)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def main() -> int:
    base = mod.load(mod.RECORD)
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
    add("assessment target drift", lambda r: r["target_assessments"][0].__setitem__("target", "PackingBounds.fake"))
    add("assessment class drift", lambda r: r["target_assessments"][0].__setitem__("classification", r["classifications"][1]))
    add("disposition inflation", lambda r: r["decision"].__setitem__("disposition", "qualified"))
    add("scope inflation", lambda r: r["decision"].__setitem__("scope", "whole_chapter"))
    add("proof exclusion removal", lambda r: r["decision"].__setitem__("does_not_mark_mathematical_target_proved", False))
    add("output exclusion removal", lambda r: r["decision"].__setitem__("does_not_issue_cert_output", False))
    add("route exclusion removal", lambda r: r["decision"].__setitem__("does_not_transition_route", False))
    add("runtime head substitution", lambda r: r["fresh_execution"].__setitem__("execution_head", "0" * 40))
    add("runtime run substitution", lambda r: r["fresh_execution"].__setitem__("workflow_run_id", 1))
    add("runtime job substitution", lambda r: r["fresh_execution"].__setitem__("replay_job_id", 1))
    add("artifact id substitution", lambda r: r["fresh_execution"]["artifact"].__setitem__("artifact_id", 1))
    add("artifact hash substitution", lambda r: r["fresh_execution"]["artifact"].__setitem__("zip_sha256", "0" * 64))
    add("bundle hash substitution", lambda r: r["fresh_execution"]["artifact"].__setitem__("adjudication_bundle_sha256", "0" * 64))
    add("replay bundle hash substitution", lambda r: r["fresh_execution"]["artifact"].__setitem__("replay_bundle_sha256", "0" * 64))
    add("Comparator rejection", lambda r: r["fresh_execution"].__setitem__("comparator", "reject"))
    add("Lean kernel rejection", lambda r: r["fresh_execution"].__setitem__("lean_default_kernel", "reject"))
    add("Nanoda rejection", lambda r: r["fresh_execution"].__setitem__("nanoda", "reject"))
    add("axiom evidence drift", lambda r: r["fresh_execution"].__setitem__("theorem_axioms", "unexpected"))
    add("trust boundary failure", lambda r: r["fresh_execution"].__setitem__("trust_boundary", "unclear"))
    add("source substitution", lambda r: r["current_source"].__setitem__("sha256", "0" * 64))
    add("source byte drift", lambda r: r["current_source"].__setitem__("byte_length", 1))
    add("whole-document inflation", lambda r: r["current_source"].__setitem__("whole_document_equivalence_between_revisions", "established"))
    add("formal subject substitution", lambda r: r["formal_subject"].__setitem__("commit", "0" * 40))
    add("axiom drift", lambda r: r["permitted_axioms"].append("Classical.propComplete"))
    add("nonvacuity weakening", lambda r: r["nonvacuity"].__setitem__("state", "unknown"))
    add("source reclassification overclaim", lambda r: r["source_formal_assessment"].__setitem__("independent_source_reclassification_performed", True))
    add("decimal provenance inflation", lambda r: r["source_formal_assessment"].__setitem__("decimal_provenance", "manuscript_precision"))
    add("normalization erasure", lambda r: r["source_formal_assessment"].__setitem__("scale_normalization", "not_required"))
    add("little-o strengthening", lambda r: r["source_formal_assessment"].__setitem__("little_o", "quantitative_rate"))
    add("composite verbatim inflation", lambda r: r["source_formal_assessment"].__setitem__("composite_boundary", "single_verbatim_theorem"))
    add("whole chapter equivalence", lambda r: r["source_formal_assessment"].__setitem__("whole_chapter_equivalence", True))
    add("full proof body equivalence", lambda r: r["source_formal_assessment"].__setitem__("full_proof_body_equivalence", True))
    add("route transition", lambda r: r["state"].__setitem__("route_state", "qualified"))
    add("Cert output insertion", lambda r: r["state"].__setitem__("cert_output", {}))
    add("proof promotion", lambda r: r["state"].__setitem__("mathematical_target_proved", True))
    add("claim promotion", lambda r: r["state"].__setitem__("may_promote_claim", True))
    add("aggregate adjudication", lambda r: r["state"].__setitem__("aggregate_adjudication", True))
    add("aggregate output", lambda r: r["state"].__setitem__("aggregate_output", True))
    add("manuscript decimal attribution", lambda r: r["state"].__setitem__("manuscript_decimal_precision_attributed", True))
    add("normalization state erasure", lambda r: r["state"].__setitem__("scale_normalization_boundary_required", False))
    add("little-o state strengthening", lambda r: r["state"].__setitem__("little_o_strengthened", True))
    add("composite state inflation", lambda r: r["state"].__setitem__("composite_is_single_verbatim_source_theorem", True))
    add("other-family insertion", lambda r: r["state"].__setitem__("other_result_families_modified", True))
    add("Human Steward gate reinsertion", lambda r: r["state"].__setitem__("separate_human_steward_authorization_required", True))
    add("streamlined rule removal", lambda r: r["state"].__setitem__("routine_stage_progression_without_human_steward_intervention", False))
    add("review prepopulation", lambda r: r["publication_gate"].__setitem__("recorded_review", {"state":"APPROVED"}))
    add("review requirement removal", lambda r: r["publication_gate"].__setitem__("fresh_non_author_specialist_approval_required", False))
    add("input substitution", lambda r: r["authority"]["execution_input"].__setitem__("git_blob_sha1", "0" * 40))
    add("contract substitution", lambda r: r["authority"]["contract"].__setitem__("git_blob_sha1", "0" * 40))
    add("design substitution", lambda r: r["authority"]["design_registry"].__setitem__("git_blob_sha1", "0" * 40))
    add("registration substitution", lambda r: r["authority"]["registration"].__setitem__("route_registry_git_blob_sha1", "0" * 40))
    add("protected replay substitution", lambda r: r["authority"]["protected_replay"].__setitem__("record_git_blob_sha1", "0" * 40))
    add("Forge composite substitution", lambda r: r["authority"]["forge_composite"].__setitem__("git_blob_sha1", "0" * 40))
    add("Forge bridge substitution", lambda r: r["authority"]["forge_bridge"].__setitem__("git_blob_sha1", "0" * 40))
    add("Solve substitution", lambda r: r["authority"]["solve_handoff"].__setitem__("git_blob_sha1", "0" * 40))
    add("unknown top-level field", lambda r: r.__setitem__("unexpected", True))

    for label, value in mutations:
        errors = mod.validation_errors(value, check_repository=False)
        if not errors:
            raise AssertionError(f"mutation accepted: {label}")
    print(f"A adjudication mutation suite rejected {len(mutations)} adversarial changes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
