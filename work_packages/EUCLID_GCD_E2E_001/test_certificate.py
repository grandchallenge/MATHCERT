from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "work_packages" / "EUCLID_GCD_E2E_001" / "check_certificate.py"
SPEC = importlib.util.spec_from_file_location("euclid_gcd_certificate", MODULE_PATH)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)

CANDIDATE = module.load(module.CANDIDATE_PATH)
RECEIPT = module.load(module.RECEIPT_PATH)
CERT = module.load(module.CERT_PATH)
OVERLAY = module.load(module.OVERLAY_PATH)


class EuclidGCDCertificateTests(unittest.TestCase):
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

    def test_changed_quotient_is_rejected(self):
        candidate = copy.deepcopy(CANDIDATE)
        candidate["euclidean_trace"][0]["quotient"] = 3
        self.assertTrue(self.errors(candidate=candidate))

    def test_changed_remainder_is_rejected(self):
        candidate = copy.deepcopy(CANDIDATE)
        candidate["euclidean_trace"][1]["remainder"] = 20
        self.assertTrue(self.errors(candidate=candidate))

    def test_broken_linkage_is_rejected(self):
        candidate = copy.deepcopy(CANDIDATE)
        candidate["euclidean_trace"][1]["dividend"] = 104
        self.assertTrue(self.errors(candidate=candidate))

    def test_non_decreasing_remainder_is_rejected(self):
        candidate = copy.deepcopy(CANDIDATE)
        candidate["euclidean_trace"][0]["remainder"] = 105
        self.assertTrue(self.errors(candidate=candidate))

    def test_truncated_trace_is_rejected(self):
        candidate = copy.deepcopy(CANDIDATE)
        candidate["euclidean_trace"] = candidate["euclidean_trace"][:2]
        self.assertTrue(self.errors(candidate=candidate))

    def test_wrong_terminal_divisor_is_rejected(self):
        candidate = copy.deepcopy(CANDIDATE)
        candidate["result"]["d"] = 7
        self.assertTrue(self.errors(candidate=candidate))

    def test_changed_bezout_coefficient_is_rejected(self):
        candidate = copy.deepcopy(CANDIDATE)
        candidate["bezout_witness"]["x"] = -1
        self.assertTrue(self.errors(candidate=candidate))

    def test_input_substitution_is_rejected(self):
        candidate = copy.deepcopy(CANDIDATE)
        candidate["inputs"]["a"] = 253
        self.assertTrue(self.errors(candidate=candidate))

    def test_zero_zero_widening_is_rejected(self):
        candidate = copy.deepcopy(CANDIDATE)
        candidate["inputs"] = {"a": 0, "b": 0}
        self.assertTrue(self.errors(candidate=candidate))

    def test_candidate_authority_inflation_is_rejected(self):
        candidate = copy.deepcopy(CANDIDATE)
        candidate["authority_state"] = "certified"
        self.assertTrue(self.errors(candidate=candidate))

    def test_solve_identity_drift_is_rejected(self):
        receipt = copy.deepcopy(RECEIPT)
        receipt["solve"]["merge_commit"] = "0" * 40
        self.assertTrue(self.errors(receipt=receipt))

    def test_route_cannot_drop_protected_boundary(self):
        overlay = copy.deepcopy(OVERLAY)
        overlay["protected_effect"] = "immediate"
        self.assertTrue(self.errors(overlay=overlay))

    def test_route_cannot_claim_successor_activation(self):
        overlay = copy.deepcopy(OVERLAY)
        overlay["route"]["successor_stages_activated"] = True
        self.assertTrue(self.errors(overlay=overlay))

    def test_output_cannot_drop_nonclaims(self):
        cert = copy.deepcopy(CERT)
        cert["rejected_or_unclaimed"] = cert["rejected_or_unclaimed"][:-1]
        self.assertTrue(self.errors(cert=cert))


if __name__ == "__main__":
    unittest.main()
