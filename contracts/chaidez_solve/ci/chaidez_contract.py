"""Chaidez v2 checks. Structural consistency is not semantic review or proof."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path, PurePosixPath

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.PIPE)


def hashes(data):
    return {"git_blob_sha1": hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest(),
            "sha256": hashlib.sha256(data).hexdigest()}


def safe_path(name):
    if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_.\-/]+", name):
        raise ValueError("unsafe artifact path")
    path = PurePosixPath(name)
    if path.is_absolute() or any(p in (".", "..", ".git") for p in name.split("/")):
        raise ValueError("unsafe artifact path")
    return name


def artifact_bytes(root, ref):
    name = safe_path(ref["path"])
    root = Path(root).resolve()
    path = root / name
    if any(p.is_symlink() for p in [path, *path.parents] if p != root.parent):
        raise ValueError(f"symlink artifact: {name}")
    if not path.is_file() or not path.resolve().is_relative_to(root):
        raise ValueError(f"absent artifact: {name}")
    tracked = git(root, "ls-files", "--stage", "--", name).decode().strip()
    if not tracked or not tracked.startswith(("100644 ", "100755 ")):
        raise ValueError(f"untracked or nonregular artifact: {name}")
    data = path.read_bytes()
    actual = hashes(data)
    if any(ref[k] != actual[k] for k in actual):
        raise ValueError(f"artifact digest drift: {name}")
    # An uncommitted edit cannot borrow the digest of a different tracked blob.
    if tracked.split()[1] != actual["git_blob_sha1"]:
        raise ValueError(f"tracked blob drift: {name}")
    anchor = ref.get("section_anchor")
    if anchor and f'<a id="{anchor}"></a>' not in data.decode("utf-8"):
        raise ValueError(f"missing explicit section anchor: {name}#{anchor}")
    return data


def protected_bytes(roots, ref, *, canary=False):
    repo, commit, artifact = ref["repository"], ref["commit"], ref["artifact"]
    if repo not in roots:
        raise ValueError(f"explicit authenticated repository root required: {repo}")
    root = roots[repo]
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("mutable commit reference")
    if not canary:
        remote = git(root, "remote", "get-url", "origin").decode().strip().removesuffix(".git")
        if remote not in (f"https://github.com/{repo}", f"git@github.com:{repo}"):
            raise ValueError("repository origin mismatch")
    git(root, "merge-base", "--is-ancestor", commit, "refs/remotes/origin/main")
    name = safe_path(artifact["path"])
    tree = git(root, "ls-tree", commit, "--", name).decode()
    if not tree.startswith(("100644 blob ", "100755 blob ")):
        raise ValueError("protected artifact is not a regular Git blob")
    data = git(root, "show", f"{commit}:{name}")
    if any(artifact[k] != value for k, value in hashes(data).items()):
        raise ValueError(f"protected artifact digest drift: {repo}:{name}")
    return data


def schema_errors(document, schema_name, schema_root=ROOT):
    schema = json.loads((Path(schema_root) / "schemas" / schema_name).read_text())
    return [f'{"/".join(map(str, e.absolute_path))}: {e.message}'
            for e in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(document)]


def source_errors(source, roots, *, canary=False):
    try:
        authority = source["programme_import"]
        if authority["repository"] != "grandchallenge/MATH-PROGRAMME" or authority["artifact"]["path"] != "governance/mathforge_external_source_imports.json":
            raise ValueError("wrong Programme import authority")
        imported = json.loads(protected_bytes(roots, authority, canary=canary))
        # An old commit is allowed only while its admitted registry bytes remain current.
        current = git(roots[authority["repository"]], "show", "refs/remotes/origin/main:" + authority["artifact"]["path"])
        if hashes(current)["git_blob_sha1"] != authority["artifact"]["git_blob_sha1"]:
            raise ValueError("stale Programme import identity")
        if imported["registry_id"] != "MATHFORGE-EXTERNAL-SOURCE-IMPORTS" or imported["schema_version"] != "2.0.0":
            raise ValueError("unknown Programme import registry")
        shard = source["catalog_shard"]
        if shard["repository"] != "grandchallenge/MATHFORGE" or shard["commit"] != imported["source_foundry"]["commit"]:
            raise ValueError("MATHFORGE commit is not the admitted foundry commit")
        if source["catalog_release_id"] != imported["catalog_release"]["catalog_release_id"]:
            raise ValueError("catalog release mismatch")
        providers = [p for p in imported["providers"] if p["provider_id"] == source["provider_id"] and p["snapshot_id"] == source["snapshot_id"]]
        if len(providers) != 1:
            raise ValueError("snapshot not uniquely admitted")
        admitted = [{k: a[k] for k in ("path", "git_blob_sha1", "sha256")} for a in providers[0]["catalog_shards"]]
        if shard["artifact"] not in admitted:
            raise ValueError("shard is not admitted by Programme")
        entries = [json.loads(line) for line in protected_bytes(roots, shard, canary=canary).splitlines() if line.strip()]
        matches = [e for e in entries if e["catalog_id"] == source["catalog_id"]]
        if len(matches) != 1:
            raise ValueError("source entry not uniquely accounted")
        entry = matches[0]
        if (entry["provider_id"] != source["provider_id"] or entry["snapshot_id"] != source["snapshot_id"] or
                entry["source"]["raw_sha256"] != source["raw_sha256"] or
                hashlib.sha256(entry["representations"]["normalized"].encode()).hexdigest() != source["normalized_sha256"] or
                entry["assurance"]["tier"] != source["assurance_tier"]):
            raise ValueError("source entry identity, normalization or assurance mismatch")
        if not entry["assurance"].get("reviewer") or not entry["assurance"].get("evidence"):
            raise ValueError("reviewed source requires attributed semantic review evidence")
        if source["exact_campaign_target"]:
            if source["reviewed_relation_id"] not in entry["relation_ids"]:
                raise ValueError("entry does not reference reviewed relation")
            relations = []
            for artifact in imported["catalog_release"]["relation_artifacts"]:
                ref = {"repository": shard["repository"], "commit": shard["commit"], "artifact": artifact}
                relations += json.loads(protected_bytes(roots, ref, canary=canary))["relations"]
            matches = [r for r in relations if r["relation_id"] == source["reviewed_relation_id"]]
            if len(matches) != 1:
                raise ValueError("reviewed relation is not unique")
            relation = matches[0]
            if (relation["review_state"] != "HUMAN_REVIEWED" or not relation.get("reviewer") or not relation.get("evidence") or
                    relation["predicate"] not in ("same_statement", "formalizes") or
                    {relation["subject_id"], relation["object_id"]} != {source["catalog_id"], "GCL-CAMPAIGN:" + source["campaign_id"]}):
                raise ValueError("relation does not establish reviewed exact-target concordance")
        elif source["reviewed_relation_id"] is not None:
            raise ValueError("non-exact proposal must not assert an unchecked relation")
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        return [f"catalog provenance: {exc}"]
    return []


def consistency_errors(d, *, graph_only=False):
    errors = []
    nodes = {n["node_id"]: n for n in d["theorem_spine"]}
    debts = {p["debt_id"]: p for p in d["proof_debt"]}
    claims = {c["claim_id"]: c for c in d.get("local_claims", [])}
    if len(nodes) != len(d["theorem_spine"]) or len(debts) != len(d["proof_debt"]) or len(claims) != len(d.get("local_claims", [])):
        errors.append("duplicate node, claim or debt identifier")
    for node in nodes.values():
        if not set(node["dependencies"]) <= nodes.keys():
            errors.append("unnamed dependency")
        if set(node["proof_debt_ids"]) != {p["debt_id"] for p in debts.values() if p["blocked_node"] == node["node_id"]}:
            errors.append("node/debt accounting mismatch")
    if any(p["blocked_node"] not in nodes for p in debts.values()):
        errors.append("debt blocks unnamed node")
    active = set()
    def visit(n):
        if n in active:
            errors.append("cyclic dependency")
            return set()
        if n not in nodes:
            return set()
        active.add(n)
        closure = {n}
        for child in nodes[n]["dependencies"]:
            closure |= visit(child)
        active.remove(n)
        return closure
    closures = {n: visit(n) for n in nodes}
    for node in nodes.values():
        if node["status"] in ("CHECKED", "PROVED", "REFUTED"):
            closure = closures[node["node_id"]]
            if any(p["status"] == "OPEN" and p["blocked_node"] in closure for p in debts.values()):
                errors.append("completed node has unresolved prerequisite debt")
            if any(nodes[n]["status"] in ("OPEN", "CONDITIONAL") for n in closure):
                errors.append("completed node depends on open/conditional node")
    if graph_only:
        return errors
    for claim in claims.values():
        node = nodes.get(claim["node_id"])
        if node is None or claim["status"] != node["status"]:
            errors.append("claim/node status disagreement")
        expected = {p["debt_id"] for p in debts.values() if p["blocked_node"] in closures.get(claim["node_id"], set())}
        if set(claim["proof_debt_ids"]) != expected:
            errors.append("claim omitted applicable transitive debt")
    status = d["result_status"]
    strongest = claims.get(d["strongest_claim_id"])
    expected_status = {"OPEN": "OPEN", "CONDITIONAL": "CONDITIONAL_RESULT", "CHECKED": "RESTRICTED_RESULT", "PROVED": "RESTRICTED_RESULT", "REFUTED": "NEGATIVE_RESULT"}
    if not strongest or status["strongest_supported_claim"] != strongest["statement"] or status["result_status"] != expected_status[strongest["status"]]:
        errors.append("result status inflates or disagrees with selected local claim")
    if status["result_status"] == "CONDITIONAL_RESULT" and not status["conditional_on"]:
        errors.append("conditional result requires named hypotheses")
    if d["local_node_advanced"] not in nodes or status["first_executable_step"]["node_id"] not in nodes:
        errors.append("local/next executable step must name a spine node")
    elif status["support_route_class"] != nodes[d["local_node_advanced"]]["support_route_class"]:
        errors.append("support route disagreement")
    expected_claims = {
        "WHAT_IS_PROVED": {c for c, v in claims.items() if v["status"] == "PROVED"},
        "WHAT_IS_CHECKED": {c for c, v in claims.items() if v["status"] in ("CHECKED", "PROVED", "REFUTED")},
        "WHAT_REMAINS_OPEN": {c for c, v in claims.items() if v["status"] in ("OPEN", "CONDITIONAL")},
        "WHAT_REQUIRES_EXTERNAL_VERIFICATION": {c for c, v in claims.items() if v["requires_external_verification"]}}
    expected_debts = {
        "WHAT_IS_PROVED": set(),
        "WHAT_IS_CHECKED": {p for p, v in debts.items() if v["status"] == "DISCHARGED"},
        "WHAT_REMAINS_OPEN": {p for p, v in debts.items() if v["status"] == "OPEN"},
        "WHAT_REQUIRES_EXTERNAL_VERIFICATION": {p for p, v in debts.items() if v["status"] == "OPEN" and v["category"] == "EXTERNAL_SOURCE"}}
    for key, answer in d["trust_quartet"].items():
        if set(answer["claim_ids"]) != expected_claims[key] or set(answer["debt_ids"]) != expected_debts[key]:
            errors.append("trust quartet disagrees with claim/debt state: " + key)
    foundation = status["foundational_profile"]
    if foundation["disposition"] == "FOUNDATIONAL_PROFILE_GAP":
        debt = debts.get(foundation["debt_id"], {})
        if debt.get("category") != "FOUNDATIONAL_PROFILE_GAP" or debt.get("status") != "OPEN" or debt.get("blocked_node") != d["local_node_advanced"]:
            errors.append("foundation gap must name active local foundational debt")
    elif any(p["category"] == "FOUNDATIONAL_PROFILE_GAP" and p["status"] == "OPEN" and p["blocked_node"] == d["local_node_advanced"] for p in debts.values()):
        errors.append("foundation profile contradicts active local foundation gap")
    return errors


def bundle_errors(d, root):
    errors, used = [], {}
    try:
        for role, ref in d["required_artifacts"].items():
            artifact_bytes(root, ref)
            used.setdefault(ref["path"], []).append(ref.get("section_anchor"))
        for anchors in used.values():
            if len(anchors) > 1 and (None in anchors or len(set(anchors)) != len(anchors)):
                raise ValueError("shared role files require distinct explicit section anchors")
        for ref in d["review"]["evidence"]:
            artifact_bytes(root, ref)
        # New dossiers use structured sidecars; narrative review remains a reserved act.
        for role, key in (("CLAIM_LEDGER", "local_claims"), ("THEOREM_SPINE", "theorem_spine"), ("PROOF_DEBT_REGISTER", "proof_debt")):
            value = json.loads(artifact_bytes(root, d["required_artifacts"][role]))
            if value.get(key) != d[key]:
                raise ValueError(role + " disagrees with dossier")
        dag = json.loads(artifact_bytes(root, d["required_artifacts"]["DEPENDENCY_DAG"]))
        if dag != {n["node_id"]: n["dependencies"] for n in d["theorem_spine"]}:
            raise ValueError("dependency DAG disagrees with spine")
        handoff = json.loads(artifact_bytes(root, d["required_artifacts"]["CERT_HANDOFF"]))
        if handoff != {"certification_state": "NOT_CERTIFIED", "local_claims": d["local_claims"], "trust_quartet": d["trust_quartet"]}:
            raise ValueError("handoff intent contradicts claim or trust state")
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        errors.append(str(exc))
    return errors
