#!/usr/bin/env python3
"""Independent interval replay of the VGSE-C05 source-definition TE3 condition.

This checker consumes only MATHCERT's own exact/interval C05 replay. It does not
import MATHSOLVE, numerical generated embeddings, or the WP05/WP06 artefacts.

For the exact C04 representative B1=B2=F07|F02=1, source TE3 plus boundary
gauge g(U_i)=1 forces

    |A-P0| = |P0-P5| |P0-P1|,

where A is the dual vertex shared by F07/F02 and P0P5, P0P1 are the two
corresponding boundary dual edges. We certify the squared ratio is < 1/1000 on
all five C05 root boxes, whereas TE3 requires it to equal 1.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from fractions import Fraction as F
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

spec = importlib.util.spec_from_file_location(
    "vgse_planar_te3_base", ROOT / "ci" / "replay_vgse_wp00_planar_evidence.py"
)
assert spec and spec.loader
planar = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = planar
spec.loader.exec_module(planar)


def norm2(z: Any):
    return planar.sq(z.re) + planar.sq(z.im)


def exact_boundary_point(index: int):
    x, y = planar.base.BOUNDARY[index]
    return planar.CI.p(F(int(x.p), int(x.q)), F(int(y.p), int(y.q)))


def frac_text(v: F) -> str:
    return str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}"


def interval_record(iv: Any) -> dict[str, str]:
    return {"lo": frac_text(iv.lo), "hi": frac_text(iv.hi)}


def build_evidence() -> dict[str, Any]:
    q, p, tri = planar.saturated()
    px, _ = planar.exact_positions(q, p, tri)

    p0 = exact_boundary_point(0)
    p1 = exact_boundary_point(1)
    p5 = exact_boundary_point(5)
    boundary_denominator = norm2(p0 - p5) * norm2(p0 - p1)
    assert boundary_denominator.lo == boundary_denominator.hi
    assert boundary_denominator.lo > 0

    threshold = F(1, 1000)
    branches = []
    for index, center in enumerate(planar.CENTERS, start=1):
        zbox = planar.root_box(q, center)
        apos = planar.eval_ci(px[planar.A], zbox)
        ratio2 = norm2(apos - p0) / boundary_denominator
        # Source TE3 requires ratio2 == 1. The following strict separation is
        # deliberately much stronger than merely excluding 1.
        assert ratio2.hi < threshold
        branches.append(
            {
                "pattern_index": index,
                "certified_squared_te3_ratio_strict_upper_bound": "1/1000",
                "te3_required_squared_ratio": "1",
                "te3_excluded": True,
            }
        )

    return {
        "schema_version": "1.0.0",
        "evidence_id": "MC-VGSE-WP00-CERT-001-TE3-CONFORMANCE-AUDIT-001",
        "campaign_id": "VGSE-001",
        "workset_id": "VGSE-WP00-CERT-001",
        "claim_id": "VGSE-C05",
        "audit_target": "source-definition TE3 conformance of the five retained C05 embeddings to the protected exact C04 weight class",
        "source_provenance": {
            "repository": "grandchallenge/MATHFORGE",
            "provider_merge_commit": "593afd971a53ca0285f8b94570997ed7c3d7c170",
            "provider_manifest_git_blob_sha1": "9cb5ac2d92b458f7f63e8a9811448f245a151ddd",
            "source_concordance_git_blob_sha1": "6685cd1b0ed4d759f7447fce4b217ef8a59f0f93",
            "arxiv_id": "2410.09574v2",
            "title": "Amplituhedra and origami, I: tree level",
            "author": "Pavel Galashin",
            "author_pdf_sha256": "e513789426ae6247438920bfc80cfba6bd9c32dc6799a4f7873d806a865f95de",
            "arxiv_v2_pdf_sha256": "f5aefb71dd0d662679e85cd0c7f96d1bbbc029a6b5cd2f1cfaa06286cc718e34",
            "definition_refs": {
                "geometric_edge_weights": "Section 1.2, equation (1.5)",
                "boundary_fixed_gauge_equivalence": "Section 1.2, paragraph immediately following equation (1.5)",
                "te3": "Definition 1.2, condition (TE3)",
            },
        },
        "source_semantics": {
            "geometric_edge_weight": "Euclidean length of the corresponding dual embedding edge",
            "gauge_equivalence": "wt'(e)=g(w) wt(e) g(b), with g=1 at every boundary vertex",
            "te3": "graph weights and Euclidean geometric edge weights must be gauge equivalent",
        },
        "protected_weight_identity": {
            "B1": "1",
            "B2": "1",
            "F07|F02": "1",
        },
        "derived_te3_identity": "|A-P0| = |P0-P5| * |P0-P1|",
        "certified_form": "|A-P0|^2 / (|P0-P5|^2 |P0-P1|^2) = 1",
        "method": {
            "position_source": "exact rational-function position expressions from replay_vgse_wp00_planar_evidence.py",
            "root_source": "five independently interval-certified complex Krawczyk root boxes from MATHCERT",
            "arithmetic": "exact Fraction endpoint complex interval arithmetic",
            "solve_code_imported_or_executed": False,
            "solve_numerical_embeddings_consumed": False,
            "programme_wp06_numerical_coordinates_consumed": False,
        },
        "branches": branches,
        "conclusion": {
            "all_five_branches_exclude_te3": True,
            "maximum_certified_squared_ratio_strictly_below": "1/1000",
            "te3_required_squared_ratio": "1",
            "disposition": "TE3_FAILS_FOR_PROTECTED_C04_WEIGHT_CLASS_ON_ALL_FIVE_RETAINED_C05_BRANCHES",
            "terminology_effect": "Current C05 evidence does not support calling these five objects t-embeddings of the protected C04 weighted graph under the source TE3 definition.",
        },
        "trust": {
            "modality": "INTERVAL_CERTIFICATE_PLUS_EXACT_SYMBOLIC_REPLAY",
            "adjudication_effect": "none_pending_review_and_human_steward_disposition",
            "may_promote_or_rewrite_claim_after_this_record_alone": False,
        },
        "scope_exclusions": [
            "This audit does not invalidate the independently certified primitive closure, prescribed boundary, convexity, noncrossing, Kawasaki, or boundary-angle properties.",
            "VGSE-C06 remains excluded.",
            "continuous rigid foldability",
            "collision freedom",
            "finite thickness",
            "manufacturability",
            "product performance",
            "patentability",
            "commercial value",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()

    text = json.dumps(build_evidence(), indent=2, sort_keys=True) + "\n"
    if args.write:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(text, encoding="utf-8")
    if args.check:
        expected = json.loads(args.check.read_text(encoding="utf-8"))
        actual = json.loads(text)
        if expected != actual:
            print("VGSE C05 TE3 conformance evidence does not match replay")
            return 1
    print("VGSE C05 TE3 replay: all five certified root boxes exclude source TE3 by squared ratio < 1/1000")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
