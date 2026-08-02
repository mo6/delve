#!/usr/bin/env python3
"""Generate the screen mock-ups in docs/SCREENS.md.

    python tools/screens.py            # all screens
    python tools/screens.py --check    # geometry assertions only, no output

Not part of the delve package and not imported by it. This exists so the mock-ups are
*generated and verified* rather than hand-drawn: every frame is asserted to be exactly
100x30, and every line of prose is asserted to fit its window. Three real bugs were found
by the assertions alone (see docs/SCREENS.md section 8).

Prose, questions and explanations are verbatim from packs/security-onboarding/.
When the design changes, change it here and re-paste into docs/SCREENS.md.
"""
import argparse
import datetime as dt
import textwrap

W, H = 100, 30
MAP_TOP, MAP_ROWS = 1, 27          # row 0 = message, rows 1..27 = map, rows 28..29 = status

# ---------------------------------------------------------------------------- locale data
# Everything here is per-locale data, not code. In the engine this lives in
# delve/strings/{en,nl}.toml under [format]; see PLAN.md section 8.
LOCALES = {
    'en': {
        'player':     'George the Novice',
        'rooms':      'Rooms',
        'currency':   '$',
        'decimal':    '.',
        'thousands':  ',',
        'months':     ['January', 'February', 'March', 'April', 'May', 'June', 'July',
                       'August', 'September', 'October', 'November', 'December'],
        'date':       '{d} {month} {y}',
        'pack':       'The Caverns of Compliance',
    },
    'nl': {
        'player':     'George de Beginner',
        'rooms':      'Kamers',
        'currency':   '€',                     # EURO SIGN
        'decimal':    ',',
        'thousands':  '.',
        # Dutch month names are lower case. This is a real rule, not a style preference,
        # and it is the same family as "sentence case in headings" (STYLE.md).
        'months':     ['januari', 'februari', 'maart', 'april', 'mei', 'juni', 'juli',
                       'augustus', 'september', 'oktober', 'november', 'december'],
        'date':       '{d} {month} {y}',
        'pack':       'De grotten der naleving',
    },
}


def fmt_date(loc, d):
    f = LOCALES[loc]
    return f['date'].format(d=d.day, month=f['months'][d.month - 1], y=d.year)


def fmt_num(loc, value, places=0):
    """1234.5 -> '1,234.5' (en) / '1.234,5' (nl)."""
    f = LOCALES[loc]
    whole, _, frac = f'{value:,.{places}f}'.partition('.')
    whole = whole.replace(',', '\x00').replace('\x00', f['thousands'])
    return whole + (f['decimal'] + frac if frac else '')


def fmt_money(loc, value):
    f = LOCALES[loc]
    # Dutch convention puts a space after the symbol; English does not.
    sep = ' ' if loc == 'nl' else ''
    return f['currency'] + sep + fmt_num(loc, value)


# ---------------------------------------------------------------------------- grid helpers
def blank():
    return [[' '] * W for _ in range(H)]


def put(g, r, c, s):
    for i, ch in enumerate(s):
        g[r][c + i] = ch


# Borders. Delve targets English and Dutch environments only (PLAN section 8), which is what
# makes these safe: every one of them is East Asian *Ambiguous* width, i.e. one cell in a
# Western terminal and two in a CJK-configured one. Outside CJK they are single-cell.
#
# Room walls are drawn with curses' ACS_* alternate character set (ACS_HLINE, ACS_ULCORNER,
# ...), which curses maps per terminal itself -- no Unicode, no code page, no font bet, and
# PDCurses provides the same names. The Unicode below is only how it *looks*; a Markdown file
# cannot show ACS. Window frames use double-line, which has no ACS equivalent and is therefore
# a genuine Unicode bet -- acceptable under the en/nl scoping, and it keeps a window frame
# instantly distinguishable from a room wall. See SCREENS section 9.
ROOM = {'h': '─', 'v': '│', 'tl': '┌', 'tr': '┐', 'bl': '└', 'br': '┘'}   # ACS_* single line
WIN = {'h': '═', 'v': '║', 'tl': '╔', 'tr': '╗', 'bl': '╚', 'br': '╝'}    # Unicode double line


def _frame(g, top, left, h, w, s, fill):
    put(g, top, left, s['tl'] + s['h'] * (w - 2) + s['tr'])
    put(g, top + h - 1, left, s['bl'] + s['h'] * (w - 2) + s['br'])
    for r in range(top + 1, top + h - 1):
        g[r][left] = s['v']
        g[r][left + w - 1] = s['v']
        for c in range(left + 1, left + w - 1):
            g[r][c] = fill


def room(g, top, left, h, w):
    _frame(g, top, left, h, w, ROOM, '.')


def box(g, top, left, h, w):
    _frame(g, top, left, h, w, WIN, ' ')


