#!/usr/bin/env python3
"""Replay the content-addressed VGSE-C06 producer-evidence binding.

This checker does not reimplement the MATHSOLVE boundary-measurement algorithm.
It deterministically binds the protected producer merge, script, evidence record,
source fixture, and bounded interpretation into MATHCERT.  It creates no
adjudication or certificate-output authority.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def build_record() -> dict:
    return {
        "schema_version": "1.0.0",
        "evidence_id": "MC-VGSE-WP00-CERT-001-C06-PRODUCER-BINDING-001",
        "route_id": "MC-ROUTE-VGSE-001",
        "campaign_id": "VGSE-001",
        "workset_id": "VGSE-WP00-CERT-001",
        "claims_addressed": ["VGSE-C06"],
        "predecessor_cert_evidence": {
            "repository": "grandchallenge/MATHCERT",
            "protected_merge": "53f198261d5b776d55aca9e704945054cd4407f5",
            "path": "evidence/vgse/VGSE-WP00-CERT-001-source-equivalence-audit.json",
            "git_blob_sha1": "062389091eb1104a3598cfcded786f6cc34ca336",
            "predecessor_state": "BLOCKED_MISSING_EQUIVALENCE_DEFINITION",
        },
        "producer_evidence": {
            "repository": "grandchallenge/MATHSOLVE",
            "tracker_issue": "https://github.com/grandchallenge/MATHSOLVE/issues/239",
            "pull_request": "https://github.com/grandchallenge/MATHSOLVE/pull/240",
            "exact_candidate_head": "303ddc5b794289f1ad800e57e08521c86ad9b1c3",
            "protected_merge": "c8e81d262d4da1a36b312f017443777a4c7888db",
            "protected_main_readback": True,
            "source_fixture": {
                "path": "work_packages/VGSE_WP00/artifacts/data/figure16_source_vectors.json",
                "git_blob_sha1": "8449555b71a38670374f172edd549385c3dda47d",
                "fixture_id": "VGSE-FIG16-SOURCE-VECTOR-001",
            },
            "replay_script": {
                "path": "work_packages/VGSE_WP00/artifacts/code/audit_figure16_pinned_c.py",
                "git_blob_sha1": "177effe7f42f8dd8987c34e816ea99e4a8160d4e4",
            },
            "evidence_record": {
                "path": "work_packages/VGSE_WP00/artifacts/data/figure16_pinned_c_measurement_audit.json",
                "git_blob_sha1": "97f2834d57d8ac9d60544d0f2498aa527aa72422",
                "audit_id": "VGSE-FIG16-PINNED-C-MEASUREMENT-AUDIT-001",
            },
        },
        "producer_result": {
            "source_pattern_count": 5,
            "almost_perfect_matching_count_each": 31,
            "nonzero_plucker_count": 19,
            "boundary_relabelings_exhausted": 720,
            "global_color_complement_conventions_tested": 2,
            "minimum_observed_best_projective_distortion_factor": 131.50098551816274,
            "certified_rounding_robust_lower_bound": 131.50058917470795,
            "required_lower_threshold": 100.0,
            "visible_reconstructed_geometric_weight_class_measures_pinned_C": False,
            "failure_survives_all_boundary_relabelings_and_global_color_complement": True,
        },
        "cert_interpretation": {
            "c04_admitted_evidence_status": "UNCHANGED",
            "c05_admitted_evidence_status": "UNCHANGED",
            "c06_state": "BLOCKED_VISIBLE_GEOMETRIC_WEIGHT_BRIDGE_TO_PINNED_C",
            "meaning": "The admitted C04 evidence remains an exact statement that the reconstructed reduced graph admits a positive weight representative measuring pinned C. The protected producer audit separately shows that the Euclidean geometric weights read from the committed visible Figure 16 drawings are not that measurement class. Therefore the missing generated-to-source bridge is upstream of C06 and remains unresolved.",
            "required_reopening_input": "Exact source graph/weight-generation data establishing the Figure 16-to-pinned-C bridge, or a separately governed source-authorized correspondence whose exact source locus and action are declared before matcher execution.",
            "historical_solve_handoff_rewritten": False,
            "post_hoc_equivalence_broadening_authorized": False,
        },
        "trust": {
            "binding_kind": "CONTENT_ADDRESSED_PRODUCER_EVIDENCE_BINDING",
            "independent_mathcert_replay_of_producer_algorithm": False,
            "adjudication_effect": "none",
            "may_adjudicate_after_this_record_alone": False,
            "certificate_output": None,
            "mathematical_target_proved": False,
        },
        "scope_exclusions": [
            "This binding does not refute the source paper or identify the exact undisclosed source graph/weight-generation data.",
            "No undeclared geometric equivalence relation is inferred from the failed visible-graph bridge.",
            "No rigid foldability, collision freedom, finite thickness, manufacturability, novelty, priority, patentability, product, or commercial inference is authorized.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    text = json.dumps(build_record(), indent=2, sort_keys=True) + "\n"
    if args.write:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(text, encoding="utf-8")
    if args.check and args.check.read_text(encoding="utf-8") != text:
        print("VGSE C06 producer-evidence binding does not match replay")
        return 1
    if not args.write and not args.check:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
