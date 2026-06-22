$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

if (-not (Get-Command lake -ErrorAction SilentlyContinue)) {
    throw "lake is not installed; cannot certify Lean files."
}

lake build
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python ci/validate_ledgers.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python ci/test_validate_ledgers.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python ci/validate_algebraic_certificates.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python ci/test_validate_algebraic_certificates.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python ci/validate_tropic_relu_certificates.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python ci/test_validate_tropic_relu_certificates.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python ci/replay_certificates.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python ci/check_sorries.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
