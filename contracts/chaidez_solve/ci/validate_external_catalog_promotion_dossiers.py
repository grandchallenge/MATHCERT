#!/usr/bin/env python3
"""Fail-closed dossier, registry, and supplemental handoff checks."""
from __future__ import annotations
import argparse
import json
import subprocess
from pathlib import Path
try:
    from ci.chaidez_contract import (ROOT, artifact_bytes, bundle_errors, consistency_errors,
                                    schema_errors, source_errors, protected_bytes)
except ModuleNotFoundError:
    from chaidez_contract import (ROOT, artifact_bytes, bundle_errors, consistency_errors,
                                 schema_errors, source_errors, protected_bytes)

REGISTRY_PATH = "governance/external_catalog_promotion_registry.json"


def validate_document(document, root=ROOT, roots=None, *, canary=False):
    failures = schema_errors(document, "external_catalog_promotion_dossier.schema.json")
    if failures:
        return failures
    if document["record_class"] != ("NON_AUTHORITATIVE_CANARY" if canary else "PRODUCTION"):
        failures.append("canary and production contexts may not cross")
    failures += consistency_errors(document)
    failures += bundle_errors(document, root)
    failures += source_errors(document["catalog_source"], roots or {}, canary=canary)
    return failures


def validate_registry(root=ROOT, roots=None, *, registry_path=REGISTRY_PATH, canary=False):
    try:
        root = Path(root)
        registry = json.loads((root / registry_path).read_text())
        errors = schema_errors(registry, "external_catalog_promotion_registry.schema.json")
        if errors:
            return errors
        entries = registry["promotions"]
        if registry["promotion_count"] != len(entries):
            errors.append("registry promotion_count mismatch")
        ids = [e["promotion_id"] for e in entries]
        paths = [e["dossier"]["path"] for e in entries]
        if len(set(ids)) != len(ids) or len(set(paths)) != len(paths):
            errors.append("duplicate registry promotion or dossier")
        inventory = {p.relative_to(root).as_posix() for p in (root / "promotions/external_catalog").rglob("*.json")}
        if inventory != set(paths):
            errors.append("registry/dossier inventory is not one-to-one")
        for entry in entries:
            if entry["dossier"]["path"] != "promotions/external_catalog/" + entry["promotion_id"] + ".json":
                errors.append("dossier path must identify its unique promotion")
            d = json.loads(artifact_bytes(root, entry["dossier"]))
            if entry["promotion_id"] != d["promotion_id"]:
                errors.append("registry/dossier promotion identity mismatch")
            errors += validate_document(d, root, roots, canary=canary)
        return errors
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        return [str(exc)]


def validate_handoff(h, root=ROOT, roots=None, *, canary=False):
    errors = schema_errors(h, "external_catalog_mathcert_handoff.schema.json")
    if errors:
        return errors
    try:
        registry = json.loads(artifact_bytes(root, h["promotion_registry"]))
        if h["promotion_registry"]["path"] != REGISTRY_PATH:
            errors.append("supplement must consume the production promotion registry")
        errors += validate_registry(root, roots, canary=canary)
        d = json.loads(artifact_bytes(root, h["dossier"]))
        if {"promotion_id": h["promotion_id"], "dossier": h["dossier"]} not in registry["promotions"]:
            errors.append("handoff dossier is not the registered promotion")
        for field in ("promotion_id", "record_class", "catalog_source", "global_theorem_spine_id", "trust_quartet", "non_claim_boundary"):
            if h[field] != d[field]:
                errors.append("handoff/dossier disagreement: " + field)
        if h["selected_claim"] not in d["local_claims"]:
            errors.append("handoff claim inflation")
        claim = h["selected_claim"]
        if h["theorem_spine_node"] != claim["node_id"] or h["proof_debt_ids"] != claim["proof_debt_ids"]:
            errors.append("handoff node/debt omission")
        nodes = {n["node_id"]: n for n in d["theorem_spine"]}
        if h["support_route_class"] != nodes[claim["node_id"]]["support_route_class"]:
            errors.append("handoff support-route disagreement")
        generic = json.loads(artifact_bytes(root, h["generic_handoff"]))
        errors += schema_errors(generic, "mathcert_handoff.schema.json")
        if errors:
            return errors
        if generic["status"] in ("certified", "qualified"):
            errors.append("supplement cannot infer certification from a prior status")
        expected = [{"claim_id": claim["claim_id"], "statement": claim["statement"]}]
        if [{k: c[k] for k in ("claim_id", "statement")} for c in generic["target_claims"]] != expected:
            errors.append("generic handoff does not scope the selected exact local claim")
        if generic["cert_contract"]["route_id"] != h["certification_route_id"]:
            errors.append("generic/supplement route disagreement")
        open_ids = {p["debt_id"] for p in d["proof_debt"] if p["status"] == "OPEN" and p["debt_id"] in claim["proof_debt_ids"]}
        if not open_ids <= set(generic["blockers"]):
            errors.append("generic handoff omits unresolved debt blockers")
        if open_ids and generic["status"] in ("ready", "submitted"):
            errors.append("ready handoff contradicts unresolved proof debt")
        for field, role in (("claim_ledger", "CLAIM_LEDGER"), ("proof_obligations", "DEPENDENCY_DAG")):
            g, ref = generic[field], d["required_artifacts"][role]
            if g["repository"] != "grandchallenge/MATHSOLVE" or g["path"] != ref["path"] or g["digest_algorithm"] != "git_blob_sha1" or g["digest"] != ref["git_blob_sha1"]:
                errors.append("generic handoff does not bind dossier " + field)
            protected_bytes({**(roots or {}), "grandchallenge/MATHSOLVE": root},
                            {"repository": "grandchallenge/MATHSOLVE", "commit": g["commit_sha"], "artifact": ref}, canary=canary)
        for ref in h["local_replay_evidence"] + h["independent_verification"]["evidence"]:
            artifact_bytes(root, ref)
        if h["independent_verification"]["disposition"] == "EVIDENCE_SUBMITTED" and not h["independent_verification"]["evidence"]:
            errors.append("submitted independent verification requires evidence; it is not acceptance")
        if h["independent_verification"]["disposition"] == "REQUIRED_PENDING" and h["independent_verification"]["evidence"]:
            errors.append("pending independent verification contradicts submitted evidence")
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        errors.append(str(exc))
    return errors


def main():
    try:
        from ci.validate_chaidez_documentary_migration import validate_wp06, validate_legacy
    except ModuleNotFoundError:
        from validate_chaidez_documentary_migration import validate_wp06, validate_legacy
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--programme-root", type=Path)
    parser.add_argument("--forge-root", type=Path)
    args = parser.parse_args()
    roots = {k: v for k, v in (("grandchallenge/MATH-PROGRAMME", args.programme_root),
                               ("grandchallenge/MATHFORGE", args.forge_root)) if v}
    failures = validate_registry(ROOT, roots) + validate_wp06() + validate_legacy()
    for path in sorted((ROOT / "cert_handoffs/external_catalog").glob("*.json")):
        failures += validate_handoff(json.loads(path.read_text()), ROOT, roots)
    if failures:
        raise SystemExit("\n".join(failures))
    print("external catalog registry and dossiers reconciled; no certification inferred")


if __name__ == "__main__":
    main()
