#!/usr/bin/env python3
"""Reject proof placeholders in tracked MATHCERT Lean files."""
from __future__ import annotations

import re
from pathlib import Path

SORRY = re.compile(r"\bsorry\b")


def main() -> int:
    errors = 0
    for path in sorted(Path("MathCert").rglob("*.lean")):
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if SORRY.search(line):
                print(f"{path}:{line_number}: untracked proof placeholder: {line.strip()}")
                errors += 1
    if errors:
        print(f"Sorry check failed with {errors} error(s)")
        return 1
    print("No Lean proof placeholders found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
