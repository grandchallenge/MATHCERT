#!/usr/bin/env python3
from __future__ import annotations

import sys

import otp_full_formula_route_proposal_compat as compat
import validate_openai_ten_proofs_permanent_route_proposal as historical


def validation_errors() -> list[str]:
    errors = compat.successor_errors(historical.ROOT, historical.PROPOSAL.parent)
    with compat.historical_membership_view(historical.PROPOSAL.parent):
        errors += historical.validation_errors()
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"Permanent route-proposal successor compatibility failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print("validated immutable historical Permanent route proposal plus exactly one bounded full-formula successor proposal")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
