#!/usr/bin/env python3
"""Validate MATHCERT adoption of GCL-AGENT-CONTINUITY-001."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
ADOPTION_REL = ".gcl/agent-continuity.json"
AGENTS_REL = "AGENTS.md"

SCHEMA_AUTHORITY_COMMIT = "7e6b61ddf77e2d73309657d089a98cae84cc735f"
SCHEMA_BLOB_SHA = "b019881a54763a949613c8116260b729742867bd"
LOCAL_VALIDATOR = "ci/validate_agent_continuity_adoption.py"
EMBEDDED_SCHEMA_REF = "embedded:specialization_data.schema_binding.embedded_schema"

EXPECTED = {
    "repository": "grandchallenge/MATHCERT",
    "specialization": "MATHCERT-CERTIFICATION-SAFE-CONTINUITY-001",
    "local_validator": LOCAL_VALIDATOR,
}
EXPECTED_SCHEMA_BINDING = {
    "authority_commit": SCHEMA_AUTHORITY_COMMIT,
    "schema_blob_sha": SCHEMA_BLOB_SHA,
    "local_snapshot": EMBEDDED_SCHEMA_REF,
    "local_snapshot_authoritative": False,
    "mutable_remote_fetch_allowed": False,
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha_bytes(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode("utf-8")
    return hashlib.sha1(header + payload).hexdigest()


def common_schema_errors(record: dict[str, Any]) -> list[str]:
    specialization_data = record.get("specialization_data", {})
    if not isinstance(specialization_data, dict):
        return ["specialization_data must be an object"]

    binding = specialization_data.get("schema_binding", {})
    if not isinstance(binding, dict):
        return ["specialization_data.schema_binding must be an object"]

    embedded = binding.get("embedded_schema")
    if not isinstance(embedded, str) or not embedded:
        return ["specialization_data.schema_binding.embedded_schema must contain the pinned schema"]

    observed_blob = git_blob_sha_bytes(embedded.encode("utf-8"))
    if observed_blob != SCHEMA_BLOB_SHA:
        return [
            f"embedded schema blob mismatch: expected {SCHEMA_BLOB_SHA}, found {observed_blob}"
        ]

    try:
        schema = json.loads(embedded)
        Draft202012Validator.check_schema(schema)
    except Exception as exc:
        return [f"invalid embedded common adoption schema: {exc}"]

    validator = Draft202012Validator(schema)
    return [
        f"common schema {error.json_path}: {error.message}"
        for error in sorted(validator.iter_errors(record), key=lambda item: list(item.path))
    ]


def adoption_errors(record: dict[str, Any], agents_text: str) -> list[str]:
    errors: list[str] = []
    errors.extend(common_schema_errors(record))

    for key, value in EXPECTED.items():
        if record.get(key) != value:
            errors.append(f"{key}: expected {value!r}, found {record.get(key)!r}")

    specialization_data = record.get("specialization_data", {})
    if not isinstance(specialization_data, dict):
        specialization_data = {}

    binding = specialization_data.get("schema_binding", {})
    if not isinstance(binding, dict):
        errors.append("specialization_data.schema_binding must be an object")
        binding = {}
    for key, value in EXPECTED_SCHEMA_BINDING.items():
        if binding.get(key) != value:
            errors.append(
                f"specialization_data.schema_binding.{key}: expected {value!r}, "
                f"found {binding.get(key)!r}"
            )
    expected_binding_keys = set(EXPECTED_SCHEMA_BINDING) | {"embedded_schema"}
    unexpected_binding = set(binding) - expected_binding_keys
    if unexpected_binding:
        errors.append(
            "unexpected Cert schema_binding fields: "
            + ", ".join(sorted(unexpected_binding))
        )

    rebind = specialization_data.get("interruption_rebind", {})
    if not isinstance(rebind, dict):
        errors.append("specialization_data.interruption_rebind must be an object")
        rebind = {}
    for key in (
        "exact_claim_or_subject",
        "certification_route",
        "candidate_artifact",
        "material_evidence_digests",
    ):
        if rebind.get(key) is not True:
            errors.append(f"interruption_rebind.{key} must be true")

    provenance = specialization_data.get("provenance", {})
    if not isinstance(provenance, dict):
        errors.append("specialization_data.provenance must be an object")
        provenance = {}
    for key in ("construction_authorship_preserved", "verification_provenance_preserved"):
        if provenance.get(key) is not True:
            errors.append(f"provenance.{key} must be true")

    succession = specialization_data.get("succession", {})
    if not isinstance(succession, dict):
        errors.append("specialization_data.succession must be an object")
        succession = {}
    if succession.get("operational_state_may_transfer") is not True:
        errors.append("succession.operational_state_may_transfer must be true")
    for key in ("certification_authority_inherited", "substantive_independence_inherited"):
        if succession.get(key) is not False:
            errors.append(f"succession.{key} must be false")
    if succession.get("non_authoring_requirements_re_evaluated_when_materially_affected") is not True:
        errors.append("non-authoring requirements must be re-evaluated when materially affected")

    fail_closed = specialization_data.get("fail_closed", {})
    if not isinstance(fail_closed, dict):
        errors.append("specialization_data.fail_closed must be an object")
        fail_closed = {}
    false_keys = (
        "continuity_receipt_satisfies_independence",
        "continuity_receipt_is_certification_disposition",
        "ci_or_protected_merge_implies_certification",
        "predecessor_agent_conclusion_is_current_certification",
    )
    for key in false_keys:
        if fail_closed.get(key) is not False:
            errors.append(f"fail_closed.{key} must be false")
    for key in (
        "changed_exact_subject_or_evidence_requires_rebind",
        "certification_disposition_fail_closed",
    ):
        if fail_closed.get(key) is not True:
            errors.append(f"fail_closed.{key} must be true")

    unexpected_specialization = set(specialization_data) - {
        "schema_binding",
        "interruption_rebind",
        "provenance",
        "succession",
        "fail_closed",
    }
    if unexpected_specialization:
        errors.append(
            "unexpected Cert specialization_data fields: "
            + ", ".join(sorted(unexpected_specialization))
        )

    authority = record.get("authority_preservation", {})
    if not isinstance(authority, dict):
        errors.append("authority_preservation must be an object")
        authority = {}
    for key in (
        "authority_changed",
        "certification_authority_changed",
        "mathematical_claim_authority_changed",
        "protected_bypass_changed",
    ):
        if authority.get(key) is not False:
            errors.append(f"authority_preservation.{key} must be false")

    required_tokens = (
        "GCL-AGENT-CONTINUITY-001@1.0.0",
        "Operational state may transfer",
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
    print(
        "MATHCERT GCL-AGENT-CONTINUITY-001 adoption: PASS "
        f"(INTELLECT schema {SCHEMA_AUTHORITY_COMMIT}:{SCHEMA_BLOB_SHA})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
