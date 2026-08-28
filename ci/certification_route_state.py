#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_REL = "governance/certification_route_state_consumers.json"
MANIFEST = ROOT / MANIFEST_REL
ROUTES_REL = "governance/certification_routes.json"
ALLOWED = {"HISTORICAL_SNAPSHOT", "CURRENT_STATE", "TRANSITION_STATE", "INVARIANT"}
CI_EXTENSIONS = {".py", ".sh", ".ps1"}
SKIP_PARTS = {".git", ".lake", "__pycache__"}
STATE_PREFIXES = ("governance/", "evidence/", "certificates/")
HEX40_RE = re.compile(r"[0-9a-f]{40}")
SOURCE_ROUTE_PIN_RE = re.compile(
    r'''["']governance/certification_routes\.json["']\s*:\s*["'](?P<blob>[0-9a-f]{40})["']'''
)
SOURCE_OBJECT_PIN_RE = re.compile(
    r'''["'](?P<path>(?:governance|evidence|certificates)/[^"']+)["']\s*:\s*["'](?P<blob>[0-9a-f]{40})["']'''
)
_UNKNOWN = object()


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


def direct_token_consumers(root: Path = ROOT) -> set[str]:
    return {path for path, text in _ci_sources(root).items() if "certification_routes" in text}


def source_route_blob_pins(path: str | Path, *, root: Path = ROOT) -> set[str]:
    source = root / normalize_consumer(path)
    if not source.is_file():
        return set()
    try:
        text = source.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return set()
    return {match.group("blob") for match in SOURCE_ROUTE_PIN_RE.finditer(text)}


def _static_eval(node: ast.AST, env: dict[str, Any]) -> Any:
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        return env.get(node.id, _UNKNOWN)
    if isinstance(node, ast.List):
        values = [_static_eval(item, env) for item in node.elts]
        return _UNKNOWN if any(value is _UNKNOWN for value in values) else values
    if isinstance(node, ast.Tuple):
        values = [_static_eval(item, env) for item in node.elts]
        return _UNKNOWN if any(value is _UNKNOWN for value in values) else tuple(values)
    if isinstance(node, ast.Dict):
        result: dict[Any, Any] = {}
        for key_node, value_node in zip(node.keys, node.values):
            if key_node is None:
                return _UNKNOWN
            key = _static_eval(key_node, env)
            value = _static_eval(value_node, env)
            if key is _UNKNOWN or value is _UNKNOWN:
                return _UNKNOWN
            try:
                result[key] = value
            except TypeError:
                return _UNKNOWN
        return result
    if isinstance(node, ast.Subscript):
        base = _static_eval(node.value, env)
        key = _static_eval(node.slice, env)
        if base is _UNKNOWN or key is _UNKNOWN:
            return _UNKNOWN
        try:
            return base[key]
        except (KeyError, IndexError, TypeError):
            return _UNKNOWN
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = _static_eval(node.left, env)
        right = _static_eval(node.right, env)
        if left is _UNKNOWN or right is _UNKNOWN:
            return _UNKNOWN
        try:
            return left + right
        except TypeError:
            return _UNKNOWN
    return _UNKNOWN


def _static_environment(text: str) -> dict[str, Any]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return {}
    env: dict[str, Any] = {}
    for node in tree.body:
        target: ast.AST | None = None
        value_node: ast.AST | None = None
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            value_node = node.value
        elif isinstance(node, ast.AnnAssign):
            target = node.target
            value_node = node.value
        if not isinstance(target, ast.Name) or value_node is None:
            continue
        value = _static_eval(value_node, env)
        if value is not _UNKNOWN:
            env[target.id] = value
    return env


def _is_state_path(value: Any) -> bool:
    return isinstance(value, str) and value.startswith(STATE_PREFIXES) and ".." not in Path(value).parts


def _merge_pin(pins: dict[str, str], rel: str, blob: str, *, source: str) -> None:
    previous = pins.get(rel)
    if previous is not None and previous != blob:
        raise ValueError(f"ambiguous protected-object pins for {rel}: {previous} != {blob} ({source})")
    pins[rel] = blob


