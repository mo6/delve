"""A minimal stdscr stand-in shared by headless render tests and the on-demand screenshot tool.

Not a `./tools.sh` entry (leading underscore); not part of the `delve` package. Reproduces curses'
`addstr` wrapping and the bottom-right-cell error so a write that overruns a row spills onto the
next one here too, matching real terminal behaviour that a clipping fake would hide.
"""

from __future__ import annotations

import curses
import os
import sys

from delve.session.views import Colour
from delve.ui import attrs as ui_attrs
from delve.ui import walls as ui_walls
from delve.ui.windows import _cw

# Synthetic colour-pair encoding in the same A_COLOR bits curses.color_pair uses
# (pairs 1-8 = fg on default bg; 9-16 = black on solid colour), without calling color_pair,
# which needs initscr().


class CursesEmu:
    """A minimal stdscr that reproduces curses' addstr wrapping and its bottom-right-cell error."""

    def __init__(self, rows: int, cols: int):
        self.rows, self.cols = rows, cols
        self.g = [[" "] * cols for _ in range(rows)]
        self.a = [[0] * cols for _ in range(rows)]   # the attr each cell was last written with

    def getmaxyx(self):
        return (self.rows, self.cols)

    def erase(self):
        self.g = [[" "] * self.cols for _ in range(self.rows)]
        self.a = [[0] * self.cols for _ in range(self.rows)]

    def refresh(self):
        pass

    def addstr(self, y, x, text, attr=0):
        """Real ncursesw (a UTF-8 locale, `locale.setlocale` in `ui/app.py`) advances its cursor
        by a wide glyph's true *display* width, not one cell per codepoint, but it never writes a
        second character for that glyph's second column: the terminal's own rendering spans both
        columns from the one codepoint. A first cut here got this wrong, writing the glyph into one
        cell and leaving the next cell's pre-existing blank in place, which `row()` then rejoined as
        a *real*, printable space, a phantom extra column no real terminal emits (confirmed against
        an actual play session, DELVE-0092 playtesting). The fix: mark a wide glyph's trailing
        cell(s) with `''`, which `row()`'s plain join drops entirely, same as a real terminal drops
        nothing there because it was never asked to render anything there."""
        cy, cx = y, x
        for ch in text:
            if cy >= self.rows or cy < 0:
                raise curses.error
            w = _cw(ch) or 1          # a zero-width combining mark still needs the cursor to move
            if 0 <= cx < self.cols:
                self.g[cy][cx] = ch
                self.a[cy][cx] = attr
                for trail in range(1, w):
                    if cx + trail < self.cols:
                        self.g[cy][cx + trail] = ""
                        self.a[cy][cx + trail] = attr
            cx += w
            if cx >= self.cols:      # wrap to the next row, exactly as curses does
                cx, cy = 0, cy + 1

    def addch(self, y, x, ch, attr=0):
        """ACS_ path used by render.draw for walls; without initscr, walls.acs_for returns ASCII
        strings and this is unused, but the real API has it so a future ACS path still lands."""
        text = ch if isinstance(ch, str) else chr(ch & 0xFF)
        self.addstr(y, x, text, attr)

    def row(self, r):
        return "".join(self.g[r])

    def attr_row(self, r):
        return self.a[r]

    def plain(self) -> str:
        """The character grid as newline-joined rows, no trailing spaces stripped (exact WxH)."""
        return "\n".join(self.row(r) for r in range(self.rows))


def _encode_pair(pair: int) -> int:
    return (pair << 8) & curses.A_COLOR


def pair_number(attr: int) -> int:
    """The colour-pair number stored on a cell, same numbering as attrs.init()."""
    return (attr & curses.A_COLOR) >> 8


