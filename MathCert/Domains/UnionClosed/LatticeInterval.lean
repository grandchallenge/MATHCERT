import Mathlib.Data.Fintype.Order
import Mathlib.Order.Atoms.Finite
import Mathlib.Order.Hom.Lattice
import Mathlib.Order.Irreducible
import Mathlib.Order.LatticeIntervals
import Mathlib.Order.Preorder.Chain

/-!
# Upper intervals in finite lattices

This file collects the generic interval machinery used in the formalization
of Bouchard's Theorem 2.13.
-/

namespace MathCert.UnionClosed.Lattice

open Finset Set

universe u

variable {L : Type u} [Fintype L] [Lattice L] [BoundedOrder L]

/-- Two elements are incomparable when neither lies below the other. -/
def Incomparable (a b : L) : Prop :=
  ¬a ≤ b ∧ ¬b ≤ a

theorem incomparable_comm {a b : L} :
    Incomparable a b ↔ Incomparable b a := by
  simp only [Incomparable, and_comm]

/-- The set of lattice elements incomparable with `x`. -/
def incomparableSet (x : L) : Set L :=
  {y | Incomparable y x}

/-- The finite set of lattice elements incomparable with `x`. -/
noncomputable def incomparableFinset (x : L) : Finset L := by
  classical
  exact Finset.univ.filter fun y => Incomparable y x

@[simp]
theorem mem_incomparableFinset {x y : L} :
    y ∈ incomparableFinset x ↔ Incomparable y x := by
  classical
  simp [incomparableFinset]

theorem le_or_ge_of_not_incomparable {x y : L}
    (h : ¬Incomparable y x) :
    y ≤ x ∨ x ≤ y := by
  simp only [Incomparable, not_and_or, Classical.not_not] at h
  exact h

theorem inf_lt_of_incomparable {x y : L} (h : Incomparable y x) :
    x ⊓ y < x := by
  refine lt_of_le_of_ne inf_le_left ?_
  intro heq
  apply h.2
  rw [← heq]
  exact (inf_le_right : x ⊓ y ≤ y)

theorem inf_lt_right_of_incomparable {x y : L} (h : Incomparable y x) :
    x ⊓ y < y := by
  refine lt_of_le_of_ne inf_le_right ?_
  intro heq
  apply h.1
  rw [← heq]
  exact (inf_le_left : x ⊓ y ≤ x)

theorem sup_lt_of_incomparable {x y : L} (h : Incomparable y x) :
    x < x ⊔ y := by
  refine lt_of_le_of_ne le_sup_left ?_
  intro heq
  exact h.1 ((le_sup_right : y ≤ x ⊔ y).trans_eq heq.symm)

theorem sup_lt_right_of_incomparable {x y : L} (h : Incomparable y x) :
    y < x ⊔ y := by
  refine lt_of_le_of_ne le_sup_right ?_
  intro heq
  exact h.2 ((le_sup_left : x ≤ x ⊔ y).trans_eq heq.symm)

/-- A greatest element among the elements incomparable with `x` is inf-irreducible. -/
theorem infIrred_of_greatest_incomparable
    {x c : L} (hc : Incomparable c x)
    (hgreat : ∀ y : L, Incomparable y x → y ≤ c) :
    InfIrred c := by
  constructor
  · intro hmax
    exact hc.2 (le_top.trans (hmax le_top))
  · intro a b hab
    by_contra hne
    push Not at hne
    have hca : c < a := lt_of_le_of_ne (hab.ge.trans inf_le_left) hne.1.symm
    have hcb : c < b := lt_of_le_of_ne (hab.ge.trans inf_le_right) hne.2.symm
    have hxa : x ≤ a := by
      by_cases ha : Incomparable a x
      · exact ((not_le_of_gt hca) (hgreat a ha)).elim
      rcases le_or_ge_of_not_incomparable ha with ha | ha
      · exact (hc.1 (hca.le.trans ha)).elim
      · exact ha
    have hxb : x ≤ b := by
      by_cases hb : Incomparable b x
      · exact ((not_le_of_gt hcb) (hgreat b hb)).elim
      rcases le_or_ge_of_not_incomparable hb with hb | hb
      · exact (hc.1 (hcb.le.trans hb)).elim
      · exact hb
    exact hc.2 (by rw [← hab]; exact le_inf hxa hxb)

