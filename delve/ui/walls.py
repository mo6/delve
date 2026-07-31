"""Room walls drawn with curses' ACS_ line-drawing set (CLAUDE.md 'Borders: ACS_ for rooms').

The map's alphabet is ASCII: a wall is '-' or '|' in the Frame (portable, one cell = one column,
never translated). Whether it *draws* as a plain dash or as a box-drawing line is a rendering
choice, made here the same way colour is made in `ui/attrs.py`. ACS_ constants are portable by
construction: curses maps each to whatever the terminal can draw, so this is not a Unicode bet
(that is what window frames are). It is exactly how NetHack's DECgraphics draws its rooms.

A wall's *shape* is read from its neighbours, not from the stored glyph, so a corner (carved as
'-') becomes the right corner piece, and a wall beside a door reads as a straight run. `wall_role`
is pure geometry with no curses import, so the shape logic is unit-tested without a terminal;
`acs_for` turns a role into the ACS_ constant at paint time, falling back to an ASCII stand-in when
curses is not initialised (the headless test emulator) or cannot line-draw at all.
"""

import curses

# Glyphs that continue a wall line: the two wall halves, plus a door, which sits *in* the wall so
# the run reads straight through it. SEALED tiles already carry a '-'/'|' glyph, so they count too.
_WALLISH = frozenset({"-", "|", "+"})

_ACS_NAME = {
    "hline": "ACS_HLINE", "vline": "ACS_VLINE",
    "ul": "ACS_ULCORNER", "ur": "ACS_URCORNER", "ll": "ACS_LLCORNER", "lr": "ACS_LRCORNER",
    "ltee": "ACS_LTEE", "rtee": "ACS_RTEE", "ttee": "ACS_TTEE", "btee": "ACS_BTEE",
    "plus": "ACS_PLUS",
}
# The stand-in when ACS_ is unavailable: the original two wall glyphs, chosen per role so a wall
# still reads as a wall (corners and horizontal tees are '-', vertical tees are '|').
_ASCII = {
    "hline": "-", "vline": "|",
    "ul": "-", "ur": "-", "ll": "-", "lr": "-",
    "ltee": "|", "rtee": "|", "ttee": "-", "btee": "-",
    "plus": "+",
}


def _wallish(cells, y: int, x: int, rows: int, cols: int) -> bool:
    return 0 <= y < rows and 0 <= x < cols and cells[y][x].glyph in _WALLISH


def wall_role(cells, y: int, x: int, rows: int, cols: int) -> str | None:
    """The line-drawing role for the cell at (y, x), read from which orthogonal neighbours are
    part of a wall, or None when the cell is not a room wall (draw its own glyph). Pure geometry:
    no curses, so a corner resolves the same in a test as on a terminal."""
    if cells[y][x].glyph not in ("-", "|"):
        return None
    up = _wallish(cells, y - 1, x, rows, cols)
    down = _wallish(cells, y + 1, x, rows, cols)
    left = _wallish(cells, y, x - 1, rows, cols)
    right = _wallish(cells, y, x + 1, rows, cols)
    if up and down and left and right:
        return "plus"
    if up and down and right:
        return "ltee"
    if up and down and left:
        return "rtee"
    if left and right and down:
        return "ttee"
    if left and right and up:
        return "btee"
    if down and right:
        return "ul"
    if down and left:
        return "ur"
    if up and right:
        return "ll"
    if up and left:
        return "lr"
    if up or down:
        return "vline"
    return "hline"


def acs_for(role: str) -> int | str:
    """The ACS_ constant for a wall role, or an ASCII stand-in if ACS_ is unavailable. The
    constants are only defined after `curses.initscr()`, so this returns the stand-in under the
    headless test emulator and on any terminal without an alternate character set."""
    return getattr(curses, _ACS_NAME[role], _ASCII[role])