# The second status line is the hint line. It is contextual: it names the keys that do
# something *right now*. This is the row SCREENS 8.8 said was being wasted on a lonely
# name -- "later should be named, or it's a row spent on nothing". This is later.
#
# It matters most for the learner who skipped the tutorial, who otherwise gets no interface
# teaching at all. PLAN 3: the audience is not developers, in an app most people run once.
HINTS = {
    'en': {
        'walk':   'Move: arrows    Talk: t    Look: ;    Help: ?    Quit: Q',
        'talk':   'Talk to Ada: t          Move: arrows              Help: ?',
        'read':   'Next page: space        Back: -            Put it down: Esc',
        'answer': 'Answer: 1-4    Ask companion: @    Eliminate ($33): $    Put it down: Esc',
        'more':   'Continue: space',
        'door':   'Move: arrows    The door is a + . Walk through it.',
        'stairs': 'Descend: >              Move: arrows              Help: ?',
        'scroll': 'Read it again: r        Trophy case: #trophies            Finish: Q',
        'repelled': 'Read it again: t        Ask your kitten: ?   Rest: s        Help: ?',
        'coins':  'Move: arrows    Coins ($) collect when you step on them.',
        'inventory': 'Tabs: arrows or Tab     Put away: Esc',
        'drop':   'Type a number   Backspace: fix   Drop: Enter   Cancel: Esc',
        'help':   'Tabs: Tab or arrows     Put away: ? or Esc',
    },
    'nl': {
        'answer': 'Antwoord: w of n        Vraag je katje: ?    Leg het weg: Esc',
        'scroll': 'Lees opnieuw: r         Prijzenkast: #trofeeen            Klaar: Q',
    },
}


def status(g, loc='en', dlvl=1, rooms=(0, 3), gold=0, hp=(12, 12), turn=14, hint=''):
    f = LOCALES[loc]
    line = (f"{f['player']}   Dlvl:{dlvl}  {f['rooms']}:{rooms[0]}/{rooms[1]}  "
            f"{f['currency']}:{fmt_num(loc, gold)}  HP:{hp[0]}({hp[1]})  T:{turn}")
    assert len(line) <= W, f'status: {len(line)} > {W}'
    assert len(hint) <= W, f'hint: {len(hint)} > {W}'
    put(g, 28, 0, line)
    put(g, 29, 0, hint)


def chapter_1_room_1(g):
    """3 rooms -> 3x1 partition; 100x27 map / 3 = 33x27 cells clamped to 33x15 (PLAN 7)."""
    room(g, 9, 4, 9, 22)                 # rows 9-17, cols 4-25
    put(g, 11, 7, '<')                   # up to the tutorial floor


def chapter_1_floor(g, revealed):
    """The real chapter-1 layout, revealed as far as the learner has earned.

    Cells are cols 0-32 / 33-65 / 66-98 and grid rows 7-21 (33x15 after the clamp). Rooms
    are jittered inside their cell. Serpentine order is left to right, so corridors are the
    L-shapes carved between consecutive cells -- there is no spanning tree and no reroll:
    a chain is connected by construction (PLAN 7).

    `revealed` is how many rooms the learner has reached. Everything beyond is not drawn,
    because it does not exist yet: the door out of room N is solid stone until its keeper is
    satisfied, so there is nothing to render and nothing to walk past.
    """
    chapter_1_room_1(g)
    if revealed >= 2:
        put(g, 13, 25, '+')                          # room 1's earned door
        for c in range(26, 33):
            g[13][c] = '#'
        for c in range(32, 38):
            g[12][c] = '#'
        room(g, 8, 38, 9, 25)                        # room 2: rows 8-16, cols 38-62
        put(g, 12, 38, '+')
    if revealed >= 3:
        put(g, 12, 62, '+')                          # room 2's earned door
        for c in range(63, 67):
            g[12][c] = '#'
        for r in range(12, 15):
            g[r][66] = '#'
        for c in range(66, 70):
            g[14][c] = '#'
        room(g, 10, 70, 9, 25)                       # room 3: rows 10-18, cols 70-94
        put(g, 14, 70, '+')


def check(g, name):
    assert len(g) == H, f'{name}: {len(g)} rows, want {H}'
    for i, r in enumerate(g):
        assert len(r) == W, f'{name}: row {i} is {len(r)} cols, want {W}'
    return g


def render(g):
    return '\n'.join(''.join(r).rstrip() for r in g)


def wrap(text, width):
    # break_on_hyphens=False: textwrap splits "yourcompany-hr.net" across lines, mangling
    # the one string the lesson is about. Domains are content, not prose. See SCREENS 8.2.
    return textwrap.wrap(text, width, break_on_hyphens=False)


# ------------------------------------------------------------------- 0: the tutorial floor
# Dlvl 0. The actual first screen a learner sees -- PLAN 9. Two rooms, so a 2x1 partition;
# cells clamp to 40x15, so 80 wide centred, cols 10-49 / 50-89.
#
# The Porter's panel sits right of room 1, which leaves it 66 columns rather than the 73 it
# gets in chapter 1: the panel takes whatever space the room leaves. See SCREENS 8.2.
TUT_LEFT, TUT_W = 34, 66
TUT_COL = TUT_LEFT + 2
TUT_TEXT_W = TUT_LEFT + TUT_W - 2 - TUT_COL      # 62

PORTER = [
    ('para', 'The Porter watches you walk the last few steps toward him and seems satisfied '
             'by something.'),
    ('para', '"There. You\'ve already learned the hard part, and nobody had to tell you. You '
             'wanted to be over here, so you came over here."'),
    ('para', 'That\'s movement. The arrow keys: up, down, left, right. You\'ve been doing it '
             'for ten seconds.'),
    ('para', '"The rest is just knowing where to look. Four parts."'),
    ('para', 'The top line is the message line. It tells you what just happened. When '
             'something matters, it appears there, and only there.'),
]


