#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
RECORD_PATH = ROOT / "governance/result_family_work_package_successors/OTP-H-GAPCVP-CERT-WP-001.json"
SCHEMA_PATH = ROOT / "schemas/openai_ten_proofs_gapcvp_certification_work_package.schema.json"
INTAKE_PATH = ROOT / "governance/result_family_intake_successors/OTP-H-GAPCVP.json"
PREDECESSOR_WP = ROOT / "governance/result_family_work_package_successors/OTP-A-SPHERE-PACKING-CERT-WP-001.json"
ROUTES = ROOT / "governance/certification_routes.json"

EXPECTED_RECORD_BLOB = "0f811d163f0d36b028cf6539963e2cf278517137"
EXPECTED_INTAKE_BLOB = "a171482c04f62134812ed6084e19a9b803db3478"
EXPECTED_PREDECESSOR_WP_BLOB = "f0c91d1959035f35843c383920dfba0b6c24b485"
PRE_REGISTRATION_ROUTES_BLOB = "2d17473b4731aa9d9c630b1e7777ad4bd794d993"
A_REGISTRATION_ROUTES_BLOB = "b9bb0dc9e18856f50a88162df37c20c034327439"
FUTURE_ROUTE_ID = "MC-ROUTE-OTP-H-GAPCVP"

EXPECTED_TARGETS = [
    "GapCVP.Comparator.gapCVP400IsNPHard",
    "GapCVP.Comparator.binaryNearestCodewordIsNPHard",
    "GapCVP.Comparator.binarySyndromeDecodingIsNPHard",
    "GapCVP.Comparator.finitePNormGapCVPIsNPHard",
]
EXPECTED_PROMISES = [
    "GapCVP.Comparator.gapCVP400Promise",
    "GapCVP.Comparator.binaryNearestCodewordPromise",
    "GapCVP.Comparator.binarySyndromeDecodingPromise",
    "GapCVP.Comparator.finitePGapCVPPromise",
]
EXPECTED_CLASSIFICATIONS = [
    "source_faithful_restricted_consequence_integer_target",
    "source_faithful_up_to_generator_orientation",
    "source_faithful_restricted_consequence_consistent_syndrome",
    "source_faithful_fixed_rational_p_consequence",
]
EXPECTED_GAPS = ["n^(1/400)", "n^(1/200)", "n^(1/200)", "n^(1/(200p))"]
EXPECTED_QUALIFICATIONS = [
    "400, 200 and 200p are exponent denominators in dimension-dependent gaps, not constant approximation factors.",
    "The Euclidean formal promise is restricted to integer targets, matching the source Theorem 1 reduction output rather than the source's most general rational-target interface.",
    "The syndrome NO side is restricted to consistent systems sufficient for the source Corollary 15 reduction.",
    "Binary generator row/column orientation is treated only as a transpose convention preserving the represented code.",
    "Malformed/non-encoding and threshold-intermediate bitstrings remain outside the promise.",
    "The finite-p theorem parameter p is fixed rational with 1 <= p and is external to the input encoding.",
    "Forge replay and semantic admission do not independently certify NP-hardness proof correctness.",
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data, usedforsecurity=False).hexdigest()


def schema_errors(instance: dict) -> list[str]:
    validator = Draft202012Validator(load(SCHEMA_PATH))
    return [
        f"schema: {'/'.join(map(str, e.absolute_path)) or '<root>'}: {e.message}"
        for e in sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path))
    ]


def import_errors(path: Path, name: str) -> list[str]:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        if hasattr(module, "validation_errors"):
            return list(module.validation_errors())
        if hasattr(module, "validate_record") and hasattr(module, "validate_repository_guards"):
            module.validate_record(module.load_record())
            module.validate_repository_guards()
            return []
        raise RuntimeError(f"unsupported validator interface: {path}")
    except Exception as exc:
        return [str(exc)]


