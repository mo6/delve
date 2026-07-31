"""Render the real ui.render/ui.windows code against a curses emulator that WRAPS at the right
margin, the way real curses does. The first cut of the panel box wrote its interior fill as one
long string anchored at the right edge; curses wrapped it onto the next row, leaving a stray
border mid-panel and erasing the map. A fake screen that clips instead of wrapping hid it, so
this one wraps and asserts the box is well formed and the map survives beside it.
"""

import curses
from collections import deque

from delve.engine.world import Direction, Point
from delve.session.commands import Move, Talk
from delve.session.run import new_run
from delve.session.views import AmountView, Cell, InfoTab, InfoView, PromptView, TextBlock, TextView
from delve.ui import attrs, render, walls, windows

_BOX = set("═║╔╗╚╝")


class CursesEmu:
    """A minimal stdscr that reproduces curses' addstr wrapping and its bottom-right-cell error,
    so a write that overruns a row spills onto the next one here too."""

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
        cy, cx = y, x
        for ch in text:
            if cy >= self.rows or cy < 0:
                raise curses.error
            if 0 <= cx < self.cols:
                self.g[cy][cx] = ch
                self.a[cy][cx] = attr
            cx += 1
            if cx >= self.cols:      # wrap to the next row, exactly as curses does
                cx, cy = 0, cy + 1

    def row(self, r):
        return "".join(self.g[r])

    def attr_row(self, r):
        return self.a[r]


_CARD = {Point(0, -1): Direction.N, Point(0, 1): Direction.S,
         Point(1, 0): Direction.E, Point(-1, 0): Direction.W}


def _open_lesson(cols, rows):
    run = new_run(seed=99, cols=cols, rows=rows)
    grid = run.chapter.grid
    keeper = run.gates["phishing"].keeper.pos
    blocked = set(run.keepers)

    def path(a, b):
        prev = {a: None}
        q = deque([a])
        while q:
            c = q.popleft()
            if c == b:
                break
            for d in _CARD:
                n = Point(c.x + d.x, c.y + d.y)
                if n not in prev and n not in blocked and grid.walkable(n.x, n.y):
                    prev[n] = c
                    q.append(n)
        if b not in prev:
            return None
        out, c = [], b
        while c is not None:
            out.append(c)
            c = prev[c]
        return out[::-1]

    targets = [Point(keeper.x + dx, keeper.y + dy)
               for dx in (-1, 0, 1) for dy in (-1, 0, 1)
               if (dx or dy) and grid.walkable(keeper.x + dx, keeper.y + dy)
               and Point(keeper.x + dx, keeper.y + dy) not in blocked]
    best = min((path(run.player.pos, t) for t in targets if path(run.player.pos, t)), key=len)
    for a, b in zip(best, best[1:], strict=False):
        run.apply(Move(_CARD[Point(b.x - a.x, b.y - a.y)]))
    return run, run.apply(Talk())


def test_panel_box_is_well_formed_and_does_not_clobber_the_map():
    for cols, rows in [(100, 30), (107, 48), (120, 30)]:
        run, frame = _open_lesson(cols, rows)
        scr = CursesEmu(rows, cols)
        render.draw(scr, frame, page=1)

        top, left, h = windows._geom(rows, cols, frame.map.cols)
        right = left + windows.PANEL_W - 1

        for r in range(top + 1, top + h - 1):
            row = scr.g[r]
            assert row[left] == "║", f"{cols}x{rows}: left border missing at row {r}"
            assert row[right] == "║", f"{cols}x{rows}: right border missing at row {r}"
            # No box character anywhere but the two border columns: a wrap would drop one inside.
            for c in range(cols):
                if c not in (left, right):
                    assert row[c] not in _BOX, \
                        f"{cols}x{rows}: stray {row[c]!r} at row {r} col {c} (a wrapped write?)"

        # The room to the left of the panel survives; nothing spilled over it.
        room_present = any(
            scr.g[y][x] in "-|.@"
            for y in range(1, rows - 3)
            for x in range(0, left)
        )
        assert room_present, f"{cols}x{rows}: the map was clobbered beside the panel"


