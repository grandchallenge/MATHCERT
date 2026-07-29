#!/usr/bin/env python3
"""Regression tests for YAML and JSON claim-ledger rejection paths."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import yaml

import validate_ledgers as module


def valid_mathcert_claim(claim_id: str) -> dict:
    return {
        "claim_id": claim_id,
        "claim_text": "test claim",
        "claim_class": "HEURISTIC",
        "support_type": "HEURISTIC_ARGUMENT",
        "status": "DRAFT",
        "promotion_condition": "Replace with a checked result.",
        "source_or_artifact": ["https://example.com/test-artifact"],
        "knowledge_graph_refs": ["UC-WP04"],
    }


class LedgerValidatorTests(unittest.TestCase):
    def write_yaml(self, path: Path, claims: list[dict]) -> None:
        path.write_text(yaml.safe_dump({"claims": claims}), encoding="utf-8")

    def write_json(self, path: Path, claims: list[dict]) -> None:
        path.write_text(json.dumps({"claims": claims}, indent=2) + "\n", encoding="utf-8")

    def test_current_repository_discovers_ledgers(self) -> None:
        self.assertTrue(module.discover_ledgers())

    def test_yaml_mathcert_record_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "claim_ledger.yaml"
            self.write_yaml(path, [valid_mathcert_claim("TEST-YAML-C001")])
            self.assertEqual(0, module.validate(path, {}))

    def test_json_provider_record_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "claim_ledger.json"
            self.write_json(
                path,
                [{"claim_id": "TEST-JSON-C001", "statement": "provider claim", "status": "OPEN"}],
            )
            self.assertEqual(0, module.validate(path, {}))

    def test_discovery_includes_json_and_yaml(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_yaml(root / "alpha_claim_ledger.yaml", [valid_mathcert_claim("TEST-A")])
            self.write_json(
                root / "beta_claim_ledger.json",
                [{"claim_id": "TEST-B", "statement": "provider claim", "status": "OPEN"}],
            )
            found = {path.suffix for path in module.discover_ledgers([root])}
            self.assertEqual({".yaml", ".json"}, found)

    def test_invalid_class_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "claim_ledger.yaml"
            claim = valid_mathcert_claim("TEST-C001")
            claim["claim_class"] = "NOT_A_CLASS"
            self.write_yaml(path, [claim])
            self.assertGreater(module.validate(path, {}), 0)

    def test_duplicate_fails_across_formats(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "first_claim_ledger.yaml"
            second = root / "second_claim_ledger.json"
            self.write_yaml(first, [valid_mathcert_claim("TEST-C002")])
            self.write_json(
                second,
                [{"claim_id": "TEST-C002", "statement": "duplicate", "status": "OPEN"}],
            )
            seen: dict[str, Path] = {}
            self.assertEqual(0, module.validate(first, seen))
            self.assertGreater(module.validate(second, seen), 0)

    def test_missing_artifact_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "claim_ledger.yaml"
            claim = valid_mathcert_claim("TEST-C003")
            claim["source_or_artifact"] = ["does/not/exist.txt"]
            self.write_yaml(path, [claim])
            self.assertGreater(module.validate(path, {}), 0)

    def test_empty_claim_list_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "claim_ledger.json"
            self.write_json(path, [])
            self.assertGreater(module.validate(path, {}), 0)

    def test_unknown_record_shape_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "claim_ledger.json"
            self.write_json(path, [{"claim_id": "TEST-C004"}])
            self.assertGreater(module.validate(path, {}), 0)


if __name__ == "__main__":
    unittest.main()
