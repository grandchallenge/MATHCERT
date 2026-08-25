from __future__ import annotations

import unittest
from unittest.mock import patch

from check_certification_platform_lane import (
    changed_paths_for_pull_request,
    evaluate,
    load_manifest,
)


class CertificationPlatformLaneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = load_manifest()

    def test_family_branch_cannot_modify_shared_finalizer(self) -> None:
        errors = evaluate(
            "agent/otp-h-gapcvp-replay-evidence-001",
            ["ci/otp_finalize_family_replay_evidence.py"],
            self.manifest,
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("platform/certification/", errors[0])

    def test_family_branch_cannot_modify_lane_manifest_or_guard(self) -> None:
        errors = evaluate(
            "agent/otp-h-gapcvp-replay-evidence-001",
            [
                "governance/certification_platform_lane.json",
                "ci/check_certification_platform_lane.py",
            ],
            self.manifest,
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("certification-platform files", errors[0])

    def test_family_branch_can_modify_family_specific_runtime(self) -> None:
        errors = evaluate(
            "agent/otp-h-gapcvp-replay-evidence-001",
            ["ci/otp_h_gapcvp_replay_evidence.py"],
            self.manifest,
        )
        self.assertEqual(errors, [])

    def test_family_branch_may_extend_stateful_validator_for_family_transition(self) -> None:
        errors = evaluate(
            "agent/otp-a-sphere-packing-output-execution-001",
            [
                "ci/validate_certification_routes.py",
                "ci/test_validate_certification_routes.py",
                "ci/validate_formal_target_certificates.py",
            ],
            self.manifest,
        )
        self.assertEqual(errors, [])

    def test_non_platform_branch_cannot_modify_canonical_ci(self) -> None:
        errors = evaluate(
            "agent/some-maintenance-branch",
            ["ci/check_lean.sh"],
            self.manifest,
        )
        self.assertEqual(len(errors), 1)

    def test_deleted_platform_path_is_included_in_pull_request_diff(self) -> None:
        with patch("check_certification_platform_lane.subprocess.run"), patch(
            "check_certification_platform_lane.subprocess.check_output",
            return_value="ci/check_lean.sh\n",
        ) as check_output:
            paths = changed_paths_for_pull_request("main")
        self.assertEqual(paths, ["ci/check_lean.sh"])
        command = check_output.call_args.args[0]
        self.assertIn("--diff-filter=ACMRD", command)
        self.assertEqual(
            len(
                evaluate(
                    "agent/otp-h-gapcvp-replay-evidence-001",
                    paths,
                    self.manifest,
                )
            ),
            1,
        )

    def test_platform_branch_accepts_declared_platform_paths(self) -> None:
        errors = evaluate(
            "platform/certification/example-repair",
            [
                "ci/otp_finalize_family_replay_evidence.py",
                "ci/validate_certification_routes.py",
                "ci/test_otp_finalize_family_replay_evidence.py",
                "governance/certification_platform_lane.json",
            ],
            self.manifest,
        )
        self.assertEqual(errors, [])

    def test_platform_branch_rejects_family_payload(self) -> None:
        errors = evaluate(
            "platform/certification/example-repair",
            [
                "ci/otp_finalize_family_replay_evidence.py",
                "certificates/formal_sources/MC-OTP-H-GAPCVP-QUAL-001.json",
            ],
            self.manifest,
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("non-platform payload", errors[0])

    def test_manifest_classifies_platform_only_and_stateful_shared_files(self) -> None:
        shared = set(self.manifest["shared_platform_paths"])
        stateful = set(self.manifest["stateful_shared_validator_paths"])
        support = set(self.manifest["lane_support_paths"])
        self.assertIn(".github/workflows/ci.yml", shared)
        self.assertIn("ci/check_lean.sh", shared)
        self.assertIn("ci/check_lean.ps1", shared)
        self.assertIn("ci/otp_finalize_family_replay_evidence.py", shared)
        self.assertNotIn("ci/validate_certification_routes.py", shared)
        self.assertIn("ci/validate_certification_routes.py", stateful)
        self.assertIn("ci/validate_formal_target_certificates.py", stateful)
        self.assertIn("governance/certification_platform_lane.json", support)
        self.assertIn("ci/check_certification_platform_lane.py", support)


if __name__ == "__main__":
    unittest.main()
