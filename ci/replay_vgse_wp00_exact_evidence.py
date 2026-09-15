#!/usr/bin/env python3
"""Independent exact evidence builder/checker for MC-ROUTE-VGSE-001.

This checker deliberately does not import or execute the MATHSOLVE VGSE replay.
It reconstructs the master-function critical equations from the pinned rational
arrangement and the rounded Figure 16 boundary, saturates by the arrangement
divisor over QQ(i), and independently replays the reduced graph boundary
measurement with an exact positive rational representative.

This is evidence production/replay. It does not adjudicate a MATHCERT route.
"""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Iterable

import sympy as sp

x, y, t = sp.symbols("x y t")
I = sp.I

# SOURCE-TRANSCRIBED / SOURCE-EXTRACTED INPUTS.
C = sp.Matrix([
    [1, 1, 0, -6, 0, 3],
    [0, 1, 1,  7, 0, -2],
    [0, 0, 0,  2, 1, 3],
])
ALPHAS = [
    sp.Integer(1),
    1 + x,
    x,
    -6 + 7*x + 2*y,
    y,
    3 - 2*x + 3*y,
]
DIVISOR_FACTORS_TEXT = "x*y*(x + 1)*(7*x + 2*y - 6)*(-2*x + 3*y + 3)"
BOUNDARY = [
    (sp.Rational(0), sp.Rational(0)),
    (sp.Rational(595245, 10**6), sp.Rational(-39685532, 10**6)),
    (sp.Rational(34923126, 10**6), sp.Rational(-39288589, 10**6)),
    (sp.Rational(69251343, 10**6), sp.Rational(-38693344, 10**6)),
    (sp.Rational(68854401, 10**6), sp.Rational(992180, 10**6)),
    (sp.Rational(34129578, 10**6), sp.Rational(20239700, 10**6)),
]

# RECONSTRUCTED GRAPH TOPOLOGY, checked independently below.
COLORS = {
    "F01": "white", "F02": "black", "F03": "white", "F04": "black",
    "F05": "white", "F06": "black", "F07": "white", "F08": "black",
}
INTERNAL_EDGES = [
    ("F01", "F04"), ("F01", "F02"), ("F07", "F02"), ("F03", "F06"),
    ("F03", "F04"), ("F03", "F08"), ("F07", "F04"), ("F05", "F04"),
    ("F05", "F06"), ("F07", "F08"),
]
BOUNDARY_OWNERS = ["F07", "F02", "F01", "F05", "F06", "F08"]
EXACT_WEIGHTS = {
    "F01|F04": sp.Rational(1), "F01|F02": sp.Rational(1),
    "F07|F02": sp.Rational(1), "F03|F06": sp.Rational(1),
    "F03|F04": sp.Rational(2, 7), "F03|F08": sp.Rational(25, 7),
    "F07|F04": sp.Rational(6, 7), "F05|F04": sp.Rational(3, 25),
    "F05|F06": sp.Rational(2, 25), "F07|F08": sp.Rational(9, 7),
    "B1": sp.Rational(1), "B2": sp.Rational(1), "B3": sp.Rational(1),
    "B4": sp.Rational(1), "B5": sp.Rational(1), "B6": sp.Rational(1),
}

SOURCE_IDENTITIES = {
    "forge_provider_manifest_blob_sha1": "9cb5ac2d92b458f7f63e8a9811448f245a151ddd",
    "forge_source_concordance_blob_sha1": "6685cd1b0ed4d759f7447fce4b217ef8a59f0f93",
    "author_pdf_sha256": "e513789426ae6247438920bfc80cfba6bd9c32dc6799a4f7873d806a865f95de",
    "arxiv_v2_pdf_sha256": "f5aefb71dd0d662679e85cd0c7f96d1bbbc029a6b5cd2f1cfaa06286cc718e34",
    "normalized_text_sha256": "74d58d4465166fc5035e5064a2c1cabc8b0f1e62cdcf82f7b41c6af65492cba4",
}

def canonical(expr: sp.Expr) -> str:
    return sp.sstr(sp.cancel(expr))

def gaussian_l1(z: sp.Expr) -> sp.Rational:
    z = sp.cancel(z)
    return sp.Rational(abs(sp.re(z))) + sp.Rational(abs(sp.im(z)))

