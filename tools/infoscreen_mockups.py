#!/usr/bin/env python3
"""Design mock-ups for DELVE-0035 (the tabbed information screen), not yet built.

    python tools/infoscreen_mockups.py            # print every mock-up
    python tools/infoscreen_mockups.py --check     # assert geometry, print nothing

Reuses the drawing primitives from tools/screens.py (the real, generated-and-asserted M2 slice
evidence) so these mock-ups sit on the same 100x30 grid and the same geometry assertions, but they
are kept out of all_screens()/SCREENS.md on purpose: SCREENS.md is evidence of what is built, and
these tabs do not exist yet. This script exists so DELVE-0035's proposed screens are pasted into
the issue the same disciplined way, not hand-drawn free-hand ASCII that could silently drift from
the panel width or line-length rules the real screens already enforce.
"""
import argparse

from screens import (
    LW_LEFT,
    LW_W,
    MAP_ROWS,
    MAP_TOP,
    W,
    blank,
    box,
    chapter_1_floor,
    check,
    put,
    render,
    status,
)

TEXT_COL = LW_LEFT + 2
TEXT_W = LW_LEFT + LW_W - 2 - TEXT_COL      # 69, same inner width as the lesson panel


def _panel(g, height, tab_rows, body, msg, hint, rooms=(2, 3), gold=70, turn=118):
    """The proposed InfoView chrome: tab strip, sub-tab strip, body, (end)."""
    chapter_1_floor(g, revealed=2)
    put(g, 13, 24, '@')                  # Ada
    put(g, 13, 22, '@')                  # you
    put(g, 0, 0, msg)
    top = MAP_TOP + (MAP_ROWS - height) // 2
    box(g, top, LW_LEFT, height, LW_W)
    for i, line in enumerate(tab_rows):
        assert len(line) <= TEXT_W, f'tab row: {len(line)} > {TEXT_W}: {line!r}'
        put(g, top + 1 + i, TEXT_COL, line)
    for i, line in enumerate(body):
        assert len(line) <= TEXT_W, f'body: {len(line)} > {TEXT_W}: {line!r}'
        put(g, top + 2 + len(tab_rows) + i, TEXT_COL, line)
    put(g, top + height - 3, TEXT_COL, '(end)')
    status(g, rooms=rooms, gold=gold, turn=turn, hint=hint)
    return g


HINT_TABS = 'Tabs: left/right   Rows: up/down   Put away: Esc'


def screen_info_pack():
    """Tab 1 (default): the pack, unchanged in content, now inside the tab strip."""
    g = blank()
    tab_rows = ['[ Pack ]  Scoring  Grader']
    body = ['70 coins']
    _panel(g, 10, tab_rows, body, 'You look through your pack.', HINT_TABS)
    return check(g, 'info-pack')


def screen_info_progress_now():
    """Tab 2, sub-tab 1: horizontal bars for score per chapter and HP (INFOSCREEN.md 6.1)."""
    g = blank()
    tab_rows = ['Pack  [ Scoring ]  Grader', '       [ Now ]  Rooms  History']
    body = [
        '',
        ' Chapters',
        ' 1 Sorting office   ####################········  92%',
        ' 2 The archive      ##############··············  71%',
        ' 3 The vault        ····························   n/a',
        ' HP                 ############········  12/12',
    ]
    _panel(g, 13, tab_rows, body, 'You check your progress.', HINT_TABS)
    return check(g, 'info-progress-now')


def screen_info_progress_rooms():
    """Tab 2, sub-tab 2: the room pass map (INFOSCREEN.md 6.4A, shipped DELVE-0055). One row per
    scored chapter ('Dlvl {n}', never translated, then one glyph per room in gate order), then a
    legend line of its own; four glyphs only (no in-between 'ok, but slower' shade), unlike this
    file's earlier design sketch."""
    g = blank()
    tab_rows = ['Pack  [ Scoring ]  Grader', '       Now  [ Rooms ]  History']
    body = [
        'Dlvl 1  ░░██▒▒██░░░░',
        'Dlvl 2  ░░▒▒░░░░····',
        'Dlvl 3  ············',
        '· sealed   ░ sat   ▒ ok   █ clear',
    ]
    _panel(g, 12, tab_rows, body, 'You check your progress.', HINT_TABS)
    return check(g, 'info-progress-rooms')


def screen_info_grader_live():
    """Tab 3, sub-tab 1: local grader status (INFOSCREEN.md 7)."""
    g = blank()
    tab_rows = ['Pack  Scoring  [ Grader ]', '                 [ Live ]  Run']
    body = [
        '',
        '  Model     qwen2.5:3b @ localhost:11434',
        '  Status    warm . last grade 520 ms',
        '  This run  In 2.1k   Out 480   LLM 7   keyword 1',
        '',
        '  Latency   ▁▁▂▃▂▁▄█▂▁  (sittings)',
        '',
        '  Below 0.65 confidence falls to keywords; that is normal.',
    ]
    _panel(g, 15, tab_rows, body, 'You check the grader.', HINT_TABS)
    return check(g, 'info-grader-live')


def all_mockups():
    return [
        ('A. Pack (default tab)', screen_info_pack()),
        ('B. Scoring > Now', screen_info_progress_now()),
        ('C. Scoring > Rooms', screen_info_progress_rooms()),
        ('D. Grader > Live', screen_info_grader_live()),
    ]


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true', help='assert geometry, print nothing')
    args = ap.parse_args()
    mockups = all_mockups()
    if args.check:
        print(f'ok: {len(mockups)} mock-ups, all exactly {W}x{MAP_ROWS + 3}')
        raise SystemExit
    for name, g in mockups:
        print(f'\n===== {name} =====')
        print(render(g))
