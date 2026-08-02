#!/usr/bin/env python3
from __future__ import annotations

import copy
import unittest

import validate_otp_ehrhart_adjudication as control


class EhrhartAdjudicationMutationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.record, self.schema, self.routes = control.defaults()

    def assert_rejected(self, mutate, token: str) -> None:
        record = copy.deepcopy(self.record)
        schema = copy.deepcopy(self.schema)
        routes = copy.deepcopy(self.routes)
        kwargs = {}
        mutate(record, schema, routes, kwargs)
        errors = control.validation_errors(record=record, schema=schema, routes=routes, **kwargs)
        self.assertTrue(any(token in error for error in errors), errors)

    def test_baseline(self) -> None:
        self.assertEqual([], control.validation_errors())

    def test_disposition_substitution_rejected(self) -> None:
        self.assert_rejected(
            lambda r, s, ro, k: r["decision"].__setitem__("disposition", "adjudication_not_clear"),
            "disposition drift",
        )

    def test_authorization_comment_substitution_rejected(self) -> None:
        self.assert_rejected(
            lambda r, s, ro, k: r["authority"]["human_steward_authorization"].__setitem__("comment_id", 1),
            "authorization drift",
        )

    def test_candidate_head_substitution_rejected(self) -> None:
        self.assert_rejected(
            lambda r, s, ro, k: r["authority"].__setitem__("execution_candidate_head", "0" * 40),
            "authorization drift",
        )

    def test_target_omission_rejected(self) -> None:
        self.assert_rejected(
            lambda r, s, ro, k: r["encoded_targets"].pop(),
            "target membership",
        )

    def test_equality_classification_inflation_rejected(self) -> None:
        self.assert_rejected(
            lambda r, s, ro, k: r["evidence_assessment"].__setitem__("equality_case_classification", "clear"),
            "scope inflation",
        )

    def test_whole_document_equivalence_inflation_rejected(self) -> None:
        self.assert_rejected(
            lambda r, s, ro, k: r["evidence_assessment"].__setitem__("whole_document_equivalence", "established"),
            "scope inflation",
        )

    def test_proof_promotion_rejected(self) -> None:
        self.assert_rejected(
            lambda r, s, ro, k: r["state"].__setitem__("mathematical_target_proved", True),
            "state inflation",
        )

    def test_cert_output_insertion_rejected(self) -> None:
        self.assert_rejected(
            lambda r, s, ro, k: r["state"].__setitem__("cert_output", {"path": "fake"}),
            "schema validation failed",
        )

    def test_aggregate_adjudication_rejected(self) -> None:
        self.assert_rejected(
            lambda r, s, ro, k: r["state"].__setitem__("aggregate_adjudication", True),
            "state inflation",
        )

    def test_review_prepopulation_rejected(self) -> None:
        self.assert_rejected(
            lambda r, s, ro, k: r["review_gate"].__setitem__("recorded_review", {"reviewer": "author"}),
            "schema validation failed",
        )

    def test_certificate_file_rejected(self) -> None:
        self.assert_rejected(
            lambda r, s, ro, k: k.__setitem__("certificate_present", True),
            "Cert output exists",
        )

    def test_predecessor_candidate_failure_rejected(self) -> None:
        self.assert_rejected(
            lambda r, s, ro, k: k.__setitem__("candidate_errors", ["candidate broken"]),
            "predecessor candidate invalid",
        )

    def test_authority_blob_substitution_rejected(self) -> None:
        bad = dict(control.EXPECTED_BLOBS)
        bad["candidate"] = "0" * 40
        self.assert_rejected(
            lambda r, s, ro, k: k.__setitem__("authority_blobs", bad),
            "candidate authority blob drift",
        )

    def test_schema_opening_rejected(self) -> None:
        self.assert_rejected(
            lambda r, s, ro, k: s.__setitem__("additionalProperties", True),
            "schema is not closed",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