/-- A least element among the elements incomparable with `x` is sup-irreducible. -/
theorem supIrred_of_least_incomparable
    {x c : L} (hc : Incomparable c x)
    (hleast : ∀ y : L, Incomparable y x → c ≤ y) :
    SupIrred c := by
  constructor
  · intro hmin
    exact hc.1 ((hmin bot_le).trans bot_le)
  · intro a b hab
    by_contra hne
    push Not at hne
    have hac : a < c := lt_of_le_of_ne (le_sup_left.trans hab.le) hne.1
    have hbc : b < c := lt_of_le_of_ne (le_sup_right.trans hab.le) hne.2
    have hax : a ≤ x := by
      by_cases ha : Incomparable a x
      · exact ((not_le_of_gt hac) (hleast a ha)).elim
      rcases le_or_ge_of_not_incomparable ha with ha | ha
      · exact ha
      · exact (hc.2 (ha.trans hac.le)).elim
    have hbx : b ≤ x := by
      by_cases hb : Incomparable b x
      · exact ((not_le_of_gt hbc) (hleast b hb)).elim
      rcases le_or_ge_of_not_incomparable hb with hb | hb
      · exact hb
      · exact (hc.2 (hb.trans hbc.le)).elim
    exact hc.1 (by rw [← hab]; exact sup_le hax hbx)

/-- A maximal element among those incomparable with `x` is inf-irreducible. -/
theorem infIrred_of_maximal_incomparable
    {x c : L} (hcmax : Maximal (fun y => Incomparable y x) c) :
    InfIrred c := by
  constructor
  · intro hmax
    exact hcmax.1.2 (le_top.trans (hmax le_top))
  · intro a b hab
    by_contra hne
    push Not at hne
    have hca : c < a := lt_of_le_of_ne (hab.ge.trans inf_le_left) hne.1.symm
    have hcb : c < b := lt_of_le_of_ne (hab.ge.trans inf_le_right) hne.2.symm
    have hxa : x ≤ a := by
      by_cases ha : Incomparable a x
      · exact ((not_le_of_gt hca) (hcmax.2 ha hca.le)).elim
      rcases le_or_ge_of_not_incomparable ha with ha | ha
      · exact (hcmax.1.1 (hca.le.trans ha)).elim
      · exact ha
    have hxb : x ≤ b := by
      by_cases hb : Incomparable b x
      · exact ((not_le_of_gt hcb) (hcmax.2 hb hcb.le)).elim
      rcases le_or_ge_of_not_incomparable hb with hb | hb
      · exact (hcmax.1.1 (hcb.le.trans hb)).elim
      · exact hb
    exact hcmax.1.2 (by rw [← hab]; exact le_inf hxa hxb)

/-- A minimal element among those incomparable with `x` is sup-irreducible. -/
theorem supIrred_of_minimal_incomparable
    {x c : L} (hcmin : Minimal (fun y => Incomparable y x) c) :
    SupIrred c := by
  constructor
  · intro hmin
    exact hcmin.1.1 ((hmin bot_le).trans bot_le)
  · intro a b hab
    by_contra hne
    push Not at hne
    have hac : a < c := lt_of_le_of_ne (le_sup_left.trans hab.le) hne.1
    have hbc : b < c := lt_of_le_of_ne (le_sup_right.trans hab.le) hne.2
    have hax : a ≤ x := by
      by_cases ha : Incomparable a x
      · exact ((not_le_of_gt hac) (hcmin.2 ha hac.le)).elim
      rcases le_or_ge_of_not_incomparable ha with ha | ha
      · exact ha
      · exact (hcmin.1.2 (ha.trans hac.le)).elim
    have hbx : b ≤ x := by
      by_cases hb : Incomparable b x
      · exact ((not_le_of_gt hbc) (hcmin.2 hb hbc.le)).elim
      rcases le_or_ge_of_not_incomparable hb with hb | hb
      · exact hb
      · exact (hcmin.1.2 (hb.trans hbc.le)).elim
    exact hcmin.1.1 (by rw [← hab]; exact sup_le hax hbx)

