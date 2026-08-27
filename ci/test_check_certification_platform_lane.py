from __future__ import annotations

import unittest
from unittest.mock import patch

from check_certification_platform_lane import (
    FULL_ESTATE_SCOPE,
    certification_scope,
    changed_paths_for_pull_request,
    evaluate,
    family_for_path,
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

    def test_a_only_transition_gets_exact_family_scope(self) -> None:
        scope = certification_scope(
            "agent/otp-a-sphere-packing-output-execution-001",
            [
                "governance/certification_routes.json",
                "governance/ci_control_registry.json",
                "ci/validate_certification_routes.py",
                "ci/validate_formal_target_certificates.py",
                "certificates/formal_sources/MC-OTP-A-SPHERE-PACKING-001.json",
                "governance/result_family_output_contracts/OTP-A-SPHERE-PACKING.json",
                "ci/otp_a_sphere_packing_output_contract.py",
                ".github/workflows/otp-a-sphere-packing-output-execution.yml",
            ],
            self.manifest,
        )
        self.assertEqual(scope, "OTP-A-SPHERE-PACKING")

    def test_h_transition_with_central_registries_gets_exact_family_scope(self) -> None:
        scope = certification_scope(
            "governance/otp-h-gapcvp-cert-route-registration-001",
            [
                "governance/certification_routes.json",
                "governance/ci_control_registry.json",
                "ci/validate_certification_routes.py",
                "ci/test_validate_certification_routes.py",
                "ci/validate_openai_ten_proofs_gapcvp_route_registration.py",
                "ci/test_openai_ten_proofs_gapcvp_route_registration.py",
                "ci/validate_openai_ten_proofs_gapcvp_certification_work_package.py",
                "governance/pre_route_candidates/OPENAI_TEN_PROOFS_H_GAPCVP_ROUTE_REGISTRATION.json",
                "schemas/openai_ten_proofs_gapcvp_route_registration.schema.json",
            ],
            self.manifest,
        )
        self.assertEqual(scope, "OTP-H-GAPCVP")

    def test_a_transition_does_not_classify_foreign_family_paths_as_a(self) -> None:
        self.assertEqual(family_for_path("ci/validate_openai_ten_proofs_binary_codes_intake_successor.py"), "OTP-B1-BINARY-CODES")
        self.assertEqual(family_for_path("ci/validate_openai_ten_proofs_spherical_codes_intake_successor.py"), "OTP-B2-SPHERICAL-CODES")
        self.assertEqual(family_for_path("ci/validate_openai_ten_proofs_gapcvp_intake_successor.py"), "OTP-H-GAPCVP")
        self.assertEqual(family_for_path("ci/validate_otp_permanent_circuit_certification.py"), "OTP-C-PERMANENT")
        self.assertEqual(family_for_path("ci/validate_otp_j2_adjudication.py"), "OTP-J2-TWO-DEGENERATE")

    def test_multi_family_change_fails_closed_to_full_estate(self) -> None:
        scope = certification_scope(
            "agent/mixed-change",
            [
                "governance/ci_control_registry.json",
                "ci/otp_a_sphere_packing_output_contract.py",
                "ci/validate_openai_ten_proofs_binary_codes_intake_successor.py",
            ],
            self.manifest,
        )
        self.assertEqual(scope, FULL_ESTATE_SCOPE)

    def test_unknown_change_fails_closed_to_full_estate(self) -> None:
        scope = certification_scope(
            "agent/unknown-change",
            ["docs/architecture.md"],
            self.manifest,
        )
        self.assertEqual(scope, FULL_ESTATE_SCOPE)

    def test_platform_change_always_runs_full_estate(self) -> None:
        scope = certification_scope(
            "platform/certification/example-repair",
            ["ci/check_lean.sh"],
            self.manifest,
        )
        self.assertEqual(scope, FULL_ESTATE_SCOPE)

    def test_global_route_only_change_fails_closed_to_full_estate(self) -> None:
        scope = certification_scope(
            "agent/route-only",
            ["governance/certification_routes.json"],
            self.manifest,
        )
        self.assertEqual(scope, FULL_ESTATE_SCOPE)

    def test_ci_control_registry_only_change_fails_closed_to_full_estate(self) -> None:
        scope = certification_scope(
            "agent/ci-registry-only",
            ["governance/ci_control_registry.json"],
            self.manifest,
        )
        self.assertEqual(scope, FULL_ESTATE_SCOPE)


if __name__ == "__main__":
    unittest.main()
