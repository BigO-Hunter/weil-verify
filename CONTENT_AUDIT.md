# CONTENT_AUDIT: what WeilEstimateFromPurityAllEmbeddings.lean (and friends) actually prove

## The named file (Weil/AlgebraicGeometry/EtaleCohomology/Trace/WeilEstimateFromPurityAllEmbeddings.lean)
Pure linear-algebra layer (no schemes in its statements): V a f.d. Q_ℓ-vector space, φ an endomorphism, Q ∈ ℕ, w ∈ ℤ.

- `isWeilNumber_of_forall_isCharpolyPureOfWeight`: if φ's charpoly is ι-pure of weight w (all roots |ι λ| = Q^{w/2}) for EVERY ring hom ι : Q_ℓ →+* C, then every ring hom L →+* C (L alg closure of Q_ℓ) sends every eigenvalue of φ to a Q-Weil number of weight w.
- **`isAlgebraic_and_norm_eq_of_forall_isCharpolyPureOfWeight`** (`@[weil "lem_fk404_weil_estimate_from_purity_all_embeddings"]`, cites FK Ch. IV §4): under the all-embeddings purity hypothesis, every eigenvalue λ ∈ L is ALGEBRAIC OVER Q and |ι' λ| = Q^{w/2} for every field embedding ι' : Q(λ) →+* C.
- Verdict on this file: honest, precise, exactly the abstract Deligne-consequence machinery a Kloosterman bound needs. NOT sorry-ridden, NOT scaffold (full proofs present, kernel-checked pending our build).

## The layer below (StacksFrontier, pinned rev)
- `LAdicSheaf.weightBound` (Tag 03VH): for a continuous representation ρ of the étale fundamental group (geometric point x), IF `HasDeligneConclusions` holds along every ι : Q_ℓ →+* C, THEN every eigenvalue of (geometric) Frobenius on H^i_c(X_k̄, F_ρ) is algebraic of |ι·| ≤ q^{w/2} with w ≤ i an integer (w = i when X smooth proper). This is the general Weil II weight bound — cohomology with COMPACT SUPPORT on separated finite-type (open!) varieties.
- The `HasDeligneConclusions` hypothesis is the pointwise-purity input (Deligne's conjecture). The WeilII* family (WeilIIDimensionInduction, WeilIIFinalAssembly*, WeilIICurveBound, RationalPointPurityReduction, GeometricComponentsPurityReduction) is the induction apparatus around it; the LaumonFourier* family computes the line Fourier family (Artin–Schreier character + integral lattice model) and lands in `IsCharpolyPureOfWeight` conclusions — i.e. the hypothesis is DISCHARGED for the Artin–Schreier/Fourier line families, which is exactly the Kloosterman-sheaf family type. Caveat: a full read of whether HasDeligneConclusions is discharged for arbitrary pointwise-pure families (Weil II main theorem) or only for the computed families was out of scope of this pass.
- No `sorry` in Weil/ (980 files); 46 `sorry` grep hits in the Stacks dep (63k files) — whether any is in the import closure of the key theorems is settled only by `#print axioms` (see AXIOM_GATE.md).

## SORRY/AXIOM COUNT (static)
- Weil repo: 0 sorry / 0 native_decide / 0 unsafe / 0 axiom decls.
- Stacks@012108f: 46 sorry grep hits / no axiom decls found.
- DEFINITIVE (`#print axioms` on the three key theorems): pending build completion — recorded in AXIOM_GATE_PART2.md.
