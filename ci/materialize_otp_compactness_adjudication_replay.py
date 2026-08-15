#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "ci/run_openai_ten_proofs_family_replay.sh"
EXPECTED_SOURCE_BLOB = "3a1de5e7a9dadeb6b4379ae06550b52895c770b1"

REPLACEMENTS = {
    'observed_manuscript_sha="64b900d5fae6fe22f2ae1b8e3b712d20055194a6c81cf343a2455e5898ac7dd6"':
        'observed_manuscript_sha="ebc561ab5c53dbd240e17a8fdb6fffeb648591eca85dbfc7466f563638f8c566"',
    'observed_manuscript_bytes="2266371"': 'observed_manuscript_bytes="2487031"',
    'source_revision_status="source_revision_drift_detected"': 'source_revision_status="current_official_revision_reacquired"',
    'source_theorem="Chapter 10, Theorem 1.1, parsed P236 L19757-L19791"':
        'source_theorem="Chapter 10, Theorem 1.1, current official PDF P240 / printed p236"',
    'exclusions=("The explicit combinatorial construction is not independently submitted beyond the checked existential targets." "No historical compactness formulation outside the corrected cyclic-family statement is submitted." "Exact concordance with the manuscript revision currently served by the mutable CDN remains pending MATHFORGE issue 52." "A successful formal replay does not by itself adjudicate or prove the mathematical theorem.")':
        'exclusions=("The explicit construction and asymptotic bridge are protected separately by the issue #91 construction-evidence record; this replay does not replace that evidence." "No historical compactness formulation outside the corrected cyclic-family statement is admitted." "Whole-document byte and semantic equivalence among manuscript revisions remain unestablished." "A successful formal replay does not itself adjudicate or prove the mathematical theorem.")',
    '"current_revision_semantic_concordance": "pending"':
        '"current_revision_semantic_concordance": "clear_for_exact_current_locus_under_protected_91_evidence"',
    '"source_revision_concordance": "blocked_pending_forge_audit"':
        '"source_revision_concordance": "clear_for_exact_current_locus"',
    '"status": "pending_source_revision_audit_and_exact_head_non_author_specialist_review"':
        '"status": "current_locus_concordance_clear_pending_adjudication"',
}


def git_blob(path: Path) -> str:
    return subprocess.check_output(["git", "hash-object", str(path)], cwd=ROOT, text=True).strip()


def materialize(destination: Path) -> str:
    actual = git_blob(SOURCE)
    if actual != EXPECTED_SOURCE_BLOB:
        raise RuntimeError(f"shared replay runner drift: expected {EXPECTED_SOURCE_BLOB}, found {actual}")
    text = SOURCE.read_text(encoding="utf-8")
    for old, new in REPLACEMENTS.items():
        count = text.count(old)
        if count != 1:
            raise RuntimeError(f"expected exactly one replay template match, found {count}: {old[:80]}")
        text = text.replace(old, new, 1)
    destination.write_text(text, encoding="utf-8", newline="\n")
    return text


def self_check(text: str) -> None:
    required = [
        'ebc561ab5c53dbd240e17a8fdb6fffeb648591eca85dbfc7466f563638f8c566',
        'observed_manuscript_bytes="2487031"',
        'current_official_revision_reacquired',
        'current official PDF P240 / printed p236',
        'clear_for_exact_current_locus_under_protected_91_evidence',
        'clear_for_exact_current_locus',
    ]
    for needle in required:
        if needle not in text:
            raise RuntimeError(f"materialized replay missing required pin: {needle}")
    if 'pending MATHFORGE issue 52' in text[text.index('OTP-J1-COMPACTNESS'):text.index('OTP-J2-TWO-DEGENERATE')]:
        raise RuntimeError("Compactness replay retained obsolete source-drift blocker")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    text = materialize(args.destination)
    self_check(text)
    print(f"materialized Compactness-only adjudication replay at {args.destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
