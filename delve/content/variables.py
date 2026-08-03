"""Pack variables: declare `{{tokens}}` in a per-locale template, fill them from an instance
`variables.md`, and substitute into displayed pack text.

The template (`variables.template.md`) ships with the pack and is the authority on which tokens
exist; the filled `variables.md` is instance-specific and gitignored (DELVE-0020). Values live in
the document body, not frontmatter (rule 5). Built-ins like `{{player}}` come from run state and
are merged by the session, never declared. Plain `str.replace` leaves a stray single brace alone,
mirroring `progress.scrolls.render_scroll`.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from pathlib import Path

from delve.content.markup import tokenize

# Engine-provided; an author cannot declare or shadow these. The session fills them from run state.
BUILTINS = frozenset({"player", "pack_title"})

_TOKEN_RE = re.compile(r"^\{\{([a-z][a-z0-9_]*)\}\}$")


def parse_variables_md(path: str, text: str) -> dict[str, str]:
    """Parse a variables template or filled file into `{name: value}` (bare names, no braces).

    Each bullet is `` `{{name}}`: value ``; after markup flattening the backticks are gone, so the
    token is the text before the first `: `. Built-in names are skipped here so a mistaken
    declaration cannot enter `Pack.variables`; the session still wins if one slips through.
    """
    out: dict[str, str] = {}
    for tok in tokenize(text):
        if tok.kind != "bullet":
            continue
        if ": " not in tok.text:
            continue
        key_part, value = tok.text.split(": ", 1)
        m = _TOKEN_RE.match(key_part.strip())
        if not m:
            continue
        name = m.group(1)
        if name in BUILTINS:
            continue
        out[name] = value.strip()
    return out


def load_variables(locale_dir: Path) -> dict[str, str]:
    """Merge template defaults with an optional filled `variables.md` (filled wins per token)."""
    locale_dir = Path(locale_dir)
    template_path = locale_dir / "variables.template.md"
    if not template_path.is_file():
        return {}
    template = parse_variables_md(str(template_path), template_path.read_text(encoding="utf-8"))
    filled_path = locale_dir / "variables.md"
    filled: dict[str, str] = {}
    if filled_path.is_file():
        filled = parse_variables_md(str(filled_path), filled_path.read_text(encoding="utf-8"))
    return {name: filled.get(name, default) for name, default in template.items()}


def substitute(text: str, values: Mapping[str, str]) -> str:
    """Replace every `{{name}}` whose bare name is in `values`. Plain replace, not `str.format`."""
    if not text or not values:
        return text
    out = text
    for name, value in values.items():
        out = out.replace(f"{{{{{name}}}}}", value)
    return out


def substitute_spans(spans: tuple, values: Mapping[str, str]) -> tuple:
    """Substitute inside each `(text, strong)` run, keeping weights."""
    if not spans or not values:
        return spans
    return tuple((substitute(t, values), strong) for t, strong in spans)


def substitute_table(rows: tuple, values: Mapping[str, str]) -> tuple:
    """Substitute inside every cell of a table's styled grid."""
    if not rows or not values:
        return rows
    return tuple(
        tuple(substitute_spans(cell, values) for cell in row)
        for row in rows
    )
