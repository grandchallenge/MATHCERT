from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_otp_ehrhart_output_execution_post_merge_attestation",
    ROOT / "ci/validate_otp_ehrhart_output_execution_post_merge_attestation.py",
)
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class OtpEhrhartOutputExecutionPostMergeAttestationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.attestation = M.load(M.ATTESTATION)
        self.closure = M.load(M.CLOSURE)
        self.attestation_schema = M.load(M.ATTESTATION_SCHEMA)
        self.closure_schema = M.load(M.CLOSURE_SCHEMA)
        self.historical_candidate = M.load(M.HISTORICAL_CANDIDATE)
        self.routes = M.load(M.ROUTES)
        self.certificate = M.load(M.CERTIFICATE)
        self.adjudication = M.load(M.ADJUDICATION)
        self.receipt = {
            "merge_parent_count": 2,
            "reviewed_head_is_direct_parent": True,
            "certificate_content_is_ancestor_of_reviewed_head": True,
            "route_transition_is_ancestor_of_reviewed_head": True,
            "reviewed_head_is_ancestor_of_merge": True,
            "certificate_blob_at_content_commit": M.EXPECTED["certificate"],
            "route_blob_at_content_commit": "cf876f43ae824f965a3aedf411671c110c380028",
            "route_blob_at_transition_commit": M.EXPECTED["routes"],
            "certificate_blob_at_merge": M.EXPECTED["certificate"],
            "route_blob_at_merge": M.EXPECTED["routes"],
        }

    def errors(self, **kwargs):
        return M.validation_errors(
            attestation=copy.deepcopy(kwargs.get("attestation", self.attestation)),
            closure=copy.deepcopy(kwargs.get("closure", self.closure)),
            attestation_schema=copy.deepcopy(kwargs.get("attestation_schema", self.attestation_schema)),
            closure_schema=copy.deepcopy(kwargs.get("closure_schema", self.closure_schema)),
            document_text=kwargs.get("document_text", M.DOCUMENT.read_text(encoding="utf-8")),
            historical_candidate=copy.deepcopy(kwargs.get("historical_candidate", self.historical_candidate)),
            routes=copy.deepcopy(kwargs.get("routes", self.routes)),
            certificate=copy.deepcopy(kwargs.get("certificate", self.certificate)),
            adjudication=copy.deepcopy(kwargs.get("adjudication", self.adjudication)),
            blobs=copy.deepcopy(kwargs.get("blobs", M.EXPECTED)),
            receipt=copy.deepcopy(kwargs.get("receipt", self.receipt)),
            other_adjudication_present=kwargs.get("other_adjudication_present", False),
        )

    def test_current_closure_passes(self):
        self.assertEqual([], self.errors())

    def test_reviewed_head_drift_fails(self):
        data = copy.deepcopy(self.attestation)
        data["subject"]["exact_reviewed_head"] = "0" * 40
        self.assertTrue(self.errors(attestation=data))

    def test_review_drift_fails(self):
        data = copy.deepcopy(self.attestation)
        data["non_author_review"]["review_id"] = 1
        self.assertTrue(self.errors(attestation=data))

    def test_disposition_comment_drift_fails(self):
        data = copy.deepcopy(self.attestation)
        data["human_steward_disposition"]["pull_request_comment_id"] = 1
        self.assertTrue(self.errors(attestation=data))

    def test_merge_commit_drift_fails(self):
        data = copy.deepcopy(self.closure)
        data["subject"]["merge_commit"] = "0" * 40
        self.assertTrue(self.errors(closure=data))

    def test_content_commit_drift_fails(self):
        data = copy.deepcopy(self.closure)
        data["execution_commits"]["certificate_content_commit"] = "0" * 40
        self.assertTrue(self.errors(closure=data))

    def test_transition_commit_drift_fails(self):
        data = copy.deepcopy(self.closure)
        data["execution_commits"]["route_transition_commit"] = "0" * 40
        self.assertTrue(self.errors(closure=data))

    def test_historical_candidate_rewrite_fails(self):
        data = copy.deepcopy(self.historical_candidate)
        data["branch_execution_state"]["execution_state"] = "protected_publication_completed"
        self.assertTrue(self.errors(historical_candidate=data))

    def test_historical_candidate_blob_drift_fails(self):
        blobs = copy.deepcopy(M.EXPECTED)
        blobs["historical_candidate"] = "0" * 40
        self.assertTrue(self.errors(blobs=blobs))

    def test_publication_not_recorded_fails(self):
        data = copy.deepcopy(self.closure)
        data["supersession"]["protected_publication_occurred"] = False
        self.assertTrue(self.errors(closure=data))

    def test_squash_like_merge_receipt_fails(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["merge_parent_count"] = 1
        self.assertTrue(self.errors(receipt=receipt))

    def test_missing_content_ancestry_fails(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["certificate_content_is_ancestor_of_reviewed_head"] = False
        self.assertTrue(self.errors(receipt=receipt))

    def test_wrong_certificate_at_content_commit_fails(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["certificate_blob_at_content_commit"] = "0" * 40
        self.assertTrue(self.errors(receipt=receipt))

    def test_wrong_route_at_transition_fails(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["route_blob_at_transition_commit"] = "0" * 40
        self.assertTrue(self.errors(receipt=receipt))

    def test_ehrhart_route_regression_fails(self):
        routes = copy.deepcopy(self.routes)
        route = next(x for x in routes["routes"] if x.get("campaign_id") == "OTP-F-EHRHART")
        route["intake_status"] = "submitted"
        self.assertTrue(self.errors(routes=routes))

    def test_ehrhart_output_substitution_fails(self):
        routes = copy.deepcopy(self.routes)
        route = next(x for x in routes["routes"] if x.get("campaign_id") == "OTP-F-EHRHART")
        route["cert_output"]["digest"] = "0" * 40
        self.assertTrue(self.errors(routes=routes))

    def test_compactness_route_inflation_fails(self):
        routes = copy.deepcopy(self.routes)
        route = next(x for x in routes["routes"] if x.get("campaign_id") == "OTP-J1-COMPACTNESS")
        route["intake_status"] = "qualified"
        self.assertTrue(self.errors(routes=routes))

    def test_two_degenerate_output_fails(self):
        routes = copy.deepcopy(self.routes)
        route = next(x for x in routes["routes"] if x.get("campaign_id") == "OTP-J2-TWO-DEGENERATE")
        route["cert_output"] = {
            "repository": "grandchallenge/MATHCERT",
            "commit_sha": "0" * 40,
            "path": "certificates/forged.json",
            "digest_algorithm": "git_blob_sha1",
            "digest": "0" * 40,
        }
        self.assertTrue(self.errors(routes=routes))

    def test_other_adjudication_fails(self):
        self.assertTrue(self.errors(other_adjudication_present=True))

    def test_certificate_proof_promotion_fails(self):
        data = copy.deepcopy(self.certificate)
        data["state"]["mathematical_target_proved"] = True
        self.assertTrue(self.errors(certificate=data))

    def test_certificate_aggregate_output_fails(self):
        data = copy.deepcopy(self.certificate)
        data["state"]["aggregate_output"] = True
        self.assertTrue(self.errors(certificate=data))

    def test_equality_classification_fails(self):
        data = copy.deepcopy(self.closure)
        data["preserved_limitations"]["classification_or_uniqueness_of_all_equality_cases"] = "established"
        self.assertTrue(self.errors(closure=data))

    def test_current_family_counts_drift_fails(self):
        data = copy.deepcopy(self.closure)
        data["current_otp_family_state"]["families"][0]["restricted_cert_output_count"] = 2
        self.assertTrue(self.errors(closure=data))

    def test_aggregate_output_count_fails(self):
        data = copy.deepcopy(self.closure)
        data["current_otp_family_state"]["aggregate_output_count"] = 1
        self.assertTrue(self.errors(closure=data))

    def test_proved_target_count_fails(self):
        data = copy.deepcopy(self.closure)
        data["current_otp_family_state"]["mathematical_targets_marked_proved"] = 1
        self.assertTrue(self.errors(closure=data))

    def test_document_drift_fails(self):
        self.assertTrue(self.errors(document_text=M.DOCUMENT.read_text(encoding="utf-8") + "\nCertified.\n"))

    def test_blob_mutations_fail(self):
        for key in M.EXPECTED:
            with self.subTest(key=key):
                blobs = copy.deepcopy(M.EXPECTED)
                blobs[key] = "0" * 40
                self.assertTrue(self.errors(blobs=blobs))

    def test_open_schemas_fail(self):
        a = copy.deepcopy(self.attestation_schema)
        a["additionalProperties"] = True
        c = copy.deepcopy(self.closure_schema)
        c["additionalProperties"] = True
        self.assertTrue(self.errors(attestation_schema=a))
        self.assertTrue(self.errors(closure_schema=c))

    def test_unexpected_authority_field_fails(self):
        data = copy.deepcopy(self.attestation)
        data["aggregate_authority"] = True
        self.assertTrue(self.errors(attestation=data))


if __name__ == "__main__":
    unittest.main()
