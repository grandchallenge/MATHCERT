# OPENMATH-2026 MATHCERT readiness

**Cert tracker:** `grandchallenge/MATHCERT#339`  
**Programme tracker:** `grandchallenge/MATH-PROGRAMME#1072`  
**Solve tracker:** `grandchallenge/MATHSOLVE#454`

This directory reserves the certification intake surface for claim-bearing OpenMath 2026 artifacts.

There are no certified OpenMath 2026 hill claims at creation.

## Required separation

For any later hill or subclaim, keep these facts separate:

1. **External checker/kernel acceptance:** the supplied formal object or approved certificate passes its pinned external checker.
2. **Semantic fidelity:** the checked object actually expresses the exact mathematical claim attributed to the hill or declared variation.
3. **Provenance and attribution:** source, authorship, tools, dependencies, and material AI/CAS/solver use are recorded.
4. **MATHCERT disposition:** GCL's own certification, qualification, rejection, or proof-debt state under the applicable route.

None implies the next.

In particular:

```text
competition acceptance != MATHCERT certification
kernel acceptance      != semantic fidelity
provenance completeness != mathematical correctness
```

## Intake prerequisites

A claim-bearing intake must identify:

- exact OpenMath hill or admitted variation;
- exact competition statement/source lock;
- exact MATHSOLVE handoff and commit;
- exact formal/certificate artifact;
- exact checker/prover version and environment;
- dependency/axiom ledger;
- producer authorship and material tool provenance;
- independent replay path where required;
- semantic-fidelity hazards;
- explicit acceptance and rejection criteria.

## Independence boundary

No system may certify a mathematical claim for which it supplied the sole construction or verification evidence.

Operational continuity may transfer across agents. Certification authority and substantive independence do not transfer automatically.

## Empty-slot rule

Do not create placeholder certified claims for `OM26-H1` through `OM26-H6`.

A slot enters Cert only when a concrete claim-bearing MATHSOLVE handoff exists.

## Active intake: OM26-H1

`OM26-H1` now has a concrete claim-bearing intake under MATHCERT issue #341. The admitted objects are the H1-02 face-criterion theorem and the exact `n=18` construction claim for `RD_LOCAL_MUTATION_086`.

The intake is **pending a fresh non-authoring Cert executor**. No MATHCERT certification disposition has been issued.

## OM26-H1 successor intake: 93-triangle reconstruction

The same pending independent Cert intake now includes a separate successor object for `OM26-H1-CON-002`, the exact 93-triangle rational reconstruction `RH_BADER_RECONSTRUCTION_093` bound to protected MATHSOLVE commit `5e5770c287f6bbf8e66f8cab4487594db6100f53`.

This successor does not replace the historical 86-triangle intake or the H1-02 theorem review. It is independently adjudicated and has no certification effect until a fresh non-authoring Cert executor completes the replay.

## H1 review evidence — 2026-10-02

A fresh non-authoring logical review pass reconstructed the face predicate from
the pinned Forge statement, replayed the 86- and 93-triangle snapshots with a
new exact rational checker, and reviewed the pinned face-criterion proof.
The reproducible record is in `OM26-H1/review_20261002/REVIEW.md`.

This is completed preparatory verification evidence. It does not issue a final
MATHCERT certification disposition: the reviewer is a distinct agent within
the same Codex system, and that separation does not by itself satisfy the
system-level independence prohibition in `AGENTS.md` and the admitted H1
bootstrap. The existing intake statuses and certification effects remain
unchanged. An eligible non-authoring certifier must evaluate the evidence and
record separate dispositions for the three exact claims.
