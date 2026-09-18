#!/usr/bin/env python3
from __future__ import annotations
import copy, unittest
from validate_agent_continuity_adoption import ROOT, adoption_errors, load_json

class AgentContinuityAdoptionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = load_json(ROOT / ".gcl/agent-continuity.json")
        cls.agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    def test_repository_candidate_is_valid(self):
        self.assertEqual([], adoption_errors(self.record, self.agents))

    def test_predecessor_certification_cannot_be_inherited(self):
        r = copy.deepcopy(self.record)
        r["authority_preservation"]["predecessor_conclusion_implies_certification"] = True
        self.assertTrue(any("predecessor_conclusion" in e for e in adoption_errors(r, self.agents)))

    def test_continuity_receipt_cannot_satisfy_independence(self):
        r = copy.deepcopy(self.record)
        r["authority_preservation"]["continuity_receipt_satisfies_independence"] = True
        self.assertTrue(any("continuity_receipt" in e for e in adoption_errors(r, self.agents)))

    def test_agent_substitution_cannot_inherit_independence(self):
        r = copy.deepcopy(self.record)
        r["authority_preservation"]["substantive_independence_inherited_across_agent_substitution"] = True
        self.assertTrue(any("substantive_independence" in e for e in adoption_errors(r, self.agents)))

    def test_changed_subject_requires_exact_rebind(self):
        r = copy.deepcopy(self.record)
        r["rebind_requirements"]["exact_claim_or_subject"] = False
        self.assertTrue(any("exact_claim_or_subject" in e for e in adoption_errors(r, self.agents)))

    def test_changed_evidence_requires_rebind(self):
        r = copy.deepcopy(self.record)
        r["rebind_requirements"]["material_evidence_digests"] = False
        self.assertTrue(any("material_evidence_digests" in e for e in adoption_errors(r, self.agents)))

    def test_ci_or_merge_cannot_imply_certification(self):
        r = copy.deepcopy(self.record)
        r["authority_preservation"]["ci_or_merge_implies_certification"] = True
        self.assertTrue(any("ci_or_merge" in e for e in adoption_errors(r, self.agents)))

if __name__ == "__main__":
    unittest.main()
