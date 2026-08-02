"""DELVE-0092: the on-demand screenshot tool drives the real renderer, not a parallel mock."""

import curses
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import screenshot as screenshot_tool  # noqa: E402
from _fakescreen import (  # noqa: E402
    ansi_render,
    colour_wanted,
    enable_fake_colour,
    pair_number,
)

from delve.session.views import Colour  # noqa: E402
from delve.ui import attrs as ui_attrs  # noqa: E402
from delve.ui import render  # noqa: E402


def _assert_100x30(text: str) -> list[str]:
    lines = text.split("\n")
    assert len(lines) == 30, f"want 30 rows, got {len(lines)}"
    for i, line in enumerate(lines):
        # Strip ANSI for width check when present.
        plain = _strip_ansi(line)
        assert len(plain) == 100, f"row {i}: want 100 cols, got {len(plain)}"
    return lines


def _strip_ansi(s: str) -> str:
    out, i = [], 0
    while i < len(s):
        if s[i] == "\033" and i + 1 < len(s) and s[i + 1] == "[":
            i += 2
            while i < len(s) and s[i] != "m":
                i += 1
            i += 1
            continue
        out.append(s[i])
        i += 1
    return "".join(out)


def test_list_scenarios_with_no_name_exits_clean():
    assert screenshot_tool.main([]) == 0
    # And the Python entry lists every registered name.
    listing = screenshot_tool.list_scenarios()
    for name in screenshot_tool.SCENARIOS:
        assert name in listing


def test_mcq_assertion_tutorial_match_real_draw_path():
    """The tool's capture equals an independent render.draw of the same scenario frame."""
    from _fakescreen import CursesEmu

    for name in ("mcq", "assertion", "tutorial"):
        _summary, fn = screenshot_tool.SCENARIOS[name]
        shot = fn()
        expected = CursesEmu(30, 100)
        with enable_fake_colour():
            render.draw(expected, shot.frame, page=shot.page, msg_page=shot.msg_page)

        got = screenshot_tool.capture(name)
        assert got.plain() == expected.plain()
        assert got.rows == 30 and got.cols == 100
        plain = screenshot_tool.render_scenario(name, colour=False)
        _assert_100x30(plain)
        assert plain == got.plain()


def test_capture_is_deterministic():
    a = screenshot_tool.render_scenario("mcq", colour=False)
    b = screenshot_tool.render_scenario("mcq", colour=False)
    assert a == b


def test_eliminated_option_ansi_traces_to_attrs_and_no_color_is_plain():
    scr = screenshot_tool.capture("mcq-eliminated")
    # At least one cell carries A_DIM (the paid removal).
    dim_cells = [(y, x) for y in range(scr.rows) for x in range(scr.cols)
                 if scr.a[y][x] & curses.A_DIM]
    assert dim_cells

    coloured = ansi_render(scr, colour=True)
    assert "\033[2m" in coloured                    # SGR dim
    _assert_100x30(coloured)

    plain = ansi_render(scr, colour=False)
    assert "\033[" not in plain
    assert plain == scr.plain()

    # A coloured map cell's pair number matches attrs._BASE's init() numbering.
    # The learner `@` is Colour.WHITE → base COLOR_WHITE (7) → pair 8.
    at = next((y, x) for y in range(scr.rows) for x in range(scr.cols)
              if scr.g[y][x] == "@" and pair_number(scr.a[y][x]) == 8)
    base, _bright = ui_attrs._BASE[Colour.WHITE]
    assert base + 1 == pair_number(scr.a[at[0]][at[1]])


def test_no_color_env_disables_ansi():
    class _Tty:
        def isatty(self):
            return True

    class _Pipe:
        def isatty(self):
            return False

    assert colour_wanted(environ={"NO_COLOR": "1"}, stream=_Tty()) is False
    assert colour_wanted(environ={}, stream=_Pipe()) is False
    assert colour_wanted(environ={}, stream=_Tty()) is True


def test_unknown_scenario_exits_nonzero(capsys):
    assert screenshot_tool.main(["no-such-screen"]) == 1
    err = capsys.readouterr().err
    assert "unknown scenario" in err
    assert "mcq" in err
