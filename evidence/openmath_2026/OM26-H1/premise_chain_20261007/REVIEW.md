# OM26-H1 premise-chain trusted mathematical replay

Record: `MC-OM26-H1-PREMISE-CHAIN-REVIEW-20261007-001`  
Tracker: MATHCERT #349  
Mode: `CERTIFIER_REPLAY__PRODUCER_SYSTEM_DISCLOSED__EXTERNAL_PRIOR_EVIDENCE_BOUND`  
Exact Solve subject: `grandchallenge/MATHSOLVE@bf094d909de041761a925c1c5c770f67983df210`

## Scope and disposition class

This review adjudicates only four geometric interface claims used by the OM26-H1 upper-bound programme:

- `OM26-H1-PREM-001`: projective elimination of parallelism while preserving an arbitrary finite selected family of counted bounded triangular faces;
- `OM26-H1-PREM-002`: the local fan/no-long-run bound `d1(v) <= 2r-3`;
- `OM26-H1-PREM-003`: the even-order clean-line parity lemma;
- `OM26-H1-PREM-004`: the blocked clean-line charge-capacity inequality `n-h <= 2U+D1-B`.

The appropriate MATHCERT class is a qualified informal proof / semantic adjudication. None of these four claims is presented here as a complete Level 4/5 theorem formalization. The external `kobon-proof` source has machine-checked real-line fan components, but its own documentation explicitly leaves extraction from an arbitrary global arrangement and the clean-line charging geometry at paper level.

Producer finite fixtures are not used as proof. The WP60-WP64 zero-context replays are corroborating evidence only and retain their recorded zero certification effect.

## Definitions used by PREM-002 through PREM-004

Work with finitely many distinct pairwise-nonparallel real affine lines, with even `n >= 4`.

A triangular face is a bounded nondegenerate cell whose boundary lies on three arrangement lines. An elementary segment is the closed segment between consecutive arrangement vertices on one supporting line. A segment is *shared* when it borders two triangular faces.

A finite intersection is a *multiple point* when at least three arrangement lines pass through it. A line is *clean* when it contains no multiple point.

For a shared elementary segment:
- `D1`: exactly one endpoint is multiple;
- `D2`: both endpoints are multiple.

Let:
- `U` be the number of bounded elementary segments bordering no triangular face;
- `D1`, `D2` be the global counts above;
- `h` be the number of arrangement lines containing at least one multiple point;
- at an `r`-fold point, `d1(v)` be the number of incident rays whose first elementary segment is D1;
- `B` count D1 rays adjacent in cyclic order to at least one D2 ray, once per D1 ray.

Two elementary extraction facts are required and survive direct review:

1. Every side of a triangular face is elementary. If another arrangement vertex lay in its relative interior, the corresponding arrangement line would enter the open triangular cell, contradicting that the triangle is a face.
2. A shared elementary segment cannot have two ordinary endpoints. If it did, its two endpoint transversals together with the shared support are the same three supporting lines for both alleged triangles. Three nonconcurrent lines have only one bounded triangular region, so two triangular faces cannot lie on opposite sides of the shared segment. Hence every shared segment belongs to D1 or D2.

## PREM-001 — projective normalization

### Accepted statement

Let `A` be a finite arrangement of distinct affine straight lines and let `F` be any finite family of counted bounded triangular faces of `A`. There exists a projectively equivalent affine arrangement `A'` with no parallel line pairs such that every face in `F` maps to a counted bounded triangular face of `A'`.

### Replay

Pass to the projective completion of the original affine plane. The union of the closed faces in `F` is compact in the original affine chart.

Choose an affine line `M` satisfying three finite-avoidance conditions:

1. its direction differs from every arrangement-line direction;
2. it passes through no finite arrangement vertex;
3. it is disjoint from the compact union of the selected closed faces.

Such an `M` exists. Choose a direction outside the finite set of arrangement directions. For that fixed direction, only finitely many translates pass through finite arrangement vertices, while all sufficiently distant translates miss the compact selected-face union.

In the projective plane, the point where `M` meets the old line at infinity is not the infinite intersection point of any parallel arrangement pair because the direction of `M` was excluded from every arrangement direction. Together with condition 2, this says that `M` contains no projective intersection point of any pair of arrangement lines.

Apply a projective automorphism sending `M` to the new line at infinity. Every original arrangement line is distinct from `M`, hence remains an affine line in the new chart. Every pairwise projective intersection lies off `M`, hence becomes finite. Therefore no two transformed arrangement lines are parallel.

Each selected closed triangular face is disjoint from `M`; its image is a compact subset of the new affine chart and is therefore bounded. A projective automorphism is a homeomorphism preserving lines, incidences, crossings, and the arrangement cell decomposition away from the new line at infinity. Thus each selected triangular cell remains a nondegenerate bounded triangular cell.

