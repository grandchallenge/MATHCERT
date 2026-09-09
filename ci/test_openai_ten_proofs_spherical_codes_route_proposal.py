#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "spherical_codes_route_proposal",
    ROOT / "ci/validate_openai_ten_proofs_spherical_codes_route_proposal.py",
)
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class SphericalCodesRouteProposalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.proposal = M.load(M.PROPOSAL)
        self.registry = M.load(M.REGISTRY)
        self.routes = M.load_routes_at_commit(M.PREDECESSOR_HEAD)
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

    def test_registered_route_presence_at_predecessor_fails(self):
        routes = copy.deepcopy(self.routes)
        routes.setdefault("routes", []).append({"route_id": M.ROUTE_ID})
        self.assertTrue(any("must not appear" in error for error in self.errors(routes=routes)))

    def test_target_substitution_fails(self):
        proposal = copy.deepcopy(self.proposal)
        proposal["target_scope"]["lean_theorems"][0] = "MetricCodes.Spherical.notTheProtectedTarget"
        self.assertTrue(any("target membership" in error for error in self.errors(proposal=proposal)))

    def test_classification_inflation_fails(self):
        proposal = copy.deepcopy(self.proposal)
        proposal["target_scope"]["classifications"][3] = "source_verbatim"
        self.assertTrue(any("classification" in error for error in self.errors(proposal=proposal)))

    def test_numerical_boundary_erasure_fails(self):
        proposal = copy.deepcopy(self.proposal)
        proposal["target_scope"]["numerical_strengthening_state"] = "source_verbatim"
        self.assertTrue(any("numerical strengthening" in error for error in self.errors(proposal=proposal)))

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
        b2 = next(item for item in readback["families"] if item["result_family"] == M.FAMILY)
        b2["non_author_review"]["review_id"] = 1
        self.assertTrue(any("review drift" in error for error in self.errors(readback=readback)))

    def test_historical_replay_route_inflation_fails(self):
        replay = copy.deepcopy(self.replay)
        replay["route_state"]["route_proposed"] = True
        self.assertTrue(any("historical replay route state" in error for error in self.errors(replay=replay)))

    def test_blob_drift_fails(self):
        for key in ("proposal", "registry", "routes", "intake", "work_package", "replay", "readback"):
            with self.subTest(key=key):
                self.assertTrue(any("blob drift" in error for error in self.errors(local_blobs={key: "0" * 40})))

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
