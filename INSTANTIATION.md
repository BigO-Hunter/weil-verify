# INSTANTIATION: can Katz 1988 Thm 4.1.1 / FKM 2013 Prop 2 be instantiated from AxiomMath/Weil?

Target: the Kloosterman bound |Kl_3(a; q)| ≤ 3 q^{1/2} (normalized ≤ 3) — a Deligne-consequence via the Kloosterman sheaf, of the kind consumed by bounded-prime-gap work.

## What the repo+dep already give (kernel-checkable, pending build)
1. Abstract estimate engine: purity-along-all-embeddings ⇒ eigenvalues are Q-Weil numbers of the right weight (`isAlgebraic_and_norm_eq_of_forall_isCharpolyPureOfWeight`, FK IV.4 lemma). This is the exact form the |Kl_3| ≤ 3 argument consumes.
2. General weight bound with COMPACT SUPPORT on open varieties: `LAdicSheaf.weightBound` (Tag 03VH) — H^i_c(X_k̄, F_ρ), w ≤ i, w = i smooth proper.
3. Fourier–Laumon machinery for the ADDITIVE LINE: ~10 LaumonFourier* modules computing the Fourier family via Artin–Schreier characters + integral lattice models, concluding in `IsCharpolyPureOfWeight` — i.e. the pointwise-purity input for AS-type families is not just assumed but computed on the line.
4. Artin–Schreier sheaf machinery (ArtinSchreierSequence, artinSchreierCharacter_*), Kummer-type characters, L-function rationality on separated finite-type varieties, ℓ-adic trace formula (LAdicTraceFormulaFinal), Poincaré duality package (FrobeniusPoincarePairing), field-of-constants decomposition.

## What is MISSING between this machinery and |Kl_3| ≤ 3
1. **The Kloosterman sheaf as a named object**: the lisse rank-3 sheaf on G_m obtained (for Kl_3) as the (dual of the) Fourier family away from 0 of the constant sheaf on A^1 — construction + lisse-ness + rank bound. The LaumonFourierLine family modules compute precisely this family's fibers/cohomology, so the gap is "package it as a lisse sheaf with a rank bound" (bounded work, likely weeks), not "invent the machinery".
2. **Stalk trace = Kloosterman sum**: tr(Frob_a | Kl_{3,a}) = Kl_3(a;q) via the sheaf-function correspondence specialized to AS + trivial characters. Components exist (AS character computations + trace formula); needs assembly.
3. **Purity of Kl_3 at every a ∈ G_m(F_q)**: via the Fourier-family purity conclusions (item 3 above) — the hard Deligne input, present on the line family.
4. Rank(Kl_3) ≤ 3 with each stalk eigenvalue weight 1 ⇒ |Kl_3(a)| ≤ 3 q^{1/2} then falls out of `isAlgebraic_and_norm_eq_of_forall_isCharpolyPureOfWeight` directly.

## Katz 1988 Thm 4.1.1 / FKM 2013 Prop 2 specifically
- These refine/extend the base bound (sums over subsets, hybrid estimates, the FKM refinement |Kl_3| ≤ 3 with the exact constant and the stronger p-adic route). Their PROOF INPUTS are: Deligne RH on curves + weight bound machinery + sheaf constructions — all of the cohomological side exists here; the FKM refinement additionally uses p-adic estimates (hypergeometric-style) NOT present in the repo.
- Verdict: the cohomological core (what made these "5–10 year formalization" items) is DELIVERED by Weil+Stacks modulo the assembly items above. The FKM p-adic refinement input, if the refined constant is needed rather than the basic bound, remains custom work but on top of a formalized base.

## Bottom line
IF the build verifies + `#print axioms` comes back clean for `isAlgebraic_and_norm_eq_of_forall_isCharpolyPureOfWeight`, `weightBound`, and `satisfiesWeilEstimate`, then:
- Katz 1988 Thm 4.1.1-class and FKM 2013 Prop 2-class inputs move from UNFORMALIZED (5–10y) to INSTANTIABLE (assembly estimate: weeks–months, not years).
- The formalize→instantiate flip is JUSTIFIED for the Kloosterman-bound branch; the p-adic refinement sub-branch may retain custom work.
- Residual risk: repo is AI-generated, human review pending; a compiled + axiom-clean status is strong but not the same as reviewed statements (statement-level fidelity to FK/SGA needs a human read of definitions like `IsCharpolyPureOfWeight`, `HasDeligneConclusions` before betting exact constants on it).