def arrangement_certificate() -> dict:
    lines = [
        (sp.Rational(1), sp.Rational(0), sp.Rational(1)),
        (sp.Rational(1), sp.Rational(0), sp.Rational(0)),
        (sp.Rational(7), sp.Rational(2), sp.Rational(-6)),
        (sp.Rational(0), sp.Rational(1), sp.Rational(0)),
        (sp.Rational(-2), sp.Rational(3), sp.Rational(3)),
    ]
    intersections: dict[tuple[sp.Rational, sp.Rational], list[tuple[int, int]]] = {}
    parallel: list[list[int]] = []
    for i in range(len(lines)):
        a,b,c = lines[i]
        for j in range(i+1, len(lines)):
            A,B,C0 = lines[j]
            det = a*B - A*b
            if det == 0:
                parallel.append([i+2, j+2])
                continue
            px = sp.cancel((b*C0 - B*c) / det)
            py = sp.cancel((c*A - C0*a) / det)
            intersections.setdefault((px, py), []).append((i,j))
    assert parallel == [[2,3]]
    assert len(intersections) == 9
    assert all(len(pairs) == 1 for pairs in intersections.values())
    beta = 1 - len(lines) + len(intersections)
    assert beta == 5
    return {
        "bounded_region_count_beta": beta,
        "finite_line_count": len(lines),
        "distinct_finite_intersections": len(intersections),
        "parallel_source_alpha_pairs": parallel,
        "finite_triple_intersection": False,
        "method": "exact_rank_two_affine_arrangement_count_1_minus_n_plus_intersections",
    }

def master_equations() -> tuple[sp.Expr, sp.Expr, sp.Expr]:
    edges = []
    for i in range(6):
        cx, cy = BOUNDARY[i]
        px, py = BOUNDARY[i-1]
        edges.append((cx-px) + I*(cy-py))
    divisor = sp.expand(sp.prod(ALPHAS))
    assert sp.expand(sp.sympify(DIVISOR_FACTORS_TEXT, locals={"x": x, "y": y})) == divisor
    ex = sum(edges[i] * sp.diff(ALPHAS[i], x) / ALPHAS[i] for i in range(6))
    ey = sum(edges[i] * sp.diff(ALPHAS[i], y) / ALPHAS[i] for i in range(6))
    nx = sp.Poly(sp.cancel(ex*divisor), x, y, domain=sp.QQ_I).as_expr()
    ny = sp.Poly(sp.cancel(ey*divisor), x, y, domain=sp.QQ_I).as_expr()
    return nx, ny, divisor

