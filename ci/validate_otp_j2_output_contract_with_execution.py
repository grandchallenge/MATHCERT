#!/usr/bin/env python3
from __future__ import annotations

import sys

import otp_full_formula_contract_membership as membership
import validate_otp_j2_output_contract as design
import validate_otp_j2_output_execution as execution


def validation_errors() -> list[str]:
    # The protected design contract remains judged against the exact historical
    # four-contract membership. The new full-formula surface is separately
    # admitted as exactly one byte-identical successor/shadow pair.
    membership_errors = membership.membership_errors(design.ROOT, design.EXPECTED_CONTRACT_FILES)
    historical_errors = design.validation_errors(
        routes=execution.obj_json(execution.CONTENT, execution.ROUTES_PATH),
        future_certificate_present=False,
        candidate_present=False,
        staged_certificate_present=False,
        staged_route_present=False,
        contract_files=set(design.EXPECTED_CONTRACT_FILES),
    )
    return membership_errors + historical_errors + execution.validation_errors()


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"successor-aware J2 output-contract compatibility failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print(
        "validated immutable design-only J2 output contract against its exact pre-output route snapshot, "
        "the single governed full-formula successor membership, and the complete J2 restricted output execution"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
