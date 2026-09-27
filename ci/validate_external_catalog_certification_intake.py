#!/usr/bin/env python3
"""Receive a protected, scoped Solve promotion. Never produce a certificate."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "contracts/chaidez_solve"
SOURCE = ROOT / "governance/external_catalog_solve_contract.json"
INTAKES = ROOT / "governance/external_catalog_certification_intakes.json"
ROUTES = ROOT / "governance/certification_routes.json"


def load_gate():
    """Use the pinned Solve implementation, not a second interpretation of its gate."""
    manifest = json.loads(SOURCE.read_text())
    for name in ("ci/chaidez_contract.py", "ci/validate_external_catalog_promotion_dossiers.py"):
        expected = [r for r in manifest["files"] if r["path"] == name]
        raw = (VENDOR / name).read_bytes()
        actual = {"git_blob_sha1": hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest(),
                  "sha256": hashlib.sha256(raw).hexdigest()}
        if len(expected) != 1 or any(expected[0][k] != v for k, v in actual.items()):
            raise ValueError("refusing to load modified Solve gate: " + name)
    sys.path.insert(0, str(VENDOR / "ci"))
    try:
        spec = importlib.util.spec_from_file_location("external_catalog_solve_gate", VENDOR / "ci/validate_external_catalog_promotion_dossiers.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.pop(0)


GATE = load_gate()
BYTES = sys.modules[GATE.artifact_bytes.__module__]


def source_contract_errors(roots=None):
    try:
        contract = json.loads(SOURCE.read_text())
        if contract["repository"] != "grandchallenge/MATHSOLVE" or contract["schema_version"] != "2.0.0":
            raise ValueError("wrong Solve contract authority")
        names = [r["path"] for r in contract["files"]]
        if len(names) != len(set(names)):
            raise ValueError("duplicate vendored contract path")
        discovered = {p.relative_to(VENDOR).as_posix() for p in VENDOR.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
        if set(names) != discovered:
            raise ValueError("vendored Solve contract inventory mismatch")
        for ref in contract["files"]:
            path = VENDOR / BYTES.safe_path(ref["path"])
            if any(ref[k] != v for k, v in BYTES.hashes(path.read_bytes()).items()):
                raise ValueError("vendored Solve artifact drift: " + ref["path"])
            if roots is not None:
                BYTES.protected_bytes(roots, {"repository": contract["repository"], "commit": contract["commit"], "artifact": ref})
        return []
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        return [str(exc)]


def validate_intake(record, roots, *, canary=False, routes=None):
    schema = json.loads((ROOT / "schemas/external_catalog_certification_intake.schema.json").read_text())
    errors = [f'{"/".join(map(str, e.absolute_path))}: {e.message}' for e in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(record)]
    if errors:
        return errors
    if record["record_class"] != ("NON_AUTHORITATIVE_CANARY" if canary else "PRODUCTION"):
        errors.append("canary is not a production certification intake")
    if routes is not None and not canary:
        errors.append("production route registry cannot be overridden")
    if not canary:
        errors += source_contract_errors(roots)
    try:
        solve = roots["grandchallenge/MATHSOLVE"]
        def read(ref):
            return BYTES.protected_bytes(roots, {"repository": "grandchallenge/MATHSOLVE", "commit": record["solve_commit"], "artifact": ref}, canary=canary)
        registry = json.loads(read(record["promotion_registry"]))
        dossier = json.loads(read(record["dossier"]))
        handoff = json.loads(read(record["supplemental_handoff"]))
        if record["promotion_registry"]["path"] != GATE.REGISTRY_PATH:
            errors.append("intake must consume the authoritative Solve promotion registry")
        if {"promotion_id": record["promotion_id"], "dossier": record["dossier"]} not in registry["promotions"]:
            errors.append("direct or unregistered catalog intake")
        errors += GATE.validate_handoff(handoff, solve, roots, canary=canary)
        for field in ("record_class", "promotion_registry", "dossier", "promotion_id", "catalog_source", "selected_claim",
                      "global_theorem_spine_id", "theorem_spine_node", "proof_debt_ids", "trust_quartet", "support_route_class",
                      "local_replay_evidence", "certification_route_id", "independent_verification", "non_claim_boundary"):
            if record[field] != handoff[field]:
                errors.append("receiving record disagrees with protected handoff: " + field)
        # Every local evidence file must actually exist in the same protected Solve commit.
        evidence = list(dossier["required_artifacts"].values()) + dossier["review"]["evidence"]
        evidence += handoff["local_replay_evidence"] + handoff["independent_verification"]["evidence"] + [handoff["generic_handoff"]]
        for ref in evidence:
            read(ref)
        route_registry = json.loads(ROUTES.read_text()) if routes is None else routes
        matches = [r for r in route_registry["routes"] if r["route_id"] == record["certification_route_id"]]
        if len(matches) != 1:
            errors.append("certification route must be uniquely registered")
        else:
            route = matches[0]
            if route["campaign_id"] != record["catalog_source"]["campaign_id"] or record["selected_claim"]["claim_id"] not in route["target_claim_ids"]:
                errors.append("registered route does not authorize this exact local claim and campaign")
        open_ids = {d["debt_id"] for d in dossier["proof_debt"] if d["status"] == "OPEN" and d["debt_id"] in record["proof_debt_ids"]}
        expected = "HOLD_FOR_PROOF_DEBT" if open_ids else "AWAITING_INDEPENDENT_VERIFICATION"
        if record["disposition"] != expected:
            errors.append("intake disposition hides debt or infers verification")
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        errors.append(str(exc))
    return errors


def validate_registry(roots=None):
    errors = source_contract_errors()
    try:
        data = json.loads(INTAKES.read_text())
        if set(data) != {"schema_version", "registry_id", "intake_count", "intakes"} or data["schema_version"] != "2.0.0" or data["registry_id"] != "MC-EXTERNAL-CATALOG-INTAKES":
            raise ValueError("unknown external catalog certification registry")
        paths = [r["path"] for r in data["intakes"]]
        discovered = {p.relative_to(ROOT).as_posix() for p in (ROOT / "intakes/external_catalog").rglob("*.json")}
        if type(data["intake_count"]) is not int or data["intake_count"] != len(paths) or len(set(paths)) != len(paths) or set(paths) != discovered:
            raise ValueError("intake registry inventory/count mismatch")
        ids = []
        for ref in data["intakes"]:
            record = json.loads(BYTES.artifact_bytes(ROOT, ref))
            ids.append(record["intake_id"])
            errors += validate_intake(record, roots or {})
        if len(set(ids)) != len(ids):
            errors.append("duplicate intake ID")
    except (ValueError, KeyError, TypeError, OSError, subprocess.CalledProcessError) as exc:
        errors.append(str(exc))
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--solve-root", type=Path)
    parser.add_argument("--programme-root", type=Path)
    parser.add_argument("--forge-root", type=Path)
    parser.add_argument("--intake", type=Path)
    args = parser.parse_args()
    roots = {"grandchallenge/" + name: root for name, root in (("MATHSOLVE", args.solve_root), ("MATH-PROGRAMME", args.programme_root), ("MATHFORGE", args.forge_root)) if root}
    errors = validate_intake(json.loads(args.intake.read_text()), roots) if args.intake else validate_registry(roots)
    if errors:
        raise SystemExit("\n".join(errors))
    print("external-catalog receiving contract replayed; no certification issued or inferred")


if __name__ == "__main__":
    main()
