from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_openai_ten_proofs_certification_work_packages",
    ROOT / "ci" / "validate_openai_ten_proofs_certification_work_packages.py",
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class OpenAITenProofsCertificationWorkPackageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = json.loads(MODULE.REGISTRY_PATH.read_text(encoding="utf-8"))
        self.packages = {}
        self.blobs = {}
        for path in sorted(MODULE.PACKAGE_DIR.glob("*.json")):
            record = json.loads(path.read_text(encoding="utf-8"))
            family = record["result_family"]
            self.packages[family] = record
            self.blobs[family] = MODULE.git_blob_sha1(path)
        self.routes = json.loads(MODULE.ROUTES_PATH.read_text(encoding="utf-8"))
        self.routes_blob = MODULE.git_blob_sha1(MODULE.ROUTES_PATH)

    def errors(self, *, registry=None, packages=None, blobs=None, routes=None, routes_blob=None):
        return MODULE.validation_errors(
            registry=copy.deepcopy(self.registry if registry is None else registry),
            packages=copy.deepcopy(self.packages if packages is None else packages),
            package_blobs=copy.deepcopy(self.blobs if blobs is None else blobs),
            routes=copy.deepcopy(self.routes if routes is None else routes),
            routes_blob=self.routes_blob if routes_blob is None else routes_blob,
        )

    def test_current_work_packages_pass(self) -> None:
        self.assertEqual(self.errors(), [])

    def test_missing_package_is_rejected(self) -> None:
        packages = copy.deepcopy(self.packages)
        packages.pop("OTP-F-EHRHART")
        self.assertTrue(self.errors(packages=packages))

    def test_unknown_aggregate_package_is_rejected(self) -> None:
        packages = copy.deepcopy(self.packages)
        packages["OTP-ALL"] = copy.deepcopy(packages["OTP-F-EHRHART"])
        self.assertTrue(self.errors(packages=packages))

    def test_intake_digest_drift_is_rejected(self) -> None:
        packages = copy.deepcopy(self.packages)
        packages["OTP-J1-COMPACTNESS"]["authority"]["intake_record"]["digest"] = "0" * 40
        self.assertTrue(self.errors(packages=packages))

    def test_tracker_issue_drift_is_rejected(self) -> None:
        packages = copy.deepcopy(self.packages)
        packages["OTP-J2-TWO-DEGENERATE"]["tracker_issue"] = (
            "https://github.com/grandchallenge/MATHCERT/issues/1"
        )
        self.assertTrue(self.errors(packages=packages))

    def test_execution_disable_is_rejected(self) -> None:
        packages = copy.deepcopy(self.packages)
        packages["OTP-F-EHRHART"]["execution"]["allowed"] = False
        self.assertTrue(self.errors(packages=packages))

    def test_aggregate_import_dependency_is_rejected(self) -> None:
        packages = copy.deepcopy(self.packages)
        packages["OTP-J1-COMPACTNESS"]["execution"]["aggregate_import_required"] = True
        self.assertTrue(self.errors(packages=packages))

    def test_premature_route_entry_is_rejected(self) -> None:
        packages = copy.deepcopy(self.packages)
        packages["OTP-J2-TWO-DEGENERATE"]["route_state"][
            "certification_route_registry_entry"
        ] = {"route_id": "MC-ROUTE-OTP-J2-TWO-DEGENERATE"}
        self.assertTrue(self.errors(packages=packages))

    def test_adjudication_enable_is_rejected(self) -> None:
        packages = copy.deepcopy(self.packages)
        packages["OTP-F-EHRHART"]["route_state"]["may_adjudicate"] = True
        self.assertTrue(self.errors(packages=packages))

    def test_proved_state_is_rejected(self) -> None:
        packages = copy.deepcopy(self.packages)
        packages["OTP-J1-COMPACTNESS"]["route_state"]["mathematical_target_proved"] = True
        self.assertTrue(self.errors(packages=packages))

    def test_package_blob_drift_is_rejected(self) -> None:
        blobs = copy.deepcopy(self.blobs)
        blobs["OTP-J2-TWO-DEGENERATE"] = "0" * 40
        self.assertTrue(self.errors(blobs=blobs))

    def test_execution_state_inflation_is_rejected(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["execution_state"]["evidence_bundle_count"] = 3
        self.assertTrue(self.errors(registry=registry))

    def test_blocked_lane_removal_is_rejected(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["blocked_repair_lanes"] = ["OTP-C-PERMANENT"]
        self.assertTrue(self.errors(registry=registry))

    def test_aggregate_work_package_is_rejected(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["route_controls"]["aggregate_work_package"] = {
            "work_package_id": "OTP-ALL-CERT-WP01"
        }
        self.assertTrue(self.errors(registry=registry))

    def test_global_route_registry_change_is_rejected(self) -> None:
        self.assertTrue(self.errors(routes_blob="0" * 40))

    def test_requested_route_registration_is_rejected(self) -> None:
        routes = copy.deepcopy(self.routes)
        routes["routes"].append({"route_id": "MC-ROUTE-OTP-F-EHRHART"})
        self.assertTrue(self.errors(routes=routes))


if __name__ == "__main__":
    unittest.main()
