from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_openai_ten_proofs_adjudication_contracts",
    ROOT / "ci/validate_openai_ten_proofs_adjudication_contracts.py",
)
assert SPEC and SPEC.loader
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)

TRANSITION = ROOT / "governance/result_family_output_candidates/staged_route_transitions/OTP-F-EHRHART.json"


class AdjudicationContractMutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contracts, cls.registry, current_routes = V.defaults()
        cls.routes = copy.deepcopy(current_routes)
        before = V.load(TRANSITION)["before"]
        index = next(
            i for i, route in enumerate(cls.routes["routes"])
            if route.get("campaign_id") == "OTP-F-EHRHART"
        )
        cls.routes["routes"][index] = before
        cls.contract_schema = V.load(V.D.CONTRACT_SCHEMA)
        cls.registry_schema = V.load(V.D.REGISTRY_SCHEMA)
        cls.local_blobs = {
            fam: {
                key: V.D.expected_authority(fam)[key]["digest"]
                for key in (
                    "cert_intake", "cert_work_package", "replay_evidence",
                    "repository_bundle", "route_proposal",
                )
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

    def mutate_contract(self, family, mutator):
        contracts = copy.deepcopy(self.contracts)
        mutator(contracts[family])
        self.assertTrue(self.errors(contracts=contracts))

    def test_current_design_passes(self):
        self.assertEqual([], self.errors())

    def test_missing_family_rejected(self):
        contracts = copy.deepcopy(self.contracts)
        contracts.pop(V.D.FAMILIES[-1])
        self.assertTrue(self.errors(contracts=contracts))

    def test_premature_may_adjudicate_rejected(self):
        self.mutate_contract(V.D.FAMILIES[0], lambda r: r["state"].__setitem__("may_adjudicate", True))

    def test_cert_output_insertion_rejected(self):
        self.mutate_contract(V.D.FAMILIES[1], lambda r: r["state"].__setitem__("cert_output", {"path": "forged"}))

    def test_proof_promotion_rejected(self):
        self.mutate_contract(V.D.FAMILIES[2], lambda r: r["state"].__setitem__("mathematical_target_proved", True))

    def test_authority_substitution_rejected(self):
        self.mutate_contract(V.D.FAMILIES[0], lambda r: r["authority"]["route_proposal"].__setitem__("digest", "0" * 40))

    def test_scope_weakening_rejected(self):
        self.mutate_contract(V.D.FAMILIES[0], lambda r: r["route_scope"].__setitem__("scope_exclusions", []))

    def test_reviewer_gate_weakening_rejected(self):
        self.mutate_contract(V.D.FAMILIES[1], lambda r: r["reviewer_requirements"].__setitem__("minimum_binding_non_author_reviewers", 0))

    def test_execution_gate_weakening_rejected(self):
        self.mutate_contract(V.D.FAMILIES[2], lambda r: r["execution_gate"].__setitem__("protected_merge_required", False))

    def test_route_state_promotion_rejected(self):
        routes = copy.deepcopy(self.routes)
        route = next(r for r in routes["routes"] if r["campaign_id"] == "OTP-F-EHRHART")
        route["intake_status"] = "qualified"
        self.assertTrue(self.errors(routes=routes))

    def test_route_output_insertion_rejected(self):
        routes = copy.deepcopy(self.routes)
        route = next(r for r in routes["routes"] if r["campaign_id"] == "OTP-J1-COMPACTNESS")
        route["cert_output"] = {"path": "forged"}
        self.assertTrue(self.errors(routes=routes))

    def test_route_blob_substitution_rejected(self):
        self.assertTrue(self.errors(route_blob="0" * 40))

    def test_registry_blob_substitution_rejected(self):
        self.assertTrue(self.errors(registry_blob="0" * 40))

    def test_local_blob_substitution_rejected(self):
        blobs = copy.deepcopy(self.local_blobs)
        blobs[V.D.FAMILIES[0]]["route_proposal"] = "0" * 40
        self.assertTrue(self.errors(local_blobs=blobs))

    def test_executed_artifact_rejected_by_design_control(self):
        self.assertTrue(self.errors(executed_present=True))

    def test_open_contract_schema_rejected(self):
        schema = copy.deepcopy(self.contract_schema)
        schema["additionalProperties"] = True
        self.assertTrue(self.errors(contract_schema=schema))


if __name__ == "__main__":
    unittest.main()
