#!/usr/bin/env python3
"""Replay-check tropical ReLU certificate artifacts.

This checker is deliberately small and independent of PyTorch.  It verifies the
Fixture 001 contract:

* a finite 2D ReLU MLP with non-negative hidden-to-logit weights;
* exact expansion of each logit into a tropical rational form;
* pruning only of affine pieces dominated on the stated box domain;
* a pairwise affine-dominance witness for a certified logit margin.

The checker uses Python's Fraction type throughout.  Floating point arithmetic is
not part of the trusted replay boundary.
"""
from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
CERT_ROOT = PACKAGE_ROOT / "certificates" / "tropic_relu"

REQUIRED_TOP_LEVEL = {
    "certificate_id",
    "schema_version",
    "claim_id",
    "certificate_kind",
    "trusted_boundary",
    "variables",
    "network",
    "tropical_rational",
    "property",
    "artifact_hashes",
    "verification",
}

CERTIFICATE_KIND = "relu_mlp_tropical_margin"
TRUST_BOUNDARIES = {
    "external_output_only",
    "external_certificate_recorded",
    "script_replayed",
    "lean_kernel_checked",
    "integrated_checked_theorem",
}


@dataclass(frozen=True)
class Affine:
    """An exact affine form b + sum_i a_i x_i over named variables."""

    bias: Fraction
    coeffs: tuple[Fraction, ...]

    def __add__(self, other: "Affine") -> "Affine":
        return Affine(self.bias + other.bias, tuple(a + b for a, b in zip(self.coeffs, other.coeffs)))

    def __sub__(self, other: "Affine") -> "Affine":
        return Affine(self.bias - other.bias, tuple(a - b for a, b in zip(self.coeffs, other.coeffs)))

    def scale(self, scalar: Fraction) -> "Affine":
        return Affine(self.bias * scalar, tuple(c * scalar for c in self.coeffs))

    def lower_bound_on_box(self, bounds: list[tuple[Fraction, Fraction]]) -> Fraction:
        total = self.bias
        for coeff, (lo, hi) in zip(self.coeffs, bounds):
            total += coeff * (lo if coeff >= 0 else hi)
        return total

    def as_key(self) -> tuple[Fraction, tuple[Fraction, ...]]:
        return (self.bias, self.coeffs)


def _error(path: Path, message: str) -> str:
    return f"{path}: {message}"


def parse_fraction(value: Any) -> Fraction:
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, str):
        return Fraction(value)
    if isinstance(value, list) and len(value) == 2 and all(isinstance(item, int) for item in value):
        if value[1] == 0:
            raise ValueError("zero denominator")
        return Fraction(value[0], value[1])
    raise ValueError(f"not a rational literal: {value!r}")


def fraction_to_json(value: Fraction) -> list[int]:
    return [value.numerator, value.denominator]


def canonical_payload_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def parse_variables(data: dict[str, Any]) -> tuple[list[str], list[tuple[Fraction, Fraction]], list[str]]:
    errors: list[str] = []
    variables = data.get("variables")
    if not isinstance(variables, dict):
        return [], [], ["variables must be an object"]
    names = variables.get("names")
    if not isinstance(names, list) or not names or not all(isinstance(name, str) and name for name in names):
        errors.append("variables.names must be a nonempty list of names")
        names = []
    domain = variables.get("domain")
    bounds: list[tuple[Fraction, Fraction]] = []
    if not isinstance(domain, dict) or domain.get("kind") != "box":
        errors.append("variables.domain.kind must be 'box'")
    else:
        raw_bounds = domain.get("bounds")
        if not isinstance(raw_bounds, dict):
            errors.append("variables.domain.bounds must be an object keyed by variable name")
        else:
            for name in names:
                raw = raw_bounds.get(name)
                try:
                    if not isinstance(raw, list) or len(raw) != 2:
                        raise ValueError("box bound must be [lo, hi]")
                    lo = parse_fraction(raw[0])
                    hi = parse_fraction(raw[1])
                    if lo > hi:
                        raise ValueError("lower bound exceeds upper bound")
                    bounds.append((lo, hi))
                except (ValueError, TypeError) as exc:
                    errors.append(f"invalid bound for {name}: {exc}")
    return names, bounds, errors


