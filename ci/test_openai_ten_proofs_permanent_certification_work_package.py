from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_openai_ten_proofs_permanent_certification_work_package",
    ROOT / "ci" / "validate_openai_ten_proofs_permanent_certification_work_package.py",
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PermanentCertificationWorkPackageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.record = json.loads(MODULE.RECORD_PATH.read_text(encoding="utf-8"))
        self.registry = json.loads(MODULE.REGISTRY_PATH.read_text(encoding="utf-8"))

    def errors(self, *, record=None, registry=None, record_blob=None, historical_blob=None):
        return MODULE.validation_errors(
            record=copy.deepcopy(self.record if record is None else record),
            registry=copy.deepcopy(self.registry if registry is None else registry),
            record_blob_override=MODULE.RECORD_BLOB if record_blob is None else record_blob,
            historical_blob_override=MODULE.HISTORICAL_REGISTRY_BLOB if historical_blob is None else historical_blob,
        )

    def mutated_record(self): return copy.deepcopy(self.record)
    def mutated_registry(self): return copy.deepcopy(self.registry)

    def mutate_projection(self, field, value):
        r = self.mutated_record()
        r["target_scope"]["source_projection"][field] = value
        return r

    def test_current_package_passes(self): self.assertEqual(self.errors(), [])

    def test_intake_merge_drift_rejected(self):
        r=self.mutated_record(); r["authority"]["cert_intake_merge"]="0"*40; self.assertTrue(self.errors(record=r))

    def test_intake_record_drift_rejected(self):
        r=self.mutated_record(); r["authority"]["intake_record"]["digest"]="0"*40; self.assertTrue(self.errors(record=r))

    def test_solve_packet_drift_rejected(self):
        r=self.mutated_record(); r["authority"]["producer_packet"]["digest"]="0"*40; self.assertTrue(self.errors(record=r))

    def test_semantic_record_drift_rejected(self):
        r=self.mutated_record(); r["authority"]["semantic_record"]["digest"]="0"*40; self.assertTrue(self.errors(record=r))

    def test_nonvacuity_witness_drift_rejected(self):
        r=self.mutated_record(); r["authority"]["nonvacuity_witness"]["digest"]="0"*40; self.assertTrue(self.errors(record=r))

    def test_comparator_pin_drift_rejected(self):
        r=self.mutated_record(); r["toolchain"]["comparator_commit"]="0"*40; self.assertTrue(self.errors(record=r))

    def test_lean_version_drift_rejected(self):
        r=self.mutated_record(); r["toolchain"]["lean"]="leanprover/lean4:v4.31.0"; self.assertTrue(self.errors(record=r))

    def test_target_removal_rejected(self):
        r=self.mutated_record(); r["target_scope"]["lean_theorems"].pop(); self.assertTrue(self.errors(record=r))

    def test_circuit_target_insertion_rejected(self):
        r=self.mutated_record(); r["target_scope"]["lean_theorems"].append("PermanentRollout.permanent_circuit_loglog_lower_bound"); self.assertTrue(self.errors(record=r))

    def test_nonvacuity_removal_rejected(self):
        r=self.mutated_record(); r["target_scope"]["nonvacuity_witnesses"].pop(); self.assertTrue(self.errors(record=r))

    def test_threshold_drift_rejected(self): self.assertTrue(self.errors(record=self.mutate_projection("dimension_threshold",31)))
    def test_log_base_drift_rejected(self): self.assertTrue(self.errors(record=self.mutate_projection("log_base",10)))
    def test_128_drift_rejected(self): self.assertTrue(self.errors(record=self.mutate_projection("division_free_variable_leaf_constant",129)))
    def test_256_drift_rejected(self): self.assertTrue(self.errors(record=self.mutate_projection("division_free_source_gate_constant",255)))
    def test_192_drift_rejected(self): self.assertTrue(self.errors(record=self.mutate_projection("rational_variable_leaf_constant",193)))
    def test_384_drift_rejected(self): self.assertTrue(self.errors(record=self.mutate_projection("rational_source_gate_constant",383)))
    def test_gate_authority_inflation_rejected(self): self.assertTrue(self.errors(record=self.mutate_projection("gate_bounds_in_work_package",True)))
    def test_total_size_authority_inflation_rejected(self): self.assertTrue(self.errors(record=self.mutate_projection("total_leaves_vertices_in_work_package",True)))
    def test_pdf_equivalence_inflation_rejected(self): self.assertTrue(self.errors(record=self.mutate_projection("historical_pdf_byte_equivalence",True)))

    def test_route_registration_rejected(self):
        r=self.mutated_record(); r["route_state"]["certification_route_registry_entry"]={"route_id":"MC-ROUTE-OTP-C-PERMANENT-FORMULA"}; self.assertTrue(self.errors(record=r))

    def test_route_proposal_rejected(self):
        r=self.mutated_record(); r["route_state"]["proposed_route_record"]={"state":"proposed_only"}; self.assertTrue(self.errors(record=r))

    def test_adjudication_rejected(self):
        r=self.mutated_record(); r["route_state"]["may_adjudicate"]=True; self.assertTrue(self.errors(record=r))

    def test_cert_output_rejected(self):
        r=self.mutated_record(); r["route_state"]["cert_output"]={"state":"qualified"}; self.assertTrue(self.errors(record=r))

    def test_proof_promotion_rejected(self):
        r=self.mutated_record(); r["route_state"]["mathematical_target_proved"]=True; self.assertTrue(self.errors(record=r))

    def test_aggregate_work_package_rejected(self):
        r=self.mutated_record(); r["route_controls"]["may_create_aggregate_work_package"]=True; self.assertTrue(self.errors(record=r))

    def test_aggregate_route_rejected(self):
        r=self.mutated_record(); r["route_controls"]["may_create_aggregate_route"]=True; self.assertTrue(self.errors(record=r))

    def test_successor_digest_mismatch_rejected(self):
        x=self.mutated_registry(); x["work_package"]["digest"]="0"*40; self.assertTrue(self.errors(registry=x))

    def test_successor_path_drift_rejected(self):
        x=self.mutated_registry(); x["work_package"]["path"]="governance/result_family_work_packages/OTP-C-PERMANENT-CERT-WP01.json"; self.assertTrue(self.errors(registry=x))

    def test_historical_registry_pin_drift_rejected(self):
        x=self.mutated_registry(); x["historical_three_family_registry"]["git_blob_sha1"]="0"*40; self.assertTrue(self.errors(registry=x))

    def test_historical_registry_actual_blob_drift_rejected(self):
        self.assertTrue(self.errors(historical_blob="0"*40))

    def test_replay_evidence_insertion_rejected(self):
        x=self.mutated_registry(); x["execution_state"]["evidence_bundle_count"]=1; self.assertTrue(self.errors(registry=x))

    def test_route_proposal_count_inflation_rejected(self):
        x=self.mutated_registry(); x["execution_state"]["proposed_route_count"]=1; self.assertTrue(self.errors(registry=x))

    def test_route_registration_count_inflation_rejected(self):
        x=self.mutated_registry(); x["execution_state"]["registered_route_count_created_by_this_operation"]=1; self.assertTrue(self.errors(registry=x))

    def test_adjudication_count_inflation_rejected(self):
        x=self.mutated_registry(); x["execution_state"]["adjudication_count"]=1; self.assertTrue(self.errors(registry=x))

    def test_output_count_inflation_rejected(self):
        x=self.mutated_registry(); x["execution_state"]["cert_output_count"]=1; self.assertTrue(self.errors(registry=x))

    def test_proved_count_inflation_rejected(self):
        x=self.mutated_registry(); x["execution_state"]["mathematical_target_proved_count"]=1; self.assertTrue(self.errors(registry=x))

    def test_registry_circuit_inflation_rejected(self):
        x=self.mutated_registry(); x["scope"]["circuit_target_count"]=1; self.assertTrue(self.errors(registry=x))

    def test_registry_gate_inflation_rejected(self):
        x=self.mutated_registry(); x["scope"]["gate_bounds_in_work_package"]=True; self.assertTrue(self.errors(registry=x))

    def test_registry_total_size_inflation_rejected(self):
        x=self.mutated_registry(); x["scope"]["total_leaves_vertices_in_work_package"]=True; self.assertTrue(self.errors(registry=x))

    def test_registry_pdf_equivalence_inflation_rejected(self):
        x=self.mutated_registry(); x["scope"]["historical_pdf_byte_equivalence"]=True; self.assertTrue(self.errors(registry=x))

    def test_all_lean_aggregate_inflation_rejected(self):
        x=self.mutated_registry(); x["aggregate_integration"]["creates_aggregate_route"]=True; self.assertTrue(self.errors(registry=x))

    def test_global_route_registry_modification_rejected(self):
        x=self.mutated_registry(); x["route_controls"]["global_certification_route_registry_modified"]=True; self.assertTrue(self.errors(registry=x))


if __name__ == "__main__":
    unittest.main()
