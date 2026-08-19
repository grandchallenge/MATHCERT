#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import validate_otp_j2_output_execution as historical
import validate_otp_j2_output_execution_with_a_registration as successor


def historical_suite_errors() -> list[str]:
    historical.ensure_history()
    exact_route_bytes = historical.obj(historical.ROUTE, historical.ROUTES_PATH)
    if exact_route_bytes is None:
        return ["cannot recover exact historical post-J2 route-registry bytes"]
    history = historical.receipt()
    history["routes_head"] = historical.EXPECTED["routes_after"]

    with tempfile.TemporaryDirectory() as td:
        routes_path = Path(td) / "certification_routes.json"
        # Preserve the historical Git blob byte-for-byte; reserializing JSON would
        # correctly change the blob identity and invalidate the historical suite.
        routes_path.write_bytes(exact_route_bytes)
        spec = importlib.util.spec_from_file_location(
            "historical_j2_output_execution_tests",
            historical.ROOT / "ci/test_otp_j2_output_execution.py",
        )
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        with patch.object(historical, "ROUTES", routes_path), patch.object(
            historical, "receipt", lambda: copy.deepcopy(history)
        ):
            spec.loader.exec_module(module)
            suite = unittest.defaultTestLoader.loadTestsFromModule(module)
            stream = io.StringIO()
            result = unittest.TextTestRunner(stream=stream, verbosity=0).run(suite)
    if result.wasSuccessful():
        return []
    return ["historical J2 output-execution tests failed under exact post-transition registry view: " + stream.getvalue().strip()]


class J2OutputExecutionARegistrationSuccessorTests(unittest.TestCase):
    def test_live_successor_passes(self):
        self.assertEqual(successor.validation_errors(), [])

    def test_historical_mutation_suite_preserved(self):
        self.assertEqual(historical_suite_errors(), [])

    def test_extra_live_route_delta_rejected(self):
        live = historical.load(historical.ROUTES)
        live["routes"].append({"route_id": "MC-ROUTE-OTHER-FAMILY"})
        projected = successor.project_a_registration(live)
        historical.ensure_history()
        self.assertNotEqual(projected, historical.obj_json(historical.ROUTE, historical.ROUTES_PATH))


if __name__ == "__main__":
    unittest.main(verbosity=2)
