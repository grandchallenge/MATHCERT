# Foundation-Aware Certification Standard

Status: proposed MATHCERT trust-ledger standard  
Purpose: certify not only that a claim has evidence, but what kind of foundational strength and constructive content that evidence carries.

## Certification principle

MATHCERT should not reduce trust to a binary `proved` / `not proved` flag. A mathematical artifact may be:

- constructively witnessed;
- classically proved but nonconstructive;
- dependent-choice analytic;
- full-choice classical;
- machine-checkable;
- human-audited only;
- numerically supported but not certified;
- foundations-sensitive and relative to axioms.

MATHCERT therefore records both proof status and proof discipline.

## Required ledger extension

Every certificate ledger entry should include:

```yaml
foundation_certificate:
  statement_id: ""
  foundational_profile_ref: ""
  ambient_structure_confirmed: true | false | unknown
  regularity_confirmed:
    status: confirmed | missing | not_applicable | unknown
    notes: ""
  axiom_profile:
    base: finite | constructive | ZF | ZF+DC | ZFC | stronger | unknown
    choice_usage: none | finite_choice | countable_choice | dependent_choice | full_choice | unknown
    excluded_middle: avoided | local | used | unknown
    large_cardinal_usage: none | consistency_background | essential | unknown
    determinacy_usage: none | local | essential | unknown
  witness_audit:
    existence_claim: explicit_witness | extractable | nonconstructive | contradiction_only | unknown
    witness_artifact: present | absent | not_required | unknown
    extraction_notes: ""
  checker_boundary:
    machine_check_status: unchecked | checked | partially_checked | not_applicable
    checker: Lean | Coq | SAT | SMT | PB | CAS | interval | custom | human_audit | none
    trusted_core_description: ""
    replay_command: ""
  numerical_audit:
    uses_numerics: true | false | unknown
    enclosure_or_error_bound: present | absent | not_required | unknown
    notes: ""
  pathology_audit:
    level: low | medium | high | unknown
    triggers: []
    mitigation: ""
  verdict:
    status: certified | provisionally_certified | human_audited | blocked | rejected | unknown
    reason: ""
```

## Certificate classes

### C0: executable finite certificate

The artifact can be checked by a small verifier over finite data.

Examples:

- SAT/SMT/PB proof trace;
- exact rational computation;
- bounded exhaustive enumeration;
- graph certificate;
- finite Lean proof.

Trust posture: strongest practical default.

### C1: formal proof certificate

The claim is checked in Lean, Coq, or an equivalent proof assistant.

Required notes:

- theorem statement location;
- imported axioms;
- whether classical axioms are used;
- replay command;
- trusted theorem dependencies.

### C2: proof-producing algebraic certificate

The artifact is produced by CAS or algebraic machinery but has an independently checkable witness.

Examples:

- Gröbner representation;
- resultant certificate;
- polynomial identity certificate;
- algebraic witness export.

Required notes:

- exact coefficient domain;
- normalization convention;
- verifier script or formal target.

### C3: interval/numerical certificate

The artifact uses computation over real or floating quantities but supplies rational or interval enclosures.

Required notes:

- precision policy;
- enclosure bound;
- interval arithmetic library or checker;
- failure condition if the enclosure is too weak.

### C4: regular analytic human-audit certificate

The proof is analytic and not yet formalized, but its regularity and axiom profile are explicit.

Required notes:

- ambient space;
- sigma-algebra/topology/normed structure;
- compactness/separability/measurability assumptions;
- whether dependent choice suffices;
- formalization target if available.

### C5: classical-choice certificate

The proof uses full choice or classical maximality.

Required notes:

- exact choice principle or equivalent theorem;
- whether choice is essential or avoidable;
- constructive content expected: usually none or unknown;
- possible regular or finite substitute.

### C6: foundations-relative certificate

The claim is certified only relative to a stated theory or consistency-strength background.

Required notes:

- base theory;
- added axiom;
- theorem vs consistency statement;
- incompatible principles if relevant;
- proof reference or formal target.

## Certification ladder update

The trust ladder should be read with foundations in view:

```text
raw claim
-> foundation profile present
-> route discipline declared
-> evidence artifact produced
-> checker boundary declared
-> axiom and choice audit complete
-> certificate replayed or human-audited
-> pathology risk resolved or explicitly accepted
```

A result should not advance to `certified` while `choice_usage: unknown`, `ambient_structure_confirmed: false`, or `regularity_confirmed: missing` unless the verdict explains why those fields are irrelevant.

## Rejection and blocking conditions

MATHCERT should block certification when:

- the statement depends on convexity but no affine/vector-space ambient is declared;
- the statement depends on measure or probability but no sigma-algebra is declared;
- numerical evidence is supplied without an enclosure, exact reconstruction, or explicit non-proof status;
- an existence theorem has no witness policy;
- full choice is used but not marked;
- a foundation-sensitive result is presented as an ordinary theorem;
- the proof claims all subsets of a continuum have a regular property under ZFC without acknowledging independence or alternative axiom context.

## Minimal certificate summary

A short certificate may use this compact form:

```yaml
certificate_summary:
  status: certified | provisional | blocked | rejected
  class: C0 | C1 | C2 | C3 | C4 | C5 | C6
  base_theory: finite | constructive | ZF | ZF+DC | ZFC | stronger | unknown
  choice_usage: none | weak | dependent_choice | full_choice | unknown
  witness_status: explicit | extractable | nonconstructive | not_required | unknown
  checker: Lean | Coq | SAT | SMT | PB | CAS | interval | human | none
  pathology_risk: low | medium | high | unknown
  next_action: ""
```

## Grand Challenge invariant

MATHCERT exists to turn mathematical output into accountable trust records:

```text
claim -> foundation profile -> evidence class -> checker boundary -> trust verdict
```

The goal is not to distrust classical mathematics. The goal is to prevent hidden foundations, hidden choice, and hidden pathology from masquerading as ordinary certifiable evidence.
