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


class OTPEhrhartOutputCandidateCorrectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.candidate = M.load(M.CANDIDATE)
        self.candidate_schema = M.load(M.CANDIDATE_SCHEMA)
        self.staged_certificate = M.load(M.STAGED_CERTIFICATE)
        self.transition = M.load(M.TRANSITION)
        self.transition_schema = M.load(M.TRANSITION_SCHEMA)
        self.future_schema = M.load(M.FUTURE_SCHEMA)
        self.routes = M.load(M.ROUTES)

    def errors(self, **kwargs):
        return M.validation_errors(
            candidate=copy.deepcopy(kwargs.get("candidate", self.candidate)),
            candidate_schema=copy.deepcopy(kwargs.get("candidate_schema", self.candidate_schema)),
            staged_certificate=copy.deepcopy(kwargs.get("staged_certificate", self.staged_certificate)),
            transition=copy.deepcopy(kwargs.get("transition", self.transition)),
            transition_schema=copy.deepcopy(kwargs.get("transition_schema", self.transition_schema)),
            future_schema=copy.deepcopy(kwargs.get("future_schema", self.future_schema)),
            routes=copy.deepcopy(kwargs.get("routes", self.routes)),
            blobs=copy.deepcopy(kwargs.get("blobs", M.EXPECTED_BLOBS)),
            live_certificate_present=kwargs.get("live_certificate_present", False),
            candidate_files=kwargs.get("candidate_files", set(M.EXPECTED_CANDIDATE_FILES)),
        )

    def execution(self, **kwargs):
        data = {
            "certificate_content_commit": "1" * 40,
            "exact_execution_head": "2" * 40,
            "certificate_content_commit_is_ancestor": True,
            "certificate_exists_at_content_commit": True,
            "certificate_blob_at_content_commit": M.EXPECTED_BLOBS["staged_certificate"],
            "certificate_blob_at_execution_head": M.EXPECTED_BLOBS["staged_certificate"],
            "registry_blob_at_content_commit": M.EXPECTED_BLOBS["routes"],
            "route_changed_at_content_commit": False,
            "route_transition_commit_after_content_commit": True,
            "cert_output_commit_sha": "1" * 40,
            "merge_method": "merge",
            "protected_main_publication_atomic": True,
            "protected_main_route_state_before_merge": "submitted",
            "protected_main_certificate_present_before_merge": False,
            "protected_main_cert_output_present_before_merge": False,
        }
        data.update(kwargs)
        return M.future_execution_errors(**data)

    def test_current_correction_passes(self):
        self.assertEqual([], self.errors())

    def test_candidate_mutations_are_rejected(self):
        for path, value in (
            (("candidate_state",), "executed"),
            (("correction_authorization", "comment_id"), 1),
            (("state", "may_execute"), True),
            (("state", "aggregate_output"), True),
            (("corrected_execution_plan", "protected_merge_method"), "squash"),
            (("corrected_execution_plan", "route_first_ordering_prohibited"), False),
        ):
            with self.subTest(path=path):
                data = copy.deepcopy(self.candidate)
                node = data
                for key in path[:-1]:
                    node = node[key]
                node[path[-1]] = value
                self.assertTrue(self.errors(candidate=data))

    def test_candidate_target_omission_is_rejected(self):
        data = copy.deepcopy(self.candidate)
        data["encoded_targets"].pop()
        self.assertTrue(self.errors(candidate=data))

    def test_blob_mutations_are_rejected(self):
        for key in M.EXPECTED_BLOBS:
            with self.subTest(blob=key):
                blobs = copy.deepcopy(M.EXPECTED_BLOBS)
                blobs[key] = "0" * 40
                self.assertTrue(self.errors(blobs=blobs))

    def test_live_certificate_is_rejected(self):
        self.assertTrue(self.errors(live_certificate_present=True))

    def test_candidate_membership_inflation_is_rejected(self):
        files = set(M.EXPECTED_CANDIDATE_FILES)
        files.add("OTP-J1-COMPACTNESS.json")
        self.assertTrue(self.errors(candidate_files=files))

    def test_open_schemas_are_rejected(self):
        c = copy.deepcopy(self.candidate_schema)
        c["additionalProperties"] = True
        t = copy.deepcopy(self.transition_schema)
        t["additionalProperties"] = True
        self.assertTrue(self.errors(candidate_schema=c))
        self.assertTrue(self.errors(transition_schema=t))

    def test_protected_merge_self_reference_is_rejected(self):
        data = copy.deepcopy(self.transition)
        data["after_template"]["cert_output"]["commit_sha"] = M.FORBIDDEN_TOKEN
        self.assertTrue(self.errors(transition=data))

    def test_content_token_removal_is_rejected(self):
        data = copy.deepcopy(self.transition)
        data["after_template"]["cert_output"]["commit_sha"] = "$OTHER"
        self.assertTrue(self.errors(transition=data))

    def test_live_route_change_is_rejected(self):
        routes = copy.deepcopy(self.routes)
        route = next(x for x in routes["routes"] if x["route_id"] == "MC-ROUTE-OTP-F-EHRHART")
        route["intake_status"] = "qualified"
        self.assertTrue(self.errors(routes=routes))

    def test_transition_before_mismatch_is_rejected(self):
        data = copy.deepcopy(self.transition)
        data["before"]["blockers"].append("forged")
        self.assertTrue(self.errors(transition=data))

    def test_unauthorized_route_field_change_is_rejected(self):
        data = copy.deepcopy(self.transition)
        data["after_template"]["source_manifest"]["digest"] = "0" * 40
        self.assertTrue(self.errors(transition=data))

    def test_transition_gate_mutations_are_rejected(self):
        mutations = (
            ("certificate_content_commit_precedes_route_transition", False),
            ("exact_reviewed_head_descends_from_certificate_content_commit", False),
            ("protected_merge_method", "squash"),
            ("squash_merge_prohibited", False),
            ("rebase_merge_prohibited", False),
            ("protected_main_publishes_certificate_and_route_together", False),
            ("partial_protected_main_state_prohibited", False),
        )
        for key, value in mutations:
            with self.subTest(key=key):
                data = copy.deepcopy(self.transition)
                data["atomicity"][key] = value
                self.assertTrue(self.errors(transition=data))

    def test_route_first_ordering_is_rejected(self):
        data = copy.deepcopy(self.transition)
        data["execution_sequence"]["route_first_ordering_prohibited"] = False
        self.assertTrue(self.errors(transition=data))

    def test_staged_proof_promotion_is_rejected(self):
        data = copy.deepcopy(self.staged_certificate)
        data["qualification"]["source_theorem_mathematically_proved"] = True
        self.assertTrue(self.errors(staged_certificate=data))

    def test_staged_equality_classification_is_rejected(self):
        data = copy.deepcopy(self.staged_certificate)
        data["qualification"]["equality_case_classification"] = "complete"
        self.assertTrue(self.errors(staged_certificate=data))

    def test_staged_aggregate_authority_is_rejected(self):
        data = copy.deepcopy(self.staged_certificate)
        data["state"]["aggregate_output"] = True
        self.assertTrue(self.errors(staged_certificate=data))

    def test_valid_future_execution_passes(self):
        self.assertEqual([], self.execution())

    def test_malformed_content_commit_is_rejected(self):
        self.assertTrue(self.execution(certificate_content_commit="bad", cert_output_commit_sha="bad"))

    def test_self_equal_content_and_head_is_rejected(self):
        self.assertTrue(self.execution(certificate_content_commit="2" * 40, cert_output_commit_sha="2" * 40))

    def test_nonancestor_content_commit_is_rejected(self):
        self.assertTrue(self.execution(certificate_content_commit_is_ancestor=False))

    def test_missing_or_wrong_certificate_is_rejected(self):
        self.assertTrue(self.execution(certificate_exists_at_content_commit=False))
        self.assertTrue(self.execution(certificate_blob_at_content_commit="0" * 40))
        self.assertTrue(self.execution(certificate_blob_at_execution_head="0" * 40))

    def test_registry_or_ordering_drift_is_rejected(self):
        self.assertTrue(self.execution(registry_blob_at_content_commit="0" * 40))
        self.assertTrue(self.execution(route_changed_at_content_commit=True))
        self.assertTrue(self.execution(route_transition_commit_after_content_commit=False))

    def test_pointer_mismatch_is_rejected(self):
        self.assertTrue(self.execution(cert_output_commit_sha="3" * 40))

    def test_squash_and_rebase_are_rejected(self):
        self.assertTrue(self.execution(merge_method="squash"))
        self.assertTrue(self.execution(merge_method="rebase"))

    def test_nonatomic_publication_is_rejected(self):
        self.assertTrue(self.execution(protected_main_publication_atomic=False))

    def test_partial_protected_main_states_are_rejected(self):
        self.assertTrue(self.execution(protected_main_route_state_before_merge="qualified"))
        self.assertTrue(self.execution(protected_main_certificate_present_before_merge=True))
        self.assertTrue(self.execution(protected_main_cert_output_present_before_merge=True))

    def test_future_claim_inflation_is_rejected(self):
        self.assertTrue(self.execution(mathematical_target_proved=True))
        self.assertTrue(self.execution(equality_case_classified=True))
        self.assertTrue(self.execution(other_family_output=True))
        self.assertTrue(self.execution(aggregate_output=True))


if __name__ == "__main__":
    unittest.main()