def test_panel_grows_on_a_taller_terminal_but_holds_at_the_minimum():
    # The 100x30 floor keeps the tuned height (and the pilot lesson's four pages); a taller
    # terminal spends the extra rows on a taller panel, so the same lesson needs fewer pages.
    assert windows._body(30) == windows.BODY_MIN
    assert windows._body(48) > windows._body(30)
    # Constant margin: every terminal row above the floor becomes exactly one panel body row.
    assert windows._body(48) - windows._body(30) == 48 - 30

    _, tall = _open_lesson(120, 48)
    _, short = _open_lesson(100, 30)
    assert windows.page_count(tall.overlay, 48) < windows.page_count(short.overlay, 30)

    # The box height is a function of terminal rows alone, so it does not change as the keeper
    # walks greet -> examine -> explain (no jitter): a menu and a text overlay share one frame.
    _, _, h_text = windows._geom(48, 120, 80)
    assert h_text == windows._body(48) + windows.CHROME


def test_display_width_counts_columns_not_codepoints():
    # A single-codepoint emoji is two terminal columns; Latin text (including é/€) is one each.
    assert windows._width("\U0001F3A3") == 2          # fishing pole
    assert windows._width("abc") == 3
    assert windows._width("café €5") == len("café €5")  # é and € are width 1, same as their length


def test_wrap_keeps_emoji_text_within_the_panel_and_leaves_ascii_untouched():
    import textwrap
    # ASCII wraps byte-for-byte as textwrap did, so every existing lesson is unchanged.
    ascii_text = "the quick brown fox jumps over the lazy dog again and again and again"
    assert windows._wrap(ascii_text, 20) == textwrap.wrap(ascii_text, 20, break_on_hyphens=False)
    # With an emoji, wrapping counts columns, so no line overflows the width (naive len would).
    emoji_text = "spot the \U0001F3A3 in the link " * 6
    lines = windows._wrap(emoji_text.strip(), windows.TEXT_W)
    assert all(windows._width(line) <= windows.TEXT_W for line in lines)


def _grid(picture: str) -> list[list[Cell]]:
    return [[Cell(glyph=ch) for ch in line] for line in picture.splitlines()]


def test_wall_role_reads_corners_edges_and_a_door_from_neighbours():
    # A room with a door ('+') punched into its bottom wall. Corners are carved as '-'; the role
    # must come from the neighbours, not the stored glyph.
    cells = _grid(
        "-----\n"
        "|...|\n"
        "|...|\n"
        "--+--"
    )
    rows, cols = len(cells), len(cells[0])

    def role(y, x):
        return walls.wall_role(cells, y, x, rows, cols)

    assert role(0, 0) == "ul" and role(0, 4) == "ur"      # top corners
    assert role(3, 0) == "ll" and role(3, 4) == "lr"      # bottom corners
    assert role(0, 2) == "hline" and role(3, 1) == "hline"  # top and bottom runs
    assert role(1, 0) == "vline" and role(2, 4) == "vline"  # side runs
    assert role(3, 1) == "hline" and role(3, 3) == "hline"  # the wall runs straight into the door
    assert role(3, 2) is None                              # the door itself stays '+', not a wall
    assert role(1, 2) is None                              # floor is not a wall


def test_acs_for_stands_in_with_ascii_without_a_terminal():
    # ACS_ constants only exist after curses.initscr(), which the test suite never calls, so every
    # role must fall back to a wall-shaped ASCII character rather than raising.
    for r in ("hline", "vline", "ul", "ur", "ll", "lr", "ltee", "rtee", "ttee", "btee", "plus"):
        assert walls.acs_for(r) in ("-", "|", "+")


def test_bar_attr_degrades_to_reverse_without_colour():
    # Colour is never initialised in the suite (no initscr), so the highlight falls back to reverse
    # video, which still makes the Correct./Not quite. line stand out.
    from delve.session.views import Colour
    assert attrs.bar_attr(Colour.GREEN) == curses.A_REVERSE
    assert attrs.bar_attr(Colour.RED) == curses.A_REVERSE


