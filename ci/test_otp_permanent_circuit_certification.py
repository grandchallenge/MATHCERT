#!/usr/bin/env python3
from __future__ import annotations

import copy

import validate_otp_permanent_circuit_certification as V


def expect_fail(records, label: str):
    errors = V.validation_errors(records, check_git=False)
    if not errors:
        raise AssertionError(f"mutation unexpectedly accepted: {label}")


def main() -> int:
    base = V.records_from_disk()

    m = copy.deepcopy(base)
    m["intake"]["target_scope"]["source_projection"]["dimension_threshold"] = 65535
    expect_fail(m, "threshold drift")

    m = copy.deepcopy(base)
    m["intake"]["target_scope"]["source_projection"]["finite_bound_denominator"] = 143
    expect_fail(m, "denominator drift")

    m = copy.deepcopy(base)
    m["intake"]["target_scope"]["source_projection"]["division_allowed"] = True
    expect_fail(m, "division enabled")

    m = copy.deepcopy(base)
    m["intake"]["target_scope"]["source_projection"]["fanout_reuse_allowed"] = False
    expect_fail(m, "fanout reuse removed")

    m = copy.deepcopy(base)
    m["intake"]["target_scope"]["lean_theorems"] = V.TARGETS[:2]
    expect_fail(m, "asymptotic target omitted")

    m = copy.deepcopy(base)
    m["proposal"]["route_contract"]["target_claim_ids"].append("PermanentFormulaLowerBound.permanent_rational_formula_lower_bound")
    expect_fail(m, "formula target insertion")

    m = copy.deepcopy(base)
    m["route"]["route"]["intake_status"] = "qualified"
    expect_fail(m, "premature route qualification")

    m = copy.deepcopy(base)
    m["route"]["route"]["cert_output"] = {"forged": True}
    expect_fail(m, "premature cert output")

    m = copy.deepcopy(base)
    m["adjudication"]["judgment"]["mathematical_target_proved"] = True
    expect_fail(m, "proof promotion")

    m = copy.deepcopy(base)
    m["staged_certificate"]["state"]["candidate_only"] = False
    expect_fail(m, "candidate boundary removal")

    m = copy.deepcopy(base)
    m["transition"]["candidate_authorization"]["reviewed_candidate_head"] = "deadbeef"
    expect_fail(m, "fabricated candidate approval")

    m = copy.deepcopy(base)
    m["transition"]["publication_constraints"]["squash_prohibited"] = False
    expect_fail(m, "squash enabled")

    print("OTP Permanent circuit adversarial mutations all rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
