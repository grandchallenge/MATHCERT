from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_otp_permanent_output_execution",
    ROOT / "ci/validate_otp_permanent_output_execution.py",
)
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class OTPPermanentOutputExecutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = M.load(M.RECORD)
        cls.schema = M.load(M.SCHEMA)
        cls.certificate = M.load(M.CERTIFICATE)
        cls.staged_certificate = M.load(M.STAGED_CERTIFICATE)
        cls.staged_route = M.load(M.STAGED_ROUTE)
        cls.routes = M.load(M.ROUTES)
        cls.history = M.receipt()
        cls.blobs = {
            "record": M.EXPECTED["record"],
            "schema": M.EXPECTED["schema"],
            "certificate": M.EXPECTED["certificate"],
            "staged_certificate": M.EXPECTED["certificate"],
            "staged_route": M.EXPECTED["staged_route"],
            "contract": M.EXPECTED["contract"],
            "adjudication": M.EXPECTED["adjudication"],
            "certificate_schema": M.EXPECTED["certificate_schema"],
            "routes_after": M.EXPECTED["routes_after"],
        }

    def errors(self, **kwargs):
        return M.validation_errors(
            record=copy.deepcopy(kwargs.get("record", self.record)),
            schema=copy.deepcopy(kwargs.get("schema", self.schema)),
            certificate=copy.deepcopy(kwargs.get("certificate", self.certificate)),
            staged_certificate=copy.deepcopy(kwargs.get("staged_certificate", self.staged_certificate)),
            staged_route=copy.deepcopy(kwargs.get("staged_route", self.staged_route)),
            routes=copy.deepcopy(kwargs.get("routes", self.routes)),
            history=copy.deepcopy(kwargs.get("history", self.history)),
            blobs=copy.deepcopy(kwargs.get("blobs", self.blobs)),
        )

    def test_current_execution_passes(self):
        self.assertEqual([], self.errors())

    def test_record_blob_substitution_fails(self):
        b=copy.deepcopy(self.blobs); b["record"]="0"*40; self.assertTrue(self.errors(blobs=b))

    def test_schema_opening_fails(self):
        s=copy.deepcopy(self.schema); s["additionalProperties"]=True; self.assertTrue(self.errors(schema=s))

    def test_target_omission_fails(self):
        c=copy.deepcopy(self.certificate); c["encoded_targets"].pop(); self.assertTrue(self.errors(certificate=c))

    def test_circuit_scope_inflation_fails(self):
        c=copy.deepcopy(self.certificate); c["qualification"]["source_projection"]["circuit_target_count"]=1; self.assertTrue(self.errors(certificate=c))

    def test_gate_scope_inflation_fails(self):
        c=copy.deepcopy(self.certificate); c["preserved_limitations"]["gate_bounds_in_scope"]=True; self.assertTrue(self.errors(certificate=c))

    def test_total_size_inflation_fails(self):
        c=copy.deepcopy(self.certificate); c["preserved_limitations"]["total_size_consequences_in_scope"]=True; self.assertTrue(self.errors(certificate=c))

    def test_historical_pdf_inflation_fails(self):
        c=copy.deepcopy(self.certificate); c["preserved_limitations"]["historical_pdf_byte_equivalence"]="established"; self.assertTrue(self.errors(certificate=c))

    def test_proof_promotion_fails(self):
        c=copy.deepcopy(self.certificate); c["state"]["mathematical_target_proved"]=True; self.assertTrue(self.errors(certificate=c))

    def test_claim_promotion_fails(self):
        c=copy.deepcopy(self.certificate); c["state"]["may_promote_claim"]=True; self.assertTrue(self.errors(certificate=c))

    def test_aggregate_output_fails(self):
        c=copy.deepcopy(self.certificate); c["state"]["aggregate_output"]=True; self.assertTrue(self.errors(certificate=c))

    def test_staged_certificate_byte_drift_fails(self):
        s=copy.deepcopy(self.staged_certificate); s["certificate_id"]="X"; self.assertTrue(self.errors(staged_certificate=s))

    def test_route_output_commit_substitution_fails(self):
        r=copy.deepcopy(self.routes); p=M.permanent_route(r); p["cert_output"]["commit_sha"]="0"*40; self.assertTrue(self.errors(routes=r))

    def test_route_output_blob_substitution_fails(self):
        r=copy.deepcopy(self.routes); p=M.permanent_route(r); p["cert_output"]["digest"]="0"*40; self.assertTrue(self.errors(routes=r))

    def test_route_scope_inflation_fails(self):
        r=copy.deepcopy(self.routes); p=M.permanent_route(r); p["target_claim_ids"].append("PermanentRollout.fake"); self.assertTrue(self.errors(routes=r))

    def test_staged_transition_commit_substitution_fails(self):
        s=copy.deepcopy(self.staged_route); s["route_transition"]["route_transition_commit"]="0"*40; self.assertTrue(self.errors(staged_route=s))

    def test_control_plan_change_fails(self):
        r=copy.deepcopy(self.record); r["protected_authority"]["control_plan"]["control_plan_change_requested"]=True; self.assertTrue(self.errors(record=r))

    def test_separate_human_steward_gate_fails(self):
        r=copy.deepcopy(self.record); r["publication_gate"]["separate_human_steward_authorization_required"]=True; self.assertTrue(self.errors(record=r))

    def test_squash_allowed_fails(self):
        r=copy.deepcopy(self.record); r["publication_gate"]["squash_merge_prohibited"]=False; self.assertTrue(self.errors(record=r))

    def test_rebase_allowed_fails(self):
        r=copy.deepcopy(self.record); r["publication_gate"]["rebase_merge_prohibited"]=False; self.assertTrue(self.errors(record=r))

    def test_prepopulated_review_fails(self):
        r=copy.deepcopy(self.record); r["review_gate"]["recorded_review"]={"state":"APPROVED"}; self.assertTrue(self.errors(record=r))

    def test_content_ancestry_loss_fails(self):
        h=copy.deepcopy(self.history); h["content_is_ancestor_of_head"]=False; self.assertTrue(self.errors(history=h))

    def test_route_ancestry_loss_fails(self):
        h=copy.deepcopy(self.history); h["route_is_ancestor_of_head"]=False; self.assertTrue(self.errors(history=h))

    def test_content_commit_scope_drift_fails(self):
        h=copy.deepcopy(self.history); h["content_files"]=[M.CERT_PATH, "x"]; self.assertTrue(self.errors(history=h))

    def test_route_commit_scope_drift_fails(self):
        h=copy.deepcopy(self.history); h["route_files"]=[M.ROUTES_PATH, "x"]; self.assertTrue(self.errors(history=h))

    def test_non_permanent_route_mutation_fails(self):
        h=copy.deepcopy(self.history); h["routes_json_at_route"]["routes"][0]["intake_status"]="pending"; self.assertTrue(self.errors(history=h))


if __name__ == "__main__":
    unittest.main()
