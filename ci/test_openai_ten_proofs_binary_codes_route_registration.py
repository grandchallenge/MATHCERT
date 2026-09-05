#!/usr/bin/env python3
from __future__ import annotations

import copy
import unittest

import validate_openai_ten_proofs_binary_codes_route_registration as validator


class BinaryCodesRouteRegistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.receipt = validator.load(validator.RECEIPT)
        cls.routes = validator.load(validator.ROUTES)

    def errors(self, *, receipt=None, routes=None, local_blobs=None):
        return validator.validation_errors(
            receipt=copy.deepcopy(self.receipt if receipt is None else receipt),
            routes=copy.deepcopy(self.routes if routes is None else routes),
            local_blobs=local_blobs,
        )

    def test_exact_candidate_is_valid(self) -> None:
        self.assertEqual(self.errors(), [])

    def test_route_must_be_unique(self) -> None:
        routes = copy.deepcopy(self.routes)
        route = next(r for r in routes["routes"] if r["route_id"] == validator.ROUTE_ID)
        routes["routes"].append(copy.deepcopy(route))
        self.assertTrue(self.errors(routes=routes))

    def test_aggregate_route_is_rejected(self) -> None:
        routes = copy.deepcopy(self.routes)
        route = copy.deepcopy(routes["routes"][-1])
        route["route_id"] = "MC-ROUTE-OPENAI-TEN-PROOFS-001"
        routes["routes"].append(route)
        self.assertTrue(self.errors(routes=routes))

    def test_provider_predecessor_drift_is_rejected(self) -> None:
        routes = copy.deepcopy(self.routes)
        routes["provider_base_commit"] = "0" * 40
        self.assertTrue(self.errors(routes=routes))

    def test_target_drift_is_rejected(self) -> None:
        routes = copy.deepcopy(self.routes)
        route = next(r for r in routes["routes"] if r["route_id"] == validator.ROUTE_ID)
        route["target_claim_ids"] = route["target_claim_ids"][:-1]
        self.assertTrue(self.errors(routes=routes))

    def test_route_output_insertion_is_rejected(self) -> None:
        routes = copy.deepcopy(self.routes)
        route = next(r for r in routes["routes"] if r["route_id"] == validator.ROUTE_ID)
        route["cert_output"] = {"repository": "grandchallenge/MATHCERT"}
        self.assertTrue(self.errors(routes=routes))

    def test_source_verbatim_inflation_is_rejected(self) -> None:
        receipt = copy.deepcopy(self.receipt)
        receipt["registration"]["classifications"][1] = "source_verbatim"
        self.assertTrue(self.errors(receipt=receipt))

    def test_minimizer_bridge_removal_is_rejected(self) -> None:
        receipt = copy.deepcopy(self.receipt)
        receipt["registration"]["minimizer_attainment_state"] = "not_required"
        self.assertTrue(self.errors(receipt=receipt))

    def test_adjudication_authority_inflation_is_rejected(self) -> None:
        receipt = copy.deepcopy(self.receipt)
        receipt["route_controls"]["may_adjudicate"] = True
        self.assertTrue(self.errors(receipt=receipt))

    def test_proof_promotion_is_rejected(self) -> None:
        receipt = copy.deepcopy(self.receipt)
        receipt["state"]["mathematical_target_proved_count"] = 1
        self.assertTrue(self.errors(receipt=receipt))

    def test_candidate_route_blob_drift_is_rejected(self) -> None:
        self.assertTrue(self.errors(local_blobs={"routes": "0" * 40}))

    def test_proposal_identity_drift_is_rejected(self) -> None:
        self.assertTrue(self.errors(local_blobs={"proposal": "1" * 40}))

    def test_cross_family_authority_inflation_is_rejected(self) -> None:
        receipt = copy.deepcopy(self.receipt)
        receipt["route_controls"]["cross_family_transfer_prohibited"] = False
        self.assertTrue(self.errors(receipt=receipt))


if __name__ == "__main__":
    unittest.main()
