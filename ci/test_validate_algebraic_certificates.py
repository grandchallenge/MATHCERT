#!/usr/bin/env python3
"""Regression tests for algebraic certificate validation."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from validate_algebraic_certificates import validate_certificate


def valid_certificate() -> dict:
    return {
        "certificate_id": "TEST-GB-001",
        "schema_version": "0.1.0",
        "claim_id": "TEST-C001",
        "certificate_kind": "polynomial_identity",
        "coefficient_domain": "QQ",
        "variables": {"universe": "finite", "names": ["x", "y"], "index_type": "Fin 2"},
        "monomial_order": "lex",
        "trusted_boundary": "lean_kernel_checked",
        "external_backend": {"name": "SymPy", "version": "fixture"},
        "problem": {
            "statement": "(x + y)^2 = x^2 + 2xy + y^2",
            "target": [
                [
                    {"c": [1, 1], "e": [[0, 2]]},
                    {"c": [2, 1], "e": [[0, 1], [1, 1]]},
                    {"c": [1, 1], "e": [[1, 2]]}
                ]
            ],
        },
        "certificate": {"normal_form": []},
        "verification": {
            "lean_status": "checked_local_lemma",
            "lean_file": "MathCert/Algebraic/ToyIdentity.lean",
            "lean_theorem": "MathCert.Algebraic.toy_square_identity",
        },
    }


def write(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)

        good = root / "good.json"
        write(good, valid_certificate())
        assert validate_certificate(good) == []

        bad_kind = root / "bad_kind.json"
        payload = valid_certificate()
        payload["certificate_kind"] = "not_a_kind"
        write(bad_kind, payload)
        assert validate_certificate(bad_kind)

        bad_boundary = root / "bad_boundary.json"
        payload = valid_certificate()
        payload["verification"].pop("lean_theorem")
        write(bad_boundary, payload)
        assert validate_certificate(bad_boundary)

        bad_sparse = root / "bad_sparse.json"
        payload = valid_certificate()
        payload["problem"]["target"] = [[{"c": [1, 0], "e": []}]]
        write(bad_sparse, payload)
        assert validate_certificate(bad_sparse)

    print("Algebraic certificate validator rejection tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