def screen_tutorial(page=1):
    body, pages = fit(blocks_for(PORTER, TUT_TEXT_W))
    h = body + CHROME
    top = MAP_TOP + (MAP_ROWS - h) // 2
    g = blank()
    room(g, 9, 12, 9, 21)                            # room 1: rows 9-17, cols 12-32
    put(g, 13, 31, '@')                              # The Porter, beside his sealed exit
    put(g, 13, 29, '@')                              # you
    put(g, 14, 28, 'f')
    put(g, 0, 0, 'The Porter looks you over. "First time? Then look down, and I will explain."')
    box(g, top, TUT_LEFT, h, TUT_W)
    r = top + 2
    if page == 1:
        put(g, r, TUT_COL, "What You're Looking At")
        r += 2
    for line in pages[page - 1]:
        assert len(line) <= TUT_TEXT_W, f'porter: {len(line)} > {TUT_TEXT_W}: {line!r}'
        put(g, r, TUT_COL, line)
        r += 1
    assert r <= top + h - 2, f'porter p{page}: body reached {r}, --More-- is {top + h - 2}'
    tail = '--More--' if page < len(pages) else '(end)'
    put(g, top + h - 2, TUT_COL, tail.ljust(TUT_TEXT_W - 14) + f'(page {page} of {len(pages)})')
    status(g, dlvl=0, rooms=(0, 2), hint=HINTS['en']['read'])
    return check(g, 'tutorial')


# ---------------------------------------------------------------------------- 1 / 6: the map
def screen_map(door=False):
    g = blank()
    chapter_1_room_1(g)
    put(g, 13, 24, '@')                  # Ada, beside her sealed exit
    if door:
        put(g, 13, 25, '+')              # the earned door: the entire progression mechanic
        put(g, 13, 20, '@')
        put(g, 13, 19, 'f')
        put(g, 0, 0, 'The wall grinds. Where there was stone, there is a door.')
        status(g, rooms=(1, 3), hint=HINTS['en']['door'])
    else:
        put(g, 15, 12, '@')
        put(g, 16, 11, 'f')
        put(g, 0, 0, 'Ada the Suspicious does not look up. There is no way out of this room.')
        status(g, hint=HINTS['en']['walk'])
    return check(g, 'map')


# ---------------------------------------------------------- 2 rooms / whole floor
def screen_two_rooms():
    """Mid-chapter: room 1 cleared and remembered, room 2 lit, room 3 does not exist yet."""
    g = blank()
    chapter_1_floor(g, revealed=2)
    put(g, 13, 24, '@')                  # Ada, still in room 1, still teaching
    put(g, 12, 61, '@')                  # Grigor, beside room 2's sealed exit
    put(g, 12, 59, '@')                  # you
    put(g, 13, 58, 'f')
    put(g, 0, 0, 'Grigor, Who Was Impersonated, looks up. There are two nameplates on his desk.')
    status(g, rooms=(1, 3), hint=HINTS['en']['talk'].replace('Ada', 'Grigor'))
    return check(g, 'two-rooms')


def screen_floor_complete():
    """All three keepers satisfied: the whole chain, and the stairs down."""
    g = blank()
    chapter_1_floor(g, revealed=3)
    put(g, 13, 24, '@')                  # Ada
    put(g, 12, 61, '@')                  # Grigor
    put(g, 14, 93, '@')                  # Marisol, beside the stairs she was guarding
    put(g, 16, 90, '>')                  # earned: the way down to Dlvl 2
    put(g, 16, 88, '@')                  # you
    put(g, 17, 87, 'f')
    put(g, 0, 0, 'A staircase grinds open in the floor. You have finished the Sorting Office.')
    status(g, rooms=(3, 3), hint=HINTS['en']['stairs'])
    return check(g, 'floor-complete')


# ----------------------------------------------------------------- objects: money (OBJECTS.md)
# Phase-2 money made real: passing a room drops coins on the way onward (the door the pass just
# opened), and they bank the moment you step on the tile, so the dead $:0 in the status line finally
# has a source. You can open your pack and set coins down again, item by item.
#
# The pack panel holds only money today; pack-authored carriables (the Holy Grail coconuts) arrive
# at 1.3.0 and will fill it then. The two overlays sit right of room 1 (cols 4-25 stay visible), the
# same "a panel beside the room, never a takeover" discipline as the keeper's panel.
OBJ_LEFT, OBJ_W = 54, 44
OBJ_COL = OBJ_LEFT + 2
OBJ_TEXT_W = OBJ_W - 4                    # 40


def _obj_panel(g, title, lines, msg):
    """A small right-anchored overlay (the pack, a prompt), room 1 still in view to its left."""
    chapter_1_room_1(g)
    put(g, 13, 24, '@')                  # Ada
    put(g, 13, 22, '@')                  # you
    put(g, 14, 21, 'f')
    put(g, 0, 0, msg)
    h = len(lines) + 6
    top = MAP_TOP + (MAP_ROWS - h) // 2
    box(g, top, OBJ_LEFT, h, OBJ_W)
    put(g, top + 2, OBJ_COL, title)
    for i, line in enumerate(lines):
        assert len(line) <= OBJ_TEXT_W, f'obj: {len(line)} > {OBJ_TEXT_W}: {line!r}'
        put(g, top + 4 + i, OBJ_COL, line)
    return g


