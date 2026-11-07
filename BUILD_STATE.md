# BUILD_STATE — weightBound / satisfiesWeilEstimate / LaumonFourier purity

Live state of the axiom-gate build. Numbers below are measured, not estimated;
each is stamped with the time it was taken.

## Current status (2026-11-07 12:52 relaunch)

| item | value |
|---|---|
| builder | `~/bigo-campaign/scripts/serial_build_multi.py` (pid 298, detached, `caffeinate -i nice -n 10`) |
| entries | `Trace.LaumonFourierLineAwayFibreOffTop`, `Trace.WeilIIWeightBound`, `FourierDeligne.LaumonFourierLineAbsIrrInputProof`, `Weil…Trace.DeligneWeilConjecture` |
| union closure | **29,230 modules** (local, incl. Mathlib) |
| unbuilt at relaunch | **19,356** (19,383 at first launch; 27 built in the first 12 min) |
| built (Stacks oleans) | 1,098 at 12:55 → rising at ~120/h (from 1,042 at 12:11) |
| budget | 600,000 s ≈ 6.9 days, resumable |
| log | `build_serial.log` (append-only) |
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

## Host pressure: the governor that decides the ETA (measured, not inferred)

The real wall on this host is not Lean and not the tree — it is
**`multiaim_agents.daemons.lean_build_governor`**, running in `enforce` mode with a
**host-wide** aggregate ceiling, not a per-tree one:

| knob | value |
|---|---|
| `LEAN_TREE_MAX_RSS_MB` (all lean processes, every lane) | 24,576 |
| `LEAN_MAX_RSS_MB` (per process) | 12,288 |
| policy | SIGSTOP (freeze) → thaw on relief, or KILL if still over ceiling ~300 s later **and** the host is dying |

Observed against this lane's children (from `~/.multiaim/logs/com.multiaim.lean-build-governor.log`):

* `FROZE … pid 43969 … weil-verify/Weil/.lake/packages/Stacks/…` then
  `THAWED … after 80 s frozen` — our module was paused mid-compile and resumed.
* `FROZE … pid 13708 … weil-verify/…` — same, again. Freezes are absorbed: the
  builder waits in `communicate()`, and `--timeout-s 5400` tolerates a 300 s freeze.
* **No `KILLED` line names a weil-verify pid.** Every kill in the log belongs to
  another lane (the 13 GB `CLZCert` module).
* **Unattributed SIGTERMs** hit two chunks (12:42:24, 139 s in; 12:52:53, 51 s in),
  with zero Lean errors in the log. Not the governor: that daemon uses only
  SIGSTOP/SIGCONT/SIGKILL, never SIGTERM (verified in
  `daemons/lean_build_governor.py`), and no ledger entry names our pids. Both
  landed 1–2 min after a detached launch, suggesting an external reaper reacting
  to new lean processes; unresolved. The builder isolated each to per-module
  builds and rebuilt every module with **0 net oleans lost** — the kill-absorbing
  property exercised for real, twice, not just claimed. Cost is one in-flight
  compile per kill, i.e. ≤ one module of work, and progress continued through it
  (1,084 → 1,098 oleans across the two).

Consequence for planning: the ETA is contingent on peer lanes' Lean footprint.
Raising `LEAN_TREE_MAX_RSS_MB` here is deliberately **not** done — swap is at
~99 % of 39.9 GB and the governor's ceiling exists precisely to stop this host
dying. Our lane stays small (one module in flight, `LAKE_JOBS=1`).

## Rate and ETA

Measured this session on the cheap foundational layers (chunked, 4 modules per
invocation): **269/h** over the first chunk, **130/h** on the second as module
weight rose. The historical long-window figure for this tree — the one to plan
with — is **121 oleans/hour**:

> 19,356 unbuilt ÷ 121/h ≈ 160 h ≈ **6.7 days** of continuous single-job building.

Early-phase logs are the optimistic tail of that curve (foundational modules run
20–45 s each); the étale-cohomology core is minutes per module. Treat 6.7 days as
the central estimate, ± the host's contention.

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
4. **My own first draft exited after a single pass** — caught at arm-up, before the
   long run: a SIGTERM during the first chunk showed that a kill leaves its module
   unbuilt, and a one-pass loop then exits `3` with that module abandoned; nobody
   restarts an unattended 7-day job. Passes now repeat until the closure is empty,
   or until a full pass builds nothing (kills genuinely not resolving).

## What "done" looks like

`build_state.json` reaches `remaining: 0`, then:

```bash
cd ~/bigo-campaign/weil-verify/Weil
LAKE_JOBS=1 LEAN_NUM_THREADS=1 lake env lean ../gate_c.lean   # see AXIOM_GATE_PART2.md
```
