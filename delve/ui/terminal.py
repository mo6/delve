"""Terminal geometry: the minimum-size rule and the resize overlay text.

Pure functions, no curses. The size guard is the one piece of M0 with real logic, so
it lives here where a test can reach it without a pty. ui/app.py is the curses glue that
calls these; it holds no logic of its own.

The minimum is 100x30, Windows Terminal's exact default, so Windows needs no resize on
first run. Below it, Delve shows an overlay and waits; it never tries to degrade. See
PLAN.md section 7.
"""

MIN_COLS = 100
MIN_ROWS = 30


def fits(cols: int, rows: int) -> bool:
    """True when the terminal is at least the 100x30 minimum."""
    return cols >= MIN_COLS and rows >= MIN_ROWS


def overlay_lines(cols: int, rows: int, need_cols: int = MIN_COLS,
                  need_rows: int = MIN_ROWS) -> list[str]:
    """The resize overlay, naming the exact size required rather than just complaining.

    PLAN.md section 12: 'the overlay names the exact size required'. The caller centres
    these lines in whatever space the (too-small) terminal currently has. `need_*` defaults
    to the 100x30 minimum but can name a run's locked map size once one is pinned, since a
    mid-run shrink must be resized back to what the dungeon was laid out for (section 7).
    """
    return [
        "Delve needs a larger terminal.",
        "",
        f"This terminal is {cols}x{rows}.",
        f"Delve needs at least {need_cols}x{need_rows}.",
        "",
        "Resize the window, or press q to quit.",
    ]
