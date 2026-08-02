from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_otp_ehrhart_output_contract",
    ROOT / "ci/validate_otp_ehrhart_output_contract.py",
)
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class OTPEhrhartOutputContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = json.loads(M.CONTRACT.read_text(encoding="utf-8"))
        self.contract_schema = json.loads(M.CONTRACT_SCHEMA.read_text(encoding="utf-8"))
        self.future_schema = json.loads(M.FUTURE_SCHEMA.read_text(encoding="utf-8"))
        self.routes = json.loads(M.ROUTES.read_text(encoding="utf-8"))
        transition = json.loads(
            (ROOT / "governance/result_family_output_candidates/staged_route_transitions/OTP-F-EHRHART.json").read_text(encoding="utf-8")
        )
        index = next(i for i, route in enumerate(self.routes["routes"]) if route["route_id"] == "MC-ROUTE-OTP-F-EHRHART")
        self.routes["routes"][index] = copy.deepcopy(transition["before"])
        self.adjudication = json.loads(M.ADJUDICATION.read_text(encoding="utf-8"))
        self.attestation = json.loads(M.ATTESTATION.read_text(encoding="utf-8"))

    def errors(self, **kwargs):
        return M.validation_errors(
            contract=copy.deepcopy(kwargs.get("contract", self.contract)),
            contract_schema=copy.deepcopy(kwargs.get("contract_schema", self.contract_schema)),
            future_schema=copy.deepcopy(kwargs.get("future_schema", self.future_schema)),
            routes=copy.deepcopy(kwargs.get("routes", self.routes)),
            adjudication=copy.deepcopy(kwargs.get("adjudication", self.adjudication)),
            attestation=copy.deepcopy(kwargs.get("attestation", self.attestation)),
            adjudication_blob=kwargs.get("adjudication_blob", M.EXPECTED_ADJUDICATION_BLOB),
            attestation_blob=kwargs.get("attestation_blob", M.EXPECTED_ATTESTATION_BLOB),
            future_schema_blob=kwargs.get("future_schema_blob", M.EXPECTED_FUTURE_SCHEMA_BLOB),
            future_certificate_present=kwargs.get("future_certificate_present", False),
            candidate_present=kwargs.get("candidate_present", False),
            contract_files=kwargs.get("contract_files", set(M.EXPECTED_CONTRACT_FILES)),
        )

    def test_current_contract_passes(self) -> None:
        self.assertEqual([], self.errors())

    def test_authorization_comment_drift_is_rejected(self) -> None:
        data = copy.deepcopy(self.contract)
        data["implementation_authorization"]["comment_id"] = 1
        self.assertTrue(self.errors(contract=data))

    def test_non_design_state_is_rejected(self) -> None:
        data = copy.deepcopy(self.contract)
        data["contract_state"] = "executed"
        self.assertTrue(self.errors(contract=data))

    def test_adjudication_blob_drift_is_rejected(self) -> None:
        self.assertTrue(self.errors(adjudication_blob="0" * 40))

    def test_attestation_blob_drift_is_rejected(self) -> None:
        self.assertTrue(self.errors(attestation_blob="0" * 40))

    def test_future_schema_blob_drift_is_rejected(self) -> None:
        self.assertTrue(self.errors(future_schema_blob="0" * 40))

    def test_target_omission_is_rejected(self) -> None:
        data = copy.deepcopy(self.contract)
        data["output_scope"]["encoded_targets"].pop()
        self.assertTrue(self.errors(contract=data))

    def test_qualification_disposition_inflation_is_rejected(self) -> None:
        data = copy.deepcopy(self.contract)
        data["qualification_semantics"]["permitted_disposition"] = "source_theorem_proved"
        self.assertTrue(self.errors(contract=data))

    def test_certificate_identity_drift_is_rejected(self) -> None:
        data = copy.deepcopy(self.contract)
        data["future_certificate"]["certificate_id"] = "MC-OTP-F-EHRHART-PROVED-001"
        self.assertTrue(self.errors(contract=data))

    def test_non_atomic_execution_is_rejected(self) -> None:
        data = copy.deepcopy(self.contract)
        data["atomic_execution"]["mode"] = "split_operations"
        self.assertTrue(self.errors(contract=data))

    def test_partial_state_is_rejected(self) -> None:
        data = copy.deepcopy(self.contract)
        data["atomic_execution"]["partial_state_prohibited"] = False
        self.assertTrue(self.errors(contract=data))

    def test_route_qualification_during_design_is_rejected(self) -> None:
        routes = copy.deepcopy(self.routes)
        route = next(item for item in routes["routes"] if item["route_id"] == "MC-ROUTE-OTP-F-EHRHART")
        route["intake_status"] = "qualified"
        self.assertTrue(self.errors(routes=routes))

    def test_cert_output_insertion_during_design_is_rejected(self) -> None:
        routes = copy.deepcopy(self.routes)
        route = next(item for item in routes["routes"] if item["route_id"] == "MC-ROUTE-OTP-F-EHRHART")
        route["cert_output"] = {"path": "forged.json"}
        self.assertTrue(self.errors(routes=routes))

    def test_mathematical_proof_promotion_is_rejected(self) -> None:
        data = copy.deepcopy(self.contract)
        data["state"]["mathematical_target_proved"] = True
        self.assertTrue(self.errors(contract=data))

    def test_future_schema_proof_promotion_is_rejected(self) -> None:
        schema = copy.deepcopy(self.future_schema)
        schema["properties"]["state"]["const"]["mathematical_target_proved"] = True
        self.assertTrue(self.errors(future_schema=schema))

    def test_open_future_schema_is_rejected(self) -> None:
        schema = copy.deepcopy(self.future_schema)
        schema["additionalProperties"] = True
        self.assertTrue(self.errors(future_schema=schema))

    def test_premature_certificate_file_is_rejected(self) -> None:
        self.assertTrue(self.errors(future_certificate_present=True))

    def test_premature_candidate_is_rejected(self) -> None:
        self.assertTrue(self.errors(candidate_present=True))

    def test_equality_classification_is_rejected(self) -> None:
        data = copy.deepcopy(self.contract)
        data["preserved_limitations"]["classification_or_uniqueness_of_all_equality_cases"] = "established"
        self.assertTrue(self.errors(contract=data))

    def test_aggregate_authority_is_rejected(self) -> None:
        data = copy.deepcopy(self.contract)
        data["state"]["aggregate_output"] = True
        self.assertTrue(self.errors(contract=data))

    def test_claim_boundary_weakening_is_rejected(self) -> None:
        data = copy.deepcopy(self.contract)
        data["claim_boundary"] = "The Ehrhart theorem is certified."
        self.assertTrue(self.errors(contract=data))

    def test_output_contract_family_inflation_is_rejected(self) -> None:
        self.assertTrue(self.errors(contract_files={"OTP-F-EHRHART.json", "OTP-J1-COMPACTNESS.json"}))


if __name__ == "__main__":
    unittest.main()
