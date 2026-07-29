#!/usr/bin/env python3
"""Verify that every certificate artifact belongs to an executable or blocked lane."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def errors(root: Path = ROOT) -> list[str]:
    data = json.loads(
        (root / "governance" / "ci_control_registry.json").read_text(encoding="utf-8")
    )
    found: list[str] = []
    families = {item["root"]: item for item in data.get("certificate_families", [])}
    exact_expected = set(data.get("exact_certificate_files", []))
    support_expected = set(data.get("supporting_artifact_files", []))
    cert_root = root / "certificates"
    discovered = {
        str(path.relative_to(root)).replace("\\", "/")
        for path in cert_root.rglob("*.json")
        if path.is_file()
    }
    if not discovered:
        return ["no certificate artifacts were discovered"]

    support_actual = {
        path for path in discovered if path.startswith("certificates/exact/source/")
    }
    exact_actual = {
        path for path in discovered
        if path.startswith("certificates/exact/") and path not in support_actual
    }
    for missing in sorted(exact_expected - exact_actual):
        found.append(f"registered exact certificate is missing: {missing}")
    for unknown in sorted(exact_actual - exact_expected):
        found.append(f"exact certificate has no replay implementation: {unknown}")
    for missing in sorted(support_expected - support_actual):
        found.append(f"registered supporting artifact is missing: {missing}")
    for unknown in sorted(support_actual - support_expected):
        found.append(f"supporting artifact is not registered: {unknown}")

    for artifact in sorted(discovered):
        matched = None
        for family_root, family in families.items():
            if artifact == family_root or artifact.startswith(family_root + "/"):
                matched = family
                break
        if matched is None:
            found.append(f"certificate artifact belongs to no governed family: {artifact}")
            continue
        admission = matched.get("admission")
        checker = matched.get("checker")
        if admission == "blocked":
            found.append(f"blocked certificate family contains an artifact: {artifact}")
        elif not checker:
            found.append(f"certificate family lacks a checker: {artifact}")
        elif not (root / checker).exists():
            found.append(f"certificate checker is missing for {artifact}: {checker}")

    return found


def main() -> int:
    found = errors()
    if found:
        print("\n".join(found), file=sys.stderr)
        print(f"Certificate coverage audit failed with {len(found)} error(s)", file=sys.stderr)
        return 1
    print("validated certificate-family admission, replay enumeration, supporting artifacts, and orphan rejection")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