def exact_algebraic_certificate() -> dict:
    nx, ny, divisor = master_equations()
    g = sp.groebner([nx, ny, 1-t*divisor], t, y, x, order="lex", domain=sp.QQ_I)
    assert len(g.polys) == 3
    basis = [p.as_expr() for p in g.polys]
    x_only = [b for b in basis if not b.has(t) and not b.has(y)]
    y_linear = [b for b in basis if not b.has(t) and sp.Poly(b, y).degree() == 1]
    assert len(x_only) == 1 and len(y_linear) == 1
    q = sp.Poly(x_only[0], x, domain=sp.QQ_I).monic()
    rel = sp.Poly(y_linear[0], y, x, domain=sp.QQ_I)
    lc_y = rel.coeff_monomial(y)
    assert lc_y != 0
    p_expr = sp.cancel(-sp.Poly(rel.as_expr().subs(y,0), x, domain=sp.QQ_I).as_expr()/lc_y)
    assert q.degree() == 5
    assert sp.gcd(q, q.diff()).degree() == 0
    tri = sp.groebner([y-p_expr, q.as_expr()], y, x, order="lex", domain=sp.QQ_I)
    assert tri.reduce(nx)[1] == 0
    assert tri.reduce(ny)[1] == 0
    divisor_checks = {}
    substituted = []
    for idx, alpha in enumerate(ALPHAS, 1):
        h = sp.Poly(sp.cancel(alpha.subs(y,p_expr)), x, domain=sp.QQ_I)
        gg = sp.gcd(q, h)
        assert gg.degree() == 0
        divisor_checks[f"alpha_{idx}"] = {"gcd_degree": gg.degree(), "gcd": canonical(gg.monic().as_expr())}
        substituted.append(h)
    q_coeffs = q.all_coeffs()
    assert q_coeffs[0] == 1
    radius = sp.Rational(1) + max(gaussian_l1(c) for c in q_coeffs[1:])
    disc = sp.cancel(sp.discriminant(q.as_expr(), x))
    disc_component_lower = max(abs(sp.re(disc)), abs(sp.im(disc)))
    separation_threshold = sp.Rational(1, 10**12)
    assert disc_component_lower > separation_threshold**2 * (2*radius)**18
    denominator_lowers = {}
    for idx, h in enumerate(substituted, 1):
        if h.degree() == 0:
            lower = gaussian_l1(h.all_coeffs()[0])
        else:
            res = sp.cancel(sp.resultant(q.as_expr(), h.as_expr(), x))
            res_lower = max(abs(sp.re(res)), abs(sp.im(res)))
            assert res_lower > 0
            coeffs = h.all_coeffs()
            degree = h.degree()
            H = sum(gaussian_l1(c) * radius**(degree-k) for k,c in enumerate(coeffs))
            lower = sp.cancel(res_lower / H**4)
        denominator_lowers[f"alpha_{idx}"] = canonical(lower)
    common_denominator_threshold = sp.Rational(8, 10**22)
    for idx in range(1,7):
        lower = sp.Rational(denominator_lowers[f"alpha_{idx}"])
        assert lower > common_denominator_threshold
    return {
        "equation_reconstruction": {
            "coefficient_domain": "QQ(i)",
            "boundary_precision": "exact_rationals_from_source_vector_coordinates_rounded_to_1e-6_pdf_point",
            "critical_numerator_x": canonical(nx),
            "critical_numerator_y": canonical(ny),
            "arrangement_divisor": DIVISOR_FACTORS_TEXT,
        },
        "saturation": {
            "construction": "<Nx,Ny,1-t*D> intersect QQ(i)[x,y]",
            "groebner_order": "lex(t,y,x)",
            "extended_groebner_basis": [canonical(b) for b in basis],
            "triangular_y_relation": canonical(y-p_expr),
            "quintic_monic": canonical(q.as_expr()),
            "quotient_ring_basis": ["1","x","x^2","x^3","x^4"],
            "quotient_ring_dimension": 5,
            "quintic_degree": q.degree(),
            "quintic_squarefree": True,
            "exact_equation_remainders_zero": True,
        },
        "divisor_exclusion": divisor_checks,
        "certified_bounds": {
            "root_radius_upper": canonical(radius),
            "root_separation_lower": "1/1000000000000",
            "root_separation_proof": "discriminant_lower_component_vs_Cauchy_radius_product_bound",
            "common_arrangement_denominator_lower": "1/1250000000000000000000",
            "individual_arrangement_denominator_lowers": denominator_lowers,
            "residual": "exact_zero_in_quotient_ring",
        },
        "conclusion": {
            "isolated_solution_count": 5,
            "all_solutions_away_from_arrangement_divisor": True,
            "all_x_roots_distinct": True,
            "unique_y_for_each_x": True,
        },
    }

def build_graph():
    colors = dict(COLORS)
    edges = []
    for left,right in INTERNAL_EDGES:
        white = left if colors[left] == "white" else right
        black = right if white == left else left
        edges.append((white, black, f"{left}|{right}"))
    for idx, owner in enumerate(BOUNDARY_OWNERS, 1):
        u = f"U{idx}"
        colors[u] = "black" if colors[owner] == "white" else "white"
        white = owner if colors[owner] == "white" else u
        black = u if colors[owner] == "white" else owner
        edges.append((white, black, f"B{idx}"))
    return colors, edges

def enumerate_matchings(colors, edges):
    interior = sorted(v for v in colors if not v.startswith("U"))
    incident = {v:[i for i,e in enumerate(edges) if v in e[:2]] for v in colors}
    selected = []
    def rec(covered, chosen, used_boundary):
        if len(covered) == len(interior):
            selected.append(tuple(chosen)); return
        vertex = next(v for v in interior if v not in covered)
        for ei in incident[vertex]:
            w,b,_ = edges[ei]
            other = b if vertex == w else w
            if other in interior and other in covered: continue
            if other.startswith("U") and other in used_boundary: continue
            nc=set(covered); nc.add(vertex)
            nb=set(used_boundary)
            if other in interior: nc.add(other)
            else: nb.add(other)
            rec(nc, chosen+[ei], nb)
    rec(set(), [], set())
    out=[]
    for matching in selected:
        used={v for ei in matching for v in edges[ei][:2] if v.startswith("U")}
        boundary=[]
        for idx in range(1,7):
            u=f"U{idx}"
            if ((colors[u]=="black" and u in used) or (colors[u]=="white" and u not in used)):
                boundary.append(idx)
        out.append((tuple(boundary), matching))
    return out