def screen_reward():
    """A room just passed: the keeper leaves coins on the floor of the room, away from the exit, so
    collecting them is a detour (and, once the pet roams, a coin it could reach first). A real `$`
    stack on the tile, glinting on the map until a step banks it (auto-collected, no key)."""
    g = blank()
    chapter_1_room_1(g)
    put(g, 13, 24, '@')                  # Ada, satisfied
    put(g, 13, 25, '+')                  # the door she just opened
    put(g, 15, 8, '$')                   # the reward, dropped in the room, away from the exit
    put(g, 13, 22, '@')                  # you, still by the keeper
    put(g, 14, 21, 'f')
    put(g, 0, 0, 'Ada the Suspicious leaves 20 coins on the floor.')
    status(g, rooms=(1, 3), gold=0, hint=HINTS['en']['coins'])
    return check(g, 'reward')


def screen_inventory():
    """The pack (i): read-only, a count per kind. Money reads as "70 coins" here while the status
    line shows it as `$:70`, natural language in the pack, the currency mark in the ledger.
    DELVE-0040 grew the plain "Your pack" title into a primary tab strip (Pack/Scoring/Grader)
    named by a fixed "Info" title (DELVE-0041); Pack is the default tab and keeps this exact
    content, so the header row changes but the coin line below it does not. The active tab is a
    coloured pill on a real terminal (DELVE-0041); this plain-ASCII mock-up cannot show that, only
    the title and tab words."""
    g = blank()
    _obj_panel(g, 'Info   Pack  Scoring  Grader', ['70 coins'], 'You look through your pack.')
    status(g, rooms=(2, 3), gold=70, turn=52, hint=HINTS['en']['inventory'])
    return check(g, 'inventory')


def screen_help():
    """The ? help overlay (DELVE-0028): the same right-anchored panel as the pack (i), with its
    own two-tab strip (Keys / Objectives) instead of Pack/Scoring/Grader. Keys (shown here, the
    default tab) lists every key active in the current context, each with its explanation; a
    second `?` or Esc puts it away and hands back whatever was open before (here, nothing: the
    learner opened it while walking)."""
    g = blank()
    _obj_panel(g, 'Help   Keys  Objectives', [
        'arrows: Move around the room',
        't: Talk to (or re-read) a keeper',
        's: Rest until your HP is full',
        ',: Pick up whatever is on your tile',
        'd: Drop something from your pack',
        'i: Open your pack and progress',
        '?: Open or close this help',
        'q: Quit',
    ], 'You wonder what you can do here.')
    status(g, rooms=(0, 3), hint=HINTS['en']['help'])
    return check(g, 'help')


def screen_toast():
    """The ambient room-entry toast (DELVE-0060): a small, top-anchored block, deliberately *not*
    vertically centred like every blocking panel above (the lesson, the pack, Help), so it reads
    as ambient weather over the room rather than a panel the room is paused for. Unlike every
    other screen here, nothing about the frame is paused for it: the hint line still reads exactly
    as an ordinary walking frame, because the toast is independent of `Frame.overlay` and never
    blocks movement, talk, or opening a panel. It appears once its background call resolves
    (replacing DELVE-0028/0057's single once-per-run passage, which used to sit on the Objectives
    tab's page 2, easy to miss) and fades on its own a few turns later."""
    g = blank()
    chapter_1_room_1(g)
    put(g, 13, 22, '@')
    put(g, 14, 21, 'f')
    put(g, 0, 0, 'You step into the room.')
    lines = [
        'Dust motes drift through the dim',
        'afternoon light as ledgers stack in',
        'uneven towers, waiting for someone',
        'patient enough to set them straight.',
    ]
    h = 4 + len(lines)
    left, w = 54, 44
    col = left + 2
    box(g, 2, left, h, w)
    put(g, 3, col, 'The Archive')
    for i, line in enumerate(lines):
        put(g, 5 + i, col, line)
    status(g, rooms=(1, 3), gold=70, turn=119, hint=HINTS['en']['walk'])
    return check(g, 'toast')


def screen_drop_amount():
    """Dropping coins (d): a typed field, because $100 is a hundred $1 and any amount can be set
    down. You type the number into an input box; the range under it is the most you hold."""
    g = blank()
    chapter_1_room_1(g)
    put(g, 13, 24, '@')
    put(g, 13, 22, '@')
    put(g, 14, 21, 'f')
    put(g, 0, 0, 'You count out some coins to set down.')
    h = 10
    top = MAP_TOP + (MAP_ROWS - h) // 2
    box(g, top, OBJ_LEFT, h, OBJ_W)
    put(g, top + 2, OBJ_COL, 'Drop how many?')
    fw = 22
    put(g, top + 4, OBJ_COL, ROOM['tl'] + ROOM['h'] * (fw - 2) + ROOM['tr'])
    put(g, top + 5, OBJ_COL, ROOM['v'] + ' ' * (fw - 2) + ROOM['v'])
    put(g, top + 5, OBJ_COL + 2, '30')                  # the typed amount, with the cursor after it
    put(g, top + 6, OBJ_COL, ROOM['bl'] + ROOM['h'] * (fw - 2) + ROOM['br'])
    put(g, top + 8, OBJ_COL, '1 to 70')                 # the range: the most you hold
    status(g, rooms=(2, 3), gold=70, turn=53, hint=HINTS['en']['drop'])
    return check(g, 'drop-amount')