class enable_fake_colour:
    """Temporarily replace `attrs.attr_for` / `bar_attr` with versions that stamp the same pair
    numbers `attrs.init()` would allocate, without needing a live curses terminal. Reads colour
    from `attrs._BASE` so the ANSI writer and the live mapping stay one table. Use as a context
    manager so other headless tests that expect the uninitialised (A_BOLD / A_REVERSE) path are
    not permanently patched."""

    def __enter__(self):
        self._prev_attr_for = ui_attrs.attr_for
        self._prev_bar_attr = ui_attrs.bar_attr

        def attr_for(colour: Colour, *, dim: bool = False) -> int:
            base, bright = ui_attrs._BASE[colour]
            attr = _encode_pair(base + 1)      # pairs 1-8, matching attrs.init()
            if bright:
                attr |= curses.A_BOLD
            if dim:
                attr |= curses.A_DIM
            return attr

        def bar_attr(colour: Colour) -> int:
            base, _bright = ui_attrs._BASE[colour]
            return _encode_pair(base + 9)      # pairs 9-16, matching attrs.init()

        ui_attrs.attr_for = attr_for  # type: ignore[assignment]
        ui_attrs.bar_attr = bar_attr  # type: ignore[assignment]
        return self

    def __exit__(self, *exc):
        ui_attrs.attr_for = self._prev_attr_for
        ui_attrs.bar_attr = self._prev_bar_attr
        return False


# The box-drawing glyph curses.ACS_* would resolve to on a real terminal with a working alternate
# character set, keyed the same as walls._ACS_NAME. `walls.acs_for` only reaches this stand-in
# because curses.ACS_* isn't populated without `curses.initscr()` (headless, same reason colour
# needs its own stand-in above); the tool fakes it too so a wall reads as a wall, not a dash, the
# same way a learner playing for real would see it.
_ACS_UNICODE = {
    "hline": "─", "vline": "│",
    "ul": "┌", "ur": "┐", "ll": "└", "lr": "┘",
    "ltee": "├", "rtee": "┤", "ttee": "┬", "btee": "┴",
    "plus": "┼",
}


class enable_fake_acs:
    """Temporarily replace `walls.acs_for` with a version that returns the box-drawing glyph a
    real terminal's alternate character set would draw, instead of `walls.py`'s own ASCII stand-in
    (which only exists because `curses.ACS_*` needs `curses.initscr()`, never called headlessly).
    Returns a plain string, not a curses ACS int, so it paints through the same `_put` path the
    ASCII stand-in already uses (no int-decoding pitfall). Use as a context manager, the same as
    `enable_fake_colour`, so `test_render.py`'s own ASCII-fallback assertions stay unaffected."""

    def __enter__(self):
        self._prev = ui_walls.acs_for
        ui_walls.acs_for = lambda role: _ACS_UNICODE[role]  # type: ignore[assignment]
        return self

    def __exit__(self, *exc):
        ui_walls.acs_for = self._prev
        return False


def colour_wanted(*, stream=None, environ=None) -> bool:
    """Whether to emit ANSI escapes: off when `NO_COLOR` is set or the stream is not a tty."""
    env = os.environ if environ is None else environ
    if env.get("NO_COLOR", "") != "":
        return False
    out = sys.stdout if stream is None else stream
    return bool(getattr(out, "isatty", lambda: False)())


def _sgr_codes(attr: int) -> list[str]:
    """SGR parameter list for one cell attribute, decoded via attrs.init()'s pair numbering."""
    codes: list[str] = []
    if attr & curses.A_BOLD:
        codes.append("1")
    if attr & curses.A_DIM:
        codes.append("2")
    if attr & curses.A_REVERSE:
        codes.append("7")
    pair = pair_number(attr)
    if 1 <= pair <= 8:
        codes.append(f"3{pair - 1}")
    elif 9 <= pair <= 16:
        codes.append("30")
        codes.append(f"4{pair - 9}")
    return codes


def ansi_render(scr: CursesEmu, *, colour: bool = True) -> str:
    """Render the emulator's grid to a string. With `colour`, wrap runs of identical attrs in
    SGR escapes derived from `delve.ui.attrs`' pair map; without, emit plain characters only."""
    reset = "\033[0m"
    lines: list[str] = []
    for y in range(scr.rows):
        parts: list[str] = []
        run_attr = 0
        run: list[str] = []
        for x in range(scr.cols):
            attr = scr.a[y][x]
            ch = scr.g[y][x]
            if attr != run_attr and run:
                text = "".join(run)
                if colour and run_attr:
                    codes = _sgr_codes(run_attr)
                    parts.append(f"\033[{';'.join(codes)}m{text}{reset}" if codes else text)
                else:
                    parts.append(text)
                run = []
            run_attr = attr
            run.append(ch)
        if run:
            text = "".join(run)
            if colour and run_attr:
                codes = _sgr_codes(run_attr)
                parts.append(f"\033[{';'.join(codes)}m{text}{reset}" if codes else text)
            else:
                parts.append(text)
        lines.append("".join(parts))
    return "\n".join(lines)
