#!/usr/bin/env python3
"""Validate MATHCERT adoption of GCL-AGENT-CONTINUITY-001."""

from __future__ import annotations
import json, sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ADOPTION = ROOT / ".gcl/agent-continuity.json"
AGENTS = ROOT / "AGENTS.md"

EXPECTED = {
    "policy_id": "GCL-AGENT-CONTINUITY-001",
    "version": "1.0.0",
    "repository": "grandchallenge/MATHCERT",
    "specialization": "MATHCERT-CERTIFICATION-CONTINUITY-001",
}

def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def adoption_errors(record: dict[str, Any], agents_text: str) -> list[str]:
    errors: list[str] = []
    for key, value in EXPECTED.items():
        if record.get(key) != value:
            errors.append(f"{key}: expected {value!r}, found {record.get(key)!r}")
    if record.get("required") is not True:
        errors.append("required must be true")

    reb = record.get("rebind_requirements", {})
    for key in ("exact_claim_or_subject","certification_route","candidate_artifact","material_evidence_digests"):
        if reb.get(key) is not True:
            errors.append(f"rebind_requirements.{key} must be true")

    prov = record.get("provenance", {})
    for key in ("construction_authorship_preserved","verification_authorship_preserved"):
        if prov.get(key) is not True:
            errors.append(f"provenance.{key} must be true")

    auth = record.get("authority_preservation", {})
    if auth.get("authority_changed") is not False:
        errors.append("authority_preservation.authority_changed must be false")
    for key in (
        "certification_authority_inherited_across_agent_substitution",
        "substantive_independence_inherited_across_agent_substitution",
        "continuity_receipt_satisfies_independence",
        "ci_or_merge_implies_certification",
        "predecessor_conclusion_implies_certification",
    ):
        if auth.get(key) is not False:
            errors.append(f"authority_preservation.{key} must be false")

    tokens = (
        "GCL-AGENT-CONTINUITY-001@1.0.0",
        "certification authority and substantive",
        "do not transfer automatically",
        "continuity receipt",
        "cannot satisfy an independence requirement",
    )
    for token in tokens:
        if token not in agents_text:
            errors.append(f"AGENTS.md missing continuity safeguard token: {token}")
    return errors

def main() -> int:
    errors: list[str] = []
    if not ADOPTION.is_file():
        errors.append("missing .gcl/agent-continuity.json")
        record = {}
    else:
        try:
            record = load_json(ADOPTION)
        except Exception as exc:
            errors.append(f"invalid adoption JSON: {exc}")
            record = {}
    if not AGENTS.is_file():
        errors.append("missing AGENTS.md")
        agents_text = ""
    else:
        agents_text = AGENTS.read_text(encoding="utf-8")
    if isinstance(record, dict):
        errors.extend(adoption_errors(record, agents_text))
    else:
        errors.append("adoption record must be a JSON object")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("MATHCERT GCL-AGENT-CONTINUITY-001 adoption: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