def test_a_highlighted_message_renders_padded_at_the_top():
    from delve.session.views import Colour
    run, frame = _open_lesson(100, 30)
    frame.messages = ["Correct."]
    frame.message_bg = Colour.GREEN
    scr = CursesEmu(30, 100)
    render.draw(scr, frame, page=1)
    assert " Correct. " in scr.row(0)          # padded, so the highlight bar has a margin


_LONG_MSG = ("You peel a sticky note off the underside of a desk. Someone wrote their passphrase "
             "on it. Cleverness is no substitute for a password manager, and you know it.")


def test_message_pages_splits_a_long_line_and_leaves_short_ones_alone():
    # DELVE-0030: a message that fits is one page, unchanged; a longer one is split.
    assert windows.message_pages("A short line.", 100) == ["A short line."]
    assert windows.message_pages("", 100) == [""]
    pages = windows.message_pages(_LONG_MSG, 100)
    assert len(pages) >= 2
    # Every page but the last leaves room for the ' --More--' suffix, and no word is broken.
    for i, p in enumerate(pages):
        suffix = " " + windows.MESSAGE_MORE if i < len(pages) - 1 else ""
        assert windows._width(p + suffix) <= 99
    assert " ".join(pages).split() == _LONG_MSG.split()


def _bare_frame():
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    frame = run.frame()
    assert frame.overlay is None            # the map, no panel: where the message pager applies
    frame.message_bg = None
    return frame


def test_a_long_message_shows_more_then_its_continuation():
    frame = _bare_frame()
    frame.messages = [_LONG_MSG]
    pages = windows.message_pages(_LONG_MSG, 100)
    assert len(pages) >= 2

    scr = CursesEmu(30, 100)
    render.draw(scr, frame, page=1, msg_page=1)
    assert scr.row(0).rstrip().endswith("--More--")     # page one ends with the prompt
    assert pages[0].split()[0] in scr.row(0)

    scr2 = CursesEmu(30, 100)
    render.draw(scr2, frame, page=1, msg_page=2)
    assert pages[1].split()[0] in scr2.row(0)           # the next keypress reveals the rest


def test_a_short_message_never_shows_more():
    frame = _bare_frame()
    frame.messages = ["You open the backpack."]
    scr = CursesEmu(30, 100)
    render.draw(scr, frame, page=1, msg_page=1)
    assert "--More--" not in scr.row(0)


def test_panel_title_and_footer_render():
    run, frame = _open_lesson(100, 30)
    scr = CursesEmu(30, 100)
    render.draw(scr, frame, page=1)
    text = "\n".join(scr.row(r) for r in range(30))
    assert "Recognising a Phish" in text
    assert "(page 1 of 4)" in text


def test_amount_field_renders_as_a_boxed_input():
    scr = CursesEmu(30, 100)
    windows.draw(scr, AmountView(prompt="Drop how many?", typed="30", maximum=70, footer="1 to 70"),
                 map_cols=100, page=1)
    text = "\n".join(scr.row(r) for r in range(30))
    assert "Drop how many?" in text
    assert "30" in text and "1 to 70" in text
    assert "┌" in text and "┘" in text                   # a single-line input field, not a stepper


def test_assertion_renders_as_a_badged_list():
    scr = CursesEmu(30, 100)
    windows.draw(scr, PromptView(text="Slechte spelling?", choices=["Waar", "Niet waar"],
                                 footer="Vraag 2 van 4.", connector="of", selected=0),
                 map_cols=100, page=1)
    text = "\n".join(scr.row(r) for r in range(30))
    assert " w  Waar" in text and " n  Niet waar" in text  # a key badge then label, MCQ-list style
    assert "Vraag 2 van 4." in text                        # the counter footer still shows


