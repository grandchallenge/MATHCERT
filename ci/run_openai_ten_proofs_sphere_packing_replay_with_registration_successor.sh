#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
historical="$root/ci/run_openai_ten_proofs_sphere_packing_replay.sh"
historical_routes_blob="2d17473b4731aa9d9c630b1e7777ad4bd794d993"
registration_routes_blob="b9bb0dc9e18856f50a88162df37c20c034327439"
output_routes_blob="4d5c8e3f2b33d5148d98e7057991e167938c75bb"
current_routes_blob="$(git -C "$root" rev-parse HEAD:governance/certification_routes.json)"

if [[ "$current_routes_blob" == "$historical_routes_blob" ]]; then
  exec bash "$historical" "$@"
fi

if [[ "$current_routes_blob" != "$registration_routes_blob" && "$current_routes_blob" != "$output_routes_blob" ]]; then
  echo "ERROR: certification route registry is neither the protected replay-stage snapshot nor an exact governed A successor: $current_routes_blob" >&2
  exit 1
fi

# The output-stage successor additionally proves the exact certificate-content ->
# route-transition publication ancestry and zero proof/aggregate promotion.
if [[ "$current_routes_blob" == "$output_routes_blob" ]]; then
  python3 "$root/ci/otp_a_sphere_packing_output_contract.py"
fi

python3 - "$root" "$current_routes_blob" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
current_routes_blob = sys.argv[2]
registration_routes_blob = 'b9bb0dc9e18856f50a88162df37c20c034327439'
output_routes_blob = '4d5c8e3f2b33d5148d98e7057991e167938c75bb'
routes = json.loads((root / 'governance/certification_routes.json').read_text(encoding='utf-8'))
receipt = json.loads((root / 'governance/pre_route_candidates/OPENAI_TEN_PROOFS_A_SPHERE_PACKING_ROUTE_REGISTRATION.json').read_text(encoding='utf-8'))
replay = json.loads((root / 'governance/result_family_replay_evidence_successors/OTP-A-SPHERE-PACKING.json').read_text(encoding='utf-8'))

expected_targets = [
    'PackingBounds.FullMain.exact_limit',
    'PackingBounds.FullMain.exact_binary_exponent',
    'PackingBounds.PackingBridge.sphere_packing_sharp_asymptotic_upper',
    'PackingBounds.sharpFullCohnElkiesManuscriptConclusions',
]
expected_source = {
    'repository': 'grandchallenge/MATHFORGE',
    'commit_sha': '706d0291370bf3f14aa37be0823e33d06f7343b0',
    'path': 'sources/OPENAI-TEN-PROOFS-001/semantic/OTP-A-SPHERE-PACKING-COMPOSITE/audit_record.json',
    'digest_algorithm': 'git_blob_sha1',
    'digest': 'b2e309ad96e750651fc7149a6bad54c6bf99015b',
}
expected_packet = {
    'repository': 'grandchallenge/MATHSOLVE',
    'commit_sha': 'c19735edf4c16ac9765bb66c7209bbf11bf1312e',
    'path': 'work_packages/OPENAI_TEN_PROOFS_WP00/result_family_handoff_successors/OTP-A-SPHERE-PACKING.json',
    'digest_algorithm': 'git_blob_sha1',
    'digest': '9e3b46972bf01ac3d24c6a0ae5f522799335ecd1',
}
expected_output = {
    'repository': 'grandchallenge/MATHCERT',
    'commit_sha': '1815f1b4010122e5bef0438f84da0b06204ba487',
    'path': 'certificates/formal_sources/MC-OTP-A-SPHERE-PACKING-001.json',
    'digest_algorithm': 'git_blob_sha1',
    'digest': '534e98ad2f00406fc869ea137f802f8cf504798a',
}

