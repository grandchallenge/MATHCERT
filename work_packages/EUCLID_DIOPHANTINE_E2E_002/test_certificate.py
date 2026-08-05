from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "work_packages" / "EUCLID_DIOPHANTINE_E2E_002" / "check_certificate.py"
SPEC = importlib.util.spec_from_file_location("euclid_diophantine_certificate", MODULE_PATH)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)

CANDIDATE = module.load(module.CANDIDATE_PATH)
RECEIPT = module.load(module.RECEIPT_PATH)
CERT = module.load(module.CERT_PATH)
OVERLAY = module.load(module.OVERLAY_PATH)


class EuclidDiophantineCertificateTests(unittest.TestCase):
    def errors(self, *, candidate=None, receipt=None, cert=None, overlay=None):
        return module.validation_errors(
            copy.deepcopy(CANDIDATE if candidate is None else candidate),
            copy.deepcopy(RECEIPT if receipt is None else receipt),
            copy.deepcopy(CERT if cert is None else cert),
            copy.deepcopy(OVERLAY if overlay is None else overlay),
            verify_local_blobs=False,
        )

    def test_canonical_package_passes(self):
        self.assertEqual(module.validation_errors(), [])

    def test_positive_input_substitution_is_rejected(self):
        candidate = copy.deepcopy(CANDIDATE)
        candidate["cases"][0]["inputs"]["c"] = 83
        self.assertTrue(self.errors(candidate=candidate))

    def test_positive_scale_drift_is_rejected(self):
        candidate = copy.deepcopy(CANDIDATE)
        candidate["cases"][0]["constructive_solution"]["scale_factor"] = 3
        self.assertTrue(self.errors(candidate=candidate))

    def test_positive_witness_drift_is_rejected(self):
        candidate = copy.deepcopy(CANDIDATE)
        candidate["cases"][0]["constructive_solution"]["x"] = -7
        self.assertTrue(self.errors(candidate=candidate))

    def test_positive_base_bezout_drift_is_rejected(self):
        candidate = copy.deepcopy(CANDIDATE)
        candidate["cases"][0]["constructive_solution"]["base_bezout"]["y"] = 4
        self.assertTrue(self.errors(candidate=candidate))

    def test_positive_obstruction_injection_is_rejected(self):
        candidate = copy.deepcopy(CANDIDATE)
        candidate["cases"][0]["divisibility_obstruction"] = {"remainder": 1}
        self.assertTrue(self.errors(candidate=candidate))

    def test_negative_quotient_drift_is_rejected(self):
        candidate = copy.deepcopy(CANDIDATE)
        candidate["cases"][1]["divisibility_obstruction"]["quotient"] = 1
        self.assertTrue(self.errors(candidate=candidate))

    def test_negative_zero_remainder_is_rejected(self):
        candidate = copy.deepcopy(CANDIDATE)
        candidate["cases"][1]["divisibility_obstruction"]["remainder"] = 0
        self.assertTrue(self.errors(candidate=candidate))

    def test_negative_out_of_range_remainder_is_rejected(self):
        candidate = copy.deepcopy(CANDIDATE)
        candidate["cases"][1]["divisibility_obstruction"]["remainder"] = 21
        self.assertTrue(self.errors(candidate=candidate))

    def test_candidate_authority_inflation_is_rejected(self):
        candidate = copy.deepcopy(CANDIDATE)
        candidate["authority_state"] = "certified"
        self.assertTrue(self.errors(candidate=candidate))

    def test_arbitrary_completeness_claim_is_rejected(self):
        candidate = copy.deepcopy(CANDIDATE)
        candidate["claim_boundary"]["arbitrary_diophantine_completeness_claimed"] = True
        self.assertTrue(self.errors(candidate=candidate))

    def test_timeout_as_unsat_is_rejected(self):
        candidate = copy.deepcopy(CANDIDATE)
        candidate["solver"]["timeout_or_failed_search_used_as_unsat"] = True
        self.assertTrue(self.errors(candidate=candidate))

    def test_recomputed_gcd_is_rejected(self):
        candidate = copy.deepcopy(CANDIDATE)
        candidate["solver"]["recomputes_gcd"] = True
        self.assertTrue(self.errors(candidate=candidate))

    def test_forge_identity_drift_is_rejected(self):
        receipt = copy.deepcopy(RECEIPT)
        receipt["forge"]["merge_commit"] = "0" * 40
        self.assertTrue(self.errors(receipt=receipt))

    def test_stage1_output_identity_drift_is_rejected(self):
        receipt = copy.deepcopy(RECEIPT)
        receipt["protected_stage1"]["certification_output"]["git_blob_sha1"] = "0" * 40
        self.assertTrue(self.errors(receipt=receipt))

    def test_stage2_solve_identity_drift_is_rejected(self):
        receipt = copy.deepcopy(RECEIPT)
        receipt["solve"]["merge_commit"] = "0" * 40
        self.assertTrue(self.errors(receipt=receipt))

    def test_output_cannot_drop_nonclaims(self):
        cert = copy.deepcopy(CERT)
        cert["rejected_or_unclaimed"] = cert["rejected_or_unclaimed"][:-1]
        self.assertTrue(self.errors(cert=cert))

    def test_route_output_blob_drift_is_rejected(self):
        overlay = copy.deepcopy(OVERLAY)
        overlay["route"]["cert_output"]["digest"] = "0" * 40
        self.assertTrue(self.errors(overlay=overlay))

    def test_route_cannot_drop_protected_boundary(self):
        overlay = copy.deepcopy(OVERLAY)
        overlay["protected_effect"] = "immediate"
        self.assertTrue(self.errors(overlay=overlay))

    def test_route_cannot_activate_book_vii(self):
        overlay = copy.deepcopy(OVERLAY)
        overlay["route"]["book_vii_stage_activated"] = True
        self.assertTrue(self.errors(overlay=overlay))

    def test_route_cannot_claim_arbitrary_completeness(self):
        overlay = copy.deepcopy(OVERLAY)
        overlay["route"]["arbitrary_diophantine_completeness_proved"] = True
        self.assertTrue(self.errors(overlay=overlay))


if __name__ == "__main__":
    unittest.main()
