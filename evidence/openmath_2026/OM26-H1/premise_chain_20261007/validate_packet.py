#!/usr/bin/env python3
from __future__ import annotations
import json, pathlib
R=pathlib.Path(__file__).resolve().parent
lock=json.loads((R/"SOURCE_LOCK.json").read_text())
elig=json.loads((R/"ELIGIBILITY_FINDING.json").read_text())
adj=json.loads((R/"ADJUDICATION.json").read_text())
adv=json.loads((R/"ADVERSARY_ROLE.json").read_text())
ref=json.loads((R/"REFEREE_ROLE.json").read_text())
finite=json.loads((R/"FINITE_REPLAY.json").read_text())
prem001=json.loads((R/"PREM001_EXTERNAL_SUPPORT.json").read_text())
assert lock["mathsolve_subject"]["commit"]=="bf094d909de041761a925c1c5c770f67983df210"
assert elig["policy_exception_requested"] is False
assert elig["formal_level_4_or_5_eligible"] is False
assert elig["independence_finding"].endswith("NO_POLICY_EXCEPTION")
basis_types={x["type"] for x in elig["basis"]}
assert "STANDARD_PROJECTIVE_GEOMETRY_EXTERNAL_SUPPORT" in basis_types
assert "INDEPENDENT_BLIND_PROTECTED_REPLAY" not in basis_types
assert prem001["zero_context_corroboration"]["certification_effect"] is False
assert prem001["zero_context_corroboration"]["independence_strength_adjudicated"] is False
assert finite["fan_enumeration"]["3"]=={"bound":3,"max_d1":3,"maximizers":2}
assert finite["fan_enumeration"]["4"]=={"bound":5,"max_d1":5,"maximizers":8}
expected={f"OM26-H1-PREM-00{i}" for i in range(1,5)}
seen=set()
for name in adj["dispositions"]:
    d=json.loads((R/name).read_text())
    seen.add(d["claim_id"])
    assert d["exact_subject"]["solve_commit"]==lock["mathsolve_subject"]["commit"]
    assert d["disposition"]=="QUALIFIED_INFORMAL_PROOF_AND_SEMANTIC_ADJUDICATION"
    assert d["certification_level"] is None
    assert d["formal_theorem_certified"] is False
    assert d["policy_exception_requested"] is False
    if d["claim_id"]=="OM26-H1-PREM-001":
        assert "PREM001_EXTERNAL_SUPPORT.json" in d["support"]
assert seen==expected
assert adj["formal_certification_level"] is None
assert adj["protected_effect"] is False
assert adv["disposition"]=="NO_FATAL_DEFECT__QUALIFIED_SCOPE_ENFORCED"
assert ref["overall_finding"]=="ACCEPT_QUALIFIED_DISPOSITIONS__NO_FORMAL_LEVEL_ASSIGNED"
assert adv["certification_effect"] is False and ref["certification_effect"] is False
assert adj["adversary_role"]=="ADVERSARY_ROLE.json"
assert adj["referee_role"]=="REFEREE_ROLE.json"
print("OM26_H1_PREMISE_CHAIN_PACKET=PASS")
print("claims="+",".join(sorted(seen)))
