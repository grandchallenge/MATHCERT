$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

function Get-ControlFamily([string]$Path) {
    $p = $Path.ToLowerInvariant()
    if ($p -match 'otp[_-]g[_-]quantum[_-]parallel[_-]repetition|quantum[_-]parallel[_-]repetition[_-]replay') { return 'OTP-G-QUANTUM-PARALLEL-REPETITION' }
    if ($p -match 'otp[_-]i[_-]ramsey|ramsey[_-]replay') { return 'OTP-I-RAMSEY' }
    if ($p -match 'spherical[_-]codes') { return 'OTP-B2-SPHERICAL-CODES' }
    if ($p -match 'binary[_-]codes') { return 'OTP-B1-BINARY-CODES' }
    if ($p -match 'gapcvp') { return 'OTP-H-GAPCVP' }
    if ($p -match 'permanent') { return 'OTP-C-PERMANENT' }
    if ($p -match 'compactness') { return 'OTP-J1-COMPACTNESS' }
    if ($p -match 'ehrhart') { return 'OTP-F-EHRHART' }
    if ($p -match 'otp[_-]j2|two[_-]degenerate|with_j2_output') { return 'OTP-J2-TWO-DEGENERATE' }
    if ($p -match 'sphere[_-]packing|otp_a_') { return 'OTP-A-SPHERE-PACKING' }
    if ($p -match 'openai[_-]ten[_-]proofs') { return 'FULL_ESTATE_ONLY' }
    return ''
}

