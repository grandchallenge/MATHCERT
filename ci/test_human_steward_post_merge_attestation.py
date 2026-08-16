from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import unittest
from pathlib import Path

import validate_otp_j2_route_target_successor as j2

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_human_steward_post_merge_attestation",
    ROOT / "ci/validate_human_steward_post_merge_attestation.py",
)
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class HumanStewardPostMergeAttestationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.attestation = json.loads(M.ATTESTATION.read_text(encoding="utf-8"))
        proc = subprocess.run(
            ["git", "-C", str(ROOT), "cat-file", "blob", M.HISTORICAL_ROUTE_BLOB],
            capture_output=True,
            text=True,
            check=True,
        )
        self.routes = json.loads(proc.stdout)
        self.schema = json.loads(M.SCHEMA.read_text(encoding="utf-8"))

    def errors(self, **kwargs):
        return M.validation_errors(
            attestation=copy.deepcopy(kwargs.get("attestation", self.attestation)),
            document_text=kwargs.get("document_text", M.EXPECTED_DOCUMENT),
            schema=copy.deepcopy(kwargs.get("schema", self.schema)),
            routes=copy.deepcopy(kwargs.get("routes", self.routes)),
            document_blob=kwargs.get("document_blob", "afe8b4241fe5c8cc99626f713f9ac76f48f7b805"),
            route_blob=kwargs.get("route_blob", M.HISTORICAL_ROUTE_BLOB),
            receipt_blob=kwargs.get("receipt_blob", "38b1c03a6506f877ad9aed74e92cb6d202b444a5"),
        )

    def test_current_attestation_passes(self) -> None:
        self.assertEqual([], self.errors())

    def test_live_j2_output_successor_passes_separately(self) -> None:
        self.assertEqual([], j2.live_output_successor_errors())

    def test_unrelated_uc_route_evolution_is_permitted(self) -> None:
        routes = copy.deepcopy(self.routes)
        uc = next(item for item in routes["routes"] if item["campaign_id"] == "UC-001")
        uc["reopening_conditions"].append("unrelated route evolution")
        self.assertEqual([], self.errors(routes=routes))

    def test_reviewed_head_drift_is_rejected(self) -> None:
        data = copy.deepcopy(self.attestation)
        data["subject"]["exact_reviewed_head"] = "0" * 40
        self.assertTrue(self.errors(attestation=data))

    def test_merge_commit_drift_is_rejected(self) -> None:
        data = copy.deepcopy(self.attestation)
        data["subject"]["merge_commit"] = "0" * 40
        self.assertTrue(self.errors(attestation=data))

    def test_false_pre_merge_chronology_is_rejected(self) -> None:
        data = copy.deepcopy(self.attestation)
        data["chronology"]["disposition_recorded_after_merge"] = False
        self.assertTrue(self.errors(attestation=data))

    def test_event_order_rewrite_is_rejected(self) -> None:
        data = copy.deepcopy(self.attestation)
        data["chronology"]["does_not_rewrite_event_order"] = False
        self.assertTrue(self.errors(attestation=data))

    def test_verbatim_text_drift_is_rejected(self) -> None:
        self.assertTrue(self.errors(document_text=M.EXPECTED_DOCUMENT + "Certified.\n"))

    def test_document_blob_drift_is_rejected(self) -> None:
        self.assertTrue(self.errors(document_blob="0" * 40))

    def test_receipt_substitution_is_rejected(self) -> None:
        self.assertTrue(self.errors(receipt_blob="0" * 40))

    def test_route_registry_substitution_is_rejected(self) -> None:
        self.assertTrue(self.errors(route_blob="0" * 40))

    def test_repository_mirror_author_drift_is_rejected(self) -> None:
        data = copy.deepcopy(self.attestation)
        data["repository_mirror"]["comment_author"] = "fyremael"
        self.assertTrue(self.errors(attestation=data))

    def test_route_state_inflation_is_rejected(self) -> None:
        routes = copy.deepcopy(self.routes)
        route = next(item for item in routes["routes"] if item["route_id"] == "MC-ROUTE-OTP-F-EHRHART")
        route["intake_status"] = "qualified"
        self.assertTrue(self.errors(routes=routes))

    def test_cert_output_insertion_is_rejected(self) -> None:
        routes = copy.deepcopy(self.routes)
        route = next(item for item in routes["routes"] if item["route_id"] == "MC-ROUTE-OTP-J1-COMPACTNESS")
        route["cert_output"] = {
            "repository": "grandchallenge/MATHCERT",
            "commit_sha": "1" * 40,
            "path": "forged.json",
            "digest_algorithm": "git_blob_sha1",
            "digest": "2" * 40,
        }
        self.assertTrue(self.errors(routes=routes))

    def test_blocker_removal_is_rejected(self) -> None:
        data = copy.deepcopy(self.attestation)
        data["preserved_limitations"]["blocked_repair_lanes"] = ["OTP-C-PERMANENT"]
        self.assertTrue(self.errors(attestation=data))

    def test_claim_boundary_weakening_is_rejected(self) -> None:
        data = copy.deepcopy(self.attestation)
        data["claim_boundary"] = "The routes are certified."
        self.assertTrue(self.errors(attestation=data))

    def test_unexpected_authority_field_is_rejected(self) -> None:
        data = copy.deepcopy(self.attestation)
        data["retroactive_pre_merge_authority"] = True
        self.assertTrue(self.errors(attestation=data))


if __name__ == "__main__":
    unittest.main()
