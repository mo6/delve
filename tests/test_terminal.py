"""The 100x30 size guard, tested without a terminal, which is the whole point of keeping
it out of curses (PLAN.md section 4)."""

import pytest

from delve.ui import terminal


@pytest.mark.parametrize(
    "cols,rows,expected",
    [
        (100, 30, True),   # exactly the minimum fits
        (120, 30, True),   # Windows Terminal's default
        (200, 60, True),   # larger is fine
        (99, 30, False),   # one column short
        (100, 29, False),  # one row short
        (80, 24, False),   # macOS Terminal default
    ],
)
def test_fits(cols, rows, expected):
    assert terminal.fits(cols, rows) is expected


def test_overlay_names_the_exact_size():
    lines = terminal.overlay_lines(80, 24)
    joined = "\n".join(lines)
    # Names both the current size and the required size, not just "too small".
    assert "80x24" in joined
    assert f"{terminal.MIN_COLS}x{terminal.MIN_ROWS}" in joined
    assert "quit" in joined.lower()
