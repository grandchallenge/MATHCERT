from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import runpy
import unittest

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_vgse_route_registration",
    ROOT / "ci" / "validate_vgse_route_registration.py",
)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(module)

C06_PRODUCER_BINDING_PATH = (
    ROOT / "evidence" / "vgse" / "VGSE-WP00-CERT-001-c06-producer-binding.json"
)
EXPECTED_C06_PRODUCER_BINDING_BLOB = "80ca458063ac2d500a2046f9594e90de0d737f86"


def git_blob_sha1(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload,
        usedforsecurity=False,
    ).hexdigest()


class VGSERouteRegistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(module.RECORD_PATH.read_text(encoding="utf-8"))
        cls.base_registry = json.loads(module.BASE_REGISTRY_PATH.read_text(encoding="utf-8"))
        cls.documentation = module.DOC_PATH.read_text(encoding="utf-8")

    def errors(self, record=None, **kwargs):
        return module.validation_errors(
            copy.deepcopy(self.record if record is None else record),
            base_registry=copy.deepcopy(kwargs.pop("base_registry", self.base_registry)),
            documentation=kwargs.pop("documentation", self.documentation),
            **kwargs,
        )

    def test_current_registration_passes(self) -> None:
        self.assertEqual(module.validation_errors(), [])

    def test_base_registry_blob_drift_fails(self) -> None:
        self.assertTrue(any("blob drift" in error for error in self.errors(base_blob="0" * 40)))

    def test_duplicate_route_in_base_fails(self) -> None:
        base = copy.deepcopy(self.base_registry)
        base["routes"].append({"route_id": "MC-ROUTE-VGSE-001", "campaign_id": "VGSE-001"})
        self.assertTrue(any("additive" in error for error in self.errors(base_registry=base)))

    def test_route_cannot_adjudicate(self) -> None:
        record = copy.deepcopy(self.record)
        record["may_adjudicate"] = True
        self.assertTrue(any("may not adjudicate" in error or "False was expected" in error for error in self.errors(record)))

    def test_route_cannot_issue_output(self) -> None:
        record = copy.deepcopy(self.record)
        record["cert_output"] = {"path": "certificate.json"}
        self.assertTrue(any("certificate output" in error or "None was expected" in error for error in self.errors(record)))

    def test_route_state_cannot_inflate(self) -> None:
        record = copy.deepcopy(self.record)
        record["route_state"] = "qualified"
        self.assertTrue(any("registered_pending_evidence" in error for error in self.errors(record)))

    def test_programme_routing_cannot_activate(self) -> None:
        record = copy.deepcopy(self.record)
        record["activation_effect"]["programme_active_routing_changed"] = True
        self.assertTrue(any("premature activation effect" in error or "False was expected" in error for error in self.errors(record)))

    def test_certificate_authority_cannot_activate(self) -> None:
        record = copy.deepcopy(self.record)
        record["activation_effect"]["certificate_output_authorized"] = True
        self.assertTrue(any("premature activation effect" in error or "False was expected" in error for error in self.errors(record)))

    def test_algebraic_lane_cannot_absorb_planar_claim(self) -> None:
        record = copy.deepcopy(self.record)
        record["lanes"]["algebraic"]["target_claim_ids"].append("VGSE-C04")
        self.assertTrue(any("algebraic target set drift" in error or "overlap" in error for error in self.errors(record)))

    def test_planar_lane_cannot_drop_equivalence_claim(self) -> None:
        record = copy.deepcopy(self.record)
        record["lanes"]["planar_geometry"]["target_claim_ids"].remove("VGSE-C06")
        self.assertTrue(any("planar target set drift" in error or "incomplete" in error for error in self.errors(record)))

    def test_modality_drift_fails(self) -> None:
        record = copy.deepcopy(self.record)
        record["lanes"]["algebraic"]["requested_modalities"].remove("SPECIALIST_AUDIT_PENDING")
        self.assertTrue(any("modality set drift" in error for error in self.errors(record)))

    def test_mathematical_proof_claim_fails(self) -> None:
        record = copy.deepcopy(self.record)
        record["claim_boundary"]["mathematical_target_proved"] = True
        self.assertTrue(any("prohibited claim authority" in error or "False was expected" in error for error in self.errors(record)))

    def test_manufacturing_claim_fails(self) -> None:
        record = copy.deepcopy(self.record)
        record["claim_boundary"]["manufacturing_claim_authorized"] = True
        self.assertTrue(any("prohibited claim authority" in error or "False was expected" in error for error in self.errors(record)))

    def test_commercial_claim_fails(self) -> None:
        record = copy.deepcopy(self.record)
        record["claim_boundary"]["product_or_commercial_claim_authorized"] = True
        self.assertTrue(any("prohibited claim authority" in error or "False was expected" in error for error in self.errors(record)))

    def test_missing_documentary_boundary_fails(self) -> None:
        documentation = self.documentation.replace("does not issue a certificate", "issues a certificate")
        self.assertTrue(any("documentation boundary missing" in error for error in self.errors(documentation=documentation)))

    def test_c06_producer_binding_is_exact_and_fail_closed(self) -> None:
        self.assertTrue(C06_PRODUCER_BINDING_PATH.is_file())
        self.assertEqual(
            git_blob_sha1(C06_PRODUCER_BINDING_PATH),
            EXPECTED_C06_PRODUCER_BINDING_BLOB,
        )
        binding = json.loads(C06_PRODUCER_BINDING_PATH.read_text(encoding="utf-8"))
        self.assertEqual(binding["route_id"], "MC-ROUTE-VGSE-001")
        self.assertEqual(binding["claims_addressed"], ["VGSE-C06"])
        self.assertEqual(
            binding["producer_evidence"]["protected_merge"],
            "c8e81d262d4da1a36b312f017443777a4c7888db",
        )
        self.assertEqual(
            binding["producer_evidence"]["evidence_record"]["git_blob_sha1"],
            "97f2834d57d8ac9d60544d0f2498aa527aa72422",
        )
        self.assertGreater(
            binding["producer_result"]["certified_rounding_robust_lower_bound"],
            binding["producer_result"]["required_lower_threshold"],
        )
        self.assertFalse(
            binding["producer_result"]
            ["visible_reconstructed_geometric_weight_class_measures_pinned_C"]
        )
        self.assertEqual(
            binding["cert_interpretation"]["c04_admitted_evidence_status"],
            "UNCHANGED",
        )
        self.assertEqual(
            binding["cert_interpretation"]["c05_admitted_evidence_status"],
            "UNCHANGED",
        )
        self.assertEqual(
            binding["cert_interpretation"]["c06_state"],
            "BLOCKED_VISIBLE_GEOMETRIC_WEIGHT_BRIDGE_TO_PINNED_C",
        )
        self.assertFalse(
            binding["cert_interpretation"]["post_hoc_equivalence_broadening_authorized"]
        )
        self.assertFalse(binding["trust"]["may_adjudicate_after_this_record_alone"])
        self.assertIsNone(binding["trust"]["certificate_output"])
        self.assertFalse(binding["trust"]["mathematical_target_proved"])

    def test_wp00_evidence_replay_when_dependencies_are_available(self) -> None:
        evidence_test = ROOT / "ci" / "test_replay_vgse_wp00_exact_evidence.py"
        if not evidence_test.exists():
            self.skipTest("VGSE WP00 evidence replay is not present on this revision")
        if importlib.util.find_spec("sympy") is None:
            self.skipTest("SymPy is installed only in the bounded VGSE evidence workflow")
        runpy.run_path(str(evidence_test), run_name="__main__")


if __name__ == "__main__":
    unittest.main(verbosity=2)