def graph_certificate() -> dict:
    import itertools
    colors, edges = build_graph()
    records=enumerate_matchings(colors, edges)
    assert len(records)==31
    minors=defaultdict(lambda: sp.Rational(0))
    multiplicities=defaultdict(int)
    for boundary, matching in records:
        minors[boundary] += sp.prod(EXACT_WEIGHTS[edges[i][2]] for i in matching)
        multiplicities[boundary] += 1
    targets={}
    for cols in itertools.combinations(range(6),3):
        d=sp.det(C[:, cols])
        if d:
            targets[tuple(c+1 for c in cols)] = abs(sp.Integer(d))
    assert set(minors)==set(targets)
    scales={sp.cancel(minors[k]/targets[k]) for k in targets}
    assert scales == {sp.Rational(1,7)}
    assert all(w>0 for w in EXACT_WEIGHTS.values())
    return {
        "positive_exact_weights": {k: canonical(v) for k,v in EXACT_WEIGHTS.items()},
        "almost_perfect_matching_count": len(records),
        "nonzero_plucker_count": len(minors),
        "common_scale": "1/7",
        "target_plucker_coordinates": {"".join(map(str,k)): int(targets[k]) for k in sorted(targets)},
        "measured_plucker_coordinates": {"".join(map(str,k)): canonical(minors[k]) for k in sorted(minors)},
        "matching_multiplicities": {"".join(map(str,k)): multiplicities[k] for k in sorted(multiplicities)},
        "support_exact": True,
        "all_weights_strictly_positive": True,
    }

def build_evidence() -> dict:
    return {
        "schema_version": "1.0.0",
        "evidence_id": "MC-VGSE-WP00-CERT-001-EXACT-ALGEBRAIC-GRAPH-001",
        "route_id": "MC-ROUTE-VGSE-001",
        "campaign_id": "VGSE-001",
        "workset_id": "VGSE-WP00-CERT-001",
        "claims_addressed": ["VGSE-C00","VGSE-C01","VGSE-C04"],
        "source_identities": SOURCE_IDENTITIES,
        "independence": {
            "solve_code_imported_or_executed": False,
            "solve_numerical_roots_consumed": False,
            "solve_numerical_weights_consumed": False,
            "method": "fresh_exact_reconstruction_from_transcribed_arrangement_rounded_source_boundary_and_graph_incidence",
            "external_backend": {"name":"SymPy","version":sp.__version__},
        },
        "hypothesis_audit": {
            "recorded_arrangement_rank": 2,
            "projective_chart": "a=(1,x,y)",
            "arrangement_divisor_saturated_explicitly": True,
            "critical_count_route": "direct_exact_saturated_ideal_computation",
            "genericity_theorem_dependency_for_recorded_count": False,
            "note": "The recorded-instance count is established directly; this evidence does not promote a general OT95/Proposition B.2 theorem-chain hypothesis audit.",
        },
        "VGSE-C00": arrangement_certificate(),
        "VGSE-C01": exact_algebraic_certificate(),
        "VGSE-C04": graph_certificate(),
        "trust": {
            "modality": "COMPUTER_ALGEBRA_CERTIFICATE_WITH_REPLAY",
            "trust_boundary": "script_replayed_exact_arithmetic",
            "adjudication_effect": "none",
            "may_adjudicate_after_this_record_alone": False,
            "certificate_output": None,
        },
        "scope_exclusions": [
            "VGSE-C05 and VGSE-C06 are not discharged by this record",
            "continuous rigid foldability", "collision freedom", "finite thickness",
            "manufacturability", "product performance", "novelty", "priority",
            "patentability", "commercial value",
        ],
    }

def main() -> int:
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    parser.add_argument("--check", type=Path)
    args=parser.parse_args()
    evidence=build_evidence()
    text=json.dumps(evidence, sort_keys=True, indent=2)+"\n"
    if args.write:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(text, encoding="utf-8")
    if args.check:
        actual=args.check.read_text(encoding="utf-8")
        if actual != text:
            print("VGSE exact evidence record does not match independent replay")
            return 1
    print("VGSE exact replay: C00 beta=5; C01 saturated quotient dimension=5 with divisor exclusion; C04 exact positive boundary measurement scale=1/7")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