def _collect_static_pins(value: Any, pins: dict[str, str], *, source: str) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if _is_state_path(key) and isinstance(item, str) and HEX40_RE.fullmatch(item):
                _merge_pin(pins, key, item, source=source)
            _collect_static_pins(item, pins, source=source)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _collect_static_pins(item, pins, source=source)


def source_object_pins(path: str | Path, *, root: Path = ROOT) -> dict[str, str]:
    consumer = normalize_consumer(path)
    source = root / consumer
    if not source.is_file():
        return {}
    try:
        text = source.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return {}
    pins: dict[str, str] = {}
    for match in SOURCE_OBJECT_PIN_RE.finditer(text):
        _merge_pin(pins, match.group("path"), match.group("blob"), source=consumer)
    if source.suffix.lower() == ".py":
        for value in _static_environment(text).values():
            _collect_static_pins(value, pins, source=consumer)
    return pins


def _path_expr(node: ast.AST, env: dict[str, str]) -> str | None:
    if isinstance(node, ast.Name):
        if node.id == "ROOT":
            return ""
        return env.get(node.id)
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value if _is_state_path(node.value) else None
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        left = _path_expr(node.left, env)
        if left is None:
            return None
        if not isinstance(node.right, ast.Constant) or not isinstance(node.right.value, str):
            return None
        combined = f"{left}/{node.right.value}" if left else node.right.value
        return combined if _is_state_path(combined) else None
    return None


def source_absence_paths(path: str | Path, *, root: Path = ROOT) -> set[str]:
    consumer = normalize_consumer(path)
    source = root / consumer
    if not source.is_file() or source.suffix.lower() != ".py":
        return set()
    try:
        tree = ast.parse(source.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return set()
    path_env: dict[str, str] = {}
    for node in tree.body:
        target: ast.AST | None = None
        value_node: ast.AST | None = None
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            value_node = node.value
        elif isinstance(node, ast.AnnAssign):
            target = node.target
            value_node = node.value
        if isinstance(target, ast.Name) and value_node is not None:
            value = _path_expr(value_node, path_env)
            if value is not None:
                path_env[target.id] = value
    absent: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.UnaryOp) or not isinstance(node.op, ast.Not):
            continue
        call = node.operand
        if not isinstance(call, ast.Call) or call.args or call.keywords:
            continue
        func = call.func
        if not isinstance(func, ast.Attribute) or func.attr != "exists":
            continue
        rel = _path_expr(func.value, path_env)
        if rel is not None:
            absent.add(rel)
    return absent


def dependency_edges(root: Path = ROOT) -> set[tuple[str, str]]:
    """Return (parent, dependency) edges for the repo-owned CI control graph."""
    sources = _ci_sources(root)
    module_to_path = {Path(path).stem: path for path in sources if path.endswith(".py")}
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
            if name in imported or f"{name}.py" in text or re.search(
                rf"(?<![A-Za-z0-9_]){re.escape(name)}(?![A-Za-z0-9_])", text
            ):
                edges.add((parent, target))
    return edges


def dependency_closure(direct: set[str], root: Path = ROOT, edges: set[tuple[str, str]] | None = None) -> set[str]:
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


def _semantic_owner_entry(consumer: str, manifest: dict[str, Any]) -> dict[str, Any] | None:
    """Resolve conventional test/wrapper ownership before considering mixed dependencies."""
    if not consumer.endswith(".py"):
        return None
    explicit = consumer_map(manifest)
    stem = Path(consumer).stem
    candidates: list[str] = []
    if stem.startswith("test_"):
        base = stem[len("test_") :]
        candidates.extend([f"ci/validate_{base}.py", f"ci/{base}.py"])
    if stem.endswith("_test"):
        candidates.append(f"ci/{stem[:-len('_test')]}.py")
    if "_with_" in stem:
        candidates.append(f"ci/{stem.split('_with_', 1)[0]}.py")
    for candidate in candidates:
        row = explicit.get(candidate)
        if row is None:
            continue
        derived = dict(row)
        derived["path"] = consumer
        derived["inherited"] = True
        derived["semantic_owner"] = candidate
        return derived
    return None


