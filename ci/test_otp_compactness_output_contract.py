from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validate_otp_compactness_output_contract", ROOT / "ci/validate_otp_compactness_output_contract.py")
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class OTPCompactnessOutputContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = M.load(M.CONTRACT)
        self.contract_schema = M.load(M.CONTRACT_SCHEMA)
        self.future_schema = M.load(M.FUTURE_SCHEMA)
        self.routes = M.load(M.ROUTES)
        self.adjudication = M.load(M.ADJUDICATION)
        self.construction = M.load(M.CONSTRUCTION)

    def errors(self, **kwargs):
        return M.validation_errors(
            contract=copy.deepcopy(kwargs.get("contract", self.contract)),
            contract_schema=copy.deepcopy(kwargs.get("contract_schema", self.contract_schema)),
            future_schema=copy.deepcopy(kwargs.get("future_schema", self.future_schema)),
            routes=copy.deepcopy(kwargs.get("routes", self.routes)),
            adjudication=copy.deepcopy(kwargs.get("adjudication", self.adjudication)),
            construction=copy.deepcopy(kwargs.get("construction", self.construction)),
            adjudication_blob=kwargs.get("adjudication_blob", M.EXPECTED_ADJUDICATION_BLOB),
            construction_blob=kwargs.get("construction_blob", M.EXPECTED_CONSTRUCTION_BLOB),
            future_schema_blob=kwargs.get("future_schema_blob", M.EXPECTED_FUTURE_SCHEMA_BLOB),
            future_certificate_present=kwargs.get("future_certificate_present", M.FUTURE_CERTIFICATE.exists()),
            candidate_present=kwargs.get("candidate_present", M.OUTPUT_CANDIDATE.exists()),
            staged_certificate_present=kwargs.get("staged_certificate_present", M.STAGED_CERTIFICATE.exists()),
            staged_route_present=kwargs.get("staged_route_present", M.STAGED_ROUTE.exists()),
            contract_files=kwargs.get("contract_files", set(M.EXPECTED_CONTRACT_FILES)),
        )

    def design_routes(self):
        routes = copy.deepcopy(self.routes)
        route = next(v for v in routes["routes"] if v["route_id"] == "MC-ROUTE-OTP-J1-COMPACTNESS")
        route["intake_status"] = "submitted"
        route["cert_output"] = None
        return routes

    def test_current_complete_successor_passes(self): self.assertEqual([], self.errors())
    def test_historical_design_snapshot_passes(self):
        self.assertEqual([], self.errors(routes=self.design_routes(), future_certificate_present=False, candidate_present=False, staged_certificate_present=False, staged_route_present=False))
    def test_authorization_drift_fails(self):
        d=copy.deepcopy(self.contract); d["implementation_authorization"]["comment_id"]=1; self.assertTrue(self.errors(contract=d))
    def test_adjudication_blob_drift_fails(self): self.assertTrue(self.errors(adjudication_blob="0"*40))
    def test_construction_blob_drift_fails(self): self.assertTrue(self.errors(construction_blob="0"*40))
    def test_future_schema_blob_drift_fails(self): self.assertTrue(self.errors(future_schema_blob="0"*40))
    def test_target_omission_fails(self):
        d=copy.deepcopy(self.contract); d["output_scope"]["encoded_targets"].pop(); self.assertTrue(self.errors(contract=d))
    def test_disposition_inflation_fails(self):
        d=copy.deepcopy(self.contract); d["qualification_semantics"]["permitted_disposition"]="qualified_source_theorem"; self.assertTrue(self.errors(contract=d))
    def test_historical_formulation_inflation_fails(self):
        d=copy.deepcopy(self.contract); d["preserved_limitations"]["historical_compactness_formulations_admitted"]=True; self.assertTrue(self.errors(contract=d))
    def test_whole_document_inflation_fails(self):
        d=copy.deepcopy(self.contract); d["preserved_limitations"]["whole_document_semantic_equivalence"]="established"; self.assertTrue(self.errors(contract=d))
    def test_proof_body_inflation_fails(self):
        d=copy.deepcopy(self.contract); d["preserved_limitations"]["proof_body_compared_in_full"]=True; self.assertTrue(self.errors(contract=d))
    def test_proof_promotion_fails(self):
        d=copy.deepcopy(self.contract); d["state"]["mathematical_target_proved"]=True; self.assertTrue(self.errors(contract=d))
    def test_route_promotion_without_successor_fails(self):
        self.assertTrue(self.errors(routes=self.routes, future_certificate_present=False, candidate_present=False, staged_certificate_present=False, staged_route_present=False))
    def test_cert_output_in_design_fails(self):
        routes=self.design_routes(); route=next(v for v in routes["routes"] if v["route_id"]=="MC-ROUTE-OTP-J1-COMPACTNESS"); route["cert_output"]={"repository":"x"}; self.assertTrue(self.errors(routes=routes, future_certificate_present=False, candidate_present=False, staged_certificate_present=False, staged_route_present=False))
    def test_successor_output_identity_drift_fails(self):
        routes=copy.deepcopy(self.routes); route=next(v for v in routes["routes"] if v["route_id"]=="MC-ROUTE-OTP-J1-COMPACTNESS"); route["cert_output"]["digest"]="0"*40; self.assertTrue(self.errors(routes=routes))
    def test_aggregate_authority_fails(self):
        d=copy.deepcopy(self.contract); d["state"]["aggregate_output"]=True; self.assertTrue(self.errors(contract=d))
    def test_control_plan_change_fails(self):
        d=copy.deepcopy(self.contract); d["protected_authority"]["control_plan"]["control_plan_change_requested"]=True; self.assertTrue(self.errors(contract=d))
    def test_new_human_steward_gate_fails(self):
        d=copy.deepcopy(self.contract); d["execution_gate"]["separate_human_steward_authorization_required"]=True; self.assertTrue(self.errors(contract=d))
    def test_publication_mode_drift_fails(self):
        d=copy.deepcopy(self.contract); d["publication_protocol"]["mode"]="single_protected_transaction"; self.assertTrue(self.errors(contract=d))
    def test_self_reference_allowed_fails(self):
        d=copy.deepcopy(self.contract); d["publication_protocol"]["certificate_must_not_name_its_own_containing_commit"]=False; self.assertTrue(self.errors(contract=d))
    def test_squash_allowed_fails(self):
        d=copy.deepcopy(self.contract); d["publication_protocol"]["squash_merge_prohibited"]=False; self.assertTrue(self.errors(contract=d))
    def test_rebase_allowed_fails(self):
        d=copy.deepcopy(self.contract); d["publication_protocol"]["rebase_merge_prohibited"]=False; self.assertTrue(self.errors(contract=d))
    def test_partial_successor_artifacts_fail(self):
        design=self.design_routes()
        self.assertTrue(self.errors(routes=design, future_certificate_present=True, candidate_present=False, staged_certificate_present=False, staged_route_present=False))
        self.assertTrue(self.errors(routes=design, future_certificate_present=False, candidate_present=True, staged_certificate_present=False, staged_route_present=False))
        self.assertTrue(self.errors(routes=design, future_certificate_present=False, candidate_present=False, staged_certificate_present=True, staged_route_present=False))
        self.assertTrue(self.errors(routes=design, future_certificate_present=False, candidate_present=False, staged_certificate_present=False, staged_route_present=True))
    def test_contract_membership_inflation_fails(self): self.assertTrue(self.errors(contract_files=set(M.EXPECTED_CONTRACT_FILES)|{"OTP-X.json"}))
    def test_contract_schema_weakening_fails(self):
        s=copy.deepcopy(self.contract_schema); s["const"]["contract_state"]="executed"; self.assertTrue(self.errors(contract_schema=s))
    def test_open_future_schema_fails(self):
        s=copy.deepcopy(self.future_schema); s["additionalProperties"]=True; self.assertTrue(self.errors(future_schema=s))
    def test_claim_boundary_weakening_fails(self):
        d=copy.deepcopy(self.contract); d["claim_boundary"]="design-only"; self.assertTrue(self.errors(contract=d))


if __name__ == "__main__": unittest.main()
