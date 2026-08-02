"""ASCII grid helpers for design mock-ups of screens that do not exist yet.

Shared by `infoscreen_mockups.py` (DELVE-0035 proposed tabs). Not a `./tools.sh` entry (leading
underscore). These are hand-placed geometry assertions for unbuilt UI; built screens are rendered
on demand by `screenshot.py` against the real renderer instead.
"""

W, H = 100, 30
MAP_TOP, MAP_ROWS = 1, 27          # row 0 = message, rows 1..27 = map, rows 28..29 = status
LW_LEFT, LW_W = 27, 73

LOCALES = {
    "en": {
        "player": "George the Novice",
        "rooms": "Rooms",
        "currency": "$",
        "decimal": ".",
        "thousands": ",",
        "months": ["January", "February", "March", "April", "May", "June", "July",
                   "August", "September", "October", "November", "December"],
        "date": "{d} {month} {y}",
        "pack": "The Caverns of Compliance",
    },
    "nl": {
        "player": "George de Beginner",
        "rooms": "Kamers",
        "currency": "€",
        "decimal": ",",
        "thousands": ".",
        "months": ["januari", "februari", "maart", "april", "mei", "juni", "juli",
                   "augustus", "september", "oktober", "november", "december"],
        "date": "{d} {month} {y}",
        "pack": "De grotten der naleving",
    },
}

ROOM = {"h": "─", "v": "│", "tl": "┌", "tr": "┐", "bl": "└", "br": "┘"}
WIN = {"h": "═", "v": "║", "tl": "╔", "tr": "╗", "bl": "╚", "br": "╝"}


def fmt_num(loc, value, places=0):
    f = LOCALES[loc]
    whole, _, frac = f"{value:,.{places}f}".partition(".")
    whole = whole.replace(",", "\x00").replace("\x00", f["thousands"])
    return whole + (f["decimal"] + frac if frac else "")


def blank():
    return [[" "] * W for _ in range(H)]


def put(g, r, c, s):
    for i, ch in enumerate(s):
        g[r][c + i] = ch


def _frame(g, top, left, h, w, s, fill):
    put(g, top, left, s["tl"] + s["h"] * (w - 2) + s["tr"])
    put(g, top + h - 1, left, s["bl"] + s["h"] * (w - 2) + s["br"])
    for r in range(top + 1, top + h - 1):
        g[r][left] = s["v"]
        g[r][left + w - 1] = s["v"]
        for c in range(left + 1, left + w - 1):
            g[r][c] = fill


def room(g, top, left, h, w):
    _frame(g, top, left, h, w, ROOM, ".")


def box(g, top, left, h, w):
    _frame(g, top, left, h, w, WIN, " ")


def status(g, loc="en", dlvl=1, rooms=(0, 3), gold=0, hp=(12, 12), turn=14, hint=""):
    f = LOCALES[loc]
    line = (f"{f['player']}   Dlvl:{dlvl}  {f['rooms']}:{rooms[0]}/{rooms[1]}  "
            f"{f['currency']}:{fmt_num(loc, gold)}  HP:{hp[0]}({hp[1]})  T:{turn}")
    assert len(line) <= W, f"status: {len(line)} > {W}"
    assert len(hint) <= W, f"hint: {len(hint)} > {W}"
    put(g, 28, 0, line)
    put(g, 29, 0, hint)


def chapter_1_room_1(g):
    room(g, 9, 4, 9, 22)
    put(g, 11, 7, "<")


def chapter_1_floor(g, revealed):
    chapter_1_room_1(g)
    if revealed >= 2:
        put(g, 13, 25, "+")
        for c in range(26, 33):
            g[13][c] = "#"
        for c in range(32, 38):
            g[12][c] = "#"
        room(g, 8, 38, 9, 25)
        put(g, 12, 38, "+")
    if revealed >= 3:
        put(g, 12, 62, "+")
        for c in range(63, 67):
            g[12][c] = "#"
        for r in range(12, 15):
            g[r][66] = "#"
        for c in range(66, 70):
            g[14][c] = "#"
        room(g, 10, 70, 9, 25)
        put(g, 14, 70, "+")


def check(g, name):
    assert len(g) == H, f"{name}: {len(g)} rows, want {H}"
    for i, r in enumerate(g):
        assert len(r) == W, f"{name}: row {i} is {len(r)} cols, want {W}"
    return g


def render(g):
    return "\n".join("".join(r).rstrip() for r in g)
