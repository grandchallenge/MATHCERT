#!/usr/bin/env python3
from __future__ import annotations

import copy
import unittest

from validate_agent_continuity_adoption import ROOT, adoption_errors, load_json

class AgentContinuityAdoptionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = load_json(ROOT / ".gcl/agent-continuity.json")
        cls.agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    def errors(self, mutate) -> list[str]:
        record = copy.deepcopy(self.record)
        mutate(record)
        return adoption_errors(record, self.agents)

    def test_repository_candidate_is_valid(self) -> None:
        self.assertEqual([], adoption_errors(self.record, self.agents))

    def test_predecessor_conclusion_cannot_be_inherited_as_certification(self) -> None:
        errors = self.errors(lambda r: r["fail_closed"].update({"predecessor_agent_conclusion_is_current_certification": True}))
        self.assertTrue(any("predecessor_agent_conclusion" in error for error in errors))

    def test_continuity_receipt_cannot_satisfy_independence(self) -> None:
        errors = self.errors(lambda r: r["fail_closed"].update({"continuity_receipt_satisfies_independence": True}))
        self.assertTrue(any("continuity_receipt_satisfies_independence" in error for error in errors))

    def test_certification_authority_is_not_inherited(self) -> None:
        errors = self.errors(lambda r: r["succession"].update({"certification_authority_inherited": True}))
        self.assertTrue(any("certification_authority_inherited" in error for error in errors))

    def test_changed_subject_or_evidence_forces_rebind(self) -> None:
        errors = self.errors(lambda r: r["fail_closed"].update({"changed_exact_subject_or_evidence_requires_rebind": False}))
        self.assertTrue(any("changed_exact_subject_or_evidence_requires_rebind" in error for error in errors))

    def test_ci_or_merge_cannot_imply_certification(self) -> None:
        errors = self.errors(lambda r: r["fail_closed"].update({"ci_or_protected_merge_implies_certification": True}))
        self.assertTrue(any("ci_or_protected_merge_implies_certification" in error for error in errors))

if __name__ == "__main__":
    unittest.main()