assert routes['provider_base_commit'] == '4b194b9632a9aa57fee21c3c054498d6b4a8ed57'
route_rows = routes['routes']
assert len(route_rows) == 13
assert sum(r.get('route_id') == 'MC-ROUTE-OTP-A-SPHERE-PACKING' for r in route_rows) == 1
assert all(r.get('route_id') != 'MC-ROUTE-OPENAI-TEN-PROOFS-001' for r in route_rows)
route = next(r for r in route_rows if r.get('route_id') == 'MC-ROUTE-OTP-A-SPHERE-PACKING')
assert route['campaign_id'] == 'OTP-A-SPHERE-PACKING'
assert route['tracker_issue'] == 'https://github.com/grandchallenge/MATHCERT/issues/158'
assert route['source_manifest'] == expected_source
assert route['intake_packet'] == expected_packet
assert route['target_claim_ids'] == expected_targets
if current_routes_blob == registration_routes_blob:
    assert route['intake_status'] == 'submitted'
    assert route['cert_output'] is None
elif current_routes_blob == output_routes_blob:
    assert route['intake_status'] == 'qualified'
    assert route['cert_output'] == expected_output
else:
    raise AssertionError('unrecognized governed A route successor')

assert receipt['route_id'] == 'MC-ROUTE-OTP-A-SPHERE-PACKING'
assert receipt['authority']['registered_route_registry_before_blob'] == '2d17473b4731aa9d9c630b1e7777ad4bd794d993'
assert receipt['authority']['registered_route_registry_candidate_blob'] == registration_routes_blob
assert receipt['registration']['route_status'] == 'submitted'
assert receipt['registration']['target_claim_ids'] == expected_targets
assert receipt['state'] == {
    'registered_route_count_created_by_this_operation': 1,
    'submitted_route_count': 1,
    'adjudication_count': 0,
    'cert_output_count': 0,
    'mathematical_target_proved_count': 0,
    'aggregate_route_count': 0,
}
controls = receipt['route_controls']
for key in ('may_adjudicate', 'may_issue_cert_output', 'may_mark_target_proved', 'may_promote_claim'):
    assert controls[key] is False
assert controls['aggregate_route_prohibited'] is True

# The protected replay-evidence record remains a historical replay-stage object.
assert replay['route_state'] == {
    'next_eligible_stage_after_protected_readback': 'separate_family_specific_A_route_proposal',
    'requested_future_route_label': 'MC-ROUTE-OTP-A-SPHERE-PACKING',
    'route_proposed': False,
    'certification_route_registry_entry': None,
    'route_registered': False,
    'may_adjudicate': False,
    'adjudication': None,
    'cert_output': None,
    'mathematical_target_proved': False,
    'aggregate_authority': False,
    'may_promote_claim': False,
}
print('A_GOVERNED_ROUTE_SUCCESSOR_COMPATIBILITY=PASS')
print('A_LIVE_ROUTE_STATE=' + route['intake_status'])
print('A_REPLAY_HISTORICAL_ROUTE_STATE=PRESERVED')
PY

# Execute the immutable historical replay harness under its exact historical
# route-registry view. Only the now-obsolete literal-HEAD registry assertion is
# projected away; every source/TCB/build/axiom/Comparator/kernel check remains
# byte-for-byte the protected harness logic.
tmp="$root/ci/.run_openai_ten_proofs_sphere_packing_replay.successor.$$.sh"
trap 'rm -f "$tmp"' EXIT
python3 - "$historical" "$tmp" <<'PY'
import sys
from pathlib import Path

source = Path(sys.argv[1]).read_text(encoding='utf-8')
needle = 'assert_eq "$(git -C "$root" rev-parse HEAD:governance/certification_routes.json)" "$expected_routes_blob" "certification route registry blob"'
replacement = 'echo "A exact governed route successor validated separately; historical replay-stage route-registry assertion projected to its protected snapshot" >&2'
if source.count(needle) != 1:
    raise SystemExit(f'expected exactly one historical route-registry assertion, found {source.count(needle)}')
Path(sys.argv[2]).write_text(source.replace(needle, replacement), encoding='utf-8')
PY
chmod +x "$tmp"
bash "$tmp" "$@"
