import MathCert.Domains.UnionClosed.IdealFamilyPort.Core
import MathCert.Domains.UnionClosed.IdealFamilyPort.FranklRare

/-!
# Ideal-Family Port Aggregator

This file exposes the checked local port surface from the external
`frankl_lean` ideal-family development. The NDS/average-rarity theorem is not
imported here: the audited upstream file containing that theorem has active
proof placeholders at the pinned commit.
-/

namespace MathCert.UnionClosed.IdealFamilyPort

abbrev SetFamily := _root_.IdealFamily.SetFamily
abbrev Ideal := _root_.IdealFamily.Ideal

end MathCert.UnionClosed.IdealFamilyPort
