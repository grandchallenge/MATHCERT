#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys

import validate_human_steward_post_merge_attestation as historical
import validate_otp_j2_route_target_successor as j2


def historical_route_snapshot() -> dict:
    proc = subprocess.run(
        ["git", "-C", str(historical.ROOT), "cat-file", "blob", historical.HISTORICAL_ROUTE_BLOB],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(proc.stdout)


def validation_errors() -> list[str]:
    # The August 2 Human Steward attestation ratified exactly the original three
    # submitted/null route registrations. Replay that immutable state from the
    # exact bound registry blob rather than interpreting later governed outputs
    # as changes to the historical ratification.
    errors = historical.validation_errors(
        routes=historical_route_snapshot(),
        route_blob=historical.HISTORICAL_ROUTE_BLOB,
    )

    # The current J2 state is governed separately by the protected output
    # contract and certificate-first publication chain. Require it exactly;
    # this wrapper does not grant any broader route or attestation authority.
    errors.extend(j2.live_output_successor_errors())
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(
            f"J2-output-aware post-merge attestation compatibility failed with {len(errors)} error(s)",
            file=sys.stderr,
        )
        return 1
    print(
        "validated immutable August 2 route-registration ratification against its exact submitted/null "
        "registry blob and separately validated the live J2 restricted output successor"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
