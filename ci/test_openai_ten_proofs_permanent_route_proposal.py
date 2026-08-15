from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_openai_ten_proofs_permanent_route_proposal",
    ROOT / "ci/validate_openai_ten_proofs_permanent_route_proposal.py",
)
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class PermanentRouteProposalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.proposal = json.loads(M.PROPOSAL.read_text(encoding="utf-8"))
        self.registry = json.loads(M.REGISTRY.read_text(encoding="utf-8"))
        self.routes = json.loads(M.ROUTES.read_text(encoding="utf-8"))
        self.blobs = {
            "proposal": M.git_blob_sha1(M.PROPOSAL),
            "routes": M.git_blob_sha1(M.ROUTES),
            "intake": M.git_blob_sha1(M.INTAKE),
            "work_package": M.git_blob_sha1(M.WORK_PACKAGE),
            "replay": M.git_blob_sha1(M.REPLAY),
            "manifest": M.git_blob_sha1(M.MANIFEST),
        }

    def errors(self, **kwargs):
        return M.validation_errors(
            proposal=copy.deepcopy(kwargs.get("proposal", self.proposal)),
            registry=copy.deepcopy(kwargs.get("registry", self.registry)),
            routes=copy.deepcopy(kwargs.get("routes", self.routes)),
            local_blobs=copy.deepcopy(kwargs.get("local_blobs", self.blobs)),
        )

    def test_current_passes(self):
        self.assertEqual(self.errors(), [])

    def test_route_state_inflation(self):
        p = copy.deepcopy(self.proposal); p["proposal_state"] = "registered"
        self.assertTrue(self.errors(proposal=p))

    def test_registered_route_insertion(self):
        routes = copy.deepcopy(self.routes); routes["routes"].append({"route_id": M.ROUTE_ID})
        self.assertTrue(self.errors(routes=routes))

    def test_may_register_inflation(self):
        p = copy.deepcopy(self.proposal); p["route_controls"]["may_register_route"] = True
        self.assertTrue(self.errors(proposal=p))

    def test_adjudication_inflation(self):
        p = copy.deepcopy(self.proposal); p["route_controls"]["may_adjudicate"] = True
        self.assertTrue(self.errors(proposal=p))

    def test_cert_output_insertion(self):
        p = copy.deepcopy(self.proposal); p["route_controls"]["cert_output"] = {"forged": True}
        self.assertTrue(self.errors(proposal=p))

    def test_proof_promotion(self):
        p = copy.deepcopy(self.proposal); p["route_controls"]["mathematical_target_proved"] = True
        self.assertTrue(self.errors(proposal=p))

    def test_aggregate_route_inflation(self):
        p = copy.deepcopy(self.proposal); p["route_controls"]["aggregate_route"] = True
        self.assertTrue(self.errors(proposal=p))

    def test_circuit_target_insertion(self):
        p = copy.deepcopy(self.proposal); p["target_scope"]["source_projection"]["circuit_target_count"] = 1
        self.assertTrue(self.errors(proposal=p))

    def test_gate_bound_insertion(self):
        p = copy.deepcopy(self.proposal); p["target_scope"]["source_projection"]["gate_bounds_in_route"] = True
        self.assertTrue(self.errors(proposal=p))

    def test_total_size_insertion(self):
        p = copy.deepcopy(self.proposal); p["target_scope"]["source_projection"]["total_leaves_vertices_in_route"] = True
        self.assertTrue(self.errors(proposal=p))

    def test_pdf_equivalence_inflation(self):
        p = copy.deepcopy(self.proposal); p["target_scope"]["source_projection"]["historical_pdf_byte_equivalence"] = True
        self.assertTrue(self.errors(proposal=p))

    def test_threshold_drift(self):
        p = copy.deepcopy(self.proposal); p["target_scope"]["source_projection"]["dimension_threshold"] = 16
        self.assertTrue(self.errors(proposal=p))

    def test_log_base_drift(self):
        p = copy.deepcopy(self.proposal); p["target_scope"]["source_projection"]["log_base"] = 10
        self.assertTrue(self.errors(proposal=p))

    def test_constant_drift(self):
        p = copy.deepcopy(self.proposal); p["target_scope"]["source_projection"]["division_free_variable_leaf_constant"] = 127
        self.assertTrue(self.errors(proposal=p))

    def test_theorem_target_drift(self):
        p = copy.deepcopy(self.proposal); p["target_scope"]["lean_theorems"] = p["target_scope"]["lean_theorems"][:1]
        self.assertTrue(self.errors(proposal=p))

    def test_nonvacuity_drift(self):
        p = copy.deepcopy(self.proposal); p["target_scope"]["nonvacuity_witnesses"][0] = "forged"
        self.assertTrue(self.errors(proposal=p))

    def test_semantic_authority_drift(self):
        p = copy.deepcopy(self.proposal); p["authority"]["forge_semantic"]["semantic_record_blob"] = "0" * 40
        self.assertTrue(self.errors(proposal=p))

    def test_solve_authority_drift(self):
        p = copy.deepcopy(self.proposal); p["authority"]["solve_handoff"]["producer_packet_blob"] = "0" * 40
        self.assertTrue(self.errors(proposal=p))

    def test_replay_authority_drift(self):
        p = copy.deepcopy(self.proposal); p["authority"]["cert_replay_evidence"]["record_blob"] = "0" * 40
        self.assertTrue(self.errors(proposal=p))

    def test_manifest_drift(self):
        blobs = copy.deepcopy(self.blobs); blobs["manifest"] = "0" * 40
        self.assertTrue(self.errors(local_blobs=blobs))

    def test_registered_registry_drift(self):
        blobs = copy.deepcopy(self.blobs); blobs["routes"] = "0" * 40
        self.assertTrue(self.errors(local_blobs=blobs))

    def test_proposal_blob_drift(self):
        blobs = copy.deepcopy(self.blobs); blobs["proposal"] = "0" * 40
        self.assertTrue(self.errors(local_blobs=blobs))

    def test_registry_count_inflation(self):
        r = copy.deepcopy(self.registry); r["state"]["registered_route_count_created_by_this_operation"] = 1
        self.assertTrue(self.errors(registry=r))

    def test_registry_proposal_digest_drift(self):
        r = copy.deepcopy(self.registry); r["proposal"]["digest"] = "0" * 40
        self.assertTrue(self.errors(registry=r))

    def test_claim_boundary_weakening(self):
        p = copy.deepcopy(self.proposal); p["claim_boundary"] = "The route is certified."
        self.assertTrue(self.errors(proposal=p))


if __name__ == "__main__":
    unittest.main()
