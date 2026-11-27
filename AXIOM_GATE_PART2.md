# AXIOM_GATE_PART2 — the three build-blocked targets

Companion to `AXIOM_GATE.md`. That report certified gate (a′) and (b′) from
existing oleans and left `weightBound`, `satisfiesWeilEstimate` and the
`LaumonFourier*` purity conclusions **PENDING on build**. This file is the
instrument for that pending measurement, and states the verdict exactly as far
as it can honestly be stated today.

## Verdict (2026-11-07 13:0x)

| target | declaration | axiom verdict |
|---|---|---|
| Weil II weight bound (Tag 03VH) | `Stacks.EtaleCohomology.LAdicSheaf.weightBound` | **PENDING — no olean** |
| Deligne's theorem | `Weil.satisfiesWeilEstimate` | **PENDING — no olean** |
| LaumonFourier purity | `Stacks.EtaleCohomology.laumonFourierLineAbsIrrInput'`, `…isLisse_laumonFourierFamilySheaf`, `…laumonFourierLineAwayFibreVanishing_of_top` | **PENDING — no olean** |

PENDING is not a hedge and not a soft clean. `#print axioms` reads the compiled
proof term; without the olean there is nothing to read. What the *source* says
is already measured and reported in `AXIOM_GATE.md` §4 — 0 code-level `sorry`,
0 `axiom`, 0 `native_decide`, 0 `implemented_by`/`unsafe def` across 63k Stacks
files and 980 Weil files — and that sweep is corroborative, not decisive.

## Why it is still pending: the measurement, not the mathematics

The three targets' oleans do not exist because their import closures are
unbuilt. Measured 2026-11-07 12:22 with `closure_analyze.py` (independent of
`closure_size.py`, agreement within the 4 modules built since that report):

| target | closure | unbuilt |
|---|---:|---:|
| `Trace.WeilIIWeightBound` | 29,128 | 19,310 |
| `Weil…Trace.DeligneWeilConjecture` | 29,229 | 19,383 (union figure) |
| `Trace.LaumonFourierLineAwayFibreOffTop` | 26,705 | 16,887 |
| `FourierDeligne.LaumonFourierLineAbsIrrInputProof` | 27,964 | 18,146 |

19,383 unbuilt modules, 320 MB of source, mass concentrated in the étale
cohomology core (`…EtaleCohomology` 2,492, `…AG.Spaces` 1,688,
`…CategoryTheory.Sites` 1,254, `…AG.Chow` 783). No aggregator can be pruned:
these are genuine proof dependencies. There is also **no cache shortcut** —
Stacks' README states a cache service "is planned", so unlike Mathlib (whose
8,471 oleans are cache-distributed) the Stacks oleans must be compiled locally.

At the measured 121 oleans/hour (long window, original host, mixed module weight)
the closure is ~160 h ≈ **6.7 days** of continuous single-job building. On the
original heavily contended verification host, that is a wall of
wall-clock, not of truth: nothing in the tree resists the build, it is simply
large.

## The build that was launched (and did not complete)

A chunked topological build of the union of all four closures was launched detached on
2026-11-07 12:40 (600,000 s budget, resumable at module granularity — oleans are the
ledger; a kill costs at most the module in flight). It did not reach completion before the
verification campaign ended; the oleans it produced lived on the original host and are not
shipped with this repo. A continuer restarts the build with `serial_build_multi.py` (see
README → Reproduce / verify). During that run the builder absorbed two external SIGTERMs
mid-chunk with **zero net oleans lost** (1,084 → 1,098 Stacks oleans across the two kills,
each cost ≤ one in-flight module) — the kill-absorbing property exercised for real, not
just claimed.

Because the LaumonFourier sub-closure (16,887) is contained in `weightBound`'s
(19,310), a single topologically-ordered union build certifies the targets one at
a time as it passes them — purity first, then `weightBound`, then
`satisfiesWeilEstimate`. No reordering, no second pass.

## The measurement to run on completion

```bash
cd Weil   # from this repo's root
LAKE_JOBS=1 LEAN_NUM_THREADS=1 lake env lean ../gate_c.lean
```

`gate_c.lean` prints `#print axioms` for the three targets plus the purity engine
that they all funnel into. Read it with this rule:

* `depends on axioms: [propext, Classical.choice, Quot.sound]` → **CLEAN**
  (stdlib-only; the same three every Mathlib theorem carries).
* anything naming `sorryAx` → **DIRTY**: a `sorry` (or a `sorry`-carrying
  dependency) survives in the closure. The next step is to locate it with
  `#print sorries`/`set_option pp.universes` on the named module, not to re-scan
  the tree by grep.
* any other name (`Lean.ofReduceBool` from `native_decide`, a project `axiom`) →
  **DIRTY**, and the name identifies the exact escape hatch used.

Partial outcomes remain wins and must be reported as such: if the build reaches
only the LaumonFourier sub-closure, gate (c) closes and (a)/(b) stay PENDING; if
it reaches `WeilIIWeightBound`, gate (a) closes.

## Instrument defects found while preparing this run

The single-root `serial_build.py` predecessor is
package-blind and on *this* tree reports "closure complete" without building a
single Stacks module (silent false certification — fixed in
`serial_build_multi.py`); `lake build` overhead is ~12 s/invocation (hence
chunking, ~64 h recovered); `setsid` does not exist on macOS (a Linux-shaped
detached launcher exits immediately and silently — detach with
`subprocess.Popen(..., start_new_session=True)` instead).
