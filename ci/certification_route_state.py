#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import os
import re
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
CI_EXTENSIONS = {".py", ".sh", ".ps1"}
SKIP_PARTS = {".git", ".lake", "__pycache__"}


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


def _ci_sources(root: Path = ROOT) -> dict[str, str]:
    ci = root / "ci"
    sources: dict[str, str] = {}
    if not ci.exists():
        return sources
    for path in sorted(ci.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in CI_EXTENSIONS:
            continue
        rel = path.relative_to(root)
        if any(part in SKIP_PARTS for part in rel.parts):
            continue
        try:
            sources[rel.as_posix()] = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
    return sources


def dependency_edges(root: Path = ROOT) -> set[tuple[str, str]]:
    """Return (parent, dependency) edges for the repo-owned CI control graph."""
    sources = _ci_sources(root)
    module_to_path = {
        Path(path).stem: path for path in sources if path.endswith(".py")
    }
    edges: set[tuple[str, str]] = set()
    for parent, text in sources.items():
        imported: set[str] = set()
        if parent.endswith(".py"):
            try:
                tree = ast.parse(text)
            except SyntaxError:
                tree = None
            if tree is not None:
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imported.update(alias.name.split(".")[-1] for alias in node.names)
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        imported.add(node.module.split(".")[-1])
        for name, target in module_to_path.items():
            if target == parent:
                continue
            if (
                name in imported
                or f"{name}.py" in text
                or re.search(rf"(?<![A-Za-z0-9_]){re.escape(name)}(?![A-Za-z0-9_])", text)
            ):
                edges.add((parent, target))
    return edges


def dependency_closure(
    direct: set[str], root: Path = ROOT, edges: set[tuple[str, str]] | None = None
) -> set[str]:
    edges = dependency_edges(root) if edges is None else edges
    closure = set(direct)
    changed = True
    while changed:
        changed = False
        for parent, target in edges:
            if target in closure and parent not in closure:
                closure.add(parent)
                changed = True
    return closure


def _reachable_explicit_entries(
    path: str,
    manifest: dict[str, Any] | None = None,
    *,
    root: Path = ROOT,
    edges: set[tuple[str, str]] | None = None,
) -> list[dict[str, Any]]:
    manifest = load_manifest() if manifest is None else manifest
    explicit = consumer_map(manifest)
    edges = dependency_edges(root) if edges is None else edges
    deps: dict[str, set[str]] = {}
    for parent, target in edges:
        deps.setdefault(parent, set()).add(target)
    pending = list(deps.get(path, set()))
    visited: set[str] = set()
    entries: list[dict[str, Any]] = []
    while pending:
        target = pending.pop()
        if target in visited:
            continue
        visited.add(target)
        row = explicit.get(target)
        if row is not None:
            entries.append(row)
        pending.extend(deps.get(target, set()) - visited)
    return entries


def effective_classification_for(
    path: str | Path,
    manifest: dict[str, Any] | None = None,
    *,
    root: Path = ROOT,
    edges: set[tuple[str, str]] | None = None,
) -> dict[str, Any] | None:
    """Resolve explicit state or inherit one unambiguous state through CI dependencies."""
    manifest = load_manifest() if manifest is None else manifest
    consumer = normalize_consumer(path)
    explicit = classification_for(consumer, manifest)
    if explicit is not None:
        return explicit

    entries = _reachable_explicit_entries(
        consumer, manifest, root=root, edges=edges
    )
    if not entries:
        return None

    # Invariant helpers do not override a substantive state view.
    substantive = [row for row in entries if row.get("classification") != "INVARIANT"]
    relevant = substantive or entries
    signatures: set[tuple[str, str | None, str | None]] = set()
    for row in relevant:
        signatures.add(
            (
                str(row.get("classification")),
                row.get("snapshot_commit"),
                row.get("snapshot_blob"),
            )
        )
    if len(signatures) != 1:
        rendered = ", ".join(
            sorted(
                f"{cls}:{commit or '-'}:{blob or '-'}"
                for cls, commit, blob in signatures
            )
        )
        raise ValueError(
            f"ambiguous transitive certification state for {consumer}: {rendered}"
        )
    cls, commit, blob = next(iter(signatures))
    row: dict[str, Any] = {
        "path": consumer,
        "classification": cls,
        "inherited": True,
    }
    if cls == "HISTORICAL_SNAPSHOT":
        row["snapshot_commit"] = commit
        row["snapshot_blob"] = blob
    return row


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
            f"commit={entry['snapshot_commit']} blob={entry['snapshot_blob']} "
            f"inherited={str(bool(entry.get('inherited'))).lower()}",
            file=sys.stderr,
            flush=True,
        )
        yield
    finally:
        _git("checkout", "--detach", "--force", "--quiet", live_head)


def _run_with_entry(command: list[str], consumer: str, entry: dict[str, Any] | None) -> int:
    if entry is None:
        return subprocess.call(command, cwd=ROOT)
    cls = entry["classification"]
    if cls != "HISTORICAL_SNAPSHOT":
        print(
            f"MATHCERT_ROUTE_STATE_VIEW={cls} consumer={consumer} "
            f"inherited={str(bool(entry.get('inherited'))).lower()}",
            file=sys.stderr,
            flush=True,
        )
    with route_view(entry):
        return subprocess.call(command, cwd=ROOT)


def run_python(argv: list[str]) -> int:
    if not argv:
        raise ValueError("exec requires Python arguments")
    consumer: str | None = None
    first = argv[0]
    if first not in {"-", "-c", "-m"} and not first.startswith("-"):
        try:
            consumer = normalize_consumer(first)
        except ValueError:
            consumer = None
    real_python = os.environ.get("MATHCERT_REAL_PYTHON", sys.executable)
    if consumer is None:
        return subprocess.call([real_python, *argv], cwd=ROOT)
    entry = effective_classification_for(consumer)
    return _run_with_entry([real_python, *argv], consumer, entry)


def _bash_consumer(argv: list[str]) -> str | None:
    for arg in argv:
        if arg in {"-c", "-lc", "-l", "-s"}:
            return None
        if arg.startswith("-"):
            continue
        try:
            return normalize_consumer(arg)
        except ValueError:
            return None
    return None


def run_bash(argv: list[str]) -> int:
    real_bash = os.environ.get("MATHCERT_REAL_BASH")
    if not real_bash:
        raise RuntimeError("MATHCERT_REAL_BASH is required for exec-bash")
    consumer = _bash_consumer(argv)
    if consumer is None:
        return subprocess.call([real_bash, *argv], cwd=ROOT)
    entry = effective_classification_for(consumer)
    return _run_with_entry([real_bash, *argv], consumer, entry)


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
    if command == "exec-bash":
        return run_bash(rest)
    if command == "classify":
        if len(rest) != 1:
            raise ValueError("classify requires exactly one path")
        row = effective_classification_for(rest[0])
        print("UNCLASSIFIED" if row is None else row["classification"])
        return 0
    raise ValueError(f"unknown command: {command}")


if __name__ == "__main__":
    raise SystemExit(main())
