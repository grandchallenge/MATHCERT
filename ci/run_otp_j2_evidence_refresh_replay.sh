#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
out="${1:-$root/evidence/j2-evidence-refresh-runtime}"
mkdir -p "$out"
out="$(cd "$out" && pwd)"
formal="$out/formal-replay"
mkdir -p "$formal"

python3 "$root/ci/build_otp_j2_construction_evidence.py" > "$out/construction-producer.json"
python3 "$root/ci/verify_otp_j2_construction_evidence.py" > "$out/construction-verifier.txt"

"$root/ci/run_otp_j2_scope_repair_replay.sh" "$formal"

python3 - "$root" "$out" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
out = Path(sys.argv[2])

def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()

source = root / "evidence/openai_ten_proofs/two_degenerate_construction/source_authority.json"
recon = root / "evidence/openai_ten_proofs/two_degenerate_construction/reconstruction.json"
ledger = root / "evidence/openai_ten_proofs/two_degenerate_construction/proof_dependency_ledger.json"
projection = root / "evidence/openai_ten_proofs/two_degenerate_scope_repair/SourceFaithfulProjection.lean"
formal = json.loads((out / "formal-replay/replay-summary.json").read_text(encoding="utf-8"))
producer = json.loads((out / "construction-producer.json").read_text(encoding="utf-8"))

assert formal["lean_kernel"] == "accept"
assert formal["nanoda_registered_targets"] == "accept"
assert formal["source_faithful_projection"] == "accept"
assert formal["dependency_separation"] == "accept"
assert formal["source_attribution_of_coloring_conjunct"] is False
assert producer["graph"]["connected"] is True
assert producer["graph"]["parity_coloring_proper"] is True
assert producer["graph"]["two_degenerate_exemplar"] is True
assert producer["algebra"]["exponent_identity_exact"] is True
assert producer["algebra"]["parameter_window_exact"]["f_tau_positive"] is True

summary = {
    "schema_version": "1.0.0",
    "operation_id": "OTP-J2-TWO-DEGENERATE-CERT-EVIDENCE-REFRESH-001",
    "result_family": "OTP-J2-TWO-DEGENERATE",
    "source_authority_git_blob_sha1": blob(source),
    "reconstruction_git_blob_sha1": blob(recon),
    "proof_dependency_ledger_git_blob_sha1": blob(ledger),
    "projection_git_blob_sha1": blob(projection),
    "current_manuscript_sha256": formal["current_manuscript_sha256"],
    "upstream_commit": formal["upstream_commit"],
    "upstream_tree": formal["upstream_tree"],
    "comparator": formal["registered_target_comparator"],
    "lean_kernel": formal["lean_kernel"],
    "nanoda": formal["nanoda_registered_targets"],
    "source_faithful_projection": formal["source_faithful_projection"],
    "dependency_separation": formal["dependency_separation"],
    "construction_layered_graph": "independent_reconstruction_and_machine_sample_check_clear",
    "parameter_window": "exact_positivity_reduction_clear",
    "exponent_bridge": "exact_coefficient_identity_clear",
    "padding_bridge": "clear",
    "extremal_interpretation": "independently_reconstructed",
    "substantive_mathematical_gap_found": False,
    "stronger_coloring_property_source_attributed": False,
    "stronger_coloring_property_certified": False,
    "proof_body_compared_in_full": False,
    "route_effect": "none",
    "adjudication_effect": "none",
    "cert_output_effect": "none",
    "mathematical_proof_promotion_effect": "none"
}
(out / "evidence-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY

find "$out" -type f ! -name 'SHA256SUMS' -print0 | sort -z | xargs -0 sha256sum > "$out/SHA256SUMS"
echo "J2 source-faithful evidence refresh replay complete; route/adjudication/output state unchanged"
