# weil-verify

Independent verification of [AxiomMath/Weil](https://github.com/AxiomMath/Weil) — an
AI-agent-written Lean 4 formalization of the **Weil conjectures** (Freitag–Kiehl route,
~980 modules on Mathlib + the ~63k-file [AxiomMath/Stacks](https://github.com/AxiomMath/Stacks)
dependency). This repo holds the claim-vs-content audit, `#print axioms` gate probes,
package-aware serial build tooling, and the measured receipts.

**Status (measured 2026-11-07):**

| gate | target | verdict |
|---|---|---|
| (a′) | FK IV.4 purity engine `isAlgebraic_and_norm_eq_of_forall_isCharpolyPureOfWeight` (+2 lemmas) | **CLEAN** — `[propext, Classical.choice, Quot.sound]`, no `sorryAx` |
| (b′) | five Stacks-side `IsWeilNumber` / purity lemmas | **CLEAN** — same three stdlib axioms |
| (a) | Weil II weight bound `LAdicSheaf.weightBound` (Tag 03VH) | **PENDING on build** |
| (b) | Deligne's theorem `Weil.satisfiesWeilEstimate` | **PENDING on build** |
| (c) | LaumonFourier purity conclusions | **PENDING on build** |

Static sweep over all 63k Stacks + 980 Weil files: **0** code-level `sorry`, `axiom`,
`native_decide`, `implemented_by`/`unsafe def` (the oft-quoted "46 sorry hits" are docstring
prose). The static sweep corroborates; only `#print axioms` on compiled oleans decides.
The three PENDING targets need ~19.4k more Stacks modules compiled (union closure 29,230
modules; measured throughput 121 oleans/h single-job ⇒ **~6.7 days** of continuous building;
heavy modules peak near 11 GB RSS; Stacks has no olean cache). See
[AXIOM_GATE.md](AXIOM_GATE.md) and [AXIOM_GATE_PART2.md](AXIOM_GATE_PART2.md).

## Board context

This is an **independent verification result, not a [Big O Speedrun](https://bigospeedrun.com)
race**. The Weil conjectures (Deligne's Riemann hypothesis for zeta functions of varieties
over finite fields) are classically proved; what is being verified here is the AI-generated
Lean formalization's axiom hygiene and statement fidelity. Do not confuse it with the
board's *zeta zeros critical line* race (proportion of Riemann-zeta zeros on the critical
line — OPEN; leader H. M. Bui + 2 more, κ* ≥ 0.703703, Nov 20 2026, Claimed) or the
*quasi-Riemann hypothesis* race (CLOSED by Levent Alpöge, θ ≤ 1/2, Nov 20 2026, Lean
Verified). Those are different targets. The Kloosterman-bound instantiation assessed in
[INSTANTIATION.md](INSTANTIATION.md) feeds bounded-prime-gap work (board: H₁ ≤ 182 claimed
by GPT-6 Astra/OpenAI, Sep 6 2026; the swarm's Lean-verified H₁ ≤ 246 lives in
[prime-gaps-246-lean](https://github.com/BigO-Hunter/prime-gaps-246-lean)).

## Contents

| file | what it is |
|---|---|
| [REPO_MAP.md](REPO_MAP.md) | claims-vs-content audit of AxiomMath/Weil at HEAD `27cdb204` (pinned Mathlib `16edf57`, Stacks `012108f`) |
| [CONTENT_AUDIT.md](CONTENT_AUDIT.md) | what the key theorems actually prove, statement by statement |
| [AXIOM_GATE.md](AXIOM_GATE.md) | measured CLEAN verdicts (gates a′/b′) + the build wall blocking the rest |
| [AXIOM_GATE_PART2.md](AXIOM_GATE_PART2.md) | the three PENDING targets, closure measurements, verdict rule |
| [INSTANTIATION.md](INSTANTIATION.md) | can Katz 1988 Thm 4.1.1 / FKM 2013 Prop 2 (Kloosterman bounds) be instantiated from this machinery — gap analysis |
| `gate_a.lean`, `gate_b.lean`, `gate_c.lean` | `#print axioms` probes (a/b measurable now; c needs the closure build) |
| `serial_build_multi.py` | package-aware, batched, kill-absorbing serial Lean builder (oleans are the ledger; resumable) |
| `closure_analyze.py` | import-closure analyzer across all package roots (built/unbuilt counts + shape) |
| `build.sh` | bootstrap driver: deps → Mathlib cache → target build → axiom check |
| `build.log` | receipt of the 2026-11-07 bootstrap build (deps, cache, partial Stacks build) |
| `tests/`, `.github/workflows/ci.yml` | tooling smoke tests + CI |

## Reproduce / verify

Requires [elan](https://github.com/leanprover/lean4-elan) (`lake` on PATH); toolchain
`leanprover/lean4:v4.34.0-rc2` (pinned by Weil's `lean-toolchain`). The Weil checkout is
multi-GB and is **not** shipped here (`.gitignore`d); the original host's oleans are gone,
so a continuer rebuilds from source — the Mathlib cache covers ~8.5k modules, the ~20k
Stacks modules must compile.

```bash
# 1. Get the tree at the audited revisions
git clone https://github.com/AxiomMath/Weil
git -C Weil checkout 27cdb2049be62ee2911429b47f54774078450e32

# 2. Bootstrap (from this repo's root; Weil/ as sibling checkout)
./build.sh "$PWD/Weil"            # deps + Mathlib cache + target attempt + axiom check

# 3. The long closure build — serial internally (LAKE_JOBS=1), resumable at module
#    granularity: a kill costs at most the module in flight. ~6.7 days single-job.
python3 serial_build_multi.py --root Weil \
  --entry StacksFrontier.AlgebraicGeometry.EtaleCohomology.Trace.LaumonFourierLineAwayFibreOffTop \
  --entry StacksFrontier.AlgebraicGeometry.EtaleCohomology.Trace.WeilIIWeightBound \
  --entry StacksFrontier.AlgebraicGeometry.EtaleCohomology.FourierDeligne.LaumonFourierLineAbsIrrInputProof \
  --entry Weil.AlgebraicGeometry.EtaleCohomology.Trace.DeligneWeilConjecture \
  --budget-s 600000 --chunk 24 --timeout-s 5400 \
  --log build_serial.log --state build_state.json

# 4. When build_state.json reaches remaining: 0 — the decisive measurement
cd Weil && LAKE_JOBS=1 LEAN_NUM_THREADS=1 lake env lean ../gate_c.lean
```

Verdict rule for `#print axioms`: `[propext, Classical.choice, Quot.sound]` = **CLEAN**
(the same three every Mathlib theorem carries); `sorryAx` = **DIRTY** (locate with
`#print sorries` on the named module); `Lean.ofReduceBool` or any project axiom =
**DIRTY**, and the name identifies the escape hatch. Partial outcomes are wins: the
LaumonFourier sub-closure (16.9k) sits inside `weightBound`'s (19.3k), so the union build
certifies gate (c) first, then (a), then (b) as it passes them.

Pace concurrent drivers yourself: nothing coordinates separate `serial_build_multi.py`
processes against each other, and N drivers means N concurrent `lake` processes at up to
~11 GB RSS per heavy module.

## Next steps for a continuer

1. **Finish the union build and run `gate_c.lean`** — record CLEAN/DIRTY per target.
   This is the open decisive measurement; everything else in the repo is in service of it.
2. **If CLEAN: statement-level fidelity read.** Axiom-clean says the kernel checked these
   proofs; it does not say `IsCharpolyPureOfWeight`, `HasDeligneConclusions` or the
   compact-support cohomology definitions mean what a human means by purity / Weil II.
   The library is AI-written and not yet human-reviewed (CONTENT_AUDIT caveat).
3. **Kloosterman assembly** (INSTANTIATION.md): package the LaumonFourier line family as
   a lisse rank-≤3 sheaf on G_m, prove stalk trace = Kl_3(a;q), discharge purity at every
   a ∈ G_m(F_q) — then |Kl_3(a;q)| ≤ 3 q^{1/2} falls out of the (already CLEAN) FK IV.4
   engine. Bounded work (weeks–months estimate), not new machinery.
4. **Re-sweep if the tree moves:** the static sorry/axiom scan is point-in-time;
   `closure_analyze.py --root Weil <entries>` re-measures the closure shape.

## CI

CI checks the **tooling** (Python compile, bash syntax, synthetic-tree smoke tests of the
package-aware resolver/closure/topo logic — the defect class that silently false-certified
the single-root predecessor). It does not build the Lean tree: a ~19.4k-module closure at
~11 GB peak RSS per heavy module is days of compute, not a CI job. The decisive Lean
measurement is `gate_c.lean` on a completed build, run by a continuer.

## Disclosure

AI-assisted work, disclosed: the audit, tooling and receipts here were produced by AI
agents; the AxiomMath/Weil library under verification is itself AI-agent-written (per its
README) with human review pending. Every quantitative claim in the receipts is a
measurement stamped with its date, not an estimate presented as fact.

## License

Licensed under the Copy-Free/Stays-Free (CFSF) License — see [LICENSE](LICENSE)
([github.com/darkhipo/cfsf](https://github.com/darkhipo/cfsf)). CFSF: copy-free (use for
any purpose) and stays-free (nobody may fence this work).

Part of [BigO-Hunter](https://github.com/BigO-Hunter) — independent verification and
packaging for [Big O Speedrun](https://bigospeedrun.com) ·
[org profile](https://github.com/BigO-Hunter/.github) ·
[bigo-hunter.github.io](https://bigo-hunter.github.io).
