#!/usr/bin/env python3
"""Package-aware import-closure analyzer for the Weil/Stacks tree.

Serial builder's single-root assumption cannot resolve StacksFrontier.* modules
(they live under .lake/packages/Stacks/, not under the root package). This walks
imports across every package root and reports built/unbuilt counts + shape.

Usage: closure_analyze.py MOD [MOD...] [--hist] [--top N]
"""
from __future__ import annotations
import re, sys
from pathlib import Path

WEIL = Path("/Users/dmitri.arkhipov/bigo-campaign/weil-verify/Weil")
PKGS = WEIL / ".lake/packages"
IMPORT_RE = re.compile(r"^\s*(?:public\s+|private\s+)?import\s+([A-Za-z0-9_.']+)", re.M)

# (package_dir, [sub-roots]) -- module name maps to <pkg>/<sub>/<rel>.lean
# module names carry their lib root (Weil.Foo -> Weil/Weil/Foo.lean,
# StacksFrontier.Foo -> <pkg>/StacksFrontier/Foo.lean), so pkg/rel resolves all.
PQ = [(WEIL, [""])] + [(p, [""]) for p in sorted(PKGS.iterdir()) if p.is_dir()]

_cache: dict[str, tuple[Path, Path] | None] = {}


def resolve(mod: str) -> tuple[Path, Path] | None:
    """-> (source file, olean path)"""
    if mod in _cache:
        return _cache[mod]
    rel = mod.replace(".", "/") + ".lean"
    orl = mod.replace(".", "/") + ".olean"
    for pkg, subs in PQ:
        for sub in subs:
            src = (pkg / sub / rel) if sub else (pkg / rel)
            if src.is_file():
                res = (src, pkg / ".lake/build/lib/lean" / orl)
                _cache[mod] = res
                return res
    _cache[mod] = None
    return None


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    hist = "--hist" in sys.argv
    seen: dict[str, Path] = {}
    edges: dict[str, list[str]] = {}
    stack = list(args)
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

    unbuilt = {m: s for m, s in seen.items() if not resolve(m)[1].exists()}
    pkgcount: dict[str, int] = {}
    for m, s in unbuilt.items():
        try:
            key = str(s.relative_to(WEIL)).split("/")[0]
            if key == ".lake":
                key = "Stacks/" + str(s.relative_to(PKGS / "Stacks")).split("/")[0]
        except ValueError:
            key = "?"
        pkgcount[key] = pkgcount.get(key, 0) + 1
    total_bytes = sum(s.stat().st_size for s in unbuilt.values())
    print(f"closure modules={len(seen)} unbuilt={len(unbuilt)} src_MB={total_bytes/1e6:.1f}")
    for k, v in sorted(pkgcount.items(), key=lambda x: -x[1]):
        print(f"  {k:40s} {v}")
    if hist:
        h: dict[str, int] = {}
        for m, s in unbuilt.items():
            parts = m.split(".")
            key = ".".join(parts[:3]) if len(parts) > 2 else m
            h[key] = h.get(key, 0) + 1
        print("  --- top unbuilt prefixes ---")
        for k, v in sorted(h.items(), key=lambda x: -x[1])[:25]:
            print(f"    {k:70s} {v}")
    Path("/tmp/unbuilt_closure.txt").write_text("\n".join(sorted(unbuilt)))
    print("  unbuilt list -> /tmp/unbuilt_closure.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
