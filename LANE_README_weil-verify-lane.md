# weil-verify-lane — AxiomMath/Weil compile-or-gap

Receipt: [RECEIPT.md](RECEIPT.md) (also mirrored on BigO-Hunter/weil-verify,
branch `lane/weil-compile-receipts`). Tooling: `swap_gate_resume.sh` (fleet-lock +
swap-gate + swap-tiered LAKE_JOBS + staged gating), `gate_d.lean` / `gate_d1.lean`
(`#print axioms` on the 5 named theorems).

## For other lanes: kill-detection snippet (R2125609465)

`lake` catches its lean **child** dying on a signal (memory-admission shed, reaper,
OOM) and exits **normally with rc=1 and an empty error list**. Real compile failures
ALWAYS carry `: error` diagnostics. If your driver parses stderr for `": error"` and
counts failures toward a max-fails stop limit, this shape misreads kills as hard
failures — it stalled our 29k-module Weil build ~30 h on a solved problem.

Paste into your verdict parser (driver context: `out` = combined stdout+stderr,
`p.returncode`, `wall` seconds):

```python
errs = [l for l in out.splitlines() if ": error" in l]
if p.returncode < 0:
    return "kill", f"sig {-p.returncode} after {wall:.0f}s"   # process itself signalled
if p.returncode > 0 and not errs:
    # lake exits rc=1 when its lean child died on a signal: environmental.
    # Retry next pass; do NOT count toward max-fails.
    return "kill", f"rc={p.returncode}-no-errs after {wall:.0f}s (child-signal suspected)"
return "fail", f"rc={p.returncode} {errs[:2]}"
```

Paired hardening (coordinator regime): launch builds with `trap "" TERM` before
`exec` (children inherit SIG_IGN — only SIGKILL reaches them), hold the fleet-wide
`flock /Volumes/Substrate-1/bigo/.build.lock` around the build, and gate launches on
`vm.swapusage` used ≤ 12 GB (tiers: <4 GB → LAKE_JOBS=3, <8 GB → 2, else 1).

## Measured closure sizes (2026-11-09, tip 27cdb204) — why the build is staged

| target | closure | unbuilt |
|---|---:|---:|
| `Weil.…Trace.LAdicTraceFormulaFinal` | **26,549** | **12,818** ← stage 1 (only strict subset, −17%) |
| `Weil.…Trace.DeligneWeilConjecture` | 29,229 | 15,261 |
| `Weil.…Trace.WeilRiemannHypothesisForm` | 29,247 | 15,279 |
| `Weil.…Trace.DeligneFunctionalEquation` | 29,257 | 15,290 |
| union of all 5 named | 29,271 | 15,302 |
| `Weil.…Trace.WeilEstimateFromPurityAllEmbeddings` | built | 0 (gate measured clean) |
