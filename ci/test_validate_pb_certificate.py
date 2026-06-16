from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from validate_pb_certificate import CertificateError, validate_artifact_dir


WEIGHTS = [[10, 6, 5, 4, 3], [12, 17, 11, 10, 9], [8, 7, 13, 6, 5], [16, 15, 14, 21, 13], [18, 17, 16, 15, 24]]


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_fixture(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    terms = [f"+{WEIGHTS[i][j]} x_{i}_{j}" for i in range(5) for j in range(5)]
    lines = ["* #variable= 25 #constraint= 10", "max: " + " ".join(terms) + " ;"]
    (out / "instance.opb").write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_json(out / "primal_witness.json", {"selected_cols": [0, 1, 2, 3, 4], "objective": 85})
    write_json(out / "pb_dual_certificate.json", {"row_duals": [10, 17, 13, 21, 24], "col_duals": [0, 0, 0, 0, 0], "upper_bound": 85})
    write_json(out / "result_card.json", {"claim": {"problem": "max_weight_assignment_pb", "optimum": 85}})


class PbCertificateTests(unittest.TestCase):
    def test_valid_fixture_certificate_replays(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "fixture006"
            write_fixture(out)
            result = validate_artifact_dir(out)
            self.assertEqual("checked", result["status"])
            self.assertEqual(85, result["optimum"])

    def test_rejects_non_permutation_witness(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "fixture006"
            write_fixture(out)
            write_json(out / "primal_witness.json", {"selected_cols": [0, 0, 2, 3, 4], "objective": 85})
            with self.assertRaises(CertificateError):
                validate_artifact_dir(out)

    def test_rejects_insufficient_dual_bound(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "fixture006"
            write_fixture(out)
            write_json(out / "pb_dual_certificate.json", {"row_duals": [0, 0, 0, 0, 0], "col_duals": [0, 0, 0, 0, 0], "upper_bound": 0})
            with self.assertRaises(CertificateError):
                validate_artifact_dir(out)


if __name__ == "__main__":
    unittest.main()
