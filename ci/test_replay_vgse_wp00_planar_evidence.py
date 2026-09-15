#!/usr/bin/env python3
"""Drift/tamper tests for the VGSE C05 exact/interval replay."""
from __future__ import annotations
import copy, importlib.util, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"ci"/"replay_vgse_wp00_planar_evidence.py"
spec=importlib.util.spec_from_file_location("vgse_planar",P); assert spec and spec.loader
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
expected=m.build_evidence()
actual=json.loads((ROOT/"evidence"/"vgse"/"VGSE-WP00-CERT-001-planar.json").read_text(encoding="utf-8"))
assert actual==expected
for path,value in [
 (("conclusion","certified_root_boxes"),4),
 (("conclusion","five_primitives_exactly_closed"),False),
 (("trust","adjudication_effect"),"certified"),
]:
 tampered=copy.deepcopy(actual); tampered[path[0]][path[1]]=value; assert tampered!=expected
print("VGSE planar exact/interval evidence tests passed")