/--
If the incomparable elements form a chain, a maximal member of any nonempty
finite subcollection is above every member of that subcollection.
-/
theorem chain_maximal_is_greatest
    {x : L} (hchain : IsChain (· ≤ ·) (incomparableSet x))
    {s : Finset L}
    (hs : ∀ y ∈ s, Incomparable y x)
    {c : L} (hcmax : Maximal (· ∈ s) c) :
    ∀ y ∈ s, y ≤ c := by
  intro y hy
  by_cases hyc : y = c
  · exact hyc.le
  rcases hchain (hs y hy) (hs c hcmax.1) hyc with hyc' | hcy
  · exact hyc'
  · exact hcmax.2 hy hcy

/-- Dual form of `chain_maximal_is_greatest`. -/
theorem chain_minimal_is_least
    {x : L} (hchain : IsChain (· ≤ ·) (incomparableSet x))
    {s : Finset L}
    (hs : ∀ y ∈ s, Incomparable y x)
    {c : L} (hcmin : Minimal (· ∈ s) c) :
    ∀ y ∈ s, c ≤ y := by
  intro y hy
  by_cases hyc : y = c
  · exact hyc.ge
  rcases hchain (hs c hcmin.1) (hs y hy) (Ne.symm hyc) with hcy | hyc'
  · exact hcy
  · exact hcmin.2 hy hyc'

theorem exists_two_lower_covers_of_not_supIrred
    {c : L} (hcmin : ¬IsMin c) (hc : ¬SupIrred c) :
    ∃ a b : L, a ⋖ c ∧ b ⋖ c ∧ a ≠ b := by
  rw [not_supIrred] at hc
  rcases hc with hc | ⟨d, e, hde, hdc, hec⟩
  · exact (hcmin hc).elim
  obtain ⟨a, hda, hac⟩ := exists_le_covBy_of_lt hdc
  obtain ⟨b, heb, hbc⟩ := exists_le_covBy_of_lt hec
  refine ⟨a, b, hac, hbc, ?_⟩
  intro hab
  subst b
  have hca : c ≤ a := by
    rw [← hde]
    exact sup_le hda heb
  exact (not_le_of_gt hac.lt) hca

theorem exists_two_upper_covers_of_not_infIrred
    {c : L} (hcmax : ¬IsMax c) (hc : ¬InfIrred c) :
    ∃ a b : L, c ⋖ a ∧ c ⋖ b ∧ a ≠ b := by
  rw [not_infIrred] at hc
  rcases hc with hc | ⟨d, e, hde, hcd, hce⟩
  · exact (hcmax hc).elim
  obtain ⟨a, hca, had⟩ := exists_covBy_le_of_lt hcd
  obtain ⟨b, hcb, hbe⟩ := exists_covBy_le_of_lt hce
  refine ⟨a, b, hca, hcb, ?_⟩
  intro hab
  subst b
  have hac : a ≤ c := by
    rw [← hde]
    exact le_inf had hbe
  exact (not_le_of_gt hca.lt) hac