def effective_classification_for(
    path: str | Path,
    manifest: dict[str, Any] | None = None,
    *,
    root: Path = ROOT,
    edges: set[tuple[str, str]] | None = None,
) -> dict[str, Any] | None:
    """Resolve explicit state, semantic ownership, or one unambiguous dependency state."""
    manifest = load_manifest() if manifest is None else manifest
    consumer = normalize_consumer(path)
    explicit = classification_for(consumer, manifest)
    if explicit is not None:
        return explicit
    owner = _semantic_owner_entry(consumer, manifest)
    if owner is not None:
        return owner
    entries = _reachable_explicit_entries(consumer, manifest, root=root, edges=edges)
    if not entries:
        return None
    substantive = [row for row in entries if row.get("classification") != "INVARIANT"]
    relevant = substantive or entries
    signatures: set[tuple[str, str | None, str | None]] = set()
    for row in relevant:
        signatures.add((str(row.get("classification")), row.get("snapshot_commit"), row.get("snapshot_blob")))
    if len(signatures) != 1:
        rendered = ", ".join(sorted(f"{cls}:{commit or '-'}:{blob or '-'}" for cls, commit, blob in signatures))
        raise ValueError(f"ambiguous transitive certification state for {consumer}: {rendered}")
    cls, commit, blob = next(iter(signatures))
    row: dict[str, Any] = {"path": consumer, "classification": cls, "inherited": True}
    if cls == "HISTORICAL_SNAPSHOT":
        row["snapshot_commit"] = commit
        row["snapshot_blob"] = blob
    return row


def resolved_consumer_map(manifest: dict[str, Any] | None = None, *, root: Path = ROOT) -> dict[str, dict[str, Any]]:
    manifest = load_manifest() if manifest is None else manifest
    direct = direct_token_consumers(root)
    edges = dependency_edges(root)
    closure = dependency_closure(direct, root, edges)
    resolved: dict[str, dict[str, Any]] = {}
    for path in sorted(closure):
        row = effective_classification_for(path, manifest, root=root, edges=edges)
        if row is None:
            raise ValueError(f"unclassified transitive certification-route consumer: {path}")
        resolved[path] = row
    return resolved


def runtime_classification_for(path: str | Path) -> dict[str, Any] | None:
    consumer = normalize_consumer(path)
    cache_path = os.environ.get("MATHCERT_ROUTE_STATE_RESOLUTIONS")
    if cache_path:
        payload = json.loads(Path(cache_path).read_text(encoding="utf-8"))
        return payload.get("consumers", {}).get(consumer)
    return effective_classification_for(consumer)


def blob_at(commit: str, rel: str = ROUTES_REL) -> str:
    return _git("rev-parse", f"{commit}:{rel}").stdout.strip()


def ensure_commit_available(commit: str) -> None:
    if not HEX40_RE.fullmatch(commit):
        raise ValueError(f"invalid historical snapshot commit: {commit}")
    probe = _git("cat-file", "-e", f"{commit}^{{commit}}", check=False)
    if probe.returncode == 0:
        return
    fetched = _git("fetch", "--no-tags", "--depth=1", "origin", commit, check=False)
    if fetched.returncode != 0:
        detail = fetched.stderr.strip() or fetched.stdout.strip() or "git fetch failed"
        raise ValueError(f"historical snapshot commit unavailable: {commit}: {detail}")
    probe = _git("cat-file", "-e", f"{commit}^{{commit}}", check=False)
    if probe.returncode != 0:
        raise ValueError(f"historical snapshot commit absent after exact fetch: {commit}")
    actual = _git("rev-parse", "--verify", f"{commit}^{{commit}}").stdout.strip()
    if actual != commit:
        raise ValueError(f"historical snapshot identity drift: {actual} != {commit}")


def verify_historical_entry(entry: dict[str, Any]) -> None:
    if entry.get("classification") != "HISTORICAL_SNAPSHOT":
        return
    commit = entry.get("snapshot_commit")
    expected = entry.get("snapshot_blob")
    if not isinstance(commit, str) or not commit:
        raise ValueError("historical consumer lacks snapshot_commit")
    if not isinstance(expected, str) or not expected:
        raise ValueError("historical consumer lacks snapshot_blob")
    ensure_commit_available(commit)
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
            expected = row.get("snapshot_blob")
            pins = source_route_blob_pins(path)
            if len(pins) > 1:
                errors.append(f"ambiguous source route-registry pins for {path}: {sorted(pins)}")
            elif pins and expected not in pins:
                errors.append(
                    f"historical consumer source route pin mismatch: {path}: source={next(iter(pins))} manifest={expected}"
                )
        elif "snapshot_commit" in row or "snapshot_blob" in row:
            errors.append(f"non-historical consumer carries snapshot identity: {path}")
    return errors


