from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

import validate_otp_j2_route_target_successor as j2

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_otp_j2_output_contract",
    ROOT / "ci/validate_otp_j2_output_contract.py",
)
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class OTPJ2OutputContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = M.load(M.CONTRACT)
        self.contract_schema = M.load(M.CONTRACT_SCHEMA)
        self.future_schema = M.load(M.FUTURE_SCHEMA)
        # The protected design contract is immutable and is tested against the
        # exact route state immediately before the separately governed output.
        self.routes = j2.pre_output_routes()
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
            future_certificate_present=kwargs.get("future_certificate_present", False),
            candidate_present=kwargs.get("candidate_present", False),
            staged_certificate_present=kwargs.get("staged_certificate_present", False),
            staged_route_present=kwargs.get("staged_route_present", False),
            contract_files=kwargs.get("contract_files", set(M.EXPECTED_CONTRACT_FILES)),
        )

    def mutate_contract(self, fn):
        d = copy.deepcopy(self.contract)
        fn(d)
        return d

    def test_current_contract_passes(self):
        self.assertEqual([], self.errors())

    def test_live_output_successor_passes_separately(self):
        self.assertEqual([], j2.live_output_successor_errors())

    def test_authorization_comment_drift_fails(self):
        d=self.mutate_contract(lambda x: x["implementation_authorization"].update(comment_id=0)); self.assertTrue(self.errors(contract=d))
    def test_authorization_disposition_drift_fails(self):
        d=self.mutate_contract(lambda x: x["implementation_authorization"].update(disposition="AUTHORIZE_BROADER_OUTPUT")); self.assertTrue(self.errors(contract=d))
    def test_adjudication_blob_substitution_fails(self): self.assertTrue(self.errors(adjudication_blob="0"*40))
    def test_future_schema_blob_substitution_fails(self): self.assertTrue(self.errors(future_schema_blob="0"*40))
    def test_target_omission_fails(self):
        d=copy.deepcopy(self.contract); d["output_scope"]["encoded_targets"].pop(); self.assertTrue(self.errors(contract=d))
    def test_historical_target_reinserted_as_live_fails(self):
        d=copy.deepcopy(self.contract); d["output_scope"]["encoded_targets"][0]=M.EXPECTED_HISTORICAL_TARGETS[0]; self.assertTrue(self.errors(contract=d))
    def test_historical_target_identity_drift_fails(self):
        d=copy.deepcopy(self.contract); d["output_scope"]["historical_predecessor_targets"].pop(); self.assertTrue(self.errors(contract=d))
    def test_stronger_coloring_scope_reinsertion_fails(self):
        d=copy.deepcopy(self.contract); d["output_scope"]["source_projection"]["stronger_coloring_side_property_in_scope"]=True; self.assertTrue(self.errors(contract=d))
    def test_source_core_weakening_fails(self):
        d=copy.deepcopy(self.contract); d["output_scope"]["source_projection"]["two_degenerate"]=False; self.assertTrue(self.errors(contract=d))
    def test_source_hash_substitution_fails(self):
        d=copy.deepcopy(self.contract); d["protected_authority"]["evidence"]["current_source_sha256"]="0"*64; self.assertTrue(self.errors(contract=d))
    def test_formal_subject_substitution_fails(self):
        d=copy.deepcopy(self.contract); d["protected_authority"]["evidence"]["formal_subject_commit"]="0"*40; self.assertTrue(self.errors(contract=d))
    def test_projection_digest_substitution_fails(self):
        d=copy.deepcopy(self.contract); d["protected_authority"]["evidence"]["source_faithful_projection_digest"]="0"*40; self.assertTrue(self.errors(contract=d))
    def test_disposition_inflation_fails(self):
        d=copy.deepcopy(self.contract); d["qualification_semantics"]["permitted_disposition"]="qualified_full_source_theorem"; self.assertTrue(self.errors(contract=d))
    def test_certificate_identity_drift_fails(self):
        d=copy.deepcopy(self.contract); d["future_certificate"]["certificate_id"]="MC-OTP-J2-BROADER-QUAL-001"; self.assertTrue(self.errors(contract=d))
    def test_certificate_path_drift_fails(self):
        d=copy.deepcopy(self.contract); d["future_certificate"]["path"]="certificates/formal_sources/broader.json"; self.assertTrue(self.errors(contract=d))
    def test_proof_promotion_fails(self):
        d=copy.deepcopy(self.contract); d["state"]["mathematical_target_proved"]=True; self.assertTrue(self.errors(contract=d))
    def test_claim_promotion_fails(self):
        d=copy.deepcopy(self.contract); d["state"]["may_promote_claim"]=True; self.assertTrue(self.errors(contract=d))
    def test_aggregate_output_fails(self):
        d=copy.deepcopy(self.contract); d["state"]["aggregate_output"]=True; self.assertTrue(self.errors(contract=d))
    def test_stronger_coloring_certification_fails(self):
        d=copy.deepcopy(self.contract); d["state"]["stronger_coloring_property_certified"]=True; self.assertTrue(self.errors(contract=d))
    def test_control_plan_change_fails(self):
        d=copy.deepcopy(self.contract); d["protected_authority"]["control_plan"]["control_plan_change_requested"]=True; self.assertTrue(self.errors(contract=d))
    def test_redundant_human_steward_gate_fails(self):
        d=copy.deepcopy(self.contract); d["execution_gate"]["separate_human_steward_authorization_required"]=True; self.assertTrue(self.errors(contract=d))
    def test_expected_head_guard_removed_fails(self):
        d=copy.deepcopy(self.contract); d["execution_gate"]["expected_head_guard_required"]=False; self.assertTrue(self.errors(contract=d))
    def test_readback_removed_fails(self):
        d=copy.deepcopy(self.contract); d["execution_gate"]["protected_main_readback_required"]=False; self.assertTrue(self.errors(contract=d))
    def test_publication_mode_drift_fails(self):
        d=copy.deepcopy(self.contract); d["publication_protocol"]["mode"]="single_transaction"; self.assertTrue(self.errors(contract=d))
    def test_route_first_allowed_fails(self):
        d=copy.deepcopy(self.contract); d["publication_protocol"]["route_first_ordering_prohibited"]=False; self.assertTrue(self.errors(contract=d))
    def test_self_reference_allowed_fails(self):
        d=copy.deepcopy(self.contract); d["publication_protocol"]["certificate_must_not_name_its_own_containing_commit"]=False; self.assertTrue(self.errors(contract=d))
    def test_squash_allowed_fails(self):
        d=copy.deepcopy(self.contract); d["publication_protocol"]["squash_merge_prohibited"]=False; self.assertTrue(self.errors(contract=d))
    def test_rebase_allowed_fails(self):
        d=copy.deepcopy(self.contract); d["publication_protocol"]["rebase_merge_prohibited"]=False; self.assertTrue(self.errors(contract=d))
    def test_ancestry_rule_removed_fails(self):
        d=copy.deepcopy(self.contract); d["publication_protocol"]["route_transition_commit_must_descend_from_certificate_content_commit"]=False; self.assertTrue(self.errors(contract=d))
    def test_route_promotion_during_design_fails(self):
        r=copy.deepcopy(self.routes); x=next(v for v in r["routes"] if v["route_id"]=="MC-ROUTE-OTP-J2-TWO-DEGENERATE"); x["intake_status"]="qualified"; self.assertTrue(self.errors(routes=r))
    def test_cert_output_during_design_fails(self):
        r=copy.deepcopy(self.routes); x=next(v for v in r["routes"] if v["route_id"]=="MC-ROUTE-OTP-J2-TWO-DEGENERATE"); x["cert_output"]={"repository":"x"}; self.assertTrue(self.errors(routes=r))
    def test_route_target_drift_fails(self):
        r=copy.deepcopy(self.routes); x=next(v for v in r["routes"] if v["route_id"]=="MC-ROUTE-OTP-J2-TWO-DEGENERATE"); x["target_claim_ids"].append("OtherFamily.theorem"); self.assertTrue(self.errors(routes=r))
    def test_premature_certificate_fails(self): self.assertTrue(self.errors(future_certificate_present=True))
    def test_premature_candidate_fails(self): self.assertTrue(self.errors(candidate_present=True))
    def test_premature_staged_certificate_fails(self): self.assertTrue(self.errors(staged_certificate_present=True))
    def test_premature_staged_route_fails(self): self.assertTrue(self.errors(staged_route_present=True))
    def test_contract_membership_inflation_fails(self): self.assertTrue(self.errors(contract_files=set(M.EXPECTED_CONTRACT_FILES)|{"OTP-X.json"}))
    def test_contract_schema_drift_fails(self):
        s=copy.deepcopy(self.contract_schema); s["const"]["contract_id"]="BROADER"; self.assertTrue(self.errors(contract_schema=s))
    def test_open_future_schema_fails(self):
        s=copy.deepcopy(self.future_schema); s["additionalProperties"]=True; self.assertTrue(self.errors(future_schema=s))
    def test_future_target_drift_fails(self):
        s=copy.deepcopy(self.future_schema); s["properties"]["encoded_targets"]["const"].pop(); self.assertTrue(self.errors(future_schema=s))
    def test_future_stronger_coloring_scope_fails(self):
        s=copy.deepcopy(self.future_schema); s["properties"]["qualification"]["const"]["source_projection"]["stronger_coloring_side_property_in_scope"]=True; self.assertTrue(self.errors(future_schema=s))
    def test_whole_document_equivalence_inflation_fails(self):
        d=copy.deepcopy(self.contract); d["preserved_limitations"]["whole_document_semantic_equivalence"]="established"; self.assertTrue(self.errors(contract=d))
    def test_proof_body_inflation_fails(self):
        d=copy.deepcopy(self.contract); d["preserved_limitations"]["proof_body_compared_in_full"]=True; self.assertTrue(self.errors(contract=d))
    def test_entropy_reformalization_inflation_fails(self):
        d=copy.deepcopy(self.contract); d["preserved_limitations"]["source_internal_entropy_lemmas_reformalized"]=True; self.assertTrue(self.errors(contract=d))
    def test_other_family_authority_fails(self):
        d=copy.deepcopy(self.contract); d["preserved_limitations"]["other_family_outputs_authorized"]=True; self.assertTrue(self.errors(contract=d))
    def test_claim_boundary_weakening_fails(self):
        d=copy.deepcopy(self.contract); d["claim_boundary"]="design-only"; self.assertTrue(self.errors(contract=d))


if __name__ == "__main__":
    unittest.main()
