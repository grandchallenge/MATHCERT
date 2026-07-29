from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import validate_certification_routes as module


class CertificationRouteTests(unittest.TestCase):
    def load_registry(self) -> dict:
        return module.load_json(module.REGISTRY_PATH)

    def write_registry(self, payload: dict) -> Path:
        handle = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        with handle:
            json.dump(payload, handle, indent=2)
            handle.write("\n")
        return Path(handle.name)

    def errors(self, payload: dict) -> list[str]:
        path = self.write_registry(payload)
        try:
            return module.route_errors(path)
        finally:
            path.unlink(missing_ok=True)

    def test_current_registry_passes(self) -> None:
        self.assertEqual([], module.route_errors())

    def test_missing_campaign_fails(self) -> None:
        data = self.load_registry()
        data["routes"] = data["routes"][:-1]
        self.assertTrue(any("uncovered" in error for error in self.errors(data)))

    def test_wrong_hodge_tracker_fails(self) -> None:
        data = self.load_registry()
        hodge = next(route for route in data["routes"] if route["campaign_id"] == "HC-001")
        hodge["tracker_issue"] = "https://github.com/grandchallenge/MATHCERT/issues/24"
        self.assertTrue(any("tracker drift" in error for error in self.errors(data)))

    def test_ready_without_packet_fails(self) -> None:
        data = self.load_registry()
        data["routes"][0]["intake_status"] = "ready"
        self.assertTrue(any("lacks intake packet" in error for error in self.errors(data)))

    def test_submitted_is_not_an_adjudication(self) -> None:
        data = self.load_registry()
        route = data["routes"][0]
        route["intake_status"] = "submitted"
        route["intake_packet"] = {
            "repository": "grandchallenge/MATHSOLVE",
            "commit_sha": "1" * 40,
            "path": "cert_handoffs/UC-001.json",
            "digest_algorithm": "git_blob_sha1",
            "digest": "2" * 40,
        }
        route["cert_output"] = {
            "repository": "grandchallenge/MATHCERT",
            "commit_sha": "3" * 40,
            "path": "dispositions/UC-001.json",
            "digest_algorithm": "git_blob_sha1",
            "digest": "4" * 40,
        }
        self.assertTrue(any("intake-only" in error for error in self.errors(data)))

    def test_adjudication_requires_output(self) -> None:
        data = self.load_registry()
        route = data["routes"][0]
        route["intake_status"] = "qualified"
        route["intake_packet"] = {
            "repository": "grandchallenge/MATHSOLVE",
            "commit_sha": "1" * 40,
            "path": "cert_handoffs/UC-001.json",
            "digest_algorithm": "git_blob_sha1",
            "digest": "2" * 40,
        }
        self.assertTrue(any("lacks MATHCERT output" in error for error in self.errors(data)))

    def test_commit_cannot_substitute_for_artifact_digest(self) -> None:
        data = self.load_registry()
        source = data["routes"][0]["source_manifest"]
        source["digest"] = source["commit_sha"]
        self.assertTrue(any("must not be substituted" in error for error in self.errors(data)))

    def test_duplicate_claim_fails(self) -> None:
        data = self.load_registry()
        data["routes"][1]["target_claim_ids"].append("UC-WP02-L002")
        self.assertTrue(any("duplicate target claim" in error for error in self.errors(data)))


if __name__ == "__main__":
    unittest.main()
