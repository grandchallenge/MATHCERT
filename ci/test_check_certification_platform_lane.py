from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from check_certification_platform_lane import (
    FULL_ESTATE_SCOPE,
    NO_LEAN_SCOPE,
    certification_scope,
    changed_paths_between,
    changed_paths_for_pull_request,
    evaluate,
    family_for_path,
    is_lean_material_path,
    load_manifest,
)


class CertificationPlatformLaneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = load_manifest()

    def test_chaidez_receiver_paths_are_platform_only(self) -> None:
        paths = [
            "ci/check_ledgers.py",
            "ci/validate_external_catalog_certification_intake.py",
            "ci/test_external_catalog_certification_intake.py",
            "schemas/external_catalog_certification_intake.schema.json",
            "governance/external_catalog_certification_intakes.json",
            "governance/external_catalog_solve_contract.json",
            "docs/EXTERNAL_CATALOG_CERTIFICATION_INTAKE.md",
            "contracts/chaidez_solve/ci/chaidez_contract.py",
            "contracts/chaidez_solve/ci/validate_external_catalog_promotion_dossiers.py",
            "contracts/chaidez_solve/schemas/external_catalog_promotion_dossier.schema.json",
            "contracts/chaidez_solve/schemas/external_catalog_promotion_registry.schema.json",
            "contracts/chaidez_solve/schemas/external_catalog_mathcert_handoff.schema.json",
            "contracts/chaidez_solve/schemas/mathcert_handoff.schema.json",
            "contracts/chaidez_solve/tests/fixtures/external_catalog_promotion/README.md",
            "contracts/chaidez_solve/tests/fixtures/external_catalog_promotion/forge/catalog/entries/canary.jsonl",
            "contracts/chaidez_solve/tests/fixtures/external_catalog_promotion/forge/catalog/relations/relations.json",
            "contracts/chaidez_solve/tests/fixtures/external_catalog_promotion/programme/governance/mathforge_external_source_imports.json",
            "contracts/chaidez_solve/tests/fixtures/external_catalog_promotion/solve/cert_handoffs/canary-generic.json",
            "contracts/chaidez_solve/tests/fixtures/external_catalog_promotion/solve/cert_handoffs/external_catalog/MS-CAT-HANDOFF-CANARY.json",
            "contracts/chaidez_solve/tests/fixtures/external_catalog_promotion/solve/governance/external_catalog_promotion_registry.json",
            "contracts/chaidez_solve/tests/fixtures/external_catalog_promotion/solve/promotions/external_catalog/MS-CAT-PROMOTION-CANARY.json",
            "contracts/chaidez_solve/tests/fixtures/external_catalog_promotion/solve/work_packages/CANARY/claim_ledger.json",
            "contracts/chaidez_solve/tests/fixtures/external_catalog_promotion/solve/work_packages/CANARY/dependency_dag.json",
            "contracts/chaidez_solve/tests/fixtures/external_catalog_promotion/solve/work_packages/CANARY/failure_and_negative_results.md",
            "contracts/chaidez_solve/tests/fixtures/external_catalog_promotion/solve/work_packages/CANARY/handoff_intent.json",
            "contracts/chaidez_solve/tests/fixtures/external_catalog_promotion/solve/work_packages/CANARY/lay_companion.md",
            "contracts/chaidez_solve/tests/fixtures/external_catalog_promotion/solve/work_packages/CANARY/next_executable_step.md",
            "contracts/chaidez_solve/tests/fixtures/external_catalog_promotion/solve/work_packages/CANARY/object_and_obstruction.md",
            "contracts/chaidez_solve/tests/fixtures/external_catalog_promotion/solve/work_packages/CANARY/proof_debt.json",
            "contracts/chaidez_solve/tests/fixtures/external_catalog_promotion/solve/work_packages/CANARY/proofs_and_computations.md",
            "contracts/chaidez_solve/tests/fixtures/external_catalog_promotion/solve/work_packages/CANARY/replay.md",
            "contracts/chaidez_solve/tests/fixtures/external_catalog_promotion/solve/work_packages/CANARY/result_status.md",
            "contracts/chaidez_solve/tests/fixtures/external_catalog_promotion/solve/work_packages/CANARY/review.md",
            "contracts/chaidez_solve/tests/fixtures/external_catalog_promotion/solve/work_packages/CANARY/status_audit.md",
            "contracts/chaidez_solve/tests/fixtures/external_catalog_promotion/solve/work_packages/CANARY/theorem_spine.json"
        ]
        self.assertTrue(set(paths) <= set(self.manifest["shared_platform_paths"]))
        for path in paths:
            with self.subTest(path=path):
                self.assertTrue(evaluate("family/canary", [path], self.manifest))
                self.assertEqual(evaluate("platform/certification/chaidez", [path], self.manifest), [])
                self.assertEqual(certification_scope("platform/certification/chaidez", [path], self.manifest), FULL_ESTATE_SCOPE)
        self.assertIn("governance/ci_control_registry.json", self.manifest["stateful_shared_validator_paths"])

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

    def test_family_branch_may_update_stateful_workflow_for_family_transition(self) -> None:
        errors = evaluate(
            "agent/otp-a-sphere-packing-output-execution-001",
            [".github/workflows/otp-a-sphere-packing-output-execution.yml"],
            self.manifest,
        )
        self.assertEqual(errors, [])
        self.assertEqual(
            certification_scope(
                "agent/otp-a-sphere-packing-output-execution-001",
                [".github/workflows/otp-a-sphere-packing-output-execution.yml"],
                self.manifest,
            ),
            "OTP-A-SPHERE-PACKING",
        )

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
                ".github/workflows/otp-a-sphere-packing-output-execution.yml",
                ".github/workflows/otp-h-gapcvp-cert-replay.yml",
                "ci/test_otp_finalize_family_replay_evidence.py",
                "governance/certification_platform_lane.json",
            ],
            self.manifest,
        )
        self.assertEqual(errors, [])

    def test_family_branch_may_register_bounded_route_state_consumers(self) -> None:
        errors = evaluate(
            "governance/certification/otp-i-ramsey-restricted-qualification-001",
            [
                "governance/certification_route_state_consumers.json",
                "ci/validate_otp_i_ramsey_certification.py",
                "certificates/formal_sources/MC-OTP-I-RAMSEY-QUAL-001.json",
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

    def test_manifest_classifies_platform_only_stateful_validators_and_workflows(self) -> None:
        shared = set(self.manifest["shared_platform_paths"])
        stateful = set(self.manifest["stateful_shared_validator_paths"])
        workflows = set(self.manifest["stateful_workflow_paths"])
        support = set(self.manifest["lane_support_paths"])
        self.assertIn(".github/workflows/ci.yml", shared)
        self.assertIn("ci/check_lean.sh", shared)
        self.assertIn("ci/check_lean.ps1", shared)
        self.assertIn("ci/otp_finalize_family_replay_evidence.py", shared)
        self.assertNotIn("ci/validate_certification_routes.py", shared)
        self.assertIn("ci/validate_certification_routes.py", stateful)
        self.assertIn("ci/validate_formal_target_certificates.py", stateful)
        self.assertIn(".github/workflows/otp-a-sphere-packing-output-execution.yml", workflows)
        self.assertIn(".github/workflows/otp-a-sphere-packing-cert-replay.yml", workflows)
        self.assertIn(".github/workflows/otp-j2-output-design.yml", workflows)
        self.assertIn(".github/workflows/otp-ehrhart-evidence-refresh.yml", workflows)
        self.assertIn(".github/workflows/otp-h-gapcvp-cert-replay.yml", workflows)
        self.assertIn(".github/workflows/otp-g-quantum-parallel-repetition-cert-replay.yml", workflows)
        self.assertIn(".github/workflows/otp-i-ramsey-cert-replay.yml", workflows)
        self.assertIn("ci/run_openai_ten_proofs_quantum_parallel_repetition_replay.sh", stateful)
        self.assertIn("ci/validate_otp_g_quantum_parallel_repetition_certification.py", stateful)
        self.assertIn("ci/test_otp_g_quantum_parallel_repetition_certification.py", stateful)
        self.assertIn("ci/run_openai_ten_proofs_ramsey_replay.sh", stateful)
        self.assertIn("ci/validate_otp_i_ramsey_certification.py", stateful)
        self.assertEqual(len(workflows), 35)
        self.assertIn("governance/certification_platform_lane.json", support)
        self.assertIn("ci/check_certification_platform_lane.py", support)

    def test_canonical_runners_keep_marker_free_otp_controls_full_estate_only(self) -> None:
        root = Path(__file__).resolve().parents[1]
        sh = (root / "ci/check_lean.sh").read_text(encoding="utf-8")
        ps1 = (root / "ci/check_lean.ps1").read_text(encoding="utf-8")

        sh_aggregate = '*openai_ten_proofs*|*openai-ten-proofs*) echo "FULL_ESTATE_ONLY" ;;'
        self.assertIn(sh_aggregate, sh)
        self.assertLess(sh.index('*otp_g_quantum_parallel_repetition*'), sh.index(sh_aggregate))
        self.assertLess(sh.index('*gapcvp*) echo "OTP-H-GAPCVP" ;;'), sh.index(sh_aggregate))
        self.assertLess(sh.index('*sphere_packing*|*sphere-packing*|*otp_a_*)'), sh.index(sh_aggregate))

        ps_aggregate = "if ($p -match 'openai[_-]ten[_-]proofs') { return 'FULL_ESTATE_ONLY' }"
        self.assertIn(ps_aggregate, ps1)
        self.assertLess(ps1.index("if ($p -match 'otp[_-]g[_-]quantum[_-]parallel[_-]repetition"), ps1.index(ps_aggregate))
        self.assertLess(ps1.index("if ($p -match 'gapcvp')"), ps1.index(ps_aggregate))
        self.assertLess(ps1.index("if ($p -match 'sphere[_-]packing|otp_a_')"), ps1.index(ps_aggregate))

        self.assertIn(
            'if [[ "$MC_CERT_SCOPE" != "FULL_ESTATE" && -n "$family" && "$family" != "$MC_CERT_SCOPE" ]]',
            sh,
        )
        self.assertIn(
            "if ($script:CertScope -ne 'FULL_ESTATE' -and $family -and $family -ne $script:CertScope)",
            ps1,
        )
        self.assertIn('MATHCERT_LEAN_SKIP=no_lean_material_change', sh)
        self.assertIn('MATHCERT_LEAN_SKIP=no_lean_material_change', ps1)
        self.assertIn("python3 ci/validate_otp_g_quantum_parallel_repetition_certification.py", sh)
        self.assertIn("python3 ci/test_otp_g_quantum_parallel_repetition_certification.py", sh)
        self.assertIn('Invoke-Control "ci/validate_otp_g_quantum_parallel_repetition_certification.py"', ps1)
        self.assertIn('Invoke-Control "ci/test_otp_g_quantum_parallel_repetition_certification.py"', ps1)
        self.assertIn("python3 ci/validate_otp_d_non_sofic_certification.py", sh)
        self.assertIn("python3 ci/test_otp_d_non_sofic_certification.py", sh)
        self.assertIn('Invoke-Control "ci/validate_otp_d_non_sofic_certification.py"', ps1)
        self.assertIn('Invoke-Control "ci/test_otp_d_non_sofic_certification.py"', ps1)
        self.assertIn("python3 ci/validate_otp_e_connes_rigidity_certification.py", sh)
        self.assertIn("python3 ci/test_otp_e_connes_rigidity_certification.py", sh)
        self.assertIn('Invoke-Control "ci/validate_otp_e_connes_rigidity_certification.py"', ps1)
        self.assertIn('Invoke-Control "ci/test_otp_e_connes_rigidity_certification.py"', ps1)

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

    def test_g_only_transition_gets_exact_family_scope(self) -> None:
        scope = certification_scope(
            "governance/certification/otp-g-quantum-parallel-repetition-001",
            [
                "governance/certification_routes.json",
                "governance/ci_control_registry.json",
                "ci/validate_certification_routes.py",
                "ci/validate_formal_target_certificates.py",
                "ci/validate_otp_g_quantum_parallel_repetition_certification.py",
                "certificates/formal_sources/MC-OTP-G-QUANTUM-PARALLEL-REPETITION-001.json",
                "governance/result_family_output_contracts/OTP-G-QUANTUM-PARALLEL-REPETITION.json",
                ".github/workflows/otp-g-quantum-parallel-repetition-cert-replay.yml",
            ],
            self.manifest,
        )
        self.assertEqual(scope, "OTP-G-QUANTUM-PARALLEL-REPETITION")

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

    def test_non_lean_unknown_change_keeps_controls_without_lean(self) -> None:
        scope = certification_scope(
            "agent/unknown-change",
            ["docs/architecture.md"],
            self.manifest,
        )
        self.assertEqual(scope, NO_LEAN_SCOPE)

    def test_unknown_lean_change_fails_closed_to_full_estate(self) -> None:
        scope = certification_scope(
            "agent/unknown-lean-change",
            ["MathCert/NewDomain/Unclassified.lean"],
            self.manifest,
        )
        self.assertEqual(scope, FULL_ESTATE_SCOPE)
        self.assertTrue(is_lean_material_path("MathCert/NewDomain/Unclassified.lean"))

    def test_platform_change_always_runs_full_estate(self) -> None:
        scope = certification_scope(
            "platform/certification/example-repair",
            ["ci/check_lean.sh"],
            self.manifest,
        )
        self.assertEqual(scope, FULL_ESTATE_SCOPE)

    def test_global_route_only_change_keeps_controls_without_lean(self) -> None:
        scope = certification_scope(
            "agent/route-only",
            ["governance/certification_routes.json"],
            self.manifest,
        )
        self.assertEqual(scope, NO_LEAN_SCOPE)

    def test_ci_control_registry_only_change_keeps_controls_without_lean(self) -> None:
        scope = certification_scope(
            "agent/ci-registry-only",
            ["governance/ci_control_registry.json"],
            self.manifest,
        )
        self.assertEqual(scope, NO_LEAN_SCOPE)

    def test_rm_dio_transition_does_not_select_unrelated_lean(self) -> None:
        scope = certification_scope(
            "certification/rm-dio-004-level2",
            [
                "certificates/exact/RM-DIO-004-Y-ABS-1000000.json",
                "ci/test_audit_certificate_coverage.py",
                "claim_ledger_rm_dio_004.yaml",
                "docs/RM_DIO_004_BOUNDED_CERTIFICATE.md",
                "governance/ci_control_registry.json",
            ],
            self.manifest,
        )
        self.assertEqual(scope, NO_LEAN_SCOPE)

    def test_push_transition_diff_includes_deletions(self) -> None:
        with patch("check_certification_platform_lane.subprocess.run"), patch(
            "check_certification_platform_lane.subprocess.check_output",
            return_value="governance/ci_control_registry.json\n",
        ) as check_output:
            paths = changed_paths_between("before-sha", "after-sha")
        self.assertEqual(paths, ["governance/ci_control_registry.json"])
        command = check_output.call_args.args[0]
        self.assertEqual(command[-2:], ["before-sha", "after-sha"])
        self.assertIn("--diff-filter=ACMRD", command)

    def test_family_workflows_do_not_trigger_on_shared_registry_edits(self) -> None:
        root = Path(__file__).resolve().parents[1]
        governed = set(self.manifest["stateful_workflow_paths"])
        offenders = [
            relative
            for relative in sorted(governed)
            if '"governance/ci_control_registry.json"'
            in (root / relative).read_text(encoding="utf-8")
        ]
        self.assertEqual(offenders, [])

    def test_required_cert_context_skips_lean_bootstrap_for_no_lean_scope(self) -> None:
        root = Path(__file__).resolve().parents[1]
        workflow = (root / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        self.assertIn("id: scope", workflow)
        self.assertIn("certification_scope != 'NO_LEAN'", workflow)
        self.assertIn("MC_CERT_SCOPE: ${{ steps.scope.outputs.certification_scope }}", workflow)

if __name__ == "__main__":
    unittest.main()
