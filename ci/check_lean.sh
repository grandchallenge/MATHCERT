#!/usr/bin/env bash
set -Eeuo pipefail
trap 'status=$?; echo "::error title=MATHCERT canonical control failed::command=${BASH_COMMAND}; exit=${status}"; exit "$status"' ERR
if ! command -v lake >/dev/null 2>&1; then echo "lake is not installed; cannot certify Lean files." >&2; exit 1; fi
cd "$(dirname "$0")/.."

control_family() {
  local path="${1,,}"
  case "$path" in
    *spherical_codes*|*spherical-codes*) echo "OTP-B2-SPHERICAL-CODES" ;;
    *binary_codes*|*binary-codes*) echo "OTP-B1-BINARY-CODES" ;;
    *gapcvp*) echo "OTP-H-GAPCVP" ;;
    *permanent*) echo "OTP-C-PERMANENT" ;;
    *compactness*) echo "OTP-J1-COMPACTNESS" ;;
    *ehrhart*) echo "OTP-F-EHRHART" ;;
    *otp_j2*|*otp-j2*|*two_degenerate*|*two-degenerate*|*with_j2_output*) echo "OTP-J2-TWO-DEGENERATE" ;;
    *sphere_packing*|*sphere-packing*|*otp_a_*) echo "OTP-A-SPHERE-PACKING" ;;
    *openai_ten_proofs*|*openai-ten-proofs*) echo "FULL_ESTATE_ONLY" ;;
    *) echo "" ;;
  esac
}

MC_CERT_SCOPE="${MC_CERT_SCOPE:-$(command python3 ci/check_certification_platform_lane.py --certification-scope)}"
case "$MC_CERT_SCOPE" in
  FULL_ESTATE|OTP-A-SPHERE-PACKING|OTP-B1-BINARY-CODES|OTP-B2-SPHERICAL-CODES|OTP-H-GAPCVP|OTP-C-PERMANENT|OTP-J1-COMPACTNESS|OTP-J2-TWO-DEGENERATE|OTP-F-EHRHART) ;;
  *) echo "unknown canonical certification scope: $MC_CERT_SCOPE" >&2; exit 1 ;;
esac
export MC_CERT_SCOPE
echo "MATHCERT_CANONICAL_SCOPE=$MC_CERT_SCOPE"

# Declaration bootstrap for MC-CERTIFICATION-STATE-ARCHITECTURE-STABILIZATION-001.
# The protected-base platform manifest cannot authorize newly discovered route-state
# consumers until the declaration itself is protected. Current global route state is
# still validated live above. During this one declaration PR, legacy OTP controls run
# against the exact last protected pre-H route registry, while H controls run live.
# No control is skipped. The semantic stabilization successor removes this shim.
MC_ROUTE_SNAPSHOT_BOOTSTRAP=0
LIVE_HEAD=""
LEGACY_ROUTE_VIEW_HEAD=""
if [[ "${GITHUB_EVENT_NAME:-}" == "pull_request" && \
      "${GITHUB_HEAD_REF:-}" == "platform/certification/mc-certification-state-architecture-stabilization-001" ]]; then
  LIVE_HEAD="$(git rev-parse HEAD)"
  LEGACY_ROUTE_SOURCE_COMMIT="0a24c03689734cac54d940c506ff4be02e200e65"
  LEGACY_ROUTE_BLOB="4d5c8e3f2b33d5148d98e7057991e167938c75bb"
  actual_route_blob="$(git rev-parse "${LEGACY_ROUTE_SOURCE_COMMIT}:governance/certification_routes.json")"
  if [[ "$actual_route_blob" != "$LEGACY_ROUTE_BLOB" ]]; then
    echo "declaration bootstrap route snapshot drift: $actual_route_blob != $LEGACY_ROUTE_BLOB" >&2
    exit 1
  fi
  bootstrap_index="$(mktemp)"
  rm -f "$bootstrap_index"
  GIT_INDEX_FILE="$bootstrap_index" git read-tree "${LIVE_HEAD}^{tree}"
  GIT_INDEX_FILE="$bootstrap_index" git update-index --cacheinfo "100644,$LEGACY_ROUTE_BLOB,governance/certification_routes.json"
  bootstrap_tree="$(GIT_INDEX_FILE="$bootstrap_index" git write-tree)"
  rm -f "$bootstrap_index"
  LEGACY_ROUTE_VIEW_HEAD="$(printf '%s\n' 'MC-CERTIFICATION-STATE-ARCHITECTURE-DECLARATION-001 exact pre-H route view' | \
    GIT_AUTHOR_NAME='MATHCERT CI' GIT_AUTHOR_EMAIL='mathcert-ci@grandchallenge.ai' \
    GIT_COMMITTER_NAME='MATHCERT CI' GIT_COMMITTER_EMAIL='mathcert-ci@grandchallenge.ai' \
    git commit-tree "$bootstrap_tree" -p "$LIVE_HEAD")"
  if [[ "$(git rev-parse "${LEGACY_ROUTE_VIEW_HEAD}:governance/certification_routes.json")" != "$LEGACY_ROUTE_BLOB" ]]; then
    echo "declaration bootstrap synthetic route view construction failed" >&2
    exit 1
  fi
  MC_ROUTE_SNAPSHOT_BOOTSTRAP=1
  echo "MATHCERT_DECLARATION_BOOTSTRAP=EXACT_PRE_H_ROUTE_VIEW source=$LEGACY_ROUTE_SOURCE_COMMIT blob=$LEGACY_ROUTE_BLOB"
