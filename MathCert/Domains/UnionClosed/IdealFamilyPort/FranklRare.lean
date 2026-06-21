/-
  FranklRare.lean

  ideal 集合族上の「レア頂点の存在」：
  ∃ v ∈ ground, 2 * deg(v) - |F| ≤ 0

  方針（射影・単射）：
  - carrier から ground を除いた有限集合の中で card を最大化する M を 1 つ取る。
  - v を ground \ M から 1 点取る（v ∉ M）。
  - ϕ : S(v) → Del(v) を
       ϕ(U) = M, ϕ(X) = X.erase v (X ≠ U)
    で定義する。
  - ϕ が well-defined かつ単射であることを示す。
  - よって |S(v)| ≤ |Del(v)|、従って 2|S(v)| ≤ |carrier|。
  - 定義により 2 * degree(v) - |F| ≤ 0（＝ rare）。

  依存：Core.lean の SetFamily / Ideal の定義と基本補題。
-/

import Mathlib.Data.Finset.Powerset
import Mathlib.Data.Finset.Max
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import MathCert.Domains.UnionClosed.IdealFamilyPort.Core

namespace IdealFamily

open scoped BigOperators
open Finset

/-- rare の述語（ℤ 版）：`2*deg(v) - |F| ≤ 0`. -/
def SetFamily.isRare {α : Type*} [DecidableEq α]
  (SF : SetFamily α) [DecidablePred SF.sets] (v : α) : Prop :=
  (2 : ℤ) * SF.degree v - SF.numEdges ≤ 0

namespace Ideal

variable {α : Type*} [DecidableEq α]
variable (F : Ideal α)
variable [DecidablePred F.sets]

