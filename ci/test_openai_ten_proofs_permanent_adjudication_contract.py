from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_openai_ten_proofs_permanent_adjudication_contract",
    ROOT / "ci/validate_openai_ten_proofs_permanent_adjudication_contract.py",
)
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class PermanentAdjudicationContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = json.loads(M.CONTRACT.read_text(encoding="utf-8"))
        self.registry = json.loads(M.REGISTRY.read_text(encoding="utf-8"))
        self.routes = json.loads(M.ROUTES.read_text(encoding="utf-8"))

    def errors(self, *, contract=None, registry=None, routes=None, routes_blob=None):
        return M.validation_errors(
            contract=copy.deepcopy(self.contract if contract is None else contract),
            registry=copy.deepcopy(self.registry if registry is None else registry),
            routes=copy.deepcopy(self.routes if routes is None else routes),
            routes_blob=M.EXPECTED_ROUTES_BLOB if routes_blob is None else routes_blob,
        )

    def test_current_passes(self):
        self.assertEqual(self.errors(), [])

    def test_target_inflation(self):
        c = copy.deepcopy(self.contract)
        c["route_scope"]["target_claim_ids"].append("PermanentRollout.permanent_circuit_loglog_lower_bound")
        self.assertTrue(self.errors(contract=c))

    def test_circuit_scope_inflation(self):
        c = copy.deepcopy(self.contract)
        c["route_scope"]["source_projection"]["circuit_target_count"] = 1
        self.assertTrue(self.errors(contract=c))

    def test_gate_bound_inflation(self):
        c = copy.deepcopy(self.contract)
        c["preserved_limitations"]["gate_bounds_in_scope"] = True
        self.assertTrue(self.errors(contract=c))

    def test_total_size_inflation(self):
        c = copy.deepcopy(self.contract)
        c["preserved_limitations"]["total_size_consequences_in_scope"] = True
        self.assertTrue(self.errors(contract=c))

    def test_pdf_equivalence_inflation(self):
        c = copy.deepcopy(self.contract)
        c["preserved_limitations"]["historical_pdf_byte_equivalence"] = "established"
        self.assertTrue(self.errors(contract=c))

    def test_premature_adjudication(self):
        c = copy.deepcopy(self.contract)
        c["state"]["may_adjudicate"] = True
        c["state"]["adjudication"] = {"disposition": "adjudication_clear_encoded_targets_only"}
        self.assertTrue(self.errors(contract=c))

    def test_output_insertion(self):
        c = copy.deepcopy(self.contract)
        c["state"]["cert_output"] = {"forged": True}
        self.assertTrue(self.errors(contract=c))

    def test_proof_promotion(self):
        c = copy.deepcopy(self.contract)
        c["state"]["mathematical_target_proved"] = True
        self.assertTrue(self.errors(contract=c))

    def test_aggregate_insertion(self):
        r = copy.deepcopy(self.registry)
        r["state"]["aggregate_contract_count"] = 1
        self.assertTrue(self.errors(registry=r))

    def test_authority_substitution(self):
        c = copy.deepcopy(self.contract)
        c["authority"]["registration_merge"] = "0" * 40
        self.assertTrue(self.errors(contract=c))

    def test_source_projection_drift(self):
        c = copy.deepcopy(self.contract)
        c["route_scope"]["source_projection"]["dimension_threshold"] = 16
        self.assertTrue(self.errors(contract=c))

    def test_disposition_inflation(self):
        c = copy.deepcopy(self.contract)
        c["decision_contract"]["admissible_dispositions"].append("certified_source_theorem")
        self.assertTrue(self.errors(contract=c))

    def test_route_state_promotion(self):
        c = copy.deepcopy(self.contract)
        c["route_scope"]["registered_route_state"] = "qualified"
        self.assertTrue(self.errors(contract=c))

    def test_routine_progression_gate_removed(self):
        c = copy.deepcopy(self.contract)
        c["execution_gate"]["routine_stage_progression_without_human_steward_intervention"] = False
        self.assertTrue(self.errors(contract=c))

    def test_control_plan_change_human_steward_gate_removed(self):
        c = copy.deepcopy(self.contract)
        c["execution_gate"]["human_steward_intervention_required_for_control_plan_change"] = False
        self.assertTrue(self.errors(contract=c))

    def test_old_human_steward_stage_reintroduced(self):
        r = copy.deepcopy(self.registry)
        r["successor_sequence"][2] = "human_steward_adjudication_authorization"
        self.assertTrue(self.errors(registry=r))

    def test_control_plan_rule_removed_from_evidence(self):
        c = copy.deepcopy(self.contract)
        c["decision_contract"]["required_evidence"][-1] = "Proceed without checking the approved control plan."
        self.assertTrue(self.errors(contract=c))

    def test_live_route_output_insertion(self):
        routes = copy.deepcopy(self.routes)
        route = next(x for x in routes["routes"] if x.get("route_id") == M.ROUTE_ID)
        route["cert_output"] = {"forged": True}
        self.assertTrue(self.errors(routes=routes))

    def test_live_route_registry_drift(self):
        self.assertTrue(self.errors(routes_blob="0" * 40))

    def test_duplicate_contract_registry_membership(self):
        r = copy.deepcopy(self.registry)
        r["contracts"].append(copy.deepcopy(r["contracts"][0]))
        r["contract_count"] = 2
        self.assertTrue(self.errors(registry=r))


if __name__ == "__main__":
    unittest.main()
