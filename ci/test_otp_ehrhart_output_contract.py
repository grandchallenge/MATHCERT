from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_COMMIT = "686a48bb49015e4b8558bbc83d182f21f8b9e097"
SPEC = importlib.util.spec_from_file_location(
    "validate_otp_ehrhart_output_contract",
    ROOT / "ci/validate_otp_ehrhart_output_contract.py",
)
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


def git(*args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(["git", *args], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def protected_routes() -> dict:
    shallow = git("rev-parse", "--is-shallow-repository")
    if shallow.returncode == 0 and shallow.stdout.decode().strip() == "true":
        git("fetch", "--no-tags", "--unshallow", "origin")
    if git("cat-file", "-e", f"{SNAPSHOT_COMMIT}^{{commit}}").returncode != 0:
        git("fetch", "--no-tags", "origin", SNAPSHOT_COMMIT)
    result = git("show", f"{SNAPSHOT_COMMIT}:governance/certification_routes.json")
    if result.returncode != 0:
        raise RuntimeError("unable to load protected route snapshot")
    return json.loads(result.stdout)


class OTPEhrhartOutputContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = M.load(M.CONTRACT)
        self.contract_schema = M.load(M.CONTRACT_SCHEMA)
        self.future_schema = M.load(M.FUTURE_SCHEMA)
        self.routes = protected_routes()
        self.adjudication = M.load(M.ADJUDICATION)
        self.attestation = M.load(M.ATTESTATION)

    def errors(self, **kwargs):
        return M.validation_errors(
            contract=copy.deepcopy(kwargs.get("contract", self.contract)),
            contract_schema=copy.deepcopy(kwargs.get("contract_schema", self.contract_schema)),
            future_schema=copy.deepcopy(kwargs.get("future_schema", self.future_schema)),
            routes=copy.deepcopy(kwargs.get("routes", self.routes)),
            adjudication=copy.deepcopy(kwargs.get("adjudication", self.adjudication)),
            attestation=copy.deepcopy(kwargs.get("attestation", self.attestation)),
            adjudication_blob=kwargs.get("adjudication_blob", M.EXPECTED_ADJUDICATION_BLOB),
            attestation_blob=kwargs.get("attestation_blob", M.EXPECTED_ATTESTATION_BLOB),
            future_schema_blob=kwargs.get("future_schema_blob", M.EXPECTED_FUTURE_SCHEMA_BLOB),
            future_certificate_present=kwargs.get("future_certificate_present", False),
            candidate_present=kwargs.get("candidate_present", False),
            contract_files=kwargs.get("contract_files", set(M.EXPECTED_CONTRACT_FILES)),
        )

    def test_current_contract_passes(self): self.assertEqual([], self.errors())
    def test_authorization_drift_fails(self):
        data=copy.deepcopy(self.contract);data["implementation_authorization"]["comment_id"]=1;self.assertTrue(self.errors(contract=data))
    def test_non_design_state_fails(self):
        data=copy.deepcopy(self.contract);data["contract_state"]="executed";self.assertTrue(self.errors(contract=data))
    def test_authority_blob_drift_fails(self):
        self.assertTrue(self.errors(adjudication_blob="0"*40));self.assertTrue(self.errors(attestation_blob="0"*40));self.assertTrue(self.errors(future_schema_blob="0"*40))
    def test_target_omission_fails(self):
        data=copy.deepcopy(self.contract);data["output_scope"]["encoded_targets"].pop();self.assertTrue(self.errors(contract=data))
    def test_non_atomic_execution_fails(self):
        data=copy.deepcopy(self.contract);data["atomic_execution"]["mode"]="split_operations";self.assertTrue(self.errors(contract=data))
    def test_route_promotion_in_design_fails(self):
        routes=copy.deepcopy(self.routes);route=next(x for x in routes["routes"] if x["campaign_id"]=="OTP-F-EHRHART");route["intake_status"]="qualified";self.assertTrue(self.errors(routes=routes))
    def test_proof_promotion_fails(self):
        data=copy.deepcopy(self.contract);data["state"]["mathematical_target_proved"]=True;self.assertTrue(self.errors(contract=data))
    def test_open_future_schema_fails(self):
        data=copy.deepcopy(self.future_schema);data["additionalProperties"]=True;self.assertTrue(self.errors(future_schema=data))
    def test_premature_artifacts_fail(self):
        self.assertTrue(self.errors(future_certificate_present=True));self.assertTrue(self.errors(candidate_present=True))
    def test_equality_inflation_fails(self):
        data=copy.deepcopy(self.contract);data["preserved_limitations"]["classification_or_uniqueness_of_all_equality_cases"]="established";self.assertTrue(self.errors(contract=data))
    def test_aggregate_authority_fails(self):
        data=copy.deepcopy(self.contract);data["state"]["aggregate_output"]=True;self.assertTrue(self.errors(contract=data))


if __name__ == "__main__": unittest.main()
