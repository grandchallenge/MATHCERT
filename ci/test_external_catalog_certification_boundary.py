import copy
import json
import unittest

try:
    from ci.validate_external_catalog_certification_boundary import POLICY, validation_errors
except ModuleNotFoundError:  # Direct script execution places ci/ on sys.path.
    from validate_external_catalog_certification_boundary import POLICY, validation_errors


class ExternalCatalogCertificationBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.policy = json.loads(POLICY.read_text(encoding="utf-8"))

    def test_committed_policy(self):
        self.assertEqual(validation_errors(self.policy), [])

    def test_no_assurance_tier_is_certification(self):
        for field in self.policy["forbidden_inferences"]:
            changed = copy.deepcopy(self.policy)
            changed["forbidden_inferences"][field] = True
            self.assertTrue(validation_errors(changed), field)

    def test_direct_catalog_intake_is_rejected(self):
        changed = copy.deepcopy(self.policy)
        changed["direct_catalog_intake"] = True
        self.assertTrue(validation_errors(changed))

    def test_local_claim_and_evidence_are_required(self):
        for field in ("exact_local_claim", "local_replay_evidence", "independent_verification"):
            changed = copy.deepcopy(self.policy)
            changed["required_handoff"][field] = False
            self.assertTrue(validation_errors(changed), field)


if __name__ == "__main__":
    unittest.main()
