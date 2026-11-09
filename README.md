# weil-verify

Serial Lean build driver and verification artifacts for the Weil-family certificate work.

## Host constraint (read this before filing a slowness bug)

`serial_build_multi.py` is serial **internally** (`LAKE_JOBS=1`) because a heavy module peaks near
11 GB RSS. Nothing coordinates *separate drivers* against each other here, so N drivers means N
concurrent `lake` processes.

When run inside the MultiAgency body, the driver optionally takes a host-wide slot from
`multiaim_agents.daemons.lean_concurrency.lean_slot`:

```python
try:
    from multiaim_agents.daemons.lean_concurrency import lean_slot as _lean_slot
except Exception:                       # limiter unavailable: build unbounded rather than not at all
    from contextlib import nullcontext as _lean_slot
```

That import is **deliberately optional and fail-open**: outside the body the driver runs exactly as
written, with no throttle and no dependency. If builds here are slow or the machine swaps, that is
the missing throttle, not a bug in this repo — pace your drivers yourself (or add your own limiter).

`BUILD_STATE.md` and the other `.md` files are receipts from the environment these results were
produced in; they reference body-side paths (`~/.multiaim/...`) for provenance, not as requirements.
