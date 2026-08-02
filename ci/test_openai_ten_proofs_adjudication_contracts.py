from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

import validate_openai_ten_proofs_route_registrations as route_registration

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_openai_ten_proofs_adjudication_contracts",
    ROOT / "ci/validate_openai_ten_proofs_adjudication_contracts.py",
)
assert SPEC and SPEC.loader
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)


class AdjudicationContractMutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contracts, cls.registry, live_routes = V.defaults()
        cls.routes = route_registration.registration_snapshot(live_routes)
        cls.contract_schema = V.load(V.D.CONTRACT_SCHEMA)
        cls.registry_schema = V.load(V.D.REGISTRY_SCHEMA)
        cls.local_blobs = {
            fam: {
                key: V.D.expected_authority(fam)[key]["digest"]
                for key in ("cert_intake", "cert_work_package", "replay_evidence", "repository_bundle", "route_proposal")
            }
            for fam in V.D.FAMILIES
        }

    def errors(self, **changes):
        return V.validation_errors(
            contracts=copy.deepcopy(changes.get("contracts", self.contracts)),
            registry=copy.deepcopy(changes.get("registry", self.registry)),
            routes=copy.deepcopy(changes.get("routes", self.routes)),
            contract_schema=copy.deepcopy(changes.get("contract_schema", self.contract_schema)),
            registry_schema=copy.deepcopy(changes.get("registry_schema", self.registry_schema)),
            contract_blobs=copy.deepcopy(changes.get("contract_blobs", V.D.CONTRACT_BLOBS)),
            registry_blob=changes.get("registry_blob", V.D.REGISTRY_BLOB),
            route_blob=changes.get("route_blob", V.D.ROUTE_REGISTRY_BLOB),
            receipt_blob=changes.get("receipt_blob", V.D.RECEIPT_BLOB),
            attestation_blob=changes.get("attestation_blob", V.D.ATTESTATION_BLOB),
            document_blob=changes.get("document_blob", V.D.ATTESTATION_DOCUMENT_BLOB),
            local_blobs=copy.deepcopy(changes.get("local_blobs", self.local_blobs)),
            executed_present=changes.get("executed_present", False),
        )

    def test_current_design_passes(self):
        self.assertEqual([], self.errors())

    def mutate_contract(self, family, mutator):
        contracts = copy.deepcopy(self.contracts)
        mutator(contracts[family])
        self.assertTrue(self.errors(contracts=contracts))

    def test_missing_family_rejected(self):
        contracts = copy.deepcopy(self.contracts)
        contracts.pop(V.D.FAMILIES[-1])
        self.assertTrue(self.errors(contracts=contracts))

    def test_premature_may_adjudicate_rejected(self):
        self.mutate_contract(V.D.FAMILIES[0], lambda r: r["state"].__setitem__("may_adjudicate", True))

    def test_adjudication_insertion_rejected(self):
        self.mutate_contract(V.D.FAMILIES[0], lambda r: r["state"].__setitem__("adjudication", {"state": "clear"}))

    def test_cert_output_insertion_rejected(self):
        self.mutate_contract(V.D.FAMILIES[1], lambda r: r["state"].__setitem__("cert_output", {"path": "forged"}))

    def test_proof_promotion_rejected(self):
        self.mutate_contract(V.D.FAMILIES[2], lambda r: r["state"].__setitem__("mathematical_target_proved", True))

    def test_aggregate_adjudication_rejected(self):
        self.mutate_contract(V.D.FAMILIES[2], lambda r: r["state"].__setitem__("aggregate_adjudication", True))

    def test_authority_substitution_rejected(self):
        self.mutate_contract(V.D.FAMILIES[0], lambda r: r["authority"]["route_proposal"].__setitem__("digest", "0" * 40))

    def test_attestation_merge_substitution_rejected(self):
        self.mutate_contract(V.D.FAMILIES[1], lambda r: r["authority"]["post_merge_attestation"].__setitem__("merge_commit", "0" * 40))

    def test_authorization_comment_drift_rejected(self):
        self.mutate_contract(V.D.FAMILIES[2], lambda r: r["authority"]["implementation_authorization"].__setitem__("comment_id", 1))

    def test_target_scope_expansion_rejected(self):
        self.mutate_contract(V.D.FAMILIES[0], lambda r: r["route_scope"]["target_claim_ids"].append("Ehrhart.Stronger"))

    def test_exclusion_removal_rejected(self):
        self.mutate_contract(V.D.FAMILIES[1], lambda r: r["route_scope"].__setitem__("scope_exclusions", ["No limitation."]))

    def test_family_boundary_weakening_rejected(self):
        self.mutate_contract(V.D.FAMILIES[2], lambda r: r["decision_contract"].__setitem__("family_boundary", "All claims clear."))

    def test_required_evidence_removal_rejected(self):
        self.mutate_contract(V.D.FAMILIES[0], lambda r: r["decision_contract"]["required_evidence"].pop())

    def test_reviewer_independence_removal_rejected(self):
        self.mutate_contract(V.D.FAMILIES[1], lambda r: r["reviewer_requirements"].__setitem__("independence", []))

    def test_human_steward_execution_gate_removal_rejected(self):
        self.mutate_contract(V.D.FAMILIES[2], lambda r: r["execution_gate"].__setitem__("separate_human_steward_authorization_required", False))

    def test_claim_boundary_weakening_rejected(self):
        self.mutate_contract(V.D.FAMILIES[0], lambda r: r.__setitem__("claim_boundary", "Certified."))

    def test_contract_blob_substitution_rejected(self):
        blobs = copy.deepcopy(V.D.CONTRACT_BLOBS)
        blobs[V.D.FAMILIES[0]] = "0" * 40
        self.assertTrue(self.errors(contract_blobs=blobs))

    def test_registry_blob_substitution_rejected(self):
        self.assertTrue(self.errors(registry_blob="0" * 40))

    def test_registry_state_inflation_rejected(self):
        registry = copy.deepcopy(self.registry)
        registry["state"]["adjudication_count"] = 1
        self.assertTrue(self.errors(registry=registry))

    def test_registry_contract_digest_drift_rejected(self):
        registry = copy.deepcopy(self.registry)
        registry["contracts"][0]["contract"]["digest"] = "0" * 40
        self.assertTrue(self.errors(registry=registry))

    def test_registry_family_inflation_rejected(self):
        registry = copy.deepcopy(self.registry)
        registry["contracts"].append(copy.deepcopy(registry["contracts"][0]))
        registry["contracts"][-1]["result_family"] = "OTP-A-EXTRA"
        self.assertTrue(self.errors(registry=registry))

    def test_route_registry_substitution_rejected(self):
        self.assertTrue(self.errors(route_blob="0" * 40))

    def test_registration_receipt_substitution_rejected(self):
        self.assertTrue(self.errors(receipt_blob="0" * 40))

    def test_attestation_substitution_rejected(self):
        self.assertTrue(self.errors(attestation_blob="0" * 40))

    def test_executed_adjudication_artifact_rejected(self):
        self.assertTrue(self.errors(executed_present=True))

    def test_route_state_mutation_rejected(self):
        routes = copy.deepcopy(self.routes)
        route = next(r for r in routes["routes"] if r.get("campaign_id") == V.D.FAMILIES[0])
        route["intake_status"] = "qualified"
        self.assertTrue(self.errors(routes=routes))

    def test_route_blocker_removal_rejected(self):
        routes = copy.deepcopy(self.routes)
        route = next(r for r in routes["routes"] if r.get("campaign_id") == V.D.FAMILIES[1])
        route["blockers"] = ["No blockers."]
        self.assertTrue(self.errors(routes=routes))

    def test_open_schema_rejected(self):
        schema = copy.deepcopy(self.contract_schema)
        schema["additionalProperties"] = True
        self.assertTrue(self.errors(contract_schema=schema))


if __name__ == "__main__":
    unittest.main()
