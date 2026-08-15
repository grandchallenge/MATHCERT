#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "evidence/openai_ten_proofs/compactness_construction/reconstruction.json"


def subdiv(k: int, prefix: str, bases: list[str], centers: list[str], reverse: bool = False):
    original, middle = (1, 0) if reverse else (0, 1)
    vertices = list(bases) + list(centers)
    colors = {v: original for v in vertices}
    edges: set[tuple[str, str]] = set()
    for b in bases:
        for c in centers:
            s = f"{prefix}s_{b}_{c}"
            vertices.append(s)
            colors[s] = middle
            edges |= {tuple(sorted((b, s))), tuple(sorted((s, c)))}
    return set(vertices), edges, colors


def stats(vertices, edges, colors):
    adj = {v: set() for v in vertices}
    for a, b in edges:
        adj[a].add(b); adj[b].add(a)
    seen, stack = set(), [next(iter(vertices))]
    while stack:
        v = stack.pop()
        if v in seen: continue
        seen.add(v); stack.extend(adj[v] - seen)
    connected = seen == vertices
    return {
        "vertices": len(vertices),
        "edges": len(edges),
        "connected": connected,
        "proper_bipartite_coloring": all(colors[a] != colors[b] for a, b in edges),
        "cycle_rank": len(edges) - len(vertices) + (1 if connected else 0),
    }


def produce() -> dict:
    s2 = subdiv(2, "", ["b1","b2","b3"], ["c1","c2"])
    s3 = subdiv(3, "", ["b1","b2","b3"], ["c1","c2","c3"])
    ja = subdiv(2, "a_", ["x","y","z"], ["c1","c2"])
    jb = subdiv(2, "b_", ["xp","y","z"], ["cp1","cp2"])
    jv = ja[0] | jb[0] | {"lambda"}
    je = ja[1] | jb[1] | {tuple(sorted(("lambda","x"))), tuple(sorted(("lambda","xp")))}
    jc = ja[2] | jb[2] | {"lambda": 1}
    k1 = subdiv(3, "k1_", ["u1","u2","u3"], ["c1","d1","c3"])
    k2 = subdiv(3, "k2_", ["up1","up2","up3"], ["cp1","d2","cp3"], True)
    kv, ke, kc = k1[0] | k2[0], k1[1] | k2[1] | {tuple(sorted(("d1","d2")))}, k1[2] | k2[2]
    partial = sum(math.comb(6,i)*math.comb(9,i)*math.factorial(i) for i in range(7))
    return {
        "metrics": {
            "S2": stats(*s2), "S3": stats(*s3),
            "J0": stats(jv, je, jc), "K0": stats(kv, ke, kc),
        },
        "k0_partial_bijections": partial,
        "k0_relation_product": partial**2,
        "upper_exponent": "21/16",
        "minimum_degree_exponent": "5/16",
        "contradiction_power": 16,
        "contradiction_n_exponent": 5,
        "lower_cubed_identity": "16 e_q^3 - n_q^4 = 32 q (q+1)^4 (q^2+1)^3 >= 0",
    }


def main() -> int:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    receipt = produce()
    for name, value in receipt["metrics"].items():
        if artifact["templates"][name]["metrics"] != value:
            print(f"producer mismatch: {name}")
            return 1
    counts = artifact["admissible_quotients"]["K0_labelled_admissible_relation_count"]
    if (counts["per_color_partial_bijections_6_to_9"], counts["two_color_product"]) != (
        receipt["k0_partial_bijections"], receipt["k0_relation_product"]
    ):
        print("producer mismatch: K0 admissible relation count")
        return 1
    exact = artifact["upper_bound_bridge"]["exact_arithmetic"]
    if (exact["four_thirds_minus_one_over_48"], exact["minimum_degree_exponent"],
        exact["contradiction_power"], exact["contradiction_N_exponent"]) != (
        receipt["upper_exponent"], receipt["minimum_degree_exponent"],
        receipt["contradiction_power"], receipt["contradiction_n_exponent"]
    ):
        print("producer mismatch: upper exponent bridge")
        return 1
    if artifact["lower_bound_bridge"]["exact_parameters"]["cubed_exact_form"] != receipt["lower_cubed_identity"]:
        print("producer mismatch: lower density identity")
        return 1
    print("deterministic Compactness construction producer agrees with retained reconstruction")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
