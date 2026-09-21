# RM-DIO-004 bounded certificate

MATHCERT certifies the exact finite statement for `-1,000,000 <= y <= 1,000,000`, with `x` unrestricted. The independent checker regenerates the interval rather than trusting the MATHSOLVE list.

The certificate records twelve ordered pairs: `(-4929,30), (-15,3), (-5,2), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1), (6,2), (16,3), (4930,30)`.

This is Level-2 certification under the MATHCERT ladder. It is not a proof of the unrestricted problem. In particular, it supplies no global height bound for integral points on the associated genus-two curve.

Replay with `python ci/replay_certificates.py`. Mutation coverage is included in `python ci/test_audit_certificate_coverage.py`.