No concurrence is removed: projective transformations preserve incidence multiplicity. This is exactly the required scope.

### Finding

`PASS__QUALIFIED_INFORMAL_PROOF`.

## PREM-002 — fan/no-long-run

### Accepted statement

At an `r`-fold point `v`, `r >= 3`, no `r-1` cyclically consecutive rays can all be D1. Consequently

[
d_1(v) le 2r-3.
]

### Replay

Suppose `r-1` consecutive rays are D1. Since each D1 elementary segment borders triangular faces on both sides, the run forces `r` consecutive triangular sectors. Label the successive radial far endpoints

[
P_0,P_1,ldots,P_r
]

and the opposite supporting lines of the `r` triangles

[
A_0,A_1,ldots,A_{r-1}.
]

For each internal `P_i`, `1 <= i <= r-1`, the radial elementary segment is D1, so `P_i` is ordinary. Both `A_{i-1}` and `A_i` pass through `P_i` and are distinct from the radial support. At an ordinary arrangement vertex exactly one nonradial arrangement line is available, hence

[
A_{i-1}=A_i.
]

Induction gives one common opposite support `A`.

Among the `2r` rays of `r` full lines through `v`, advancing `r` cyclic ray positions takes a ray to its antipodal ray on the same supporting line. Therefore the first and last boundary rays of the strip are opposite rays of one arrangement line through `v`; `P_0` and `P_r` lie on that line with `v` between them.

The common opposite support `A` contains both `P_0` and `P_r`, so it is that same radial line and hence contains `v`. This makes the end triangle degenerate, contradiction.

Thus every cyclic block of `r-1` rays contains at most `r-2` D1 rays. There are `2r` such cyclic blocks and each D1 ray belongs to exactly `r-1` of them. Double counting gives

[
(r-1)d_1(v)le 2r(r-2).
]

For `r>=3`, the integer consequence is `d1(v) <= 2r-3`.

### Machine-checked component

At external source `alejandrozu/kobon-proof@22d1165f6c455fe45e461baef4410f6d5c78a014`:

- `Kobon/FanGeometry.lean` proves ordinary nonradial uniqueness, propagation along a real fan strip, and the opposite-ray obstruction;
- `Kobon/CyclicFan.lean` proves `Geometry.no_long_run` and `Geometry.selected_card_le`, obtaining the `2r-3` cyclic fan bound from actual real-line fan data.

Those modules do not themselves construct the cyclic fan from an arbitrary global arrangement. The elementary-side and D1-ray extraction above supplies that paper-level interface.

### Finding

`PASS__QUALIFIED_INFORMAL_PROOF_WITH_MACHINE_CHECKED_COMPONENT`.

## PREM-003 — clean-line parity

### Accepted statement

For even `n>=4`, every clean line has at one of its ordinary crossings a bounded transverse elementary segment with triangle-use count either zero or two.

### Replay

Fix a clean line `L` and make it horizontal. Because all arrangement lines are pairwise nonparallel and `L` contains no multiple point, the other `n-1` lines cross `L` at `m=n-1` distinct ordinary points. Since `n` is even, `m` is odd.

Order the crossings from left to right. For the bounded interval of `L` between crossings `i` and `i+1`, let `x_i` and `y_i` be the indicators that the incident face above or below `L` is triangular. Set

[
x_0=y_0=x_m=y_m=0
]

for the exterior rays.

A bounded segment of `L` has two ordinary endpoints, so it cannot be a side of triangular faces on both sides. Hence

[
x_i+y_ile1.
]

Let `R_i` be the transverse arrangement line at crossing `i`. Its upper and lower elementary pieces incident to `L` have triangle-use counts

[
a_i=x_{i-1}+x_i,qquad b_i=y_{i-1}+y_i.
]

Assume, for contradiction, that every bounded transverse piece has triangle-use exactly one. Then:
- any use-zero piece is unbounded;
- use two is impossible, because such a piece is necessarily bounded but would not have use one.

At the first crossing at least one transverse direction is bounded: `R_1` intersects the other nonparallel transverse lines away from `L`. Reflect vertically if necessary so the upper piece is bounded. Then `a_1=1`, hence `x_1=1`; the lower piece has use zero and is unbounded.

Now suppose some upper piece of `R_j` had use zero. It would be unbounded. The nonparallel lines `R_1` and `R_j` intersect away from `L`. If their intersection is below `L`, it lies on the allegedly unbounded lower ray of `R_1`; if above `L`, it lies on the allegedly unbounded upper ray of `R_j`. Either case is impossible. Therefore every `a_j` is nonzero.

Use two is impossible under the contradictory assumption, so in fact

[
a_j=x_{j-1}+x_j=1
]