# ---------------------------------------------------------------------------- 2: the lesson
# Verbatim from packs/security-onboarding/en/01-the-sorting-office/01-phishing.md
LESSON = [
    ('para', 'Ada does not look up. She is holding a letter to the lamp, and she keeps holding '
             'it while she talks.'),
    ('para', '"Everyone wants me to teach them the tell," she says. "The spelling mistake. The odd '
             'greeting. They want a checklist so they can stop thinking. I will not give you one, '
             'because the people who write these letters have read the same checklist, and they '
             'are better at it than you."'),
    ('para', 'She puts the letter down.'),
    ('para', 'A phishing message wants one of three things: your credentials, your money, or your '
             'click. It has no other purpose. Everything else is set dressing: the logo, the '
             "footer, the plausible name of a colleague. All of it paid for out of the attacker's "
             'time budget, and that budget is larger than you think.'),
    ('para', 'What it needs from you is a decision made quickly. So it manufactures urgency: a '
             'deadline, a threat, an authority you would rather not disappoint. The invoice is '
             'overdue. The account will be suspended. The CEO is in a meeting and needs this now.'),
    ('quote', 'The hurry is not a side effect of the attack. The hurry is the attack.'),
    ('para', 'Underneath the urgency there is almost always a mismatch, something that does not '
             'fit, and would not survive ten seconds of unhurried attention:'),
    ('bullet', 'A sender domain that is nearly right. micros0ft.com. yourcompany-hr.net.'),
    ('bullet', 'A link whose text says one thing and whose destination says another.'),
    ('bullet', 'A request that bypasses a process which exists precisely to stop this request.'),
    ('bullet', 'A channel that is wrong: your bank does not text you a login link.'),
    ('para', '"The mismatch is always there," Ada says. "It has to be. They cannot forge the whole '
             'world, only the parts you look at. Your job is to look at one more part than they '
             'paid for."'),
    ('para', 'She finally looks up.'),
    ('para', '"So. Not a checklist. A habit. When a message makes you feel that you must act now, '
             'that is the moment to do the opposite. Slow down and check one thing. Just one. '
             'Almost every attack in this building dies right there."'),
]

# The panel is anchored right, clear of room 1 (cols 4-25), so the learner can see the room,
# the keeper and themselves while reading. Height is computed, not fixed: see fit_panel.
LW_LEFT, LW_W = 27, 73
TEXT_COL = LW_LEFT + 2
TEXT_W = LW_LEFT + LW_W - 2 - TEXT_COL      # 69
CHROME = 5          # top border, blank, [body], blank, --More--, bottom border
MAX_BODY = MAP_ROWS - CHROME


def blocks_for(items, text_w):
    """Paragraph-sized blocks, so pages break where a reader would break."""
    blocks, bullets = [], []
    TEXT_W = text_w
    for kind, text in items:
        if kind == 'bullet':
            w = wrap(text, TEXT_W - 4)
            bullets += ['  - ' + w[0]] + ['    ' + x for x in w[1:]]
            continue
        if bullets:
            blocks.append(bullets)
            bullets = []
        if kind == 'quote':
            # A quote is set off by a leading '> ' marker (and coloured in the app), not a bare
            # indent (SCREENS 8; a play-testing remark). The marker keeps the same 4-col offset.
            blocks.append(['  > ' + w for w in wrap(text, TEXT_W - 4)])
        else:
            blocks.append(wrap(text, TEXT_W))
    if bullets:
        blocks.append(bullets)
    return blocks


def paginate(blocks, first_rows, rest_rows):
    """Fill pages with whole blocks; split a block only if it can't fit a page alone."""
    pages, cur, cap = [], [], first_rows
    for block in blocks:
        need = len(block) + (1 if cur else 0)
        if cur and len(cur) + need > cap:
            pages.append(cur)
            cur, cap = [], rest_rows
            need = len(block)
        if need > cap:
            rest = block
            while rest:
                if cur:
                    pages.append(cur)
                    cur, cap = [], rest_rows
                cur, rest = rest[:cap], rest[cap:]
            continue
        if cur:
            cur.append('')
        cur += block
    if cur:
        pages.append(cur)
    return pages


MIN_BODY = 8            # below this it's a ticker tape, not a reading surface


def _fill(pages):
    """Rows each page actually needs. Page 1 also spends title + blank."""
    return [len(pages[0]) + 2] + [len(p) for p in pages[1:]]


