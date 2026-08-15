#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "ci/validate_openai_ten_proofs_permanent_cert_replay_evidence.py"
spec = importlib.util.spec_from_file_location("permanent_replay_evidence", VALIDATOR)
assert spec and spec.loader
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def require_rejected(label: str, **kwargs) -> None:
    errors = v.validation_errors(**kwargs)
    if not errors:
        raise AssertionError(f"mutation unexpectedly accepted: {label}")


def main() -> int:
    baseline_record = v.load(v.RECORD_PATH)
    baseline_registry = v.load(v.REGISTRY_PATH)
    baseline_errors = v.validation_errors()
    if baseline_errors:
        raise AssertionError("baseline replay evidence is invalid:\n" + "\n".join(baseline_errors))

    r = copy.deepcopy(baseline_record); r["execution"]["subject_head_sha"] = "0" * 40
    require_rejected("execution head drift", record=r)
    r = copy.deepcopy(baseline_record); r["execution"]["workflow_run_id"] += 1
    require_rejected("workflow run drift", record=r)
    r = copy.deepcopy(baseline_record); r["actions_artifact"]["sha256"] = "0" * 64
    require_rejected("artifact digest drift", record=r)
    r = copy.deepcopy(baseline_record); r["repository_bundle"]["manifest_sha256"] = "0" * 64
    require_rejected("manifest digest drift", record=r)
    r = copy.deepcopy(baseline_record); r["target_scope"]["circuit_target_count"] = 1
    require_rejected("circuit target insertion", record=r)
    r = copy.deepcopy(baseline_record); r["target_scope"]["theorems"].append("PermanentRollout.permanent_circuit_loglog_lower_bound")
    require_rejected("circuit theorem insertion", record=r)
    r = copy.deepcopy(baseline_record); r["target_scope"]["source_projection"]["gate_bounds_in_replay"] = True
    require_rejected("gate-bound authority inflation", record=r)
    r = copy.deepcopy(baseline_record); r["target_scope"]["source_projection"]["total_leaves_vertices_in_replay"] = True
    require_rejected("total-size authority inflation", record=r)
    r = copy.deepcopy(baseline_record); r["target_scope"]["source_projection"]["historical_pdf_byte_equivalence"] = True
    require_rejected("historical PDF equivalence inflation", record=r)
    r = copy.deepcopy(baseline_record); r["route_state"]["route_proposal_created"] = True
    require_rejected("route proposal inflation", record=r)
    r = copy.deepcopy(baseline_record); r["route_state"]["registered_route"] = "MC-ROUTE-OTP-C-PERMANENT-FORMULA"
    require_rejected("route registration inflation", record=r)
    r = copy.deepcopy(baseline_record); r["route_state"]["may_adjudicate"] = True
    require_rejected("adjudication inflation", record=r)
    r = copy.deepcopy(baseline_record); r["route_state"]["cert_output"] = "forbidden"
    require_rejected("Cert output inflation", record=r)
    r = copy.deepcopy(baseline_record); r["route_state"]["mathematical_target_proved"] = True
    require_rejected("proof promotion", record=r)
    r = copy.deepcopy(baseline_record); r["review_state"]["status"] = "approved"
    require_rejected("premature specialist-review clearance", record=r)

    comparator = (v.EVIDENCE_ROOT / "comparator.log").read_bytes()
    bad_comparator = bytearray(comparator)
    bad_comparator[0] ^= 1
    require_rejected("repository evidence file mutation", file_overrides={"comparator.log": bytes(bad_comparator)})
    manifest = (v.EVIDENCE_ROOT / "SHA256SUMS").read_bytes()
    bad_manifest = manifest.replace(b"13e0245c", b"03e0245c", 1)
    require_rejected("repository evidence manifest mutation", file_overrides={"SHA256SUMS": bad_manifest})
    require_rejected("record blob drift", record_blob_override="0" * 40)
    require_rejected("historical evidence registry drift", historical_blob_override="0" * 40)

    g = copy.deepcopy(baseline_registry); g["execution_state"]["route_proposal_count"] = 1
    require_rejected("successor route proposal count inflation", registry=g)
    g = copy.deepcopy(baseline_registry); g["execution_state"]["specialist_review_count"] = 1
    require_rejected("premature specialist review count", registry=g)
    g = copy.deepcopy(baseline_registry); g["scope"]["gate_bounds_in_replay"] = True
    require_rejected("registry gate-bound inflation", registry=g)
    g = copy.deepcopy(baseline_registry); g["route_controls"]["route_registration_created"] = True
    require_rejected("registry route-registration inflation", registry=g)

    print("Permanent replay-evidence mutation tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
