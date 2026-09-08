from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_openai_ten_proofs_ramsey_intake_successor",
    ROOT / "ci/validate_openai_ten_proofs_ramsey_intake_successor.py",
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class RamseyIntakeSuccessorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.record = MODULE.load_json(MODULE.RECORD)

    def errors(self, record=None, *, legacy_file_exists=False):
        return MODULE.validation_errors(
            copy.deepcopy(self.record if record is None else record),
            legacy_file_exists=legacy_file_exists,
        )

    def test_current_record_passes(self):
        self.assertEqual(self.errors(), [])

    def test_producer_digest_drift_rejected(self):
        data = copy.deepcopy(self.record)
        data["authority"]["producer_packet"]["digest"] = "0" * 40
        self.assertTrue(self.errors(data))

    def test_target_inflation_rejected(self):
        data = copy.deepcopy(self.record)
        data["target_scope"]["lean_theorems"].append("Ramsey.fake")
        self.assertTrue(self.errors(data))

    def test_qualification_removal_rejected(self):
        data = copy.deepcopy(self.record)
        data["target_scope"]["mandatory_qualifications"].pop()
        self.assertTrue(self.errors(data))

    def test_route_registration_rejected(self):
        data = copy.deepcopy(self.record)
        data["state"]["route_registered"] = True
        self.assertTrue(self.errors(data))

    def test_adjudication_rejected(self):
        data = copy.deepcopy(self.record)
        data["state"]["may_adjudicate"] = True
        self.assertTrue(self.errors(data))

    def test_unknown_field_rejected(self):
        data = copy.deepcopy(self.record)
        data["authority_inflation"] = True
        self.assertTrue(self.errors(data))

    def test_historical_namespace_insertion_rejected(self):
        self.assertTrue(self.errors(legacy_file_exists=True))


if __name__ == "__main__":
    unittest.main()
