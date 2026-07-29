$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

if (-not (Get-Command lake -ErrorAction SilentlyContinue)) {
    throw "lake is not installed; cannot certify Lean files."
}

function Invoke-Control([string]$Path) {
    python $Path
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

lake build
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Invoke-Control "ci/validate_certification_routes.py"
Invoke-Control "ci/test_validate_certification_routes.py"
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
Invoke-Control "ci/audit_ci_reachability.py"
Invoke-Control "ci/test_audit_ci_reachability.py"
