#!/usr/bin/env python3
from __future__ import annotations

import copy
import unittest

import validate_otp_b1_binary_codes_certification as module


class B1CertificationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.adjudication = module.load(module.ADJUDICATION)
        self.contract = module.load(module.CONTRACT)
        self.certificate = module.load(module.CERTIFICATE)
        self.routes = module.load(module.ROUTES)
        self.replay = module.load(module.REPLAY)
        self.work_package = module.load(module.WORK_PACKAGE)

    def errors(self, **kwargs):
        values = {
            "adjudication": copy.deepcopy(self.adjudication),
            "contract": copy.deepcopy(self.contract),
            "certificate": copy.deepcopy(self.certificate),
            "routes": copy.deepcopy(self.routes),
            "replay": copy.deepcopy(self.replay),
            "work_package": copy.deepcopy(self.work_package),
            "check_history": False,
        }
        values.update(kwargs)
        return module.validation_errors(**values)

    def test_current_candidate_passes(self):
        self.assertEqual([], self.errors())

    def test_target_substitution_fails(self):
        cert = copy.deepcopy(self.certificate)
        cert["encoded_targets"][0] = "MetricCodes.Hamming.notTheTarget"
        self.assertTrue(any("certificate target" in item for item in self.errors(certificate=cert)))

    def test_derived_target_reclassification_fails(self):
        cert = copy.deepcopy(self.certificate)
        cert["classifications"][1] = "source_verbatim"
        self.assertTrue(any("classification" in item for item in self.errors(certificate=cert)))

    def test_axiom_inflation_fails(self):
        cert = copy.deepcopy(self.certificate)
        cert["qualification"]["permitted_axioms"].append("sorryAx")
        self.assertTrue(any("axiom" in item for item in self.errors(certificate=cert)))

    def test_proof_promotion_fails(self):
        cert = copy.deepcopy(self.certificate)
        cert["state"]["mathematical_target_proved"] = True
        self.assertTrue(any("authority inflation" in item for item in self.errors(certificate=cert)))

    def test_route_return_to_submitted_fails(self):
        routes = copy.deepcopy(self.routes)
        route = next(item for item in routes["routes"] if item["campaign_id"] == module.FAMILY)
        route["intake_status"] = "submitted"
        self.assertTrue(any("route state" in item for item in self.errors(routes=routes)))

    def test_route_output_drift_fails(self):
        routes = copy.deepcopy(self.routes)
        route = next(item for item in routes["routes"] if item["campaign_id"] == module.FAMILY)
        route["cert_output"]["digest"] = "0" * 40
        self.assertTrue(any("output identity" in item for item in self.errors(routes=routes)))

    def test_replay_rejection_fails(self):
        replay = copy.deepcopy(self.replay)
        replay["producer_replay"]["nanoda"] = "reject"
        self.assertTrue(any("replay result" in item for item in self.errors(replay=replay)))

    def test_minimizer_gate_removal_fails(self):
        adjudication = copy.deepcopy(self.adjudication)
        adjudication["evidence_assessment"]["minimizer_attainment"] = "not_checked"
        self.assertTrue(any("minimizer_attainment" in item for item in self.errors(adjudication=adjudication)))

    def test_independent_review_gate_removal_fails(self):
        adjudication = copy.deepcopy(self.adjudication)
        adjudication["binding_gate"]["fresh_non_author_coding_theory_Lean_specialist_approval_required"] = False
        self.assertTrue(any("binding gate removed" in item for item in self.errors(adjudication=adjudication)))

    def test_certificate_blob_drift_fails(self):
        self.assertTrue(any("certificate blob drift" in item for item in self.errors(local_blobs={"certificate": "0" * 40})))


if __name__ == "__main__":
    unittest.main()
