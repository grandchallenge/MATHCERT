#!/usr/bin/env python3
from __future__ import annotations

import sys

import otp_full_formula_contract_membership as membership
import validate_otp_permanent_output_contract as historical


def validation_errors() -> list[str]:
    errors = membership.membership_errors(historical.ROOT, historical.EXPECTED_CONTRACT_FILES)
    errors += historical.validation_errors(contract_files=set(historical.EXPECTED_CONTRACT_FILES))
    return errors


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"Permanent output-contract successor compatibility failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print("validated protected Permanent output contract plus exactly one byte-identical full-formula successor membership")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
