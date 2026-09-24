# External catalog certification intake

This is an operational receiving gate, not a certificate generator. MATHFORGE
owns source records and semantic review; MATHSOLVE owns reviewed promotion and
Chaidez dossiers; MATHCERT alone adjudicates scoped local claims with the required
independent verification. Source assurance, review, promotion, mathematical status
and certification remain distinct.

The production intake registry starts empty. Ordinary catalog records cannot
enter MATHCERT. An intake must pin a protected MATHSOLVE commit and the exact
promotion registry, dossier and supplemental-handoff paths by Git blob and
SHA-256. Every referenced local evidence artifact must exist in that same
protected commit. The generic handoff remains mandatory and unchanged.

The receiver reuses the exact protected Solve gate under `contracts/chaidez_solve`,
whose source commit and all file identities are recorded in
`governance/external_catalog_solve_contract.json`. Source, normalized statement,
reviewed assurance and exact-target relation are checked through the Programme
import and admitted Forge shard. The receiving record must agree with the
handoff's exact local claim, spine node, all applicable debt, trust quartet,
support route, replay evidence and independent-verification disposition.

The current certification-route registry must explicitly cover both the campaign
and selected claim ID. Merely naming an existing route does not authorize a new
claim. Real route admission and independent mathematical verification remain
separate governed acts. Neither is manufactured by this implementation.

The only receiving dispositions are HOLD_FOR_PROOF_DEBT and
AWAITING_INDEPENDENT_VERIFICATION. Submitted verification evidence is not accepted
verification and cannot issue or imply a certificate. Direct catalog intake,
mutable identities, missing proof debt, contradictory trust state and claim
inflation fail closed.

## Replay

```sh
python ci/validate_external_catalog_certification_intake.py
python -m unittest ci.test_external_catalog_certification_intake -v
```

These commands check the empty production inventory and a full synthetic
filesystem canary. The canary's simulated reviewer and route exist only in test
repositories. It demonstrates contract replay, not production exercise or proof.

For a real receiving record, use explicit authenticated checkouts with freshly
fetched protected `origin/main` references:

```sh
python ci/validate_external_catalog_certification_intake.py \
  --intake /path/to/scoped-intake.json \
  --solve-root /path/to/MATHSOLVE \
  --programme-root /path/to/MATH-PROGRAMME \
  --forge-root /path/to/MATHFORGE
```

Missing roots, stale Programme imports, mismatched local/protected evidence or
unprotected commits fail closed. No scheduled cross-repository workflow is added.
The platform branch and all control paths are declared in the platform-lane
manifest; admission requires FULL_ESTATE. Both canonical shell runners reach the
new validator and tests. Green CI remains engineering evidence only.
