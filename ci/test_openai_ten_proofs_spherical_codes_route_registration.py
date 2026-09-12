#!/usr/bin/env python3
from __future__ import annotations

import copy
import unittest

import validate_openai_ten_proofs_spherical_codes_route_registration as validator


class SphericalCodesRouteRegistrationTests(unittest.TestCase):
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

    def test_duplicate_route_is_rejected(self) -> None:
        routes = copy.deepcopy(self.routes)
        route = next(row for row in routes["routes"] if row["route_id"] == validator.ROUTE_ID)
        routes["routes"].append(copy.deepcopy(route))
        self.assertTrue(self.errors(routes=routes))

    def test_target_drift_is_rejected(self) -> None:
        routes = copy.deepcopy(self.routes)
        route = next(row for row in routes["routes"] if row["route_id"] == validator.ROUTE_ID)
        route["target_claim_ids"] = route["target_claim_ids"][:-1]
        self.assertTrue(self.errors(routes=routes))

    def test_output_insertion_is_rejected(self) -> None:
        routes = copy.deepcopy(self.routes)
        route = next(row for row in routes["routes"] if row["route_id"] == validator.ROUTE_ID)
        route["cert_output"] = {"path": "invented"}
        self.assertTrue(self.errors(routes=routes))

    def test_formal_strengthening_inflation_is_rejected(self) -> None:
        receipt = copy.deepcopy(self.receipt)
        receipt["registration"]["classifications"][-1] = "source_verbatim"
        self.assertTrue(self.errors(receipt=receipt))

    def test_adjudication_authority_is_rejected(self) -> None:
        receipt = copy.deepcopy(self.receipt)
        receipt["route_controls"]["may_adjudicate"] = True
        self.assertTrue(self.errors(receipt=receipt))

    def test_candidate_blob_drift_is_rejected(self) -> None:
        self.assertTrue(self.errors(local_blobs={"routes": "0" * 40}))


if __name__ == "__main__":
    unittest.main()
