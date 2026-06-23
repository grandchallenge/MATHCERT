#!/usr/bin/env python3
"""Regression tests for tropical ReLU certificate replay."""
from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

from validate_tropic_relu_certificates import validate_certificate


def canonical_payload_hash(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def fixture_certificate() -> dict:
    root = Path(__file__).resolve().parents[1]
    return json.loads((root / "certificates" / "tropic_relu" / "fixture_001_relu_mlp_margin.json").read_text())


def refresh_hashes(payload: dict) -> None:
    payload["artifact_hashes"] = {
        "network_sha256": canonical_payload_hash(payload["network"]),
        "tropical_rational_sha256": canonical_payload_hash(payload["tropical_rational"]),
        "property_sha256": canonical_payload_hash(payload["property"]),
    }


def write(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def assert_rejected(path: Path, phrase: str) -> None:
    errors = validate_certificate(path)
    assert errors, f"{path} was expected to be rejected"
    assert any(phrase in error for error in errors), f"missing {phrase!r} in {errors}"


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)

        good = root / "good.json"
        payload = fixture_certificate()
        write(good, payload)
        assert validate_certificate(good) == []

        stale_hash = root / "stale_hash.json"
        payload = fixture_certificate()
        payload["network"]["description"] += " drift"
        write(stale_hash, payload)
        assert_rejected(stale_hash, "network_sha256 mismatch")

        impossible_margin = root / "impossible_margin.json"
        payload = fixture_certificate()
        payload["property"]["margin"] = [2, 1]
        refresh_hashes(payload)
        write(impossible_margin, payload)
        assert_rejected(impossible_margin, "below required margin")

        unsafe_prune = root / "unsafe_prune.json"
        payload = fixture_certificate()
        class1 = payload["tropical_rational"]["logits"]["class_1"]
        class1["numerator_pruned_terms"] = [
            term for term in class1["numerator_pruned_terms"] if term["id"] != "class1_sum"
        ]
        refresh_hashes(payload)
        write(unsafe_prune, payload)
        assert_rejected(unsafe_prune, "do not exactly match replayed ReLU expansion")

        bad_domain = root / "bad_domain.json"
        payload = fixture_certificate()
        payload["variables"]["domain"]["bounds"]["x1"] = [2, -2]
        refresh_hashes(payload)
        write(bad_domain, payload)
        assert_rejected(bad_domain, "lower bound exceeds upper bound")

    print("Tropical ReLU certificate validator rejection tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
