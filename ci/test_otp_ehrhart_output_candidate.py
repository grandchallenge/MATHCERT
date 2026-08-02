from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_otp_ehrhart_output_candidate",
    ROOT / "ci/validate_otp_ehrhart_output_candidate.py",
)
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class OTPEhrhartOutputExecutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.candidate = M.load(M.CANDIDATE)
        self.schema = M.load(M.CANDIDATE_SCHEMA)
        self.certificate = M.load(M.LIVE_CERTIFICATE)
        self.staged = M.load(M.STAGED_CERTIFICATE)
        self.transition = M.load(M.TRANSITION)
        self.future_schema = M.load(M.FUTURE_SCHEMA)
        self.routes = M.load(M.ROUTES)
        self.receipt = M.actual_git_receipt()

    def errors(self, **kwargs):
        return M.validation_errors(
            candidate=copy.deepcopy(kwargs.get("candidate", self.candidate)),
            candidate_schema=copy.deepcopy(kwargs.get("candidate_schema", self.schema)),
            certificate=copy.deepcopy(kwargs.get("certificate", self.certificate)),
            staged_certificate=copy.deepcopy(kwargs.get("staged_certificate", self.staged)),
            transition=copy.deepcopy(kwargs.get("transition", self.transition)),
            future_schema=copy.deepcopy(kwargs.get("future_schema", self.future_schema)),
            routes=copy.deepcopy(kwargs.get("routes", self.routes)),
            blobs=copy.deepcopy(kwargs.get("blobs", M.EXPECTED_BLOBS)),
            candidate_files=kwargs.get("candidate_files", set(M.EXPECTED_CANDIDATE_FILES)),
            git_receipt=copy.deepcopy(kwargs.get("git_receipt", self.receipt)),
        )

    def test_current_execution_passes(self):
        self.assertEqual([], self.errors())

    def test_authorization_drift_is_rejected(self):
        data = copy.deepcopy(self.candidate)
        data["execution_authorization"]["comment_id"] = 1
        self.assertTrue(self.errors(candidate=data))

    def test_open_schema_is_rejected(self):
        data = copy.deepcopy(self.schema)
        data["additionalProperties"] = True
        self.assertTrue(self.errors(candidate_schema=data))

    def test_candidate_blob_drift_is_rejected(self):
        blobs = copy.deepcopy(M.EXPECTED_BLOBS)
        blobs["candidate"] = "0" * 40
        self.assertTrue(self.errors(blobs=blobs))

    def test_certificate_modification_is_rejected(self):
        data = copy.deepcopy(self.certificate)
        data["qualification"]["source_theorem_mathematically_proved"] = True
        self.assertTrue(self.errors(certificate=data))

    def test_equality_inflation_is_rejected(self):
        data = copy.deepcopy(self.certificate)
        data["qualification"]["equality_case_classification"] = "complete"
        self.assertTrue(self.errors(certificate=data))

    def test_aggregate_output_is_rejected(self):
        data = copy.deepcopy(self.certificate)
        data["state"]["aggregate_output"] = True
        self.assertTrue(self.errors(certificate=data))

    def test_route_pointer_mismatch_is_rejected(self):
        routes = copy.deepcopy(self.routes)
        route = next(x for x in routes["routes"] if x["campaign_id"] == "OTP-F-EHRHART")
        route["cert_output"]["commit_sha"] = "0" * 40
        self.assertTrue(self.errors(routes=routes))

    def test_target_inflation_is_rejected(self):
        routes = copy.deepcopy(self.routes)
        route = next(x for x in routes["routes"] if x["campaign_id"] == "OTP-F-EHRHART")
        route["target_claim_ids"].append("forged")
        self.assertTrue(self.errors(routes=routes))

    def test_other_family_output_is_rejected(self):
        routes = copy.deepcopy(self.routes)
        route = next(x for x in routes["routes"] if x["campaign_id"] == "OTP-J1-COMPACTNESS")
        route["intake_status"] = "qualified"
        route["cert_output"] = copy.deepcopy(
            next(x for x in routes["routes"] if x["campaign_id"] == "OTP-F-EHRHART")["cert_output"]
        )
        self.assertTrue(self.errors(routes=routes))

    def test_aggregate_route_is_rejected(self):
        routes = copy.deepcopy(self.routes)
        route = copy.deepcopy(routes["routes"][-1])
        route["campaign_id"] = "OPENAI-TEN-PROOFS-001"
        route["route_id"] = "MC-ROUTE-OPENAI-TEN-PROOFS-001"
        routes["routes"].append(route)
        self.assertTrue(self.errors(routes=routes))

    def test_nonancestor_content_commit_is_rejected(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["content_commit_is_ancestor_of_head"] = False
        self.assertTrue(self.errors(git_receipt=receipt))

    def test_route_first_ordering_is_rejected(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["content_commit_is_ancestor_of_route_commit"] = False
        self.assertTrue(self.errors(git_receipt=receipt))

    def test_missing_content_certificate_is_rejected(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["certificate_blob_at_content_commit"] = None
        self.assertTrue(self.errors(git_receipt=receipt))

    def test_changed_registry_at_content_commit_is_rejected(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["registry_blob_at_content_commit"] = "0" * 40
        self.assertTrue(self.errors(git_receipt=receipt))

    def test_route_commit_scope_inflation_is_rejected(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["route_commit_files"] = [M.ROUTES_PATH, "README.md"]
        self.assertTrue(self.errors(git_receipt=receipt))

    def test_execution_branch_scope_inflation_is_rejected(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["execution_changed_files"].append("README.md")
        self.assertTrue(self.errors(git_receipt=receipt))

    def test_squash_permission_is_rejected(self):
        data = copy.deepcopy(self.candidate)
        data["publication_gate"]["protected_merge_method"] = "squash"
        self.assertTrue(self.errors(candidate=data))

    def test_partial_publication_permission_is_rejected(self):
        data = copy.deepcopy(self.candidate)
        data["publication_gate"]["partial_protected_main_state_prohibited"] = False
        self.assertTrue(self.errors(candidate=data))

    def test_whole_document_promotion_is_rejected(self):
        data = copy.deepcopy(self.candidate)
        data["preserved_limitations"]["whole_document_semantic_equivalence"] = "established"
        self.assertTrue(self.errors(candidate=data))


if __name__ == "__main__":
    unittest.main()
