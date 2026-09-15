#!/usr/bin/env python3
"""Source-fixture binding for VGSE-C05 and negative audit for VGSE-C06.

This replay binds the independently reconstructed planar cellulation to the exact
protected Figure 16 source-vector fixture identity.  It also tests the narrowest
well-defined generated-to-source relation available from the protected records:
label-preserving identity in the common boundary coordinate gauge.

It deliberately does not invent the undeclared geometric equivalence group named
by VGSE-C06.  Failure of the identity-gauge test is therefore not a refutation
under a broader, future, explicitly declared group.
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import sys
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


planar = load("vgse_planar_source_audit", ROOT / "ci" / "replay_vgse_wp00_planar_evidence.py")
base = planar.base

SOURCE_FIXTURE = {
    "repository": "grandchallenge/MATHSOLVE",
    "protected_ref": "e6ec267cf5de910d2cb827008c66d10f31fe92c6",
    "path": "work_packages/VGSE_WP00/artifacts/data/figure16_source_vectors.json",
    "git_blob_sha1": "8449555b71a38670374f172edd549385c3dda47d",
    "fixture_id": "VGSE-FIG16-SOURCE-VECTOR-001",
    "pdf_sha256": "e513789426ae6247438920bfc80cfba6bd9c32dc6799a4f7873d806a865f95de",
    "evidence_class": "SOURCE_VECTOR_GEOMETRY_REPLICATION",
    "not_an_independent_algebraic_to_geometry_reconstruction": True,
}

CLAIM_LEDGER = {
    "repository": "grandchallenge/MATHSOLVE",
    "protected_ref": "e6ec267cf5de910d2cb827008c66d10f31fe92c6",
    "path": "work_packages/VGSE_WP00/claim_ledger.json",
    "git_blob_sha1": "a5d9edb3697bfbb5fe26b8dacbda4b2a2debb69f",
}

CERT_HANDOFF = {
    "repository": "grandchallenge/MATHSOLVE",
    "protected_ref": "e6ec267cf5de910d2cb827008c66d10f31fe92c6",
    "path": "cert_handoffs/VGSE-001.json",
    "git_blob_sha1": "42cfa84978fd63c75f074b388afd8b1fcbd56091",
}


def q(s: str) -> F:
    return F(s)


# Exact decimal coordinates copied from the exact protected source-vector blob
# identified above.  Pattern-1 is sufficient to bind the reconstructed labeled
# cellulation.  All five source interiors are used by the C06 identity-gauge audit.
SOURCE_PATTERNS = [
    {
        "pattern_id": "FIG16-01",
        "boundary": [(q("0"), q("0")), (q("34.129578"), q("20.2397")), (q("68.854401"), q("0.99218")), (q("69.251343"), q("-38.693344")), (q("34.923126"), q("-39.288589")), (q("0.595245"), q("-39.685532"))],
        "A": (q("26.192261"), q("2.976288")),
        "D": (q("36.113647"), q("14.485123")),
        "C": (q("43.25705"), q("-33.732651")),
    },
    {
        "pattern_id": "FIG16-02",
        "A": (q("21.231567"), q("2.182709")),
        "D": (q("29.76413"), q("12.50103")),
        "C": (q("60.123535"), q("-2.777977")),
    },
    {
        "pattern_id": "FIG16-03",
        "A": (q("13.889862"), q("-32.145195")),
        "D": (q("28.176666"), q("-1.389145")),
        "C": (q("62.306244"), q("-5.357643")),
    },
    {
        "pattern_id": "FIG16-04",
        "A": (q("8.929169"), q("-31.946884")),
        "D": (q("44.64621"), q("6.349823")),
        "C": (q("42.46347"), q("-35.518417")),
    },
    {
        "pattern_id": "FIG16-05",
        "A": (q("4.563721"), q("-20.041092")),
        "D": (q("28.970245"), q("-23.612946")),
        "C": (q("36.312256"), q("-36.312302")),
    },
]

SOURCE_PATTERN1_FACE_CYCLES = {
    "F01": [planar.A, planar.P2, planar.P1],
    "F02": [planar.P0, planar.A, planar.P1],
    "F03": [planar.P4, planar.C, planar.D],
    "F04": [planar.A, planar.D, planar.C, planar.P2],
    "F05": [planar.P2, planar.C, planar.P3],
    "F06": [planar.P3, planar.C, planar.P4],
    "F07": [planar.A, planar.P0, planar.P5, planar.D],
    "F08": [planar.P4, planar.D, planar.P5],
}


def source_binding() -> dict:
    source_boundary = SOURCE_PATTERNS[0]["boundary"]
    # The cert replay uses the same polygon with opposite traversal, anchored at P0.
    cert_order = [source_boundary[i] for i in (0, 5, 4, 3, 2, 1)]
    replay_boundary = [(F(int(u.p), int(u.q)), F(int(v.p), int(v.q))) for u, v in base.BOUNDARY]
    assert replay_boundary == cert_order
    assert planar.FACES == SOURCE_PATTERN1_FACE_CYCLES
    return {
        "source_fixture": SOURCE_FIXTURE,
        "pattern_id": "FIG16-01",
        "boundary_reindex_source_1_based": [1, 6, 5, 4, 3, 2],
        "boundary_coordinates_exactly_bound": True,
        "face_cycles_exactly_bound": True,
        "face_cycles": SOURCE_PATTERN1_FACE_CYCLES,
        "interpretation": "The C05 reconstructed cellulation is explicitly bound to the labeled topology and boundary coordinates extracted in the pinned protected source-vector fixture.",
    }


def interval_distance_lower(iv, value: F) -> F:
    if value < iv.lo:
        return iv.lo - value
    if value > iv.hi:
        return value - iv.hi
    return F(0)


def pair_identity_mismatch_lower(generated: dict, source: dict) -> F:
    distances = []
    for label in (planar.A, planar.D, planar.C):
        sx, sy = source[label]
        distances.append(interval_distance_lower(generated[label].re, sx))
        distances.append(interval_distance_lower(generated[label].im, sy))
    return max(distances)


def identity_gauge_audit() -> dict:
    qpoly, pexpr, tri = planar.saturated()
    px, _ = planar.exact_positions(qpoly, pexpr, tri)
    generated = []
    for center in planar.CENTERS:
        box = planar.root_box(qpoly, center)
        generated.append({label: planar.eval_ci(px[label], box) for label in (planar.A, planar.D, planar.C)})

    mismatch = [[pair_identity_mismatch_lower(g, s) for s in SOURCE_PATTERNS] for g in generated]
    best_bottleneck = None
    for perm in itertools.permutations(range(5)):
        bottleneck = max(mismatch[i][perm[i]] for i in range(5))
        if best_bottleneck is None or bottleneck < best_bottleneck:
            best_bottleneck = bottleneck
    assert best_bottleneck is not None

    # This threshold is deliberately far weaker than the observed separation and
    # still three orders of magnitude larger than the 1e-6 source-vector rounding.
    threshold = F(1, 1000)
    assert best_bottleneck > threshold
    return {
        "relation_tested": "label_preserving_identity_in_common_boundary_coordinate_gauge",
        "generated_branches": 5,
        "source_patterns": 5,
        "bijections_exhausted": 120,
        "source_coordinate_rounding": "1/1000000 PDF point",
        "best_bijection_linf_coordinate_mismatch_lower_bound_gt": "1/1000 PDF point",
        "identity_gauge_match_at_source_precision": False,
        "meaning": "No bijection can identify the five generated embeddings with the five rounded source drawings by labeled coordinate identity at source precision.",
    }


def build_evidence() -> dict:
    return {
        "schema_version": "1.0.0",
        "evidence_id": "MC-VGSE-WP00-CERT-001-SOURCE-EQUIVALENCE-AUDIT-001",
        "route_id": "MC-ROUTE-VGSE-001",
        "campaign_id": "VGSE-001",
        "workset_id": "VGSE-WP00-CERT-001",
        "claims_addressed": ["VGSE-C05", "VGSE-C06"],
        "c05_source_binding": source_binding(),
        "c06_authority": {
            "claim_ledger": CLAIM_LEDGER,
            "cert_handoff": CERT_HANDOFF,
            "ledger_support_route": "NONE",
            "ledger_blocker": "A permutation-and-equivalence matcher between generated coordinates and the rounded source drawings has not been admitted.",
            "handoff_required_input": "A generated-to-source equivalence record with the declared equivalence group.",
            "equivalence_group_definition_in_pinned_records": None,
        },
        "c06_narrow_relation_audit": identity_gauge_audit(),
        "c06_outcome": {
            "state": "BLOCKED_MISSING_EQUIVALENCE_DEFINITION",
            "identity_gauge_relation_refuted_at_source_precision": True,
            "broader_geometric_equivalence_assessed": False,
            "claim_refuted_under_undeclared_future_group": False,
            "may_certify_c06": False,
            "required_reopening_input": "An explicit, source-faithful geometric equivalence group and matcher contract admitted on an exact protected revision.",
        },
        "trust": {
            "modality": "SEMANTIC_REPLAY_PLUS_INTERVAL_NEGATIVE_AUDIT",
            "trust_boundary": "pinned_source_fixture_identity_plus_exact_interval_replay",
            "adjudication_effect": "none",
            "may_adjudicate_after_this_record_alone": False,
            "certificate_output": None,
        },
        "scope_exclusions": [
            "No undeclared geometric transformation group is inferred or invented.",
            "No rigid foldability, collision freedom, finite thickness, manufacturability, product, novelty, priority, patentability, or commercial inference is authorized.",
        ],
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    text = json.dumps(build_evidence(), indent=2, sort_keys=True) + "\n"
    if args.write:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(text, encoding="utf-8")
    if args.check and args.check.read_text(encoding="utf-8") != text:
        print("VGSE source/equivalence audit record does not match replay")
        return 1
    print("VGSE source audit: C05 fixture-bound; C06 identity gauge fails at source precision; broader equivalence remains undefined and blocked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
