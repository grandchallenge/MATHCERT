# OPENMATH-2026 / OM26-H1 — authenticated hill capture

**Hill:** `alejandrozu/kobon-triangles`  
**Rendered title:** `Kobon triangles`  
**Canonical URL:** `https://app.autolab.ai/hills/alejandrozu/kobon-triangles`  
**Capture date:** `2026-09-27`  
**Acquisition:** authenticated AutoLab render supplied by the Human Steward, with the rendered hill body transcribed into the campaign record.

## Source-bound hill body

# Kobon triangles

Construct an arrangement of exactly `n` distinct straight lines in the Euclidean plane. The evaluator counts its bounded triangular faces: nonzero-area triangles whose interiors are not crossed by any line in the arrangement. Sharing vertices is allowed. A larger triangle subdivided by another line does not count.

This is a construction task. A higher count is better; it does not establish an upper bound or prove optimality. Submit an actual geometric arrangement, rather than a claimed triangle count or an abstract pseudoline arrangement.

## Submission

Place a UTF-8 `solution.json` in the submission directory. Its only field is `lines`, a list of triples `[a, b, c]` defining `a*x + b*y + c = 0`.

For example, this three-line submission has one triangular face when `n=3`:
```json
{"lines": [[1, 0, 0], [0, 1, 0], [1, 1, -1]]}
```

- There must be exactly `n` triples, each containing three JSON integers.
- Each coefficient must have absolute value at most `10^30`.
- At least one of `a` and `b` must be nonzero.
- Proportional triples represent the same line and are rejected as duplicates.
- Parallel lines and intersections of three or more lines are allowed.
- The file must be at most 65,536 bytes and must not be a symlink.
- Floats, booleans, NaN, infinity, duplicate JSON keys, and extra fields are invalid.

Integers specify rational lines exactly; rational coefficients can be converted to integers by clearing denominators, provided they meet the coefficient bound. There is no bounding box, minimum triangle area, or geometric tolerance. All intersections and ordering comparisons use exact arithmetic.

The evaluator reads only this data file. It never executes submitted programs, imports submission modules, or trusts a score supplied by the submission.

## Metric and parameters

| **Name** | **Meaning** | **Direction / default** |
| --- | --- | --- |
| `triangles` | Verified number of bounded triangular faces | Maximize |
| `n` | Required number of distinct lines, from 3 through 100 | Default: 18 |

`n` is a primary comparison setting: a score for 18 lines is compared with other 18-line scores, not with a score for another line count. The geometric rule and exact arithmetic are also fixed comparison settings. Invalid submissions return `passed: false` with a reason and receive no valid score.

The output includes the zero-based indices of the three supporting lines for each counted triangle, so results can be inspected and plotted independently.

The watchdog is 120 seconds to protect the evaluator from hangs. Search runtime is not scored or limited by this hill: any construction method may be used to produce the submission before evaluation.

## Validation and private checks

This is a deterministic geometric optimization task, so there is no training dataset or hidden target arrangement. Both validation and final evaluation count the same submitted arrangement with the same exact rule; `final=True` changes only an informational report field.

`private/validation.json` and `private/test.json` contain separate held-out regression fixtures for checking the evaluator, not data fed to a submitted solver. They are loaded by the hill's tests and are excluded from public source by the hill packaging system. No answer from these fixtures is used as a submission's score. Public tests also compare the counting algorithm against an independent exact triangle-interior intersection check.

## Baseline and local verification

`examples/baseline/solution.json` contains the 18 lines `2*i*x - y - i*i = 0`, for `i = 0, ..., 17`. It has 16 triangular faces. This is a simple valid starting point, not a claimed best-known construction.
```sh
autolab hills check kobon-triangles
uv tool run --from hills==0.11.0 hills eval <submission-directory> -H kobon-triangles
```

The line count, input bounds, scoring rule, and evaluator are fixed for a given hill version. Improving a construction does not change those rules.

## Capture qualification

The supplied authenticated render does not expose a separate immutable AutoLab hill-version token. This record therefore binds the exact captured body by Git blob identity. Before any final competition submission, the live hill must be re-read and compared against this capture. The `hills==0.11.0` string above is the package pin in the displayed local-evaluation command; it is not treated as an AutoLab hill-version identifier.

The page sidebar displayed `7 hills`. The Human Steward has clarified that the OpenMath sprint contains six hills and that the displayed seven-count is a typo. This clarification affects campaign cardinality only; it does not alter the mathematical or evaluator semantics of this hill.