def test_quote_block_is_marked_not_a_bare_indent():
    scr = CursesEmu(30, 100)
    view = TextView(title="", body=[TextBlock("quote", "The hurry is the attack.")])
    windows.draw(scr, view, map_cols=100, page=1)
    text = "\n".join(scr.row(r) for r in range(30))
    assert "> The hurry is the attack." in text


def test_info_panel_tab_strip_marks_the_active_tab():
    # DELVE-0041: the active tab is a filled pill (bar_attr), not a bracket marker, and the panel
    # title ("Info") precedes the tab strip.
    scr = CursesEmu(30, 100)
    tabs = [InfoTab("pack", "Pack"), InfoTab("progress", "Progress"), InfoTab("grader", "Grader")]
    view = InfoView(tabs=tabs, active=1, body=[TextBlock("para", "Coming soon.")])
    windows.draw(scr, view, map_cols=100, page=1)
    text = "\n".join(scr.row(r) for r in range(30))
    assert "Info" in text
    assert "[ Progress ]" not in text and "[ Pack ]" not in text   # no bracket marker any more
    assert " Progress " in text and "Pack" in text and "Grader" in text
    assert "Coming soon." in text


def test_scoring_bar_draws_filled_and_empty_glyphs_in_distinct_attrs():
    # DELVE-0043: coloured blocks (filled BRIGHT_CYAN, empty plain), not '#'/'·' ASCII, and the
    # filled/empty runs carry different curses attrs so the bar reads even without colour pairs
    # initialised (CursesEmu never calls attrs.init(), so BRIGHT_CYAN degrades to plain A_BOLD).
    from delve.ui.windows import BAR_EMPTY, BAR_FILLED

    scr = CursesEmu(30, 100)
    tabs = [InfoTab("pack", "Pack"), InfoTab("scoring", "Scoring"), InfoTab("grader", "Grader")]
    bar = TextBlock("bar", "The Vault 60%", bar=("The Vault", 0.6, "60%"))
    view = InfoView(tabs=tabs, active=1, body=[bar])
    windows.draw(scr, view, map_cols=100, page=1)
    text = "\n".join(scr.row(r) for r in range(30))
    assert BAR_FILLED in text and BAR_EMPTY in text
    assert "#" not in text and "·" not in text            # not the old ASCII glyphs

    row = next(r for r in range(30) if BAR_FILLED in scr.row(r))
    line, attr_line = scr.row(row), scr.attr_row(row)
    filled_col = line.index(BAR_FILLED)
    empty_col = line.index(BAR_EMPTY)
    assert attr_line[filled_col] != attr_line[empty_col]
    assert attr_line[filled_col] & curses.A_BOLD           # BRIGHT_CYAN degrades to bold
    assert not (attr_line[empty_col] & curses.A_BOLD)


def test_status_tab_shows_the_live_terminal_size_read_at_paint_time():
    # DELVE-0044: the terminal-size row is a ui-owned fact, filled in from the test harness's own
    # stdscr dimensions at paint time, not staled from anything session built ahead of time.
    scr = CursesEmu(30, 100)
    tabs = [InfoTab("pack", "Pack"), InfoTab("scoring", "Scoring"),
            InfoTab("grader", "Grader"), InfoTab("status", "Status")]
    view = InfoView(tabs=tabs, active=3, body=[TextBlock("plain", "Terminal")])
    windows.draw(scr, view, map_cols=100, page=1)
    text = "\n".join(scr.row(r) for r in range(30))
    assert "Terminal 30x100" in text


def test_status_tab_fills_the_size_row_within_a_condensed_multiline_block():
    # A playtesting fix folded the terminal-size row into the same block as every other Status
    # fact (RunState._status_body always appends it last); `_fill_status_size` must splice the
    # live value into only the block's last line, leaving the earlier lines untouched.
    scr = CursesEmu(30, 100)
    tabs = [InfoTab("pack", "Pack"), InfoTab("scoring", "Scoring"),
            InfoTab("grader", "Grader"), InfoTab("status", "Status")]
    text = "Version 9.9.9\nPack: Test\nTerminal"
    spans = (("Version 9.9.9", False), ("\nPack: Test", False), ("\nTerminal", False))
    view = InfoView(tabs=tabs, active=3, body=[TextBlock("plain", text, spans=spans)])
    windows.draw(scr, view, map_cols=100, page=1)
    rendered = "\n".join(scr.row(r) for r in range(30))
    assert "Version 9.9.9" in rendered
    assert "Pack: Test" in rendered
    assert "Terminal 30x100" in rendered


