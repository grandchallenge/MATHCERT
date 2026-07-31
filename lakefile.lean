import Lake
open Lake DSL

package «MathCert» where
  version := v!"0.1.0"

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @ "5e932f97dd25535344f80f9dd8da3aab83df0fe6"

require mathsolve from git
  "https://github.com/grandchallenge/MATHSOLVE.git" @ "916f3434abcce29098ba7508a3b457a461461193"

@[default_target]
lean_lib «MathCert»