def _tree_entry(commit: str, rel: str) -> tuple[str, str] | None:
    proc = _git("ls-tree", commit, "--", rel, check=False)
    line = proc.stdout.strip()
    if proc.returncode != 0 or not line:
        return None
    prefix, _, path = line.partition("\t")
    fields = prefix.split()
    if len(fields) != 3 or path != rel:
        return None
    mode, kind, blob = fields
    if kind != "blob":
        raise ValueError(f"historical state path is not a blob: {rel}: {kind}")
    return mode, blob


def _contract_source_paths(entry: dict[str, Any], *, root: Path = ROOT) -> set[str]:
    consumer = normalize_consumer(entry["path"])
    sources = {consumer}
    owner = entry.get("semantic_owner")
    if isinstance(owner, str) and owner:
        sources.add(normalize_consumer(owner))
    if Path(consumer).suffix.lower() == ".py":
        return sources
    edges = dependency_edges(root)
    deps: dict[str, set[str]] = {}
    for parent, target in edges:
        deps.setdefault(parent, set()).add(target)
    pending = list(deps.get(consumer, set()))
    while pending:
        target = pending.pop()
        if target in sources:
            continue
        sources.add(target)
        pending.extend(deps.get(target, set()) - sources)
    return sources


def historical_state_contract(
    entry: dict[str, Any], *, root: Path = ROOT
) -> tuple[dict[str, tuple[str, str]], set[str], list[str]]:
    """Resolve the exact protected state needed by the current consumer implementation.

    The current CI implementation remains live. Repository state objects explicitly pinned by
    that implementation are read from the exact stage anchor; the route registry is always
    anchored to the manifest snapshot. Paths that the implementation explicitly requires to
    be absent are absent when they were absent at the stage anchor.
    """
    verify_historical_entry(entry)
    commit = str(entry["snapshot_commit"])
    sources = _contract_source_paths(entry, root=root)
    pins: dict[str, str] = {}
    absence_paths: set[str] = set()
    for source in sorted(sources):
        for rel, blob in source_object_pins(source, root=root).items():
            _merge_pin(pins, rel, blob, source=source)
        absence_paths.update(source_absence_paths(source, root=root))
    route_pin = pins.get(ROUTES_REL)
    snapshot_blob = str(entry["snapshot_blob"])
    if route_pin is not None and route_pin != snapshot_blob:
        raise ValueError(
            f"historical consumer route pin disagrees with exact stage: {route_pin} != {snapshot_blob}"
        )
    pins[ROUTES_REL] = snapshot_blob

    entries: dict[str, tuple[str, str]] = {}
    removals: set[str] = set()
    for rel, expected in sorted(pins.items()):
        stage_entry = _tree_entry(commit, rel)
        if stage_entry is None:
            raise ValueError(f"protected historical object absent at stage {commit}: {rel}")
        mode, actual = stage_entry
        if actual != expected:
            raise ValueError(
                f"protected historical object drift at {commit}: {rel}: {actual} != {expected}"
            )
        entries[rel] = (mode, actual)
    for rel in sorted(absence_paths - set(entries)):
        stage_entry = _tree_entry(commit, rel)
        if stage_entry is None:
            removals.add(rel)
        else:
            entries[rel] = stage_entry
    return entries, removals, sorted(sources)


