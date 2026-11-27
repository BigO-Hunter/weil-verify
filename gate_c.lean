import StacksFrontier.AlgebraicGeometry.EtaleCohomology.Trace.WeilIIWeightBound
import StacksFrontier.AlgebraicGeometry.EtaleCohomology.Trace.LaumonFourierLineAwayFibreOffTop
import StacksFrontier.AlgebraicGeometry.EtaleCohomology.FourierDeligne.LaumonFourierLineAbsIrrInputProof
import Weil.AlgebraicGeometry.EtaleCohomology.Trace.DeligneWeilConjecture

/-! # AXIOM_GATE part 2 — the three build-blocked targets

Run from `Weil/` with `LAKE_JOBS=1 LEAN_NUM_THREADS=1 lake env lean ../gate_c.lean`.
Requires the serial build (README → Reproduce / verify; AXIOM_GATE_PART2.md) to have
produced these oleans.
Verdict rule: `[propext, Classical.choice, Quot.sound]` = stdlib-only = CLEAN.
Any `sorryAx`, `Lean.ofReduceBool`, `native_decide` or project axiom = DIRTY.
-/

-- (a) Weil II weight bound, Tag 03VH
#print axioms Stacks.EtaleCohomology.LAdicSheaf.weightBound

-- (b) Deligne's theorem in the form the K3 step consumes
#print axioms Weil.satisfiesWeilEstimate

-- (c) LaumonFourier purity conclusions
#print axioms Stacks.EtaleCohomology.laumonFourierLineAbsIrrInput'
#print axioms Stacks.EtaleCohomology.isLisse_laumonFourierFamilySheaf
#print axioms Stacks.EtaleCohomology.laumonFourierLineAwayFibreVanishing_of_top

-- (d) the purity engine each of the above funnels into (already CLEAN, gate_a)
#print axioms Stacks.EtaleCohomology.isWeilNumber_of_forall_isCharpolyPureOfWeight
