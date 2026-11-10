# RECEIPT — AxiomMath/Weil compile-or-gap (lane `weil-verify-lane`)

**Status: PARTIAL — build resumed under fleet admission control; no gap found; no full-compile verdict yet.**
Everything below is measured on this host unless attributed otherwise. The work under test is
**AxiomMath's** (github.com/AxiomMath/Weil, Apache-2.0); this receipt only reports what was
verified here and credits their formalization. Companion lane: BigO-Hunter/weil-verify (org).

## 1. Claim under test

github.com/AxiomMath/Weil — "A Lean 4 formalization of the proof of the Weil conjectures",
README claims zero `sorry`/`admit`/`axiom` anywhere, all four Weil conjectures proved,
following Freitag–Kiehl 1988 on Mathlib + AxiomMath/Stacks.

## 2. Space + pins (measured 2026-11-09 17:55–18:10 PST)

| item | value |
|---|---|
| volume | /Volumes/Substrate-1: 3.6 Ti, **372 Gi free** (91% used) — sufficient |
| repo tip (default branch `main`) | `27cdb2049be62ee2911429b47f54774078450e32` (2026-11-05 18:48 -0800, "One library: WeilFrontier renamed to Weil") |
| verified against | `git ls-remote` HEAD == refs/heads/main == local checkout SHA (byte-exact tip) |
| lean-toolchain | `leanprover/lean4:v4.34.0-rc2` (their `lean-toolchain`, matches README claim) |
| Mathlib pin | `16edf57de7933555826307a3d81b4391a3657a09` (lake-manifest) |
| Stacks pin | AxiomMath/Stacks `012108f61d7f92a6ffc35ec3f263b6da5d438125` |
| build locus | `~/bigo-campaign/weil-verify/Weil` (org lane's tree, at tip, clean) — extended, not duplicated |
| lane dir | `/Volumes/Substrate-1/bigo/weil-verify-lane` (this receipt, gate logs, relaunch tooling) |

## 3. Build state (census, 2026-11-09 18:06 PST; staged schedule 18:20)

Union import closure of the 7 gate targets (org lane's 4 + this lane's 3 named-theorem files):
**29,230 modules** (local, incl. Mathlib). Oleans present:

| package | oleans | note |
|---|---:|---|
| Mathlib | 8,471 | from Mathlib cache |
| Stacks (StacksFrontier) | 5,189 | compiled here, ~121–153/h serial |
| Weil (repo itself) | 4 | incl. `Trace.WeilEstimateFromPurityAllEmbeddings`, `Trace.FrobeniusPoincarePairing` |
| other deps (batteries/aesop/…) | 6 | cached |
| **total** | **13,670 / 29,230 (46.8%)** | 15,276 remain per driver ledger |

**Staged schedule (coordinator opt #1, measured)**: per-target closures are `LAdicTraceFormulaFinal`
**26,549 / 12,818 unbuilt — the only strict subset (−17%)**; `DeligneWeilConjecture` 29,229/15,261,
`WeilRiemannHypothesisForm` 29,247/15,279, `DeligneFunctionalEquation` 29,257/15,290 (all ≈ the
union — they sit on the shared étale core). So: **stage 1** builds only the LAdicTraceFormulaFinal
closure and gates it immediately (first verdict-grade measurement ~16–20 h earlier than the union);
**stage 2** builds the union delta and gates the rest. Stacks still has **no cache service**
(README: "planned", re-checked 2026-11-09) — local compile is the only path.

Named-theorem module status: `WeilEstimateFromPurityAllEmbeddings` **built** (olean present);
`DeligneWeilConjecture`, `DeligneFunctionalEquation`, `LAdicTraceFormulaFinal`,
`WeilRiemannHypothesisForm` **not built yet** — pending the shared étale-cohomology closure.

History: the org lane's serial build ran 11-07 → 11-08 11:23 (3,431 modules, 181 kills absorbed),
then stopped on 8 "hard failures". This lane found those were **SIGTERM kills misclassified as
compile failures** (all `rc=1` with empty Lean-error lists; `RegularSubring` rebuilt clean in 11 s
on 11-09). Stalled ~30 h on a solved problem. Relaunches 11-09 17:58 and (pending) via
`swap_gate_resume.sh` lost children to the same external SIGTERM reaper (~90 s cadence, see §5).

## 4. Audit state

**Source-level scans (this lane, 2026-11-09, at tip):**

| tree | scan | result |
|---|---|---|
| Weil/ (979 .lean files) | `\b(sorry\|sorryAx\|admit)\b` | 10 hits, **all English prose in docstrings** ("admit a sheafification"…); 0 code-level |
| Weil/ | `^\s*(axiom\|opaque)` | 1 hit, docstring prose; **0 real declarations** |
| Weil/ | `native_decide`, `implemented_by`, `unsafe def/lemma/theorem/instance` | **0** |
| StacksFrontier (62,527 .lean files) | `\b(sorry\|sorryAx)\b` | 46 hits, all docstring prose discussing sorry-freedom; **0** bare-tactic lines, **0** code-position hits |
| StacksFrontier | `^\s*(axiom\|opaque)\s+ident` | 52 hits, **all wrapped docstring prose**; 0 real declarations |

**`#print axioms` (decisive instrument) — measured:**

- `WeilEstimateFromPurityAllEmbeddings` gate (org lane AXIOM_GATE.md, 2026-11-07, same SHA,
  olean still present): `Stacks.EtaleCohomology.isAlgebraic_and_norm_eq_of_forall_isCharpolyPureOfWeight`,
  `…isWeilNumber_of_forall_isCharpolyPureOfWeight`, `…isWeilNumber_of_isCharpolyPureOfWeight_comp`
  → **`[propext, Classical.choice, Quot.sound]` — clean, no `sorryAx`**. Also gate (b′) five
  Stacks-side `IsWeilNumber`/duality theorems: same three axioms, clean.
- The four remaining named theorems: **PENDING — no olean exists**; `#print axioms` has nothing to
  read until the closure build passes them. PENDING is not a pass: it is a measurement that has
  not happened yet.

An actual `axiom` declaration anywhere in an import cone would appear in every downstream
`#print axioms`, so the completed build + gates will decide the zero-axiom claim for the whole cone.

## 5. Host incidents (why this is slow; both registered as wounds)

0. **Self-inflicted, disclosed**: my first two wound registrations silently failed (required
   `description` parameter missing; my output truncation hid the error). Re-issued correctly —
   lesson recorded so the next mind greps the full tool result, not a `head`.
1. **SIGTERM reaper on lake builds** — kills at 41 s/92 s/90 s/186 s into each fresh `lake`
   (11-09 17:59–18:05), matching the org lane's 11-07 "unattributed SIGTERMs". Kill-ledger
   correlation: `guards_dispatch`-family guards spawn within seconds of each kill window;
   leading suspect `com.multiaim.memory-admission` ("refuse optional Lean compute under memory
   pressure", 60 s cadence) under 94% swap. Sender not yet pinned to a line of code. → register
   **R2125609466**.
2. **Driver verdict misclassification** — SIGTERM'd lean exits rc=1 with empty error list; the
   driver counted those as hard FAILs toward its stop-at-8 limit (caused the 11-08 stall). →
   register **R2125609465**. Countermeasure applied per coordinator rules: relaunch wrapped in
   `trap "" TERM` (lake inherits SIG_IGN; only SIGKILL reaches it), fleet-wide `flock` on
   `/Volumes/Substrate-1/bigo/.build.lock`, `LAKE_JOBS=1`, swap gate (no launch > 12 GB used),
   `.trace`-bust sweep after kills (0 orphans found — the olean ledger stayed consistent).

## 6. Files / push status

- This receipt: `/Volumes/Substrate-1/bigo/weil-verify-lane/RECEIPT.md` (committed `02f385a`, lane git)
- Gate file for the five named theorems: `gate_d.lean` (lane dir + `~/bigo-campaign/weil-verify/gate_d.lean`)
  — exact full names: `Weil.satisfiesWeilEstimate`,
  `Weil.prod_aeval_inv_rationalFrobeniusCharpolyReverse_zpow_eq`,
  `Weil.zetaFunction_eq_prod_rationalFrobeniusCharpolyReverse`,
  `Weil.exists_zetaSeries_mul_prod_even_eq_prod_odd`,
  `Stacks.EtaleCohomology.isAlgebraic_and_norm_eq_of_forall_isCharpolyPureOfWeight`.
- Gate/relaunch receipts: `swap_gate.log`, `swap_gate_resume.sh`, `driver_launch.log` (same dir)
- Org lane: cloned at `/Volumes/Substrate-1/bigo/weil-verify-lane/org-lane` (BigO-Hunter/weil-verify) —
  extended via driver entries; no org-lane files modified on main.
- **Pushed**: branch `lane/weil-compile-receipts` → BigO-Hunter/weil-verify @ `14900f59`
  (receipt copy `LANE_RECEIPT_weil-verify-lane.md` + README note, PARTIAL status). main untouched.

## 7. Single next action

`swap_gate_resume.sh` v2 is armed and self-sufficient: when swap ≤ 12 GB it takes the fleet lock,
builds **stage 1** (`LAdicTraceFormulaFinal` closure, LAKE_JOBS tiered by swap headroom: <4 GB → 3,
<8 GB → 2, else 1), runs `gate_d1.lean` on completion, then **stage 2** (full union) and
`gate_d.lean`; all gate output lands in `gate_d_results.log`. Watch `swap_gate.log` for stage
transitions; append gate results here as they land. Final verdict (verified-receipt vs gap) is
written only when the gates are measured or a hard blocker is proven — no rounding up in either
direction.
