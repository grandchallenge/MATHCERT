#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import io
import sys
import unittest

import otp_full_formula_route_proposal_compat as compat
import validate_openai_ten_proofs_permanent_route_proposal as historical


def historical_test_errors() -> list[str]:
    spec = importlib.util.spec_from_file_location(
        "historical_permanent_route_proposal_tests_via_validator",
        historical.ROOT / "ci/test_openai_ten_proofs_permanent_route_proposal.py",
    )
    if not spec or not spec.loader:
        return ["cannot load historical Permanent route-proposal test suite"]
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    suite = unittest.defaultTestLoader.loadTestsFromModule(module)
    stream = io.StringIO()
    with compat.historical_membership_view(historical.PROPOSAL.parent):
        result = unittest.TextTestRunner(stream=stream, verbosity=0).run(suite)
    if result.wasSuccessful():
        return []
    return ["historical Permanent route-proposal tests failed under frozen membership view: " + stream.getvalue().strip()]


def validation_errors() -> list[str]:
    errors = compat.successor_errors(historical.ROOT, historical.PROPOSAL.parent)
    with compat.historical_membership_view(historical.PROPOSAL.parent):
        errors += historical.validation_errors()
    errors += historical_test_errors()
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"Permanent route-proposal successor compatibility failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print("validated immutable historical Permanent route proposal and its historical mutation suite plus exactly one bounded full-formula successor proposal")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
