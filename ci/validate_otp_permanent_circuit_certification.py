#!/usr/bin/env python3
from __future__ import annotations

import sys

import otp_permanent_circuit_execution_history as history
import otp_permanent_circuit_output_execution as output

TARGETS = output.TARGETS


def validation_errors() -> list[str]:
    return output.validation_errors() + history.validation_errors()


def main() -> int:
    errors = validation_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"OTP Permanent circuit executed-output validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print("OTP Permanent circuit executed output validates fail-closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
