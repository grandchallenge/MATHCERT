#!/usr/bin/env python3
"""Validate the bounded OTP-E-CONNES-RIGIDITY MATHCERT intake successor."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
from typing import Any
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
RECORD=ROOT/"governance/result_family_intake_successors/OTP-E-CONNES-RIGIDITY.json"
SCHEMA=ROOT/"schemas/openai_ten_proofs_connes_rigidity_result_family_intake_successor.schema.json"
LEGACY_DIR=ROOT/"governance/result_family_intakes"
LEGACY_VALIDATOR=ROOT/"ci/validate_openai_ten_proofs_result_family_intakes.py"
EXPECTED_LEGACY_VALIDATOR_BLOB="e0a16870c45aadc2b2a323159df595da489384f7"
FAMILY_ID="OTP-E-CONNES-RIGIDITY"
EXPECTED_CANONICAL_SHA256="d4c05bbdb8199ce82113c790fd6ff2f73c143a9c6d91619d6d106f257bac5135"

def load_json(path: Path)->Any: return json.loads(path.read_text(encoding="utf-8"))
def git_blob_sha1(path: Path)->str:
    data=path.read_bytes(); return hashlib.sha1(f"blob {len(data)}\0".encode("ascii")+data,usedforsecurity=False).hexdigest()
def canonical_sha256(data: Any)->str:
    return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def validation_errors(data: dict[str,Any]|None=None,*,legacy_file_exists: bool|None=None)->list[str]:
    record=load_json(RECORD) if data is None else data; schema=load_json(SCHEMA)
    errors=[f"schema: {e.json_path}: {e.message}" for e in sorted(Draft202012Validator(schema).iter_errors(record),key=lambda e:list(e.path))]
    if canonical_sha256(record)!=EXPECTED_CANONICAL_SHA256: errors.append("Connes rigidity successor intake exact content drift")
    if git_blob_sha1(LEGACY_VALIDATOR)!=EXPECTED_LEGACY_VALIDATOR_BLOB: errors.append("historical result-family intake validator changed")
    exists=(LEGACY_DIR/f"{FAMILY_ID}.json").exists() if legacy_file_exists is None else legacy_file_exists
    if exists: errors.append("Connes rigidity successor inserted into frozen historical intake namespace")
    return errors
def main()->int:
    errors=validation_errors()
    if errors: print("\n".join(errors),file=sys.stderr); return 1
    print("OTP-E-CONNES-RIGIDITY successor intake: PASS; exact two-target scope and zero route/output authority"); return 0
if __name__=="__main__": raise SystemExit(main())