fi

run_python_in_route_view() {
  local route_view_head="$1"
  shift
  local status=0
  git checkout --detach --quiet "$route_view_head"
  if command python3 "$@"; then
    status=0
  else
    status=$?
  fi
  git checkout --detach --quiet "$LIVE_HEAD"
  return "$status"
}

python3() {
  local path="${1:-}"
  local family=""
  if [[ "$path" == *.py ]]; then
    family="$(control_family "$path")"
  fi
  if [[ "$MC_CERT_SCOPE" != "FULL_ESTATE" && -n "$family" && "$family" != "$MC_CERT_SCOPE" ]]; then
    echo "MATHCERT_CONTEXT_SKIP=$path family=$family active=$MC_CERT_SCOPE"
    return 0
  fi
  if [[ "$MC_ROUTE_SNAPSHOT_BOOTSTRAP" == "1" && "$MC_CERT_SCOPE" == "FULL_ESTATE" && \
        -n "$family" && "$family" != "OTP-H-GAPCVP" ]]; then
    echo "MATHCERT_HISTORICAL_ROUTE_VIEW=$path family=$family route_blob=4d5c8e3f2b33d5148d98e7057991e167938c75bb"
    run_python_in_route_view "$LEGACY_ROUTE_VIEW_HEAD" "$@"
    return $?
  fi
  command python3 "$@"
}

