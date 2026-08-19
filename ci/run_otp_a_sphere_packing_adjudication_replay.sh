#!/usr/bin/env bash
set -Eeuo pipefail

if (($# != 1)); then
  echo "usage: $0 OUTPUT_DIR" >&2
  exit 64
fi

output_dir="$1"
root="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$output_dir"
output_dir="$(cd "$output_dir" && pwd)"

python3 "$root/ci/validate_otp_a_sphere_packing_adjudication_input.py"
python3 "$root/ci/test_otp_a_sphere_packing_adjudication_input.py"

# Reuse the protected A exact replay harness under the exact registered-route
# successor projection. This retains source/TCB/build/axiom/Comparator/kernel/
# Nanoda semantics while the adjudication layer separately binds current route
# and design-contract authority.
bash "$root/ci/run_openai_ten_proofs_sphere_packing_replay_with_registration_successor.sh" "$output_dir/replay"

INPUT="$root/governance/result_family_adjudication_execution_inputs/OTP-A-SPHERE-PACKING.json" \
CONTRACT="$root/governance/result_family_adjudication_contracts/OTP-A-SPHERE-PACKING.json" \
DESIGN="$root/governance/adjudication_design/OPENAI_TEN_PROOFS_A_SPHERE_PACKING_ADJUDICATION_CONTRACT.json" \
ROUTES="$root/governance/certification_routes.json" \
REPLAY_DIR="$output_dir/replay" \
OUT="$output_dir/adjudication-execution-attestation.json" \
python3 - <<'PY'
import json, os
from pathlib import Path

inp=json.loads(Path(os.environ['INPUT']).read_text(encoding='utf-8'))
contract=json.loads(Path(os.environ['CONTRACT']).read_text(encoding='utf-8'))
design=json.loads(Path(os.environ['DESIGN']).read_text(encoding='utf-8'))
routes=json.loads(Path(os.environ['ROUTES']).read_text(encoding='utf-8'))
replay=Path(os.environ['REPLAY_DIR'])

expected_targets=[
 'PackingBounds.FullMain.exact_limit',
 'PackingBounds.FullMain.exact_binary_exponent',
 'PackingBounds.PackingBridge.sphere_packing_sharp_asymptotic_upper',
 'PackingBounds.sharpFullCohnElkiesManuscriptConclusions',
]
expected_classes=[
 'direct_source_theorem_projection_modulo_proved_full_radial_equivalence',
 'derived_base_two_logarithmic_consequence',
 'source_faithful_displayed_consequence_with_proved_scale_normalization',
 'source_faithful_derived_composite_certificate',
]
expected_axioms=['propext','Quot.sound','Classical.choice']

assert inp['encoded_targets']==expected_targets
assert inp['classifications']==expected_classes
assert inp['permitted_axioms']==expected_axioms
assert inp['nonvacuity_state']=='clear_for_current_root_four_target_surface'
assert inp['decision_contract']['disposition_at_input_stage'] is None
assert inp['required_state']['route_state']=='submitted'
assert inp['required_state']['cert_output'] is None
assert inp['required_state']['mathematical_target_proved'] is False
assert inp['required_state']['may_promote_claim'] is False
assert inp['required_state']['manuscript_decimal_precision_attributed'] is False
assert inp['required_state']['scale_normalization_boundary_required'] is True
assert inp['required_state']['composite_is_single_verbatim_source_theorem'] is False
assert inp['execution_recipe']['separate_human_steward_authorization_required'] is False
assert inp['execution_recipe']['execution_authorized_by_protected_contract'] is True

assert contract['route_scope']['target_claim_ids']==expected_targets
assert contract['route_scope']['classifications']==expected_classes
assert contract['route_scope']['permitted_axioms']==expected_axioms
assert contract['route_scope']['nonvacuity_state']=='clear_for_current_root_four_target_surface'
assert contract['execution_gate']['routine_stage_progression_without_human_steward_intervention'] is True
assert contract['execution_gate']['human_steward_intervention_required_for_control_plan_change'] is True
assert contract['state']['cert_output'] is None

assert design['activation']['routine_stage_progression_without_human_steward_intervention'] is True
assert design['activation']['human_steward_intervention_required_for_control_plan_change'] is True

route=next(r for r in routes['routes'] if r.get('route_id')=='MC-ROUTE-OTP-A-SPHERE-PACKING')
assert route['intake_status']=='submitted'
assert route['target_claim_ids']==expected_targets
assert route['cert_output'] is None

comp=json.loads((replay/'comparator-result.json').read_text(encoding='utf-8'))
assert comp=={
 'comparator':'accept',
 'lean_default_kernel':'accept',
 'nanoda':'accept',
 'otp_successor_comparator':'ACCEPT',
}
summary=json.loads((replay/'evidence-summary.json').read_text(encoding='utf-8'))
assert summary['target_count']==4
assert summary['solution_build']=='pass'
assert summary['theorem_axioms']=='permitted_only'
assert summary['comparator']=='accept'
assert summary['lean_default_kernel']=='accept'
assert summary['nanoda']=='accept'
assert summary['trust_boundary_scan']=='clear'
assert summary['source_pdf_identity']=='exact_2026_08_06_bytes_reacquired'
sem=json.loads((replay/'semantic-concordance-attestation.json').read_text(encoding='utf-8'))
assert sem['classifications']==expected_classes
assert sem['independent_source_reclassification_performed'] is False
assert sem['whole_chapter_equivalence'] is False
assert sem['full_proof_body_equivalence'] is False
nv=json.loads((replay/'nonvacuity-attestation.json').read_text(encoding='utf-8'))
assert nv['state']=='clear_bound_to_protected_current_root_evidence'

obj={
 'schema_version':'1.0.0',
 'operation_id':'OTP-A-SPHERE-PACKING-ADJUDICATION-EXECUTION-001',
 'input_id':'MC-OTP-A-SPHERE-PACKING-ADJUDICATION-EXECUTION-INPUT-001',
 'mathcert_head':os.environ.get('MATHCERT_HEAD_SHA','unknown'),
 'source_identity':'exact_2026_08_06_bytes_reacquired',
 'targets':expected_targets,
 'classifications':expected_classes,
 'source_to_formal_concordance':'clear_under_protected_target_by_target_classifications',
 'decimal_provenance':'clear_formal_only_not_manuscript_precision',
 'scale_normalization':'clear_positive_rescaling_and_unit_separation_equivalence_required',
 'little_o':'clear_explicit_witness_is_normal_form_only',
 'composite_boundary':'clear_mixed_source_derived_not_single_verbatim_theorem',
 'nonvacuity':'clear_for_current_root_four_target_surface',
 'permitted_axioms':expected_axioms,
 'solution_build':'pass',
 'comparator':'accept',
 'lean_default_kernel':'accept',
 'nanoda':'accept',
 'trust_boundary':'clear',
 'route_state':'submitted',
 'cert_output':None,
 'mathematical_target_proved':False,
 'may_promote_claim':False,
 'aggregate_authority':False,
 'adjudication_disposition':None,
 'control_plan_conformance':'clear',
 'separate_human_steward_authorization_required':False,
 'human_steward_intervention_required_only_for_control_plan_change':True,
}
Path(os.environ['OUT']).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')
PY

(
  cd "$output_dir"
  sha256sum adjudication-execution-attestation.json replay/bundle.tar.gz replay/SHA256SUMS | LC_ALL=C sort > SHA256SUMS
)
tar --sort=name --mtime='UTC 1970-01-01' --owner=0 --group=0 --numeric-owner \
  --exclude='adjudication-bundle.tar.gz' -C "$(dirname "$output_dir")" -cf - "$(basename "$output_dir")" | gzip -n > "$output_dir/adjudication-bundle.tar.gz"
sha256sum "$output_dir/adjudication-bundle.tar.gz" > "$output_dir/adjudication-bundle.sha256"

echo "A_ADJUDICATION_EXECUTION_EVIDENCE=PASS"
echo "A_ADJUDICATION_DISPOSITION=UNSET"
