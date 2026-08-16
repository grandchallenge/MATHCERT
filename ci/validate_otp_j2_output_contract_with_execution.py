#!/usr/bin/env python3
from __future__ import annotations

import sys

import validate_otp_j2_output_contract as design
import validate_otp_j2_output_execution as execution


def validation_errors() -> list[str]:
    # The protected design contract remains judged in its exact pre-output
    # submitted/null state. The live output successor is validated separately.
    historical_errors = design.validation_errors(
        routes=execution.obj_json(execution.CONTENT, execution.ROUTES_PATH),
        future_certificate_present=False,
        candidate_present=False,
        staged_certificate_present=False,
        staged_route_present=False,
    )
    return historical_errors + execution.validation_errors()


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"successor-aware J2 output-contract compatibility failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print(
        "validated immutable design-only J2 output contract against its exact pre-output route snapshot "
        "and separately validated the complete certificate-first restricted output execution"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