def parse_affine(raw: Any, names: list[str]) -> Affine:
    if not isinstance(raw, dict):
        raise ValueError("affine form must be an object")
    bias = parse_fraction(raw.get("bias", [0, 1]))
    coeff_map = raw.get("coefficients", {})
    if not isinstance(coeff_map, dict):
        raise ValueError("affine coefficients must be an object")
    coeffs = []
    for name in names:
        coeffs.append(parse_fraction(coeff_map.get(name, [0, 1])))
    extra = set(coeff_map) - set(names)
    if extra:
        raise ValueError(f"coefficients mention undeclared variables {sorted(extra)}")
    return Affine(bias, tuple(coeffs))


def term_map(terms: Iterable[dict[str, Any]]) -> dict[str, Affine]:
    result: dict[str, Affine] = {}
    for term in terms:
        term_id = term.get("id")
        if not isinstance(term_id, str) or not term_id:
            raise ValueError("each term requires a nonempty id")
        if term_id in result:
            raise ValueError(f"duplicate term id {term_id!r}")
        result[term_id] = term["_affine"]
    return result


def parse_terms(raw_terms: Any, names: list[str]) -> list[dict[str, Any]]:
    if not isinstance(raw_terms, list):
        raise ValueError("terms must be a list")
    parsed = []
    for raw in raw_terms:
        if not isinstance(raw, dict):
            raise ValueError("term must be an object")
        if "id" not in raw:
            raise ValueError("term missing id")
        affine = parse_affine(raw, names)
        copied = dict(raw)
        copied["_affine"] = affine
        parsed.append(copied)
    return parsed


def canonical_affine_set(forms: Iterable[Affine]) -> set[tuple[tuple[int, int], tuple[tuple[int, int], ...]]]:
    return {
        (tuple(fraction_to_json(form.bias)), tuple(tuple(fraction_to_json(c)) for c in form.coeffs))
        for form in forms
    }


def expand_nonnegative_relu_logit(network: dict[str, Any], logit_name: str, names: list[str]) -> list[Affine]:
    hidden_units = network.get("hidden_units")
    logits = network.get("logits")
    if not isinstance(hidden_units, list) or not isinstance(logits, dict):
        raise ValueError("network.hidden_units and network.logits are required")
    hidden: dict[str, Affine] = {}
    for unit in hidden_units:
        if not isinstance(unit, dict) or unit.get("activation") != "relu":
            raise ValueError("Fixture 001 only supports ReLU hidden units")
        unit_name = unit.get("name")
        if not isinstance(unit_name, str) or not unit_name:
            raise ValueError("hidden unit missing name")
        hidden[unit_name] = parse_affine(unit.get("preactivation"), names)
    logit = logits.get(logit_name)
    if not isinstance(logit, dict):
        raise ValueError(f"missing logit {logit_name!r}")
    base = parse_affine({"bias": logit.get("bias", [0, 1]), "coefficients": {}}, names)
    terms = [base]
    coefficients = logit.get("hidden_coefficients", {})
    if not isinstance(coefficients, dict):
        raise ValueError(f"logit {logit_name!r} hidden_coefficients must be an object")
    for hidden_name, raw_coeff in coefficients.items():
        if hidden_name not in hidden:
            raise ValueError(f"logit {logit_name!r} refers to unknown hidden unit {hidden_name!r}")
        coeff = parse_fraction(raw_coeff)
        if coeff < 0:
            raise ValueError("Fixture 001 exact expansion only supports non-negative hidden-to-logit weights")
        if coeff == 0:
            continue
        shifted = [term + hidden[hidden_name].scale(coeff) for term in terms]
        terms = terms + shifted
    return terms


