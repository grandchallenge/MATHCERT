#!/usr/bin/env python3
from __future__ import annotations

import copy
import unittest

import validate_openai_ten_proofs_sphere_packing_route_registration as validator


class SpherePackingRouteRegistrationAndAdjudicationDesignTests(unittest.TestCase):
    def receipt(self):
        return validator.load(validator.RECEIPT)

    def routes(self):
        return validator.load(validator.ROUTES)

    def contract(self):
        return validator.load(validator.DESIGN_CONTRACT)

    def registry(self):
        return validator.load(validator.DESIGN_REGISTRY)

    def blobs(self):
        return {
            "routes": validator.EXPECTED_ROUTES_BLOB,
            "proposal": validator.EXPECTED_PROPOSAL_BLOB,
            "proposal_registry": validator.EXPECTED_PROPOSAL_REGISTRY_BLOB,
            "replay": validator.EXPECTED_REPLAY_BLOB,
        }

    def design_blobs(self):
        return {
            "contract": validator.EXPECTED_DESIGN_CONTRACT_BLOB,
            "registry": validator.EXPECTED_DESIGN_REGISTRY_BLOB,
            "routes": validator.EXPECTED_ROUTES_BLOB,
            "registration_receipt": validator.EXPECTED_REGISTRATION_RECEIPT_BLOB,
            "proposal": validator.EXPECTED_PROPOSAL_BLOB,
            "proposal_registry": validator.EXPECTED_PROPOSAL_REGISTRY_BLOB,
            "replay": validator.EXPECTED_REPLAY_BLOB,
        }

    def errors(self, receipt=None, routes=None, blobs=None, contract=None, registry=None, design_blobs=None):
        return validator.validation_errors(
            receipt or self.receipt(),
            routes or self.routes(),
            blobs or self.blobs(),
            design_contract=contract or self.contract(),
            design_registry=registry or self.registry(),
            design_blobs=design_blobs or self.design_blobs(),
        )

    def design_errors(self, contract=None, registry=None, design_blobs=None):
        return validator.design_validation_errors(
            contract or self.contract(),
            registry or self.registry(),
            design_blobs or self.design_blobs(),
        )

    def test_current_passes(self):
        self.assertEqual(self.errors(), [])

    def test_registry_blob_drift_rejected(self):
        b = self.blobs(); b["routes"] = "0" * 40
        self.assertTrue(self.errors(blobs=b))

    def test_proposal_blob_drift_rejected(self):
        b = self.blobs(); b["proposal"] = "0" * 40
        self.assertTrue(self.errors(blobs=b))

    def test_replay_blob_drift_rejected(self):
        b = self.blobs(); b["replay"] = "0" * 40
        self.assertTrue(self.errors(blobs=b))

    def test_target_substitution_rejected(self):
        r = self.routes(); r["routes"][-1]["target_claim_ids"][0] = "Fake.target"
        self.assertTrue(self.errors(routes=r))

    def test_target_reordering_rejected(self):
        rec = self.receipt(); rec["registration"]["target_claim_ids"] = list(reversed(rec["registration"]["target_claim_ids"]))
        self.assertTrue(self.errors(receipt=rec))

    def test_composite_semantic_drift_rejected(self):
        rec = self.receipt(); rec["authority"]["forge_composite_semantic"]["digest"] = "0" * 40
        self.assertTrue(self.errors(receipt=rec))

    def test_bridge_semantic_drift_rejected(self):
        rec = self.receipt(); rec["authority"]["forge_bridge_semantic"]["digest"] = "0" * 40
        self.assertTrue(self.errors(receipt=rec))

    def test_solve_handoff_drift_rejected(self):
        rec = self.receipt(); rec["authority"]["solve_handoff"]["digest"] = "0" * 40
        self.assertTrue(self.errors(receipt=rec))

    def test_route_status_inflation_rejected(self):
        r = self.routes(); r["routes"][-1]["intake_status"] = "qualified"
        self.assertTrue(self.errors(routes=r))

    def test_cert_output_insertion_rejected(self):
        r = self.routes(); r["routes"][-1]["cert_output"] = {"fake": True}
        self.assertTrue(self.errors(routes=r))

    def test_registration_adjudication_authority_rejected(self):
        rec = self.receipt(); rec["route_controls"]["may_adjudicate"] = True
        self.assertTrue(self.errors(receipt=rec))

    def test_registration_proof_promotion_rejected(self):
        rec = self.receipt(); rec["route_controls"]["may_mark_target_proved"] = True
        self.assertTrue(self.errors(receipt=rec))

    def test_registration_claim_promotion_rejected(self):
        rec = self.receipt(); rec["route_controls"]["may_promote_claim"] = True
        self.assertTrue(self.errors(receipt=rec))

    def test_registration_composite_reclassification_rejected(self):
        rec = self.receipt(); rec["route_controls"]["may_reclassify_composite_as_verbatim_source_theorem"] = True
        self.assertTrue(self.errors(receipt=rec))

    def test_registration_decimal_source_attribution_rejected(self):
        rec = self.receipt(); rec["route_controls"]["may_attribute_decimal_precision_to_source"] = True
        self.assertTrue(self.errors(receipt=rec))

    def test_registration_normalization_erasure_rejected(self):
        rec = self.receipt(); rec["route_controls"]["may_remove_scale_normalization_boundary"] = True
        self.assertTrue(self.errors(receipt=rec))

    def test_aggregate_route_rejected(self):
        r = self.routes(); r["routes"].append({"route_id":"MC-ROUTE-OPENAI-TEN-PROOFS-001"})
        self.assertTrue(self.errors(routes=r))

    def test_registration_schema_rejects_extra_property(self):
        rec = self.receipt(); rec["unexpected"] = True
        self.assertTrue(self.errors(receipt=rec))

    def test_design_contract_blob_drift_rejected(self):
        b = self.design_blobs(); b["contract"] = "0" * 40
        self.assertTrue(self.design_errors(design_blobs=b))

    def test_design_registry_blob_drift_rejected(self):
        b = self.design_blobs(); b["registry"] = "0" * 40
        self.assertTrue(self.design_errors(design_blobs=b))

    def test_design_preserves_exact_route_registry_blob(self):
        b = self.design_blobs(); b["routes"] = "0" * 40
        self.assertTrue(self.design_errors(design_blobs=b))

    def test_design_target_substitution_rejected(self):
        c = self.contract(); c["route_scope"]["target_claim_ids"][0] = "Fake.target"
        self.assertTrue(self.design_errors(contract=c))

    def test_design_target_reordering_rejected(self):
        c = self.contract(); c["route_scope"]["target_claim_ids"] = list(reversed(c["route_scope"]["target_claim_ids"]))
        self.assertTrue(self.design_errors(contract=c))

    def test_design_classification_reordering_rejected(self):
        c = self.contract(); c["route_scope"]["classifications"] = list(reversed(c["route_scope"]["classifications"]))
        self.assertTrue(self.design_errors(contract=c))

    def test_design_route_qualification_rejected(self):
        c = self.contract(); c["route_scope"]["registered_route_state"] = "qualified"
        self.assertTrue(self.design_errors(contract=c))

    def test_design_adjudication_authority_rejected(self):
        c = self.contract(); c["state"]["may_adjudicate"] = True
        self.assertTrue(self.design_errors(contract=c))

    def test_design_adjudication_insertion_rejected(self):
        c = self.contract(); c["state"]["adjudication"] = {"fake": True}
        self.assertTrue(self.design_errors(contract=c))

    def test_design_cert_output_insertion_rejected(self):
        c = self.contract(); c["state"]["cert_output"] = {"fake": True}
        self.assertTrue(self.design_errors(contract=c))

    def test_design_proof_promotion_rejected(self):
        c = self.contract(); c["state"]["mathematical_target_proved"] = True
        self.assertTrue(self.design_errors(contract=c))

    def test_design_claim_promotion_rejected(self):
        c = self.contract(); c["state"]["may_promote_claim"] = True
        self.assertTrue(self.design_errors(contract=c))

    def test_design_aggregate_authority_rejected(self):
        c = self.contract(); c["state"]["aggregate_adjudication"] = True
        self.assertTrue(self.design_errors(contract=c))

    def test_design_decimal_source_attribution_rejected(self):
        c = self.contract(); c["preserved_limitations"]["manuscript_decimal_precision_attributed"] = True
        self.assertTrue(self.design_errors(contract=c))

    def test_design_normalization_erasure_rejected(self):
        c = self.contract(); c["preserved_limitations"]["scale_normalization_boundary_required"] = False
        self.assertTrue(self.design_errors(contract=c))

    def test_design_composite_reclassification_rejected(self):
        c = self.contract(); c["preserved_limitations"]["composite_is_single_verbatim_source_theorem"] = True
        self.assertTrue(self.design_errors(contract=c))

    def test_design_axiom_inflation_rejected(self):
        c = self.contract(); c["route_scope"]["permitted_axioms"].append("sorryAx")
        self.assertTrue(self.design_errors(contract=c))

    def test_design_nonvacuity_weakening_rejected(self):
        c = self.contract(); c["route_scope"]["nonvacuity_state"] = "unknown"
        self.assertTrue(self.design_errors(contract=c))

    def test_design_separate_human_steward_execution_gate_required(self):
        c = self.contract(); c["execution_gate"]["separate_human_steward_authorization_required"] = False
        self.assertTrue(self.design_errors(contract=c))

    def test_design_exact_execution_head_authorization_required(self):
        c = self.contract(); c["execution_gate"]["authorization_must_name_contract_and_exact_execution_head"] = False
        self.assertTrue(self.design_errors(contract=c))

    def test_design_non_author_review_required(self):
        c = self.contract(); c["execution_gate"]["fresh_non_author_approval_required"] = False
        self.assertTrue(self.design_errors(contract=c))

    def test_design_registry_contract_digest_rejected(self):
        r = self.registry(); r["contracts"][0]["contract"]["digest"] = "0" * 40
        self.assertTrue(self.design_errors(registry=r))

    def test_design_registry_authority_inflation_rejected(self):
        r = self.registry(); r["controls"]["may_adjudicate"] = True
        self.assertTrue(self.design_errors(registry=r))

    def test_design_registry_later_authorization_removal_rejected(self):
        r = self.registry(); r["activation"]["later_execution_requires_separate_human_steward_authorization"] = False
        self.assertTrue(self.design_errors(registry=r))

    def test_design_contract_schema_rejects_extra_property(self):
        c = self.contract(); c["unexpected"] = True
        self.assertTrue(self.design_errors(contract=c))

    def test_design_registry_schema_rejects_extra_property(self):
        r = self.registry(); r["unexpected"] = True
        self.assertTrue(self.design_errors(registry=r))


if __name__ == "__main__":
    unittest.main()
