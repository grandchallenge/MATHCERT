#!/usr/bin/env python3
from __future__ import annotations

import copy
import unittest

import validate_otp_j2_output_execution as v


class OTPJ2OutputExecutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = v.load(v.RECORD)
        cls.schema = v.load(v.SCHEMA)
        cls.cert = v.load(v.CERT)
        cls.staged_cert = v.load(v.STAGED_CERT)
        cls.staged_route = v.load(v.STAGED_ROUTE)
        cls.routes = v.load(v.ROUTES)
        cls.history = v.receipt()

    def errors(self, **kwargs):
        args = {
            "record": copy.deepcopy(self.record),
            "schema": copy.deepcopy(self.schema),
            "certificate": copy.deepcopy(self.cert),
            "staged_certificate": copy.deepcopy(self.staged_cert),
            "staged_route": copy.deepcopy(self.staged_route),
            "routes": copy.deepcopy(self.routes),
            "history": copy.deepcopy(self.history),
        }
        args.update(kwargs)
        return v.validation_errors(**args)

    def test_baseline(self):
        self.assertEqual([], self.errors())

    def test_target_inflation_rejected(self):
        cert = copy.deepcopy(self.cert)
        cert["encoded_targets"].append("OtherFamily.theorem")
        self.assertTrue(self.errors(certificate=cert))

    def test_historical_target_reinsertion_rejected(self):
        cert = copy.deepcopy(self.cert)
        cert["encoded_targets"][0] = "TwoDegenerateGraphs.twoDegenerateExtremalCounterexample"
        self.assertTrue(self.errors(certificate=cert))

    def test_stronger_coloring_scope_rejected(self):
        cert = copy.deepcopy(self.cert)
        cert["qualification"]["source_projection"]["stronger_coloring_side_property_in_scope"] = True
        self.assertTrue(self.errors(certificate=cert))

    def test_proof_promotion_rejected(self):
        cert = copy.deepcopy(self.cert)
        cert["state"]["mathematical_target_proved"] = True
        self.assertTrue(self.errors(certificate=cert))

    def test_stronger_coloring_certification_rejected(self):
        cert = copy.deepcopy(self.cert)
        cert["state"]["stronger_coloring_property_certified"] = True
        self.assertTrue(self.errors(certificate=cert))

    def test_disposition_substitution_rejected(self):
        cert = copy.deepcopy(self.cert)
        cert["qualification"]["disposition"] = "qualified_full_source_theorem"
        self.assertTrue(self.errors(certificate=cert))

    def test_route_output_substitution_rejected(self):
        routes = copy.deepcopy(self.routes)
        v.route_of(routes)["cert_output"]["digest"] = "0" * 40
        self.assertTrue(self.errors(routes=routes))

    def test_route_target_substitution_rejected(self):
        routes = copy.deepcopy(self.routes)
        v.route_of(routes)["target_claim_ids"].pop()
        self.assertTrue(self.errors(routes=routes))

    def test_route_state_regression_rejected(self):
        routes = copy.deepcopy(self.routes)
        v.route_of(routes)["intake_status"] = "submitted"
        self.assertTrue(self.errors(routes=routes))

    def test_non_j2_route_mutation_rejected(self):
        history = copy.deepcopy(self.history)
        history["json_route"] = copy.deepcopy(history["json_route"])
        v.others(history["json_route"])[0]["claim_boundary"] = "mutated"
        self.assertTrue(self.errors(history=history))

    def test_certificate_commit_scope_rejected(self):
        history = copy.deepcopy(self.history)
        history["content_files"] = [v.CERT_PATH, "other"]
        self.assertTrue(self.errors(history=history))

    def test_route_commit_scope_rejected(self):
        history = copy.deepcopy(self.history)
        history["route_files"] = [v.ROUTES_PATH, "other"]
        self.assertTrue(self.errors(history=history))

    def test_route_first_or_non_direct_chain_rejected(self):
        history = copy.deepcopy(self.history)
        history["route_parent"] = v.BASE
        self.assertTrue(self.errors(history=history))

    def test_ancestry_rejected(self):
        history = copy.deepcopy(self.history)
        history["route_head"] = False
        self.assertTrue(self.errors(history=history))

    def test_certificate_byte_drift_rejected(self):
        history = copy.deepcopy(self.history)
        history["cert_head"] = "0" * 40
        self.assertTrue(self.errors(history=history))

    def test_route_registry_after_drift_rejected(self):
        history = copy.deepcopy(self.history)
        history["routes_head"] = "0" * 40
        self.assertTrue(self.errors(history=history))

    def test_staged_transition_commit_rejected(self):
        staged = copy.deepcopy(self.staged_route)
        staged["route_transition"]["route_transition_commit"] = "0" * 40
        self.assertTrue(self.errors(staged_route=staged))

    def test_staged_certificate_drift_rejected(self):
        staged = copy.deepcopy(self.staged_cert)
        staged["claim_boundary"] += " mutated"
        self.assertTrue(self.errors(staged_certificate=staged))

    def test_review_prepopulation_rejected(self):
        record = copy.deepcopy(self.record)
        record["review_gate"]["recorded_review"] = {"state": "APPROVED"}
        self.assertTrue(self.errors(record=record))

    def test_redundant_human_steward_gate_rejected(self):
        record = copy.deepcopy(self.record)
        record["publication_gate"]["separate_human_steward_authorization_required"] = True
        self.assertTrue(self.errors(record=record))

    def test_squash_permission_rejected(self):
        record = copy.deepcopy(self.record)
        record["publication_gate"]["squash_merge_prohibited"] = False
        self.assertTrue(self.errors(record=record))

    def test_partial_main_permission_rejected(self):
        record = copy.deepcopy(self.record)
        record["publication_gate"]["partial_protected_main_state_prohibited"] = False
        self.assertTrue(self.errors(record=record))

    def test_aggregate_authority_rejected(self):
        record = copy.deepcopy(self.record)
        record["branch_execution_state"]["aggregate_output"] = True
        self.assertTrue(self.errors(record=record))


if __name__ == "__main__":
    unittest.main(verbosity=2)
