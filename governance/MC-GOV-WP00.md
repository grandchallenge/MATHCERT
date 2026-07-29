# MC-GOV-WP00 — Certification provider coverage and conformance upgrade

## Identity

- Parent audit: `grandchallenge/MATH-PROGRAMME#123`
- Provider issue: `grandchallenge/MATHCERT#31`
- Audited base: `1799d9a623a825b559742afd33009778d5119ce0`
- Provider role: MATHCERT owns adjudication and replay. It does not own discovery or proof search.

## Corrected contract

MATHCERT now publishes a machine-readable route registry for every governed campaign. The registry binds each route to the exact MATHSOLVE campaign-manifest commit, path, and Git blob identity.

The initial registry records every route as `pending`. This is deliberate. Existing plans, semantic audits, schemas, and restricted proof artifacts do not become completed campaign dispositions without a content-addressed MATHSOLVE handoff and a MATHCERT output record.

The state model is:

- `pending`: no complete handoff packet is accepted;
- `ready`: a complete packet exists upstream but MATHCERT has not acknowledged intake;
- `submitted`: MATHCERT has acknowledged intake but has not adjudicated it;
- `certified`: the exact scoped claim is certified;
- `qualified`: the exact scoped claim is accepted with explicit qualifications;
- `rejected`: the submitted claim is rejected;
- `proof_debt`: the packet is closed as unresolved certification debt.

Only `certified` and `qualified` can support positive mathematical promotion.

## Portfolio

The registry covers:

- `UC-001`;
- `NS-CI-001`;
- `HC-001`;
- `BSD-001`;
- `PNP-001`;
- `RH-001`;
- `YM-001`;
- `OZ-001`.

Each route preserves its campaign boundary. No route record certifies an open problem.

## CI controls

The standard shell and PowerShell suites now execute the same registered controls.

The control registry distinguishes direct controls from library checkers exercised through adversarial tests. A new matching `validate_*`, `test_*`, `replay_*`, `check_*`, or `audit_*` Python file fails CI until it is registered and reached.

Certificate-family admission is fail-closed:

- exact certificates are enumerated and independently replayed;
- algebraic certificates are recursively validated;
- tropical ReLU certificates are recursively validated;
- interval, SAT, and external certificate directories remain blocked until an executable checker is registered.

The pseudo-Boolean checker is exercised by its adversarial test suite in the standard path.

## Formal trust boundary

Lean files may not contain `sorry` or `admit`.

An `axiom` or `opaque` declaration must appear in `governance/formal_trust_allowlist.json` with a source identity, justification, and review issue. The initial allowlist is empty.

This mechanism does not turn imported mathematics into a checked theorem. It only makes the trust boundary explicit and testable.

## Workflow policy

The Cert workflow now uses:

- a fixed Ubuntu runner family;
- immutable action commit identities;
- Python 3.13;
- a checked-in dependency lock;
- read-only default permissions;
- bounded execution time;
- cancellation-aware concurrency.

Repository ruleset enforcement remains an administrative acceptance condition. A green workflow is not assumed to be a required merge gate without recorded ruleset evidence.

## Handoff to MATHSOLVE

`grandchallenge/MATHSOLVE#73` must produce packets against this contract. Those packets must use exact claim IDs and artifact identities. MATHCERT must not infer packet acceptance from an issue, pull request, branch, or prose document.

## Claim boundary

This work package validates certification machinery and route lineage. It certifies no new mathematical claim.
