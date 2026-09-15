#!/usr/bin/env python3
"""Tests for the independent VGSE WP00 exact evidence replay."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "ci" / "replay_vgse_wp00_exact_evidence.py"
EVIDENCE_PATH = ROOT / "evidence" / "vgse" / "VGSE-WP00-CERT-001-exact-algebraic-graph.json"

spec = importlib.util.spec_from_file_location("vgse_exact", MODULE_PATH)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

expected = mod.build_evidence()
actual = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
assert actual == expected

tampered = copy.deepcopy(actual)
tampered["VGSE-C04"]["common_scale"] = "1/8"
assert tampered != expected

tampered = copy.deepcopy(actual)
tampered["VGSE-C01"]["conclusion"]["isolated_solution_count"] = 6
assert tampered != expected

print("VGSE exact evidence replay tests passed")
