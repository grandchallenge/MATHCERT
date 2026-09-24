import copy
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from ci.validate_external_catalog_certification_intake import (
    BYTES, INTAKES, VENDOR, source_contract_errors, validate_intake, validate_registry,
)


def commit(root):
    BYTES.git(root, "add", "--all")
    env = {**os.environ, "GIT_AUTHOR_NAME": "Synthetic Canary", "GIT_COMMITTER_NAME": "Synthetic Canary",
           "GIT_AUTHOR_EMAIL": "canary@example.invalid", "GIT_COMMITTER_EMAIL": "canary@example.invalid",
           "GIT_AUTHOR_DATE": "2000-01-01T00:00:00+0000", "GIT_COMMITTER_DATE": "2000-01-01T00:00:00+0000"}
    subprocess.run(["git", "-C", str(root), "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-qm", "Non-authoritative fixture"], env=env, check=True)
    BYTES.git(root, "update-ref", "refs/remotes/origin/main", "HEAD")
    return BYTES.git(root, "rev-parse", "HEAD").decode().strip()


def reference(root, path):
    return {"path": path, **BYTES.hashes((root / path).read_bytes())}


def make_canary(parent):
    fixture = VENDOR / "tests/fixtures/external_catalog_promotion"
    roots = {}
    for name, repo in (("forge", "MATHFORGE"), ("programme", "MATH-PROGRAMME"), ("solve", "MATHSOLVE")):
        root = Path(parent) / name
        root.mkdir()
        BYTES.git(root, "init", "-q", "--initial-branch=main")
        BYTES.git(root, "config", "core.autocrlf", "false")
        if name == "solve":
            shutil.copytree(fixture / name / "work_packages", root / "work_packages")
            commit(root)
        shutil.copytree(fixture / name, root, dirs_exist_ok=True)
        commit(root)
        roots["grandchallenge/" + repo] = root
    solve = roots["grandchallenge/MATHSOLVE"]
    path = "cert_handoffs/external_catalog/MS-CAT-HANDOFF-CANARY.json"
    handoff = json.loads((solve / path).read_text())
    record = {k: v for k, v in handoff.items() if k not in ("handoff_id", "generic_handoff")}
    record.update(intake_id="MC-CAT-INTAKE-CANARY", solve_repository="grandchallenge/MATHSOLVE",
                  solve_commit=BYTES.git(solve, "rev-parse", "HEAD").decode().strip(), supplemental_handoff=reference(solve, path),
                  disposition="HOLD_FOR_PROOF_DEBT", direct_catalog_intake=False, certification_inferred=False)
    routes = {"routes": [{"route_id": handoff["certification_route_id"], "campaign_id": handoff["catalog_source"]["campaign_id"],
                           "target_claim_ids": [handoff["selected_claim"]["claim_id"]]}]}
    return record, roots, routes


class ExternalCatalogReceivingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="cert-chaidez-canary.")
        self.addCleanup(self.temp.cleanup)
        self.record, self.roots, self.routes = make_canary(self.temp.name)

    def validate(self, record=None, routes=None):
        return validate_intake(record or self.record, self.roots, canary=True, routes=routes or self.routes)

    def test_full_canary_reaches_receiving_gate_not_certification(self):
        self.assertEqual(self.validate(), [])
        self.assertEqual(self.record["disposition"], "HOLD_FOR_PROOF_DEBT")
        self.assertEqual(self.record["independent_verification"]["disposition"], "REQUIRED_PENDING")

    def test_zero_production_and_exact_vendored_source(self):
        self.assertEqual(source_contract_errors(), [])
        self.assertEqual(validate_registry(), [])
        registry = json.loads(INTAKES.read_text())
        self.assertEqual((registry["intake_count"], registry["intakes"]), (0, []))

    def test_every_required_receiving_member(self):
        for key in self.record:
            record = copy.deepcopy(self.record)
            del record[key]
            with self.subTest(key=key):
                self.assertTrue(self.validate(record))

    def test_protected_commit_blob_and_sha256_are_required(self):
        for commit_value in ("main", "HEAD", "0" * 40):
            record = copy.deepcopy(self.record)
            record["solve_commit"] = commit_value
            self.assertTrue(self.validate(record))
        for field in ("promotion_registry", "dossier", "supplemental_handoff"):
            for digest, length in (("git_blob_sha1", 40), ("sha256", 64)):
                record = copy.deepcopy(self.record)
                record[field][digest] = "0" * length
                self.assertTrue(self.validate(record), (field, digest))
        record = copy.deepcopy(self.record)
        record["dossier"]["path"] = "../outside"
        self.assertTrue(self.validate(record))

    def test_direct_catalog_and_canary_promotion_are_rejected(self):
        self.assertTrue(self.validate(self.record["catalog_source"]))
        record = copy.deepcopy(self.record)
        record["direct_catalog_intake"] = True
        self.assertTrue(self.validate(record))
        self.assertTrue(validate_intake(self.record, self.roots))
        record["record_class"] = "PRODUCTION"
        self.assertTrue(validate_intake(record, self.roots, routes=self.routes))

    def test_claim_inflation_debt_omission_and_trust_disagreement(self):
        cases = [
            lambda r: r["selected_claim"].update(statement="All mathematical conjectures are proved"),
            lambda r: r.update(proof_debt_ids=[]),
            lambda r: r["selected_claim"].update(proof_debt_ids=[]),
            lambda r: r["trust_quartet"]["WHAT_REMAINS_OPEN"].update(debt_ids=[]),
            lambda r: r["trust_quartet"]["WHAT_IS_PROVED"].update(claim_ids=[r["selected_claim"]["claim_id"]]),
            lambda r: r.update(support_route_class="CONTINUUM_PROOF"),
            lambda r: r.update(theorem_spine_node="OTHER"),
            lambda r: r.update(global_theorem_spine_id="OTHER"),
            lambda r: r.update(disposition="AWAITING_INDEPENDENT_VERIFICATION"),
            lambda r: r.update(local_replay_evidence=[]),
        ]
        for change in cases:
            record = copy.deepcopy(self.record)
            change(record)
            self.assertTrue(self.validate(record))

    def test_route_must_cover_exact_claim_and_campaign(self):
        for field, value in (("route_id", "MC-ROUTE-OTHER"), ("campaign_id", "OTHER"), ("target_claim_ids", ["OTHER"])):
            routes = copy.deepcopy(self.routes)
            routes["routes"][0][field] = value
            self.assertTrue(self.validate(routes=routes))
        routes = copy.deepcopy(self.routes)
        routes["routes"] *= 2
        self.assertTrue(self.validate(routes=routes))

    def test_independent_verification_is_not_inferred(self):
        for state in ("CERTIFIED", "APPROVED", "CI_PASSED", "ASSURANCE_ACCEPTED", "EVIDENCE_SUBMITTED"):
            record = copy.deepcopy(self.record)
            record["independent_verification"]["disposition"] = state
            self.assertTrue(self.validate(record))
        record = copy.deepcopy(self.record)
        record["certification_inferred"] = True
        self.assertTrue(self.validate(record))
        for inferred in ("catalog_tier_is_certificate", "dossier_completion_is_certificate", "replay_is_certificate", "formal_annotation_is_certificate", "ci_is_certificate"):
            record = copy.deepcopy(self.record)
            record[inferred] = True
            self.assertTrue(self.validate(record))

    def test_working_file_drift_cannot_replace_protected_evidence(self):
        solve = self.roots["grandchallenge/MATHSOLVE"]
        path = self.record["local_replay_evidence"][0]["path"]
        (solve / path).write_text("replacement evidence\n")
        BYTES.git(solve, "add", "--all")
        self.assertTrue(self.validate())

    def test_unprotected_solve_commit_rejected(self):
        solve = self.roots["grandchallenge/MATHSOLVE"]
        BYTES.git(solve, "update-ref", "refs/remotes/origin/main", "HEAD^")
        self.assertTrue(self.validate())


if __name__ == "__main__":
    unittest.main()
