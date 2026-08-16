#!/usr/bin/env python3
from __future__ import annotations

import sys

import validate_otp_ehrhart_output_execution as historical
import validate_otp_j2_route_target_successor as j2


def validation_errors() -> list[str]:
    # Preserve the historical Ehrhart execution candidate against the exact
    # route state immediately before the separately governed J2 output.
    errors = historical.validation_errors(routes=j2.pre_output_routes())
    # Require the live J2 restricted qualification independently and exactly.
    errors.extend(j2.live_output_successor_errors())
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(
            f"J2-output-aware OTP-F-EHRHART execution candidate compatibility failed with {len(errors)} error(s)",
            file=sys.stderr,
        )
        return 1
    print(
        "validated historical certificate-first OTP-F-EHRHART execution candidate against the exact "
        "pre-J2-output route snapshot and separately validated the live J2 restricted output successor"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
