# REPO_MAP: AxiomMath/Weil — claims vs content

Verified 2026-11-07, HEAD 27cdb2049be62ee2911429b47f54774078450e32.

## Identity / provenance
- github.com/AxiomMath/Weil, GitHub repo created 2026-11-06T00:55Z, pushed 2026-11-06T02:50Z, 14 stars, 2 forks, Apache-2.0. 5.4 MB source.
- Tip commit 2026-11-05: "One library: WeilFrontier renamed to Weil" — the repo OBJECT is one day old, but the commit message shows it is a rename of a prior "WeilFrontier" library; the underlying effort is older than the repo date. Provenance of the AI-agent work (org says modules "written by AI agents") is not further traceable from public data.
- README: Lean 4 (v4.34.0-rc2) formalization of the proof of the Weil conjectures following Freitag–Kiehl 1988, on Mathlib@16edf57 + AxiomMath/Stacks@012108f ("The Stacks Project in Lean", ~63k Lean files). "All four Weil conjectures are proved... no `sorry`, no `native_decide`, no added axiom." "About 980 modules written by AI agents. Every proof is kernel-checked; the code has not yet been reviewed by humans."

## Claims (README, all with explicit theorem statements)
1. Rationality of Z_X(t) for any finite-type X/k — `exists_mul_zetaSeries_eq` (ZetaRationality.lean).
2. Functional equation (smooth projective pure dim n) — `prod_aeval_inv_rationalFrobeniusCharpolyReverse_zpow_eq` (DeligneFunctionalEquation.lean).
3. Riemann hypothesis (Deligne) — `satisfiesWeilEstimate` (DeligneWeilConjecture.lean) + Weil's original form (WeilRiemannHypothesisForm.lean). Derived from `LAdicSheaf.weightBound` (Stacks Tag 03VH) "proved in StacksFrontier along Laumon's Fourier-transform route".
4. Betti numbers via Artin comparison (BettiNumber.lean), good reduction.
5. LeanEval problem `weil_conjectures` restated in Mathlib-only terms and proved verbatim (Weil/LeanEval/WeilConjectures.lean).
6. Axiom claim: only propext, Classical.choice, Quot.sound.

## Content (measured, HEAD)
- 980 .lean files in Weil/; EtaleCohomology/Trace/ holds 30 files incl. all four conjecture files + `WeilEstimateFromPurityAllEmbeddings.lean` (exists, tagged `@[weil "lem_fk404_weil_estimate_from_purity_all_embeddings"]`, cites FK IV.4).
- Grep: 0 `sorry`, 0 `native_decide`, 0 `unsafe`, 0 top-level `axiom` declarations in Weil/.
- Dependency AxiomMath/Stacks@012108f: 62,975 files, 46 `sorry` occurrences, no genuine `axiom` declarations found by grep (hits are docstring prose about Stacks "Situation (A)/(B)/(C)"). Definitive check = `#print axioms` post-build.
- DEEPER THAN CLAIMED: StacksFrontier contains the Weil II apparatus — `LAdicSheaf.weightBound` (Tag 03VH: eigenvalues on H^i_c(X_kbar, F) are |ι λ| ≤ q^{w/2}, w ≤ i, w = i for smooth proper, under `HasDeligneConclusions`), a ~12-file WeilII* family (dimension induction, final assembly, curve bound), a ~10-file LaumonFourier* family (Artin–Schreier lattice models for the Fourier family, with `IsCharpolyPureOfWeight` conclusions), Artin–Schreier sheaf machinery, L-function rationality via H^ν_c for separated finite-type X with compactification (open varieties covered).
- No Kloosterman-sheaf construction anywhere (grep "kloosterman": 0).
