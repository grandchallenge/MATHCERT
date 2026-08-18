#!/usr/bin/env python3
from __future__ import annotations

import copy
import json

import validate_openai_ten_proofs_gapcvp_certification_work_package as v


def mutate(base: dict, path: tuple, value) -> dict:
    out = copy.deepcopy(base)
    cur = out
    for key in path[:-1]:
        cur = cur[key]
    cur[path[-1]] = value
    return out


def reject(label: str, record: dict) -> None:
    if not v.validation_errors(record=record):
        raise AssertionError(f"{label}: mutation was accepted")


def main() -> None:
    base = json.loads(v.RECORD_PATH.read_text(encoding="utf-8"))
    if v.validation_errors():
        raise AssertionError("canonical GapCVP work package does not validate")

    reject("source root drift", mutate(base, ("authority", "official_subject", "commit"), "0" * 40))
    reject("Solve packet drift", mutate(base, ("authority", "producer_packet", "digest"), "0" * 40))
    reject("Forge semantic drift", mutate(base, ("authority", "forge_semantic", "digest"), "0" * 40))
    reject("toolchain drift", mutate(base, ("toolchain", "mathlib_commit"), "0" * 40))

    swapped = copy.deepcopy(base)
    swapped["target_scope"]["lean_theorems"][0], swapped["target_scope"]["lean_theorems"][1] = swapped["target_scope"]["lean_theorems"][1], swapped["target_scope"]["lean_theorems"][0]
    reject("target reorder", swapped)
    promise_swap = copy.deepcopy(base)
    promise_swap["target_scope"]["promise_interfaces"][0], promise_swap["target_scope"]["promise_interfaces"][1] = promise_swap["target_scope"]["promise_interfaces"][1], promise_swap["target_scope"]["promise_interfaces"][0]
    reject("promise reorder", promise_swap)
    reject("gap factor inflation", mutate(base, ("target_scope", "gap_factors"), ["400", "200", "200", "200p"]))

    extra_axiom = copy.deepcopy(base)
    extra_axiom["execution_contract"]["permitted_axioms"].append("sorryAx")
    reject("axiom inflation", extra_axiom)
    aggregate_build = copy.deepcopy(base)
    aggregate_build["execution_contract"]["deterministic_commands"][1] = "lake build All"
    reject("aggregate replay substitution", aggregate_build)
    weakened_output = copy.deepcopy(base)
    weakened_output["execution_contract"]["expected_outputs"][-1] = "ACCEPT"
    reject("expected output weakening", weakened_output)

    erased_qualification = copy.deepcopy(base)
    erased_qualification["target_scope"]["mandatory_qualifications"].pop(1)
    reject("integer-target qualification erasure", erased_qualification)
    erased_qualification = copy.deepcopy(base)
    erased_qualification["target_scope"]["mandatory_qualifications"].pop(2)
    reject("consistent-syndrome qualification erasure", erased_qualification)
    erased_witness = copy.deepcopy(base)
    erased_witness["target_scope"]["nonvacuity"]["witnesses"].pop()
    reject("nonvacuity witness erasure", erased_witness)

    for field, value in [
        ("route_registered", True),
        ("may_adjudicate", True),
        ("adjudication", {"state": "qualified"}),
        ("cert_output", {"certificate": "invented"}),
        ("mathematical_target_proved", True),
        ("aggregate_authority", True),
        ("may_promote_claim", True),
    ]:
        reject(f"authority inflation {field}", mutate(base, ("route_state", field), value))

    extra = copy.deepcopy(base)
    extra["new_authority"] = True
    reject("schema openness", extra)

    if not v.validation_errors(routes_blob_override="0" * 40):
        raise AssertionError("route registry drift was accepted")
    if not v.validation_errors(predecessor_blob_override="0" * 40):
        raise AssertionError("protected A predecessor work-package drift was accepted")
    if not v.validation_errors(intake_blob_override="0" * 40):
        raise AssertionError("protected H intake drift was accepted")

    print("OTP-H-GAPCVP work-package adversarial mutation suite: PASS")


if __name__ == "__main__":
    main()