def validate_hashes(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    hashes = data.get("artifact_hashes")
    if not isinstance(hashes, dict):
        return ["artifact_hashes must be an object"]
    expected_payloads = {
        "network_sha256": data.get("network"),
        "tropical_rational_sha256": data.get("tropical_rational"),
        "property_sha256": data.get("property"),
    }
    for key, payload in expected_payloads.items():
        claimed = hashes.get(key)
        if not isinstance(claimed, str) or len(claimed) != 64:
            errors.append(f"artifact_hashes.{key} must be a 64-character sha256 hex digest")
            continue
        actual = canonical_payload_hash(payload)
        if claimed != actual:
            errors.append(f"artifact_hashes.{key} mismatch: expected {actual}, found {claimed}")
    return errors


def validate_pruning(
    logit_name: str,
    raw_terms: list[dict[str, Any]],
    pruned_terms: list[dict[str, Any]],
    bounds: list[tuple[Fraction, Fraction]],
) -> list[str]:
    errors: list[str] = []
    raw_by_id = term_map(raw_terms)
    kept_by_id = term_map(pruned_terms)
    missing = set(kept_by_id) - set(raw_by_id)
    if missing:
        errors.append(f"{logit_name}: pruned terms not present in raw terms: {sorted(missing)}")
    removed = set(raw_by_id) - set(kept_by_id)
    for removed_id in removed:
        removed_form = raw_by_id[removed_id]
        if not any((kept_form - removed_form).lower_bound_on_box(bounds) >= 0 for kept_form in kept_by_id.values()):
            errors.append(f"{logit_name}: removed term {removed_id!r} is not dominated by any kept term on the box")
    return errors


def validate_property(
    data: dict[str, Any],
    names: list[str],
    bounds: list[tuple[Fraction, Fraction]],
    parsed_logits: dict[str, dict[str, list[dict[str, Any]]]],
) -> list[str]:
    errors: list[str] = []
    prop = data.get("property")
    if not isinstance(prop, dict):
        return ["property must be an object"]
    if prop.get("kind") != "logit_margin_lower_bound":
        return ["property.kind must be logit_margin_lower_bound"]
    greater = prop.get("greater_logit")
    lesser = prop.get("lesser_logit")
    if greater not in parsed_logits or lesser not in parsed_logits:
        return ["property must name existing greater_logit and lesser_logit"]
    try:
        margin = parse_fraction(prop.get("margin"))
    except (ValueError, TypeError) as exc:
        return [f"property.margin invalid: {exc}"]

    greater_num = term_map(parsed_logits[greater]["numerator_pruned_terms"])
    greater_den = term_map(parsed_logits[greater]["denominator_terms"])
    lesser_num = term_map(parsed_logits[lesser]["numerator_pruned_terms"])
    lesser_den = term_map(parsed_logits[lesser]["denominator_terms"])

    witness = prop.get("witness")
    if not isinstance(witness, dict) or witness.get("mode") != "pairwise_affine_dominance":
        return ["property.witness.mode must be pairwise_affine_dominance"]
    cover = witness.get("cover")
    if not isinstance(cover, list):
        return ["property.witness.cover must be a list"]

    required_pairs = {(ln, gd) for ln in lesser_num for gd in greater_den}
    covered_pairs: set[tuple[str, str]] = set()
    for entry in cover:
        if not isinstance(entry, dict):
            errors.append("property witness entries must be objects")
            continue
        ln = entry.get("lesser_numerator_term_id")
        gd = entry.get("greater_denominator_term_id")
        gn = entry.get("greater_numerator_term_id")
        ld = entry.get("lesser_denominator_term_id")
        if ln not in lesser_num or gd not in greater_den or gn not in greater_num or ld not in lesser_den:
            errors.append(f"property witness references unknown term ids: {entry}")
            continue
        covered_pairs.add((ln, gd))
        difference = greater_num[gn] + lesser_den[ld] - lesser_num[ln] - greater_den[gd]
        lower = difference.lower_bound_on_box(bounds)
        if lower < margin:
            errors.append(
                f"witness for lesser numerator {ln!r} and greater denominator {gd!r} gives lower bound "
                f"{lower}, below required margin {margin}"
            )
        if "claimed_min_difference" in entry:
            try:
                claimed = parse_fraction(entry["claimed_min_difference"])
                if lower != claimed:
                    errors.append(f"witness entry {entry} claimed min {claimed}, replay computed {lower}")
            except (ValueError, TypeError) as exc:
                errors.append(f"invalid claimed_min_difference in witness entry {entry}: {exc}")
    missing = required_pairs - covered_pairs
    if missing:
        errors.append(f"property witness does not cover denominator/numerator pairs: {sorted(missing)}")
    return errors


def validate_certificate(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [_error(path, f"invalid JSON: {exc}")]

    if not isinstance(data, dict):
        return [_error(path, "top-level value must be an object")]

    missing = REQUIRED_TOP_LEVEL - set(data)
    if missing:
        errors.append(f"missing required fields {sorted(missing)}")

    if data.get("schema_version") != "0.1.0":
        errors.append("schema_version must be 0.1.0")
    if data.get("certificate_kind") != CERTIFICATE_KIND:
        errors.append(f"certificate_kind must be {CERTIFICATE_KIND}")
    if data.get("trusted_boundary") not in TRUST_BOUNDARIES:
        errors.append(f"invalid trusted_boundary {data.get('trusted_boundary')!r}")

    names, bounds, variable_errors = parse_variables(data)
    errors.extend(variable_errors)
    if errors:
        return [_error(path, error) for error in errors]

    errors.extend(validate_hashes(data))

    tropical = data.get("tropical_rational")
    if not isinstance(tropical, dict) or not isinstance(tropical.get("logits"), dict):
        errors.append("tropical_rational.logits must be an object")
        return [_error(path, error) for error in errors]

    parsed_logits: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for logit_name, logit in tropical["logits"].items():
        if not isinstance(logit_name, str) or not isinstance(logit, dict):
            errors.append("each tropical logit must be an object keyed by name")
            continue
        try:
            raw_terms = parse_terms(logit.get("numerator_raw_terms"), names)
            pruned_terms = parse_terms(logit.get("numerator_pruned_terms"), names)
            denominator_terms = parse_terms(logit.get("denominator_terms"), names)
        except (ValueError, TypeError) as exc:
            errors.append(f"{logit_name}: invalid terms: {exc}")
            continue
        parsed_logits[logit_name] = {
            "numerator_raw_terms": raw_terms,
            "numerator_pruned_terms": pruned_terms,
            "denominator_terms": denominator_terms,
        }

        try:
            expanded = expand_nonnegative_relu_logit(data["network"], logit_name, names)
            pruned_forms = [term["_affine"] for term in pruned_terms]
            if canonical_affine_set(expanded) != canonical_affine_set(pruned_forms):
                errors.append(f"{logit_name}: pruned tropical terms do not exactly match replayed ReLU expansion")
        except (ValueError, TypeError) as exc:
            errors.append(f"{logit_name}: cannot replay ReLU expansion: {exc}")

        if len(denominator_terms) != 1 or denominator_terms[0]["_affine"].as_key() != Affine(Fraction(0), tuple(Fraction(0) for _ in names)).as_key():
            errors.append(f"{logit_name}: Fixture 001 expects a single zero denominator term")

        errors.extend(validate_pruning(logit_name, raw_terms, pruned_terms, bounds))

    if parsed_logits:
        errors.extend(validate_property(data, names, bounds, parsed_logits))

    verification = data.get("verification")
    if not isinstance(verification, dict) or verification.get("checker") != "ci/validate_tropic_relu_certificates.py":
        errors.append("verification.checker must name ci/validate_tropic_relu_certificates.py")

    return [_error(path, error) for error in errors]


def main() -> int:
    if not CERT_ROOT.exists():
        print("No tropical ReLU certificates found; nothing to validate.")
        return 0
    files = sorted(CERT_ROOT.glob("*.json"))
    if not files:
        print("No tropical ReLU certificates found; nothing to validate.")
        return 0

    errors: list[str] = []
    for path in files:
        errors.extend(validate_certificate(path))

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        print(f"Tropical ReLU certificate validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1

    print(f"Validated {len(files)} tropical ReLU certificate(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