$script:CertScope = $env:MC_CERT_SCOPE
if ([string]::IsNullOrWhiteSpace($script:CertScope)) {
    $script:CertScope = ((python ci/check_certification_platform_lane.py --certification-scope) | Out-String).Trim()
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
$validScopes = @(
    'FULL_ESTATE',
    'NO_LEAN',
    'OTP-A-SPHERE-PACKING',
    'OTP-B1-BINARY-CODES',
    'OTP-B2-SPHERICAL-CODES',
    'OTP-G-QUANTUM-PARALLEL-REPETITION',
    'OTP-H-GAPCVP',
    'OTP-I-RAMSEY',
    'OTP-C-PERMANENT',
    'OTP-J1-COMPACTNESS',
    'OTP-J2-TWO-DEGENERATE',
    'OTP-F-EHRHART'
)
if ($validScopes -notcontains $script:CertScope) { throw "unknown canonical certification scope: $script:CertScope" }
$env:MC_CERT_SCOPE = $script:CertScope
Write-Host "MATHCERT_CANONICAL_SCOPE=$script:CertScope"

function Invoke-Control([string]$Path) {
    $family = Get-ControlFamily $Path
    if ($script:CertScope -ne 'FULL_ESTATE' -and $family -and $family -ne $script:CertScope) {
        Write-Host "MATHCERT_CONTEXT_SKIP=$Path family=$family active=$script:CertScope"
        return
    }
    python $Path
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

if ($script:CertScope -eq 'NO_LEAN') {
    Write-Host "MATHCERT_LEAN_SKIP=no_lean_material_change"
} else {
    if (-not (Get-Command lake -ErrorAction SilentlyContinue)) { throw "lake is not installed; cannot certify Lean files." }
    lake build
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    lake build mathsolve/MathSolve
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    lake env lean MathCert/FormalSources/RHNSReplay.lean
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    lake env lean MathCert/FormalSources/UCRestrictedReplay.lean
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    lake env lean MathCert/Domains/NumberTheory/EuclidGCD.lean
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    lake env lean MathCert/Domains/NumberTheory/EuclidDiophantine.lean
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
Invoke-Control "ci/validate_certification_routes.py"
Invoke-Control "ci/test_validate_certification_routes.py"
Invoke-Control "ci/validate_formal_source_provenance.py"
Invoke-Control "ci/test_formal_source_provenance.py"
Invoke-Control "ci/validate_formal_target_certificates.py"
Invoke-Control "ci/test_formal_target_certificates.py"
Invoke-Control "ci/validate_external_catalog_certification_boundary.py"
Invoke-Control "ci/test_external_catalog_certification_boundary.py"
Invoke-Control "ci/validate_external_catalog_certification_intake.py"
Invoke-Control "ci/test_external_catalog_certification_intake.py"
Invoke-Control "ci/validate_uc_restricted_qualification_schema.py"
Invoke-Control "ci/test_uc_restricted_qualification_schema.py"
Invoke-Control "ci/validate_uc_restricted_qualification.py"
Invoke-Control "ci/test_uc_restricted_qualification.py"
Invoke-Control "ci/validate_uc_provider_identity_exclusion.py"
Invoke-Control "ci/test_uc_provider_identity_exclusion.py"
Invoke-Control "ci/check_ledgers.py"
Invoke-Control "ci/test_validate_ledgers.py"
Invoke-Control "ci/validate_algebraic_certificates.py"
Invoke-Control "ci/test_validate_algebraic_certificates.py"
Invoke-Control "ci/validate_tropic_relu_certificates.py"
Invoke-Control "ci/test_validate_tropic_relu_certificates.py"
Invoke-Control "ci/test_validate_pb_certificate.py"
Invoke-Control "ci/replay_certificates.py"
Invoke-Control "ci/audit_certificate_coverage.py"
Invoke-Control "ci/test_audit_certificate_coverage.py"
Invoke-Control "ci/check_formal_trust.py"
Invoke-Control "ci/test_check_formal_trust.py"
Invoke-Control "ci/validate_openai_ten_proofs_result_family_intakes.py"
Invoke-Control "ci/test_openai_ten_proofs_result_family_intakes.py"
Invoke-Control "ci/validate_openai_ten_proofs_sphere_packing_intake_successor.py"
Invoke-Control "ci/test_openai_ten_proofs_sphere_packing_intake_successor.py"
Invoke-Control "ci/validate_openai_ten_proofs_spherical_codes_intake_successor.py"
Invoke-Control "ci/test_openai_ten_proofs_spherical_codes_intake_successor.py"
Invoke-Control "ci/validate_openai_ten_proofs_gapcvp_intake_successor.py"
Invoke-Control "ci/test_openai_ten_proofs_gapcvp_intake_successor.py"
Invoke-Control "ci/validate_openai_ten_proofs_binary_codes_intake_successor.py"
Invoke-Control "ci/test_openai_ten_proofs_binary_codes_intake_successor.py"
if (Test-Path "ci/validate_openai_ten_proofs_ramsey_intake_successor.py") {
    Invoke-Control "ci/validate_openai_ten_proofs_ramsey_intake_successor.py"
    Invoke-Control "ci/test_openai_ten_proofs_ramsey_intake_successor.py"
}
if (Test-Path "ci/validate_openai_ten_proofs_quantum_parallel_repetition_intake_successor.py") {
    Invoke-Control "ci/validate_openai_ten_proofs_quantum_parallel_repetition_intake_successor.py"
    Invoke-Control "ci/test_openai_ten_proofs_quantum_parallel_repetition_intake_successor.py"
}
if (Test-Path "ci/validate_openai_ten_proofs_non_sofic_intake_successor.py") {
    Invoke-Control "ci/validate_openai_ten_proofs_non_sofic_intake_successor.py"
    Invoke-Control "ci/test_openai_ten_proofs_non_sofic_intake_successor.py"
}
if (Test-Path "ci/validate_openai_ten_proofs_connes_rigidity_intake_successor.py") {
    Invoke-Control "ci/validate_openai_ten_proofs_connes_rigidity_intake_successor.py"
    Invoke-Control "ci/test_openai_ten_proofs_connes_rigidity_intake_successor.py"
}
Invoke-Control "ci/validate_openai_ten_proofs_certification_work_packages.py"
Invoke-Control "ci/test_openai_ten_proofs_certification_work_packages.py"
Invoke-Control "ci/validate_openai_ten_proofs_permanent_certification_work_package.py"
Invoke-Control "ci/test_openai_ten_proofs_permanent_certification_work_package.py"
Invoke-Control "ci/validate_openai_ten_proofs_sphere_packing_certification_work_package.py"
Invoke-Control "ci/test_openai_ten_proofs_sphere_packing_certification_work_package.py"
Invoke-Control "ci/validate_openai_ten_proofs_gapcvp_certification_work_package.py"
Invoke-Control "ci/test_openai_ten_proofs_gapcvp_certification_work_package.py"
Invoke-Control "ci/validate_openai_ten_proofs_binary_codes_certification_work_package.py"
Invoke-Control "ci/test_openai_ten_proofs_binary_codes_certification_work_package.py"
Invoke-Control "ci/validate_openai_ten_proofs_spherical_codes_certification_work_package.py"
Invoke-Control "ci/test_openai_ten_proofs_spherical_codes_certification_work_package.py"
Invoke-Control "ci/validate_openai_ten_proofs_replay_execution.py"
Invoke-Control "ci/test_openai_ten_proofs_replay_execution.py"
Invoke-Control "ci/validate_openai_ten_proofs_replay_evidence.py"
Invoke-Control "ci/test_openai_ten_proofs_replay_evidence.py"
Invoke-Control "ci/validate_openai_ten_proofs_permanent_cert_replay_evidence.py"
Invoke-Control "ci/test_openai_ten_proofs_permanent_cert_replay_evidence.py"
Invoke-Control "ci/validate_openai_ten_proofs_route_proposals.py"
Invoke-Control "ci/test_openai_ten_proofs_route_proposals.py"
Invoke-Control "ci/validate_openai_ten_proofs_sphere_packing_route_proposal.py"
Invoke-Control "ci/test_openai_ten_proofs_sphere_packing_route_proposal.py"
Invoke-Control "ci/validate_openai_ten_proofs_sphere_packing_route_registration.py"
Invoke-Control "ci/test_openai_ten_proofs_sphere_packing_route_registration.py"
Invoke-Control "ci/validate_openai_ten_proofs_permanent_route_proposal_with_full_formula_successor.py"
Invoke-Control "ci/test_openai_ten_proofs_permanent_route_proposal_with_full_formula_successor.py"
Invoke-Control "ci/validate_openai_ten_proofs_route_registrations_with_j2_successor.py"
Invoke-Control "ci/test_openai_ten_proofs_route_registrations.py"
Invoke-Control "ci/validate_openai_ten_proofs_permanent_route_registration.py"
Invoke-Control "ci/test_openai_ten_proofs_permanent_route_registration.py"
Invoke-Control "ci/validate_openai_ten_proofs_permanent_adjudication_contract.py"
Invoke-Control "ci/test_openai_ten_proofs_permanent_adjudication_contract.py"
Invoke-Control "ci/validate_otp_permanent_execution_candidate.py"
Invoke-Control "ci/test_otp_permanent_execution_candidate.py"
Invoke-Control "ci/validate_otp_permanent_adjudication.py"
Invoke-Control "ci/test_otp_permanent_adjudication.py"
Invoke-Control "ci/validate_otp_permanent_output_contract_with_full_formula_successor.py"
Invoke-Control "ci/test_otp_permanent_output_contract.py"
Invoke-Control "ci/validate_otp_permanent_output_execution.py"
Invoke-Control "ci/test_otp_permanent_output_execution.py"
Invoke-Control "ci/validate_human_steward_post_merge_attestation_with_j2_output.py"
Invoke-Control "ci/test_human_steward_post_merge_attestation.py"
Invoke-Control "ci/validate_openai_ten_proofs_adjudication_design_with_successors.py"
Invoke-Control "ci/test_openai_ten_proofs_adjudication_contracts.py"
Invoke-Control "ci/validate_otp_ehrhart_adjudication.py"
Invoke-Control "ci/test_otp_ehrhart_adjudication.py"
Invoke-Control "ci/validate_otp_ehrhart_adjudication_post_merge_attestation.py"
Invoke-Control "ci/test_otp_ehrhart_adjudication_post_merge_attestation.py"
Invoke-Control "ci/validate_otp_ehrhart_output_candidate.py"
Invoke-Control "ci/test_otp_ehrhart_output_contract.py"
Invoke-Control "ci/test_otp_ehrhart_output_candidate.py"
Invoke-Control "ci/validate_otp_ehrhart_output_execution_post_merge_attestation_with_j2_output.py"
Invoke-Control "ci/test_otp_ehrhart_output_execution_post_merge_attestation.py"
Invoke-Control "ci/validate_otp_compactness_evidence_refresh.py"
Invoke-Control "ci/test_otp_compactness_evidence_refresh.py"
Invoke-Control "ci/build_otp_compactness_construction_evidence.py"
Invoke-Control "ci/verify_otp_compactness_construction_evidence.py"
Invoke-Control "ci/validate_otp_compactness_construction_evidence_with_j2_output.py"
Invoke-Control "ci/test_otp_compactness_construction_evidence.py"
Invoke-Control "ci/validate_otp_compactness_output_contract_with_full_formula_successor.py"
Invoke-Control "ci/test_otp_compactness_output_contract.py"
Invoke-Control "ci/validate_otp_compactness_output_execution_with_j2_output.py"
Invoke-Control "ci/test_otp_compactness_output_execution.py"
Invoke-Control "ci/build_otp_j2_construction_evidence.py"
Invoke-Control "ci/verify_otp_j2_construction_evidence.py"
Invoke-Control "ci/validate_otp_j2_route_target_successor.py"
Invoke-Control "ci/test_otp_j2_route_target_successor.py"
Invoke-Control "ci/validate_otp_j2_adjudication_input.py"
Invoke-Control "ci/test_otp_j2_adjudication_input.py"
Invoke-Control "ci/validate_otp_j2_adjudication.py"
Invoke-Control "ci/test_otp_j2_adjudication.py"
Invoke-Control "ci/validate_otp_a_sphere_packing_adjudication_input.py"
Invoke-Control "ci/test_otp_a_sphere_packing_adjudication_input.py"
Invoke-Control "ci/validate_otp_a_sphere_packing_adjudication.py"
Invoke-Control "ci/test_otp_a_sphere_packing_adjudication.py"
Invoke-Control "ci/validate_otp_j2_output_contract_with_execution.py"
Invoke-Control "ci/test_otp_j2_output_contract.py"
Invoke-Control "ci/validate_otp_j2_output_execution_with_a_registration.py"
Invoke-Control "ci/test_otp_j2_output_execution_with_a_registration.py"
Invoke-Control "ci/validate_otp_j2_source_faithful_evidence_with_successor.py"
Invoke-Control "ci/test_otp_j2_source_faithful_evidence.py"
Invoke-Control "ci/validate_otp_j2_scope_repair_with_successor.py"
Invoke-Control "ci/test_otp_j2_scope_repair.py"
Invoke-Control "work_packages/EUCLID_GCD_E2E_001/check_certificate.py"
Invoke-Control "work_packages/EUCLID_GCD_E2E_001/test_certificate.py"
Invoke-Control "work_packages/EUCLID_DIOPHANTINE_E2E_002/check_certificate.py"
Invoke-Control "work_packages/EUCLID_DIOPHANTINE_E2E_002/test_certificate.py"
Invoke-Control "ci/validate_vgse_route_registration.py"
Invoke-Control "ci/test_vgse_route_registration.py"
if (Test-Path "ci/replay_vgse_c05_te3_conformance.py") {
    python "ci/replay_vgse_c05_te3_conformance.py" --check "evidence/vgse/VGSE-WP00-CERT-001-te3-conformance-audit.json"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Invoke-Control "ci/test_replay_vgse_c05_te3_conformance.py"
}
Invoke-Control "ci/validate_otp_permanent_full_formula_certification.py"
Invoke-Control "ci/test_otp_permanent_full_formula_certification.py"
Invoke-Control "ci/validate_otp_permanent_circuit_certification.py"
Invoke-Control "ci/test_otp_permanent_circuit_certification.py"
Invoke-Control "ci/otp_a_sphere_packing_output_contract.py"
Invoke-Control "ci/otp_a_sphere_packing_output_contract_test.py"
if (Test-Path "ci/validate_otp_replay_readback_reconciliation.py") {
    Invoke-Control "ci/validate_otp_replay_readback_reconciliation.py"
    Invoke-Control "ci/test_otp_replay_readback_reconciliation.py"
}
if (Test-Path "ci/validate_openai_ten_proofs_gapcvp_route_proposal.py") {
    Invoke-Control "ci/validate_openai_ten_proofs_gapcvp_route_proposal.py"
    Invoke-Control "ci/test_openai_ten_proofs_gapcvp_route_proposal.py"
}
if (Test-Path "ci/validate_openai_ten_proofs_gapcvp_route_registration.py") {
    Invoke-Control "ci/validate_openai_ten_proofs_gapcvp_route_registration.py"
    Invoke-Control "ci/test_openai_ten_proofs_gapcvp_route_registration.py"
}
if (Test-Path "ci/validate_openai_ten_proofs_binary_codes_route_proposal.py") {
    Invoke-Control "ci/validate_openai_ten_proofs_binary_codes_route_proposal.py"
    Invoke-Control "ci/test_openai_ten_proofs_binary_codes_route_proposal.py"
}
if (Test-Path "ci/validate_openai_ten_proofs_binary_codes_route_registration.py") {
    Invoke-Control "ci/validate_openai_ten_proofs_binary_codes_route_registration.py"
    Invoke-Control "ci/test_openai_ten_proofs_binary_codes_route_registration.py"
}
if (Test-Path "ci/validate_openai_ten_proofs_spherical_codes_route_proposal.py") {
    Invoke-Control "ci/validate_openai_ten_proofs_spherical_codes_route_proposal.py"
    Invoke-Control "ci/test_openai_ten_proofs_spherical_codes_route_proposal.py"
}
if (Test-Path "ci/validate_openai_ten_proofs_spherical_codes_route_registration.py") {
    Invoke-Control "ci/validate_openai_ten_proofs_spherical_codes_route_registration.py"
    Invoke-Control "ci/test_openai_ten_proofs_spherical_codes_route_registration.py"
}
if (Test-Path "ci/validate_otp_g_quantum_parallel_repetition_certification.py") {
    Invoke-Control "ci/validate_otp_g_quantum_parallel_repetition_certification.py"
    Invoke-Control "ci/test_otp_g_quantum_parallel_repetition_certification.py"
}
if (Test-Path "ci/validate_otp_d_non_sofic_certification.py") {
    Invoke-Control "ci/validate_otp_d_non_sofic_certification.py"
    Invoke-Control "ci/test_otp_d_non_sofic_certification.py"
}
if (Test-Path "ci/validate_otp_e_connes_rigidity_certification.py") {
    Invoke-Control "ci/validate_otp_e_connes_rigidity_certification.py"
    Invoke-Control "ci/test_otp_e_connes_rigidity_certification.py"
}
if (Test-Path "ci/validate_otp_i_ramsey_certification.py") {
    Invoke-Control "ci/validate_otp_i_ramsey_certification.py"
    Invoke-Control "ci/test_otp_i_ramsey_certification.py"
}
Invoke-Control "ci/audit_ci_reachability.py"
Invoke-Control "ci/test_audit_ci_reachability.py"
