"""Smoke tests for the verification tooling — no Lean toolchain required.

Pins the defect class this repo's builder fixes: a single-root resolver treats
dependency-package modules (StacksFrontier.* under .lake/packages/Stacks/) as
unknown-foreign and silently reports "closure complete" without building them.
These tests exercise resolution, closure walk, topo order and the olean ledger
on a synthetic two-package tree.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import closure_analyze  # noqa: E402
import serial_build_multi as sbm  # noqa: E402


def make_tree(root: Path) -> None:
    """root package `Root` + dependency package `Dep` with two modules."""
    (root / "Root").mkdir(parents=True)
    (root / "Root.lean").write_text("import Dep.Pkg.Mod\n")
    (root / "Root" / "Sub.lean").write_text("import Root\n")
    pkg = root / ".lake/packages/Dep"
    (pkg / "Dep/Pkg").mkdir(parents=True)
    (pkg / "Dep/Pkg/Mod.lean").write_text("public import Dep.Pkg.Leaf\n")
    (pkg / "Dep/Pkg/Leaf.lean").write_text("private import Mathlib.Tactic\n")


class TestPackageAwareResolution(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        make_tree(self.root)
        self.tree = sbm.Tree(self.root)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_root_module_resolves(self) -> None:
        src, olean = self.tree.resolve("Root")
        self.assertEqual(src, self.root / "Root.lean")
        self.assertEqual(olean, self.root / ".lake/build/lib/lean/Root.olean")

    def test_package_module_resolves_to_package_olean(self) -> None:
        src, olean = self.tree.resolve("Dep.Pkg.Mod")
        pkg = self.root / ".lake/packages/Dep"
        self.assertEqual(src, pkg / "Dep/Pkg/Mod.lean")
        self.assertEqual(olean, pkg / ".lake/build/lib/lean/Dep/Pkg/Mod.olean")

    def test_single_root_resolver_misses_package_modules(self) -> None:
        # The predecessor's defect: root-only resolution returns None for
        # package modules, which a caller then skips as "foreign".
        single = sbm.Tree.__new__(sbm.Tree)
        single.root = self.root
        single.roots = [self.root]
        single.cache = {}
        self.assertIsNone(single.resolve("Dep.Pkg.Mod"))

    def test_foreign_module_is_unknown(self) -> None:
        self.assertIsNone(self.tree.resolve("Mathlib.Tactic"))

    def test_closure_includes_package_modules(self) -> None:
        seen, edges, unknown = sbm.closure(self.tree, ["Root"])
        self.assertIn("Dep.Pkg.Mod", seen)
        self.assertIn("Dep.Pkg.Leaf", seen)
        self.assertIn("Mathlib.Tactic", unknown)  # foreign, not silently dropped
        self.assertEqual(edges["Root"], ["Dep.Pkg.Mod"])

    def test_topo_orders_dependencies_first(self) -> None:
        seen, edges, _ = sbm.closure(self.tree, ["Root"])
        order = sbm.topo(set(seen), edges)
        self.assertLess(order.index("Dep.Pkg.Leaf"), order.index("Dep.Pkg.Mod"))
        self.assertLess(order.index("Dep.Pkg.Mod"), order.index("Root"))

    def test_oleans_are_the_ledger(self) -> None:
        seen, _, _ = sbm.closure(self.tree, ["Root"])
        todo = {m for m, (_, o) in seen.items() if not o.exists()}
        self.assertEqual(len(todo), 3)
        # Mark one module built; it must drop out of todo (resume property).
        _, olean = self.tree.resolve("Dep.Pkg.Leaf")
        olean.parent.mkdir(parents=True, exist_ok=True)
        olean.write_bytes(b"")
        todo2 = {m for m, (_, o) in seen.items() if not o.exists()}
        self.assertEqual(todo2, todo - {"Dep.Pkg.Leaf"})


class TestImportRegex(unittest.TestCase):
    def test_plain_public_private(self) -> None:
        text = "import A\npublic import B\nprivate import C\n"
        self.assertEqual(sbm.IMPORT_RE.findall(text), ["A", "B", "C"])

    def test_comment_line_not_matched(self) -> None:
        self.assertEqual(sbm.IMPORT_RE.findall("-- import A\n/- import B -/\n"), [])


class TestClosureAnalyzer(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        make_tree(self.root)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_package_roots(self) -> None:
        roots = closure_analyze.package_roots(self.root)
        self.assertEqual(roots[0], self.root)
        self.assertIn(self.root / ".lake/packages/Dep", roots)

    def test_walk_and_unbuilt(self) -> None:
        resolve = closure_analyze.make_resolver(closure_analyze.package_roots(self.root))
        seen, edges = closure_analyze.walk_closure(resolve, ["Root"])
        self.assertEqual(set(seen), {"Root", "Dep.Pkg.Mod", "Dep.Pkg.Leaf"})
        unbuilt = {m for m in seen if not resolve(m)[1].exists()}
        self.assertEqual(len(unbuilt), 3)

    def test_missing_packages_dir_is_tolerated(self) -> None:
        bare = Path(self._tmp.name) / "bare"
        bare.mkdir()
        self.assertEqual(closure_analyze.package_roots(bare), [bare])


if __name__ == "__main__":
    unittest.main()
