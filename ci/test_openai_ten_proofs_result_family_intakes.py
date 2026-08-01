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
        self.intakes = {
            path.stem: json.loads(path.read_text(encoding="utf-8"))
            for path in sorted(MODULE.INTAKE_DIR.glob("*.json"))
        }
        self.blobs = {
            path.stem: MODULE.git_blob_sha1(path)
            for path in sorted(MODULE.INTAKE_DIR.glob("*.json"))
        }

    def errors(self, *, registry=None, intakes=None, blobs=None):
        return MODULE.validation_errors(
            registry=copy.deepcopy(self.registry if registry is None else registry),
            intakes=copy.deepcopy(self.intakes if intakes is None else intakes),
            intake_blobs=copy.deepcopy(self.blobs if blobs is None else blobs),
        )

    def test_current_intakes_pass(self) -> None:
        self.assertEqual(self.errors(), [])

    def test_missing_intake_is_rejected(self) -> None:
        intakes = copy.deepcopy(self.intakes)
        intakes.pop("OTP-F-EHRHART")
        self.assertTrue(self.errors(intakes=intakes))

    def test_unknown_aggregate_intake_is_rejected(self) -> None:
        intakes = copy.deepcopy(self.intakes)
        intakes["OTP-ALL"] = copy.deepcopy(intakes["OTP-F-EHRHART"])
        self.assertTrue(self.errors(intakes=intakes))

    def test_solve_packet_digest_drift_is_rejected(self) -> None:
        intakes = copy.deepcopy(self.intakes)
        intakes["OTP-J1-COMPACTNESS"]["authority"]["producer_packet"]["digest"] = "0" * 40
        self.assertTrue(self.errors(intakes=intakes))

    def test_semantic_record_digest_drift_is_rejected(self) -> None:
        intakes = copy.deepcopy(self.intakes)
        intakes["OTP-J2-TWO-DEGENERATE"]["authority"]["semantic_record"]["digest"] = "0" * 40
        self.assertTrue(self.errors(intakes=intakes))

    def test_solve_review_identity_drift_is_rejected(self) -> None:
        intakes = copy.deepcopy(self.intakes)
        intakes["OTP-F-EHRHART"]["authority"]["solve_review"]["review_id"] = 1
        self.assertTrue(self.errors(intakes=intakes))

    def test_local_intake_blob_drift_is_rejected(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["intakes"][0]["digest"] = "0" * 40
        self.assertTrue(self.errors(registry=registry))

    def test_duplicate_intake_identity_is_rejected(self) -> None:
        intakes = copy.deepcopy(self.intakes)
        intakes["OTP-J1-COMPACTNESS"]["intake_id"] = intakes["OTP-F-EHRHART"]["intake_id"]
        self.assertTrue(self.errors(intakes=intakes))

    def test_registered_route_is_rejected(self) -> None:
        intakes = copy.deepcopy(self.intakes)
        intakes["OTP-F-EHRHART"]["certification_state"]["certification_route_registry_entry"] = {
            "route_id": "MC-ROUTE-OTP-F-EHRHART"
        }
        self.assertTrue(self.errors(intakes=intakes))

    def test_cert_output_is_rejected(self) -> None:
        intakes = copy.deepcopy(self.intakes)
        intakes["OTP-J1-COMPACTNESS"]["certification_state"]["cert_output"] = {
            "state": "qualified"
        }
        self.assertTrue(self.errors(intakes=intakes))

    def test_adjudication_is_rejected(self) -> None:
        intakes = copy.deepcopy(self.intakes)
        intakes["OTP-J2-TWO-DEGENERATE"]["certification_state"]["may_adjudicate"] = True
        self.assertTrue(self.errors(intakes=intakes))

    def test_proved_state_is_rejected(self) -> None:
        intakes = copy.deepcopy(self.intakes)
        intakes["OTP-F-EHRHART"]["certification_state"]["mathematical_target_proved"] = True
        self.assertTrue(self.errors(intakes=intakes))

    def test_claim_promotion_is_rejected(self) -> None:
        intakes = copy.deepcopy(self.intakes)
        intakes["OTP-J1-COMPACTNESS"]["certification_state"]["may_promote_claim"] = True
        self.assertTrue(self.errors(intakes=intakes))

    def test_aggregate_route_is_rejected(self) -> None:
        intakes = copy.deepcopy(self.intakes)
        intakes["OTP-J2-TWO-DEGENERATE"]["route_controls"]["may_create_aggregate_route"] = True
        self.assertTrue(self.errors(intakes=intakes))

    def test_semantic_count_inflation_is_rejected(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["gate_state"]["semantic_clear_count"] = 12
        self.assertTrue(self.errors(registry=registry))

    def test_blocked_repair_lane_removal_is_rejected(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["blocked_repair_lanes"] = ["OTP-C-PERMANENT"]
        self.assertTrue(self.errors(registry=registry))

    def test_all_lean_cannot_create_route(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["aggregate_integration"]["creates_cert_route"] = True
        self.assertTrue(self.errors(registry=registry))

    def test_cert_state_inflation_is_rejected(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["cert_state"]["adjudication_count"] = 3
        self.assertTrue(self.errors(registry=registry))

    def test_global_route_registry_modification_is_rejected(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["route_controls"]["global_certification_route_registry_modified"] = True
        self.assertTrue(self.errors(registry=registry))

    def test_aggregate_intake_injection_is_rejected(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["route_controls"]["aggregate_intake"] = {"intake_id": "MC-OTP-INTAKE-ALL"}
        self.assertTrue(self.errors(registry=registry))


if __name__ == "__main__":
    unittest.main()
