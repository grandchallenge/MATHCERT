from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_openai_ten_proofs_result_family_intakes",
    ROOT / "ci" / "validate_openai_ten_proofs_result_family_intakes.py",
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class OpenAITenProofsResultFamilyIntakeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = json.loads(MODULE.REGISTRY_PATH.read_text(encoding="utf-8"))
        self.intakes = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted(MODULE.INTAKE_DIR.glob("*.json"))}
        self.blobs = {p.stem: MODULE.git_blob_sha1(p) for p in sorted(MODULE.INTAKE_DIR.glob("*.json"))}

    def errors(self, *, registry=None, intakes=None, blobs=None):
        return MODULE.validation_errors(
            registry=copy.deepcopy(self.registry if registry is None else registry),
            intakes=copy.deepcopy(self.intakes if intakes is None else intakes),
            intake_blobs=copy.deepcopy(self.blobs if blobs is None else blobs),
        )

    def permanent(self):
        return copy.deepcopy(self.intakes)

    def mutate_projection(self, field, value):
        intakes = self.permanent()
        intakes["OTP-C-PERMANENT"]["target_scope"]["source_projection"][field] = value
        return intakes

    def test_current_intakes_pass(self): self.assertEqual(self.errors(), [])

    def test_missing_intake_rejected(self):
        x=self.permanent(); x.pop("OTP-C-PERMANENT"); self.assertTrue(self.errors(intakes=x))

    def test_unknown_intake_rejected(self):
        x=self.permanent(); x["OTP-ALL"]=copy.deepcopy(x["OTP-F-EHRHART"]); self.assertTrue(self.errors(intakes=x))

    def test_permanent_packet_digest_drift_rejected(self):
        x=self.permanent(); x["OTP-C-PERMANENT"]["authority"]["producer_packet"]["digest"]="0"*40; self.assertTrue(self.errors(intakes=x))

    def test_permanent_semantic_digest_drift_rejected(self):
        x=self.permanent(); x["OTP-C-PERMANENT"]["authority"]["semantic_record"]["digest"]="0"*40; self.assertTrue(self.errors(intakes=x))

    def test_permanent_witness_drift_rejected(self):
        x=self.permanent(); x["OTP-C-PERMANENT"]["authority"]["nonvacuity_witness"]["digest"]="0"*40; self.assertTrue(self.errors(intakes=x))

    def test_protected_solve_merge_drift_rejected(self):
        x=self.permanent(); x["OTP-C-PERMANENT"]["authority"]["solve_handoff_merge"]="0"*40; self.assertTrue(self.errors(intakes=x))

    def test_route_registration_rejected(self):
        x=self.permanent(); x["OTP-C-PERMANENT"]["certification_state"]["certification_route_registry_entry"]={"route_id":"MC-ROUTE-OTP-C-PERMANENT-FORMULA"}; self.assertTrue(self.errors(intakes=x))

    def test_cert_output_rejected(self):
        x=self.permanent(); x["OTP-C-PERMANENT"]["certification_state"]["cert_output"]={"state":"qualified"}; self.assertTrue(self.errors(intakes=x))

    def test_adjudication_rejected(self):
        x=self.permanent(); x["OTP-C-PERMANENT"]["certification_state"]["may_adjudicate"]=True; self.assertTrue(self.errors(intakes=x))

    def test_proof_promotion_rejected(self):
        x=self.permanent(); x["OTP-C-PERMANENT"]["certification_state"]["mathematical_target_proved"]=True; self.assertTrue(self.errors(intakes=x))

    def test_circuit_insertion_rejected(self):
        x=self.permanent(); x["OTP-C-PERMANENT"]["route_controls"]["may_include_circuit_target"]=True; self.assertTrue(self.errors(intakes=x))

    def test_gate_insertion_rejected(self):
        x=self.permanent(); x["OTP-C-PERMANENT"]["route_controls"]["may_include_gate_bounds"]=True; self.assertTrue(self.errors(intakes=x))

    def test_total_size_insertion_rejected(self):
        x=self.permanent(); x["OTP-C-PERMANENT"]["route_controls"]["may_include_total_size_consequences"]=True; self.assertTrue(self.errors(intakes=x))

    def test_target_inflation_rejected(self):
        x=self.permanent(); x["OTP-C-PERMANENT"]["target_scope"]["lean_theorems"].append("Permanent.fake"); self.assertTrue(self.errors(intakes=x))

    def test_threshold_drift_rejected(self): self.assertTrue(self.errors(intakes=self.mutate_projection("dimension_threshold",31)))
    def test_log_base_drift_rejected(self): self.assertTrue(self.errors(intakes=self.mutate_projection("log_base",10)))
    def test_128_drift_rejected(self): self.assertTrue(self.errors(intakes=self.mutate_projection("division_free_variable_leaf_constant",129)))
    def test_256_drift_rejected(self): self.assertTrue(self.errors(intakes=self.mutate_projection("division_free_source_gate_constant",255)))
    def test_192_drift_rejected(self): self.assertTrue(self.errors(intakes=self.mutate_projection("rational_variable_leaf_constant",193)))
    def test_384_drift_rejected(self): self.assertTrue(self.errors(intakes=self.mutate_projection("rational_source_gate_constant",383)))
    def test_circuit_count_inflation_rejected(self): self.assertTrue(self.errors(intakes=self.mutate_projection("circuit_target_count",1)))
    def test_gate_authority_inflation_rejected(self): self.assertTrue(self.errors(intakes=self.mutate_projection("gate_bounds_in_intake",True)))
    def test_total_authority_inflation_rejected(self): self.assertTrue(self.errors(intakes=self.mutate_projection("total_leaves_vertices_in_intake",True)))
    def test_pdf_equivalence_inflation_rejected(self): self.assertTrue(self.errors(intakes=self.mutate_projection("historical_pdf_byte_equivalence",True)))

    def test_registry_blob_drift_rejected(self):
        r=copy.deepcopy(self.registry); r["intakes"][3]["digest"]="0"*40; self.assertTrue(self.errors(registry=r))

    def test_blocked_lane_drift_rejected(self):
        r=copy.deepcopy(self.registry); r["blocked_repair_lanes"]=["OTP-C-PERMANENT"]; self.assertTrue(self.errors(registry=r))

    def test_unaccepted_successor_removal_rejected(self):
        r=copy.deepcopy(self.registry); r["permanent_unaccepted_successors"].pop(); self.assertTrue(self.errors(registry=r))

    def test_all_lean_route_inflation_rejected(self):
        r=copy.deepcopy(self.registry); r["aggregate_integration"]["creates_cert_route"]=True; self.assertTrue(self.errors(registry=r))

    def test_cert_state_inflation_rejected(self):
        r=copy.deepcopy(self.registry); r["cert_state"]["registered_route_count"]=1; self.assertTrue(self.errors(registry=r))

    def test_global_registry_modification_rejected(self):
        r=copy.deepcopy(self.registry); r["route_controls"]["global_certification_route_registry_modified"]=True; self.assertTrue(self.errors(registry=r))

    def test_aggregate_intake_rejected(self):
        r=copy.deepcopy(self.registry); r["route_controls"]["aggregate_intake"]={"intake_id":"ALL"}; self.assertTrue(self.errors(registry=r))

    def test_omitted_conclusions_in_registry_rejected(self):
        r=copy.deepcopy(self.registry); r["route_controls"]["may_include_permanent_circuit_or_omitted_formula_conclusions"]=True; self.assertTrue(self.errors(registry=r))


if __name__ == "__main__":
    unittest.main()
