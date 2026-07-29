#!/usr/bin/env python3
"""Reject untracked Lean proof gaps and unregistered trust-boundary declarations."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLACEHOLDER = re.compile(r"\b(sorry|admit)\b")
DECLARATION = re.compile(r"^\s*(axiom|opaque)\s+([A-Za-z_][A-Za-z0-9_'.]*)")


def errors(root: Path = ROOT) -> list[str]:
    allowlist = root / "governance" / "formal_trust_allowlist.json"
    data = json.loads(allowlist.read_text(encoding="utf-8"))
    records = data.get("declarations", [])
    allowed = {
        (str(item.get("kind")), str(item.get("name"))): item
        for item in records
        if isinstance(item, dict)
    }
    found: list[str] = []
    seen: set[tuple[str, str]] = set()

    for path in sorted((root / "MathCert").rglob("*.lean")):
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if PLACEHOLDER.search(line):
                found.append(f"{path.relative_to(root)}:{line_number}: proof placeholder: {line.strip()}")
            match = DECLARATION.match(line)
            if not match:
                continue
            key = (match.group(1), match.group(2))
            seen.add(key)
            record = allowed.get(key)
            if record is None:
                found.append(
                    f"{path.relative_to(root)}:{line_number}: unregistered {key[0]} declaration {key[1]}"
                )
                continue
            for field in ("source_id", "justification", "review_issue"):
                if not str(record.get(field, "")).strip():
                    found.append(f"formal trust allowlist {key[1]} missing {field}")

    for key in sorted(set(allowed) - seen):
        found.append(f"formal trust allowlist contains stale declaration: {key[0]} {key[1]}")
    return found


def main() -> int:
    found = errors()
    if found:
        print("\n".join(found), file=sys.stderr)
        print(f"Formal trust check failed with {len(found)} error(s)", file=sys.stderr)
        return 1
    print("validated Lean placeholder absence and provenance of governed axiom/opaque declarations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
