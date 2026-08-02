"""Paint a Frame to the screen: message line on top, map centred-left, status and hint at the
bottom, and the keeper's panel over the right of the map when an overlay is present, or the
ambient room-entry toast (DELVE-0060) top-left or top-right (whichever side the learner isn't
standing on, so it never covers the room they're in) when there is one and no panel is open. The
only logic here is placement; everything shown is read straight off the Frame.

The map is painted in the 16-colour palette (M8): each cell carries its own `Colour`, mapped to a
curses attribute in `ui/attrs.py`, dimmed for visited-but-unlit tiles. It degrades to the old
monochrome look on a terminal with no colour. Room walls ('-'/'|' in the Frame) are drawn with
curses' ACS_ line-drawing set via `ui/walls.py`, which maps each wall to a box-drawing piece from
its neighbours (corners and tees included); on a terminal that cannot line-draw it stands in with
the original ASCII, so there is no separate fallback path.
"""

import curses

from delve.session.views import Colour, Frame
from delve.ui import attrs, walls, windows


def _player_x(m) -> int:
    """The learner's own column on the map (distinct from a keeper, also drawn as `@`, by colour:
    `Colour.WHITE` for the player, `Colour.BRIGHT_MAGENTA` for a keeper, `RunState._cell`). Used
    only to decide which side of the screen the ambient toast should avoid (DELVE-0060); falls
    back to the map's left edge if somehow not found, so a toast still has a side to anchor to."""
    for row in m.cells:
        for x, cell in enumerate(row):
            if cell.glyph == "@" and cell.colour == Colour.WHITE:
                return x
    return 0


def _put(stdscr, y: int, x: int, text: str, attr: int = curses.A_NORMAL) -> None:
    try:
        stdscr.addstr(y, x, text, attr)
    except curses.error:
        pass


def _putch(stdscr, y: int, x: int, ch: int, attr: int = curses.A_NORMAL) -> None:
    """Draw a single ACS_ character. Separate from `_put` because the box-drawing constants are
    ints (with the alt-charset bit set), not text, so they go through `addch`, not `addstr`."""
    try:
        stdscr.addch(y, x, ch, attr)
    except curses.error:
        pass


def draw(stdscr, frame: Frame, page: int = 1, msg_page: int = 1) -> None:
    stdscr.erase()
    rows, cols = stdscr.getmaxyx()
    m = frame.map
    map_area_h = rows - 3

    msg = frame.messages[-1] if frame.messages else ""
    # A message wider than the line is paged with a --More-- prompt (DELVE-0030), but only on the
    # bare map: while a panel is open it owns the screen and the frozen encounter text is short, so
    # the message shows as-is there. `msg_page` is the UI-owned page offset, like the overlay page.
    if msg and frame.overlay is None:
        pages = windows.message_pages(msg, cols)
        idx = min(max(msg_page, 1), len(pages)) - 1
        msg = pages[idx] + (" " + windows.MESSAGE_MORE if idx < len(pages) - 1 else "")
    # A right/wrong answer highlights the line (green/black, red/black); everything else is plain.
    if msg and frame.message_bg is not None:
        _put(stdscr, 0, 0, f" {msg} "[: cols - 1], attrs.bar_attr(frame.message_bg))
    else:
        _put(stdscr, 0, 0, msg[: cols - 1])

    # The map is anchored top-left of the map area; the panel (when present) covers the right,
    # which at this point in the slice is unexplored and therefore black anyway.
    for y in range(min(m.rows, map_area_h)):
        for x in range(m.cols):
            cell = m.cells[y][x]
            if cell.glyph == " ":
                continue
            attr = attrs.attr_for(cell.colour, dim=cell.dim)
            if cell.glyph == "@":                 # the learner and keepers stand out, bold
                attr |= curses.A_BOLD
            role = walls.wall_role(m.cells, y, x, m.rows, m.cols)
            box = walls.acs_for(role) if role is not None else None
            if isinstance(box, int):              # an ACS_ constant: draw it with addch
                _putch(stdscr, 1 + y, x, box, attr)
            else:                                  # a plain glyph, or the ASCII wall stand-in
                _put(stdscr, 1 + y, x, box or cell.glyph, attr)

    if frame.overlay is not None:
        windows.draw(stdscr, frame.overlay, m.cols, page)
    # The ambient toast (DELVE-0060) is independent of overlay, but only drawn while no panel is
    # open: a panel owns the screen (the same "a panel owns the screen" precedent the top message
    # line already follows above), and its geometry is not guaranteed clear of the toast's corner.
    elif frame.toast is not None:
        windows.draw_toast(stdscr, frame.toast, m.cols, _player_x(m))
    # A small spinner window while that same call is still running (DELVE-0082), replaced by the
    # toast above the instant it resolves; `RunState.frame()` never sets both at once.
    elif frame.toast_loading is not None:
        windows.draw_toast_loading(stdscr, frame.toast_loading, m.cols, _player_x(m))

    s = frame.status
    status = (
        f"{s.name}  Dlvl:{s.dlvl}  {s.rooms_label}:{s.rooms_done}/{s.rooms_total}  "
        f"{s.gold_symbol}:{s.gold}  HP:{s.hp}({s.max_hp})  T:{s.turn}"
    )
    _put(stdscr, rows - 2, 0, status[: cols - 1])
    _put(stdscr, rows - 1, 0, frame.hint[: cols - 1])
    stdscr.refresh()
