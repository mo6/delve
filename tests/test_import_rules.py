"""Enforce PLAN.md section 4's dependency rules in CI, from M1. Both fail silently under a
deadline (one `import engine.world` in render.py and the loop is back inside curses,
untestable), so they are checked mechanically rather than by intention.

Rule 1: `engine` imports nothing from content, assess, session, ui, gate, or progress.
Rule 2: `ui` imports only `session` (and itself); nothing outside `ui` imports curses.
"""

import ast
import pathlib

import pytest

PKG = pathlib.Path(__file__).resolve().parent.parent / "delve"
PY_FILES = sorted(PKG.rglob("*.py"))


def _subpackage(path: pathlib.Path) -> str:
    """'engine', 'ui', ... for a file under delve/, or '' for delve/*.py at the top."""
    rel = path.relative_to(PKG).parts
    return rel[0] if len(rel) > 1 else ""


def _imported_delve_targets(path: pathlib.Path) -> set[str]:
    """Absolute 'delve.<sub>...' names a file imports, resolving relative imports."""
    tree = ast.parse(path.read_text())
    pkg_parts = path.relative_to(PKG.parent).with_suffix("").parts[:-1]  # package of the module
    targets: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            targets.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0:
                if node.module:
                    targets.add(node.module)
            else:
                base = list(pkg_parts)
                if node.level > 1:
                    base = base[: -(node.level - 1)]
                prefix = ".".join(base)
                targets.add(f"{prefix}.{node.module}" if node.module else prefix)
    return {t for t in targets if t == "delve" or t.startswith("delve.")}


def _sub(target: str) -> str:
    """'engine' from 'delve.engine.world'; '' from 'delve'."""
    parts = target.split(".")
    return parts[1] if len(parts) > 1 else ""


ENGINE_FILES = [p for p in PY_FILES if _subpackage(p) == "engine"]
UI_FILES = [p for p in PY_FILES if _subpackage(p) == "ui"]
NON_UI_FILES = [p for p in PY_FILES if _subpackage(p) != "ui"]


@pytest.mark.parametrize("path", ENGINE_FILES, ids=lambda p: p.name)
def test_engine_imports_only_engine(path):
    forbidden = {"content", "assess", "session", "ui", "gate", "progress"}
    crossed = {_sub(t) for t in _imported_delve_targets(path)} & forbidden
    assert not crossed, f"engine/{path.name} imports {crossed} (PLAN section 4, rule 1)"


@pytest.mark.parametrize("path", UI_FILES, ids=lambda p: p.name)
def test_ui_imports_only_session(path):
    allowed = {"session", "ui", ""}  # '' = the top-level `delve` package (__version__)
    crossed = {_sub(t) for t in _imported_delve_targets(path)} - allowed
    assert not crossed, f"ui/{path.name} reaches past session into {crossed} (rule 2)"


@pytest.mark.parametrize("path", NON_UI_FILES, ids=lambda p: str(p.relative_to(PKG)))
def test_only_ui_imports_curses(path):
    tree = ast.parse(path.read_text())
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.add(node.module.split(".")[0])
    assert "curses" not in names, f"{path.relative_to(PKG)} imports curses; only ui/ may (rule 2)"
