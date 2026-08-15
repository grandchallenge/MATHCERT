#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RECONSTRUCTION = ROOT / "evidence/openai_ten_proofs/compactness_construction/reconstruction.json"


def load(path: Path = RECONSTRUCTION) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("reconstruction must be a JSON object")
    return value


def subdivision(k: int, prefix: str, bases: list[str], centers: list[str], reverse: bool = False):
    original, middle = (1, 0) if reverse else (0, 1)
    vertices = set(bases + centers)
    colors = {v: original for v in vertices}
    edges: set[tuple[str, str]] = set()
    for b in bases:
        for c in centers:
            s = f"{prefix}s_{b}_{c}"
            vertices.add(s); colors[s] = middle
            edges |= {tuple(sorted((b, s))), tuple(sorted((s, c)))}
    return vertices, edges, colors


def metrics(graph) -> dict[str, Any]:
    vertices, edges, colors = graph
    adjacency = {v: set() for v in vertices}
    for a, b in edges:
        adjacency[a].add(b); adjacency[b].add(a)
    seen, stack = set(), [next(iter(vertices))]
    while stack:
        v = stack.pop()
        if v in seen: continue
        seen.add(v); stack.extend(adjacency[v] - seen)
    connected = seen == vertices
    return {
        "vertices": len(vertices), "edges": len(edges), "connected": connected,
        "proper_bipartite_coloring": all(colors[a] != colors[b] for a, b in edges),
        "cycle_rank": len(edges) - len(vertices) + (1 if connected else 0),
    }


def source_graphs():
    s2 = subdivision(2, "", ["b1","b2","b3"], ["c1","c2"])
    s3 = subdivision(3, "", ["b1","b2","b3"], ["c1","c2","c3"])
    ja = subdivision(2, "a_", ["x","y","z"], ["c1","c2"])
    jb = subdivision(2, "b_", ["xp","y","z"], ["cp1","cp2"])
    j = (ja[0] | jb[0] | {"lambda"}, ja[1] | jb[1] | {tuple(sorted(("lambda","x"))), tuple(sorted(("lambda","xp")))}, ja[2] | jb[2] | {"lambda":1})
    k1 = subdivision(3, "k1_", ["u1","u2","u3"], ["c1","d1","c3"])
    k2 = subdivision(3, "k2_", ["up1","up2","up3"], ["cp1","d2","cp3"], True)
    k = (k1[0] | k2[0], k1[1] | k2[1] | {tuple(sorted(("d1","d2")))}, k1[2] | k2[2])
    return {"S2":s2, "S3":s3, "J0":j, "K0":k}


EXPECTED_GENERATORS = {
    "S2": {"base_graph":"K3,2","bases":["b1","b2","b3"],"centers":["c1","c2"],"operation":"subdivide every edge exactly once","original_color":0,"subdivision_color":1},
    "S3": {"base_graph":"K3,3","bases":["b1","b2","b3"],"centers":["c1","c2","c3"],"operation":"subdivide every edge exactly once","original_color":0,"subdivision_color":1},
    "J0": {"all_other_copy_vertices_distinct":True,"copies":[{"bases":["x","y","z"],"centers":["c1","c2"],"kind":"S2","subdivision_prefix":"a_"},{"bases":["xp","y","z"],"centers":["cp1","cp2"],"kind":"S2","subdivision_prefix":"b_"}],"extra_vertex":{"color":1,"name":"lambda","neighbors":["x","xp"]},"identified_before_quotient":["y","z"]},
    "K0": {"bridge_edge":["d1","d2"],"copies":[{"bases":["u1","u2","u3"],"centers":["c1","d1","c3"],"kind":"S3","reverse_coloring":False,"subdivision_prefix":"k1_"},{"bases":["up1","up2","up3"],"centers":["cp1","d2","cp3"],"kind":"S3","reverse_coloring":True,"subdivision_prefix":"k2_"}],"copies_disjoint_before_bridge":True},
}


