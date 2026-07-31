"""The map's colour: a `Colour` view-model value to a curses attribute.

The Frame carries one of sixteen `Colour` names per cell (PLAN.md section 4); this is where they
become curses. Sixteen colours the portable way: eight base colours (the only `COLOR_*` constants
guaranteed on Apple's ncurses 6.0 and on PDCurses) plus **bold** for the bright half, which is how
NetHack has always drawn its bright palette. No 256-colour or extended-colour APIs, which aren't
portably there (CLAUDE.md, PLAN.md section 3).

`init()` sets up the pairs once inside `curses.wrapper`; it degrades cleanly on a terminal with no
colour, where `attr_for` falls back to the plain bold/dim attributes the M2 renderer already used.
Only `ui/` imports curses (rule 2), so this lives here.
"""

import curses

from delve.session.views import Colour

# Each logical colour is a base COLOR_* (0-7) and whether it is the bright variant. Bright renders
# as the base colour plus A_BOLD, the portable 16 on every target terminal.
_BASE: dict[Colour, tuple[int, bool]] = {
    Colour.BLACK: (curses.COLOR_BLACK, False),
    Colour.RED: (curses.COLOR_RED, False),
    Colour.GREEN: (curses.COLOR_GREEN, False),
    Colour.YELLOW: (curses.COLOR_YELLOW, False),
    Colour.BLUE: (curses.COLOR_BLUE, False),
    Colour.MAGENTA: (curses.COLOR_MAGENTA, False),
    Colour.CYAN: (curses.COLOR_CYAN, False),
    Colour.WHITE: (curses.COLOR_WHITE, False),
    Colour.BRIGHT_BLACK: (curses.COLOR_BLACK, True),
    Colour.BRIGHT_RED: (curses.COLOR_RED, True),
    Colour.BRIGHT_GREEN: (curses.COLOR_GREEN, True),
    Colour.BRIGHT_YELLOW: (curses.COLOR_YELLOW, True),
    Colour.BRIGHT_BLUE: (curses.COLOR_BLUE, True),
    Colour.BRIGHT_MAGENTA: (curses.COLOR_MAGENTA, True),
    Colour.BRIGHT_CYAN: (curses.COLOR_CYAN, True),
    Colour.BRIGHT_WHITE: (curses.COLOR_WHITE, True),
}

_enabled = False
_pairs: dict[int, int] = {}      # base COLOR_* -> pair number (colour on the default background)
_bg_pairs: dict[int, int] = {}   # base COLOR_* -> pair number (black text on that solid colour)


def init() -> None:
    """Allocate one pair per base colour on the terminal's default background. Called once inside
    `curses.wrapper`; a no-colour terminal leaves `_enabled` False and stays monochrome."""
    global _enabled
    if not curses.has_colors():
        return
    curses.start_color()
    try:
        curses.use_default_colors()   # keep the terminal's own background (-1), so panels sit clean
        background = -1
    except curses.error:
        background = curses.COLOR_BLACK
    for colour in range(8):
        pair = colour + 1
        curses.init_pair(pair, colour, background)
        _pairs[colour] = pair
    # A second bank of pairs for a filled highlight: black text on a solid colour, used for the
    # correct/not-quite message bar. Pairs 9-16, clear of the foreground pairs above.
    for colour in range(8):
        pair = colour + 9
        curses.init_pair(pair, curses.COLOR_BLACK, colour)
        _bg_pairs[colour] = pair
    _enabled = True


def attr_for(colour: Colour, *, dim: bool = False) -> int:
    """The curses attribute for a cell: its colour pair (bright adds A_BOLD), dimmed for a visited
    but unlit tile. With no colour it returns just the bold/dim attributes, i.e. the old look."""
    base, bright = _BASE[colour]
    attr = curses.color_pair(_pairs[base]) if _enabled and base in _pairs else 0
    if bright:
        attr |= curses.A_BOLD
    if dim:
        attr |= curses.A_DIM
    return attr


def bar_attr(colour: Colour) -> int:
    """A filled highlight: black text on a solid `colour`, for the correct/not-quite message line.
    On a terminal with no colour it falls back to reverse video, so the line still stands out."""
    base, _bright = _BASE[colour]
    if _enabled and base in _bg_pairs:
        return curses.color_pair(_bg_pairs[base])
    return curses.A_REVERSE
