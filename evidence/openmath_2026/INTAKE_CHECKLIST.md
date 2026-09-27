# OPENMATH-2026 certification intake checklist

Apply this checklist to each concrete claim, not to the campaign as a whole.

## A. Subject identity

- [ ] Exact hill/variation identity.
- [ ] Exact source statement and source-lock reference.
- [ ] Exact claim text under review.
- [ ] Exact MATHSOLVE producer commit and handoff.
- [ ] Any distinction between competition wording and formal theorem is explicit.

## B. Formal/checker artifact

- [ ] Artifact bytes or immutable repository identity.
- [ ] Prover/checker/certificate modality.
- [ ] Version and environment lock.
- [ ] Replay command.
- [ ] Dependency and axiom inventory.
- [ ] No hidden network or mutable dependency required for replay.

## C. Semantic fidelity

- [ ] Hypotheses match.
- [ ] Quantifiers match.
- [ ] Domains/carriers match.
- [ ] Exceptional cases are accounted for.
- [ ] Claimed conclusion matches the checked conclusion.
- [ ] Equivalent reformulation, if used, has a justified bridge.

## D. Provenance and authorship

- [ ] Mathematical source attribution.
- [ ] Human authorship attribution.
- [ ] Material AI system disclosure.
- [ ] CAS/SAT/SMT/search/tool disclosure.
- [ ] Imported formal-library dependencies.
- [ ] Competition provenance requirements satisfied independently of GCL requirements.

## E. Independence and replay

- [ ] Authoring provenance is explicit.
- [ ] Required non-authoring verification is supplied.
- [ ] Independent verifier does not merely reuse producer state when substantive independence matters.
- [ ] Continuity receipts or CI success are not used as independence evidence.

## F. Disposition

Record exactly one applicable MATHCERT state according to existing policy.

Do not derive that state from an OpenMath leaderboard, Hill/Climb acceptance, CI badge, or external checker result alone.
