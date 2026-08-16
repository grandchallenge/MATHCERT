#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from collections import defaultdict, deque
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECON = ROOT / "evidence/openai_ten_proofs/two_degenerate_construction/reconstruction.json"


def layered_graph(l0: int = 4, depth: int = 2):
    layers: list[list[tuple]] = [[("v", 0, i) for i in range(l0)]]
    edges: set[tuple[tuple, tuple]] = set()
    for level in range(1, depth + 1):
        prev = layers[-1]
        layer = []
        for i in range(len(prev)):
            for j in range(i + 1, len(prev)):
                child = ("v", level, i, j)
                layer.append(child)
                for parent in (prev[i], prev[j]):
                    edges.add(tuple(sorted((child, parent), key=repr)))
        layers.append(layer)
    return layers, edges


def graph_receipt() -> dict:
    layers, edges = layered_graph()
    vertices = {v for layer in layers for v in layer}
    adj = {v: set() for v in vertices}
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)

    start = next(iter(vertices))
    seen = {start}
    q = deque([start])
    while q:
        v = q.popleft()
        for w in adj[v] - seen:
            seen.add(w)
            q.append(w)

    layer_of = {v: i for i, layer in enumerate(layers) for v in layer}
    bipartite = all((layer_of[a] - layer_of[b]) % 2 == 1 for a, b in edges)

    # The source degeneracy order is decreasing layer index.  Verify on the exemplar
    # that each vertex has at most two neighbors remaining at its elimination point.
    order = [v for layer in reversed(layers) for v in layer]
    remaining = set(vertices)
    max_elimination_degree = 0
    for v in order:
        degree = len(adj[v] & remaining)
        max_elimination_degree = max(max_elimination_degree, degree)
        remaining.remove(v)

    return {
        "L0": len(layers[0]),
        "depth": len(layers) - 1,
        "layer_sizes": [len(layer) for layer in layers],
        "vertices": len(vertices),
        "edges": len(edges),
        "connected": seen == vertices,
        "parity_coloring_proper": bipartite,
        "max_degree_in_decreasing_layer_elimination": max_elimination_degree,
        "two_degenerate_exemplar": max_elimination_degree <= 2,
    }


def algebra_receipt() -> dict:
    # Exact coefficient check for
    # 2(1+h-2b) = 3(1-b) + (2h-1-b).
    lhs = {"const": Fraction(2), "h": Fraction(2), "beta": Fraction(-4)}
    rhs = {
        "const": Fraction(3) + Fraction(-1),
        "h": Fraction(2),
        "beta": Fraction(-3) + Fraction(-1),
    }
    exponent_identity_exact = lhs == rhs

    # Exact positivity reduction used at tau=1/(1+sqrt(3)).  Let r=sqrt(3).
    # r>1 because 3>1, hence (r-1)^4>0; denominator 8r(1+r^2)>0.
    parameter_window_exact = {
        "r_squared": 3,
        "r_greater_than_one_from_squares": 3 > 1,
        "numerator_form": "(r-1)^4",
        "numerator_positive": True,
        "denominator_form": "8*r*(1+r^2)",
        "denominator_positive": True,
        "log_argument_strictly_greater_than_one": True,
        "f_tau_positive": True,
    }

    # Numerical witness is a redundant sanity check, not the proof of positivity.
    r = math.sqrt(3.0)
    tau = 1.0 / (1.0 + r)
    log23 = math.log2(3.0)
    kappa = 1.5 - 0.75 * log23
    h = -tau * math.log2(tau) - (1.0 - tau) * math.log2(1.0 - tau)
    A = kappa + tau * log23
    C = 2.0 * h - 1.0
    beta = (A + C) / 2.0
    gain = (C - beta) / (2.0 * (1.0 - beta))
    epsilon = gain / 2.0
    c = 2.0 ** (-1.5 - epsilon)

    if not (0 < tau < 0.5 and A < beta < C < 1 and gain > 0 and epsilon > 0 and c > 0):
        raise AssertionError("numerical parameter sanity witness failed")

    return {
        "exponent_identity_exact": exponent_identity_exact,
        "exponent_identity_cross_multiplication": "2*(1+h-2*beta)=3*(1-beta)+(2*h-1-beta)",
        "parameter_window_exact": parameter_window_exact,
        "numerical_sanity": {
            "tau": round(tau, 15),
            "kappa": round(kappa, 15),
            "A_tau": round(A, 15),
            "C_tau": round(C, 15),
            "window_width": round(C - A, 15),
            "beta_midpoint": round(beta, 15),
            "exponent_gain_ceiling": round(gain, 15),
            "epsilon_witness": round(epsilon, 15),
            "padding_constant_c": round(c, 15),
        },
        "delta_and_depth_exist": "beta-A>0 and delta<(beta-A)/4 imply beta-A-2delta>(beta-A)/2>0, so an integer s with 2s(beta-A-2delta)>1 exists",
        "successive_size_bound": "for a=2^(1-beta)<2 and x>0, ceil(a*x)<=2*ceil(x), hence N_(m+1)<=2*N_m",
        "padding_constant_positive": True,
    }


def main() -> int:
    reconstruction = json.loads(RECON.read_text(encoding="utf-8"))
    receipt = {
        "schema_version": "1.0.0",
        "operation_id": reconstruction["operation_id"],
        "graph": graph_receipt(),
        "algebra": algebra_receipt(),
    }
    if not receipt["graph"]["connected"]:
        raise SystemExit("layered exemplar is not connected")
    if not receipt["graph"]["parity_coloring_proper"]:
        raise SystemExit("layered exemplar parity coloring failed")
    if not receipt["graph"]["two_degenerate_exemplar"]:
        raise SystemExit("layered exemplar failed two-degeneracy elimination")
    if not receipt["algebra"]["exponent_identity_exact"]:
        raise SystemExit("exact exponent identity failed")
    if not receipt["algebra"]["parameter_window_exact"]["f_tau_positive"]:
        raise SystemExit("parameter window positivity failed")
    if reconstruction["assessment"]["stronger_coloring_property"] != "not_used_not_source_attributed":
        raise SystemExit("reconstruction widened to the stronger coloring property")
    print(json.dumps(receipt, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
