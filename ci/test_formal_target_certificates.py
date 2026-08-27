from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

import validate_formal_target_certificates as module


class FormalTargetCertificateTests(unittest.TestCase):
    def load_records(self) -> dict[str, dict]:
        return {
            path.name: module.load_json(path)
            for path in module.CERT_DIR.glob("*.json")
        }

    def write_records(self, records: dict[str, dict]) -> Path:
        root = Path(tempfile.mkdtemp())
        for name, payload in records.items():
            (root / name).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return root

    def record_errors(self, mutate) -> list[str]:
        records = copy.deepcopy(self.load_records())
        mutate(records)
        directory = self.write_records(records)
        return module.certificate_errors(directory=directory)

    def write_registry(self, payload: dict) -> Path:
        handle = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        with handle:
            json.dump(payload, handle)
        return Path(handle.name)

    def a_errors_for_registry(self, registry: dict) -> list[str]:
        path = self.write_registry(registry)
        try:
            return module._a_certificate_errors(module.CERT_DIR / module.A_FILE, path)
        finally:
            path.unlink(missing_ok=True)

    def test_current_certificates_pass(self) -> None:
        self.assertEqual([], module.certificate_errors())

    def test_mathematical_proof_inflation_fails(self) -> None:
        errors = self.record_errors(
            lambda r: r["MC-FC-WP00-RH-001.json"].__setitem__("mathematical_target_proved", True)
        )
        self.assertTrue(any("mathematical target must remain unproved" in error for error in errors))

    def test_missing_ns_axiom_fails(self) -> None:
        errors = self.record_errors(
            lambda r: r["MC-FC-WP00-NS-CI-001.json"]["axiom_report"]["imported_domain_axioms"].pop()
        )
        self.assertTrue(any("imported domain axiom set drift" in error for error in errors))

    def test_rh_domain_axiom_inflation_fails(self) -> None:
        errors = self.record_errors(
            lambda r: r["MC-FC-WP00-RH-001.json"]["axiom_report"]["imported_domain_axioms"].append("Hidden.Axiom")
        )
        self.assertTrue(any("imported domain axiom set drift" in error for error in errors))

    def test_unexpected_axiom_fails(self) -> None:
        errors = self.record_errors(
            lambda r: r["MC-FC-WP00-NS-CI-001.json"]["axiom_report"]["unexpected_axioms"].append("Hidden.Axiom")
        )
        self.assertTrue(any("unexpected axiom" in error for error in errors))

    def test_solve_commit_drift_fails(self) -> None:
        errors = self.record_errors(
            lambda r: r["MC-FC-WP00-RH-001.json"]["solve_provider"].__setitem__("merge_commit", "0" * 40)
        )
        self.assertTrue(any("MATHSOLVE merge drift" in error for error in errors))

    def test_disposition_inflation_fails(self) -> None:
        errors = self.record_errors(
            lambda r: r["MC-FC-WP00-RH-001.json"].__setitem__("disposition", "theorem_certified")
        )
        self.assertTrue(any("disposition inflation" in error for error in errors))

    def test_rh_concordance_downgrade_fails(self) -> None:
        errors = self.record_errors(
            lambda r: r["MC-FC-WP00-RH-001.json"].__setitem__("concordance_theorem_kernel_checked", False)
        )
        self.assertTrue(any("concordance disposition drift" in error for error in errors))

    def test_ns_false_equivalence_promotion_fails(self) -> None:
        errors = self.record_errors(
            lambda r: r["MC-FC-WP00-NS-CI-001.json"].__setitem__("concordance_theorem_kernel_checked", True)
        )
        self.assertTrue(any("concordance disposition drift" in error for error in errors))

    def test_permanent_target_omission_fails(self) -> None:
        errors = self.record_errors(
            lambda r: r["MC-OTP-C-PERMANENT-001.json"]["encoded_targets"].pop()
        )
        self.assertTrue(any("encoded target scope drift" in error or "schema violation" in error for error in errors))

    def test_permanent_circuit_scope_inflation_fails(self) -> None:
        errors = self.record_errors(
            lambda r: r["MC-OTP-C-PERMANENT-001.json"]["qualification"]["source_projection"].__setitem__("circuit_target_count", 1)
        )
        self.assertTrue(any("source projection or scope inflation" in error or "schema violation" in error for error in errors))

    def test_permanent_gate_scope_inflation_fails(self) -> None:
        errors = self.record_errors(
            lambda r: r["MC-OTP-C-PERMANENT-001.json"]["preserved_limitations"].__setitem__("gate_bounds_in_scope", True)
        )
        self.assertTrue(any("limitation inflated" in error or "schema violation" in error for error in errors))

    def test_permanent_proof_promotion_fails(self) -> None:
        errors = self.record_errors(
            lambda r: r["MC-OTP-C-PERMANENT-001.json"]["state"].__setitem__("mathematical_target_proved", True)
        )
        self.assertTrue(any("mathematical target must remain unproved" in error or "schema violation" in error for error in errors))

    def test_compactness_target_omission_fails(self) -> None:
        errors = self.record_errors(
            lambda r: r["MC-OTP-J1-COMPACTNESS-001.json"]["encoded_targets"].pop()
        )
        self.assertTrue(any("encoded target scope drift" in error or "schema violation" in error for error in errors))

    def test_compactness_historical_formulation_inflation_fails(self) -> None:
        errors = self.record_errors(
            lambda r: r["MC-OTP-J1-COMPACTNESS-001.json"]["preserved_limitations"].__setitem__("historical_compactness_formulations_admitted", True)
        )
        self.assertTrue(any("limitation inflated" in error or "schema violation" in error for error in errors))

    def test_compactness_proof_promotion_fails(self) -> None:
        errors = self.record_errors(
            lambda r: r["MC-OTP-J1-COMPACTNESS-001.json"]["state"].__setitem__("mathematical_target_proved", True)
        )
        self.assertTrue(any("mathematical target must remain unproved" in error or "schema violation" in error for error in errors))

    def test_j2_target_omission_fails(self) -> None:
        errors = self.record_errors(
            lambda r: r["MC-OTP-J2-TWO-DEGENERATE-001.json"]["encoded_targets"].pop()
        )
        self.assertTrue(any("encoded target scope drift" in error or "schema violation" in error for error in errors))

    def test_j2_historical_target_reinsertion_fails(self) -> None:
        errors = self.record_errors(
            lambda r: r["MC-OTP-J2-TWO-DEGENERATE-001.json"]["encoded_targets"].__setitem__(0, "TwoDegenerateGraphs.twoDegenerateExtremalCounterexample")
        )
        self.assertTrue(any("encoded target scope drift" in error or "schema violation" in error for error in errors))

    def test_j2_stronger_coloring_scope_inflation_fails(self) -> None:
        errors = self.record_errors(
            lambda r: r["MC-OTP-J2-TWO-DEGENERATE-001.json"]["qualification"]["source_projection"].__setitem__("stronger_coloring_side_property_in_scope", True)
        )
        self.assertTrue(any("source-faithful projection or scope inflation" in error or "schema violation" in error for error in errors))

    def test_j2_stronger_coloring_certification_fails(self) -> None:
        errors = self.record_errors(
            lambda r: r["MC-OTP-J2-TWO-DEGENERATE-001.json"]["state"].__setitem__("stronger_coloring_property_certified", True)
        )
        self.assertTrue(any("stronger coloring property certification inflation" in error or "schema violation" in error for error in errors))

    def test_j2_proof_promotion_fails(self) -> None:
        errors = self.record_errors(
            lambda r: r["MC-OTP-J2-TWO-DEGENERATE-001.json"]["state"].__setitem__("mathematical_target_proved", True)
        )
        self.assertTrue(any("mathematical target must remain unproved" in error or "schema violation" in error for error in errors))

    def test_permanent_route_output_drift_fails(self) -> None:
        registry = module.load_json(module.REGISTRY_PATH)
        route = next(route for route in registry["routes"] if route["campaign_id"] == "OTP-C-PERMANENT")
        route["cert_output"]["digest"] = "0" * 40
        path = self.write_registry(registry)
        try:
            errors = module.certificate_errors(registry_path=path)
        finally:
            path.unlink(missing_ok=True)
        self.assertTrue(any("OTP-C-PERMANENT: route output identity drift" in error for error in errors))

    def test_compactness_route_output_drift_fails(self) -> None:
        registry = module.load_json(module.REGISTRY_PATH)
        route = next(route for route in registry["routes"] if route["campaign_id"] == "OTP-J1-COMPACTNESS")
        route["cert_output"]["digest"] = "0" * 40
        path = self.write_registry(registry)
        try:
            errors = module.certificate_errors(registry_path=path)
        finally:
            path.unlink(missing_ok=True)
        self.assertTrue(any("OTP-J1-COMPACTNESS: route output identity drift" in error for error in errors))

    def test_j2_route_output_drift_fails(self) -> None:
        registry = module.load_json(module.REGISTRY_PATH)
        route = next(route for route in registry["routes"] if route["campaign_id"] == "OTP-J2-TWO-DEGENERATE")
        route["cert_output"]["digest"] = "0" * 40
        path = self.write_registry(registry)
        try:
            errors = module.certificate_errors(registry_path=path)
        finally:
            path.unlink(missing_ok=True)
        self.assertTrue(any("OTP-J2-TWO-DEGENERATE: route output identity drift" in error for error in errors))

    def test_route_downgrade_fails(self) -> None:
        registry = module.load_json(module.REGISTRY_PATH)
        rh = next(route for route in registry["routes"] if route["campaign_id"] == "RH-001")
        rh["intake_status"] = "ready"
        path = self.write_registry(registry)
        try:
            errors = module.certificate_errors(registry_path=path)
        finally:
            path.unlink(missing_ok=True)
        self.assertTrue(any("route is not qualified" in error for error in errors))

    def test_a_validation_ignores_independently_registered_later_route(self) -> None:
        registry = module.load_json(module.REGISTRY_PATH)
        registry["routes"].append({
            "route_id": "MC-ROUTE-OTP-LATER-TEST",
            "campaign_id": "OTP-LATER-TEST",
        })
        self.assertEqual([], self.a_errors_for_registry(registry))

    def test_a_validation_still_rejects_a_route_mutation(self) -> None:
        registry = module.load_json(module.REGISTRY_PATH)
        route = next(route for route in registry["routes"] if route["route_id"] == "MC-ROUTE-OTP-A-SPHERE-PACKING")
        route["cert_output"]["digest"] = "0" * 40
        self.assertTrue(self.a_errors_for_registry(registry))

    def test_a_validation_still_rejects_duplicate_a_route(self) -> None:
        registry = module.load_json(module.REGISTRY_PATH)
        route = next(route for route in registry["routes"] if route["route_id"] == "MC-ROUTE-OTP-A-SPHERE-PACKING")
        registry["routes"].append(copy.deepcopy(route))
        self.assertTrue(self.a_errors_for_registry(registry))

    def test_a_validation_still_rejects_missing_owned_predecessor_route(self) -> None:
        registry = module.load_json(module.REGISTRY_PATH)
        registry["routes"] = [
            route for route in registry["routes"]
            if route.get("route_id") != "MC-ROUTE-UC-001"
        ]
        self.assertTrue(self.a_errors_for_registry(registry))

    def test_missing_certificate_fails(self) -> None:
        records = self.load_records()
        records.pop("MC-FC-WP00-RH-001.json")
        directory = self.write_records(records)
        errors = module.certificate_errors(directory=directory)
        self.assertTrue(any("missing formal target certificate" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
