from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_otp_ehrhart_adjudication_post_merge_attestation",
    ROOT / "ci/validate_otp_ehrhart_adjudication_post_merge_attestation.py",
)
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class OtpEhrhartAdjudicationPostMergeAttestationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.attestation = json.loads(M.ATTESTATION.read_text(encoding="utf-8"))
        self.schema = json.loads(M.SCHEMA.read_text(encoding="utf-8"))
        self.adjudication = json.loads(M.ADJUDICATION.read_text(encoding="utf-8"))

    def errors(self, **kwargs):
        return M.validation_errors(
            attestation=copy.deepcopy(kwargs.get("attestation", self.attestation)),
            document_text=kwargs.get("document_text", M.DOCUMENT.read_text(encoding="utf-8")),
            schema=copy.deepcopy(kwargs.get("schema", self.schema)),
            adjudication=copy.deepcopy(kwargs.get("adjudication", self.adjudication)),
            document_blob=kwargs.get("document_blob", M.EXPECTED_DOCUMENT_BLOB),
            schema_blob=kwargs.get("schema_blob", M.EXPECTED_SCHEMA_BLOB),
            adjudication_blob=kwargs.get("adjudication_blob", M.EXPECTED_ADJUDICATION_BLOB),
        )

    def test_current_attestation_passes(self) -> None:
        self.assertEqual([], self.errors())

    def test_reviewed_head_drift_is_rejected(self) -> None:
        data = copy.deepcopy(self.attestation)
        data["subject"]["exact_reviewed_head"] = "0" * 40
        self.assertTrue(self.errors(attestation=data))

    def test_merge_commit_drift_is_rejected(self) -> None:
        data = copy.deepcopy(self.attestation)
        data["subject"]["merge_commit"] = "0" * 40
        self.assertTrue(self.errors(attestation=data))

    def test_review_identity_drift_is_rejected(self) -> None:
        data = copy.deepcopy(self.attestation)
        data["non_author_review"]["review_id"] = 1
        self.assertTrue(self.errors(attestation=data))

    def test_disposition_comment_drift_is_rejected(self) -> None:
        data = copy.deepcopy(self.attestation)
        data["human_steward_disposition"]["pull_request_comment_id"] = 1
        self.assertTrue(self.errors(attestation=data))

    def test_workflow_identity_drift_is_rejected(self) -> None:
        data = copy.deepcopy(self.attestation)
        data["exact_head_checks"]["cert_checks"]["run_id"] = 1
        self.assertTrue(self.errors(attestation=data))

    def test_document_text_drift_is_rejected(self) -> None:
        text = M.DOCUMENT.read_text(encoding="utf-8") + "\nCertified.\n"
        self.assertTrue(self.errors(document_text=text))

    def test_document_blob_drift_is_rejected(self) -> None:
        self.assertTrue(self.errors(document_blob="0" * 40))

    def test_schema_blob_drift_is_rejected(self) -> None:
        self.assertTrue(self.errors(schema_blob="0" * 40))

    def test_adjudication_record_blob_drift_is_rejected(self) -> None:
        self.assertTrue(self.errors(adjudication_blob="0" * 40))

    def test_target_membership_drift_is_rejected(self) -> None:
        data = copy.deepcopy(self.adjudication)
        data["encoded_targets"].pop()
        self.assertTrue(self.errors(adjudication=data))

    def test_route_state_inflation_is_rejected(self) -> None:
        data = copy.deepcopy(self.adjudication)
        data["state"]["route_state"] = "qualified"
        self.assertTrue(self.errors(adjudication=data))

    def test_cert_output_insertion_is_rejected(self) -> None:
        data = copy.deepcopy(self.adjudication)
        data["state"]["cert_output"] = {"path": "certificates/forged.json"}
        self.assertTrue(self.errors(adjudication=data))

    def test_proof_status_promotion_is_rejected(self) -> None:
        data = copy.deepcopy(self.adjudication)
        data["state"]["mathematical_target_proved"] = True
        self.assertTrue(self.errors(adjudication=data))

    def test_equality_classification_inflation_is_rejected(self) -> None:
        data = copy.deepcopy(self.adjudication)
        data["preserved_limitations"]["classification_or_uniqueness_of_all_equality_cases"] = "established"
        self.assertTrue(self.errors(adjudication=data))

    def test_aggregate_authority_is_rejected(self) -> None:
        data = copy.deepcopy(self.adjudication)
        data["state"]["aggregate_adjudication"] = True
        self.assertTrue(self.errors(adjudication=data))

    def test_open_schema_is_rejected(self) -> None:
        schema = copy.deepcopy(self.schema)
        schema["additionalProperties"] = True
        self.assertTrue(self.errors(schema=schema))

    def test_unexpected_authority_field_is_rejected(self) -> None:
        data = copy.deepcopy(self.attestation)
        data["new_cert_authority"] = True
        self.assertTrue(self.errors(attestation=data))


if __name__ == "__main__":
    unittest.main()