def test_other_tabs_are_unaffected_by_the_status_size_fill():
    scr = CursesEmu(30, 100)
    tabs = [InfoTab("pack", "Pack"), InfoTab("scoring", "Scoring"),
            InfoTab("grader", "Grader"), InfoTab("status", "Status")]
    view = InfoView(tabs=tabs, active=0, body=[TextBlock("plain", "You are carrying nothing.")])
    windows.draw(scr, view, map_cols=100, page=1)
    text = "\n".join(scr.row(r) for r in range(30))
    assert "You are carrying nothing." in text
    assert "30x100" not in text


# -- Scoring's sub-tab strip (DELVE-0055) ----------------------------------------------------


def _tabs():
    return [InfoTab("pack", "Pack"), InfoTab("scoring", "Scoring"),
            InfoTab("grader", "Grader"), InfoTab("status", "Status")]


def test_sub_tab_row_draws_only_when_subtabs_is_non_empty():
    scr = CursesEmu(30, 100)
    subtabs = [InfoTab("now", "Now"), InfoTab("rooms", "Rooms")]
    view = InfoView(tabs=_tabs(), active=1, body=[TextBlock("plain", "x")],
                    subtabs=subtabs, active_sub=0)
    windows.draw(scr, view, map_cols=100, page=1)
    text = "\n".join(scr.row(r) for r in range(30))
    assert " Now " in text and "Rooms" in text

    scr2 = CursesEmu(30, 100)
    plain_view = InfoView(tabs=_tabs(), active=0, body=[TextBlock("plain", "70 coins")])
    windows.draw(scr2, plain_view, map_cols=100, page=1)
    text2 = "\n".join(scr2.row(r) for r in range(30))
    assert "Now" not in text2 and "Rooms" not in text2


def test_page_count_for_tabs_without_subtabs_is_unchanged_by_this_story():
    # The reserve-row regression this story must not introduce: Pack/Grader/Status carry no
    # subtabs, so their panel height and page count stay byte-for-byte what they were before.
    body = [TextBlock("plain", f"line {i}") for i in range(40)]
    view = InfoView(tabs=_tabs(), active=0, body=body)
    assert windows.page_count(view, 20) == windows.page_count(view, 20)   # stable, no crash
    plain_pages = windows._text_pages(view, 20)
    view_with_empty_subtabs = InfoView(tabs=_tabs(), active=0, body=body, subtabs=[], active_sub=0)
    assert windows._text_pages(view_with_empty_subtabs, 20) == plain_pages


