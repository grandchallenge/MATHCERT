#!/usr/bin/env python3
import copy
import unittest
from validate_rm_dio_004_certificate import certificate_errors, load_certificate

class ResearchMathCertificateTests(unittest.TestCase):
    def setUp(self): self.certificate = load_certificate()
    def test_committed_certificate(self): self.assertEqual(certificate_errors(self.certificate), [])
    def test_rejects_upstream_commit_drift(self):
        changed = copy.deepcopy(self.certificate); changed["upstream"]["mathsolve_protected_commit"] = "0" * 40; self.assertTrue(certificate_errors(changed))
    def test_rejects_blob_drift(self):
        changed = copy.deepcopy(self.certificate); changed["upstream"]["handoff_blob_sha1"] = "0" * 40; self.assertTrue(certificate_errors(changed))
    def test_rejects_missing_solution(self):
        changed = copy.deepcopy(self.certificate); changed["solutions"].pop(); changed["solution_count"] -= 1; self.assertTrue(certificate_errors(changed))
    def test_rejects_bound_inflation(self):
        changed = copy.deepcopy(self.certificate); changed["domain"]["maximum"] += 1; self.assertTrue(certificate_errors(changed))
    def test_rejects_unbounded_claim_inflation(self):
        changed = copy.deepcopy(self.certificate); changed["excluded_claims"] = []; self.assertTrue(certificate_errors(changed))

if __name__ == "__main__": unittest.main()
