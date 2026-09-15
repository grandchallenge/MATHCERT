#!/usr/bin/env python3
"""Tests for the independent VGSE WP00 exact and interval evidence replays."""
from __future__ import annotations
import copy, importlib.util, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    assert spec and spec.loader
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

exact=load("vgse_exact",ROOT/"ci"/"replay_vgse_wp00_exact_evidence.py")
expected=exact.build_evidence()
actual=json.loads((ROOT/"evidence"/"vgse"/"VGSE-WP00-CERT-001-exact-algebraic-graph.json").read_text(encoding="utf-8"))
assert actual==expected
for path,value in [(("VGSE-C04","common_scale"),"1/8"),(("VGSE-C01","conclusion","isolated_solution_count"),6)]:
    tampered=copy.deepcopy(actual); target=tampered
    for key in path[:-1]: target=target[key]
    target[path[-1]]=value; assert tampered!=expected

planar=load("vgse_planar",ROOT/"ci"/"replay_vgse_wp00_planar_evidence.py")
expected=planar.build_evidence()
actual=json.loads((ROOT/"evidence"/"vgse"/"VGSE-WP00-CERT-001-planar.json").read_text(encoding="utf-8"))
assert actual==expected
for path,value in [(("conclusion","certified_root_boxes"),4),(("conclusion","five_primitives_exactly_closed"),False),(("trust","adjudication_effect"),"certified")]:
    tampered=copy.deepcopy(actual); tampered[path[0]][path[1]]=value; assert tampered!=expected

print("VGSE exact and interval evidence replay tests passed")
