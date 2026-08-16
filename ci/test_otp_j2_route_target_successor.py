#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "ci/validate_otp_j2_route_target_successor.py"
spec = importlib.util.spec_from_file_location("j2succ", MODULE)
assert spec and spec.loader
j2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(j2)


def reject(label: str, receipt: dict, contract: dict, routes: dict) -> None:
    errors = j2.validation_errors(receipt, contract, routes, check_files=False)
    if not errors:
        raise AssertionError(f"mutation accepted: {label}")


def main() -> int:
    receipt = j2.load(j2.RECEIPT)
    contract = j2.load(j2.CONTRACT)
    routes = j2.load(j2.ROUTES)
    baseline = j2.validation_errors(receipt, contract, routes, check_files=True)
    if baseline:
        raise AssertionError("baseline invalid:\n" + "\n".join(baseline))

    cases: list[tuple[str, dict, dict, dict]] = []

    def receipt_case(label: str, fn) -> None:
        r = copy.deepcopy(receipt)
        fn(r)
        cases.append((label, r, contract, routes))

    def contract_case(label: str, fn) -> None:
        c = copy.deepcopy(contract)
        fn(c)
        cases.append((label, receipt, c, routes))

    def route_case(label: str, fn) -> None:
        rs = copy.deepcopy(routes)
        route = j2.find_route(rs)
        assert route is not None
        fn(route)
        cases.append((label, receipt, contract, rs))

    receipt_case("predecessor route substitution", lambda x: x["authority"]["predecessor_route_registry"].__setitem__("digest", "0" * 40))
    receipt_case("predecessor contract substitution", lambda x: x["authority"]["predecessor_adjudication_contract"].__setitem__("digest", "0" * 40))
    receipt_case("scope repair substitution", lambda x: x["authority"]["scope_repair"].__setitem__("record_git_blob_sha1", "0" * 40))
    receipt_case("projection substitution", lambda x: x["authority"]["scope_repair"].__setitem__("projection_git_blob_sha1", "0" * 40))
    receipt_case("evidence substitution", lambda x: x["authority"]["completed_evidence"].__setitem__("record_git_blob_sha1", "0" * 40))
    receipt_case("source substitution", lambda x: x["authority"]["official_source"].__setitem__("sha256", "0" * 64))
    receipt_case("formal commit substitution", lambda x: x["authority"]["formal_subject"].__setitem__("commit", "0" * 40))
    receipt_case("predecessor history rewrite", lambda x: x.__setitem__("predecessor_live_target_claim_ids", j2.NEW_TARGETS))
    receipt_case("successor target inflation", lambda x: x["successor_live_target_claim_ids"].append("Other.target"))
    receipt_case("mixed old new targets", lambda x: x["successor_live_target_claim_ids"].__setitem__(0, j2.OLD_TARGETS[0]))
    receipt_case("route state transition", lambda x: x.__setitem__("route_state_after_successor", "qualified"))
    receipt_case("adjudication insertion", lambda x: x["required_state"].__setitem__("may_adjudicate", True))
    receipt_case("output insertion", lambda x: x["required_state"].__setitem__("cert_output", "certificate.json"))
    receipt_case("proof promotion", lambda x: x["required_state"].__setitem__("mathematical_target_proved", True))
    receipt_case("aggregate authority", lambda x: x["required_state"].__setitem__("aggregate_authority", True))
    receipt_case("coloring source attribution", lambda x: x["required_state"].__setitem__("stronger_coloring_property_source_authorized", True))
    receipt_case("coloring certification", lambda x: x["required_state"].__setitem__("stronger_coloring_property_certified", True))
    receipt_case("manual steward gate reintroduced", lambda x: x["streamlined_control_plan"].__setitem__("separate_human_steward_authorization_required_for_this_stage", True))
    receipt_case("intervention boundary weakened", lambda x: x["streamlined_control_plan"].__setitem__("human_steward_intervention_required_only_for_control_plan_change", False))
    receipt_case("unknown nested field", lambda x: x["required_state"].__setitem__("extra", False))

    contract_case("contract target inflation", lambda x: x["route_scope"]["target_claim_ids"].append("Other.target"))
    contract_case("contract historical target rewrite", lambda x: x["route_scope"].__setitem__("historical_predecessor_target_claim_ids", j2.NEW_TARGETS))
    contract_case("contract route state transition", lambda x: x["route_scope"].__setitem__("registered_route_state", "qualified"))
    contract_case("contract manual steward gate", lambda x: x["execution_gate"].__setitem__("separate_human_steward_authorization_required", True))
    contract_case("contract adjudication insertion", lambda x: x["state"].__setitem__("adjudication", "clear"))
    contract_case("contract may adjudicate", lambda x: x["state"].__setitem__("may_adjudicate", True))
    contract_case("contract output insertion", lambda x: x["state"].__setitem__("cert_output", "x"))
    contract_case("contract proof promotion", lambda x: x["state"].__setitem__("mathematical_target_proved", True))
    contract_case("contract coloring certification", lambda x: x["preserved_limitations"].__setitem__("stronger_coloring_property_certified", True))
    contract_case("contract history rewrite", lambda x: x["preserved_limitations"].__setitem__("historical_records_rewritten", True))
    contract_case("contract unknown nested field", lambda x: x["execution_gate"].__setitem__("extra", True))

    route_case("live old targets retained", lambda x: x.__setitem__("target_claim_ids", j2.OLD_TARGETS))
    route_case("live mixed targets", lambda x: x.__setitem__("target_claim_ids", [j2.NEW_TARGETS[0], j2.OLD_TARGETS[1]]))
    route_case("live target inflation", lambda x: x["target_claim_ids"].append("Other.target"))
    route_case("live route qualification", lambda x: x.__setitem__("intake_status", "qualified"))
    route_case("live output insertion", lambda x: x.__setitem__("cert_output", {"repository": "x/y"}))
    route_case("live route id drift", lambda x: x.__setitem__("route_id", "MC-ROUTE-OTP-J2-OTHER"))
    route_case("live coloring exclusion removed", lambda x: x.__setitem__("claim_boundary", "source-faithful only"))

    for label, r, c, rs in cases:
        reject(label, r, c, rs)

    print(f"J2 route-target successor mutation suite rejected {len(cases)} adversarial changes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
