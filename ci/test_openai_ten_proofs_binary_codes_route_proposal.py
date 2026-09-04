#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "binary_codes_route_proposal",
    ROOT / "ci/validate_openai_ten_proofs_binary_codes_route_proposal.py",
)
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class BinaryCodesRouteProposalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.proposal = M.load(M.PROPOSAL)
        self.registry = M.load(M.REGISTRY)
        self.routes = M.load_at_commit(M.PROPOSAL_PROTECTED_PREDECESSOR_HEAD, M.ROUTE_REGISTRY_PATH)
        self.replay = M.load(M.REPLAY)
        self.readback = M.load(M.READBACK)

    def errors(self, **kwargs):
        args = {
            "proposal": copy.deepcopy(self.proposal),
            "registry": copy.deepcopy(self.registry),
            "routes": copy.deepcopy(self.routes),
            "replay": copy.deepcopy(self.replay),
            "readback": copy.deepcopy(self.readback),
        }
        args.update(kwargs)
        return M.validation_errors(**args)

    def test_current_candidate_is_clear(self):
        self.assertEqual(self.errors(), [])

    def test_route_registration_inflation_fails(self):
        proposal = copy.deepcopy(self.proposal)
        proposal["route_controls"]["may_register_route"] = True
        self.assertTrue(any("authority inflation" in error for error in self.errors(proposal=proposal)))

    def test_registered_route_presence_at_proposal_predecessor_fails(self):
        routes = copy.deepcopy(self.routes)
        routes.setdefault("routes", []).append({"route_id": M.ROUTE_ID})
        self.assertTrue(any("must not appear" in error for error in self.errors(routes=routes)))

    def test_target_substitution_fails(self):
        proposal = copy.deepcopy(self.proposal)
        proposal["target_scope"]["lean_theorems"][0] = "MetricCodes.Hamming.notTheProtectedTarget"
        self.assertTrue(any("target membership" in error for error in self.errors(proposal=proposal)))

    def test_classification_inflation_fails(self):
        proposal = copy.deepcopy(self.proposal)
        proposal["target_scope"]["classifications"][1] = "source_verbatim"
        self.assertTrue(any("classification" in error for error in self.errors(proposal=proposal)))

    def test_mandatory_qualification_drift_fails(self):
        proposal = copy.deepcopy(self.proposal)
        proposal["target_scope"]["mandatory_qualifications"][1] = "sInf is source-equivalent without a bridge."
        self.assertTrue(any("qualification" in error for error in self.errors(proposal=proposal)))

    def test_permitted_axiom_inflation_fails(self):
        proposal = copy.deepcopy(self.proposal)
        proposal["target_scope"]["permitted_axioms"].append("sorryAx")
        self.assertTrue(any("axiom" in error for error in self.errors(proposal=proposal)))

    def test_replay_head_drift_fails(self):
        proposal = copy.deepcopy(self.proposal)
        proposal["authority"]["cert_replay_evidence"]["admitted_head"] = "0" * 40
        self.assertTrue(any("authority surface" in error for error in self.errors(proposal=proposal)))

    def test_readback_review_drift_fails(self):
        readback = copy.deepcopy(self.readback)
        b1 = next(f for f in readback["families"] if f["result_family"] == M.FAMILY)
        b1["non_author_review"]["review_id"] = 1
        self.assertTrue(any("review drift" in error for error in self.errors(readback=readback)))

    def test_historical_replay_route_inflation_fails(self):
        replay = copy.deepcopy(self.replay)
        replay["route_state"]["route_proposed"] = True
        self.assertTrue(any("historical replay route state" in error for error in self.errors(replay=replay)))

    def test_route_registry_blob_drift_fails(self):
        self.assertTrue(any("routes blob drift" in error for error in self.errors(local_blobs={"routes": "0" * 40})))

    def test_readback_blob_drift_fails(self):
        self.assertTrue(any("readback blob drift" in error for error in self.errors(local_blobs={"readback": "0" * 40})))

    def test_proposal_blob_drift_fails(self):
        self.assertTrue(any("proposal blob drift" in error for error in self.errors(local_blobs={"proposal": "0" * 40})))

    def test_registry_blob_drift_fails(self):
        self.assertTrue(any("registry blob drift" in error for error in self.errors(local_blobs={"registry": "0" * 40})))

    def test_aggregate_authority_inflation_fails(self):
        registry = copy.deepcopy(self.registry)
        registry["state"]["aggregate_route_count"] = 1
        self.assertTrue(any("state inflation" in error for error in self.errors(registry=registry)))

    def test_cross_family_transfer_inflation_fails(self):
        proposal = copy.deepcopy(self.proposal)
        proposal["route_controls"]["cross_family_transfer"] = True
        self.assertTrue(any("authority inflation" in error for error in self.errors(proposal=proposal)))

    def test_head_change_gate_removal_fails(self):
        proposal = copy.deepcopy(self.proposal)
        proposal["activation"]["head_change_requires_reapproval"] = False
        self.assertTrue(any("reapproval" in error for error in self.errors(proposal=proposal)))


if __name__ == "__main__":
    unittest.main()
