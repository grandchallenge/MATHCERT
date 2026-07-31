#!/usr/bin/env python3
"""Adversarial tests for expanded Formal Conjectures provenance."""
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

    def errors(self, record: dict, routes: dict) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            record_path = root / "record.json"
            routes_path = root / "routes.json"
            record_path.write_text(json.dumps(record), encoding="utf-8")
            routes_path.write_text(json.dumps(routes), encoding="utf-8")
            return provenance_errors(record_path, routes_path)

    def test_current_package_passes(self) -> None:
        self.assertEqual([], self.errors(self.record, self.routes))

    def test_archive_hash_drift_fails(self) -> None:
        record = copy.deepcopy(self.record)
        record["independent_replay"]["archive_sha256"] = "0" * 64
        self.assertTrue(any("archive_sha256" in e for e in self.errors(record, self.routes)))

    def test_missing_common_provider_artifact_fails(self) -> None:
        record = copy.deepcopy(self.record)
        record["common_provider_blobs"].pop(next(iter(record["common_provider_blobs"])))
        self.assertTrue(any("common provider" in e for e in self.errors(record, self.routes)))

    def test_odd_zeta_scope_omission_fails(self) -> None:
        record = copy.deepcopy(self.record)
        record["campaign_provider_blobs"]["OZ-001"].pop(
            "formal_sources/formal_conjectures/concordance/OZ-001-ZETA11.json"
        )
        self.assertTrue(any("campaign provider" in e or "odd-zeta" in e for e in self.errors(record, self.routes)))

    def test_non_route_inflation_fails(self) -> None:
        record = copy.deepcopy(self.record)
        record["scope_controls"]["explicit_non_routes"]["YM-001"] = "direct"
        self.assertTrue(any("non-route" in e for e in self.errors(record, self.routes)))

    def test_pilot_lane_contamination_fails(self) -> None:
        record = copy.deepcopy(self.record)
        record["scope_controls"]["pilot_lane"]["campaigns"].append("PNP-001")
        self.assertTrue(any("pilot" in e for e in self.errors(record, self.routes)))

    def test_manifest_identity_drift_fails(self) -> None:
        record = copy.deepcopy(self.record)
        record["solve_manifest_blobs"]["UC-001"] = "0" * 40
        self.assertTrue(any("manifest identities" in e for e in self.errors(record, self.routes)))

    def test_pending_packet_promotion_fails(self) -> None:
        record = copy.deepcopy(self.record)
        record["solve_handoff_packets"]["OZ-001"]["state"] = "ready"
        self.assertTrue(any("OZ-001 packet drift" in e for e in self.errors(record, self.routes)))

    def test_mathematical_proof_inflation_fails(self) -> None:
        record = copy.deepcopy(self.record)
        record["certification_result"]["mathematical_target_proved"] = True
        self.assertTrue(any("certification boundary" in e for e in self.errors(record, self.routes)))

    def test_ready_route_packet_drift_fails(self) -> None:
        routes = copy.deepcopy(self.routes)
        uc = next(r for r in routes["routes"] if r["campaign_id"] == "UC-001")
        uc["intake_packet"]["digest"] = "0" * 40
        self.assertTrue(any("UC-001 accepted packet drift" in e for e in self.errors(self.record, routes)))

    def test_pending_route_cannot_become_ready_fails(self) -> None:
        routes = copy.deepcopy(self.routes)
        oz = next(r for r in routes["routes"] if r["campaign_id"] == "OZ-001")
        oz["intake_status"] = "ready"
        self.assertTrue(any("OZ-001 route state drift" in e for e in self.errors(self.record, routes)))

    def test_cert_output_inflation_fails(self) -> None:
        routes = copy.deepcopy(self.routes)
        hc = next(r for r in routes["routes"] if r["campaign_id"] == "HC-001")
        hc["cert_output"] = {
            "repository": "grandchallenge/MATHCERT",
            "commit_sha": "1" * 40,
            "path": "dispositions/HC-001.json",
            "digest_algorithm": "git_blob_sha1",
            "digest": "2" * 40,
        }
        self.assertTrue(any("HC-001 adjudication inflation" in e for e in self.errors(self.record, routes)))


if __name__ == "__main__":
    unittest.main()