/--
If the incomparable elements form a chain and their greatest member is
join-reducible, then every incomparable element is inf-irreducible.
-/
theorem infIrred_of_incomparable_chain_and_greatest_not_supIrred
    {x cTop : L}
    (hchain : IsChain (· ≤ ·) (incomparableSet x))
    (hcTop : Incomparable cTop x)
    (hgreat : ∀ y : L, Incomparable y x → y ≤ cTop)
    (hcTopSup : ¬SupIrred cTop) :
    ∀ c : L, Incomparable c x → InfIrred c := by
  have hcTopInf : InfIrred cTop :=
    infIrred_of_greatest_incomparable hcTop hgreat
  have hcTop_not_min : ¬IsMin cTop := by
    intro hmin
    exact hcTop.1 ((hmin bot_le).trans bot_le)
  obtain ⟨l₁, l₂, hl₁, hl₂, hlne⟩ :=
    exists_two_lower_covers_of_not_supIrred hcTop_not_min hcTopSup
  have hlower : ∃ l : L, l ⋖ cTop ∧ l ≤ x := by
    have hnot_both :
        ¬(Incomparable l₁ x ∧ Incomparable l₂ x) := by
      rintro ⟨hl₁x, hl₂x⟩
      rcases hchain hl₁x hl₂x hlne with hle | hge
      · exact hl₁.2 (lt_of_le_of_ne hle hlne) hl₂.lt
      · exact hl₂.2 (lt_of_le_of_ne hge (Ne.symm hlne)) hl₁.lt
    rcases not_and_or.mp hnot_both with hl₁x | hl₂x
    · refine ⟨l₁, hl₁, ?_⟩
      rcases le_or_ge_of_not_incomparable hl₁x with hle | hge
      · exact hle
      · exact (hcTop.2 (hge.trans hl₁.le)).elim
    · refine ⟨l₂, hl₂, ?_⟩
      rcases le_or_ge_of_not_incomparable hl₂x with hle | hge
      · exact hle
      · exact (hcTop.2 (hge.trans hl₂.le)).elim
  obtain ⟨l, hlcTop, hlx⟩ := hlower
  intro c hcx
  by_contra hcInf
  have hc_not_max : ¬IsMax c := by
    intro hmax
    exact hcx.2 (le_top.trans (hmax le_top))
  obtain ⟨u₁, u₂, hcu₁, hcu₂, hune⟩ :=
    exists_two_upper_covers_of_not_infIrred hc_not_max hcInf
  have hupper : ∃ u : L, c ⋖ u ∧ x ≤ u := by
    have hnot_both :
        ¬(Incomparable u₁ x ∧ Incomparable u₂ x) := by
      rintro ⟨hu₁x, hu₂x⟩
      rcases hchain hu₁x hu₂x hune with hle | hge
      · exact hcu₂.2 hcu₁.lt (lt_of_le_of_ne hle hune)
      · exact hcu₁.2 hcu₂.lt (lt_of_le_of_ne hge (Ne.symm hune))
    rcases not_and_or.mp hnot_both with hu₁x | hu₂x
    · refine ⟨u₁, hcu₁, ?_⟩
      rcases le_or_ge_of_not_incomparable hu₁x with hle | hge
      · exact (hcx.1 (hcu₁.le.trans hle)).elim
      · exact hge
    · refine ⟨u₂, hcu₂, ?_⟩
      rcases le_or_ge_of_not_incomparable hu₂x with hle | hge
      · exact (hcx.1 (hcu₂.le.trans hle)).elim
      · exact hge
  obtain ⟨u, hcu, hxu⟩ := hupper
  have hc_le_top : c ≤ cTop := hgreat c hcx
  have hc_ne_top : c ≠ cTop := by
    intro h
    apply hcInf
    simpa [h] using hcTopInf
  have hc_lt_top : c < cTop := lt_of_le_of_ne hc_le_top hc_ne_top
  let w := cTop ⊓ u
  have hlw : l < w := by
    have hle : l ≤ w := le_inf hlcTop.le (hlx.trans hxu)
    refine lt_of_le_of_ne hle ?_
    intro hwl
    apply hcx.1
    have hcl : c ≤ l := by
      rw [hwl]
      exact le_inf hc_le_top hcu.le
    exact hcl.trans hlx
  have hwt : w < cTop := by
    refine lt_of_le_of_ne inf_le_left ?_
    intro hEq
    have htopu : cTop ≤ u := by
      rw [← hEq]
      exact inf_le_right
    have htop_ne_u : cTop ≠ u := by
      intro h
      exact hcTop.2 (h ▸ hxu)
    have htop_lt_u : cTop < u :=
      lt_of_le_of_ne htopu htop_ne_u
    exact hcu.2 hc_lt_top htop_lt_u
  exact hlcTop.2 hlw hwt