def fit_panel():
    """The panel height that wastes the fewest rows.

    A teaching overlay must not occupy more vertical space than it needs: every row it
    doesn't take is a row of dungeon the learner can still see while the keeper talks.

    The obvious rule -- "shortest panel that costs no extra page" -- is wrong, and the
    numbers say so plainly. For 01-phishing.md:

        3 pages -> body 19, panel 24 tall,  3 map rows kept, worst page 8 rows empty
        4 pages -> body 13, panel 18 tall,  9 map rows kept, worst page 3 rows empty

    Four pages is shorter, shows three times as much map, AND packs better. Minimising page
    count actively produces a taller, emptier panel, because paragraph-aligned pages can only
    break where the author put a blank line. Pages are cheap (PLAN 7); rows are not.

    So the objective is wasted rows, not pages. Height is computed once and held for the
    whole lesson: a panel that resized per page would jitter under the reader.
    """
    return fit(lesson_blocks())


def fit(blocks):
    best = None
    for b in range(MIN_BODY, MAX_BODY + 1):
        pages = paginate(blocks, b - 2, b)
        body = max(_fill(pages))
        if body > b:
            continue
        waste = sum(body - f for f in _fill(pages))
        if best is None or (waste, body) < best[0]:
            best = ((waste, body), body, pages)
    assert best, 'no panel height fits'
    return best[1], best[2]


def lesson_blocks():
    return blocks_for(LESSON, TEXT_W)


def lesson_pages():
    return fit_panel()[1]


def screen_lesson(page=1):
    body, pages = fit_panel()
    body = keeper_body()                         # one frame for the whole encounter
    h = body + CHROME
    top = MAP_TOP + (MAP_ROWS - h) // 2          # centred in the map area
    g = blank()
    put(g, 0, 0, 'Ada the Suspicious, wizard, teaches.')
    chapter_1_room_1(g)
    put(g, 13, 24, '@')                  # Ada
    put(g, 13, 22, '@')                  # you
    put(g, 14, 21, 'f')
    box(g, top, LW_LEFT, h, LW_W)
    r = top + 2
    if page == 1:
        put(g, r, TEXT_COL, 'Recognising a Phish')
        r += 2
    for line in pages[page - 1]:
        assert len(line) <= TEXT_W, f'lesson: {len(line)} > {TEXT_W}: {line!r}'
        put(g, r, TEXT_COL, line)
        r += 1
    assert r <= top + h - 2, f'lesson p{page}: body reached row {r}, --More-- is {top + h - 2}'
    tail = '--More--' if page < len(pages) else '(end)'
    put(g, top + h - 2, TEXT_COL, tail.ljust(TEXT_W - 14) + f'(page {page} of {len(pages)})')
    status(g, hint=HINTS['en']['read'])
    return check(g, f'lesson p{page}')


# ---------------------------------------------------------------------------- 3 / 4: the gate
# The examination uses the SAME panel as the lesson: same side, same width, same height.
# A keeper who teaches from a side panel and then asks from a box over the room is two
# different interfaces wearing one character. The panel is the keeper's frame for the whole
# encounter -- greet, instruct, examine, explain -- so nothing jumps as the gate advances
# through the states in PLAN 6.
def _options(labels, eliminated=()):
    """Numbered menu with a hanging indent (keys 1..n, OBJECTS.md 1.1.0). Each option is a key
    badge (` 1 `) then its text; the focused option's badge is highlighted in colour in the real
    render, which an ASCII frame cannot show. An eliminated option (DELVE-0018, paid gold removal)
    is still listed but marked with a leading `x` in place of its number, matching the dimmed
    badge the real renderer paints. At 69 cols the pack's longest option wraps."""
    out = []
    for i, text in enumerate(labels, 1):
        w = wrap(text, TEXT_W - 4)
        badge = " x " if (i - 1) in eliminated else f" {i} "
        out.append(f'{badge} {w[0]}')
        out += ['    ' + x for x in w[1:]]
    return out


EXAM = (
    wrap('An email appearing to come from your CEO asks you to urgently buy gift cards for '
         'a client, and to keep it quiet until the deal closes. What is the strongest single '
         'signal that this is an attack?', TEXT_W)
    + ['']
    + _options([                                     # shuffled: correct answer is not first
        'Gift cards are an unusual business expense',
        'It combines manufactured urgency with a request to bypass normal purchasing',
        'A CEO would not normally email someone in your role directly',
        'The message came by email rather than in person',
    ], eliminated={0})                               # first wrong option removed for gold
    + ['', 'Question 1 of 4.']            # the counter is all the panel footer carries (localised)
)

EXPLANATION = (
    ['2 - It combines manufactured urgency with a request to bypass', '    normal purchasing', '']
    + wrap('Urgency plus process-bypass is the signature, and secrecy is what makes it fatal; '
           '"don\'t tell anyone" exists solely to stop you doing the one check that kills it.',
           TEXT_W)
    + ['']
    + wrap('The other answers are all genuinely odd, and oddness is worth noticing. But oddness '
           "alone isn't evidence: CEOs do email people directly, unusual expenses do happen, and "
           'plenty of legitimate business runs on email. Suspicion that fires on "unusual" fires '
           'constantly and teaches you to ignore it.', TEXT_W)
)


def keeper_body():
    """One height for the whole encounter: the tallest thing the keeper ever shows."""
    return max(fit_panel()[0], len(EXAM), len(EXPLANATION))


