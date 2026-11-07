# BUILD_STATE — weightBound / satisfiesWeilEstimate / LaumonFourier purity

Live state of the axiom-gate build. Numbers below are measured, not estimated;
each is stamped with the time it was taken.

## Current status (2026-11-07 12:40 launch)

| item | value |
|---|---|
| builder | `~/bigo-campaign/scripts/serial_build_multi.py` (pid 3727, detached, `caffeinate -i nice -n 10`) |
| entries | `Trace.LaumonFourierLineAwayFibreOffTop`, `Trace.WeilIIWeightBound`, `FourierDeligne.LaumonFourierLineAbsIrrInputProof`, `Weil…Trace.DeligneWeilConjecture` |
| union closure | **29,230 modules** (local, incl. Mathlib) |
| unbuilt at launch | **19,383** |
| built (Stacks oleans) | 1,071 at 12:45 (from 1,042 at 12:11) |
| budget | 600,000 s ≈ 6.9 days, resumable |
| log | `build_serial.log` (append-only, one line per chunk) |
| state | `build_state.json` (cursor, built, rate/h, ETA days) |

Per-target unbuilt counts at 12:22 (my own closure walk, `closure_analyze.py`,
which agrees with `kloosterman-sheaf/closure_size.py` to within the 4 modules
built since that report):

| target | closure | unbuilt | source MB |
|---|---:|---:|---:|
| `Stacks…LAdicSheaf.weightBound` | 29,128 | **19,310** | 320.0 |
| `Weil.satisfiesWeilEstimate` | 29,229 | 19,424 → 19,383 measured union-side | — |
| `LaumonFourierLineAwayFibreOffTop` | 26,705 | **16,887** | 282.9 |
| `laumonFourierLineAbsIrrInputProof` | 27,964 | 18,146 | 300.9 |

The mass is the étale-cohomology core, not one prunable aggregator: top unbuilt
prefixes are `…EtaleCohomology` (2,492), `…AG.Spaces` (1,688),
`…CategoryTheory.Sites` (1,254), `…AG.Chow` (783). The cheapest target
(LaumonFourier purity, 16,887) is a sub-closure of `weightBound`, so a single
union build in topological order certifies the gate targets one at a time as it
passes them — no reordering needed.

## Resume / operate

```bash
# resume after a kill, reboot, or budget exhaustion (idempotent: oleans are the ledger)
cd ~/bigo-campaign/weil-verify
python3 - <<'PY'
import subprocess
subprocess.Popen(["caffeinate","-i","nice","-n","10","python3",
 "/Users/dmitri.arkhipov/bigo-campaign/scripts/serial_build_multi.py","--root","Weil",
 "--entry","StacksFrontier.AlgebraicGeometry.EtaleCohomology.Trace.LaumonFourierLineAwayFibreOffTop",
 "--entry","StacksFrontier.AlgebraicGeometry.EtaleCohomology.Trace.WeilIIWeightBound",
 "--entry","StacksFrontier.AlgebraicGeometry.EtaleCohomology.FourierDeligne.LaumonFourierLineAbsIrrInputProof",
 "--entry","Weil.AlgebraicGeometry.EtaleCohomology.Trace.DeligneWeilConjecture",
 "--budget-s","600000","--chunk","24","--timeout-s","5400",
 "--log","build_serial.log","--state","build_state.json"],
 start_new_session=True)
PY
```

Check progress: `tail -3 build_serial.log` and
`find Weil/.lake/packages/Stacks/.lake/build/lib/lean -name '*.olean' | wc -l`.

## Rate and ETA

Measured on this host under its current load (load avg ~270 on 16 cores, swap
39.7/39.9 GB used). Early modules are cheap (8 modules / 43 s ⇒ 520/h; 8 / 102 s
⇒ 366/h); the historical long-window figure for the same tree is **121
oleans/hour**, which is the number to plan with because it was taken across
mixed heavy modules:

> 19,383 unbuilt ÷ 121/h ≈ 160 h ≈ **6.7 days** of continuous single-job building.

That figure moves only with host contention, which this lane does not control
(five unrelated Lean builds were running at launch). The builder is memory-frugal
by construction: one module in flight, `LAKE_JOBS=1`, `LEAN_NUM_THREADS=1`.

## Defects found in the tooling (recorded here because this repo is the lane's register)

1. **`scripts/serial_build.py` is package-blind and fails *silently* on this tree.**
   `module_file()` searches only `root/` and `root/Submission/`, and `olean_path()`
   assumes all oleans land in `root/.lake/build/lib/lean`. In the Weil tree every
   gate-target dependency lives in `.lake/packages/Stacks/`. Result: `StacksFrontier.*`
   is treated as unknown-foreign, excluded from `todo`, and the script prints
   **"NOTHING TO BUILD — closure complete"** having built only the 31 Weil-local
   modules. A caller would read exit 0 as certification. Fixed in
   `serial_build_multi.py` (multi-root resolve + per-package olean paths);
   the original is left untouched because the Catalan lane still uses it.
2. **`lake build` costs ~12 s of plan/setup per invocation here** (measured:
   18.6 s wall for a 6.0 s compile). One-module-per-invocation × 19,383 ≈ 64 h
   of pure overhead, ~40 % of the total wall clock. Hence chunked invocations.
3. **`setsid` does not exist on macOS.** A launch wrapper written for Linux
   (`setsid nohup …`) exits immediately with no log file and no error visible to
   the caller. Detach with `subprocess.Popen(..., start_new_session=True)`.

## What "done" looks like

`build_state.json` reaches `remaining: 0`, then:

```bash
cd ~/bigo-campaign/weil-verify/Weil
LAKE_JOBS=1 LEAN_NUM_THREADS=1 lake env lean ../gate_c.lean   # see AXIOM_GATE_PART2.md
```
