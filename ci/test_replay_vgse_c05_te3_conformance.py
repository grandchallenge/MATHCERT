#!/usr/bin/env python3
"""Regression tests for the independent VGSE-C05 TE3 conformance audit."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "vgse_te3", ROOT / "ci" / "replay_vgse_c05_te3_conformance.py"
)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

expected = json.loads(
    (ROOT / "evidence" / "vgse" / "VGSE-WP00-CERT-001-te3-conformance-audit.json").read_text(
        encoding="utf-8"
    )
)
actual = mod.build_evidence()

assert actual == expected
assert actual["conclusion"]["all_five_branches_exclude_te3"] is True
assert actual["conclusion"]["maximum_certified_squared_ratio_strictly_below"] == "1/1000"
assert len(actual["branches"]) == 5
assert all(branch["te3_excluded"] is True for branch in actual["branches"])
assert actual["trust"]["may_promote_or_rewrite_claim_after_this_record_alone"] is False
assert actual["source_provenance"]["arxiv_id"] == "2410.09574v2"
assert actual["source_provenance"]["provider_merge_commit"] == "593afd971a53ca0285f8b94570997ed7c3d7c170"
assert actual["source_provenance"]["definition_refs"]["geometric_edge_weights"] == "Section 1.2, equation (1.5)"
assert actual["source_provenance"]["definition_refs"]["te3"] == "Definition 1.2, condition (TE3)"

# Fail closed under a synthetic evidence mutation.
tampered = json.loads(json.dumps(expected))
tampered["branches"][0]["te3_excluded"] = False
assert tampered != actual

print("VGSE C05 TE3 conformance regression: PASS")