def _gate_panel(g, msg, rows, hint, tail=''):
    chapter_1_room_1(g)
    put(g, 13, 24, '@')                  # Ada
    put(g, 13, 22, '@')                  # you
    put(g, 14, 21, 'f')
    put(g, 0, 0, msg)
    body = keeper_body()
    h = body + CHROME
    top = MAP_TOP + (MAP_ROWS - h) // 2
    box(g, top, LW_LEFT, h, LW_W)
    for i, line in enumerate(rows):
        assert len(line) <= TEXT_W, f'gate: {len(line)} > {TEXT_W}: {line!r}'
        put(g, top + 2 + i, TEXT_COL, line)
    if tail:
        put(g, top + h - 2, TEXT_COL, tail)
    status(g, hint=hint)
    return g


def screen_mcq():
    return check(_gate_panel(blank(), 'Ada the Suspicious examines you.', EXAM,
                             HINTS['en']['answer']), 'mcq')


def screen_explanation():
    return check(_gate_panel(blank(), 'Correct.', EXPLANATION, HINTS['en']['more'],
                             tail='--More--'), 'explanation')


# ---------------------------------------------------------------------------- 5: REPELLED
# The most important guardrail in the design (CLAUDE.md rule 4), and pure tone: REPELLED is
# not death and must never read as punishment. This screen is where that promise is kept or
# broken, which is why it is worth drawing before it is worth building.
#
# HP:3(12) is a third failed sitting at standard: 12 - 3*3. The penalty is per *failed sitting*,
# not per wrong answer (PLAN 6, AUTHORING 4), so a room's total bleed is penalty*attempts = 9,
# capped below 12, and REPELLED always fires before HP:0. An earlier "per wrong answer" reading
# made this screen unreachable; see SCREENS 8.10.
REPELLED = (
    wrap('Ada the Suspicious turns back to her work. "Not yet," she says. There is no edge '
         'in it. "You have read it once. Read it twice."', TEXT_W)
    + ['']
    + wrap('The wall is stone again. Nothing you earned is gone: every door you opened is '
           'still open, and the way back is still the way back.', TEXT_W)
    + ['',
       '    Ask her to teach it again    t    free, always and forever',
       '    Ask your kitten              ?    costs score, not health',
       '    Rest until you heal          s',
       '',
       'She does not seem to be in any hurry.']
)


def screen_repelled():
    g = blank()
    chapter_1_room_1(g)
    put(g, 13, 24, '@')                  # Ada, unmoved
    put(g, 13, 17, '@')                  # you, pushed back across the room
    put(g, 14, 16, 'f')
    put(g, 0, 0, 'Ada the Suspicious shakes her head. You are pushed back from the door.')
    body = keeper_body()
    h = body + CHROME
    top = MAP_TOP + (MAP_ROWS - h) // 2
    box(g, top, LW_LEFT, h, LW_W)
    put(g, top + 2, TEXT_COL, 'REPELLED')
    for i, line in enumerate(REPELLED):
        assert len(line) <= TEXT_W, f'repelled: {len(line)} > {TEXT_W}: {line!r}'
        put(g, top + 4 + i, TEXT_COL, line)
    assert top + 4 + len(REPELLED) <= top + h - 1, 'repelled: body overruns the frame'
    status(g, hp=(3, 12), turn=31, hint=HINTS['en']['repelled'])
    return check(g, 'repelled')


# ---------------------------------------------------------------------------- 7: assertion (nl)
def screen_assertion_nl():
    """An assertion is an examination, so it uses the keeper's panel; its two answers are a
    numbered-style list, the same look and navigation as an MCQ (BUTTONS.md), each behind a key
    badge (` w ` / ` n `, the label's first letter). The prompt is verbatim from the nl pack
    (question 2); the footer is just the localised counter."""
    g = blank()
    chapter_1_room_1(g)
    put(g, 13, 24, '@')
    put(g, 13, 22, '@')
    put(g, 14, 21, 'f')
    put(g, 0, 0, 'Ada de Achterdochtige overhoort je.')
    h = keeper_body() + CHROME
    top = MAP_TOP + (MAP_ROWS - h) // 2
    box(g, top, LW_LEFT, h, LW_W)
    prompt = wrap('Slechte spelling en grammatica zijn een betrouwbare manier om phishing te '
                  'herkennen.', TEXT_W)
    r = top + 2
    for line in prompt:
        assert len(line) <= TEXT_W, f'nl: {len(line)} > {TEXT_W}'
        put(g, r, TEXT_COL, line)
        r += 1
    r += 1
    for key, label in [('w', 'Waar'), ('n', 'Niet waar')]:
        put(g, r, TEXT_COL, f' {key}  {label}')      # ` w ` badge (colour-highlighted when focused)
        r += 1
    r += 1
    put(g, r, TEXT_COL, 'Vraag 2 van 4.')
    status(g, loc='nl', hint=HINTS['nl']['answer'])
    return check(g, 'assertion-nl')