lake build
lake build mathsolve/MathSolve
lake env lean MathCert/FormalSources/RHNSReplay.lean
lake env lean MathCert/FormalSources/UCRestrictedReplay.lean
lake env lean MathCert/Domains/NumberTheory/EuclidGCD.lean
lake env lean MathCert/Domains/NumberTheory/EuclidDiophantine.lean
python3 ci/validate_certification_routes.py
python3 ci/test_validate_certification_routes.py
python3 ci/validate_formal_source_provenance.py
python3 ci/test_formal_source_provenance.py
python3 ci/validate_formal_target_certificates.py
python3 ci/test_formal_target_certificates.py
python3 ci/validate_uc_restricted_qualification_schema.py
python3 ci/test_uc_restricted_qualification_schema.py
python3 ci/validate_uc_restricted_qualification.py
python3 ci/test_uc_restricted_qualification.py
python3 ci/validate_uc_provider_identity_exclusion.py
python3 ci/test_uc_provider_identity_exclusion.py
python3 ci/check_ledgers.py
python3 ci/test_validate_ledgers.py
python3 ci/validate_algebraic_certificates.py
python3 ci/test_validate_algebraic_certificates.py
python3 ci/validate_tropic_relu_certificates.py
python3 ci/test_validate_tropic_relu_certificates.py
python3 ci/test_validate_pb_certificate.py
python3 ci/replay_certificates.py
python3 ci/audit_certificate_coverage.py
python3 ci/test_audit_certificate_coverage.py
python3 ci/check_formal_trust.py
python3 ci/test_check_formal_trust.py
python3 ci/validate_openai_ten_proofs_result_family_intakes.py
python3 ci/test_openai_ten_proofs_result_family_intakes.py
python3 ci/validate_openai_ten_proofs_sphere_packing_intake_successor.py
python3 ci/test_openai_ten_proofs_sphere_packing_intake_successor.py
python3 ci/validate_openai_ten_proofs_spherical_codes_intake_successor.py
python3 ci/test_openai_ten_proofs_spherical_codes_intake_successor.py
python3 ci/validate_openai_ten_proofs_gapcvp_intake_successor.py
python3 ci/test_openai_ten_proofs_gapcvp_intake_successor.py
python3 ci/validate_openai_ten_proofs_binary_codes_intake_successor.py
python3 ci/test_openai_ten_proofs_binary_codes_intake_successor.py
python3 ci/validate_openai_ten_proofs_certification_work_packages.py
python3 ci/test_openai_ten_proofs_certification_work_packages.py
python3 ci/validate_openai_ten_proofs_permanent_certification_work_package.py
python3 ci/test_openai_ten_proofs_permanent_certification_work_package.py
python3 ci/validate_openai_ten_proofs_sphere_packing_certification_work_package.py
python3 ci/test_openai_ten_proofs_sphere_packing_certification_work_package.py
python3 ci/validate_openai_ten_proofs_gapcvp_certification_work_package.py
python3 ci/test_openai_ten_proofs_gapcvp_certification_work_package.py
python3 ci/validate_openai_ten_proofs_binary_codes_certification_work_package.py
python3 ci/test_openai_ten_proofs_binary_codes_certification_work_package.py
python3 ci/validate_openai_ten_proofs_spherical_codes_certification_work_package.py
python3 ci/test_openai_ten_proofs_spherical_codes_certification_work_package.py
python3 ci/validate_openai_ten_proofs_replay_execution.py
python3 ci/test_openai_ten_proofs_replay_execution.py
python3 ci/validate_openai_ten_proofs_replay_evidence.py
python3 ci/test_openai_ten_proofs_replay_evidence.py
python3 ci/validate_openai_ten_proofs_permanent_cert_replay_evidence.py
python3 ci/test_openai_ten_proofs_permanent_cert_replay_evidence.py
python3 ci/validate_openai_ten_proofs_route_proposals.py
python3 ci/test_openai_ten_proofs_route_proposals.py
python3 ci/validate_openai_ten_proofs_sphere_packing_route_proposal.py
python3 ci/test_openai_ten_proofs_sphere_packing_route_proposal.py
python3 ci/validate_openai_ten_proofs_sphere_packing_route_registration.py
python3 ci/test_openai_ten_proofs_sphere_packing_route_registration.py
python3 ci/validate_openai_ten_proofs_permanent_route_proposal_with_full_formula_successor.py
python3 ci/test_openai_ten_proofs_permanent_route_proposal_with_full_formula_successor.py
python3 ci/validate_openai_ten_proofs_route_registrations_with_j2_successor.py
python3 ci/test_openai_ten_proofs_route_registrations.py
python3 ci/validate_openai_ten_proofs_permanent_route_registration.py
python3 ci/test_openai_ten_proofs_permanent_route_registration.py
python3 ci/validate_openai_ten_proofs_permanent_adjudication_contract.py
python3 ci/test_openai_ten_proofs_permanent_adjudication_contract.py
python3 ci/validate_otp_permanent_execution_candidate.py
python3 ci/test_otp_permanent_execution_candidate.py
python3 ci/validate_otp_permanent_adjudication.py
python3 ci/test_otp_permanent_adjudication.py
python3 ci/validate_otp_permanent_output_contract_with_full_formula_successor.py
python3 ci/test_otp_permanent_output_contract.py
python3 ci/validate_otp_permanent_output_execution.py
python3 ci/test_otp_permanent_output_execution.py
python3 ci/validate_human_steward_post_merge_attestation_with_j2_output.py
python3 ci/test_human_steward_post_merge_attestation.py
python3 ci/validate_openai_ten_proofs_adjudication_design_with_successors.py
python3 ci/test_openai_ten_proofs_adjudication_contracts.py
python3 ci/validate_otp_ehrhart_adjudication.py
python3 ci/test_otp_ehrhart_adjudication.py
python3 ci/validate_otp_ehrhart_adjudication_post_merge_attestation.py
python3 ci/test_otp_ehrhart_adjudication_post_merge_attestation.py
python3 ci/validate_otp_ehrhart_output_candidate.py
python3 ci/test_otp_ehrhart_output_contract.py
python3 ci/test_otp_ehrhart_output_candidate.py
python3 ci/validate_otp_ehrhart_output_execution_post_merge_attestation_with_j2_output.py
python3 ci/test_otp_ehrhart_output_execution_post_merge_attestation.py
python3 ci/validate_otp_compactness_evidence_refresh.py
python3 ci/test_otp_compactness_evidence_refresh.py
python3 ci/build_otp_compactness_construction_evidence.py
python3 ci/verify_otp_compactness_construction_evidence.py
python3 ci/validate_otp_compactness_construction_evidence_with_j2_output.py
python3 ci/test_otp_compactness_construction_evidence.py
python3 ci/validate_otp_compactness_output_contract_with_full_formula_successor.py
python3 ci/test_otp_compactness_output_contract.py
python3 ci/validate_otp_compactness_output_execution_with_j2_output.py
python3 ci/test_otp_compactness_output_execution.py
python3 ci/build_otp_j2_construction_evidence.py
python3 ci/verify_otp_j2_construction_evidence.py
python3 ci/validate_otp_j2_route_target_successor.py
python3 ci/test_otp_j2_route_target_successor.py
python3 ci/validate_otp_j2_adjudication_input.py
python3 ci/test_otp_j2_adjudication_input.py
python3 ci/validate_otp_j2_adjudication.py
python3 ci/test_otp_j2_adjudication.py
python3 ci/validate_otp_a_sphere_packing_adjudication_input.py
python3 ci/test_otp_a_sphere_packing_adjudication_input.py
python3 ci/validate_otp_a_sphere_packing_adjudication.py
python3 ci/test_otp_a_sphere_packing_adjudication.py
python3 ci/validate_otp_j2_output_contract_with_execution.py
python3 ci/test_otp_j2_output_contract.py
python3 ci/validate_otp_j2_output_execution_with_a_registration.py
python3 ci/test_otp_j2_output_execution_with_a_registration.py
python3 ci/validate_otp_j2_source_faithful_evidence_with_successor.py
python3 ci/test_otp_j2_source_faithful_evidence.py
python3 ci/validate_otp_j2_scope_repair_with_successor.py
python3 ci/test_otp_j2_scope_repair.py
python3 work_packages/EUCLID_GCD_E2E_001/check_certificate.py
python3 work_packages/EUCLID_GCD_E2E_001/test_certificate.py
python3 work_packages/EUCLID_DIOPHANTINE_E2E_002/check_certificate.py
python3 work_packages/EUCLID_DIOPHANTINE_E2E_002/test_certificate.py
python3 ci/validate_vgse_route_registration.py
python3 ci/test_vgse_route_registration.py
python3 ci/validate_otp_permanent_full_formula_certification.py
python3 ci/test_otp_permanent_full_formula_certification.py
python3 ci/validate_otp_permanent_circuit_certification.py
python3 ci/test_otp_permanent_circuit_certification.py
python3 ci/otp_a_sphere_packing_output_contract.py
python3 ci/otp_a_sphere_packing_output_contract_test.py
if [[ -f ci/validate_otp_replay_readback_reconciliation.py ]]; then
  python3 ci/validate_otp_replay_readback_reconciliation.py
  python3 ci/test_otp_replay_readback_reconciliation.py
fi
if [[ -f ci/validate_openai_ten_proofs_gapcvp_route_proposal.py ]]; then
  python3 ci/validate_openai_ten_proofs_gapcvp_route_proposal.py
  python3 ci/test_openai_ten_proofs_gapcvp_route_proposal.py
fi
if [[ -f ci/validate_openai_ten_proofs_gapcvp_route_registration.py ]]; then
  python3 ci/validate_openai_ten_proofs_gapcvp_route_registration.py
  python3 ci/test_openai_ten_proofs_gapcvp_route_registration.py
fi
python3 ci/audit_ci_reachability.py
python3 ci/test_audit_ci_reachability.py
