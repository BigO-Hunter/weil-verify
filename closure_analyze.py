#!/usr/bin/env python3
"""Package-aware import-closure analyzer for a Lean tree with lake packages.

A single-root assumption cannot resolve dependency-package modules (e.g.
StacksFrontier.* lives under .lake/packages/Stacks/, not under the root
package). This walks imports across every package root and reports
built/unbuilt counts + shape.

Usage: closure_analyze.py MOD [MOD...] [--root DIR] [--out FILE] [--hist] [--top N]
  --root  Lean project root (default: ./Weil)
  --out   where to write the unbuilt-module list (default: ./unbuilt_closure.txt)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

IMPORT_RE = re.compile(r"^\s*(?:public\s+|private\s+)?import\s+([A-Za-z0-9_.']+)", re.M)


def package_roots(root: Path) -> list[Path]:
    """Root package + every lake dependency package, in stable order."""
    pkgs = root / ".lake/packages"
    return [root] + ([p for p in sorted(pkgs.iterdir()) if p.is_dir()] if pkgs.is_dir() else [])


def make_resolver(roots: list[Path]):
    """-> resolve(mod) -> (source file, olean path) | None, with memoization.

    Module names carry their lib root (Weil.Foo -> Weil/Weil/Foo.lean,
    StacksFrontier.Foo -> <pkg>/StacksFrontier/Foo.lean), so pkg/rel resolves all.
    """
    cache: dict[str, tuple[Path, Path] | None] = {}

    def resolve(mod: str) -> tuple[Path, Path] | None:
        if mod in cache:
            return cache[mod]
        rel = mod.replace(".", "/") + ".lean"
        orl = mod.replace(".", "/") + ".olean"
        res = None
        for pkg in roots:
            src = pkg / rel
            if src.is_file():
                res = (src, pkg / ".lake/build/lib/lean" / orl)
                break
        cache[mod] = res
        return res

    return resolve


def walk_closure(resolve, entries: list[str]):
    """-> (seen: mod->source, edges: mod->imports) across all package roots."""
    seen: dict[str, Path] = {}
    edges: dict[str, list[str]] = {}
    stack = list(entries)
    while stack:
        m = stack.pop()
        if m in seen or m in edges:
            continue
        r = resolve(m)
        if r is None:
            continue
        src, _ = r
        seen[m] = src
        try:
            imps = IMPORT_RE.findall(src.read_text(errors="replace"))
        except OSError:
            imps = []
        edges[m] = imps
        stack.extend(imps)
    return seen, edges


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("modules", nargs="+", metavar="MOD")
    ap.add_argument("--root", default="Weil", help="Lean project root (default: ./Weil)")
    ap.add_argument("--out", default="unbuilt_closure.txt", help="unbuilt-list output file")
    ap.add_argument("--hist", action="store_true", help="top unbuilt module prefixes")
    ap.add_argument("--top", type=int, default=25, help="prefix histogram depth")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    resolve = make_resolver(package_roots(root))
    seen, _edges = walk_closure(resolve, args.modules)

    unbuilt = {m: s for m, s in seen.items() if not resolve(m)[1].exists()}
    pkgcount: dict[str, int] = {}
    pkgs = root / ".lake/packages"
    for m, s in unbuilt.items():
        try:
            rel = s.relative_to(root)
            key = rel.parts[0]
            if key == ".lake" and len(rel.parts) > 3:
                # .lake/packages/<pkg>/<sub>/... -> "<pkg>/<sub>"
                key = rel.parts[2] + "/" + rel.parts[3]
        except ValueError:
            key = "?"
        pkgcount[key] = pkgcount.get(key, 0) + 1
    total_bytes = sum(s.stat().st_size for s in unbuilt.values())
    print(f"closure modules={len(seen)} unbuilt={len(unbuilt)} src_MB={total_bytes/1e6:.1f}")
    for k, v in sorted(pkgcount.items(), key=lambda x: -x[1]):
        print(f"  {k:40s} {v}")
    if args.hist:
        h: dict[str, int] = {}
        for m in unbuilt:
            parts = m.split(".")
            key = ".".join(parts[:3]) if len(parts) > 2 else m
            h[key] = h.get(key, 0) + 1
        print("  --- top unbuilt prefixes ---")
        for k, v in sorted(h.items(), key=lambda x: -x[1])[: args.top]:
            print(f"    {k:70s} {v}")
    out = Path(args.out)
    out.write_text("\n".join(sorted(unbuilt)))
    print(f"  unbuilt list -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