def validation_errors(
    record: dict | None = None,
    *,
    record_blob_override: str | None = None,
    intake_blob_override: str | None = None,
    predecessor_blob_override: str | None = None,
    routes_blob_override: str | None = None,
) -> list[str]:
    errors: list[str] = []
    record = load(RECORD_PATH) if record is None else record
    errors.extend(schema_errors(record))

    if (git_blob_sha1(RECORD_PATH) if record_blob_override is None else record_blob_override) != EXPECTED_RECORD_BLOB:
        errors.append("GapCVP work-package record blob drift")
    if (git_blob_sha1(INTAKE_PATH) if intake_blob_override is None else intake_blob_override) != EXPECTED_INTAKE_BLOB:
        errors.append("protected GapCVP intake record drift")
    if (git_blob_sha1(PREDECESSOR_WP) if predecessor_blob_override is None else predecessor_blob_override) != EXPECTED_PREDECESSOR_WP_BLOB:
        errors.append("protected predecessor A work-package drift")
    routes_blob = git_blob_sha1(ROUTES) if routes_blob_override is None else routes_blob_override
    if routes_blob not in {PRE_REGISTRATION_ROUTES_BLOB, A_REGISTRATION_ROUTES_BLOB}:
        errors.append("certification route registry is neither protected work-package snapshot nor exact A registration successor")

    intake_errors = import_errors(ROOT / "ci/validate_openai_ten_proofs_gapcvp_intake_successor.py", "gapcvp_intake")
    if intake_errors:
        errors.append("protected GapCVP intake validation failed: " + "; ".join(intake_errors))
    predecessor_errors = import_errors(ROOT / "ci/validate_openai_ten_proofs_sphere_packing_certification_work_package.py", "sphere_wp")
    if predecessor_errors:
        errors.append("protected predecessor A work-package validation failed: " + "; ".join(predecessor_errors))

    authority = record.get("authority", {})
    if authority.get("protected_mathcert_base") != "54b883bb5c6ffaf099efd7270df3519a45b13038": errors.append("protected MATHCERT base drift")
    if authority.get("cert_intake_merge") != "ff9fa0a67a5a809f3519e0059f2ef9b082b1febb": errors.append("GapCVP intake merge drift")
    if authority.get("intake_record", {}).get("digest") != EXPECTED_INTAKE_BLOB: errors.append("GapCVP intake binding drift")
    if authority.get("producer_packet", {}).get("digest") != "0dd2b38e40a126a1a2a2d57989038f788b8e40e4": errors.append("Solve producer packet drift")
    if authority.get("forge_semantic", {}).get("digest") != "673f541fbb552d307cc226c51d2f0fd2916b328d": errors.append("Forge semantic record drift")
    official = authority.get("official_subject", {})
    if official.get("commit") != "94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6" or official.get("tree") != "174289e4d4958cb0509874e6e53400e098213de7": errors.append("official source root/tree drift")

    toolchain = record.get("toolchain", {})
    for key, value in {
        "lean_commit": "8c9756b28d64dab099da31a4c09229a9e6a2ef35",
        "comparator_commit": "07bc4ea40f2266dcb861820a2ec1fa3244ed307f",
        "mathlib_commit": "81a5d257c8e410db227a6665ed08f64fea08e997",
        "lean4export_commit": "4e7915201d3f9f04470d9eae002fa695f7cdc589",
        "lean4checker_commit": "b7398199245524275543dec6113229c9bb4902e5",
        "nanoda_commit": "ddfac2bf5a7b56cb46e141494427ff3dd55963c7",
        "landrun_commit": "811cfff51ceaf3d9843708aa6d22e9b84ccac8b4",
    }.items():
        if toolchain.get(key) != value: errors.append(f"toolchain drift: {key}")

    execution = record.get("execution_contract", {})
    if execution.get("deterministic_commands") != ["lake exe cache get", "lake build GapCVP", "lake exe comparator ComparatorChallenges/H_GapCVP.json"]: errors.append("deterministic replay command drift")
    if execution.get("expected_outputs") != ["Nanoda kernel accepts the solution", "Lean default kernel accepts the solution", "Your solution is okay!", "OTP_SUCCESSOR_COMPARATOR=ACCEPT"]: errors.append("expected replay-output drift")
    if execution.get("permitted_axioms") != ["propext", "Classical.choice", "Quot.sound"]: errors.append("permitted-axiom boundary drift")
    if execution.get("expected_exported_target_count") != 4 or execution.get("expected_exported_promise_definition_count") != 4: errors.append("export-count boundary drift")

    scope = record.get("target_scope", {})
    if scope.get("lean_theorems") != EXPECTED_TARGETS: errors.append("GapCVP target membership/order drift")
    if scope.get("promise_interfaces") != EXPECTED_PROMISES: errors.append("GapCVP promise-interface membership/order drift")
    if scope.get("classifications") != EXPECTED_CLASSIFICATIONS: errors.append("GapCVP semantic classification drift")
    if scope.get("gap_factors") != EXPECTED_GAPS: errors.append("GapCVP gap-factor drift")
    if scope.get("mandatory_qualifications") != EXPECTED_QUALIFICATIONS: errors.append("GapCVP mandatory qualification drift")
    nonvacuity = scope.get("nonvacuity", {})
    witnesses = nonvacuity.get("witnesses", [])
    if nonvacuity.get("yes_witness_count") != 4 or nonvacuity.get("no_witness_count") != 4 or len(witnesses) != 4: errors.append("GapCVP nonvacuity witness matrix drift")
    if [w.get("promise") for w in witnesses] != EXPECTED_PROMISES: errors.append("GapCVP nonvacuity witness/promise alignment drift")

    route = record.get("route_state", {})
    zero_authority = {"certification_route_registry_entry":None,"route_registered":False,"may_adjudicate":False,"adjudication":None,"cert_output":None,"mathematical_target_proved":False,"aggregate_authority":False,"may_promote_claim":False}
    if any(route.get(k) != v for k, v in zero_authority.items()): errors.append("GapCVP historical work-package route/adjudication/output/proof authority inflation")
    route_ids = [r.get("route_id") for r in load(ROUTES).get("routes", []) if isinstance(r, dict)]
    if FUTURE_ROUTE_ID in route_ids: errors.append("future GapCVP route is already registered")
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("OTP-H-GAPCVP executable certification work package validation: PASS; immutable work-package authority preserved across exact separately governed A route registration")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
