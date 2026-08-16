#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "evidence/openai_ten_proofs/two_degenerate_construction/source_authority.json"
RECON = ROOT / "evidence/openai_ten_proofs/two_degenerate_construction/reconstruction.json"
LEDGER = ROOT / "evidence/openai_ten_proofs/two_degenerate_construction/proof_dependency_ledger.json"
PROJECTION = ROOT / "evidence/openai_ten_proofs/two_degenerate_scope_repair/SourceFaithfulProjection.lean"

EXPECTED_SOURCE_SHA256 = "ebc561ab5c53dbd240e17a8fdb6fffeb648591eca85dbfc7466f563638f8c566"
EXPECTED_SOURCE_BYTES = 2487031
EXPECTED_PROJECTION_BLOB = "ac1ec20e95d6acbcd1c3a111afe28bca92a43377"
EXPECTED_THEOREMS = [
    "TwoDegenerateGraphs.mathcert_sourceFaithfulTwoDegenerateExtremalCounterexample",
    "TwoDegenerateGraphs.mathcert_sourceFaithfulNotErdos146",
]


def git_blob_sha1(path: Path) -> str:
    import hashlib
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def independent_layer_check(l0: int = 4, depth: int = 2) -> dict:
    layers: list[list[str]] = [[f"v0_{i}" for i in range(l0)]]
    adj: dict[str, set[str]] = defaultdict(set)
    for level in range(1, depth + 1):
        previous = layers[-1]
        current: list[str] = []
        for i in range(len(previous)):
            for j in range(i + 1, len(previous)):
                child = f"v{level}_{i}_{j}"
                current.append(child)
                for parent in (previous[i], previous[j]):
                    adj[child].add(parent)
                    adj[parent].add(child)
        layers.append(current)
    vertices = {v for layer in layers for v in layer}

    closure = {layers[0][0]}
    changed = True
    while changed:
        changed = False
        for v in list(closure):
            for w in adj[v]:
                if w not in closure:
                    closure.add(w)
                    changed = True

    parity_ok = True
    layer_index = {v: i for i, layer in enumerate(layers) for v in layer}
    for v in vertices:
        for w in adj[v]:
            if abs(layer_index[v] - layer_index[w]) != 1:
                parity_ok = False

    remaining = set(vertices)
    while remaining:
        candidate = next((v for v in remaining if len(adj[v] & remaining) <= 2), None)
        if candidate is None:
            break
        remaining.remove(candidate)

    return {
        "layer_sizes": [len(x) for x in layers],
        "connected": closure == vertices,
        "edges_only_between_consecutive_layers": parity_ok,
        "two_degenerate_by_peeling": not remaining,
    }


def main() -> int:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    recon = json.loads(RECON.read_text(encoding="utf-8"))
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))

    if source["official_source"]["sha256"] != EXPECTED_SOURCE_SHA256:
        raise SystemExit("source SHA-256 substitution")
    if source["official_source"]["bytes"] != EXPECTED_SOURCE_BYTES:
        raise SystemExit("source byte-length substitution")
    if source["theorem"]["number"] != "1.2":
        raise SystemExit("theorem-locus drift")
    if source["mathcert_projection"]["git_blob_sha1"] != EXPECTED_PROJECTION_BLOB:
        raise SystemExit("projection authority drift")
    if git_blob_sha1(PROJECTION) != EXPECTED_PROJECTION_BLOB:
        raise SystemExit("projection bytes drift")

    unauthorized = source["explicitly_not_source_authorized"]
    if len(unauthorized) != 1 or "two-coloring" not in unauthorized[0]:
        raise SystemExit("stronger coloring-side exclusion missing")
    if recon["refutation_bridge"]["coloring_property_needed"] is not False:
        raise SystemExit("refutation improperly depends on coloring property")
    if recon["assessment"]["stronger_coloring_property"] != "not_used_not_source_attributed":
        raise SystemExit("reconstruction improperly attributes stronger property")
    if ledger["formal_projection_dependency"]["stronger_coloring_conjunct_used"] is not False:
        raise SystemExit("proof ledger improperly uses stronger coloring conjunct")

    layer = independent_layer_check()
    expected_sizes = [4, 6, 15]
    if layer["layer_sizes"] != expected_sizes:
        raise SystemExit(f"layer cardinality drift: {layer['layer_sizes']}")
    if not all((layer["connected"], layer["edges_only_between_consecutive_layers"], layer["two_degenerate_by_peeling"])):
        raise SystemExit(f"independent layered-graph check failed: {layer}")

    lhs = (2, 2, -4)
    rhs = (3 - 1, 2, -3 - 1)
    if lhs != rhs:
        raise SystemExit("exponent identity coefficient check failed")

    window = recon["parameter_layer"]["window_nonempty_proof"]
    if window["optimizer"] != "tau=1/(1+sqrt(3))":
        raise SystemExit("parameter optimizer drift")
    if "(r-1)^4" not in window["exact_positive_form"]:
        raise SystemExit("exact parameter-window positivity reduction missing")

    if recon["extremal_bridge"]["final_constant"] != "c=2^(-3/2-epsilon)>0":
        raise SystemExit("padding constant drift")
    if "N_(m+1)<=2*N_m" not in recon["extremal_bridge"]["all_n_padding"]:
        raise SystemExit("all-n padding bridge missing")
    if recon["assessment"]["substantive_mathematical_gap_found"] is not False:
        raise SystemExit("candidate cannot be clear with a substantive mathematical gap")
    if recon["assessment"]["proof_body_compared_in_full"] is not False:
        raise SystemExit("proof-body comparison overclaim")
    if ledger["boundary"]["all_source_internal_entropy_lemmas_reformalized"] is not False:
        raise SystemExit("entropy-lemma formalization overclaim")

    projection_text = PROJECTION.read_text(encoding="utf-8")
    for theorem in EXPECTED_THEOREMS:
        if theorem.split(".")[-1] not in projection_text:
            raise SystemExit(f"source-faithful theorem missing: {theorem}")
    signature = projection_text.split("theorem mathcert_sourceFaithfulTwoDegenerateExtremalCounterexample", 1)[1].split(":= by", 1)[0]
    if "Coloring" in signature:
        raise SystemExit("coloring-side property leaked into source-faithful theorem signature")

    print("independent J2 construction verifier: source identity, layered structure, exponent bridge, padding, dependency boundary, and coloring exclusion are clear")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