/--
Along an incomparable chain of inf-irreducibles with a unique doubly
irreducible element at the bottom, meeting with `x` is strictly monotone.
-/
theorem inf_strictMono_on_incomparable_chain
    {x cBot c d : L}
    (hchain : IsChain (· ≤ ·) (incomparableSet x))
    (hcBot : Incomparable cBot x)
    (hleast : ∀ y : L, Incomparable y x → cBot ≤ y)
    (hcBotSup : SupIrred cBot)
    (hallInf : ∀ y : L, Incomparable y x → InfIrred y)
    (hunique :
      ∀ a b : L,
        SupIrred a → InfIrred a → SupIrred b → InfIrred b → a = b)
    (hc : Incomparable c x) (hd : Incomparable d x) (hcd : c < d) :
    x ⊓ c < x ⊓ d := by
  have hcBotInf : InfIrred cBot := hallInf cBot hcBot
  have hdInf : InfIrred d := hallInf d hd
  have hd_not_sup : ¬SupIrred d := by
    intro hdSup
    have hdcBot := hunique d cBot hdSup hdInf hcBotSup hcBotInf
    have hcBot_le_c := hleast c hc
    exact (not_le_of_gt hcd) (hdcBot.le.trans hcBot_le_c)
  have hd_not_min : ¬IsMin d := by
    intro hmin
    exact hd.1 ((hmin bot_le).trans bot_le)
  rw [not_supIrred] at hd_not_sup
  rcases hd_not_sup with hdMin | ⟨a, b, hab, had, hbd⟩
  · exact (hd_not_min hdMin).elim
  have classify :
      ∀ z : L, z < d → z ≤ x ∨ Incomparable z x := by
    intro z hzd
    by_cases hz : Incomparable z x
    · exact Or.inr hz
    rcases le_or_ge_of_not_incomparable hz with hzx | hxz
    · exact Or.inl hzx
    · exact (hd.2 (hxz.trans hzd.le)).elim
  rcases classify a had with hax | hax
  · rcases classify b hbd with hbx | hbx
    · exact (hd.1 (hab.ge.trans (sup_le hax hbx))).elim
    ·
      have hnot_ac : ¬a ≤ c := by
        intro hac
        by_cases hpc : b = c
        · have hdc : d ≤ c := by
            rw [← hab, hpc]
            exact sup_le hac le_rfl
          exact (not_le_of_gt hcd) hdc
        rcases hchain hbx hc hpc with hbc | hcb
        · have hdc : d ≤ c := by
            rw [← hab]
            exact sup_le hac hbc
          exact (not_le_of_gt hcd) hdc
        · have hdb : d ≤ b := by
            rw [← hab]
            exact sup_le (hac.trans hcb) le_rfl
          exact (not_le_of_gt hbd) hdb
      have hmeet_le : x ⊓ c ≤ x ⊓ d :=
        inf_le_inf_left x hcd.le
      refine lt_of_le_of_ne hmeet_le ?_
      intro heq
      apply hnot_ac
      have ha_meet_d : a ≤ x ⊓ d := by
        exact le_inf hax (le_sup_left.trans hab.le)
      rw [← heq] at ha_meet_d
      exact ha_meet_d.trans inf_le_right
  · rcases classify b hbd with hbx | hbx
    ·
      have hnot_bc : ¬b ≤ c := by
        intro hbc
        by_cases hpc : a = c
        · have hdc : d ≤ c := by
            rw [← hab, hpc]
            exact sup_le le_rfl hbc
          exact (not_le_of_gt hcd) hdc
        rcases hchain hax hc hpc with hac | hca
        · have hdc : d ≤ c := by
            rw [← hab]
            exact sup_le hac hbc
          exact (not_le_of_gt hcd) hdc
        · have hda : d ≤ a := by
            rw [← hab]
            exact sup_le le_rfl (hbc.trans hca)
          exact (not_le_of_gt had) hda
      have hmeet_le : x ⊓ c ≤ x ⊓ d :=
        inf_le_inf_left x hcd.le
      refine lt_of_le_of_ne hmeet_le ?_
      intro heq
      apply hnot_bc
      have hb_meet_d : b ≤ x ⊓ d := by
        exact le_inf hbx (le_sup_right.trans hab.le)
      rw [← heq] at hb_meet_d
      exact hb_meet_d.trans inf_le_right
    ·
      by_cases habne : a = b
      · subst b
        have hda : d ≤ a := by
          rw [← hab]
          exact sup_le le_rfl le_rfl
        exact ((not_le_of_gt had) hda).elim
      rcases hchain hax hbx habne with hab' | hba'
      ·
        have hdb : d ≤ b := by
          rw [← hab]
          exact sup_le hab' le_rfl
        exact ((not_le_of_gt hbd) hdb).elim
      ·
        have hda : d ≤ a := by
          rw [← hab]
          exact sup_le le_rfl hba'
        exact ((not_le_of_gt had) hda).elim

