#!/usr/bin/env python3
from __future__ import annotations

import copy
import unittest

import validate_otp_h_gapcvp_certification as module


class HGapCVPCertificationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.adjudication = module.load(module.ADJUDICATION)
        self.contract = module.load(module.CONTRACT)
        self.certificate = module.load(module.CERTIFICATE)
        self.routes = module.load(module.ROUTES)
        self.replay = module.load(module.REPLAY)
        self.work_package = module.load(module.WORK_PACKAGE)
        self.blobs = {
            "adjudication": module.ADJUDICATION_BLOB,
            "contract": module.CONTRACT_BLOB,
            "certificate": module.CERTIFICATE_BLOB,
            "replay": module.REPLAY_BLOB,
            "work_package": module.WORK_PACKAGE_BLOB,
        }

    def errors(self, **changes):
        values = {
            "adjudication": copy.deepcopy(self.adjudication),
            "contract": copy.deepcopy(self.contract),
            "certificate": copy.deepcopy(self.certificate),
            "routes": copy.deepcopy(self.routes),
            "replay": copy.deepcopy(self.replay),
            "work_package": copy.deepcopy(self.work_package),
            "local_blobs": copy.deepcopy(self.blobs),
            "check_history": False,
        }
        values.update(changes)
        return module.validation_errors(**values)

    def test_baseline(self):
        self.assertEqual([], self.errors())

    def test_route_cannot_remain_submitted(self):
        routes = copy.deepcopy(self.routes)
        next(r for r in routes["routes"] if r["route_id"] == module.ROUTE_ID)["intake_status"] = "submitted"
        self.assertTrue(any("route state" in e for e in self.errors(routes=routes)))

    def test_output_identity_is_exact(self):
        routes = copy.deepcopy(self.routes)
        next(r for r in routes["routes"] if r["route_id"] == module.ROUTE_ID)["cert_output"]["digest"] = "0" * 40
        self.assertTrue(any("output identity" in e for e in self.errors(routes=routes)))

    def test_integer_target_restriction_cannot_be_removed(self):
        adjudication = copy.deepcopy(self.adjudication)
        adjudication["classifications"][0] = "source_faithful_exact_projection"
        self.assertTrue(any("classification" in e for e in self.errors(adjudication=adjudication)))

    def test_consistent_syndrome_restriction_cannot_be_removed(self):
        adjudication = copy.deepcopy(self.adjudication)
        adjudication["classifications"][2] = "source_faithful_exact_projection"
        self.assertTrue(any("classification" in e for e in self.errors(adjudication=adjudication)))

    def test_gap_factor_cannot_be_constantized(self):
        certificate = copy.deepcopy(self.certificate)
        certificate["gap_factors"][0] = "400"
        self.assertTrue(any("gap" in e for e in self.errors(certificate=certificate)))

    def test_outside_promise_totalization_rejected(self):
        adjudication = copy.deepcopy(self.adjudication)
        adjudication["decision"]["does_not_totalize_outside_promise_inputs"] = False
        self.assertTrue(any("outside-promise" in e for e in self.errors(adjudication=adjudication)))

    def test_proof_promotion_rejected(self):
        certificate = copy.deepcopy(self.certificate)
        certificate["state"]["mathematical_target_proved"] = True
        self.assertTrue(any("promotion" in e for e in self.errors(certificate=certificate)))

    def test_axiom_expansion_rejected(self):
        certificate = copy.deepcopy(self.certificate)
        certificate["qualification"]["permitted_axioms"].append("Classical.something")
        self.assertTrue(any("axiom" in e for e in self.errors(certificate=certificate)))

    def test_blob_substitution_rejected(self):
        blobs = copy.deepcopy(self.blobs)
        blobs["certificate"] = "0" * 40
        self.assertTrue(any("certificate blob" in e for e in self.errors(local_blobs=blobs)))

    def test_partial_publication_safeguard_required(self):
        contract = copy.deepcopy(self.contract)
        contract["publication_protocol"]["partial_state_on_protected_main_prohibited"] = False
        self.assertTrue(any("partial_state" in e for e in self.errors(contract=contract)))


if __name__ == "__main__":
    unittest.main()
