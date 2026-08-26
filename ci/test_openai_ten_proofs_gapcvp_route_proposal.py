#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("gapcvp_route_proposal", ROOT / "ci/validate_openai_ten_proofs_gapcvp_route_proposal.py")
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class GapCVPRouteProposalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.proposal = M.load(M.PROPOSAL)
        self.registry = M.load(M.REGISTRY)
        self.routes = M.load(M.ROUTES)
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
        self.assertTrue(self.errors(proposal=proposal))

    def test_registered_route_presence_fails(self):
        routes = copy.deepcopy(self.routes)
        routes.setdefault("routes", []).append({"route_id": M.ROUTE_ID})
        self.assertTrue(any("must not appear" in e for e in self.errors(routes=routes)))

    def test_target_substitution_fails(self):
        proposal = copy.deepcopy(self.proposal)
        proposal["target_scope"]["lean_theorems"][0] = "GapCVP.Comparator.notTheProtectedTarget"
        self.assertTrue(any("target membership" in e for e in self.errors(proposal=proposal)))

    def test_promise_substitution_fails(self):
        proposal = copy.deepcopy(self.proposal)
        proposal["target_scope"]["promise_interfaces"][3] = "GapCVP.Comparator.unboundedPPromise"
        self.assertTrue(any("promise membership" in e for e in self.errors(proposal=proposal)))

    def test_gap_factor_inflation_fails(self):
        proposal = copy.deepcopy(self.proposal)
        proposal["target_scope"]["gap_factors"][0] = "400"
        self.assertTrue(any("gap-factor" in e for e in self.errors(proposal=proposal)))

    def test_replay_head_drift_fails(self):
        proposal = copy.deepcopy(self.proposal)
        proposal["authority"]["cert_replay_evidence"]["admitted_head"] = "0" * 40
        self.assertTrue(any("authority surface" in e for e in self.errors(proposal=proposal)))

    def test_readback_review_drift_fails(self):
        readback = copy.deepcopy(self.readback)
        h = next(f for f in readback["families"] if f["result_family"] == "OTP-H-GAPCVP")
        h["non_author_review"]["review_id"] = 1
        self.assertTrue(any("review drift" in e for e in self.errors(readback=readback)))

    def test_historical_replay_route_inflation_fails(self):
        replay = copy.deepcopy(self.replay)
        replay["route_state"]["route_proposed"] = True
        self.assertTrue(any("historical replay route state" in e for e in self.errors(replay=replay)))

    def test_route_registry_blob_drift_fails(self):
        self.assertTrue(any("routes blob drift" in e for e in self.errors(local_blobs={"routes": "0" * 40})))

    def test_readback_blob_drift_fails(self):
        self.assertTrue(any("readback blob drift" in e for e in self.errors(local_blobs={"readback": "0" * 40})))

    def test_aggregate_authority_inflation_fails(self):
        registry = copy.deepcopy(self.registry)
        registry["state"]["aggregate_route_count"] = 1
        self.assertTrue(any("state inflation" in e for e in self.errors(registry=registry)))

    def test_cross_family_transfer_inflation_fails(self):
        proposal = copy.deepcopy(self.proposal)
        proposal["route_controls"]["cross_family_transfer"] = True
        self.assertTrue(any("authority inflation" in e for e in self.errors(proposal=proposal)))

    def test_head_change_gate_removal_fails(self):
        proposal = copy.deepcopy(self.proposal)
        proposal["activation"]["head_change_requires_reapproval"] = False
        self.assertTrue(any("reapproval" in e for e in self.errors(proposal=proposal)))

    def test_proposal_blob_drift_fails(self):
        self.assertTrue(any("proposal blob drift" in e for e in self.errors(local_blobs={"proposal": "0" * 40})))


if __name__ == "__main__":
    unittest.main()
