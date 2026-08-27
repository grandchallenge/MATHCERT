#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "governance" / "result_family_replay_evidence_readbacks" / "OTP-H-B1-B2.json"
SCHEMA = ROOT / "schemas" / "openai_ten_proofs_replay_readback_reconciliation.schema.json"
ROUTES = ROOT / "governance" / "certification_routes.json"

EXPECTED = {
    "OTP-H-GAPCVP": {
        "candidate_path": "governance/result_family_replay_evidence_successors/OTP-H-GAPCVP.json",
        "candidate_blob": "a12f2c553b71f4daec9255e1f254f48a21f439c3",
        "issue": 165, "pr": 169,
        "head": "fca63848cfb1428292e4b74a4ed8980646d45aa2",
        "review": 5023763871,
        "merge": "f34f33b22292ca244956781065fdf84efe2b43f2",
        "parents": ["aa6a730394db45ca05c9a3d0a02434bc74fd8a61", "fca63848cfb1428292e4b74a4ed8980646d45aa2"],
        "runs": [32848939191, 32848939207, 32848940096, 32848939106],
        "disposition": "H_REPLAY_EVIDENCE_PROTECTED__ZERO_ROUTE_OUTPUT_AUTHORITY",
        "next": "separate_family_specific_H_route_proposal",
    },
    "OTP-B1-BINARY-CODES": {
        "candidate_path": "governance/result_family_replay_evidence_successors/OTP-B1-BINARY-CODES.json",
        "candidate_blob": "fd669ae6cfc39110560656c2123d5d4449200830",
        "issue": 166, "pr": 170,
        "head": "67f445b9a5e015083644416d96f4a10722efe032",
        "review": 5023771071,
        "merge": "d8daab1c0deec3d41ac438714e21ee752c14ac46",
        "parents": ["f34f33b22292ca244956781065fdf84efe2b43f2", "67f445b9a5e015083644416d96f4a10722efe032"],
        "runs": [32849083880, 32849083816, 32849084349, 32849083761],
        "disposition": "B1_REPLAY_EVIDENCE_PROTECTED__ZERO_ROUTE_OUTPUT_AUTHORITY",
        "next": "separate_family_specific_B1_route_proposal",
    },
    "OTP-B2-SPHERICAL-CODES": {
        "candidate_path": "governance/result_family_replay_evidence_successors/OTP-B2-SPHERICAL-CODES.json",
        "candidate_blob": "288193448eee80c041beef57059182e1abe2e33c",
        "issue": 167, "pr": 171,
        "head": "da41ab10f440b45fe53d321bc08bd3ffa8770930",
        "review": 5023775055,
        "merge": "938738844c4659b30a21d963da468ddfd1df51ad",
        "parents": ["d8daab1c0deec3d41ac438714e21ee752c14ac46", "da41ab10f440b45fe53d321bc08bd3ffa8770930"],
        "runs": [32849224700, 32849225046, 32849225863, 32849224740],
        "disposition": "B2_REPLAY_EVIDENCE_PROTECTED__ZERO_ROUTE_OUTPUT_AUTHORITY",
        "next": "separate_family_specific_B2_route_proposal",
    },
}


def load(path: Path):return json.loads(path.read_text())

def blob(p):
 b=p.read_bytes();return hashlib.sha1(f"blob {len(b)}\0".encode()+b,usedforsecurity=False).hexdigest()
