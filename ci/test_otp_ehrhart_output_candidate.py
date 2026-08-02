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


class OTPEhrhartOutputCandidateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.candidate = M.load(M.CANDIDATE)
        self.candidate_schema = M.load(M.CANDIDATE_SCHEMA)
        self.staged_certificate = M.load(M.STAGED_CERTIFICATE)
        self.transition = M.load(M.TRANSITION)
        self.transition_schema = M.load(M.TRANSITION_SCHEMA)
        self.future_schema = M.load(M.FUTURE_SCHEMA)
        self.routes = M.load(M.ROUTES)
        self.contract = M.load(M.CONTRACT)
        self.adjudication = M.load(M.ADJUDICATION)
        self.attestation = M.load(M.ATTESTATION)

    def errors(self, **kwargs):
        return M.validation_errors(
            candidate=copy.deepcopy(kwargs.get("candidate", self.candidate)),
            candidate_schema=copy.deepcopy(kwargs.get("candidate_schema", self.candidate_schema)),
            staged_certificate=copy.deepcopy(kwargs.get("staged_certificate", self.staged_certificate)),
            transition=copy.deepcopy(kwargs.get("transition", self.transition)),
            transition_schema=copy.deepcopy(kwargs.get("transition_schema", self.transition_schema)),
            future_schema=copy.deepcopy(kwargs.get("future_schema", self.future_schema)),
            routes=copy.deepcopy(kwargs.get("routes", self.routes)),
            contract=copy.deepcopy(kwargs.get("contract", self.contract)),
            adjudication=copy.deepcopy(kwargs.get("adjudication", self.adjudication)),
            attestation=copy.deepcopy(kwargs.get("attestation", self.attestation)),
            blobs=copy.deepcopy(kwargs.get("blobs", M.EXPECTED_BLOBS)),
            live_certificate_present=kwargs.get("live_certificate_present", False),
            candidate_files=kwargs.get("candidate_files", set(M.EXPECTED_CANDIDATE_FILES)),
        )

    def test_current_candidate_passes(self):
        self.assertEqual([], self.errors())

    def test_authorization_comment_drift_is_rejected(self):
        data = copy.deepcopy(self.candidate)
        data["implementation_authorization"]["comment_id"] = 1
        self.assertTrue(self.errors(candidate=data))

    def test_candidate_state_drift_is_rejected(self):
        data = copy.deepcopy(self.candidate)
        data["candidate_state"] = "executed"
        self.assertTrue(self.errors(candidate=data))

    def test_contract_blob_drift_is_rejected(self):
        blobs = copy.deepcopy(M.EXPECTED_BLOBS)
        blobs["contract"] = "0" * 40
        self.assertTrue(self.errors(blobs=blobs))

    def test_live_registry_blob_drift_is_rejected(self):
        blobs = copy.deepcopy(M.EXPECTED_BLOBS)
        blobs["routes"] = "0" * 40
        self.assertTrue(self.errors(blobs=blobs))

    def test_staged_certificate_blob_drift_is_rejected(self):
        blobs = copy.deepcopy(M.EXPECTED_BLOBS)
        blobs["staged_certificate"] = "0" * 40
        self.assertTrue(self.errors(blobs=blobs))

    def test_transition_blob_drift_is_rejected(self):
        blobs = copy.deepcopy(M.EXPECTED_BLOBS)
        blobs["transition"] = "0" * 40
        self.assertTrue(self.errors(blobs=blobs))

    def test_target_omission_is_rejected(self):
        data = copy.deepcopy(self.candidate)
        data["encoded_targets"].pop()
        self.assertTrue(self.errors(candidate=data))

    def test_candidate_execution_authority_is_rejected(self):
        data = copy.deepcopy(self.candidate)
        data["state"]["may_execute"] = True
        self.assertTrue(self.errors(candidate=data))

    def test_live_route_qualification_is_rejected(self):
        routes = copy.deepcopy(self.routes)
        route = next(x for x in routes["routes"] if x["route_id"] == "MC-ROUTE-OTP-F-EHRHART")
        route["intake_status"] = "qualified"
        self.assertTrue(self.errors(routes=routes))

    def test_live_certificate_insertion_is_rejected(self):
        self.assertTrue(self.errors(live_certificate_present=True))

    def test_staged_proof_promotion_is_rejected(self):
        data = copy.deepcopy(self.staged_certificate)
        data["qualification"]["source_theorem_mathematically_proved"] = True
        self.assertTrue(self.errors(staged_certificate=data))

    def test_staged_disposition_inflation_is_rejected(self):
        data = copy.deepcopy(self.staged_certificate)
        data["qualification"]["disposition"] = "source_theorem_proved"
        self.assertTrue(self.errors(staged_certificate=data))

    def test_unexpected_axiom_is_rejected(self):
        data = copy.deepcopy(self.staged_certificate)
        data["axiom_report"]["unexpected_axioms"] = ["False"]
        self.assertTrue(self.errors(staged_certificate=data))

    def test_placeholder_insertion_is_rejected(self):
        data = copy.deepcopy(self.staged_certificate)
        data["trust_boundary"]["solution_placeholder_count"] = 1
        self.assertTrue(self.errors(staged_certificate=data))

    def test_transition_before_mismatch_is_rejected(self):
        data = copy.deepcopy(self.transition)
        data["before"]["blockers"].append("forged")
        self.assertTrue(self.errors(transition=data))

    def test_transition_target_inflation_is_rejected(self):
        data = copy.deepcopy(self.transition)
        data["after_template"]["target_claim_ids"].append("forged")
        self.assertTrue(self.errors(transition=data))

    def test_transition_partial_application_is_rejected(self):
        data = copy.deepcopy(self.transition)
        data["atomicity"]["partial_application_prohibited"] = False
        self.assertTrue(self.errors(transition=data))

    def test_transition_certificate_digest_drift_is_rejected(self):
        data = copy.deepcopy(self.transition)
        data["after_template"]["cert_output"]["digest"] = "0" * 40
        self.assertTrue(self.errors(transition=data))

    def test_execution_commit_resolution_is_rejected_during_candidate_stage(self):
        data = copy.deepcopy(self.transition)
        data["execution_commit_binding"]["unresolved_during_candidate_preparation"] = False
        data["after_template"]["cert_output"]["commit_sha"] = "a" * 40
        self.assertTrue(self.errors(transition=data))

    def test_non_atomic_candidate_plan_is_rejected(self):
        data = copy.deepcopy(self.candidate)
        data["atomic_execution_plan"]["same_protected_commit_required"] = False
        self.assertTrue(self.errors(candidate=data))

    def test_premature_execution_authorization_is_rejected(self):
        data = copy.deepcopy(self.candidate)
        data["execution_authorization"]["authorization"] = {"comment_id": 1}
        self.assertTrue(self.errors(candidate=data))

    def test_premature_review_completion_is_rejected(self):
        data = copy.deepcopy(self.candidate)
        data["review_state"]["status"] = "approved"
        self.assertTrue(self.errors(candidate=data))

    def test_equality_classification_is_rejected(self):
        data = copy.deepcopy(self.candidate)
        data["preserved_limitations"]["classification_or_uniqueness_of_all_equality_cases"] = "established"
        self.assertTrue(self.errors(candidate=data))

    def test_other_family_candidate_is_rejected(self):
        files = set(M.EXPECTED_CANDIDATE_FILES)
        files.add("OTP-J1-COMPACTNESS.json")
        self.assertTrue(self.errors(candidate_files=files))

    def test_claim_boundary_weakening_is_rejected(self):
        data = copy.deepcopy(self.candidate)
        data["claim_boundary"] = "Certificate prepared."
        self.assertTrue(self.errors(candidate=data))

    def test_open_candidate_schema_is_rejected(self):
        schema = copy.deepcopy(self.candidate_schema)
        schema["additionalProperties"] = True
        self.assertTrue(self.errors(candidate_schema=schema))

    def test_open_transition_schema_is_rejected(self):
        schema = copy.deepcopy(self.transition_schema)
        schema["additionalProperties"] = True
        self.assertTrue(self.errors(transition_schema=schema))

    def test_certificate_identity_drift_is_rejected(self):
        data = copy.deepcopy(self.staged_certificate)
        data["certificate_id"] = "MC-OTP-F-EHRHART-PROVED-001"
        self.assertTrue(self.errors(staged_certificate=data))

    def test_unauthorized_route_field_mutation_is_rejected(self):
        data = copy.deepcopy(self.transition)
        data["after_template"]["source_manifest"]["digest"] = "0" * 40
        self.assertTrue(self.errors(transition=data))


if __name__ == "__main__":
    unittest.main()
