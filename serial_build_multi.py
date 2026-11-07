#!/usr/bin/env python3
"""Package-aware, batched, kill-absorbing serial Lean builder.

Descends from ~/bigo-campaign/scripts/serial_build.py (Catalan lane, 0 kills
absorbed vs 40 dead attempts) with two fixes this tree needs:

1. MULTI-ROOT RESOLUTION. Modules of a dependency package live under
   <root>/.lake/packages/<pkg>/, and their oleans build into that package's
   .lake/build/lib/lean. The single-root original treats `StacksFrontier.*`
   as unknown-and-skip, so it would report "closure complete" having built
   only the root package's own modules.
2. BATCHING. `lake build` costs ~12 s of plan/setup per invocation on this
   host; 19.3k modules one-at-a-time = ~64 h of pure overhead. Builds a
   topo-ordered chunk per invocation, then isolates failures individually.
   Oleans remain the ledger, so a kill resumes at the next unbuilt module.

Exit 0 = closure complete, 3 = budget exhausted (resumable), 1 = hard failures.

Usage: serial_build_multi.py --root Weil --entry Mod [--entry ...]
         [--budget-s N] [--chunk 24] [--log F] [--state F]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path

IMPORT_RE = re.compile(r"^\s*(?:public\s+|private\s+)?import\s+([A-Za-z0-9_.']+)", re.M)


class Tree:
    def __init__(self, root: Path):
        self.root = root
        pkgs = root / ".lake/packages"
        self.roots = [root] + ([p for p in sorted(pkgs.iterdir()) if p.is_dir()] if pkgs.is_dir() else [])
        self.cache: dict[str, tuple[Path, Path] | None] = {}

    def resolve(self, mod: str) -> tuple[Path, Path] | None:
        """-> (source, olean) or None for foreign/unknown modules."""
        if mod in self.cache:
            return self.cache[mod]
        rel_s = mod.replace(".", "/") + ".lean"
        rel_o = mod.replace(".", "/") + ".olean"
        res = None
        for pkg in self.roots:
            src = pkg / rel_s
            if src.is_file():
                res = (src, pkg / ".lake/build/lib/lean" / rel_o)
                break
        self.cache[mod] = res
        return res

    def imports(self, src: Path) -> list[str]:
        try:
            return IMPORT_RE.findall(src.read_text(errors="replace"))
        except OSError:
            return []


def closure(tree: Tree, entries: list[str]):
    edges: dict[str, list[str]] = {}
    seen: dict[str, tuple[Path, Path]] = {}
    unknown: set[str] = set()
    stack = list(entries)
    while stack:
        m = stack.pop()
        if m in seen or m in edges:
            continue
        r = tree.resolve(m)
        if r is None:
            unknown.add(m)
            continue
        seen[m] = r
        imps = tree.imports(r[0])
        edges[m] = imps
        stack.extend(imps)
    return seen, edges, unknown


def topo(todo: set[str], edges: dict[str, list[str]]) -> list[str]:
    order: list[str] = []
    state: dict[str, int] = {}

    def visit(m: str):
        s = state.get(m)
        if s == 2:
            return
        if s == 1:  # cyclic import (shouldn't happen in Lean)
            return
        state[m] = 1
        for dep in edges.get(m, ()):
            if dep in todo:
                visit(dep)
        state[m] = 2
        order.append(m)

    for m in sorted(todo):
        visit(m)
    return order


def run_lake(root: Path, mods: list[str], env: dict, timeout_s: int) -> tuple[str, str]:
    """-> (verdict, detail) with verdict in {ok, fail, kill, timeout}."""
    t0 = time.time()
    p = None
    try:
        p = subprocess.Popen(
            ["lake", "build", *mods],
            cwd=root,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            start_new_session=True,
        )
        out, _ = p.communicate(timeout=timeout_s)
    except subprocess.TimeoutExpired:
        if p is not None:
            try:
                os.killpg(os.getpgid(p.pid), signal.SIGKILL)
            except OSError:
                pass
        return "timeout", f"{time.time() - t0:.0f}s"
    wall = time.time() - t0
    if p.returncode == 0:
        return "ok", f"{wall:.0f}s"
    errs = [line for line in out.splitlines() if ": error" in line]
    if p.returncode < 0:
        return "kill", f"sig {-p.returncode} after {wall:.0f}s"
    return "fail", f"rc={p.returncode} {errs[:2]}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--entry", action="append", required=True)
    ap.add_argument("--budget-s", type=int, default=6 * 24 * 3600)
    ap.add_argument("--chunk", type=int, default=24)
    ap.add_argument("--timeout-s", type=int, default=5400, help="per-chunk cap")
    ap.add_argument("--max-fails", type=int, default=8)
    ap.add_argument("--log", default=None)
    ap.add_argument("--state", default=None)
    args = ap.parse_args()

    root = Path(args.root).resolve()
    tree = Tree(root)
    logf = open(args.log, "a") if args.log else None
    state_path = Path(args.state) if args.state else None

    def log(msg: str):
        line = f"[{time.strftime('%m-%d %H:%M:%S')}] {msg}"
        print(line, flush=True)
        if logf:
            logf.write(line + "\n")
            logf.flush()

    def save_state(**kw):
        if not state_path:
            return
        try:
            cur = json.loads(state_path.read_text())
        except (OSError, ValueError):
            cur = {}
        cur.update(kw)
        cur["updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        state_path.write_text(json.dumps(cur, indent=1))

    env = {**os.environ, "LEAN_NUM_THREADS": "1", "LAKE_JOBS": "1"}
    t_start = time.time()
    t_end = t_start + args.budget_s
    seen, edges, unknown = closure(tree, args.entry)
    if unknown:
        log(f"WARNING unresolved (assumed foreign): {sorted(unknown)[:5]}")
    local = {m: r for m, r in seen.items()}
    todo = {m for m, r in local.items() if not r[1].exists()}
    log(f"closure={len(seen)} unbuilt={len(todo)} entries={args.entry}")
    save_state(total_closure=len(seen), unbuilt_start=len(todo), started=time.strftime("%Y-%m-%dT%H:%M:%S"))
    if not todo:
        log("NOTHING TO BUILD — closure complete")
        return 0

    order = topo(todo, edges)
    log(f"topo order ready ({len(order)} modules), chunk={args.chunk}")

    built = kills = fails = done_from_chunk = 0
    failed: list[str] = []
    # Pass loop: a kill leaves its module unbuilt, so one pass can exit short of
    # the closure. Repeat until nothing is left, or a full pass builds nothing
    # (kills are not resolving) — never exit 3 on a merely-interrupted module.
    while True:
        remaining_list = [m for m in order if not tree.resolve(m)[1].exists()]
        if not remaining_list:
            log(f"NOTHING REMAINING — closure complete (built={built} kills={kills} fails={fails})")
            save_state(built=built, kills=kills, fails=fails, remaining=0, failed=failed)
            return 0
        log(f"pass start: {len(remaining_list)} remaining")
        built_before_pass = built
        i = 0
        order = remaining_list
        while i < len(order):
            if time.time() > t_end:
                log(f"BUDGET reached at {i}/{len(order)} — resumable")
                save_state(built=built, kills=kills, fails=fails, remaining=len(order) - i)
                return 3
            chunk = order[i : i + args.chunk]
            pending = [m for m in chunk if not tree.resolve(m)[1].exists()]
            if not pending:
                i += len(chunk)
                continue
            verdict, detail = run_lake(root, pending, env, args.timeout_s)
            if verdict == "ok":
                built += len(pending)
                i += len(chunk)
                done_from_chunk += len(pending)
                elapsed_h = (time.time() - t_start) / 3600 or 1e-9
                rate = done_from_chunk / elapsed_h
                eta_h = (len(order) - i) / rate if rate > 0 else float("inf")
                log(f"[{i}/{len(order)}] ok {len(pending)} mods ({detail}) rate={rate:.0f}/h ETA={eta_h/24:.1f}d")
                save_state(built=built, kills=kills, fails=fails, cursor=i, remaining=len(order) - i,
                           rate_per_hour=round(rate, 1), eta_days=round(eta_h / 24, 2),
                           last_batch=pending[-1])
                continue
            # batch failed or was killed: isolate per module so a kill costs at most one module
            log(f"[{i}] batch {verdict} ({detail}) — isolating {len(pending)} modules")
            for mod in pending:
                if time.time() > t_end:
                    save_state(built=built, kills=kills, fails=fails, remaining=len(order) - i)
                    return 3
                if tree.resolve(mod)[1].exists():
                    continue
                v, d = run_lake(root, [mod], env, args.timeout_s)
                if v == "ok":
                    built += 1
                    done_from_chunk += 1
                    log(f"  ok {mod} ({d})")
                elif v in ("kill", "timeout"):
                    kills += 1
                    log(f"  {v.upper()} {mod} ({d}) — will retry next pass")
                else:
                    fails += 1
                    failed.append(mod)
                    log(f"  FAIL {mod} ({d})")
                    if fails >= args.max_fails:
                        log(f"{args.max_fails} hard failures — stopping for inspection: {failed}")
                        save_state(built=built, kills=kills, fails=fails, failed=failed)
                        return 1
            i += len(chunk)
        if built == built_before_pass:
            log(f"pass made no progress ({kills} kills so far) — stopping, resumable")
            save_state(built=built, kills=kills, fails=fails, remaining=len(order), failed=failed)
            return 3


if __name__ == "__main__":
    sys.exit(main())
