from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_otp_permanent_output_contract",
    ROOT / "ci/validate_otp_permanent_output_contract.py",
)
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class OTPPermanentOutputContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = M.load(M.CONTRACT)
        self.contract_schema = M.load(M.CONTRACT_SCHEMA)
        self.future_schema = M.load(M.FUTURE_SCHEMA)
        self.routes = M.load(M.ROUTES)
        self.adjudication = M.load(M.ADJUDICATION)

    def errors(self, **kwargs):
        return M.validation_errors(
            contract=copy.deepcopy(kwargs.get("contract", self.contract)),
            contract_schema=copy.deepcopy(kwargs.get("contract_schema", self.contract_schema)),
            future_schema=copy.deepcopy(kwargs.get("future_schema", self.future_schema)),
            routes=copy.deepcopy(kwargs.get("routes", self.routes)),
            adjudication=copy.deepcopy(kwargs.get("adjudication", self.adjudication)),
            adjudication_blob=kwargs.get("adjudication_blob", M.EXPECTED_ADJUDICATION_BLOB),
            future_schema_blob=kwargs.get("future_schema_blob", M.EXPECTED_FUTURE_SCHEMA_BLOB),
            future_certificate_present=kwargs.get("future_certificate_present", True),
            candidate_present=kwargs.get("candidate_present", True),
            staged_certificate_present=kwargs.get("staged_certificate_present", True),
            staged_route_present=kwargs.get("staged_route_present", True),
            contract_files=kwargs.get("contract_files", set(M.EXPECTED_CONTRACT_FILES)),
            successor_mode=kwargs.get("successor_mode", True),
        )

    def design_routes(self):
        r = copy.deepcopy(self.routes)
        x = next(v for v in r["routes"] if v["route_id"] == "MC-ROUTE-OTP-C-PERMANENT-FORMULA")
        x["intake_status"] = "submitted"
        x["claim_boundary"] = "This registered route is limited to the two protected Permanent formula variable-leaf targets with coefficient field complex, n >= 32, log base 2, and constants 128/192. It does not adjudicate or prove either theorem, issue a Cert output, include circuit Theorem 1.1, include the separate 256/384 gate bounds or total-leaf/vertex consequences, establish historical admitted-PDF byte equivalence, or create aggregate OpenAI Ten Proofs authority."
        x["cert_output"] = None
        x["blockers"] = ["No MATHCERT adjudication has been authorized or recorded.", "Circuit Theorem 1.1, separate 256/384 gate bounds, and total-leaf/vertex consequences remain outside this route.", "Historical admitted-PDF byte equivalence remains unestablished."]
        x["reopening_conditions"] = ["Update this route only through a separately authorized, exact-head reviewed MATHCERT adjudication, authority-repin, or scope-extension operation."]
        return r

    def test_current_governed_successor_passes(self): self.assertEqual([], self.errors())
    def test_original_design_state_still_passes(self):
        self.assertEqual([], self.errors(routes=self.design_routes(), successor_mode=False,
            future_certificate_present=False, candidate_present=False,
            staged_certificate_present=False, staged_route_present=False))
    def test_adjudication_blob_substitution_fails(self): self.assertTrue(self.errors(adjudication_blob="0"*40))
    def test_future_schema_blob_drift_fails(self): self.assertTrue(self.errors(future_schema_blob="0"*40))
    def test_target_omission_fails(self):
        d=copy.deepcopy(self.contract); d["output_scope"]["encoded_targets"].pop(); self.assertTrue(self.errors(contract=d))
    def test_circuit_scope_inflation_fails(self):
        d=copy.deepcopy(self.contract); d["output_scope"]["source_projection"]["circuit_target_count"]=1; self.assertTrue(self.errors(contract=d))
    def test_gate_scope_inflation_fails(self):
        d=copy.deepcopy(self.contract); d["preserved_limitations"]["gate_bounds_in_scope"]=True; self.assertTrue(self.errors(contract=d))
    def test_total_size_inflation_fails(self):
        d=copy.deepcopy(self.contract); d["preserved_limitations"]["total_size_consequences_in_scope"]=True; self.assertTrue(self.errors(contract=d))
    def test_historical_pdf_inflation_fails(self):
        d=copy.deepcopy(self.contract); d["preserved_limitations"]["historical_pdf_byte_equivalence"]="established"; self.assertTrue(self.errors(contract=d))
    def test_disposition_inflation_fails(self):
        d=copy.deepcopy(self.contract); d["qualification_semantics"]["permitted_disposition"]="qualified_full_source_theorem"; self.assertTrue(self.errors(contract=d))
    def test_proof_promotion_fails(self):
        d=copy.deepcopy(self.contract); d["state"]["mathematical_target_proved"]=True; self.assertTrue(self.errors(contract=d))
    def test_unbacked_route_promotion_fails(self):
        r=self.design_routes(); x=next(v for v in r["routes"] if v["route_id"]=="MC-ROUTE-OTP-C-PERMANENT-FORMULA"); x["intake_status"]="qualified"
        self.assertTrue(self.errors(routes=r, successor_mode=False, future_certificate_present=False, candidate_present=False, staged_certificate_present=False, staged_route_present=False))
    def test_successor_output_identity_drift_fails(self):
        r=copy.deepcopy(self.routes); x=next(v for v in r["routes"] if v["route_id"]=="MC-ROUTE-OTP-C-PERMANENT-FORMULA"); x["cert_output"]["digest"]="0"*40; self.assertTrue(self.errors(routes=r))
    def test_incomplete_successor_artifact_set_fails(self): self.assertTrue(self.errors(staged_route_present=False))
    def test_control_plan_change_fails(self):
        d=copy.deepcopy(self.contract); d["protected_authority"]["control_plan"]["control_plan_change_requested"]=True; self.assertTrue(self.errors(contract=d))
    def test_separate_human_steward_gate_fails(self):
        d=copy.deepcopy(self.contract); d["execution_gate"]["separate_human_steward_authorization_required"]=True; self.assertTrue(self.errors(contract=d))
    def test_self_reference_allowed_fails(self):
        d=copy.deepcopy(self.contract); d["publication_protocol"]["certificate_must_not_name_its_own_containing_commit"]=False; self.assertTrue(self.errors(contract=d))
    def test_squash_allowed_fails(self):
        d=copy.deepcopy(self.contract); d["publication_protocol"]["squash_merge_prohibited"]=False; self.assertTrue(self.errors(contract=d))
    def test_rebase_allowed_fails(self):
        d=copy.deepcopy(self.contract); d["publication_protocol"]["rebase_merge_prohibited"]=False; self.assertTrue(self.errors(contract=d))
    def test_open_contract_schema_fails(self):
        s=copy.deepcopy(self.contract_schema); s["additionalProperties"]=True; self.assertTrue(self.errors(contract_schema=s))
    def test_nested_contract_schema_closure_fails(self):
        d=copy.deepcopy(self.contract); d["reviewer_requirements"]["unexpected_authority"]="inflated"; self.assertTrue(self.errors(contract=d))
    def test_open_future_schema_fails(self):
        s=copy.deepcopy(self.future_schema); s["additionalProperties"]=True; self.assertTrue(self.errors(future_schema=s))
    def test_output_contract_family_inflation_fails(self): self.assertTrue(self.errors(contract_files=set(M.EXPECTED_CONTRACT_FILES)|{"OTP-X.json"}))
    def test_claim_boundary_weakening_fails(self):
        d=copy.deepcopy(self.contract); d["claim_boundary"]="design-only"; self.assertTrue(self.errors(contract=d))


if __name__ == "__main__": unittest.main()