/-- レア頂点の存在（ideal family 版） -/
theorem ideal_version_of_frankl_conjecture :
  ∃ v ∈ F.ground, F.toSetFamily.isRare v := by
  classical
  -- 省略記法
  let SF := F.toSetFamily
  -- proper 部分（ground を除いた carrier）
  let C : Finset (Finset α) := SF.carrier
  let Cp : Finset (Finset α) := C.erase F.ground

  -- Cp が非空（∅ が入る）：
  have hEmpty_mem : F.sets (∅ : Finset α) := F.has_empty
  have hEmpty_subset : (∅ : Finset α) ⊆ F.ground := by
    intro x hx; exact False.elim (Finset.notMem_empty x hx)
  have hEmpty_inC : (∅ : Finset α) ∈ C := by
    have hpow : (∅ : Finset α) ∈ SF.ground.powerset :=
      by simp
    let fs := Finset.mem_filter.mpr ⟨hpow, hEmpty_mem⟩
    simp_all only [SetFamily.inc_ground, C, SF]
    exact fs

  have hGround_inC : F.ground ∈ C := by
    have hpow : F.ground ∈ SF.ground.powerset := by
      simp_all only [SetFamily.inc_ground, mem_powerset, subset_refl, C, SF]
    have hset : F.sets F.ground := F.has_ground
    let fm := Finset.mem_filter.mpr ⟨hpow, hset⟩
    simp_all only [SetFamily.inc_ground, C, SF]
    exact fm
  have hCp_ne : Cp.Nonempty := by
    refine ⟨∅, ?_⟩
    have hneq : (∅ : Finset α) ≠ F.ground := by
      -- ground は非空
      have : F.ground.Nonempty := F.nonempty_ground
      exact by
        intro h; have := Finset.nonempty_iff_ne_empty.mp this
        simp_all only [subset_refl, SetFamily.nonempty_ground, ne_eq, not_true_eq_false, C, SF]
    simpa [Cp] using Finset.mem_erase.mpr ⟨hneq, hEmpty_inC⟩

  -- Cp の中で card を最大にする M を取る
  obtain ⟨M, hMin, hMax⟩ := Finset.exists_max_image Cp (fun s => s.card) hCp_ne
  have hM_inC : M ∈ C := (Finset.mem_of_mem_erase hMin)
  have hM_sets : F.sets M := by
    rcases Finset.mem_filter.mp hM_inC with ⟨hPowM, hSetM⟩
    simpa [Ideal.toSetFamily_sets] using hSetM
  have hM_sub : M ⊆ F.ground := by
    rcases Finset.mem_filter.mp hM_inC with ⟨hPowM, _⟩
    exact Finset.mem_powerset.mp hPowM
  have hM_ne_ground : M ≠ F.ground := (Finset.mem_erase.mp hMin).1

  -- v を ground \ M から 1 点取る
  have hNotSubset : ¬ F.ground ⊆ M := by
    intro h
    exact hM_ne_ground (Finset.Subset.antisymm hM_sub h)
  have hExists : ∃ v, v ∈ F.ground ∧ v ∉ M := by
    -- 「¬ ground ⊆ M」から存在を取り出す
    -- ⊆ の定義に展開
    -- (∀ {a}, a ∈ ground → a ∈ M) の否定
    classical
    simp only [Finset.subset_iff, not_forall] at hNotSubset
    obtain ⟨x, hxU, hxM⟩ := hNotSubset
    exact ⟨x, hxU, hxM⟩

  rcases hExists with ⟨v, hvU, hvNotM⟩

  -- 記号：S(v), Del(v)
  let S  : Finset (Finset α) := SF.S v
  let SS : Finset (Finset α) := SF.delCarrier v

  -- φ の定義
  let phi (X : Finset α) : Finset α :=
    if hX : X = F.ground then M else X.erase v

  -- φ は S から S̄ へ写る
  have phi_maps :
    ∀ ⦃X⦄, X ∈ S → phi  X ∈ SS := by
    intro X hXin
    rcases Finset.mem_filter.mp hXin with ⟨hXinC, hvXin⟩
    rcases Finset.mem_filter.mp hXinC with ⟨hXpow, hXset⟩
    by_cases hTop : X = F.ground
    · -- φ(U) = M
      have hMinC : M ∈ C := hM_inC
      have hv_not : v ∉ M := hvNotM
      -- M ∈ S̄
      have : M ∈ SF.carrier := hMinC
      have hIn : M ∈ SS := by
        simp only [SS, SetFamily.delCarrier]
        exact Finset.mem_filter.mpr ⟨hMinC, hv_not⟩

      subst hTop
      simp only [phi, dif_pos rfl]
      exact hIn
    · -- φ(X) = X.erase v
      have hX_neU : X ≠ F.ground := hTop
      -- 下方閉性（X ≠ ground）より X.erase v ∈ F
      have hSub : X.erase v ⊆ X := Finset.erase_subset _ _
      have hXerase_set : F.sets (X.erase v) :=
        F.down_closed (A := X.erase v) (B := X) (by simpa [Ideal.toSetFamily_sets] using hXset)
          (by simp [hX_neU]) hSub
      -- carrier への所属
      have hXerase_subU : X.erase v ⊆ F.ground := by
        have : SF.sets (X.erase v) := by simpa [Ideal.toSetFamily_sets] using hXerase_set
        simpa [Ideal.toSetFamily_ground] using (SF.inc_ground (s := X.erase v) this)
      have hXerase_inC : X.erase v ∈ C := by
        have hpow : X.erase v ∈ SF.ground.powerset :=
          Finset.mem_powerset.mpr hXerase_subU
        have hset : SF.sets (X.erase v) := by simpa [Ideal.toSetFamily_sets] using hXerase_set
        let fm :=Finset.mem_filter.mpr ⟨hpow, hset⟩
        simp_all [C, SF, Cp, S]
        exact fm
      have hv_not : v ∉ X.erase v := by simp
      -- よって S̄ に入る
      have : X.erase v ∈ SS := by
        simp only [SS, SetFamily.delCarrier]
        exact Finset.mem_filter.mpr ⟨hXerase_inC, hv_not⟩

      simp only [phi, dif_neg hTop]
      exact this

  -- φ の単射（S 上）
  have phi_inj : ∀ {X1} (hX1 : X1 ∈ S) {X2} (hX2 : X2 ∈ S),
      phi  X1 = phi  X2 → X1 = X2 := by
    intro X1 hX1 X2 hX2 hEq
    have hvX1 : v ∈ X1 := (Finset.mem_filter.mp hX1).2
    have hvX2 : v ∈ X2 := (Finset.mem_filter.mp hX2).2
    by_cases h1 : X1 = F.ground
    · have hφ1 : phi  X1 = M := by
        subst h1
        simp only [phi, dif_pos rfl]

      have hφ2M : phi  X2 = M := by
        rw [hφ1] at hEq
        exact hEq.symm
      by_cases h2 : X2 = F.ground
      · simp [h1, h2]
      · -- X2 ≠ ground の場合は矛盾
        have hErase : X2.erase v = M := by
          have : phi X2 = X2.erase v := by
            simp only [phi, dif_neg h2]
          rw [this] at hφ2M
          exact hφ2M
        -- X2 = insert v (X2.erase v) = insert v M
        have hX2_eq : X2 = insert v (X2.erase v) := by
          subst hErase h1
          simp_all only [SetFamily.inc_ground, erase_nonempty, mem_erase, ne_eq, not_false_eq_true,
            card_erase_of_mem, and_imp, not_true_eq_false, and_true, insert_erase, C, SF, Cp, S, SS]
        have hX2_eq' : X2 = insert v M := by simpa [hErase] using hX2_eq
        -- X2 は proper（ground ではない）かつ carrier の元
        have hX2_inC : X2 ∈ C := (Finset.mem_filter.mp hX2).1
        have hX2_inCp : X2 ∈ Cp := by
          exact Finset.mem_erase.mpr ⟨h2, hX2_inC⟩
        -- card 矛盾：card X2 = card M + 1
        have hCard : X2.card = M.card + 1 := by
          have : v ∉ M := hvNotM
          simp [hX2_eq']
          exact card_insert_of_notMem hvNotM
        have hMaxIneq : X2.card ≤ M.card := by
          have := hMax X2 hX2_inCp
          simpa using this
        -- 矛盾
        apply (lt_irrefl (M.card)).elim
        calc M.card < M.card + 1 := Nat.lt_succ_self _
          _ = X2.card := hCard.symm
          _ ≤ M.card := hMaxIneq
    · -- X1 ≠ ground
      by_cases h2 : X2 = F.ground
      · -- 対称な矛盾
        have hφ2 : phi X2 = M := by
          subst h2
          simp only [phi, dif_pos rfl]
        have hφ1M : phi  X1 = M := by
          rw [hφ2] at hEq
          exact hEq
        -- X1 ≠ ground なので X1.erase v = M となり，先ほどと同様に矛盾
        have hErase : X1.erase v = M := by
          have : phi X1 = X1.erase v := by
            simp only [phi, dif_neg h1]
          rw [this] at hφ1M
          exact hφ1M
        have hX1_eq : X1 = insert v (X1.erase v) := by
          exact (insert_erase hvX1).symm
        have hX1_inC : X1 ∈ C := (Finset.mem_filter.mp hX1).1
        have hX1_inCp : X1 ∈ Cp := by
          exact Finset.mem_erase.mpr ⟨h1, hX1_inC⟩
        have hCard : X1.card = M.card + 1 := by
          have : v ∉ M := hvNotM
          rw [hX1_eq]
          simp [hErase]
          exact card_insert_of_notMem hvNotM

        have hMaxIneq : X1.card ≤ M.card := by
          have := hMax X1 hX1_inCp
          simpa using this
        omega
      · -- どらも ground でない：erase の等しさから復元
        have hEraseEq : X1.erase v = X2.erase v := by
          have hφ1 : phi X1 = X1.erase v := by
            simp only [phi, dif_neg h1]
          have hφ2 : phi X2 = X2.erase v := by
            simp only [phi, dif_neg h2]
          rw [hφ1, hφ2] at hEq
          exact hEq
        have hX1_eq : X1 = insert v (X1.erase v) := by
          exact (insert_erase hvX1).symm
        have hX2_eq : X2 = insert v (X2.erase v) := by
          exact (insert_erase hvX2).symm
        rw [hX1_eq, hX2_eq, hEraseEq]

  -- 単射から |S| ≤ |S̄|
  have hCardLe : S.card ≤ SS.card := by
    -- Finset の inj_on 版カード不等式
    refine Finset.card_le_card_of_injOn
      (f := fun X => phi  X) ?maps ?inj
    · -- 値域に入る
      intro X hX; exact phi_maps hX
    · -- 単射
      intro X1 hX1 X2 hX2 hEq; exact phi_inj  hX1 hX2 hEq

  -- |S| と |Del| の分割（filter の標準恒等式）
  have hSplit :
      S.card + SS.card = C.card := by
    -- `filter p` と `filter ¬p` の和が全体の card
    simp [S, SS, SetFamily.S, SetFamily.delCarrier]
    exact Finset.card_filter_add_card_filter_not (s := C) (p := fun s => v ∈ s)


  -- Nat 版：2 * |S| ≤ |C|
  have hNat : 2 * S.card ≤ C.card := by
    -- |S| + |S| ≤ |S| + |S̄| = |C|
    have hNat' : S.card + S.card ≤ C.card := by
      have := Nat.add_le_add_left hCardLe S.card
      simpa [hSplit] using this
    omega

  -- ℤ 版へ持ち上げて rare を得る
  have hZ : (2 : ℤ) * SF.degree v ≤ SF.numEdges := by
    -- degree = |S|, numEdges = |C|
    have hZ' : ((2 * S.card : ℕ) : ℤ) ≤ (C.card : ℤ) := by exact_mod_cast hNat
    simpa [SetFamily.degree_eq_zcast_degreeNat, SetFamily.degreeNat_eq_cardS,
           SetFamily.numEdges_eq_zcast_card, S] using hZ'
  have hRare : SF.isRare v := by
    -- a ≤ b ↔ a - b ≤ 0
    dsimp [SetFamily.isRare]
    simp_all [C, SF, Cp, S, SS]
    omega

  exact ⟨v, hvU, hRare⟩

end Ideal
end IdealFamily
