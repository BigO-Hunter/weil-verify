# AXIOM_GATE — `#print axioms` on the Weil/Stacks dependencies of `|Kl_3| ≤ 3√q`

Run 2026-11-07 in `~/bigo-campaign/weil-verify/`, toolchain `leanprover/lean4:v4.34.0-rc2`
(from `Weil/lean-toolchain`), invoked as `lake env lean <file>` from inside `Weil/` with
`LEAN_NUM_THREADS=1`. Builds in this session used `LAKE_JOBS=1 LEAN_NUM_THREADS=1`.

## Verdict in one line

**The FK IV.4 estimate engine is clean — `[propext, Classical.choice, Quot.sound]`, no `sorryAx`.**
The other three gate targets (`weightBound`, `satisfiesWeilEstimate`, the `LaumonFourier*` purity
conclusion) **could not be measured in this session**: their oleans do not exist, and building them
needs 16.5k–19.4k more Stacks modules (measurements and arithmetic below). That is a *build-time*
wall, not a mathematical one, and the source-level evidence (§4) points the same way.

## 1. Gate (a) — MEASURED, CLEAN

`gate_a.lean` (imports `Weil.…Trace.WeilEstimateFromPurityAllEmbeddings` +
`…Trace.FrobeniusPoincarePairing`; ran in 54 s):

```
'Stacks.EtaleCohomology.isAlgebraic_and_norm_eq_of_forall_isCharpolyPureOfWeight' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'Stacks.EtaleCohomology.isWeilNumber_of_forall_isCharpolyPureOfWeight' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'Stacks.EtaleCohomology.isWeilNumber_of_isCharpolyPureOfWeight_comp' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
```

This is the lemma the `|Kl_3| ≤ 3 q^{1/2}` step consumes directly: eigenvalues that are
`ι`-pure of weight `w` along every embedding are algebraic with `|ι' λ| = q^{w/2}`. Its import
closure *includes* the Stacks machinery it uses (`FrobeniusPoincarePairing`, `Weil.Attr`,
`FieldTheory.IsAlgClosed.Classification`), so those are certified stdlib-only too.

## 2. Gate (b′) — MEASURED, CLEAN (Stacks-side theorems that already have oleans)

`gate_b.lean`:

```
'Stacks.EtaleCohomology.IsWeilNumber.norm_pos' depends on axioms: [propext, Classical.choice, Quot.sound]
'Stacks.EtaleCohomology.IsWeilNumber.weight_unique' depends on axioms: [propext, Classical.choice, Quot.sound]
'Stacks.EtaleCohomology.IsWeilNumber.zpow_div' depends on axioms: [propext, Classical.choice, Quot.sound]
'Stacks.EtaleCohomology.isPureOfWeight_of_duality' depends on axioms: [propext, Classical.choice, Quot.sound]
'Stacks.EtaleCohomology.exists_ringHom_complex_eq_of_transcendental' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
```

## 3. Gate (b), (c), (d) — BLOCKED ON BUILD, not measured

`#print axioms` needs the target's `.olean`. These three do not have one, and building it drags in
most of the étale-cohomology tree. Measured with `kloosterman-sheaf/closure_size.py`, which walks
`import` lines and counts each module's olean:

| target | closure | Stacks modules **unbuilt** |
|---|---:|---:|
| `Stacks…LAdicSheaf.weightBound` (Tag 03VH, `Trace/WeilIIWeightBound.lean`) | 29,128 | **19,363** of 20,352 |
| `Weil.satisfiesWeilEstimate` (`Trace/DeligneWeilConjecture.lean`) | 29,229 | **19,424** of 20,418 |
| `LaumonFourierLineAwayFibreOffTop` (fibres away from `a = 0`) | 26,705 | **16,937** of 17,929 |
| `laumonFourierFamilySheaf` (`Trace/LaumonFourierLineFamily.lean`) | 26,343 | **16,525** of 17,567 |

Tree state at the time of measurement: **9,896 oleans** total (Mathlib 8,471 + Stacks 924 +
batteries/aesop/etc. + 4 Weil), i.e. the audit's "9,775 oleans" figure is accurate but is the
*Mathlib-foundation* count — it never reached the étale-cohomology modules, and
`WeilEstimateFromPurityAllEmbeddings.olean` is one of only two Weil `Trace` oleans that exist.

Measured build throughput on this host this session (a detached
`lake build …DeligneWeilConjecture` at `LAKE_JOBS=1 LEAN_NUM_THREADS=1`, still running):
**121 new oleans in 60 minutes ≈ 2/min.** At that rate the remaining 19,424 modules are
**≈ 9,700 minutes ≈ 6.8 days of continuous single-job building**, on a host that is also running
five unrelated Lean builds. Scaling `LAKE_JOBS` up is not free here: peak memory per étale module
is large and the host is the acknowledged bottleneck, so the honest planning number is days.

## 4. Static corroboration (weaker instrument, full coverage)

The decisive instrument is blocked; the source scan covers the whole tree instead. Over all
**63k Stacks files and 980 Weil files**:

| construct that could introduce a non-stdlib axiom | found |
|---|---|
| code-level `sorry` (`… := by sorry`, `:= sorry`, `exact sorry`, `· sorry`, bare `sorry` line) | **0** |
| `axiom` declarations | **0** (all `grep` hits are docstring prose: "axiom (B) of Situation…") |
| `native_decide` | **0** |
| `implemented_by` / `unsafe def` | **0** |
| `sorryAx` | 0 uses; 3 files *mention* it in comments describing drafts that were rewritten without it |

The `sorry` regex was sanity-checked against a synthetic `:= by sorry` file before the sweep, so
the zero is a measured zero, not a broken pattern. The commonly quoted "46 `sorry` hits in Stacks"
are prose: 11 files contain the word, all in docstrings discussing sorry-freeness (e.g.
"a hypothesis set can be free of `sorry`"; "Two restatement routes avoiding that `sorry` exist").

## 5. What would change this verdict

* A completed build of `WeilIIWeightBound` or `DeligneWeilConjecture`, then the same three
  `#print axioms` lines. Nothing in this report forecloses that; the verdict for those two is
  **PENDING**, not clean and not dirty.
* Any `sorry`/`axiom`/`native_decide` that lands in the tree *after* this sweep. The scan is a
  point-in-time measurement of a tree that is being edited; the `#print axioms` gate is not.
* Statement-level fidelity: axiom-clean says the kernel checked the proofs of *these* statements.
  It does not say `IsCharpolyPureOfWeight`, `HasDeligneConclusions` or
  `rationalGeometricCompactlySupportedCohomology` say what a human means by purity / Weil II /
  compact support. That remains a human read (the CONTENT_AUDIT caveat, unchanged).

## 6. Files

`gate_a.lean`, `gate_b.lean` (this directory); `kloosterman-sheaf/gate_trace.lean` (the packaging's
own receipts, all `[propext, Classical.choice, Quot.sound]`);
`kloosterman-sheaf/closure_size.py`, `closure_sorry_scan.py` (the measuring instruments).