def test_focused_rows_active_tab_is_a_filled_pill_the_other_rows_is_plain():
    # DELVE-0056: the row under keyboard focus draws its active tab as the filled bar_attr pill;
    # the other row's active tab stays visible but plain (bold colour, no fill), so the two rows
    # never look identical and the learner can tell which row the next arrow press will move.
    subtabs = [InfoTab("now", "Now"), InfoTab("rooms", "Rooms")]

    scr = CursesEmu(30, 100)
    view = InfoView(tabs=_tabs(), active=1, body=[TextBlock("plain", "x")],
                    subtabs=subtabs, active_sub=0, sub_focus=False)   # primary row focused
    windows.draw(scr, view, map_cols=100, page=1)
    primary_row = next(r for r in range(30) if " Scoring " in scr.row(r))
    primary_col = scr.row(primary_row).index(" Scoring ")
    sub_row = next(r for r in range(30) if "Now" in scr.row(r))
    sub_col = scr.row(sub_row).index("Now")
    assert scr.attr_row(primary_row)[primary_col] & curses.A_REVERSE   # focused: filled pill
    assert not (scr.attr_row(sub_row)[sub_col] & curses.A_REVERSE)     # unfocused: no fill
    assert scr.attr_row(sub_row)[sub_col] & curses.A_BOLD              # unfocused: still coloured

    scr2 = CursesEmu(30, 100)
    view2 = InfoView(tabs=_tabs(), active=1, body=[TextBlock("plain", "x")],
                     subtabs=subtabs, active_sub=0, sub_focus=True)    # sub-tab row focused
    windows.draw(scr2, view2, map_cols=100, page=1)
    primary_row2 = next(r for r in range(30) if "Scoring" in scr2.row(r))
    primary_col2 = scr2.row(primary_row2).index("Scoring")
    sub_row2 = next(r for r in range(30) if " Now " in scr2.row(r))
    sub_col2 = scr2.row(sub_row2).index(" Now ")
    assert not (scr2.attr_row(primary_row2)[primary_col2] & curses.A_REVERSE)  # unfocused now
    assert scr2.attr_row(sub_row2)[sub_col2] & curses.A_REVERSE               # focused now


def test_tab_with_no_subtabs_renders_exactly_as_before_this_story():
    scr = CursesEmu(30, 100)
    view = InfoView(tabs=_tabs(), active=0, body=[TextBlock("plain", "70 coins")])
    windows.draw(scr, view, map_cols=100, page=1)
    text = "\n".join(scr.row(r) for r in range(30))
    active_row = next(r for r in range(30) if " Pack " in scr.row(r))
    active_col = scr.row(active_row).index(" Pack ")
    assert scr.attr_row(active_row)[active_col] & curses.A_REVERSE
    assert "70 coins" in text


def test_rooms_body_stays_within_text_width_for_the_pilot_packs_largest_chapter():
    from pathlib import Path

    from delve import strings as strings_pkg
    from delve.content.parser import load_pack
    from delve.session.launch import load_tutorial
    from delve.session.run import new_game

    pilot = Path(__file__).resolve().parent.parent / "packs" / "security-onboarding"
    pack = load_pack(pilot, "en")
    tutorial = load_tutorial("en")
    strings = strings_pkg.load("en")
    run = new_game(pack, seed=7, cols=100, rows=30, name="Ada", strings=strings,
                  tutorial=tutorial, skip_tutorial=True, pet_species="none")
    body = run._scoring_rooms_body()
    # Condensed into one block (DELVE-0059): each line must still individually fit, since a
    # Dlvl/glyph row wrapping mid-string would be visually broken.
    for block in body:
        for line in block.text.split("\n"):
            assert windows._width(line) <= windows.TEXT_W


def test_bold_run_survives_wrapping():
    from delve.ui.windows import _wrap_spans
    lines = _wrap_spans((("a ", False), ("strong", True), (" tail", False)), 40)
    flat = [seg for line in lines for seg in line]
    assert ("strong", True) in flat            # the bold run stays its own strong segment


def test_table_lays_out_aligned_columns():
    from delve.ui.windows import _layout_table
    rows = (
        ((("Factor", True),), (("Verdict", True),)),
        ((("SMS", False),), (("Weak but real, long enough that this cell wraps.", False),)),
    )
    lines = _layout_table(rows, 40)
    widths = {sum(len(t) for t, _ in segs) for _, segs in lines}
    assert len(widths) == 1                    # every row the same width, so the columns align
    assert any("│" in t for _, segs in lines for t, _ in segs)   # a column separator is drawn


def test_toast_anchors_right_when_the_learner_is_on_the_left():
    from delve.session.views import ToastView
    view = ToastView(title="The Porter", body=[TextBlock("para", "Dust settles in the quiet.")])
    scr = CursesEmu(30, 100)
    windows.draw_toast(scr, view, map_cols=100, player_x=10)
    assert "".join(scr.g[windows.TOAST_TOP]).strip().startswith(("╔",))
    assert scr.g[windows.TOAST_TOP].index("╔") > 50   # right half of the screen


