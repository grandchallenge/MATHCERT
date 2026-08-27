#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "governance/certification_route_state_consumers.json"
ROUTES_REL = "governance/certification_routes.json"
ALLOWED = {"HISTORICAL_SNAPSHOT", "CURRENT_STATE", "TRANSITION_STATE", "INVARIANT"}


def _git(*args: str, check: bool = True, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    return subprocess.run(
        ["git", "-C", str(ROOT), *args],
        text=True,
        capture_output=True,
        check=check,
        env=merged,
    )


def load_manifest(path: Path = MANIFEST) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_consumer(path: str | Path) -> str:
    p = Path(path)
    if p.is_absolute():
        try:
            p = p.resolve().relative_to(ROOT.resolve())
        except ValueError as exc:
            raise ValueError(f"consumer outside repository: {path}") from exc
    return p.as_posix().lstrip("./")


def consumer_map(manifest: dict[str, Any] | None = None) -> dict[str, dict[str, Any]]:
    manifest = load_manifest() if manifest is None else manifest
    result: dict[str, dict[str, Any]] = {}
    for row in manifest.get("consumers", []):
        path = normalize_consumer(row["path"])
        if path in result:
            raise ValueError(f"duplicate consumer classification: {path}")
        result[path] = row
    return result


def classification_for(path: str | Path, manifest: dict[str, Any] | None = None) -> dict[str, Any] | None:
    return consumer_map(manifest).get(normalize_consumer(path))


def blob_at(commit: str, rel: str = ROUTES_REL) -> str:
    return _git("rev-parse", f"{commit}:{rel}").stdout.strip()


def verify_historical_entry(entry: dict[str, Any]) -> None:
    if entry.get("classification") != "HISTORICAL_SNAPSHOT":
        return
    commit = entry.get("snapshot_commit")
    expected = entry.get("snapshot_blob")
    if not isinstance(commit, str) or not commit:
        raise ValueError("historical consumer lacks snapshot_commit")
    if not isinstance(expected, str) or not expected:
        raise ValueError("historical consumer lacks snapshot_blob")
    actual = blob_at(commit)
    if actual != expected:
        raise ValueError(f"historical route snapshot drift: {actual} != {expected}")


def validate_manifest(manifest: dict[str, Any] | None = None) -> list[str]:
    manifest = load_manifest() if manifest is None else manifest
    errors: list[str] = []
    if manifest.get("route_registry_path") != ROUTES_REL:
        errors.append("route registry path drift")
    allowed = set(manifest.get("allowed_classes", []))
    if allowed != ALLOWED:
        errors.append(f"allowed class drift: {sorted(allowed)}")
    seen: set[str] = set()
    for row in manifest.get("consumers", []):
        try:
            path = normalize_consumer(row.get("path", ""))
        except Exception as exc:
            errors.append(str(exc))
            continue
        if not path:
            errors.append("empty consumer path")
            continue
        if path in seen:
            errors.append(f"duplicate consumer: {path}")
        seen.add(path)
        cls = row.get("classification")
        if cls not in ALLOWED:
            errors.append(f"unknown classification for {path}: {cls}")
        if cls == "HISTORICAL_SNAPSHOT":
            try:
                verify_historical_entry(row)
            except Exception as exc:
                errors.append(f"{path}: {exc}")
        elif "snapshot_commit" in row or "snapshot_blob" in row:
            errors.append(f"non-historical consumer carries snapshot identity: {path}")
    return errors


def _synthetic_historical_head(entry: dict[str, Any]) -> tuple[str, str]:
    verify_historical_entry(entry)
    live_head = _git("rev-parse", "HEAD").stdout.strip()
    live_tree = _git("rev-parse", "HEAD^{tree}").stdout.strip()
    route_blob = str(entry["snapshot_blob"])

    fd, index_path = tempfile.mkstemp(prefix="mathcert-route-view-index-")
    os.close(fd)
    os.unlink(index_path)
    env = {"GIT_INDEX_FILE": index_path}
    try:
        _git("read-tree", live_tree, env=env)
        _git("update-index", "--cacheinfo", f"100644,{route_blob},{ROUTES_REL}", env=env)
        synthetic_tree = _git("write-tree", env=env).stdout.strip()
    finally:
        try:
            os.unlink(index_path)
        except FileNotFoundError:
            pass

    commit_env = {
        "GIT_AUTHOR_NAME": "MATHCERT CI",
        "GIT_AUTHOR_EMAIL": "mathcert-ci@grandchallenge.ai",
        "GIT_COMMITTER_NAME": "MATHCERT CI",
        "GIT_COMMITTER_EMAIL": "mathcert-ci@grandchallenge.ai",
    }
    proc = subprocess.run(
        ["git", "-C", str(ROOT), "commit-tree", synthetic_tree, "-p", live_head],
        input="MC-CERTIFICATION-STATE-ARCHITECTURE-STABILIZATION-001 historical route view\n",
        text=True,
        capture_output=True,
        check=True,
        env={**os.environ, **commit_env},
    )
    synthetic_head = proc.stdout.strip()
    actual = blob_at(synthetic_head)
    if actual != route_blob:
        raise ValueError(f"synthetic historical view drift: {actual} != {route_blob}")
    return live_head, synthetic_head


@contextmanager
def route_view(entry: dict[str, Any]) -> Iterator[None]:
    if entry.get("classification") != "HISTORICAL_SNAPSHOT":
        yield
        return
    if _git("status", "--porcelain", "--untracked-files=no").stdout.strip():
        raise RuntimeError("historical route view requires a clean tracked working tree")
    live_head, synthetic_head = _synthetic_historical_head(entry)
    try:
        _git("checkout", "--detach", "--force", "--quiet", synthetic_head)
        print(
            "MATHCERT_ROUTE_STATE_VIEW="
            f"HISTORICAL_SNAPSHOT consumer={normalize_consumer(entry['path'])} "
            f"commit={entry['snapshot_commit']} blob={entry['snapshot_blob']}",
            flush=True,
        )
        yield
    finally:
        _git("checkout", "--detach", "--force", "--quiet", live_head)


def run_python(argv: list[str]) -> int:
    if not argv:
        raise ValueError("exec requires a Python consumer path")
    consumer = normalize_consumer(argv[0])
    entry = classification_for(consumer)
    if entry is None:
        return subprocess.call([sys.executable, *argv], cwd=ROOT)
    cls = entry["classification"]
    if cls != "HISTORICAL_SNAPSHOT":
        print(f"MATHCERT_ROUTE_STATE_VIEW={cls} consumer={consumer}", flush=True)
    with route_view(entry):
        return subprocess.call([sys.executable, *argv], cwd=ROOT)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv == ["validate"]:
        errors = validate_manifest()
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        print("certification route-state manifest: PASS")
        return 0
    command, *rest = argv
    if command == "exec":
        return run_python(rest)
    if command == "classify":
        if len(rest) != 1:
            raise ValueError("classify requires exactly one path")
        row = classification_for(rest[0])
        print("UNCLASSIFIED" if row is None else row["classification"])
        return 0
    raise ValueError(f"unknown command: {command}")


if __name__ == "__main__":
    raise SystemExit(main())
