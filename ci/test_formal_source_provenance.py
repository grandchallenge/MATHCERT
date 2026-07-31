#!/usr/bin/env python3
"""Adversarial tests for immutable expanded Formal Conjectures provenance."""
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from validate_formal_source_provenance import RECORD_PATH, ROUTES_PATH, provenance_errors


class FormalSourceProvenanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.record = json.loads(RECORD_PATH.read_text(encoding="utf-8"))
        self.routes = json.loads(ROUTES_PATH.read_text(encoding="utf-8"))

    def errors(self, record: dict, routes: dict | None = None) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            record_path = root / "record.json"
            routes_path = root / "routes.json"
            record_path.write_text(json.dumps(record), encoding="utf-8")
            routes_path.write_text(json.dumps(routes or self.routes), encoding="utf-8")
            return provenance_errors(record_path, routes_path)

    def test_current_historical_record_passes(self) -> None:
        self.assertEqual([], self.errors(self.record))

    def test_current_route_changes_do_not_rewrite_history(self) -> None:
        routes = copy.deepcopy(self.routes)
        routes["routes"] = []
        self.assertEqual([], self.errors(self.record, routes))

    def test_archive_hash_drift_fails(self) -> None:
        record = copy.deepcopy(self.record)
        record["independent_replay"]["archive_sha256"] = "0" * 64
        self.assertTrue(any("archive_sha256" in e for e in self.errors(record)))

    def test_missing_common_provider_artifact_fails(self) -> None:
        record = copy.deepcopy(self.record)
        record["common_provider_blobs"].pop(next(iter(record["common_provider_blobs"])))
        self.assertTrue(any("common provider" in e for e in self.errors(record)))

    def test_odd_zeta_scope_omission_fails(self) -> None:
        record = copy.deepcopy(self.record)
        record["campaign_provider_blobs"]["OZ-001"].pop(
            "formal_sources/formal_conjectures/concordance/OZ-001-ZETA11.json"
        )
        self.assertTrue(any("campaign provider" in e or "odd-zeta" in e for e in self.errors(record)))

    def test_non_route_inflation_fails(self) -> None:
        record = copy.deepcopy(self.record)
        record["scope_controls"]["explicit_non_routes"]["YM-001"] = "direct"
        self.assertTrue(any("non-route" in e for e in self.errors(record)))

    def test_pilot_lane_contamination_fails(self) -> None:
        record = copy.deepcopy(self.record)
        record["scope_controls"]["pilot_lane"]["campaigns"].append("PNP-001")
        self.assertTrue(any("pilot" in e for e in self.errors(record)))

    def test_pilot_lane_historical_status_drift_fails(self) -> None:
        record = copy.deepcopy(self.record)
        record["scope_controls"]["pilot_lane"]["status"] = "qualified"
        self.assertTrue(any("pilot" in e for e in self.errors(record)))

    def test_manifest_identity_drift_fails(self) -> None:
        record = copy.deepcopy(self.record)
        record["solve_manifest_blobs"]["UC-001"] = "0" * 40
        self.assertTrue(any("manifest identities" in e for e in self.errors(record)))

    def test_pending_packet_promotion_fails(self) -> None:
        record = copy.deepcopy(self.record)
        record["solve_handoff_packets"]["OZ-001"]["state"] = "ready"
        self.assertTrue(any("OZ-001 packet drift" in e for e in self.errors(record)))

    def test_target_elaboration_backdated_fails(self) -> None:
        record = copy.deepcopy(self.record)
        record["certification_result"]["target_declaration_elaborated"] = True
        self.assertTrue(any("certification boundary" in e for e in self.errors(record)))

    def test_adjudication_backdated_fails(self) -> None:
        record = copy.deepcopy(self.record)
        record["certification_result"]["adjudicated_outputs"] = 2
        self.assertTrue(any("certification boundary" in e for e in self.errors(record)))

    def test_mathematical_proof_inflation_fails(self) -> None:
        record = copy.deepcopy(self.record)
        record["certification_result"]["mathematical_target_proved"] = True
        self.assertTrue(any("certification boundary" in e for e in self.errors(record)))


if __name__ == "__main__":
    unittest.main()
