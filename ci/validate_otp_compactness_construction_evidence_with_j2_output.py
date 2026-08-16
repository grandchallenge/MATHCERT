#!/usr/bin/env python3
from __future__ import annotations

import sys

import validate_otp_compactness_construction_evidence as historical
import validate_otp_j2_route_target_successor as j2


def validation_errors() -> list[str]:
    live = historical.load(historical.ROUTES)
    errors = historical.validation_errors(routes=j2.pre_output_routes())
    errors.extend(j2.live_output_successor_errors(live))
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"J2-output-aware Compactness construction compatibility failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print(
        "validated immutable Compactness construction evidence against the exact pre-J2-output route snapshot "
        "and separately validated the live J2 restricted output successor"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
