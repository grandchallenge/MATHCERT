# Agent instructions

**Engineering architecture and reliability:** Adopt [GCL-ENGINEERING-001 v1.0.0](https://github.com/grandchallenge/gcl-standards/blob/2a3cfed9419ba9b74eeaaee70b9db8c3f47f3c9b/standards/GCL-ENGINEERING-001.md), pinned at protected `gcl-standards` commit `2a3cfed9419ba9b74eeaaee70b9db8c3f47f3c9b`. Engineering agents own architecture, necessity, integration, tests, deploy/readback and retirement; reuse GitHub and existing components before inventing infrastructure. Do not duplicate workflow authority or mistake CI/merge for live completion. Preserve this repository's superior, reserved, and domain-specific policies. Cross-repository adoption requires explicit readback, never assumption.

MATHCERT is the sole mathematics certification authority. Under
`GCL-AGENT-STAFFING-001` version `1.0.0`, one Codex system may prepare evidence,
staff multiple preparatory roles through distinct logical passes, merge
non-reserved maintenance through satisfied protected controls, and read back
the result. Authoring-system Adversary and Referee passes are declared
`non_authoring_read_only`.

No system may certify a mathematical claim for which it supplied the sole
construction or verification evidence. Automation may not write directly to a
protected branch, manufacture certification authority, or infer certification
from CI, numerical evidence, review, or integration.

MATHCERT adopts `GCL-AGENT-CONTINUITY-001@1.0.0` from
`grandchallenge/INTELLECT/governance/agent_execution/GCL-AGENT-CONTINUITY-001.md`.
After interruption or agent substitution, the exact claim or subject,
certification route, candidate artifact, and material evidence identities must
be rebound before certification action. Construction authorship and
verification provenance remain explicit.

Operational state may transfer to a successor agent, but certification authority and substantive independence do not transfer automatically.
A continuity receipt cannot satisfy an independence requirement and cannot
serve as a certification disposition. If agent substitution materially affects
a non-authoring or independence condition, that condition must be re-evaluated.
A changed exact subject or evidence identity requires rebinding. CI success,
protected integration, or a predecessor-agent conclusion does not imply
certification.
