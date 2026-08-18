from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_openai_ten_proofs_sphere_packing_route_proposal",
    ROOT / "ci/validate_openai_ten_proofs_sphere_packing_route_proposal.py",
)
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class SpherePackingRouteProposalTests(unittest.TestCase):
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

    def test_adjudication_insertion(self):
        p = copy.deepcopy(self.proposal); p["route_controls"]["adjudication"] = {"forged": True}
        self.assertTrue(self.errors(proposal=p))

    def test_cert_output_insertion(self):
        p = copy.deepcopy(self.proposal); p["route_controls"]["cert_output"] = {"forged": True}
        self.assertTrue(self.errors(proposal=p))

    def test_proof_promotion(self):
        p = copy.deepcopy(self.proposal); p["route_controls"]["mathematical_target_proved"] = True
        self.assertTrue(self.errors(proposal=p))

    def test_claim_promotion(self):
        p = copy.deepcopy(self.proposal); p["route_controls"]["may_promote_claim"] = True
        self.assertTrue(self.errors(proposal=p))

    def test_aggregate_route_inflation(self):
        p = copy.deepcopy(self.proposal); p["route_controls"]["aggregate_route"] = True
        self.assertTrue(self.errors(proposal=p))

    def test_target_substitution(self):
        p = copy.deepcopy(self.proposal); p["target_scope"]["lean_theorems"][0] = "Forged.theorem"
        self.assertTrue(self.errors(proposal=p))

    def test_target_reordering(self):
        p = copy.deepcopy(self.proposal); p["target_scope"]["lean_theorems"] = list(reversed(p["target_scope"]["lean_theorems"]))
        self.assertTrue(self.errors(proposal=p))

    def test_classification_erasure(self):
        p = copy.deepcopy(self.proposal); p["target_scope"]["classifications"][1] = "source_verbatim"
        self.assertTrue(self.errors(proposal=p))

    def test_qualification_erasure(self):
        p = copy.deepcopy(self.proposal); p["target_scope"]["mandatory_qualifications"] = p["target_scope"]["mandatory_qualifications"][:-1]
        self.assertTrue(self.errors(proposal=p))

    def test_nonvacuity_erasure(self):
        p = copy.deepcopy(self.proposal); p["target_scope"]["nonvacuity_evidence"] = []
        self.assertTrue(self.errors(proposal=p))

    def test_axiom_inflation(self):
        p = copy.deepcopy(self.proposal); p["target_scope"]["permitted_axioms"].append("sorryAx")
        self.assertTrue(self.errors(proposal=p))

    def test_source_root_drift(self):
        p = copy.deepcopy(self.proposal); p["authority"]["official_subject"]["commit"] = "0" * 40
        self.assertTrue(self.errors(proposal=p))

    def test_source_pdf_drift(self):
        p = copy.deepcopy(self.proposal); p["authority"]["source_pdf"]["sha256"] = "0" * 64
        self.assertTrue(self.errors(proposal=p))

    def test_composite_semantic_drift(self):
        p = copy.deepcopy(self.proposal); p["authority"]["forge_composite_semantic"]["record_blob"] = "0" * 40
        self.assertTrue(self.errors(proposal=p))

    def test_bridge_semantic_drift(self):
        p = copy.deepcopy(self.proposal); p["authority"]["forge_bridge_semantic"]["record_blob"] = "0" * 40
        self.assertTrue(self.errors(proposal=p))

    def test_solve_drift(self):
        p = copy.deepcopy(self.proposal); p["authority"]["solve_handoff"]["producer_packet_blob"] = "0" * 40
        self.assertTrue(self.errors(proposal=p))

    def test_work_package_drift(self):
        p = copy.deepcopy(self.proposal); p["authority"]["cert_work_package"]["record_blob"] = "0" * 40
        self.assertTrue(self.errors(proposal=p))

    def test_replay_evidence_drift(self):
        p = copy.deepcopy(self.proposal); p["authority"]["cert_replay_evidence"]["record_blob"] = "0" * 40
        self.assertTrue(self.errors(proposal=p))

    def test_bundle_drift(self):
        p = copy.deepcopy(self.proposal); p["authority"]["cert_replay_evidence"]["bundle_sha256"] = "0" * 64
        self.assertTrue(self.errors(proposal=p))

    def test_routes_blob_drift(self):
        blobs = copy.deepcopy(self.blobs); blobs["routes"] = "0" * 40
        self.assertTrue(self.errors(local_blobs=blobs))

    def test_replay_local_blob_drift(self):
        blobs = copy.deepcopy(self.blobs); blobs["replay"] = "0" * 40
        self.assertTrue(self.errors(local_blobs=blobs))

    def test_proposal_blob_drift(self):
        blobs = copy.deepcopy(self.blobs); blobs["proposal"] = "0" * 40
        self.assertTrue(self.errors(local_blobs=blobs))

    def test_registry_registration_count_inflation(self):
        r = copy.deepcopy(self.registry); r["state"]["registered_route_count_created_by_this_operation"] = 1
        self.assertTrue(self.errors(registry=r))

    def test_registry_another_family_insertion(self):
        r = copy.deepcopy(self.registry); r["scope"]["another_family_target_count"] = 1
        self.assertTrue(self.errors(registry=r))

    def test_registry_aggregate_inflation(self):
        r = copy.deepcopy(self.registry); r["scope"]["aggregate_route"] = True
        self.assertTrue(self.errors(registry=r))

    def test_precision_inflation(self):
        r = copy.deepcopy(self.registry); r["scope"]["source_authored_30_decimal_precision"] = True
        self.assertTrue(self.errors(registry=r))

    def test_normalization_erasure(self):
        r = copy.deepcopy(self.registry); r["scope"]["normalization_bridge_required"] = False
        self.assertTrue(self.errors(registry=r))

    def test_human_steward_gate_erasure(self):
        p = copy.deepcopy(self.proposal); p["activation"]["condition"] = "exact-head Cert checks only"
        self.assertTrue(self.errors(proposal=p))

    def test_claim_boundary_weakening(self):
        p = copy.deepcopy(self.proposal); p["claim_boundary"] = "The route is certified."
        self.assertTrue(self.errors(proposal=p))


if __name__ == "__main__":
    unittest.main()
