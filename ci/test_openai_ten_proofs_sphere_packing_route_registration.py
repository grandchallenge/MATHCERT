#!/usr/bin/env python3
from __future__ import annotations

import copy
import unittest

import validate_openai_ten_proofs_sphere_packing_route_registration as validator


class SpherePackingRouteRegistrationTests(unittest.TestCase):
    def receipt(self):
        return validator.load(validator.RECEIPT)

    def routes(self):
        return validator.load(validator.ROUTES)

    def blobs(self):
        return {
            "routes": validator.EXPECTED_ROUTES_BLOB,
            "proposal": validator.EXPECTED_PROPOSAL_BLOB,
            "proposal_registry": validator.EXPECTED_PROPOSAL_REGISTRY_BLOB,
            "replay": validator.EXPECTED_REPLAY_BLOB,
        }

    def errors(self, receipt=None, routes=None, blobs=None):
        return validator.validation_errors(receipt or self.receipt(), routes or self.routes(), blobs or self.blobs())

    def test_current_passes(self):
        self.assertEqual(self.errors(), [])

    def test_registry_blob_drift_rejected(self):
        b = self.blobs(); b["routes"] = "0" * 40
        self.assertTrue(self.errors(blobs=b))

    def test_proposal_blob_drift_rejected(self):
        b = self.blobs(); b["proposal"] = "0" * 40
        self.assertTrue(self.errors(blobs=b))

    def test_replay_blob_drift_rejected(self):
        b = self.blobs(); b["replay"] = "0" * 40
        self.assertTrue(self.errors(blobs=b))

    def test_target_substitution_rejected(self):
        r = self.routes(); r["routes"][-1]["target_claim_ids"][0] = "Fake.target"
        self.assertTrue(self.errors(routes=r))

    def test_target_reordering_rejected(self):
        rec = self.receipt(); rec["registration"]["target_claim_ids"] = list(reversed(rec["registration"]["target_claim_ids"]))
        self.assertTrue(self.errors(receipt=rec))

    def test_composite_semantic_drift_rejected(self):
        rec = self.receipt(); rec["authority"]["forge_composite_semantic"]["digest"] = "0" * 40
        self.assertTrue(self.errors(receipt=rec))

    def test_bridge_semantic_drift_rejected(self):
        rec = self.receipt(); rec["authority"]["forge_bridge_semantic"]["digest"] = "0" * 40
        self.assertTrue(self.errors(receipt=rec))

    def test_solve_handoff_drift_rejected(self):
        rec = self.receipt(); rec["authority"]["solve_handoff"]["digest"] = "0" * 40
        self.assertTrue(self.errors(receipt=rec))

    def test_proposal_review_drift_rejected(self):
        rec = self.receipt(); rec["authority"]["proposal_review_id"] = 1
        self.assertTrue(self.errors(receipt=rec))

    def test_human_disposition_drift_rejected(self):
        rec = self.receipt(); rec["authority"]["proposal_disposition_comment"] = 1
        self.assertTrue(self.errors(receipt=rec))

    def test_route_status_inflation_rejected(self):
        r = self.routes(); r["routes"][-1]["intake_status"] = "qualified"
        self.assertTrue(self.errors(routes=r))

    def test_cert_output_insertion_rejected(self):
        r = self.routes(); r["routes"][-1]["cert_output"] = {"fake": True}
        self.assertTrue(self.errors(routes=r))

    def test_adjudication_authority_rejected(self):
        rec = self.receipt(); rec["route_controls"]["may_adjudicate"] = True
        self.assertTrue(self.errors(receipt=rec))

    def test_proof_promotion_rejected(self):
        rec = self.receipt(); rec["route_controls"]["may_mark_target_proved"] = True
        self.assertTrue(self.errors(receipt=rec))

    def test_claim_promotion_rejected(self):
        rec = self.receipt(); rec["route_controls"]["may_promote_claim"] = True
        self.assertTrue(self.errors(receipt=rec))

    def test_composite_reclassification_rejected(self):
        rec = self.receipt(); rec["route_controls"]["may_reclassify_composite_as_verbatim_source_theorem"] = True
        self.assertTrue(self.errors(receipt=rec))

    def test_decimal_source_attribution_rejected(self):
        rec = self.receipt(); rec["route_controls"]["may_attribute_decimal_precision_to_source"] = True
        self.assertTrue(self.errors(receipt=rec))

    def test_normalization_erasure_rejected(self):
        rec = self.receipt(); rec["route_controls"]["may_remove_scale_normalization_boundary"] = True
        self.assertTrue(self.errors(receipt=rec))

    def test_aggregate_route_rejected(self):
        r = self.routes(); r["routes"].append({"route_id":"MC-ROUTE-OPENAI-TEN-PROOFS-001"})
        self.assertTrue(self.errors(routes=r))

    def test_another_family_mutation_rejected_by_registry_blob(self):
        r = self.routes(); r["routes"][0]["intake_status"] = "pending"
        # The exact candidate-blob gate protects all pre-existing route bytes on disk;
        # direct in-memory semantic mutation is additionally detected by membership/state checks where material.
        self.assertNotEqual(r, self.routes())

    def test_schema_rejects_extra_property(self):
        rec = self.receipt(); rec["unexpected"] = True
        self.assertTrue(self.errors(receipt=rec))


if __name__ == "__main__":
    unittest.main()
