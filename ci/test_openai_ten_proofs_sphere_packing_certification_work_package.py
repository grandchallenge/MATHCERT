#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
from pathlib import Path

import validate_openai_ten_proofs_sphere_packing_certification_work_package as v


def require_reject(label: str, record: dict) -> None:
    errors = v.validation_errors(record=record)
    if not errors:
        raise AssertionError(f"{label}: mutation was accepted")


def mutate(base: dict, path: tuple, value) -> dict:
    out = copy.deepcopy(base)
    cur = out
    for key in path[:-1]:
        cur = cur[key]
    cur[path[-1]] = value
    return out


def main() -> None:
    base = json.loads(v.RECORD_PATH.read_text(encoding="utf-8"))
    if v.validation_errors():
        raise AssertionError("canonical work package does not validate")

    require_reject("source root drift", mutate(base, ("authority", "official_subject", "commit"), "0" * 40))
    require_reject("Solve packet drift", mutate(base, ("authority", "producer_packet", "digest"), "0" * 40))
    require_reject("Forge semantic drift", mutate(base, ("authority", "forge_composite_semantic", "digest"), "0" * 40))
    require_reject("toolchain drift", mutate(base, ("toolchain", "comparator_commit"), "0" * 40))

    swapped = copy.deepcopy(base)
    swapped["target_scope"]["lean_theorems"][0], swapped["target_scope"]["lean_theorems"][1] = (
        swapped["target_scope"]["lean_theorems"][1], swapped["target_scope"]["lean_theorems"][0]
    )
    require_reject("target reorder", swapped)
    shorter = copy.deepcopy(base)
    shorter["target_scope"]["lean_theorems"].pop()
    require_reject("target removal", shorter)
    replaced = copy.deepcopy(base)
    replaced["target_scope"]["lean_theorems"][2] = "PackingBounds.PackingBridge.substitute"
    require_reject("target substitution", replaced)

    extra_axiom = copy.deepcopy(base)
    extra_axiom["execution_contract"]["permitted_axioms"].append("sorryAx")
    require_reject("axiom inflation", extra_axiom)
    erased_qualification = copy.deepcopy(base)
    erased_qualification["target_scope"]["mandatory_qualifications"].pop(1)
    require_reject("qualification erasure", erased_qualification)
    erased_nonvacuity = copy.deepcopy(base)
    erased_nonvacuity["target_scope"]["nonvacuity"]["evidence"].pop()
    require_reject("nonvacuity erasure", erased_nonvacuity)
    changed_command = copy.deepcopy(base)
    changed_command["execution_contract"]["deterministic_commands"][1] = "lake build All"
    require_reject("aggregate replay substitution", changed_command)
    changed_output = copy.deepcopy(base)
    changed_output["execution_contract"]["expected_outputs"][-1] = "ACCEPT"
    require_reject("expected output weakening", changed_output)

    for field, value in [
        ("route_registered", True),
        ("may_adjudicate", True),
        ("adjudication", {"state": "qualified"}),
        ("cert_output", {"certificate": "invented"}),
        ("mathematical_target_proved", True),
        ("aggregate_authority", True),
        ("may_promote_claim", True),
    ]:
        require_reject(f"authority inflation {field}", mutate(base, ("route_state", field), value))

    extra = copy.deepcopy(base)
    extra["new_authority"] = True
    require_reject("schema openness", extra)

    if not v.validation_errors(routes_blob_override="0" * 40):
        raise AssertionError("route registry drift was accepted")
    if not v.validation_errors(historical_blob_override="0" * 40):
        raise AssertionError("historical work-package registry drift was accepted")
    if not v.validation_errors(intake_blob_override="0" * 40):
        raise AssertionError("protected intake drift was accepted")

    print("OTP-A-SPHERE-PACKING work-package adversarial mutation suite: PASS")


if __name__ == "__main__":
    main()
