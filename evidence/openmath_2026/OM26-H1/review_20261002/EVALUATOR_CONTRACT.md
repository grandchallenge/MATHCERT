# OM26-H1 evaluator contract — Kobon triangles

Source: the content-addressed authenticated hill capture in `STATEMENT.md`.

## Accepted object

A UTF-8 `solution.json` containing exactly one field, `lines`, with exactly `n` integer triples `[a,b,c]` representing distinct Euclidean lines `a*x + b*y + c = 0`.

Validity constraints:

- exactly `n` triples;
- three JSON integers per triple;
- `|a|,|b|,|c| <= 10^30`;
- `(a,b) != (0,0)`;
- proportional triples are duplicate lines and invalid;
- file size at most 65,536 bytes;
- no symlink;
- no floats, booleans, NaN, infinity, duplicate keys, or extra fields.

Parallel lines and intersections of three or more lines are permitted.

## Score semantics

`triangles` is the verified number of bounded nonzero-area triangular faces whose interiors are not crossed by any line in the arrangement. A triangle subdivided by another line is not counted. Shared vertices are permitted.

The objective is maximization. A larger score is evidence of a better construction at the same `n`; it is not an upper bound and does not establish optimality.

`n` ranges from 3 through 100 and is a primary comparison setting. The default is `n=18`.

## Exactness

All geometry is rational/exact. Integer coefficients specify rational lines exactly. The source states that intersections and ordering comparisons use exact arithmetic and that there is no geometric tolerance, bounding box, or minimum triangle area.

## Evaluation boundary

The evaluator reads only `solution.json`; it does not execute submitted programs, import submission modules, or trust a submitted score. Validation and final evaluation count the same submitted arrangement under the same exact rule; `final=True` changes only an informational field.

The private validation/test files are evaluator regression fixtures, not hidden target data. Public tests also compare the counting algorithm against an independent exact triangle-interior intersection check.

The 120-second watchdog protects evaluator execution. Search/generation runtime before submission is not scored or limited by the hill.

## Baseline

For `n=18`, the displayed baseline is the family `2*i*x - y - i*i = 0` for `i=0,...,17`, with a reported score of 16. This is explicitly not claimed to be best known.

## Release rule

This contract is sufficient to release MATHSOLVE research and candidate-construction work for OM26-H1. Final competition submission remains subject to a live pre-submit concordance check because the supplied render did not expose an immutable AutoLab hill-version token.
