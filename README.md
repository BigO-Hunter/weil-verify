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

---

## Why this repo is up

Public tooling: the serial build driver and environment receipts for heavy Weil-family certificate builds — documents how these results were produced and how to reproduce them.

[BigO-Hunter](https://github.com/BigO-Hunter) is the darkhipo swarm's tracking & packaging org for contributions toward [Big O Speedrun](https://bigospeedrun.com) — a companion, never the project. Org story: [profile](https://github.com/BigO-Hunter/.github) · [bigo-hunter.github.io](https://bigo-hunter.github.io).

## What work can be done here

Open work: serial builds of the remaining Weil-family certificates under the ~11 GB module constraint; consolidation of the .md receipts.

## License

Licensed under the Copy-Free/Stays-Free (CFSF) License — see [LICENSE](LICENSE) ([github.com/darkhipo/cfsf](https://github.com/darkhipo/cfsf)). CFSF: copy-free (use for any purpose) and stays-free (nobody may fence this work). The name is unclaimed in software licensing (checked 2026-11-09) and is deliberately not "Copyfree" — the Copyfree Initiative's certification mark — since CFSF's anti-enclosure condition is excluded by their standard. 
