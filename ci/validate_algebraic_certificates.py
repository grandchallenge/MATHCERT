#!/usr/bin/env python3
"""Validate MATHCERT algebraic certificate artifacts.

This validator intentionally performs lightweight structural checks without
requiring jsonschema. It is a CI guardrail for certificate shape and provenance,
not a mathematical proof checker.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
CERT_ROOT = PACKAGE_ROOT / "certificates" / "algebraic"

REQUIRED = {
    "certificate_id",
    "schema_version",
    "claim_id",
    "certificate_kind",
    "coefficient_domain",
    "variables",
    "monomial_order",
    "trusted_boundary",
    "external_backend",
    "problem",
    "certificate",
    "verification",
}

KINDS = {
    "polynomial_identity",
    "remainder_verification",
    "groebner_basis",
    "ideal_membership",
    "ideal_nonmembership",
    "ideal_equality",
    "radical_membership",
    "finite_truncation",
    "finite_to_infinite_bridge",
    "tropical_initial_ideal",
}

TRUST_BOUNDARIES = {
    "external_output_only",
    "external_certificate_recorded",
    "script_replayed",
    "lean_kernel_checked",
    "integrated_checked_theorem",
}

BACKENDS = {"SageMath", "SymPy", "Singular", "Magma", "Custom"}


def _error(path: Path, message: str) -> str:
    return f"{path}: {message}"


def is_rational_pair(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 2
        and isinstance(value[0], int)
        and isinstance(value[1], int)
        and value[1] > 0
    )


def is_sparse_monomial(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    if not is_rational_pair(value.get("c")):
        return False
    exponents = value.get("e")
    if not isinstance(exponents, list):
        return False
    for pair in exponents:
        if (
            not isinstance(pair, list)
            or len(pair) != 2
            or not isinstance(pair[0], int)
            or not isinstance(pair[1], int)
            or pair[0] < 0
            or pair[1] < 0
        ):
            return False
    return True


def is_sparse_polynomial(value: Any) -> bool:
    return isinstance(value, list) and all(is_sparse_monomial(term) for term in value)


def validate_tropical_initial_ideal(path: Path, data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    certificate = data.get("certificate")
    if not isinstance(certificate, dict):
        return [_error(path, "certificate must be an object")]

    weight = certificate.get("weight")
    if not isinstance(weight, list) or not all(is_rational_pair(entry) for entry in weight):
        errors.append(_error(path, "certificate.weight must be a list of rational pairs"))

    if certificate.get("valuation") not in {"trivial", "nontrivial", "unspecified"}:
        errors.append(_error(path, "certificate.valuation must be trivial, nontrivial, or unspecified"))

    if not isinstance(certificate.get("initial_generators"), list):
        errors.append(_error(path, "certificate.initial_generators must be a list"))

    contains_monomial = certificate.get("contains_monomial")
    if not isinstance(contains_monomial, bool):
        errors.append(_error(path, "certificate.contains_monomial must be boolean"))

    decision = certificate.get("route_decision")
    if decision not in {"retained", "rejected"}:
        errors.append(_error(path, "certificate.route_decision must be retained or rejected"))

    if contains_monomial is True and decision != "rejected":
        errors.append(_error(path, "contains_monomial=true requires route_decision=rejected"))

    if contains_monomial is False and decision != "retained":
        errors.append(_error(path, "contains_monomial=false requires route_decision=retained"))

    if contains_monomial is True and not certificate.get("monomial_witness"):
        errors.append(_error(path, "rejected tropical certificates require a monomial_witness"))

    if contains_monomial is False and certificate.get("monomial_witness"):
        errors.append(_error(path, "retained tropical certificates must not carry a monomial_witness"))

    return errors


def validate_certificate(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [_error(path, f"invalid JSON: {exc}")]

    if not isinstance(data, dict):
        return [_error(path, "top-level value must be an object")]

    missing = REQUIRED - set(data)
    if missing:
        errors.append(_error(path, f"missing required fields {sorted(missing)}"))

    if data.get("schema_version") != "0.1.0":
        errors.append(_error(path, "schema_version must be 0.1.0"))

    if data.get("certificate_kind") not in KINDS:
        errors.append(_error(path, f"invalid certificate_kind {data.get('certificate_kind')!r}"))

    if data.get("trusted_boundary") not in TRUST_BOUNDARIES:
        errors.append(_error(path, f"invalid trusted_boundary {data.get('trusted_boundary')!r}"))

    variables = data.get("variables")
    if not isinstance(variables, dict) or not isinstance(variables.get("names"), list):
        errors.append(_error(path, "variables.names must be a list"))
    elif not all(isinstance(name, str) and name for name in variables["names"]):
        errors.append(_error(path, "variables.names entries must be nonempty strings"))

    backend = data.get("external_backend")
    if not isinstance(backend, dict) or backend.get("name") not in BACKENDS:
        errors.append(_error(path, "external_backend.name must name a supported backend"))

    verification = data.get("verification")
    if not isinstance(verification, dict) or "lean_status" not in verification:
        errors.append(_error(path, "verification.lean_status is required"))
    elif data.get("trusted_boundary") in {"lean_kernel_checked", "integrated_checked_theorem"}:
        if not verification.get("lean_file") or not verification.get("lean_theorem"):
            errors.append(
                _error(path, "Lean-certified boundaries require verification.lean_file and verification.lean_theorem")
            )

    problem = data.get("problem", {})
    for field in ("generators", "target"):
        if field in problem:
            polys = problem[field]
            if not isinstance(polys, list) or not all(is_sparse_polynomial(poly) for poly in polys):
                errors.append(_error(path, f"problem.{field} must be a list of sparse polynomials"))

    if data.get("certificate_kind") == "tropical_initial_ideal":
        errors.extend(validate_tropical_initial_ideal(path, data))

    return errors


def main() -> int:
    if not CERT_ROOT.exists():
        print("No algebraic certificates found; nothing to validate.")
        return 0
    files = sorted(CERT_ROOT.glob("*.json"))
    if not files:
        print("No algebraic certificates found; nothing to validate.")
        return 0

    errors: list[str] = []
    for path in files:
        errors.extend(validate_certificate(path))

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        print(f"Algebraic certificate validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1

    print(f"Validated {len(files)} algebraic certificate(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