# ---------------------------------------------------------------------------- 8 / 9: the scroll
SCROLL = {
    'en': ('The Scroll of Vigilance', [
        'Be it known to all who keep the Caverns:',
        '',
        '{name} went down into the dark on {date}, and came back up.',
        '',
        'Four floors. Twelve keepers. Ada, who would not give a checklist. Grigor, who '
        'was impersonated for eleven days. Entropy, who counts. The Second Factor, who '
        'asks twice. Marisol among her shelves. Rook, who watches the coffee shops. '
        'Iolanthe, who was never the auditor. The Oracle, who told the truth about what '
        'it is given. And Wren, at the last door, who said: tell us fast.',
        '',
        'Score: {score}',
        '',
        'Carry it out with you. The keepers stay down here; the habits do not.',
    ]),
    'nl': ('De rol der waakzaamheid', [
        'Aan allen die de grotten bewaken, zij bekend:',
        '',
        '{name} daalde af in het donker op {date}, en kwam weer boven.',
        '',
        'Vier verdiepingen. Twaalf poortwachters. Ada, die geen lijstje wilde geven. '
        'Grigor, wiens naam elf dagen lang geleend werd. Entropie, die telt. De Tweede '
        'Factor, die tweemaal vraagt. Marisol tussen haar rekken. Rook, die de '
        'koffietentjes in de gaten houdt. Iolanthe, die nooit de accountant was. Het '
        'Orakel, dat de waarheid vertelde over wat het krijgt aangereikt. En '
        'Winterkoning, bij de laatste deur, die zei: vertel het ons snel.',
        '',
        'Score: {score}',
        '',
        'Neem hem mee naar buiten. De poortwachters blijven hier beneden; de gewoonten niet.',
    ]),
}
AWARDED = dt.date(2026, 7, 17)


def screen_scroll(loc):
    f = LOCALES[loc]
    title, body = SCROLL[loc]
    subs = {
        'name':  f['player'].split()[0],
        'date':  fmt_date(loc, AWARDED),
        'score': fmt_num(loc, 91.666, 1) + '%',      # 11 of 12: the separator matters
        'pack':  f['pack'],
    }
    g = blank()
    put(g, 0, 0, 'You pick up the scroll.' if loc == 'en' else 'Je pakt de rol op.')
    bw, bl = 76, 12
    box(g, 3, bl, 22, bw)
    tw = bw - 6
    r = 5
    put(g, r, bl + 3, title)
    r += 2
    for para in body:
        if not para:
            r += 1
            continue
        for line in wrap(para.format(**subs), tw):
            assert len(line) <= tw, f'scroll {loc}: {len(line)} > {tw}'
            put(g, r, bl + 3, line)
            r += 1
    # Dutch runs ~15% longer than English. This window fits en with two rows to spare and
    # nl with none; a fixed height that fits one locale does not fit the other. See SCREENS 8.3.
    assert r <= 23, f'scroll {loc}: body reached row {r}, footer is row 23'
    put(g, 23, bl + 3, f"{subs['pack']}, {'sealed' if loc == 'en' else 'verzegeld op'} "
                       f"{subs['date']}")
    status(g, loc=loc, dlvl=4, rooms=(12, 12), gold=1250, hp=(9, 12), turn=2841,
           hint=HINTS.get(loc, HINTS['en']).get('scroll', HINTS['en']['scroll']))
    return check(g, f'scroll-{loc}')


# ---------------------------------------------------------------------------- driver
_tens = ''.join(str(i * 10).rjust(10) for i in range(1, 11))
_ones = '1234567890' * 10
assert len(_tens) == 100 and len(_ones) == 100
RULER = _tens + '\n' + _ones


def all_screens():
    n = len(lesson_pages())
    return [
        ('0. The tutorial floor (Dlvl 0)', screen_tutorial()),
        ('1. Arrival on Dlvl 1', screen_map(False)),
        *[(f'2. Ada instructs (page {p} of {n})', screen_lesson(p)) for p in range(1, n + 1)],
        ('3. The examination', screen_mcq()),
        ('4. The explanation', screen_explanation()),
        ('5. The door appears', screen_map(True)),
        ('6. Repelled', screen_repelled()),
        ('7. Two rooms and a corridor', screen_two_rooms()),
        ('8. The floor complete', screen_floor_complete()),
        ('9. An assertion, in Dutch', screen_assertion_nl()),
        ('10. The scroll (en)', screen_scroll('en')),
        ('11. The scroll (nl)', screen_scroll('nl')),
        ('12. Objects: the coin reward', screen_reward()),
        ('13. Objects: your pack', screen_inventory()),
        ('14. Objects: dropping coins', screen_drop_amount()),
        ('15. Help: the Keys tab', screen_help()),
        ('16. The ambient room-entry toast', screen_toast()),
    ]


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true', help='assert geometry, print nothing')
    args = ap.parse_args()
    screens = all_screens()
    if args.check:
        print(f'ok: {len(screens)} screens, all exactly {W}x{H}')
        body, pages = fit_panel()
        print(f'    lesson: {sum(len(b) for b in lesson_blocks())} lines at {TEXT_W} cols '
              f'-> {len(pages)} pages {[len(p) for p in pages]}')
        print(f'    panel:  body {body} rows -> {body + CHROME} tall of {MAP_ROWS} '
              f'({MAP_ROWS - body - CHROME} rows of map kept)')
        for loc in LOCALES:
            print(f'    {loc}: {fmt_date(loc, AWARDED)} | {fmt_money(loc, 1250)} | '
                  f'{fmt_num(loc, 91.666, 1)}%')
        raise SystemExit
    for name, g in screens:
        print(f'\n===== {name} =====')
        print(RULER)
        print(render(g))