/-- Number of elements incomparable with `x`. -/
noncomputable def incomparableCard (x : L) : Nat :=
  @Fintype.card {y : L // Incomparable y x} (Fintype.ofFinite _)

/-- Number of elements outside the principal upper interval generated by `x`. -/
noncomputable def outsideUpperIntervalCard (x : L) : Nat :=
  @Fintype.card {y : L // ¬x ≤ y} (Fintype.ofFinite _)

/--
In the difficult branch of the chain argument, every incomparable point and
its meet with `x` give two distinct points outside `Ici x`.
-/
theorem twice_incomparableCard_le_outsideUpperIntervalCard
    {x cBot : L}
    (hchain : IsChain (· ≤ ·) (incomparableSet x))
    (hcBot : Incomparable cBot x)
    (hleast : ∀ y : L, Incomparable y x → cBot ≤ y)
    (hcBotSup : SupIrred cBot)
    (hallInf : ∀ y : L, Incomparable y x → InfIrred y)
    (hunique :
      ∀ a b : L,
        SupIrred a → InfIrred a → SupIrred b → InfIrred b → a = b) :
    2 * incomparableCard x ≤ outsideUpperIntervalCard x := by
  classical
  let P := {y : L // Incomparable y x}
  let O := {y : L // ¬x ≤ y}
  letI : Fintype P := Fintype.ofFinite _
  letI : Fintype O := Fintype.ofFinite _
  let f : P × Bool → O := fun z =>
    if z.2 then
      ⟨x ⊓ z.1.1,
        fun hxmeet =>
          z.1.2.2 (hxmeet.trans inf_le_right)⟩
    else
      ⟨z.1.1, z.1.2.2⟩
  have hf : Function.Injective f := by
    rintro ⟨a, ha⟩ ⟨b, hb⟩ hEq
    cases ha <;> cases hb
    · have hab : a = b := by
        apply Subtype.ext
        exact congrArg (fun z : O => z.1) hEq
      simpa [hab]
    ·
      exfalso
      have hval := congrArg (fun z : O => z.1) hEq
      simp [f] at hval
      exact a.2.1 (hval.trans_le inf_le_left)
    ·
      exfalso
      have hval := congrArg (fun z : O => z.1) hEq
      simp [f] at hval
      exact b.2.1 (hval.symm.trans_le inf_le_left)
    ·
      have hmeet :
          x ⊓ a.1 = x ⊓ b.1 := by
        simpa [f] using congrArg (fun z : O => z.1) hEq
      have hab : a = b := by
        apply Subtype.ext
        by_contra habne
        rcases hchain a.2 b.2 (by simpa using habne) with hab | hba
        · have hablt : a.1 < b.1 :=
            lt_of_le_of_ne hab (by simpa using habne)
          have hstrict :=
            inf_strictMono_on_incomparable_chain hchain hcBot hleast
              hcBotSup hallInf hunique a.2 b.2 hablt
          exact (ne_of_lt hstrict) hmeet
        · have hbalt : b.1 < a.1 :=
            lt_of_le_of_ne hba (by simpa using Ne.symm habne)
          have hstrict :=
            inf_strictMono_on_incomparable_chain hchain hcBot hleast
              hcBotSup hallInf hunique b.2 a.2 hbalt
          exact (ne_of_lt hstrict) hmeet.symm
      simpa [hab]
  unfold incomparableCard outsideUpperIntervalCard
  have hcard := Fintype.card_le_of_injective f hf
  simpa [P, O, Nat.mul_comm] using hcard

/-- The canonical closure from a lattice to the principal upper interval. -/
def upperIntervalCeil (x y : L) : Set.Ici x :=
  ⟨x ⊔ y, le_sup_left⟩

@[simp]
theorem upperIntervalCeil_val (x y : L) :
    (upperIntervalCeil x y).1 = x ⊔ y :=
  rfl

@[simp]
theorem upperIntervalCeil_eq_self (x : L) (y : Set.Ici x) :
    upperIntervalCeil x y.1 = y := by
  apply Subtype.ext
  exact sup_eq_right.mpr y.2

@[simp]
theorem upperIntervalCeil_sup (x y z : L) :
    upperIntervalCeil x (y ⊔ z) =
      upperIntervalCeil x y ⊔ upperIntervalCeil x z := by
  apply Subtype.ext
  simp only [upperIntervalCeil_val, Set.Ici.coe_sup]
  ac_rfl

/-- Joining with `x` is a surjective join homomorphism onto `Ici x`. -/
def upperIntervalCeilSupHom (x : L) : SupHom L (Set.Ici x) where
  toFun := upperIntervalCeil x
  map_sup' := upperIntervalCeil_sup x

theorem upperIntervalCeil_surjective (x : L) :
    Function.Surjective (upperIntervalCeil x) := by
  intro y
  exact ⟨y.1, upperIntervalCeil_eq_self x y⟩

/--
Every sup-irreducible of a principal upper interval is the image of an
original sup-irreducible under the closure `y ↦ x ⊔ y`.
-/
theorem upperInterval_supIrred_has_origin
    (x : L) (q : Set.Ici x) (hq : SupIrred q) :
    ∃ j : L, SupIrred j ∧ upperIntervalCeil x j = q := by
  classical
  obtain ⟨t, htq, ht⟩ := exists_supIrred_decomposition q.1
  have htne : t.Nonempty := by
    rw [Finset.nonempty_iff_ne_empty]
    intro htempty
    subst t
    simp only [Finset.sup_empty] at htq
    apply hq.not_isMin
    intro z _
    apply Subtype.coe_le_coe.mp
    rw [← htq]
    exact bot_le
  let f := upperIntervalCeilSupHom x
  have hmap : t.sup (fun j => f j) = q := by
    rw [← Finset.sup'_eq_sup htne]
    calc
      t.sup' htne (fun j => f j) = f (t.sup' htne id) := by
        symm
        simpa only [Function.comp_apply, id_eq] using
          (map_finset_sup' f htne id)
      _ = f q.1 := by rw [Finset.sup'_eq_sup htne, htq]
      _ = q := upperIntervalCeil_eq_self x q
  obtain ⟨j, hjt, hjq⟩ := hq.finset_sup_eq hmap
  exact ⟨j, ht hjt, by simpa [f, upperIntervalCeilSupHom] using hjq⟩

/--
The upper cone of an interval element is canonically the same as its upper
cone in the ambient lattice.
-/
def upperIntervalUpperConeEquiv (x : L) (q : Set.Ici x) :
    {z : Set.Ici x // q ≤ z} ≃ {z : L // q.1 ≤ z} where
  toFun z := ⟨z.1.1, z.2⟩
  invFun z := ⟨⟨z.1, q.2.trans z.2⟩, z.2⟩
  left_inv _ := rfl
  right_inv _ := rfl

/-- Cardinality of the principal upper interval generated by `x`. -/
noncomputable def upperIntervalCard (x : L) : Nat :=
  @Fintype.card (Set.Ici x) (Fintype.ofFinite _)

/-- The upper interval has the same cardinality as the ambient cone of `x`. -/
theorem card_upperInterval_eq_upperConeType (x : L) :
    upperIntervalCard x =
      @Fintype.card {z : L // x ≤ z} (Fintype.ofFinite _) := by
  letI : Fintype (Set.Ici x) := Fintype.ofFinite _
  letI : Fintype {z : L // x ≤ z} := Fintype.ofFinite _
  unfold upperIntervalCard
  let e : Set.Ici x ≃ {z : L // x ≤ z} := Equiv.refl _
  exact Fintype.card_congr e

/-- A non-bottom principal upper interval is strictly smaller than the lattice. -/
theorem card_upperInterval_lt (x : L) (hx : x ≠ ⊥) :
    upperIntervalCard x < Fintype.card L := by
  letI : Fintype (Set.Ici x) := Fintype.ofFinite _
  letI : Fintype {y : L // x ≤ y} := Fintype.ofFinite _
  unfold upperIntervalCard
  exact
    Fintype.card_subtype_lt
      (p := fun y : L => x ≤ y)
      (x := ⊥) (by simpa using hx)

end MathCert.UnionClosed.Lattice