for every `j=1,ldots,m`. Starting from `x_0=0`, the `x_j` alternate. Because `m` is odd, this forces `x_m=1`, contradicting the boundary condition `x_m=0`.

Therefore the assumption was false. Some bounded transverse elementary piece has triangle-use different from one, hence zero or two.

The pairwise-nonparallel hypothesis is essential to this proof: it supplies exactly `n-1` distinct crossings on `L` and forces the transverse-line intersections used in the contradiction.

### Finding

`PASS__QUALIFIED_INFORMAL_PROOF`.

## PREM-004 — blocked capacity

### Accepted statement

Choose for every clean line one chargeable transverse segment furnished by PREM-003. Then the total available capacity is at most

[
2U+D1-B,
]

and since there are exactly `n-h` clean lines,

[
n-hle 2U+D1-B.
]

### Replay

A clean line is charged through its ordinary crossing with the selected transverse segment. At an ordinary arrangement vertex exactly two arrangement lines meet, so for a fixed target segment and a fixed ordinary endpoint there is exactly one possible non-target line that can supply a charge. Consequently:

- a U segment has at most two ordinary endpoints and charge capacity at most two;
- a D1 segment has exactly one ordinary endpoint and capacity at most one;
- a D2 segment has no ordinary endpoint and capacity zero.

PREM-003 chooses a bounded target of use zero or two. A use-zero target is counted by U. A use-two target is shared; because the clean line meets it at an ordinary endpoint, it cannot be D2 and therefore is D1.

Now take a D1 ray at a multiple point `v` that is cyclically adjacent to a D2 ray. Since both elementary rays are shared, their common sector is triangular. Let `P` be the ordinary far endpoint of the D1 side and `Q` the multiple far endpoint of the D2 side. The opposite side of this triangle lies on the arrangement line through `P` and `Q`.

At the ordinary point `P`, that opposite support is the unique nonradial arrangement line. Any clean line charging the D1 target through `P` would have to be this same line. But the line contains the multiple point `Q`, so it is not clean. Therefore that D1 target has zero clean-line charge capacity.

Each D1 segment has exactly one multiple endpoint and hence corresponds to exactly one D1 ray at a multiple point. Counting blocked D1 rays once is therefore the same as counting blocked D1 target segments once. Subtracting those `B` unavailable D1 capacities from the baseline `2U+D1` gives total capacity `2U+D1-B`.

Finally, `h` counts exactly the arrangement lines containing at least one multiple point, so there are `n-h` clean lines. Assigning one charge per clean line proves the inequality.

### Finding

`PASS__QUALIFIED_INFORMAL_PROOF`.

## Independence and prior-evidence assessment

The Cert disposition does not rely on the producer checker as authority.

The mathematical content of the current Solve premise proof is unchanged from the proof bytes audited by WP60; only status/provenance lines changed. WP60-WP64 supply repeated zero-context replay closure, but their own records correctly deny certification effect and they are treated only as corroboration.

More importantly, the pinned external `alejandrozu/kobon-proof` source predates the GCL premise packet and contains:
- an independently authored paper derivation of the clean-line parity and charging budget;
- real-line Lean proofs of the fan propagation and cyclic `2r-3` bound;
- an explicitly conditional arithmetic module rather than a disguised global theorem.

This independent prior source means the present system is not the sole source of construction/proof or verification evidence for the adjudicated chain. No policy exception is requested.

## Residual uncertainty and exclusions

- PREM-001, PREM-003, PREM-004 and the global-arrangement extraction feeding PREM-002 remain paper-level mathematics, not kernel-complete formal theorems.
- The external Lean fan modules verify local real-line fan implications, not the full global arrangement-to-fan extraction.
- Producer fixtures and finite searches do not prove the general claims.
- These four dispositions do not by themselves certify any downstream q=3/q=4/q=5/q=6 exclusion. Each downstream theorem still has its own finite and geometric dependencies.
- No hill-global upper bound `K(18)<=94`, optimality of the 93 construction, novelty/priority, competition acceptance, or publication-readiness claim follows.

## Overall trusted-replay disposition

All four exact premise claims survive trusted mathematical replay at their stated scopes.

Recommended MATHCERT dispositions:

- PREM-001: `QUALIFIED_INFORMAL_PROOF_AND_SEMANTIC_ADJUDICATION`;
- PREM-002: `QUALIFIED_INFORMAL_PROOF_AND_SEMANTIC_ADJUDICATION`, with an external machine-checked local fan component;
- PREM-003: `QUALIFIED_INFORMAL_PROOF_AND_SEMANTIC_ADJUDICATION`;
- PREM-004: `QUALIFIED_INFORMAL_PROOF_AND_SEMANTIC_ADJUDICATION`.

No formal certification level is assigned.
