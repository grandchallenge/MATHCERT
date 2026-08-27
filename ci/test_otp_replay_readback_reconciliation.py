#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "ci" / "validate_otp_replay_readback_reconciliation.py"
spec = importlib.util.spec_from_file_location("reconcile", MODULE_PATH)
reconcile = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(reconcile)


class ReplayReadbackReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.record = json.loads(reconcile.RECORD.read_text(encoding="utf-8"))

    def errors(self, record):
        return reconcile.validation_errors(record, check_repo=False)

    def test_canonical_record(self):
        self.assertEqual([], reconcile.validation_errors())

    def test_rejects_merge_substitution(self):
        mutated = copy.deepcopy(self.record)
        mutated["families"][0]["protected_merge"] = "0" * 40
        self.assertTrue(self.errors(mutated))

    def test_rejects_review_substitution(self):
        mutated = copy.deepcopy(self.record)
        mutated["families"][1]["non_author_review"]["review_id"] = 1
        self.assertTrue(self.errors(mutated))

    def test_rejects_route_authority_insertion(self):
        mutated = copy.deepcopy(self.record)
        mutated["families"][2]["route_proposed"] = True
        self.assertTrue(self.errors(mutated))

    def test_rejects_candidate_blob_drift(self):
        mutated = copy.deepcopy(self.record)
        mutated["historical_candidate_policy"]["files"][0]["blob"] = "f" * 40
        self.assertTrue(self.errors(mutated))

    def test_rejects_aggregate_authority(self):
        mutated = copy.deepcopy(self.record)
        mutated["preserved_authority"]["aggregate_ten_proofs_authority"] = True
        self.assertTrue(self.errors(mutated))

    def test_rejects_extra_family(self):
        mutated = copy.deepcopy(self.record)
        mutated["families"].append(copy.deepcopy(mutated["families"][0]))
        self.assertTrue(self.errors(mutated))

    def test_schema_is_closed(self):
        mutated = copy.deepcopy(self.record)
        mutated["unauthorized"] = True
        self.assertTrue(any(error.startswith("schema:") for error in self.errors(mutated)))


if __name__ == "__main__":
    unittest.main()
