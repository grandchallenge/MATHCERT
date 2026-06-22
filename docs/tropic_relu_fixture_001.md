# Tropical ReLU Fixture 001: MLP to certificate to checker

Fixture 001 is the first MATHCERT tropical-neural extraction artifact.  Its job is
not to prove that tropical algebra explains all neural computation.  Its job is to
prove one small compiler/checker loop:

```text
2D ReLU MLP -> tropical rational certificate -> pure-Python replay checker
```

The checker does not import PyTorch, NumPy, or an optimizer.  It uses exact
rational arithmetic and affine bounds over a stated box.

## Network

The certified classifier has two real inputs and two hidden ReLU units:

```text
h_sum  = ReLU(x1 + x2)
h_diff = ReLU(x1 - x2)
class_0 = 0
class_1 = 1 + h_sum + h_diff
```

The certified domain is the box

```text
-1 <= x1 <= 1
-1 <= x2 <= 1
```

The property is the margin claim

```text
for all x in [-1, 1]^2, class_1(x) - class_0(x) >= 1.
```

## Tropical rational form

A ReLU is a maximum of two affine forms:

```text
ReLU(a) = max(0, a).
```

Because the hidden-to-logit coefficients in this fixture are non-negative, the
class-1 logit expands exactly as a max-plus polynomial:

```text
class_1(x)
  = 1 + max(0, x1 + x2) + max(0, x1 - x2)
  = max(
      1,
      1 + x1 + x2,
      1 + x1 - x2,
      1 + 2*x1
    ).
```

Each logit is recorded as

```text
max(numerator_terms) - max(denominator_terms).
```

Fixture 001 uses a zero denominator, so the rational form is a max-affine
polynomial.  The rational envelope is still useful because later fixtures can
represent general piecewise-linear networks as differences of max-plus
polynomials.

## Pruning record

The raw class-1 numerator includes one intentionally redundant affine probe:

```text
x1 - 2.
```

On the certified box, `x1 - 2 <= -1`, while the constant term `1` is always
available.  The checker therefore accepts removal of the probe because it is
dominated everywhere on the domain.

This is a small but important test: pruning is not trusted as an optimization
claim.  It is accepted only when the certificate supplies a domain-local affine
dominance witness that the checker can replay.

## Margin witness

To prove

```text
class_1 - class_0 >= 1,
```

the certificate does not enumerate activation regions.  It supplies a pairwise
affine-dominance witness for the tropical rational forms.  In this fixture the
constant class-1 numerator term is enough:

```text
class1_const + class0_den0 - class0_const - class1_den0 = 1.
```

The lower bound of this affine difference over the box is exactly `1`, so the
checker accepts the margin claim.

## Trusted boundary

The trusted replay boundary is:

```text
ci/validate_tropic_relu_certificates.py
```

The checker verifies:

1. schema shape and declared trust boundary;
2. SHA-256 hashes of the network, tropical rational payload, and property;
3. exact ReLU-to-tropical expansion for non-negative hidden-to-logit weights;
4. domain-local dominance for removed affine pieces;
5. pairwise affine-dominance coverage for the claimed logit margin.

The checker is intentionally not a Lean theorem.  Its certificate level is
`script_replayed_fixture`.  A future lift can promote this to a Lean-checked
finite affine-bounds theorem once the schema stops moving.

## Run

```bash
python3 ci/validate_tropic_relu_certificates.py
python3 ci/test_validate_tropic_relu_certificates.py
```

These commands are included in the standard MATHCERT certification path through
`ci/check_lean.sh` and `ci/check_lean.ps1`.
