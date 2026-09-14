#!/usr/bin/env python3
"""Validate the corpus-level OpenAI Ten Proofs verification record."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "governance/corpus_verifications/OPENAI-TEN-PROOFS-001.json"
SCHEMA = ROOT / "schemas/openai_ten_proofs_corpus_verification.schema.json"
ROUTES = ROOT / "governance/certification_routes.json"

FAMILIES = {
    "OTP-A-SPHERE-PACKING",
    "OTP-B1-BINARY-CODES",
    "OTP-B2-SPHERICAL-CODES",
    "OTP-C-PERMANENT",
    "OTP-D-NON-SOFIC",
    "OTP-E-CONNES-RIGIDITY",
    "OTP-F-EHRHART",
    "OTP-G-QUANTUM-PARALLEL-REPETITION",
    "OTP-H-GAPCVP",
    "OTP-I-RAMSEY",
    "OTP-J1-COMPACTNESS",
    "OTP-J2-TWO-DEGENERATE",
}

EXPECTED = {
    1: ("SpherePacking.lean", "e6117934a80142a8249356fdafa797eba030e920", {"OTP-A-SPHERE-PACKING"}, {"PackingBounds.sharpFullCohnElkiesManuscriptConclusions"}),
    2: ("MetricCodes.lean", "51628c0db81bd6cb9a79777fa601306c9d64cbc5", {"OTP-B1-BINARY-CODES", "OTP-B2-SPHERICAL-CODES"}, {"MetricCodes.Johnson.binaryRate_lt_mrrw", "MetricCodes.Spherical.HigherHierarchy.strict_hierarchy"}),
    3: ("NonSoficGroup.lean", "dd1f8e63960300c8674fcd491007d2a628fbc6fe", {"OTP-D-NON-SOFIC"}, {"SoficGroups.SourceTopLevelCompressionFinal.exists_finitelyPresented_nonsofic_group"}),
    4: ("ConnesRigidity.lean", "81cf03e3f7ccdc66815cc00c9969bcfd2341c8d6", {"OTP-E-CONNES-RIGIDITY"}, {"ConnesRigidity.exists_infinite_pairwise_nonisomorphic_propertyT_icc_groups_with_isomorphic_factors"}),
    5: ("Permanent.lean", "56100e1ae26e6920a569166d0f4cdb4b42b04301", {"OTP-C-PERMANENT"}, {"PermanentFormulaLowerBound.permanent_rational_formula_logarithmic_lower_bound"}),
    6: ("QuantumParallelRepetition.lean", "887c4378f124a5d81a3f2624b6dc34867ec409c4", {"OTP-G-QUANTUM-PARALLEL-REPETITION"}, {"QuantumParallelRepetition.distributionUniformExponential"}),
    7: ("GapCVP.lean", "47f3a395e4d9ec3e2892664860f26ed63421b0c9", {"OTP-H-GAPCVP"}, {"GapCVP.Comparator.gapCVP400IsNPHard"}),
    8: ("EhrhartVolumeInequality.lean", "842c602ab882dfae64352fed0bce2d83c19b31e8", {"OTP-F-EHRHART"}, {"Ehrhart.Volume.ehrhart_volume_inequality_for_sets"}),
    9: ("MulticolorTriangleRamsey.lean", "24b55f531a4d36347cd2277b1b9c7d784d91ae35", {"OTP-I-RAMSEY"}, {"ErdosProblems.MulticolourTriangleRamsey.erdos_problem_183_explicit"}),
    10: ("CompactnessAndDegeneracy.lean", "0e973d50014e8c800af597ef699ef29b81e42fc6", {"OTP-J1-COMPACTNESS", "OTP-J2-TWO-DEGENERATE"}, {"CompactnessConjecture.quantitativeCompactnessCounterexample", "TwoDegenerateGraphs.twoDegenerateExtremalCounterexample"}),
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob(path: Path) -> str:
    payload = path.read_bytes()
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload, usedforsecurity=False).hexdigest()


def validate(record_path: Path = RECORD) -> list[str]:
    errors: list[str] = []
    record = load(record_path)
    schema = load(SCHEMA)
    for failure in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(record):
        errors.append(f"schema {failure.json_path}: {failure.message}")

    results = record.get("results", [])
    if [item.get("ordinal") for item in results] != list(range(1, 11)):
        errors.append("result ordinals must be exactly 1 through 10")

    family_union: set[str] = set()
    declarations: set[str] = set()
    modules: set[str] = set()
    cert_refs: list[dict[str, str]] = []
    for item in results:
        ordinal = item.get("ordinal")
        expected = EXPECTED.get(ordinal)
        if expected is None:
            errors.append(f"unexpected result ordinal {ordinal}")
            continue
        module, module_blob, families, main_declarations = expected
        if item.get("module") != module or item.get("module_blob") != module_blob:
            errors.append(f"result {ordinal}: module identity drift")
        if set(item.get("families", [])) != families:
            errors.append(f"result {ordinal}: family membership drift")
        if set(item.get("main_declarations", [])) != main_declarations:
            errors.append(f"result {ordinal}: main declaration drift")
        family_union.update(item.get("families", []))
        declarations.update(item.get("main_declarations", []))
        modules.add(str(item.get("module")))
        cert_refs.extend(item.get("certificates", []))

    if family_union != FAMILIES:
        errors.append("the twelve-family corpus coverage is incomplete or broadened")
    if len(declarations) != 12:
        errors.append("expected exactly twelve distinct advertised main declarations")
    if len(modules) != 10:
        errors.append("expected exactly ten distinct Lean source modules")

    routes = load(ROUTES).get("routes", [])
    otp_routes = {r.get("campaign_id"): r for r in routes if r.get("campaign_id") in FAMILIES}
    if set(otp_routes) != FAMILIES:
        errors.append("protected route registry does not contain all twelve families")
    for family, route in otp_routes.items():
        if route.get("intake_status") != "qualified":
            errors.append(f"{family}: protected route is not qualified")
        if not route.get("cert_output"):
            errors.append(f"{family}: protected route has no certificate output")

    for ref in cert_refs:
        path = ROOT / ref["path"]
        if not path.is_file():
            errors.append(f"missing certificate {ref['path']}")
            continue
        if git_blob(path) != ref["git_blob_sha1"]:
            errors.append(f"certificate blob drift: {ref['path']}")

    if len({(ref["path"], ref["git_blob_sha1"]) for ref in cert_refs}) != 14:
        errors.append("expected fourteen distinct protected certificate surfaces")
    if record.get("conclusion", {}).get("supplied_lean_formalizations_verified") is not True:
        errors.append("corpus proof-verification conclusion was weakened")
    if record.get("limitations", {}).get("pdf_exposition_line_by_line_equivalence") != "not_required_and_not_asserted":
        errors.append("PDF exposition boundary drift")
    return errors


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else RECORD
    errors = validate(path)
    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        return 1
    print("OPENAI_TEN_PROOFS_CORPUS_VERIFICATION_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
