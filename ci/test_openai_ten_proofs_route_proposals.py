from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_openai_ten_proofs_route_proposals",
    ROOT / "ci/validate_openai_ten_proofs_route_proposals.py",
)
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class RouteProposalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.proposals = {
            path.stem: json.loads(path.read_text(encoding="utf-8"))
            for path in sorted(M.P.glob("*.json"))
        }
        self.registry = json.loads(M.R.read_text(encoding="utf-8"))
        self.routes = json.loads(M.G.read_text(encoding="utf-8"))
        self.local_blobs: dict[str, str] = {}
        for family, values in M.E.items():
            _, _, _, _, _, _, bundle_slug, _, _, _, _, _, _ = values
            for path in (
                f"governance/result_family_intakes/{family}.json",
                f"governance/result_family_work_packages/{family}-CERT-WP01.json",
                f"governance/result_family_replay_evidence/{family}.json",
                f"evidence/openai_ten_proofs/{bundle_slug}.zip.b64",
            ):
                self.local_blobs[path] = M.blob(ROOT / path)

    def errors(self, **kwargs):
        return M.validation_errors(
            proposals=copy.deepcopy(kwargs.get("proposals", self.proposals)),
            registry=copy.deepcopy(kwargs.get("registry", self.registry)),
            routes=copy.deepcopy(kwargs.get("routes", self.routes)),
            local_blobs=copy.deepcopy(kwargs.get("local_blobs", self.local_blobs)),
        )

    def test_current_passes(self) -> None:
        self.assertEqual(self.errors(), [])

    def test_missing_family(self) -> None:
        proposals = copy.deepcopy(self.proposals)
        proposals.pop("OTP-F-EHRHART")
        self.assertTrue(self.errors(proposals=proposals))

    def test_family_inflation(self) -> None:
        proposals = copy.deepcopy(self.proposals)
        proposals["OTP-A-SPHERE-PACKING"] = copy.deepcopy(
            proposals["OTP-F-EHRHART"]
        )
        self.assertTrue(self.errors(proposals=proposals))

    def test_route_state_inflation(self) -> None:
        proposals = copy.deepcopy(self.proposals)
        proposals["OTP-F-EHRHART"]["proposal_state"] = "registered"
        self.assertTrue(self.errors(proposals=proposals))

    def test_global_route_insertion(self) -> None:
        routes = copy.deepcopy(self.routes)
        routes["routes"].append({"route_id": "MC-ROUTE-OTP-F-EHRHART"})
        self.assertTrue(self.errors(routes=routes))

    def test_adjudication_output_inflation(self) -> None:
        proposals = copy.deepcopy(self.proposals)
        controls = proposals["OTP-J1-COMPACTNESS"]["route_controls"]
        controls["may_adjudicate"] = True
        controls["cert_output"] = {"forged": True}
        self.assertTrue(self.errors(proposals=proposals))

    def test_proof_promotion(self) -> None:
        proposals = copy.deepcopy(self.proposals)
        proposals["OTP-J2-TWO-DEGENERATE"]["route_controls"][
            "mathematical_target_proved"
        ] = True
        self.assertTrue(self.errors(proposals=proposals))

    def test_aggregate_route(self) -> None:
        proposals = copy.deepcopy(self.proposals)
        proposals["OTP-F-EHRHART"]["route_controls"]["aggregate_route"] = True
        self.assertTrue(self.errors(proposals=proposals))

    def test_whole_document_inflation(self) -> None:
        proposals = copy.deepcopy(self.proposals)
        proposals["OTP-J1-COMPACTNESS"]["evidence_disposition"][
            "whole_document_semantic_equivalence"
        ] = "established"
        self.assertTrue(self.errors(proposals=proposals))

    def test_full_proof_claim(self) -> None:
        proposals = copy.deepcopy(self.proposals)
        proposals["OTP-J2-TWO-DEGENERATE"]["evidence_disposition"][
            "proof_body_compared_in_full"
        ] = True
        self.assertTrue(self.errors(proposals=proposals))

    def test_audit_blob_drift(self) -> None:
        proposals = copy.deepcopy(self.proposals)
        proposals["OTP-F-EHRHART"]["authority"]["source_revision_audit"][
            "digest"
        ] = "0" * 40
        self.assertTrue(self.errors(proposals=proposals))

    def test_manifest_drift(self) -> None:
        proposals = copy.deepcopy(self.proposals)
        proposals["OTP-F-EHRHART"]["authority"]["provider_manifest"][
            "commit_sha"
        ] = "0" * 40
        self.assertTrue(self.errors(proposals=proposals))

    def test_semantic_drift(self) -> None:
        proposals = copy.deepcopy(self.proposals)
        proposals["OTP-J1-COMPACTNESS"]["authority"]["semantic_record"][
            "digest"
        ] = "0" * 40
        self.assertTrue(self.errors(proposals=proposals))

    def test_bundle_substitution(self) -> None:
        proposals = copy.deepcopy(self.proposals)
        proposals["OTP-J2-TWO-DEGENERATE"]["authority"]["repository_bundle"][
            "decoded_sha256"
        ] = "0" * 64
        self.assertTrue(self.errors(proposals=proposals))

    def test_local_intake_drift(self) -> None:
        blobs = copy.deepcopy(self.local_blobs)
        blobs["governance/result_family_intakes/OTP-F-EHRHART.json"] = "0" * 40
        self.assertTrue(self.errors(local_blobs=blobs))

    def test_local_work_package_drift(self) -> None:
        blobs = copy.deepcopy(self.local_blobs)
        blobs[
            "governance/result_family_work_packages/OTP-J1-COMPACTNESS-CERT-WP01.json"
        ] = "0" * 40
        self.assertTrue(self.errors(local_blobs=blobs))

    def test_local_evidence_drift(self) -> None:
        blobs = copy.deepcopy(self.local_blobs)
        blobs[
            "governance/result_family_replay_evidence/OTP-J2-TWO-DEGENERATE.json"
        ] = "0" * 40
        self.assertTrue(self.errors(local_blobs=blobs))

    def test_exclusion_removal(self) -> None:
        proposals = copy.deepcopy(self.proposals)
        proposals["OTP-J2-TWO-DEGENERATE"]["source_scope"][
            "scope_exclusions"
        ] = ["narrow only"]
        self.assertTrue(self.errors(proposals=proposals))

    def test_registry_count_inflation(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["state"]["registered_route_count"] = 3
        self.assertTrue(self.errors(registry=registry))

    def test_registry_blob_drift(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["proposals"][0]["digest"] = "0" * 40
        self.assertTrue(self.errors(registry=registry))

    def test_registry_identity_drift(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["record_id"] = "FORGED-REGISTRY"
        self.assertTrue(self.errors(registry=registry))

    def test_registry_extra_field(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["route_registration_authority"] = True
        self.assertTrue(self.errors(registry=registry))

    def test_registry_claim_boundary_weakening(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["claim_boundary"] = "Three routes are certified."
        self.assertTrue(self.errors(registry=registry))


if __name__ == "__main__":
    unittest.main()