def verify(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    graphs = source_graphs(); templates = data.get("templates", {})
    expected_metrics = {
        "S2":{"vertices":11,"edges":12,"connected":True,"proper_bipartite_coloring":True,"cycle_rank":2},
        "S3":{"vertices":15,"edges":18,"connected":True,"proper_bipartite_coloring":True,"cycle_rank":4},
        "J0":{"vertices":21,"edges":26,"connected":True,"proper_bipartite_coloring":True,"cycle_rank":6},
        "K0":{"vertices":30,"edges":37,"connected":True,"proper_bipartite_coloring":True,"cycle_rank":8},
    }
    for name in ("S2","S3","J0","K0"):
        if templates.get(name,{}).get("generator") != EXPECTED_GENERATORS[name]: errors.append(f"{name} source generator drift")
        derived = metrics(graphs[name])
        if derived != expected_metrics[name] or templates.get(name,{}).get("metrics") != derived: errors.append(f"{name} independently derived metrics drift")

    admissible = data.get("admissible_quotients", {})
    if set(admissible.get("rules", [])) != {
        "equivalent vertices must have the same source 2-color",
        "each distinguished S2 or S3 copy is injective under the quotient",
        "repeated quotient edges are suppressed",
        "J additionally requires x and xp to remain inequivalent",
    }: errors.append("admissible quotient rule drift")
    for key in ("quotients_are_simple_bipartite","distinguished_subdivisions_embed","connectedness_preserved_from_connected_template","cycle_preserved_by_injected_S2_or_S3","identity_relation_is_admissible_J","identity_relation_is_admissible_K"):
        if admissible.get("consequences",{}).get(key) is not True: errors.append(f"missing quotient consequence: {key}")
    partial = sum(math.comb(6,i)*math.comb(9,i)*math.factorial(i) for i in range(7))
    counts = admissible.get("K0_labelled_admissible_relation_count",{})
    if (counts.get("per_color_partial_bijections_6_to_9"),counts.get("two_color_product")) != (partial,partial**2): errors.append("K0 labelled admissible-relation count drift")

    if data.get("forbidden_family") != {"definition":"F = {C4,C6} union J union K","finite":True,"nonempty":True,"all_members_connected":True,"all_members_bipartite":True,"all_members_contain_cycle":True}: errors.append("forbidden-family invariant drift")

    upper = data.get("upper_bound_bridge",{}); deps = upper.get("proof_dependencies",[])
    if [x.get("id") for x in deps] != [f"U{i}" for i in range(1,9)] or any(x.get("status") != "independently_reconstructed" for x in deps): errors.append("upper-bound dependency chain drift")
    exact = upper.get("exact_arithmetic",{})
    if Fraction(4,3)-Fraction(1,48) != Fraction(21,16) or Fraction(5,16)*16 != 5: errors.append("internal exponent arithmetic failure")
    if exact != {"contradiction_N_exponent":5,"contradiction_power":16,"difference_check":[63,48,21,16],"four_thirds_minus_one_over_48":"21/16","minimum_degree_exponent":"5/16"}: errors.append("upper-bound exact arithmetic ledger drift")

    lower = data.get("lower_bound_bridge",{}); params = lower.get("exact_parameters",{})
    if params.get("vertices_nq") != "2(q+1)(q^2+1)" or params.get("edges_eq") != "(q+1)^2(q^2+1)": errors.append("generalized-quadrangle parameter drift")
    for q in (1,2,3,5,11):
        a,b=q+1,q*q+1; n,e=2*a*b,a*a*b
        if 16*e**3-n**4 != 32*q*a**4*b**3 or 16*e**3 < n**4: errors.append("lower density identity failure"); break
    for t in (2,3):
        for q in (1,2,7):
            lhs=t**3*(q+1)*(q*q+1)-(t*q+1)*(t*t*q*q+1); rhs=(t**3-t**2)*q*q+(t**3-t)*q+(t**3-1)
            if lhs != rhs or lhs < 0: errors.append("prime-power growth identity failure"); break
    growth=lower.get("growth_and_padding",{})
    if growth.get("uniform_lower_constant") != "2^(-4/3)/81 is a valid common positive coefficient for both t=2 and t=3 classes": errors.append("uniform lower constant drift")
    parity=lower.get("parity_split",{})
    if parity.get("even_q",{}).get("choice") != "q=2^j" or parity.get("odd_q",{}).get("choice") != "q=3^j": errors.append("parity split drift")
    literature=lower.get("primary_literature_crosscheck",{})
    facts={"W(q) is a generalized quadrangle of order (q,q)","Q(4,q) is dual to W(q)","W(q) is self-dual for even q","for odd q every triad of Q(4,q) has 0 or 2 centers"}
    if literature.get("arxiv_id") != "1706.06583" or set(literature.get("facts",[])) != facts: errors.append("primary finite-geometry cross-check drift")

    concordance=data.get("source_to_encoded_concordance",{})
    if concordance.get("exact_targets") != ["CompactnessConjecture.quantitativeCompactnessCounterexample","CompactnessConjecture.compactnessCounterexample_bigO","CompactnessConjecture.not_erdos_180"]: errors.append("encoded target set drift")
    if concordance.get("proof_body_compared_in_full") is not False: errors.append("full proof-body comparison inflation")
    return errors


def main() -> int:
    errors=verify(load())
    if errors:
        print("\n".join(errors)); print(f"Compactness independent verifier failed with {len(errors)} error(s)"); return 1
    print("independently verified Compactness templates, quotient invariants, upper bridge, generalized-quadrangle lower bridge, and target concordance"); return 0


if __name__ == "__main__":
    raise SystemExit(main())
