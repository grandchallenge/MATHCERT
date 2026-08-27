#!/usr/bin/env python3
from __future__ import annotations

import copy
import unittest

import validate_openai_ten_proofs_gapcvp_route_registration as validator


class GapCVPRouteRegistrationTests(unittest.TestCase):
    def receipt(self):
        return validator.load(validator.RECEIPT)

    def routes(self):
        return validator.load(validator.ROUTES)

    def blobs(self):
        return {
            "routes": validator.EXPECTED_ROUTES_BLOB,
            "proposal": validator.EXPECTED_PROPOSAL_BLOB,
            "proposal_registry": validator.EXPECTED_PROPOSAL_REGISTRY_BLOB,
            "intake": validator.EXPECTED_INTAKE_BLOB,
            "work_package": validator.EXPECTED_WORK_PACKAGE_BLOB,
            "replay": validator.EXPECTED_REPLAY_BLOB,
            "readback": validator.EXPECTED_READBACK_BLOB,
        }

    def errors(self, receipt=None, routes=None, blobs=None):
        return validator.validation_errors(
            self.receipt() if receipt is None else receipt,
            self.routes() if routes is None else routes,
            self.blobs() if blobs is None else blobs,
        )

    def reject_receipt(self, mutate):
        receipt = copy.deepcopy(self.receipt())
        mutate(receipt)
        self.assertTrue(self.errors(receipt=receipt))

    def reject_routes(self, mutate):
        routes = copy.deepcopy(self.routes())
        mutate(routes)
        self.assertTrue(self.errors(routes=routes))

    def test_canonical(self):
        self.assertEqual(self.errors(), [])

    def test_route_registry_blob_drift(self):
        blobs = self.blobs(); blobs["routes"] = "0" * 40
        self.assertTrue(self.errors(blobs=blobs))

    def test_proposal_blob_drift(self):
        blobs = self.blobs(); blobs["proposal"] = "0" * 40
        self.assertTrue(self.errors(blobs=blobs))

    def test_replay_blob_drift(self):
        blobs = self.blobs(); blobs["replay"] = "0" * 40
        self.assertTrue(self.errors(blobs=blobs))

    def test_target_substitution(self):
        self.reject_receipt(lambda r: r["registration"]["target_claim_ids"].__setitem__(0, "Fake.target"))

    def test_target_reordering(self):
        self.reject_receipt(lambda r: r["registration"].__setitem__("target_claim_ids", list(reversed(r["registration"]["target_claim_ids"]))))

    def test_promise_broadening(self):
        self.reject_receipt(lambda r: r["registration"]["promise_interfaces"].__setitem__(0, "GapCVP.Comparator.generalRationalTargetPromise"))

    def test_classification_inflation(self):
        self.reject_receipt(lambda r: r["registration"]["classifications"].__setitem__(0, "source_verbatim_full_interface"))

    def test_gap_denominator_as_constant(self):
        self.reject_receipt(lambda r: r["registration"]["gap_factors"].__setitem__(0, "400"))

    def test_axiom_widening(self):
        self.reject_receipt(lambda r: r["registration"]["permitted_axioms"].append("sorryAx"))

    def test_nonvacuity_weakening(self):
        self.reject_receipt(lambda r: r["registration"].__setitem__("nonvacuity_state", "unknown"))

    def test_integer_target_broadening_authority(self):
        self.reject_receipt(lambda r: r["route_controls"].__setitem__("may_broaden_integer_target", True))

    def test_consistent_syndrome_broadening_authority(self):
        self.reject_receipt(lambda r: r["route_controls"].__setitem__("may_broaden_consistent_syndrome", True))

    def test_outside_promise_totalization(self):
        self.reject_receipt(lambda r: r["route_controls"].__setitem__("may_totalize_outside_promise", True))

    def test_input_dependent_p(self):
        self.reject_receipt(lambda r: r["route_controls"].__setitem__("may_make_p_input_dependent", True))

    def test_adjudication_authority(self):
        self.reject_receipt(lambda r: r["route_controls"].__setitem__("may_adjudicate", True))

    def test_output_authority(self):
        self.reject_receipt(lambda r: r["route_controls"].__setitem__("may_issue_cert_output", True))

    def test_proof_promotion(self):
        self.reject_receipt(lambda r: r["route_controls"].__setitem__("may_mark_target_proved", True))

    def test_claim_promotion(self):
        self.reject_receipt(lambda r: r["route_controls"].__setitem__("may_promote_claim", True))

    def test_cross_family_transfer(self):
        self.reject_receipt(lambda r: r["route_controls"].__setitem__("cross_family_transfer_prohibited", False))

    def test_aggregate_authority(self):
        self.reject_receipt(lambda r: r["route_controls"].__setitem__("aggregate_route_prohibited", False))

    def test_schema_rejects_extra_property(self):
        self.reject_receipt(lambda r: r.__setitem__("unexpected", True))

    def test_route_state_must_remain_submitted(self):
        self.reject_routes(lambda r: next(x for x in r["routes"] if x.get("route_id") == validator.ROUTE_ID).__setitem__("intake_status", "qualified"))

    def test_route_output_insertion(self):
        self.reject_routes(lambda r: next(x for x in r["routes"] if x.get("route_id") == validator.ROUTE_ID).__setitem__("cert_output", {"fake": True}))

    def test_route_target_substitution(self):
        self.reject_routes(lambda r: next(x for x in r["routes"] if x.get("route_id") == validator.ROUTE_ID)["target_claim_ids"].__setitem__(0, "Fake.target"))

    def test_aggregate_route_insertion(self):
        self.reject_routes(lambda r: r["routes"].append({"route_id": "MC-ROUTE-OPENAI-TEN-PROOFS-001"}))

    def test_another_family_mutation_changes_pinned_registry_identity(self):
        routes = self.routes()
        next(x for x in routes["routes"] if x.get("route_id") == "MC-ROUTE-OTP-A-SPHERE-PACKING")["target_claim_ids"][0] = "Fake.other.family.target"
        blobs = self.blobs(); blobs["routes"] = "0" * 40
        self.assertTrue(self.errors(routes=routes, blobs=blobs))


if __name__ == "__main__":
    unittest.main()
