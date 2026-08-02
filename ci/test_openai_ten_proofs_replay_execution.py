from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_openai_ten_proofs_replay_execution",
    ROOT / "ci" / "validate_openai_ten_proofs_replay_execution.py",
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class OpenAITenProofsReplayExecutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.record = json.loads(MODULE.RECORD_PATH.read_text(encoding="utf-8"))
        self.workflow = MODULE.WORKFLOW_PATH.read_text(encoding="utf-8")
        self.runner = MODULE.RUNNER_PATH.read_text(encoding="utf-8")
        self.adapter = MODULE.ADAPTER_PATH.read_text(encoding="utf-8")
        self.routes = json.loads(MODULE.ROUTES_PATH.read_text(encoding="utf-8"))
        self.routes_blob = MODULE.git_blob_sha1(MODULE.ROUTES_PATH)
        self.wp_blob = MODULE.git_blob_sha1(MODULE.WORK_PACKAGE_REGISTRY)

    def errors(self, **overrides):
        return MODULE.validation_errors(
            record=copy.deepcopy(overrides.get("record", self.record)),
            workflow_text=overrides.get("workflow", self.workflow),
            runner_text=overrides.get("runner", self.runner),
            adapter_text=overrides.get("adapter", self.adapter),
            routes=copy.deepcopy(overrides.get("routes", self.routes)),
            routes_blob=overrides.get("routes_blob", self.routes_blob),
            wp_registry_blob=overrides.get("wp_blob", self.wp_blob),
        )

    def test_current_execution_passes(self) -> None:
        self.assertEqual(self.errors(), [])

    def test_toolchain_drift_is_rejected(self) -> None:
        record = copy.deepcopy(self.record)
        record["workflow"]["toolchain"]["comparator"] = "0" * 40
        self.assertTrue(self.errors(record=record))

    def test_family_removal_is_rejected(self) -> None:
        record = copy.deepcopy(self.record)
        record["families"].pop()
        self.assertTrue(self.errors(record=record))

    def test_completed_state_without_evidence_is_rejected(self) -> None:
        record = copy.deepcopy(self.record)
        record["execution_state"]["completed_family_count"] = 3
        self.assertTrue(self.errors(record=record))

    def test_route_registration_is_rejected(self) -> None:
        routes = copy.deepcopy(self.routes)
        routes["routes"].append({"route_id": "MC-ROUTE-OTP-F-EHRHART"})
        self.assertTrue(self.errors(routes=routes))

    def test_route_registry_blob_drift_is_rejected(self) -> None:
        self.assertTrue(self.errors(routes_blob="0" * 40))

    def test_work_package_registry_drift_is_rejected(self) -> None:
        self.assertTrue(self.errors(wp_blob="0" * 40))

    def test_unpinned_action_is_rejected(self) -> None:
        workflow = self.workflow.replace(
            "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02",
            "actions/upload-artifact@v4",
        )
        self.assertTrue(self.errors(workflow=workflow))

    def test_missing_nanoda_acceptance_is_rejected(self) -> None:
        runner = self.runner.replace("Nanoda kernel accepts the solution", "nanoda omitted")
        self.assertTrue(self.errors(runner=runner))

    def test_landrun_separator_removal_is_rejected(self) -> None:
        adapter = self.adapter.replace(
            'exec "$real_landrun" "${prefix[@]}" -- "$@"',
            'exec "$real_landrun" "${prefix[@]}" "$@"',
        )
        self.assertTrue(self.errors(adapter=adapter))

    def test_adjudication_enable_is_rejected(self) -> None:
        record = copy.deepcopy(self.record)
        record["route_controls"]["may_adjudicate"] = True
        self.assertTrue(self.errors(record=record))

    def test_aggregate_route_enable_is_rejected(self) -> None:
        record = copy.deepcopy(self.record)
        record["route_controls"]["aggregate_route_prohibited"] = False
        self.assertTrue(self.errors(record=record))


if __name__ == "__main__":
    unittest.main()