def _synthetic_historical_head(entry: dict[str, Any]) -> tuple[str, str]:
    state_entries, removals, _ = historical_state_contract(entry)
    live_head = _git("rev-parse", "HEAD").stdout.strip()
    live_tree = _git("rev-parse", "HEAD^{tree}").stdout.strip()
    fd, index_path = tempfile.mkstemp(prefix="mathcert-route-view-index-")
    os.close(fd)
    os.unlink(index_path)
    env = {"GIT_INDEX_FILE": index_path}
    try:
        _git("read-tree", live_tree, env=env)
        for rel, (mode, blob) in sorted(state_entries.items()):
            _git("update-index", "--add", "--cacheinfo", f"{mode},{blob},{rel}", env=env)
        for rel in sorted(removals):
            _git("update-index", "--force-remove", "--", rel, env=env, check=False)
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
        input="MC-CERTIFICATION-STATE-ARCHITECTURE-STABILIZATION-001 historical state view\n",
        text=True,
        capture_output=True,
        check=True,
        env={**os.environ, **commit_env},
    )
    synthetic_head = proc.stdout.strip()
    for rel, (_, expected) in state_entries.items():
        actual = _tree_entry(synthetic_head, rel)
        if actual is None or actual[1] != expected:
            raise ValueError(f"synthetic historical state drift: {rel}")
    for rel in removals:
        if _tree_entry(synthetic_head, rel) is not None:
            raise ValueError(f"synthetic historical absence drift: {rel}")
    return live_head, synthetic_head


def _changed_names(*, cached: bool) -> list[str]:
    args = ["diff"]
    if cached:
        args.append("--cached")
    args.extend(["--name-only", "-z", "--diff-filter=ACDMRTUXB"])
    raw = _git(*args).stdout
    return [name for name in raw.split("\0") if name]


def _capture_mode_only_changes(*, label: str) -> dict[str, bool]:
    staged = _changed_names(cached=True)
    if staged:
        raise RuntimeError(f"{label} forbids staged tracked changes: {', '.join(sorted(staged))}")
    modes: dict[str, bool] = {}
    for rel in _changed_names(cached=False):
        head_entry = _tree_entry("HEAD", rel)
        path = ROOT / rel
        if head_entry is None or not path.exists():
            raise RuntimeError(f"{label} forbids tracked content changes: {rel}")
        head_mode, head_blob = head_entry
        work_blob = _git("hash-object", "--", rel, check=False).stdout.strip()
        if not work_blob or work_blob != head_blob:
            raise RuntimeError(f"{label} forbids tracked content changes: {rel}")
        if head_mode not in {"100644", "100755"}:
            raise RuntimeError(f"{label} cannot preserve non-regular mode-only change: {rel}")
        modes[rel] = bool(path.stat().st_mode & stat.S_IXUSR)
    return modes


