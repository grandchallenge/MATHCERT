from __future__ import annotations

import copy
import unittest

import otp_full_formula_contract_membership as contract_membership
import validate_otp_g_quantum_parallel_repetition_certification as module
import validate_otp_j2_output_contract as j2_design


class QuantumParallelRepetitionCertificationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.values = {name: module.load(path) for name, path in {
            "adjudication": module.ADJUDICATION, "contract": module.CONTRACT,
            "certificate": module.CERTIFICATE, "work_package": module.WORK_PACKAGE,
            "intake": module.INTAKE, "routes": module.ROUTES}.items()}

    def errors(self, **changes):
        values = copy.deepcopy(self.values)
        values.update(changes)
        return module.validation_errors(**values, check_history=False)

    def test_current_candidate_passes(self):
        self.assertEqual([], self.errors())

    def test_target_substitution_fails(self):
        cert = copy.deepcopy(self.values["certificate"]); cert["encoded_targets"][0] = "Quantum.fake"
        self.assertTrue(any("target" in e for e in self.errors(certificate=cert)))

    def test_empty_answer_reclassification_fails(self):
        cert = copy.deepcopy(self.values["certificate"]); cert["classifications"][1] = "source_verbatim_all_domains"
        self.assertTrue(any("classification" in e for e in self.errors(certificate=cert)))

    def test_proof_promotion_fails(self):
        cert = copy.deepcopy(self.values["certificate"]); cert["state"]["mathematical_target_proved"] = True
        self.assertTrue(any("authority inflation" in e for e in self.errors(certificate=cert)))

    def test_specialist_gate_removal_fails(self):
        adj = copy.deepcopy(self.values["adjudication"]); adj["binding_gate"]["fresh_non_author_quantum_information_Lean_specialist_approval_required"] = False
        self.assertTrue(any("binding gate removed" in e for e in self.errors(adjudication=adj)))

    def test_route_output_drift_fails(self):
        routes = copy.deepcopy(self.values["routes"])
        next(r for r in routes["routes"] if r["campaign_id"] == module.FAMILY)["cert_output"]["digest"] = "0" * 40
        self.assertTrue(any("output identity" in e for e in self.errors(routes=routes)))

    def test_certificate_blob_drift_fails(self):
        self.assertTrue(any("certificate blob drift" in e for e in self.errors(local_blobs={"certificate": "0" * 40})))

    def test_legacy_output_contract_membership_admits_exact_g_blob(self):
        self.assertEqual(
            [],
            contract_membership.membership_errors(module.ROOT, set(j2_design.EXPECTED_CONTRACT_FILES)),
        )


if __name__ == "__main__":
    unittest.main()
