from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

import validate_otp_j2_route_target_successor as j2

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_otp_ehrhart_output_execution",
    ROOT / "ci/validate_otp_ehrhart_output_execution.py",
)
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class OTPEhrhartOutputExecutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.record = M.load(M.RECORD)
        self.schema = M.load(M.SCHEMA)
        self.certificate = M.load(M.CERTIFICATE)
        self.staged = M.load(M.STAGED_CERTIFICATE)
        # Preserve the historical Ehrhart candidate mutation surface against
        # the exact route state before the separately governed J2 output.
        self.routes = j2.pre_output_routes()
        self.receipt = M.git_receipt()

    def errors(self, **kwargs):
        return M.validation_errors(
            record=copy.deepcopy(kwargs.get("record", self.record)),
            schema=copy.deepcopy(kwargs.get("schema", self.schema)),
            certificate=copy.deepcopy(kwargs.get("certificate", self.certificate)),
            staged_certificate=copy.deepcopy(kwargs.get("staged_certificate", self.staged)),
            routes=copy.deepcopy(kwargs.get("routes", self.routes)),
            receipt=copy.deepcopy(kwargs.get("receipt", self.receipt)),
            blobs=copy.deepcopy(kwargs.get("blobs", M.EXPECTED)),
        )

    def test_current_execution_passes(self):
        self.assertEqual([], self.errors())

    def test_live_j2_output_successor_passes_separately(self):
        self.assertEqual([], j2.live_output_successor_errors())

    def test_authorization_drift_fails(self):
        data = copy.deepcopy(self.record)
        data["execution_authorization"]["comment_id"] = 1
        self.assertTrue(self.errors(record=data))

    def test_open_schema_fails(self):
        data = copy.deepcopy(self.schema)
        data["additionalProperties"] = True
        self.assertTrue(self.errors(schema=data))

    def test_certificate_proof_promotion_fails(self):
        data = copy.deepcopy(self.certificate)
        data["qualification"]["source_theorem_mathematically_proved"] = True
        self.assertTrue(self.errors(certificate=data))

    def test_equality_inflation_fails(self):
        data = copy.deepcopy(self.certificate)
        data["qualification"]["equality_case_classification"] = "complete"
        self.assertTrue(self.errors(certificate=data))

    def test_route_pointer_drift_fails(self):
        routes = copy.deepcopy(self.routes)
        route = next(x for x in routes["routes"] if x["campaign_id"] == "OTP-F-EHRHART")
        route["cert_output"]["commit_sha"] = "0" * 40
        self.assertTrue(self.errors(routes=routes))

    def test_compactness_output_substitution_fails(self):
        routes = copy.deepcopy(self.routes)
        route = next(x for x in routes["routes"] if x["campaign_id"] == "OTP-J1-COMPACTNESS")
        route["cert_output"]["digest"] = "0" * 40
        self.assertTrue(any("successor output identity drift" in x for x in self.errors(routes=routes)))

    def test_compactness_invalid_state_fails(self):
        routes = copy.deepcopy(self.routes)
        route = next(x for x in routes["routes"] if x["campaign_id"] == "OTP-J1-COMPACTNESS")
        route["intake_status"] = "ready"
        self.assertTrue(any("invalid successor route state" in x for x in self.errors(routes=routes)))

    def test_compactness_boundary_weakening_fails(self):
        routes = copy.deepcopy(self.routes)
        route = next(x for x in routes["routes"] if x["campaign_id"] == "OTP-J1-COMPACTNESS")
        route["claim_boundary"] = "qualified"
        self.assertTrue(any("successor boundary missing token" in x for x in self.errors(routes=routes)))

    def test_other_family_output_substitution_fails(self):
        routes = copy.deepcopy(self.routes)
        route = next(x for x in routes["routes"] if x["campaign_id"] == "OTP-J1-COMPACTNESS")
        route["cert_output"] = copy.deepcopy(
            next(x for x in routes["routes"] if x["campaign_id"] == "OTP-F-EHRHART")["cert_output"]
        )
        self.assertTrue(self.errors(routes=routes))

    def test_two_degenerate_output_fails_in_historical_snapshot(self):
        routes = copy.deepcopy(self.routes)
        route = next(x for x in routes["routes"] if x["campaign_id"] == "OTP-J2-TWO-DEGENERATE")
        route["intake_status"] = "qualified"
        route["cert_output"] = copy.deepcopy(M.COMPACTNESS_OUTPUT)
        self.assertTrue(any("OTP-J2-TWO-DEGENERATE: unauthorized output promotion" in x for x in self.errors(routes=routes)))

    def test_uc_loss_fails(self):
        routes = copy.deepcopy(self.routes)
        route = next(x for x in routes["routes"] if x["campaign_id"] == "UC-001")
        route["intake_status"] = "ready"
        route["cert_output"] = None
        self.assertTrue(self.errors(routes=routes))

    def test_nonancestor_content_commit_fails(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["content_is_ancestor_of_head"] = False
        self.assertTrue(self.errors(receipt=receipt))

    def test_route_first_ordering_fails(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["content_is_ancestor_of_route"] = False
        self.assertTrue(self.errors(receipt=receipt))

    def test_changed_registry_at_content_commit_fails(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["routes_at_content"] = "0" * 40
        self.assertTrue(self.errors(receipt=receipt))

    def test_route_commit_scope_inflation_fails(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["route_files"] = [M.ROUTES_PATH, "README.md"]
        self.assertTrue(self.errors(receipt=receipt))

    def test_squash_permission_fails(self):
        data = copy.deepcopy(self.record)
        data["publication_gate"]["protected_merge_method"] = "squash"
        self.assertTrue(self.errors(record=data))

    def test_whole_document_promotion_fails(self):
        data = copy.deepcopy(self.record)
        data["preserved_limitations"]["whole_document_semantic_equivalence"] = "established"
        self.assertTrue(self.errors(record=data))


if __name__ == "__main__":
    unittest.main()
