#!/usr/bin/env bash
set -euo pipefail

if ! command -v lake >/dev/null 2>&1; then
  echo "lake is not installed; cannot certify Lean files." >&2
  exit 1
fi

cd "$(dirname "$0")/.."

lake build
python3 ci/validate_certification_routes.py
python3 ci/test_validate_certification_routes.py
python3 ci/validate_ledgers.py
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
python3 ci/audit_ci_reachability.py
python3 ci/test_audit_ci_reachability.py
