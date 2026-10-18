#!/usr/bin/env python3
"""Independent finite corroboration for OM26-H1 premise-chain adjudication."""
from __future__ import annotations
import itertools, json

def has_cyclic_run(word,k):
    n=len(word)
    return any(all(word[(i+j)%n] for j in range(k)) for i in range(n))

fan={}
for r in range(3,7):
    n=2*r
    good=[]
    for word in itertools.product((0,1), repeat=n):
        if not has_cyclic_run(word,r-1):
            good.append(word)
    mx=max(map(sum,good))
    max_words=sum(sum(w)==mx for w in good)
    assert mx<=2*r-3
    fan[str(r)]={"max_d1":mx,"bound":2*r-3,"maximizers":max_words}
assert fan["3"]=={"max_d1":3,"bound":3,"maximizers":2}
assert fan["4"]=={"max_d1":5,"bound":5,"maximizers":8}

parity={}
for m in range(3,20,2):
    x=[0]
    for _ in range(m):
        x.append(1-x[-1])
    assert x[-1]==1
    parity[str(m)]={"endpoint_forced":1,"required_endpoint":0,"contradiction":True}

out={
 "schema_version":"1.0.0",
 "record_id":"MC-OM26-H1-PREMISE-CHAIN-FINITE-REPLAY-20261007-001",
 "fan_enumeration":fan,
 "clean_line_parity_endpoint_check":parity,
 "claim_boundary":"Finite corroboration only. General geometric validity is supplied by REVIEW.md, not by this enumeration."
}
print(json.dumps(out,indent=2,sort_keys=True))
