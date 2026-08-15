#!/usr/bin/env python3
from __future__ import annotations

import copy
import unittest

import validate_otp_permanent_adjudication as control


class PermanentAdjudicationMutationTests(unittest.TestCase):
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
        self.assert_rejected(lambda r, s, ro, k: r["decision"].__setitem__("disposition", "adjudication_not_clear"), "disposition drift")

    def test_candidate_head_substitution_rejected(self) -> None:
        self.assert_rejected(lambda r, s, ro, k: r["authority"].__setitem__("execution_candidate_head", "0" * 40), "authority or streamlined control-plan drift")

    def test_candidate_review_substitution_rejected(self) -> None:
        self.assert_rejected(lambda r, s, ro, k: r["authority"]["evidence_candidate_review"].__setitem__("review_id", 1), "authority or streamlined control-plan drift")

    def test_control_plan_weakening_rejected(self) -> None:
        self.assert_rejected(lambda r, s, ro, k: r["authority"]["control_plan"].__setitem__("human_steward_intervention_required_only_for_control_plan_change", False), "authority or streamlined control-plan drift")

    def test_control_plan_change_request_rejected(self) -> None:
        self.assert_rejected(lambda r, s, ro, k: r["authority"]["control_plan"].__setitem__("control_plan_change_requested", True), "authority or streamlined control-plan drift")

    def test_target_omission_rejected(self) -> None:
        self.assert_rejected(lambda r, s, ro, k: r["encoded_targets"].pop(), "target membership")

    def test_circuit_scope_inflation_rejected(self) -> None:
        self.assert_rejected(lambda r, s, ro, k: r["evidence_assessment"].__setitem__("circuit_targets_in_scope", True), "scope inflation")

    def test_gate_scope_inflation_rejected(self) -> None:
        self.assert_rejected(lambda r, s, ro, k: r["evidence_assessment"].__setitem__("gate_bounds_in_scope", True), "scope inflation")

    def test_total_size_scope_inflation_rejected(self) -> None:
        self.assert_rejected(lambda r, s, ro, k: r["evidence_assessment"].__setitem__("total_size_consequences_in_scope", True), "scope inflation")

    def test_historical_pdf_equivalence_inflation_rejected(self) -> None:
        self.assert_rejected(lambda r, s, ro, k: r["evidence_assessment"].__setitem__("historical_pdf_byte_equivalence", "established"), "scope inflation")

    def test_proof_promotion_rejected(self) -> None:
        self.assert_rejected(lambda r, s, ro, k: r["state"].__setitem__("mathematical_target_proved", True), "state inflation")

    def test_output_authority_rejected(self) -> None:
        self.assert_rejected(lambda r, s, ro, k: r["state"].__setitem__("may_issue_output", True), "state inflation")

    def test_cert_output_insertion_rejected(self) -> None:
        self.assert_rejected(lambda r, s, ro, k: r["state"].__setitem__("cert_output", {"path": "fake"}), "schema validation failed")

    def test_aggregate_adjudication_rejected(self) -> None:
        self.assert_rejected(lambda r, s, ro, k: r["state"].__setitem__("aggregate_adjudication", True), "state inflation")

    def test_aggregate_output_rejected(self) -> None:
        self.assert_rejected(lambda r, s, ro, k: r["state"].__setitem__("aggregate_output", True), "state inflation")

    def test_review_prepopulation_rejected(self) -> None:
        self.assert_rejected(lambda r, s, ro, k: r["review_gate"].__setitem__("recorded_review", {"reviewer": "author"}), "schema validation failed")

    def test_certificate_file_rejected(self) -> None:
        self.assert_rejected(lambda r, s, ro, k: k.__setitem__("certificate_present", True), "Permanent Cert output exists")

    def test_predecessor_candidate_failure_rejected(self) -> None:
        self.assert_rejected(lambda r, s, ro, k: k.__setitem__("candidate_errors", ["candidate broken"]), "predecessor candidate invalid")

    def test_authority_blob_substitution_rejected(self) -> None:
        bad = dict(control.EXPECTED_BLOBS)
        bad["candidate"] = "0" * 40
        self.assert_rejected(lambda r, s, ro, k: k.__setitem__("authority_blobs", bad), "candidate authority blob drift")

    def test_route_transition_rejected(self) -> None:
        def mutate(r, s, ro, k):
            route = next(row for row in ro["routes"] if row.get("route_id") == "MC-ROUTE-OTP-C-PERMANENT-FORMULA")
            route["intake_status"] = "qualified"
        self.assert_rejected(mutate, "route is not submitted")

    def test_schema_opening_rejected(self) -> None:
        self.assert_rejected(lambda r, s, ro, k: s.__setitem__("additionalProperties", True), "schema contains open object")


if __name__ == "__main__":
    unittest.main(verbosity=2)
