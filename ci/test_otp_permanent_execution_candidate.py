from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_otp_permanent_execution_candidate",
    ROOT / "ci/validate_otp_permanent_execution_candidate.py",
)
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class PermanentExecutionCandidateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.candidate = json.loads(M.CANDIDATE.read_text(encoding="utf-8"))
        self.manifest = json.loads(M.MANIFEST.read_text(encoding="utf-8"))
        self.routes = json.loads(M.ROUTES.read_text(encoding="utf-8"))

    def errors(self, *, candidate=None, manifest=None, routes=None, contract_blob=None,
               design_registry_blob=None, routes_blob=None):
        return M.validation_errors(
            candidate=copy.deepcopy(self.candidate if candidate is None else candidate),
            manifest=copy.deepcopy(self.manifest if manifest is None else manifest),
            routes=copy.deepcopy(self.routes if routes is None else routes),
            contract_blob=M.EXPECTED_CONTRACT_BLOB if contract_blob is None else contract_blob,
            design_registry_blob=M.EXPECTED_DESIGN_REGISTRY_BLOB if design_registry_blob is None else design_registry_blob,
            routes_blob=M.EXPECTED_ROUTES_BLOB if routes_blob is None else routes_blob,
        )

    def test_current_passes(self):
        self.assertEqual(self.errors(), [])

    def test_target_inflation(self):
        c = copy.deepcopy(self.candidate)
        c["encoded_targets"].append("PermanentRollout.permanent_circuit_loglog_lower_bound")
        self.assertTrue(self.errors(candidate=c))

    def test_circuit_scope_inflation(self):
        c = copy.deepcopy(self.candidate)
        c["preserved_limitations"]["circuit_targets_in_scope"] = True
        self.assertTrue(self.errors(candidate=c))

    def test_gate_scope_inflation(self):
        c = copy.deepcopy(self.candidate)
        c["preserved_limitations"]["gate_bounds_in_scope"] = True
        self.assertTrue(self.errors(candidate=c))

    def test_total_size_inflation(self):
        c = copy.deepcopy(self.candidate)
        c["preserved_limitations"]["total_size_consequences_in_scope"] = True
        self.assertTrue(self.errors(candidate=c))

    def test_pdf_equivalence_inflation(self):
        c = copy.deepcopy(self.candidate)
        c["preserved_limitations"]["historical_pdf_byte_equivalence"] = "established"
        self.assertTrue(self.errors(candidate=c))

    def test_route_state_promotion(self):
        c = copy.deepcopy(self.candidate)
        c["state"]["route_state"] = "qualified"
        self.assertTrue(self.errors(candidate=c))

    def test_adjudication_insertion(self):
        c = copy.deepcopy(self.candidate)
        c["state"]["may_adjudicate"] = True
        c["state"]["adjudication"] = {"disposition": "adjudication_clear_encoded_targets_only"}
        self.assertTrue(self.errors(candidate=c))

    def test_output_insertion(self):
        c = copy.deepcopy(self.candidate)
        c["state"]["cert_output"] = {"forged": True}
        self.assertTrue(self.errors(candidate=c))

    def test_proof_promotion(self):
        c = copy.deepcopy(self.candidate)
        c["state"]["mathematical_target_proved"] = True
        self.assertTrue(self.errors(candidate=c))

    def test_aggregate_insertion(self):
        c = copy.deepcopy(self.candidate)
        c["state"]["aggregate_adjudication"] = True
        self.assertTrue(self.errors(candidate=c))

    def test_contract_authority_substitution(self):
        self.assertTrue(self.errors(contract_blob="0" * 40))

    def test_design_registry_authority_substitution(self):
        self.assertTrue(self.errors(design_registry_blob="0" * 40))

    def test_route_registry_authority_substitution(self):
        self.assertTrue(self.errors(routes_blob="0" * 40))

    def test_generation_head_drift(self):
        c = copy.deepcopy(self.candidate)
        c["generation"]["generation_head"] = "0" * 40
        self.assertTrue(self.errors(candidate=c))

    def test_artifact_digest_drift(self):
        c = copy.deepcopy(self.candidate)
        c["generation"]["artifact"]["sha256"] = "0" * 64
        self.assertTrue(self.errors(candidate=c))

    def test_artifact_id_drift(self):
        c = copy.deepcopy(self.candidate)
        c["generation"]["artifact"]["id"] = 1
        self.assertTrue(self.errors(candidate=c))

    def test_control_plan_routine_progression_removed(self):
        c = copy.deepcopy(self.candidate)
        c["control_plan"]["routine_stage_progression_without_human_steward_intervention"] = False
        self.assertTrue(self.errors(candidate=c))

    def test_control_plan_steward_boundary_removed(self):
        c = copy.deepcopy(self.candidate)
        c["control_plan"]["human_steward_intervention_required_only_for_control_plan_change"] = False
        self.assertTrue(self.errors(candidate=c))

    def test_control_plan_change_requested(self):
        c = copy.deepcopy(self.candidate)
        c["control_plan"]["control_plan_change_requested"] = True
        self.assertTrue(self.errors(candidate=c))

    def test_manifest_file_hash_mutation(self):
        m = copy.deepcopy(self.manifest)
        m["files"][0]["sha256"] = "0" * 64
        self.assertTrue(self.errors(manifest=m))

    def test_manifest_file_membership_mutation(self):
        m = copy.deepcopy(self.manifest)
        m["files"].pop()
        self.assertTrue(self.errors(manifest=m))

    def test_live_route_target_drift(self):
        routes = copy.deepcopy(self.routes)
        route = next(x for x in routes["routes"] if x.get("route_id") == M.ROUTE_ID)
        route["target_claim_ids"] = route["target_claim_ids"][:1]
        self.assertTrue(self.errors(routes=routes))

    def test_live_route_output_insertion(self):
        routes = copy.deepcopy(self.routes)
        route = next(x for x in routes["routes"] if x.get("route_id") == M.ROUTE_ID)
        route["cert_output"] = {"forged": True}
        self.assertTrue(self.errors(routes=routes))


if __name__ == "__main__":
    unittest.main()
