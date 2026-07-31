"""Engine strings: the message line, the hint line, the status labels, keeper stage directions,
and the number/date formatting data, one TOML catalogue per locale (PLAN.md section 8).

No gettext: a `.po`/`.mo` toolchain for a few hundred strings is a build step this project does
not want. `tomllib` reads a table that a translator can diff and review, and the same file also
carries the `[format]` data (currency, decimal, month names) that PLAN.md section 8 insists is
locale *data*, not translation, and must never come from `locale.setlocale`/`strftime`.

`Strings` is a thin, duck-typed accessor: `s("msg.cant_go")`, or `s("msg.descend", title=...)`
for one that interpolates. It is handed to `RunState` (session) and, opaquely, to `ui` so the
frontend can localise its own prompts without importing this package (rule 2). `fmt` exposes the
`[format]` table for the scroll and status line.
"""

import os
import tomllib
from pathlib import Path

_DIR = Path(__file__).resolve().parent
LANGS = ("en", "nl")
DEFAULT = "en"


class Strings:
    """A loaded catalogue. Keys are dotted paths into the TOML tables (`msg.cant_go`); a value
    may interpolate with `str.format` fields, or be a list of paragraphs (the REPELLED panel)."""

    def __init__(self, lang: str, data: dict):
        self.lang = lang
        self._data = data
        self.fmt: dict = data["format"]

    def __call__(self, key: str, **kw):
        node = self._data
        for part in key.split("."):
            node = node[part]
        if isinstance(node, list):
            return [item.format(**kw) for item in node] if kw else list(node)
        return node.format(**kw) if kw else node

    def keeper_kind(self, kind: str) -> str:
        """The localised voice label ('wizard' -> 'tovenaar'), falling back to the raw kind so an
        unlisted keeper voice degrades to its English slug rather than raising."""
        return self._data["keeper_kind"].get(kind, kind)

    def flavour_emoji(self) -> dict:
        """The global keyword→emoji table (`[flavour_emoji]`) that garnishes question text; empty if
        the locale defines none, so the augmentation is simply a no-op (session/flavour.py)."""
        return dict(self._data.get("flavour_emoji", {}))

    def teach(self, kind: str, **kw) -> str:
        """The stage direction as the keeper opens the lesson, in that keeper's voice (M8): a
        wizard settles in, a gatekeeper keeps it short, a shopkeeper lays it out. An unlisted kind
        falls back to a neutral line rather than raising."""
        table = self._data["teach"]
        return table.get(kind, table["default"]).format(**kw)


def normalise(lang: str | None) -> str:
    """A user-supplied or detected locale to one of the supported codes. `nl_NL`, `nl-BE`, `NL`
    all collapse to `nl`; anything unsupported falls back to English (PLAN.md section 8)."""
    if lang is None:
        lang = _detect()
    code = (lang or "").replace("-", "_").split("_")[0].lower()
    return code if code in LANGS else DEFAULT


def _detect() -> str:
    """The system locale, read from the environment rather than `locale.setlocale` (which is
    process-global and host-dependent, the dependency class PLAN.md section 8 rejects)."""
    for var in ("LC_ALL", "LC_MESSAGES", "LANG"):
        value = os.environ.get(var)
        if value:
            return value
    return DEFAULT


def load(lang: str | None = None) -> Strings:
    """Load the catalogue for `lang` (normalised), defaulting to the system locale then English."""
    code = normalise(lang)
    data = tomllib.loads((_DIR / f"{code}.toml").read_text(encoding="utf-8"))
    return Strings(code, data)
