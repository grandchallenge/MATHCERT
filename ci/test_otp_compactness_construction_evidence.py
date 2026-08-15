from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_otp_compactness_construction_evidence",
    ROOT / "ci/validate_otp_compactness_construction_evidence.py",
)
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class CompactnessConstructionEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.record = M.load(M.RECORD)
        self.schema = M.load(M.SCHEMA)
        self.source = M.load(M.SOURCE)
        self.reconstruction = M.load(M.RECONSTRUCTION)
        self.routes = M.load(M.ROUTES)

    def errors(self, **kwargs):
        defaults = dict(
            record=copy.deepcopy(self.record), schema=copy.deepcopy(self.schema),
            source=copy.deepcopy(self.source), reconstruction=copy.deepcopy(self.reconstruction),
            routes=copy.deepcopy(self.routes), source_blob=M.SOURCE_BLOB,
            reconstruction_blob=M.RECON_BLOB, route_blob=M.ROUTE_BLOB,
            predecessor_blob=M.PREDECESSOR_BLOB, contract_blob=M.CONTRACT_BLOB,
            adjudication_present=False, output_present=False, certificate_present=False,
        )
        defaults.update(kwargs)
        return M.validation_errors(**defaults)

    def test_current_passes(self): self.assertEqual(self.errors(), [])

    def test_source_substitution(self):
        source=copy.deepcopy(self.source); source["current_official_revision"]["expected_sha256"]="0"*64
        self.assertTrue(self.errors(source=source))

    def test_historical_reacquisition_inflation(self):
        source=copy.deepcopy(self.source); source["historical_admitted_revision"]["reacquirable_exact_bytes"]=True
        self.assertTrue(self.errors(source=source))

    def test_construction_mutation(self):
        r=copy.deepcopy(self.reconstruction); r["templates"]["J0"]["generator"]["extra_vertex"]["neighbors"].pop()
        self.assertTrue(self.errors(reconstruction=r))

    def test_property_omission(self):
        r=copy.deepcopy(self.reconstruction); r["forbidden_family"]["all_members_connected"]=False
        self.assertTrue(self.errors(reconstruction=r))

    def test_exponent_drift(self):
        r=copy.deepcopy(self.reconstruction); r["upper_bound_bridge"]["exact_arithmetic"]["four_thirds_minus_one_over_48"]="64/47"
        self.assertTrue(self.errors(reconstruction=r))

    def test_quantifier_reversal(self):
        r=copy.deepcopy(self.reconstruction); r["source_to_encoded_concordance"]["member_lower"]="there exists one family member with Omega(n^(4/3))"
        self.assertTrue(self.errors(reconstruction=r))

    def test_uniformity_inflation(self):
        r=copy.deepcopy(self.reconstruction); r["lower_bound_bridge"]["growth_and_padding"]["uniform_lower_constant"]="1"
        self.assertTrue(self.errors(reconstruction=r))

    def test_construction_to_extremal_inflation(self):
        r=copy.deepcopy(self.reconstruction); r["source_to_encoded_concordance"]["proof_body_compared_in_full"]=True
        self.assertTrue(self.errors(reconstruction=r))

    def test_vacuity(self):
        r=copy.deepcopy(self.reconstruction); r["forbidden_family"]["nonempty"]=False
        self.assertTrue(self.errors(reconstruction=r))

    def test_another_family_insertion(self):
        record=copy.deepcopy(self.record); record["result_family"]="OTP-J2-TWO-DEGENERATE"
        self.assertTrue(self.errors(record=record))

    def test_adjudication_insertion(self): self.assertTrue(self.errors(adjudication_present=True))

    def test_output_insertion(self):
        self.assertTrue(self.errors(output_present=True)); self.assertTrue(self.errors(certificate_present=True))

    def test_proof_promotion(self):
        record=copy.deepcopy(self.record); record["required_state"]["mathematical_target_proved"]=True
        self.assertTrue(self.errors(record=record))

    def test_route_transition(self):
        routes=copy.deepcopy(self.routes); route=next(x for x in routes["routes"] if x["route_id"]==M.ROUTE_ID); route["intake_status"]="qualified"
        self.assertTrue(self.errors(routes=routes))

    def test_authorization_substitution(self):
        record=copy.deepcopy(self.record); record["authority"]["human_steward_authorization"]["comment_id"]=1
        self.assertTrue(self.errors(record=record))

    def test_predecessor_substitution(self): self.assertTrue(self.errors(predecessor_blob="0"*40))

    def test_schema_opening(self):
        schema=copy.deepcopy(self.schema); schema["additionalProperties"]=True
        self.assertTrue(self.errors(schema=schema))

    def test_review_prepollution(self):
        record=copy.deepcopy(self.record); record["review_gate"]["recorded_review"]={"reviewer":"forged","state":"APPROVED"}
        self.assertTrue(self.errors(record=record))


if __name__ == "__main__": unittest.main()
