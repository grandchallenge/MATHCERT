#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import types
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
BASE_COMMIT = "64e042ddb1147338ad7868a2847715fe7c1c079d"
SOURCE_PATH = "ci/validate_formal_target_certificates.py"
CERT_DIR = ROOT / "certificates" / "formal_sources"
SCHEMA_PATH = ROOT / "schemas" / "formal_target_certificate.schema.json"
EHRHART_SCHEMA_PATH = ROOT / "schemas" / "otp_ehrhart_qualified_output.schema.json"
REGISTRY_PATH = ROOT / "governance" / "certification_routes.json"
EHRHART_FILE = "MC-OTP-F-EHRHART-001.json"
EHRHART_BLOB = "27a855c949b67e71372c7f0d6601d80125d33968"
CONTENT_COMMIT = "24d99cbdcd6da33ae2404c0f6034d503498d9a4b"
TARGETS = [
    "Ehrhart.Volume.ehrhart_volume_inequality_for_sets",
    "Ehrhart.SimplexVolume.exists_centeredBody_sharp",
    "Ehrhart.SimplexVolume.barycenter_centeredSimplex",
    "Ehrhart.SimplexVolume.normalizedVolume_centeredSimplex",
]
LEGACY_FILES = {"MC-FC-WP00-RH-001.json", "MC-FC-WP00-NS-CI-001.json"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(data)}\0".encode("ascii") + data,
        usedforsecurity=False,
    ).hexdigest()


def git(*args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args], cwd=ROOT, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=False,
    )


def protected_module() -> types.ModuleType:
    shallow = git("rev-parse", "--is-shallow-repository")
    if shallow.returncode == 0 and shallow.stdout.decode().strip() == "true":
        result = git("fetch", "--no-tags", "--unshallow", "origin")
        if result.returncode != 0:
            raise RuntimeError("unable to unshallow formal-certificate history")
    if git("cat-file", "-e", f"{BASE_COMMIT}^{{commit}}").returncode != 0:
        result = git("fetch", "--no-tags", "origin", BASE_COMMIT)
        if result.returncode != 0:
            raise RuntimeError("unable to fetch protected formal-certificate validator")
    result = git("show", f"{BASE_COMMIT}:{SOURCE_PATH}")
    if result.returncode != 0:
        raise RuntimeError("unable to read protected formal-certificate validator")
    module = types.ModuleType("protected_formal_target_certificates")
    module.__file__ = str(ROOT / SOURCE_PATH)
    exec(compile(result.stdout.decode("utf-8"), module.__file__, "exec"), module.__dict__)
    return module


def certificate_errors(
    directory: Path = CERT_DIR,
    schema_path: Path = SCHEMA_PATH,
    registry_path: Path = REGISTRY_PATH,
    root: Path = ROOT,
    ehrhart_schema_path: Path = EHRHART_SCHEMA_PATH,
) -> list[str]:
    errors: list[str] = []
    try:
        base = protected_module()
    except RuntimeError as exc:
        return [str(exc)]

    with tempfile.TemporaryDirectory() as temporary:
        legacy_dir = Path(temporary)
        for name in LEGACY_FILES:
            source = directory / name
            if source.exists():
                shutil.copyfile(source, legacy_dir / name)
        errors.extend(
            base.certificate_errors(
                directory=legacy_dir,
                schema_path=schema_path,
                registry_path=registry_path,
                root=root,
            )
        )

    actual = {path.name for path in directory.glob("*.json")}
    expected = LEGACY_FILES | {EHRHART_FILE}
    for missing in sorted(expected - actual):
        errors.append(f"missing formal target certificate: {missing}")
    for unknown in sorted(actual - expected):
        errors.append(f"unregistered formal target certificate: {unknown}")

    ehrhart_path = directory / EHRHART_FILE
    if not ehrhart_path.exists():
        return errors
    data = load_json(ehrhart_path)
    schema = load_json(ehrhart_schema_path)
    if schema.get("additionalProperties") is not False:
        errors.append("Ehrhart qualification schema must remain closed")
    errors.extend(
        f"{ehrhart_path}: Ehrhart schema violation: {error.message}"
        for error in Draft202012Validator(schema).iter_errors(data)
    )
    if git_blob(ehrhart_path) != EHRHART_BLOB:
        errors.append(f"{ehrhart_path}: certificate blob identity drift")
    if data.get("certificate_id") != "MC-OTP-F-EHRHART-QUAL-001":
        errors.append(f"{ehrhart_path}: certificate identity drift")
    if data.get("result_family") != "OTP-F-EHRHART" or data.get("route_id") != "MC-ROUTE-OTP-F-EHRHART":
        errors.append(f"{ehrhart_path}: family/route identity drift")
    if data.get("encoded_targets") != TARGETS:
        errors.append(f"{ehrhart_path}: encoded target scope drift")
    qualification = data.get("qualification", {})
    if qualification.get("disposition") != "qualified_encoded_targets_only":
        errors.append(f"{ehrhart_path}: disposition inflation")
    if qualification.get("source_theorem_mathematically_proved") is not False:
        errors.append(f"{ehrhart_path}: mathematical target must remain unproved")
    if qualification.get("equality_case_classification") != "excluded":
        errors.append(f"{ehrhart_path}: equality-case inflation")
    if data.get("state") != {
        "route_state": "qualified",
        "cert_output_inserted": True,
        "mathematical_target_proved": False,
        "may_promote_claim": False,
        "aggregate_output": False,
    }:
        errors.append(f"{ehrhart_path}: state inflation")

    registry = load_json(registry_path)
    route = next(
        (item for item in registry.get("routes", []) if item.get("campaign_id") == "OTP-F-EHRHART"),
        {},
    )
    if route.get("intake_status") != "qualified":
        errors.append("OTP-F-EHRHART: route is not qualified")
    if route.get("cert_output") != {
        "repository": "grandchallenge/MATHCERT",
        "commit_sha": CONTENT_COMMIT,
        "path": "certificates/formal_sources/MC-OTP-F-EHRHART-001.json",
        "digest_algorithm": "git_blob_sha1",
        "digest": EHRHART_BLOB,
    }:
        errors.append("OTP-F-EHRHART: route output identity drift")
    return errors


def main() -> int:
    errors = certificate_errors()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"formal target certificate validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print("validated protected RH/NS qualifications and exact OTP-F-EHRHART restricted output")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
