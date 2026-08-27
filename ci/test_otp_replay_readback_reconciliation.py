#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import json
import os
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

    def test_later_live_h_route_does_not_invalidate_historical_readback(self):
        live = copy.deepcopy(json.loads(reconcile.ROUTES.read_text(encoding="utf-8")))
        live.setdefault("routes", []).append({"route_id": "MC-ROUTE-OTP-H-GAPCVP"})
        predecessor = reconcile.load_at_commit(
            reconcile.PROTECTED_PREDECESSOR_HEAD,
            reconcile.ROUTE_REGISTRY_PATH,
        )
        self.assertEqual(
            [],
            reconcile.validation_errors(
                current_routes=live,
                predecessor_routes=predecessor,
                predecessor_route_blob=reconcile.PROTECTED_PREDECESSOR_ROUTE_BLOB,
            ),
        )

    def test_rejects_h_route_at_protected_predecessor(self):
        predecessor = copy.deepcopy(
            reconcile.load_at_commit(
                reconcile.PROTECTED_PREDECESSOR_HEAD,
                reconcile.ROUTE_REGISTRY_PATH,
            )
        )
        predecessor.setdefault("routes", []).append({"route_id": "MC-ROUTE-OTP-H-GAPCVP"})
        errors = reconcile.validation_errors(
            predecessor_routes=predecessor,
            predecessor_route_blob=reconcile.PROTECTED_PREDECESSOR_ROUTE_BLOB,
        )
        self.assertIn("H/B1/B2 route existed at protected replay-readback predecessor", errors)

    def test_rejects_predecessor_route_blob_drift(self):
        predecessor = reconcile.load_at_commit(
            reconcile.PROTECTED_PREDECESSOR_HEAD,
            reconcile.ROUTE_REGISTRY_PATH,
        )
        errors = reconcile.validation_errors(
            predecessor_routes=predecessor,
            predecessor_route_blob="0" * 40,
        )
        self.assertIn("protected predecessor route-registry bytes drift", errors)

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
    scope = os.environ.get("MC_CERT_SCOPE", "")
    if scope and scope != reconcile.FULL_ESTATE_SCOPE:
        print(
            "MATHCERT_CONTEXT_SKIP=ci/test_otp_replay_readback_reconciliation.py "
            f"family=FULL_ESTATE_ONLY active={scope}"
        )
        raise SystemExit(0)
    unittest.main()
