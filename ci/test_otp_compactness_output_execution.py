#!/usr/bin/env python3
from __future__ import annotations
import copy, unittest
import validate_otp_compactness_output_execution as v
import validate_otp_j2_route_target_successor as j2

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record=v.load(v.RECORD); cls.schema=v.load(v.SCHEMA); cls.cert=v.load(v.CERT); cls.staged_cert=v.load(v.STAGED_CERT); cls.staged_route=v.load(v.STAGED_ROUTE); cls.routes=j2.pre_output_routes(); cls.history=v.receipt()
    def errors(self, **kw):
        args=dict(record=copy.deepcopy(self.record), schema=copy.deepcopy(self.schema), certificate=copy.deepcopy(self.cert), staged_certificate=copy.deepcopy(self.staged_cert), staged_route=copy.deepcopy(self.staged_route), routes=copy.deepcopy(self.routes), history=copy.deepcopy(self.history))
        args.update(kw); return v.validation_errors(**args)
    def test_baseline(self): self.assertEqual(self.errors(), [])
    def test_live_j2_output_successor_passes_separately(self): self.assertEqual(j2.live_output_successor_errors(), [])
    def test_target_inflation_rejected(self):
        c=copy.deepcopy(self.cert); c["encoded_targets"].append("X"); self.assertTrue(self.errors(certificate=c))
    def test_proof_promotion_rejected(self):
        c=copy.deepcopy(self.cert); c["state"]["mathematical_target_proved"]=True; self.assertTrue(self.errors(certificate=c))
    def test_disposition_substitution_rejected(self):
        c=copy.deepcopy(self.cert); c["qualification"]["disposition"]="proved"; self.assertTrue(self.errors(certificate=c))
    def test_route_output_substitution_rejected(self):
        r=copy.deepcopy(self.routes); v.route_of(r)["cert_output"]["digest"]="0"*40; self.assertTrue(self.errors(routes=r))
    def test_non_compactness_route_mutation_rejected(self):
        h=copy.deepcopy(self.history); h["json_route"]=copy.deepcopy(h["json_route"]); v.others(h["json_route"])[0]["claim_boundary"]="mutated"; self.assertTrue(self.errors(history=h))
    def test_certificate_commit_scope_rejected(self):
        h=copy.deepcopy(self.history); h["content_files"]=[v.CERT_PATH,"other"]; self.assertTrue(self.errors(history=h))
    def test_route_commit_scope_rejected(self):
        h=copy.deepcopy(self.history); h["route_files"]=[v.ROUTES_PATH,"other"]; self.assertTrue(self.errors(history=h))
    def test_ancestry_rejected(self):
        h=copy.deepcopy(self.history); h["route_head"]=False; self.assertTrue(self.errors(history=h))
    def test_staged_transition_commit_rejected(self):
        s=copy.deepcopy(self.staged_route); s["route_transition"]["route_transition_commit"]="0"*40; self.assertTrue(self.errors(staged_route=s))
    def test_review_prepopulation_rejected(self):
        r=copy.deepcopy(self.record); r["review_gate"]["recorded_review"]={"state":"APPROVED"}; self.assertTrue(self.errors(record=r))
    def test_separate_human_gate_rejected(self):
        r=copy.deepcopy(self.record); r["publication_gate"]["separate_human_steward_authorization_required"]=True; self.assertTrue(self.errors(record=r))

if __name__=="__main__": unittest.main(verbosity=2)