def test_toast_anchors_left_when_the_learner_is_on_the_right():
    """The regression this guards: a fixed right-anchored toast overlaid a room the learner was
    standing in (reported against the tutorial's second room, further right in its layout)."""
    from delve.session.views import ToastView
    view = ToastView(title="The Porter", body=[TextBlock("para", "Dust settles in the quiet.")])
    scr = CursesEmu(30, 100)
    windows.draw_toast(scr, view, map_cols=100, player_x=80)
    assert scr.g[windows.TOAST_TOP].index("╔") == 0   # flush against the left edge


def test_toast_anchor_flips_exactly_at_the_screen_midpoint():
    from delve.session.views import ToastView
    view = ToastView(title="t", body=[TextBlock("para", "x")])
    scr = CursesEmu(30, 100)
    windows.draw_toast(scr, view, map_cols=100, player_x=49)   # just left of centre
    right_left = scr.g[windows.TOAST_TOP].index("╔")
    scr2 = CursesEmu(30, 100)
    windows.draw_toast(scr2, view, map_cols=100, player_x=50)  # at/past centre
    left_left = scr2.g[windows.TOAST_TOP].index("╔")
    assert right_left > left_left == 0


def test_player_x_distinguishes_the_learner_from_a_keeper_drawn_the_same_glyph():
    from delve.session.views import Cell, Colour, MapView
    from delve.ui.render import _player_x
    cells = [[Cell(" ", Colour.BLACK) for _ in range(10)] for _ in range(3)]
    cells[1][3] = Cell("@", Colour.BRIGHT_MAGENTA)   # a keeper, further left
    cells[1][7] = Cell("@", Colour.WHITE)            # the learner, further right
    assert _player_x(MapView(cols=10, rows=3, cells=cells)) == 7


def test_line_edit_types_backspaces_submits_and_cancels():
    from delve.ui.app import _line_edit
    assert _line_edit("", "A", 20) == ("A", "edit")
    assert _line_edit("Ad", "a", 20) == ("Ada", "edit")
    assert _line_edit("Ada", "\x7f", 20) == ("Ad", "edit")            # backspace as DEL
    assert _line_edit("Ada", curses.KEY_BACKSPACE, 20) == ("Ad", "edit")   # ...or as a key code
    assert _line_edit("Ada", "\n", 20)[1] == "submit"
    assert _line_edit("Ada", "\x1b", 20)[1] == "cancel"               # Esc
    assert _line_edit("12345", "6", 5) == ("12345", "edit")           # clamped at max_len
    assert _line_edit("Zo", "ë", 20) == ("Zoë", "edit")               # accented char accepted


# -- Pack tab's two-column list-plus-description layout (DELVE-0075) ------------------------------


def test_pack_view_draws_the_list_and_the_selected_rows_description_side_by_side():
    scr = CursesEmu(30, 100)
    body = [TextBlock("para", "torch look\nA hand torch.", spans=(("torch look", True),
                                                                  ("\nA hand torch.", False)))]
    view = InfoView(tabs=_tabs(), active=0, body=body,
                    pack_rows=["torch look", "70 coins"], pack_selected=0)
    windows.draw(scr, view, map_cols=100, page=1)
    text = "\n".join(scr.row(r) for r in range(30))
    assert "torch look" in text and "70 coins" in text     # both list rows
    assert "A hand torch." in text                          # the focused row's description