def _restore_mode_changes(
    incoming: dict[str, bool],
    produced: dict[str, bool],
    *,
    live_head: str,
    synthetic_head: str,
) -> None:
    restore: dict[str, bool] = {}
    for rel, executable in produced.items():
        live = _tree_entry(live_head, rel)
        synthetic = _tree_entry(synthetic_head, rel)
        if live is not None and synthetic is not None and live[1] == synthetic[1]:
            restore[rel] = executable
    restore.update(incoming)
    for rel, executable in restore.items():
        path = ROOT / rel
        live = _tree_entry(live_head, rel)
        if live is None or not path.exists():
            continue
        current = path.stat().st_mode
        if executable:
            os.chmod(path, current | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        else:
            os.chmod(path, current & ~(stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))


@contextmanager
def route_view(entry: dict[str, Any]) -> Iterator[None]:
    if entry.get("classification") != "HISTORICAL_SNAPSHOT":
        yield
        return
    incoming_modes = _capture_mode_only_changes(label="historical state view")
    state_entries, removals, sources = historical_state_contract(entry)
    live_head, synthetic_head = _synthetic_historical_head(entry)
    body_error: BaseException | None = None
    mutation_error: BaseException | None = None
    produced_modes: dict[str, bool] = {}
    _git("checkout", "--detach", "--force", "--quiet", synthetic_head)
    print(
        "MATHCERT_ROUTE_STATE_VIEW="
        f"HISTORICAL_SNAPSHOT consumer={normalize_consumer(entry['path'])} "
        f"commit={entry['snapshot_commit']} blob={entry['snapshot_blob']} "
        f"objects={len(state_entries)} absent={len(removals)} sources={len(sources)} "
        f"inherited={str(bool(entry.get('inherited'))).lower()}",
        file=sys.stderr,
        flush=True,
    )
    try:
        try:
            yield
        except BaseException as exc:
            body_error = exc
        try:
            produced_modes = _capture_mode_only_changes(label="historical consumer")
        except BaseException as exc:
            mutation_error = exc
    finally:
        _git("checkout", "--detach", "--force", "--quiet", live_head)
        _restore_mode_changes(
            incoming_modes,
            produced_modes,
            live_head=live_head,
            synthetic_head=synthetic_head,
        )
    if mutation_error is not None:
        raise mutation_error
    if body_error is not None:
        raise body_error


def _run_with_entry(command: list[str], consumer: str, entry: dict[str, Any] | None) -> int:
    if entry is None:
        return subprocess.call(command, cwd=ROOT)
    cls = entry["classification"]
    if cls != "HISTORICAL_SNAPSHOT":
        owner = entry.get("semantic_owner")
        owner_text = f" semantic_owner={owner}" if owner else ""
        print(
            f"MATHCERT_ROUTE_STATE_VIEW={cls} consumer={consumer} "
            f"inherited={str(bool(entry.get('inherited'))).lower()}{owner_text}",
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
    entry = runtime_classification_for(consumer)
    return _run_with_entry([real_python, *argv], consumer, entry)


def _script_consumer(argv: list[str], suffix: str) -> str | None:
    for arg in argv:
        lowered = arg.lower()
        if lowered in {"-c", "-lc", "-l", "-s", "-file"}:
            continue
        if arg.startswith("-"):
            continue
        if not lowered.endswith(suffix):
            return None
        try:
            return normalize_consumer(arg)
        except ValueError:
            return None
    return None


def _is_route_state_shim(path: str) -> bool:
    return "mathcert-route-state-bin" in Path(path).parts


def _resolve_real_bash() -> str:
    configured = os.environ.get("MATHCERT_REAL_BASH")
    if configured:
        return configured
    for fixed in ("/usr/bin/bash", "/bin/bash"):
        if Path(fixed).is_file():
            return fixed
    found = shutil.which("bash")
    if found and not _is_route_state_shim(found):
        return found
    raise RuntimeError("no non-shim Bash executable available for exec-bash")


def _resolve_real_powershell() -> str:
    configured = os.environ.get("MATHCERT_REAL_POWERSHELL")
    if configured:
        return configured
    for name in ("pwsh", "powershell"):
        found = shutil.which(name)
        if found and not _is_route_state_shim(found):
            return found
    raise RuntimeError("no non-shim PowerShell executable available for exec-pwsh")


def run_bash(argv: list[str]) -> int:
    real_bash = _resolve_real_bash()
    consumer = _script_consumer(argv, ".sh")
    if consumer is None:
        return subprocess.call([real_bash, *argv], cwd=ROOT)
    entry = runtime_classification_for(consumer)
    return _run_with_entry([real_bash, *argv], consumer, entry)


def run_powershell(argv: list[str]) -> int:
    real_powershell = _resolve_real_powershell()
    consumer = _script_consumer(argv, ".ps1")
    if consumer is None:
        return subprocess.call([real_powershell, *argv], cwd=ROOT)
    entry = runtime_classification_for(consumer)
    return _run_with_entry([real_powershell, *argv], consumer, entry)


def resolution_payload() -> dict[str, Any]:
    resolved = resolved_consumer_map()
    return {
        "control_id": "MC-CERTIFICATION-STATE-ARCHITECTURE-STABILIZATION-001",
        "head": _git("rev-parse", "HEAD").stdout.strip(),
        "manifest_blob": _git("rev-parse", f"HEAD:{MANIFEST_REL}").stdout.strip(),
        "consumers": resolved,
    }


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
    if command == "resolve":
        if rest:
            raise ValueError("resolve takes no arguments")
        print(json.dumps(resolution_payload(), sort_keys=True))
        return 0
    if command == "exec":
        return run_python(rest)
    if command == "exec-bash":
        return run_bash(rest)
    if command == "exec-pwsh":
        return run_powershell(rest)
    if command == "classify":
        if len(rest) != 1:
            raise ValueError("classify requires exactly one path")
        row = effective_classification_for(rest[0])
        print("UNCLASSIFIED" if row is None else row["classification"])
        return 0
    raise ValueError(f"unknown command: {command}")


if __name__ == "__main__":
    raise SystemExit(main())
