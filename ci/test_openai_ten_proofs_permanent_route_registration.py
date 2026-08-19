from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_openai_ten_proofs_permanent_route_registration",
    ROOT / "ci/validate_openai_ten_proofs_permanent_route_registration.py",
)
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)

A_ROUTE_ID = "MC-ROUTE-OTP-A-SPHERE-PACKING"
A_PROVIDER_BASE_COMMIT = "4b194b9632a9aa57fee21c3c054498d6b4a8ed57"
A_REGISTRY_BLOB = "b9bb0dc9e18856f50a88162df37c20c034327439"


class PermanentRouteRegistrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.receipt = json.loads(M.RECEIPT.read_text(encoding="utf-8"))
        self.routes = json.loads(M.ROUTES.read_text(encoding="utf-8"))
        self.blobs = {
            "routes": M.git_blob_sha1(M.ROUTES),
            "proposal": M.git_blob_sha1(M.PROPOSAL),
            "proposal_registry": M.git_blob_sha1(M.PROPOSAL_REGISTRY),
        }
        self.a_route = copy.deepcopy(
            next(r for r in self.routes["routes"] if r.get("route_id") == A_ROUTE_ID)
        )
        self.historical_provider_base = M.snapshot_routes()["provider_base_commit"]

    def permanent_view(self, routes, local_blobs):
        """Project only the exact independently governed A registration successor.

        Permanent's protected registration semantics stay frozen. The test fixture may
        ignore the later A provider-base advance only when the live registry blob,
        provider base, and A route all match the exact governed A registration candidate.
        Any unknown provider-base or A-route drift remains visible to the historical
        Permanent validator and must fail closed.
        """
        supplied = copy.deepcopy(routes)
        blobs = copy.deepcopy(local_blobs)
        a_route = next(
            (r for r in supplied.get("routes", []) if r.get("route_id") == A_ROUTE_ID),
            None,
        )
        if (
            self.blobs["routes"] == A_REGISTRY_BLOB
            and blobs.get("routes") in {A_REGISTRY_BLOB, "0" * 40}
            and supplied.get("provider_base_commit") == A_PROVIDER_BASE_COMMIT
            and a_route == self.a_route
        ):
            supplied["provider_base_commit"] = self.historical_provider_base
        return supplied, blobs

    def errors(self, **kwargs):
        routes = copy.deepcopy(kwargs.get("routes", self.routes))
        blobs = copy.deepcopy(kwargs.get("local_blobs", self.blobs))
        routes, blobs = self.permanent_view(routes, blobs)
        return M.validation_errors(
            receipt=copy.deepcopy(kwargs.get("receipt", self.receipt)),
            routes=routes,
            local_blobs=blobs,
        )

    def route(self, routes):
        return next(r for r in routes["routes"] if r.get("route_id") == M.ROUTE_ID)

    def test_current_passes(self):
        self.assertEqual(self.errors(), [])

    def test_exact_a_provider_base_successor_is_permitted(self):
        self.assertEqual(self.routes["provider_base_commit"], A_PROVIDER_BASE_COMMIT)
        self.assertEqual(self.blobs["routes"], A_REGISTRY_BLOB)
        self.assertEqual(self.errors(), [])

    def test_unknown_provider_base_successor_is_rejected(self):
        routes = copy.deepcopy(self.routes)
        routes["provider_base_commit"] = "0" * 40
        self.assertTrue(self.errors(routes=routes))

    def test_a_route_drift_disables_successor_projection(self):
        routes = copy.deepcopy(self.routes)
        a_route = next(r for r in routes["routes"] if r.get("route_id") == A_ROUTE_ID)
        a_route["intake_status"] = "adjudicated"
        self.assertTrue(self.errors(routes=routes))

    def test_unrelated_registry_blob_evolution_is_permitted(self):
        blobs = copy.deepcopy(self.blobs)
        blobs["routes"] = "0" * 40
        self.assertEqual(self.errors(local_blobs=blobs), [])

    def test_unrelated_route_evolution_is_permitted(self):
        routes = copy.deepcopy(self.routes)
        compactness = next(r for r in routes["routes"] if r.get("campaign_id") == "OTP-J1-COMPACTNESS")
        compactness["reopening_conditions"].append("independent later evolution")
        self.assertEqual(self.errors(routes=routes), [])

    def test_missing_route(self):
        routes = copy.deepcopy(self.routes)
        routes["routes"] = [r for r in routes["routes"] if r.get("route_id") != M.ROUTE_ID]
        self.assertTrue(self.errors(routes=routes))

    def test_duplicate_route(self):
        routes = copy.deepcopy(self.routes)
        routes["routes"].append(copy.deepcopy(self.route(routes)))
        self.assertTrue(self.errors(routes=routes))

    def test_aggregate_route(self):
        routes = copy.deepcopy(self.routes)
        routes["routes"].append({"route_id": "MC-ROUTE-OPENAI-TEN-PROOFS-001"})
        self.assertTrue(self.errors(routes=routes))

    def test_target_inflation(self):
        routes = copy.deepcopy(self.routes)
        self.route(routes)["target_claim_ids"].append("PermanentRollout.permanent_circuit_loglog_lower_bound")
        self.assertTrue(self.errors(routes=routes))

    def test_gate_bound_inflation(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["registration"]["source_projection"]["gate_bounds_in_route"] = True
        self.assertTrue(self.errors(receipt=receipt))

    def test_total_size_inflation(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["registration"]["source_projection"]["total_leaves_vertices_in_route"] = True
        self.assertTrue(self.errors(receipt=receipt))

    def test_pdf_equivalence_inflation(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["registration"]["source_projection"]["historical_pdf_byte_equivalence"] = True
        self.assertTrue(self.errors(receipt=receipt))

    def test_cert_output_substitution(self):
        routes = copy.deepcopy(self.routes)
        self.route(routes)["cert_output"] = {"forged": True}
        self.assertTrue(self.errors(routes=routes))

    def test_permanent_status_drift(self):
        routes = copy.deepcopy(self.routes)
        self.route(routes)["intake_status"] = "submitted"
        self.route(routes)["cert_output"] = None
        self.assertTrue(self.errors(routes=routes))

    def test_adjudication_authority_inflation(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["route_controls"]["may_adjudicate"] = True
        self.assertTrue(self.errors(receipt=receipt))

    def test_proof_promotion(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["route_controls"]["may_mark_target_proved"] = True
        self.assertTrue(self.errors(receipt=receipt))

    def test_proposal_merge_drift(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["authority"]["proposal_merge"] = "0" * 40
        self.assertTrue(self.errors(receipt=receipt))

    def test_proposal_head_drift(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["authority"]["proposal_reviewed_head"] = "0" * 40
        self.assertTrue(self.errors(receipt=receipt))

    def test_proposal_blob_drift(self):
        blobs = copy.deepcopy(self.blobs)
        blobs["proposal"] = "0" * 40
        self.assertTrue(self.errors(local_blobs=blobs))

    def test_proposal_registry_blob_drift(self):
        blobs = copy.deepcopy(self.blobs)
        blobs["proposal_registry"] = "0" * 40
        self.assertTrue(self.errors(local_blobs=blobs))

    def test_source_manifest_substitution(self):
        routes = copy.deepcopy(self.routes)
        self.route(routes)["source_manifest"]["digest"] = "0" * 40
        self.assertTrue(self.errors(routes=routes))

    def test_solve_packet_substitution(self):
        routes = copy.deepcopy(self.routes)
        self.route(routes)["intake_packet"]["digest"] = "0" * 40
        self.assertTrue(self.errors(routes=routes))

    def test_status_inflation(self):
        routes = copy.deepcopy(self.routes)
        self.route(routes)["intake_status"] = "adjudicated"
        self.assertTrue(self.errors(routes=routes))

    def test_blocker_removal(self):
        routes = copy.deepcopy(self.routes)
        self.route(routes)["blockers"] = ["all clear"]
        self.assertTrue(self.errors(routes=routes))

    def test_claim_boundary_weakening(self):
        routes = copy.deepcopy(self.routes)
        self.route(routes)["claim_boundary"] = "Permanent is certified."
        self.assertTrue(self.errors(routes=routes))

    def test_state_inflation(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["state"]["adjudication_count"] = 1
        self.assertTrue(self.errors(receipt=receipt))

    def test_aggregate_prohibition_removal(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["route_controls"]["aggregate_route_prohibited"] = False
        self.assertTrue(self.errors(receipt=receipt))


if __name__ == "__main__":
    unittest.main()