def test_pack_views_focused_list_row_is_highlighted_and_the_description_title_is_styled():
    # DELVE-0076 reversed DELVE-0075's original placement so the list row, not the description,
    # carries the reverse-video highlight; DELVE-0078 restored the description title's own bold
    # styling, which had been silently flattened to plain text. "gadget" appears both as the
    # list's own row label and as the description's bold title, so they land on the same drawn row
    # (the list column, then the description column beside it), letting one row check both.
    scr = CursesEmu(30, 100)
    body = [TextBlock("para", "gadget\nAn urgent memo.", spans=(("gadget", True),
                                                                ("\nAn urgent memo.", False)))]
    view = InfoView(tabs=_tabs(), active=0, body=body, pack_rows=["gadget", "70 coins"],
                    pack_selected=0)
    windows.draw(scr, view, map_cols=100, page=1)
    row = next(r for r in range(30) if scr.row(r).count("gadget") == 2)
    list_col = scr.row(row).index("gadget")
    desc_col = scr.row(row).rindex("gadget")
    assert scr.attr_row(row)[list_col] != curses.A_NORMAL     # the list row is highlighted
    assert scr.attr_row(row)[desc_col] != curses.A_NORMAL     # the description title is styled too
    body_row = next(r for r in range(30) if "An urgent memo." in scr.row(r))
    body_col = scr.row(body_row).index("An urgent memo.")
    assert scr.attr_row(body_row)[body_col] == curses.A_NORMAL   # the description body stays plain


def test_pack_view_scrolls_the_list_to_keep_a_far_focused_row_in_view():
    scr = CursesEmu(30, 100)
    rows = [f"item{i}" for i in range(20)]
    body = [TextBlock("para", "item19", spans=(("item19", True),))]
    view = InfoView(tabs=_tabs(), active=0, body=body, pack_rows=rows, pack_selected=19)
    windows.draw(scr, view, map_cols=100, page=1)
    text = "\n".join(scr.row(r) for r in range(30))
    assert "item19" in text                # the focused row scrolled into view
    assert "item0 " not in text and "item0\n" not in text   # the far-off top of the list is not


def test_pack_scroll_offset_keeps_selection_in_view_and_never_overscrolls():
    assert windows._pack_scroll_offset(0, 5, 10) == 0        # fits entirely: no scroll
    assert windows._pack_scroll_offset(9, 20, 5) == 5         # bottom-pinned once past the window
    assert windows._pack_scroll_offset(0, 20, 5) == 0         # back at the top: no scroll
    assert windows._pack_scroll_offset(19, 20, 5) == 15       # never scrolls past the list's end


# -- 'kv' blocks: label/value colouring (DELVE-0078) ----------------------------------------------


def test_kv_spans_colours_the_label_up_to_the_first_colon_space():
    spans = windows._kv_spans("Model: qwen2.5:3b @ localhost:11434")
    assert spans[0] == ("Model:", windows.LABEL_COLOUR)
    assert spans[1] == (" qwen2.5:3b @ localhost:11434", False)


def test_kv_spans_only_splits_on_the_first_colon_space_even_with_more_in_the_value():
    # Neither "qwen2.5:3b" nor "localhost:11434" has a space right after its colon, so only the
    # label's own "Model: " counts as the separator.
    spans = windows._kv_spans("Status: warm, last grade 520 ms")
    assert spans[0][1] is windows.LABEL_COLOUR
    assert "warm" in spans[1][0] and spans[1][1] is False


def test_kv_spans_leaves_a_colonless_line_unstyled():
    assert windows._kv_spans("no colon here") == (("no colon here", False),)


def test_kv_spans_handles_multiple_newline_joined_lines():
    spans = windows._kv_spans("Model: x\nStatus: y")
    labels = [t for t, c in spans if c is windows.LABEL_COLOUR]
    assert labels == ["Model:", "\nStatus:"]


def test_a_kv_block_renders_its_label_in_colour_and_its_value_plain():
    scr = CursesEmu(30, 100)
    body = [TextBlock("kv", "Model: qwen2.5:3b")]
    view = InfoView(tabs=_tabs(), active=0, body=body)
    windows.draw(scr, view, map_cols=100, page=1)
    row = next(r for r in range(30) if "Model:" in scr.row(r))
    label_col = scr.row(row).index("Model:")
    value_col = scr.row(row).index("qwen2.5:3b")
    assert scr.attr_row(row)[label_col] == attrs.attr_for(windows.LABEL_COLOUR)
    assert scr.attr_row(row)[value_col] == curses.A_NORMAL
