#!/usr/bin/env python3
"""Validate MATHCERT adoption of GCL-AGENT-CONTINUITY-001."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ADOPTION_REL = ".gcl/agent-continuity.json"
AGENTS_REL = "AGENTS.md"

EXPECTED = {
    "policy_id": "GCL-AGENT-CONTINUITY-001",
    "version": "1.0.0",
    "repository": "grandchallenge/MATHCERT",
    "specialization": "MATHCERT-CERTIFICATION-SAFE-CONTINUITY-001",
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

    rebind = record.get("interruption_rebind", {})
    for key in ("exact_claim_or_subject","certification_route","candidate_artifact","material_evidence_digests"):
        if rebind.get(key) is not True:
            errors.append(f"interruption_rebind.{key} must be true")

    provenance = record.get("provenance", {})
    for key in ("construction_authorship_preserved","verification_provenance_preserved"):
        if provenance.get(key) is not True:
            errors.append(f"provenance.{key} must be true")

    succession = record.get("succession", {})
    if succession.get("operational_state_may_transfer") is not True:
        errors.append("succession.operational_state_may_transfer must be true")
    for key in ("certification_authority_inherited","substantive_independence_inherited"):
        if succession.get(key) is not False:
            errors.append(f"succession.{key} must be false")
    if succession.get("non_authoring_requirements_re_evaluated_when_materially_affected") is not True:
        errors.append("non-authoring requirements must be re-evaluated when materially affected")

    fail_closed = record.get("fail_closed", {})
    false_keys = (
        "continuity_receipt_satisfies_independence",
        "continuity_receipt_is_certification_disposition",
        "ci_or_protected_merge_implies_certification",
        "predecessor_agent_conclusion_is_current_certification",
    )
    for key in false_keys:
        if fail_closed.get(key) is not False:
            errors.append(f"fail_closed.{key} must be false")
    for key in ("changed_exact_subject_or_evidence_requires_rebind","certification_disposition_fail_closed"):
        if fail_closed.get(key) is not True:
            errors.append(f"fail_closed.{key} must be true")

    authority = record.get("authority_preservation", {})
    for key in ("authority_changed","certification_authority_changed","mathematical_claim_authority_changed","protected_bypass_changed"):
        if authority.get(key) is not False:
            errors.append(f"authority_preservation.{key} must be false")

    required_tokens = (
        "GCL-AGENT-CONTINUITY-001@1.0.0",
        "operational state may transfer",
        "certification authority and substantive independence do not transfer automatically",
        "continuity receipt cannot satisfy an independence requirement",
        "changed exact subject or evidence identity requires rebinding",
    )
    for token in required_tokens:
        if token not in agents_text:
            errors.append(f"AGENTS.md missing Cert continuity binding token: {token}")

    return errors

def repository_errors(root: Path = ROOT) -> list[str]:
    adoption_path = root / ADOPTION_REL
    agents_path = root / AGENTS_REL
    if not adoption_path.is_file():
        return [f"missing required adoption record: {ADOPTION_REL}"]
    if not agents_path.is_file():
        return [f"missing required agent instructions: {AGENTS_REL}"]
    try:
        record = load_json(adoption_path)
    except Exception as exc:
        return [f"invalid adoption JSON: {exc}"]
    if not isinstance(record, dict):
        return ["adoption record must be an object"]
    return adoption_errors(record, agents_path.read_text(encoding="utf-8"))

def main() -> int:
    errors = repository_errors()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("MATHCERT GCL-AGENT-CONTINUITY-001 adoption: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
