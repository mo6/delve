"""NetHack-style windows: the keeper's panel for a lesson, a question, or an explanation.

Pagination and panel geometry live here, not in the core: the core hands over the whole text
as semantic blocks and the UI breaks it into pages (PLAN.md section 4). Pages break on
paragraph boundaries and never inside a URL or domain (break_on_hyphens=False).

The panel is a right-anchored double-line box, deliberately distinct from a room's single-line
wall. Its body height is a pure function of the terminal height (`_body`): held at the tuned
minimum on a 100x30 floor, and one row taller per extra terminal row above it, so a taller
terminal shows more of the lesson at once. Because it depends only on `rows`, it is constant
across the whole encounter, so nothing jitters as the keeper walks greet/instruct/
examine/explain.
"""

import curses
import textwrap
import time
import unicodedata
from dataclasses import replace

from delve.session.views import (
    AmountView,
    Colour,
    FreeTextView,
    GradingView,
    HelpView,
    InfoView,
    MenuView,
    PromptView,
    TextBlock,
    TextView,
    ToastView,
)
from delve.ui import attrs

PANEL_W = 73
TEXT_W = 69                 # inner text width: PANEL_W - 2 borders - 2 padding
CHROME = 5                  # top border, blank, [body], footer, bottom border
BODY_MIN = 14              # body rows at the 100x30 floor: the tuned encounter height, held there
MIN_ROWS = 30              # the enforced terminal floor; below it the app shows a resize overlay

# A Scoring-tab bar row's column layout (DELVE-0043): a fixed label field, then a fixed-width bar,
# well inside TEXT_W regardless of chapter title length. `ui` owns this (not `session`), the same
# way it owns every other column-width decision in this file.
BAR_LABEL_W = 20
BAR_W = 30
BAR_FILLED = "█"            # coloured (Colour.BRIGHT_CYAN): the scored portion
BAR_EMPTY = "░"             # plain attribute: not yet scored

# The Pack tab's two-column layout (DELVE-0075): a fixed-width list column, a one-column gap on
# each side of the vertical divider, and the description column taking whatever's left of TEXT_W.
PACK_LIST_W = 26
PACK_DESC_W = TEXT_W - PACK_LIST_W - 3

# The Grader tab's two-column layout (DELVE-0087): even halves of TEXT_W with the same one-column
# gap on each side of the vertical divider as Pack. Even (not Pack's list/desc asymmetry) because
# both columns carry the same Model/Status/This run/… row shapes.
GRADER_COL_W = (TEXT_W - 3) // 2
GRADER_COL_RIGHT_W = TEXT_W - GRADER_COL_W - 3

# The ambient room-entry toast (DELVE-0060): its own, smaller right-anchored block, deliberately
# narrower than PANEL_W and top-anchored rather than vertically centred like every blocking panel,
# so it visibly reads as ambient weather over the room rather than a panel the room is paused for.
TOAST_W = 44
TOAST_TEXT_W = TOAST_W - 4
TOAST_TOP = 2                # just under the message line, the same row the map itself starts on

# The toast's own "still generating" spinner (DELVE-0082): the "dots" braille sequence (one of the
# well-known set at stackoverflow.com/questions/2685435, the default in most modern CLI spinner
# libraries). Single-codepoint, BMP, narrow, so it's the same class of Unicode bet this file's own
# double-line window borders already make (proven macOS/Linux, unverified Windows/PDCurses) rather
# than a new one. `_SPINNER_MS` is how long each glyph holds; the animation frame is derived from
# wall-clock time at paint time, not any counter threaded through the Frame or the app loop, since
# it is purely cosmetic (rule 2: nothing here is state `session` needs to know about). The app
# loop's toast-pending wake (`ui/app.py:_TOAST_POLL_MS`) is derived from this same value so every
# idle redraw lands on the next glyph rather than mid-cycle (DELVE-0093); do not change one alone.
_SPINNER = "⣾⣽⣻⢿⡿⣟⣯⣷"
_SPINNER_MS = 120


def _spinner_glyph(now_ms: float) -> str:
    """The spinner glyph for a wall-clock millisecond timestamp. Pure so tests can drive a
    simulated redraw sequence without painting through curses (DELVE-0093)."""
    return _SPINNER[int(now_ms / _SPINNER_MS) % len(_SPINNER)]


def _body(rows: int) -> int:
    """Panel body rows. Fixed at the tuned `BODY_MIN` on a minimum-height terminal, then one extra
    row per extra terminal row, so a taller terminal shows more of the lesson at once (fewer pages)
    while the margin above and below the panel stays constant. A pure function of `rows`: it never
    changes mid-encounter, so nothing jitters as the keeper walks greet/instruct/examine/explain
    (PLAN.md section 7), and only a resize moves it. Clamped to what the map area can hold."""
    avail = (rows - 3) - CHROME          # map area is rows - 3; the panel needs CHROME of chrome
    return max(8, min(avail, BODY_MIN + max(0, rows - MIN_ROWS)))

_WIN = {"h": "═", "v": "║", "tl": "╔", "tr": "╗", "bl": "╚", "br": "╝"}

# A quote/citation block is set off by a leading marker (a visible '> ', so it never reads as a bare
# indent) and drawn in a colour, so a keeper's aphorism stands out from the prose around it. The
# marker keeps its own width, so it is legible on a colourless terminal too (where the colour falls
# back to bold). Single-line box chars draw the amount field, distinct from the double-line panel.
QUOTE_PREFIX = "  > "
_FIELD = {"h": "─", "v": "│", "tl": "┌", "tr": "┐", "bl": "└", "br": "┘"}


def _cw(ch: str) -> int:
    """A character's *display* width in terminal columns, which is not its string length: a
    combining mark takes 0, an East Asian Wide/Fullwidth glyph (CJK, and most emoji) takes 2, and
    everything Delve otherwise ships (Latin, `é`, `€`, box-drawing) takes 1. This is the one fact
    the panel has to respect so an emoji in an explanation does not run a wrapped line through the
    box border (DISPLAY.md section 1). Single-codepoint emoji only; the validator keeps packs to
    those, since a ZWJ or variation-selector sequence is several codepoints wearing one glyph."""
    if unicodedata.combining(ch):
        return 0
    return 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1


def _width(text: str) -> int:
    return sum(_cw(c) for c in text)


def _wrap(text: str, width: int) -> list[str]:
    # Pure narrow text (ASCII, Latin, `é`/`€`) keeps textwrap exactly, so every existing lesson
    # wraps byte-for-byte as the mock-ups verified; only text carrying a wide glyph takes the
    # column-aware path below.
    if _width(text) == len(text):
        return textwrap.wrap(text, width, break_on_hyphens=False) or [""]
    lines, cur, cur_w = [], "", 0
    for word in text.split():                    # never break a word, so a URL/domain stays whole
        ww = _width(word)
        if cur and cur_w + 1 + ww > width:
            lines.append(cur)
            cur, cur_w = "", 0
        cur, cur_w = (cur + " " + word, cur_w + 1 + ww) if cur else (word, ww)
    if cur:
        lines.append(cur)
    return lines or [""]


# A drawn line is `(quote, segments)`: `quote` colours the whole line, and `segments` is a list of
# `(text, strong)` runs so **bold** can stand out inside it. A blank line is `(False, [])`.


def _merge(segs: list, text: str, strong: bool) -> None:
    if text and segs and segs[-1][1] == strong:
        segs[-1] = (segs[-1][0] + text, strong)
    elif text:
        segs.append((text, strong))


def _seg_width(segs) -> int:
    return sum(_width(t) for t, _ in segs)


def _longest_word(cell) -> int:
    """The widest unbreakable run in a cell, so a table column is never sized below a word it must
    hold (which would overflow it and shove the whole column out of alignment)."""
    best = cur = 0
    for text, _ in cell:
        for ch in text:
            cur = 0 if ch == " " else cur + _cw(ch)
            best = max(best, cur)
    return best


def _wrap_words(words, width: int) -> list[list]:
    """Fill `width` with `words` (each a list of `(text, strong)` segments), never breaking a word,
    so a URL or domain stays whole. Returns lines of segments."""
    if not words:
        return [[]]
    lines, line, width_so_far = [], [], 0
    for word in words:
        wl = _seg_width(word)
        if line and width_so_far + 1 + wl > width:
            lines.append(line)
            line, width_so_far = [], 0
        if line:
            _merge(line, " ", False)
            width_so_far += 1
        for text, strong in word:
            _merge(line, text, strong)
        width_so_far += wl
    if line:
        lines.append(line)
    return lines


def _wrap_spans(spans, width: int) -> list[list]:
    """Word-wrap styled runs to `width`, carrying each word's `strong` weight through. A literal
    '\\n' in a span is a hard line break (so a bold title can sit on its own line above wrapped
    body, with no blank between them); each logical line is wrapped independently."""
    lines: list[list] = []
    words: list[list] = []
    cur: list = []
    for text, strong in spans:
        for ch in text:
            if ch == "\n":
                if cur:
                    words.append(cur)
                    cur = []
                lines.extend(_wrap_words(words, width))
                words = []
            elif ch == " ":
                if cur:
                    words.append(cur)
                    cur = []
            else:
                _merge(cur, ch, strong)
    if cur:
        words.append(cur)
    lines.extend(_wrap_words(words, width))
    return lines or [[]]


LABEL_COLOUR = Colour.BRIGHT_CYAN  # a 'kv' block's label half (DELVE-0078)


def _kv_spans(text: str) -> tuple:
    """Split each of a `kind="kv"` block's `"\\n"`-joined lines at its first `": "`, colouring the
    label half (including the colon) `LABEL_COLOUR` and leaving the value half plain. A line with
    no `": "` (should not happen for a genuine label/value row, but never crashes) passes through
    unstyled. Only the *first* `": "` counts, so a value containing its own colon (a host:port, a
    model tag like `qwen2.5:3b`) never gets mistaken for a second label."""
    spans = []
    for i, line in enumerate(text.split("\n")):
        prefix = "\n" if i else ""
        cut = line.find(": ")
        if cut == -1:
            spans.append((prefix + line, False))
            continue
        spans.append((prefix + line[: cut + 1], LABEL_COLOUR))
        spans.append((line[cut + 1 :], False))
    return tuple(spans)


def _wrap_block_lines(block, width: int) -> list[list]:
    """A block's body as lines of segments. A code block is verbatim: split on its own newlines and
    never reflowed, because its whitespace is meaningful (carets pointing under a URL, columns of a
    passphrase comparison) and textwrap would collapse it. A 'kv' block (DELVE-0078) colon-splits
    and colours its label before wrapping, overriding whatever plain `spans` `session` set (colour
    is a `ui` decision, rule 2). Styled (spans) blocks word-wrap with their weights; a plain block
    keeps the exact textwrap behaviour the mock-ups were built on."""
    if block.kind == "code":
        return [[(line[:width], False)] for line in block.text.split("\n")]
    if block.kind == "kv":
        return _wrap_spans(_kv_spans(block.text), width)
    if block.spans:
        return _wrap_spans(block.spans, width)
    return [[(line, False)] for line in _wrap(block.text, width)]


def _layout_table(rows, width: int) -> list:
    """Lay a table's cell grid into aligned, wrapped columns within `width`: proportional column
    widths, cells wrapped to their column, the header row bold with an underline beneath. Layout is
    the panel's job; the grid came in as structure (rule 2)."""
    if not rows:
        return []
    ncol = max(len(r) for r in rows)
    norm = [list(r) + [()] * (ncol - len(r)) for r in rows]
    avail = max(ncol, width - 3 * (ncol - 1))             # 3 cols per " | " separator
    maxw = [max((_seg_width(row[c]) for row in norm), default=1) or 1 for c in range(ncol)]
    # Floor each column at its longest word so no cell overflows, then share the slack by content.
    minw = [min(max((_longest_word(row[c]) for row in norm), default=1), avail)
            for c in range(ncol)]
    extra = max(0, avail - sum(minw))
    spread = sum(maxw) or 1
    colw = [minw[c] + round(extra * maxw[c] / spread) for c in range(ncol)]
    colw[-1] = max(minw[-1], colw[-1] + (avail - sum(colw)))    # rounding into the last column
    out: list = []
    for ri, row in enumerate(norm):
        header = ri == 0
        cells = []
        for c in range(ncol):
            cell = row[c] or (("", False),)
            if header:
                cell = tuple((t, True) for t, _ in cell)
            cells.append(_wrap_spans(cell, colw[c]))
        for li in range(max(len(w) for w in cells)):
            segs: list = []
            for c in range(ncol):
                line = cells[c][li] if li < len(cells[c]) else []
                segs.extend(line)
                segs.append((" " * max(0, colw[c] - _seg_width(line)), False))
                if c < ncol - 1:
                    segs.append((" │ ", False))
            out.append((False, segs))
        if header:
            rule: list = []
            for c in range(ncol):
                rule.append(("─" * colw[c], False))
                if c < ncol - 1:
                    rule.append(("─┼─", False))
            out.append((False, rule))
    return out


def _bar_segments(label: str, frac: float | None, tail: str) -> list:
    """One Scoring-tab row (DELVE-0043) as styled segments: a fixed-width label, a coloured bar
    (`frac` 0..1 filled with `BAR_FILLED`, the rest `BAR_EMPTY`; `frac=None` means "not yet
    attempted" and draws fully empty, never a misleadingly-filled zero score), then `tail` (a
    percentage or a fraction like `12/12`). A style is `Colour.BRIGHT_CYAN` for the filled run,
    `False` (plain) elsewhere; `_put_line` renders a `Colour` style via `attrs.attr_for`. Truncates
    a label wider than `BAR_LABEL_W` with a single ellipsis rather than wrapping onto a second
    line; this row is never routed through the word-wrapper, which would collapse its padding."""
    if len(label) > BAR_LABEL_W:
        label = label[: BAR_LABEL_W - 1] + "…"
    filled = round(max(0.0, min(1.0, frac if frac is not None else 0.0)) * BAR_W)
    segs = [(f"{label:<{BAR_LABEL_W}} ", False)]
    if filled:
        segs.append((BAR_FILLED * filled, Colour.BRIGHT_CYAN))
    if BAR_W - filled:
        segs.append((BAR_EMPTY * (BAR_W - filled), False))
    segs.append((f"  {tail}", False))
    return segs


def _blocks(body, text_w: int) -> list[list]:
    """Paragraph-sized blocks of styled lines, so pages break where a reader would. Each line is
    `(quote, segments)`; a bullet keeps its hanging indent, a quote its marker, a table its grid.
    Consecutive `bar` rows batch into one block the same way bullets do (a playtesting fix): the
    Scoring > Now tab is a dense list of related bars (one per chapter, then HP), and without this
    each row was its own block, so the generic "blank line between blocks" pagination rule
    (`_paginate`) burned a wasted row after every single bar."""
    blocks: list[list] = []
    bullets: list = []
    bars: list = []
    for b in body:
        if b.kind == "bullet":
            wrapped = _wrap_block_lines(b, text_w - 4)
            for k, segs in enumerate(wrapped):
                bullets.append((False, [("  - " if k == 0 else "    ", False), *segs]))
            continue
        if bullets:
            blocks.append(bullets)
            bullets = []
        if b.kind == "bar":
            bars.append((False, _bar_segments(*b.bar)))
            continue
        if bars:
            blocks.append(bars)
            bars = []
        if b.kind == "table":
            blocks.append(_layout_table(b.table, text_w))
        elif b.kind == "quote":
            wrapped = _wrap_block_lines(b, text_w - len(QUOTE_PREFIX))
            blocks.append([(True, [(QUOTE_PREFIX, False), *segs]) for segs in wrapped])
        else:  # para, plain, code
            blocks.append([(False, segs) for segs in _wrap_block_lines(b, text_w)])
    if bullets:
        blocks.append(bullets)
    if bars:
        blocks.append(bars)
    return blocks


def _paginate(blocks: list[list[str]], first_rows: int, rest_rows: int) -> list[list[str]]:
    """Fill pages with whole blocks; split a block only if it can't fit a page alone."""
    pages: list[list[str]] = []
    cur: list[str] = []
    cap = first_rows
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
            cur.append((False, []))       # a blank line between blocks
        cur += block
    if cur:
        pages.append(cur)
    return pages


def _text_pages(view, body: int) -> list[list[str]]:
    # Page 1 reserves two rows for header chrome: a TextView's title (content, so later pages
    # don't repeat it) or an InfoView/HelpView's tab strip (navigation chrome, so it stays on every
    # page, per InfoView's own docstring; only the row budget is shared, not the "page 1 only"
    # rule). A third row is reserved only when the tab strip carries a sub-tab strip (DELVE-0055),
    # so Pack/Grader/Status and both Help tabs (none of which have one) keep today's exact
    # geometry and page counts.
    has_title = isinstance(view, TextView) and view.title
    reserve = 2 if (isinstance(view, (InfoView, HelpView)) or has_title) else 0
    if isinstance(view, (InfoView, HelpView)) and view.subtabs:
        reserve += 1
    return _paginate(_blocks(view.body, TEXT_W), body - reserve, body)


def page_count(overlay, rows: int) -> int:
    """Pages the overlay needs at this terminal height. Menus and prompts are always one; so is
    the Pack tab's compact row list (DELVE-0069, `overlay.pack_rows` non-empty) and the Grader
    tab's two-column layout (DELVE-0087, `overlay.grader_left` non-empty), the same
    never-paginated treatment MenuView/PromptView already get, since both layouts are sized to
    fit the panel's body height on one page."""
    if isinstance(overlay, InfoView) and (overlay.pack_rows or overlay.grader_left):
        return 1
    if isinstance(overlay, (TextView, InfoView, HelpView)):
        return len(_text_pages(overlay, _body(rows)))
    return 1


MESSAGE_MORE = "--More--"


def message_pages(msg: str, cols: int) -> list[str]:
    """Split a top-line message into pages that each fit the terminal width, so a message wider than
    the line is paged with a `--More--` prompt rather than truncated (DELVE-0030, NetHack's
    --More--). A message that already fits is a single page, returned unchanged. A longer one is
    wrapped so that each page *plus* a trailing ' --More--' still fits `cols - 1`; the caller
    appends the prompt to every page but the last. Never breaks a word (`_wrap`), so a domain in a
    message stays whole; column-aware, like the panel wrap. Pure, so it is unit-tested."""
    limit = max(1, cols - 1)
    if not msg or _width(msg) <= limit:
        return [msg]
    inner = max(1, limit - _width(" " + MESSAGE_MORE))
    return _wrap(msg, inner) or [msg]


def _put(stdscr, y: int, x: int, text: str, attr: int = curses.A_NORMAL) -> None:
    try:
        stdscr.addstr(y, x, text, attr)
    except curses.error:
        pass


def _put_line(stdscr, y: int, col: int, quote: bool, segs) -> None:
    """Draw one styled line: a quote line is cyan; a `strong` run is bold, and bright yellow when
    it is not already coloured, so **bold** stands out with colour and stays visible (bold) without.
    A `Colour` style (a Scoring-tab bar's filled run, DELVE-0043) draws in that colour directly,
    bypassing the bool bold/quote handling entirely.
    """
    x = col
    for text, strong in segs:
        if isinstance(strong, Colour):
            attr = attrs.attr_for(strong)
        else:
            attr = attrs.attr_for(Colour.BRIGHT_CYAN) if quote else curses.A_NORMAL
            if strong:
                attr = attr | curses.A_BOLD if quote else attrs.attr_for(Colour.BRIGHT_YELLOW)
        _put(stdscr, y, x, text, attr)
        x += _width(text)                  # a wide glyph advances two columns, so runs stay aligned


def _box(stdscr, top: int, left: int, h: int, w: int) -> None:
    s = _WIN
    line = s["h"] * (w - 2)
    _put(stdscr, top, left, s["tl"] + line + s["tr"])
    _put(stdscr, top + h - 1, left, s["bl"] + line + s["br"])
    # Left border plus a cleared interior in one write (ends at left+w-2, never the last cell),
    # then the right border as a single char. Writing the fill as one long string anchored at the
    # right edge made curses wrap it onto the next row: a stray border and an erased map.
    interior = s["v"] + " " * (w - 2)
    for r in range(top + 1, top + h - 1):
        _put(stdscr, r, left, interior)
        _put(stdscr, r, left + w - 1, s["v"])


def _geom(rows: int, cols: int, map_cols: int) -> tuple[int, int, int]:
    map_area_h = rows - 3
    h = _body(rows) + CHROME
    top = 1 + max(0, (map_area_h - h) // 2)
    left = max(0, min(cols, map_cols) - PANEL_W)
    return top, left, h


def draw(stdscr, overlay, map_cols: int, page: int) -> None:
    rows, cols = stdscr.getmaxyx()
    top, left, h = _geom(rows, cols, map_cols)
    col = left + 2
    _box(stdscr, top, left, h, PANEL_W)
    if isinstance(overlay, TextView):
        _draw_text(stdscr, overlay, top, col, h, page)
    elif isinstance(overlay, (InfoView, HelpView)):
        _draw_info(stdscr, overlay, top, col, h, page)
    elif isinstance(overlay, MenuView):
        _draw_menu(stdscr, overlay, top, col)
    elif isinstance(overlay, PromptView):
        _draw_prompt(stdscr, overlay, top, col)
    elif isinstance(overlay, AmountView):
        _draw_amount(stdscr, overlay, top, col)
    elif isinstance(overlay, FreeTextView):
        _draw_freetext(stdscr, overlay, top, col)
    elif isinstance(overlay, GradingView):
        _draw_grading(stdscr, overlay, top, col)


def _draw_text(stdscr, view: TextView, top: int, col: int, h: int, page: int) -> None:
    pages = _text_pages(view, h - CHROME)      # same body the box was sized to, so the tail aligns
    page = max(1, min(page, len(pages)))
    r = top + 2
    if view.title and page == 1:
        _put(stdscr, r, col, view.title, curses.A_BOLD)
        r += 2
    for quote, segs in pages[page - 1]:
        _put_line(stdscr, r, col, quote, segs)
        r += 1
    tail = view.more_label if page < len(pages) else view.end_label
    if len(pages) > 1:
        counter = view.page_fmt.format(page=page, total=len(pages))
        tail = tail.ljust(max(len(tail) + 1, TEXT_W - len(counter))) + counter   # right-align it
    _put(stdscr, top + h - 2, col, tail)


def _fill_status_size(stdscr, view: InfoView | HelpView) -> InfoView | HelpView:
    """The Status tab's terminal-size row (DELVE-0044): the one row in this panel that is a
    `ui`-owned fact rather than a `session`-computed one (`session` never reads `stdscr`, rule 2).
    `RunState._status_body` condenses every row, including this one, into a single block (a
    playtesting fix closed the tab's last remaining gap, which a structurally separate `kind="size"`
    block used to leave); here, read at paint time so it can never go stale, the live `rows x cols`
    is spliced into that block's *last line* (a private position-based contract with
    `_status_body`, which always appends the size row last and always returns exactly one block).
    A copy is returned rather than mutating the shared view, since neither view is frozen. A no-op
    on a `HelpView` (no tab of its is ever keyed 'status') or an empty body, so this is safe to
    call on either."""
    if not (view.tabs and 0 <= view.active < len(view.tabs)
            and view.tabs[view.active].key == "status" and view.body):
        return view
    rows, cols = stdscr.getmaxyx()
    block = view.body[0]
    lines = block.text.split("\n")
    lines[-1] = f"{lines[-1]} {rows}x{cols}"
    spans = tuple((("\n" if i else "") + line, False) for i, line in enumerate(lines))
    filled = TextBlock(block.kind, "\n".join(lines), spans=spans)
    return replace(view, body=[filled, *view.body[1:]])


def _draw_tab_row(stdscr, r: int, x: int, tabs, active: int, focused: bool) -> None:
    """One tab row: the active tab is a filled pill (DELVE-0041, the same bar_attr treatment as a
    focused MCQ option's number badge) when `focused` is True, or a plain bright colour with no
    fill otherwise (DELVE-0056), so two rows can each show an "active" tab without looking
    identical; only the row under keyboard focus is the one left/right will move next."""
    for i, t in enumerate(tabs):
        if i:
            x += 2
        is_active = i == active
        if is_active and focused:
            label = f" {t.label} "
            attr = attrs.bar_attr(Colour.CYAN)
        elif is_active:
            label = t.label
            attr = attrs.attr_for(Colour.BRIGHT_CYAN)
        else:
            label = t.label
            attr = curses.A_NORMAL
        _put(stdscr, r, x, label, attr)
        x += _width(label)


def _pack_scroll_offset(selected: int, count: int, visible: int) -> int:
    """Where the Pack tab's list column starts scrolling from (DELVE-0075), recomputed fresh every
    frame from the focused row alone: `ui` never remembers a scroll position across frames (rule 2,
    PLAN.md section 4's "the core never tracks a scroll offset" already covers the page counters
    `ui/app.py` owns; this extends the same no-state-carried-forward rule to the list). Clamps so
    the focused row always sits inside `[offset, offset + visible)`, and never scrolls past the end
    of a list that already fits."""
    if visible <= 0 or count <= visible:
        return 0
    offset = max(0, selected - visible + 1)
    return min(offset, count - visible)


def _draw_pack_columns(stdscr, view: InfoView, r: int, col: int, bottom: int) -> None:
    """The Pack tab's list-plus-description layout (DELVE-0075, replacing DELVE-0069's list/detail
    toggle): a compact list on the left, the focused row's own description on the right, always
    both visible with no confirm/back step. The focused row's name is marked by highlighting it in
    the list (a full-width reverse-video block, the same `bar_attr` treatment used elsewhere for a
    filled highlight, DELVE-0076 moving it off the description, DELVE-0075's original spot); the
    description column draws its lines through `_put_line`, the same styled-segment path every
    other panel uses (DELVE-0078 fixed this column silently flattening its segments to plain text,
    which had been discarding `_title_block`'s own bold title styling). The list scrolls
    (`_pack_scroll_offset`) once the carried-kind count outgrows its own visible rows."""
    visible = max(0, bottom - r)
    offset = _pack_scroll_offset(view.pack_selected, len(view.pack_rows), visible)
    sep_col = col + PACK_LIST_W + 1
    for dr in range(visible):
        _put(stdscr, r + dr, sep_col, "│")
    for i in range(offset, min(offset + visible, len(view.pack_rows))):
        label = view.pack_rows[i]
        text = label if _width(label) <= PACK_LIST_W else label[: PACK_LIST_W - 1] + "…"
        attr = attrs.bar_attr(Colour.CYAN) if i == view.pack_selected else curses.A_NORMAL
        _put(stdscr, r + (i - offset), col, text.ljust(PACK_LIST_W), attr)
    desc_col = sep_col + 2
    dr = r
    for block in _blocks(view.body, PACK_DESC_W):
        for quote, segs in block:
            if dr >= bottom:
                break
            _put_line(stdscr, dr, desc_col, quote, segs)
            dr += 1


def _draw_grader_columns(stdscr, view: InfoView, r: int, col: int, bottom: int) -> None:
    """The Grader tab's side-by-side Grading / Ambient toast sections (DELVE-0087): the same
    vertical-divider arithmetic as Pack (`GRADER_COL_W` / `GRADER_COL_RIGHT_W`), but both panes
    are ordinary paginated text blocks rather than a list-plus-description. Each column wraps to
    its own half-width so the Model/This run two-line strings session already prepared fit
    without running past the divider."""
    visible = max(0, bottom - r)
    sep_col = col + GRADER_COL_W + 1
    for dr in range(visible):
        _put(stdscr, r + dr, sep_col, "│")
    dr = r
    for block in _blocks(view.grader_left, GRADER_COL_W):
        for quote, segs in block:
            if dr >= bottom:
                break
            _put_line(stdscr, dr, col, quote, segs)
            dr += 1
    right_col = sep_col + 2
    dr = r
    for block in _blocks(view.grader_right, GRADER_COL_RIGHT_W):
        for quote, segs in block:
            if dr >= bottom:
                break
            _put_line(stdscr, dr, right_col, quote, segs)
            dr += 1


def _draw_info(stdscr, view: InfoView | HelpView, top: int, col: int, h: int, page: int) -> None:
    view = _fill_status_size(stdscr, view)
    r = top + 2
    x = col
    if view.title:
        _put(stdscr, r, x, view.title, curses.A_BOLD)
        x += _width(view.title) + 3
    _draw_tab_row(stdscr, r, x, view.tabs, view.active, not view.sub_focus)
    r += 1
    if view.subtabs:
        _draw_tab_row(stdscr, r, col, view.subtabs, view.active_sub, view.sub_focus)
        r += 1
    r += 1
    if isinstance(view, InfoView) and view.pack_rows:
        _draw_pack_columns(stdscr, view, r, col, top + h - 2)
        _put(stdscr, top + h - 2, col, view.end_label)
        return
    if isinstance(view, InfoView) and view.grader_left:
        _draw_grader_columns(stdscr, view, r, col, top + h - 2)
        _put(stdscr, top + h - 2, col, view.end_label)
        return
    pages = _text_pages(view, h - CHROME)      # same body the box was sized to, so the tail aligns
    page = max(1, min(page, len(pages)))
    for quote, segs in pages[page - 1]:
        _put_line(stdscr, r, col, quote, segs)
        r += 1
    tail = view.more_label if page < len(pages) else view.end_label
    if len(pages) > 1:
        counter = view.page_fmt.format(page=page, total=len(pages))
        tail = tail.ljust(max(len(tail) + 1, TEXT_W - len(counter))) + counter   # right-align it
    _put(stdscr, top + h - 2, col, tail)


def draw_toast(stdscr, view: ToastView, map_cols: int, player_x: int = 0) -> None:
    """The ambient room-entry toast (DELVE-0060): unlike every other panel this file draws, this
    one is never the sole thing on screen, so it takes no `page` (there is no pager chrome, no
    (end), nothing to page through) and no overlay-exclusivity; the caller (`ui/render.py`) only
    calls this when it decides to, independent of whatever `overlay` is or isn't showing.

    Anchored top-left or top-right, whichever side the learner is *not* standing on (`player_x`,
    the learner's own map column, `ui/render.py:_player_x`): a fixed corner used to overlay
    whichever room the learner currently stood in happened to reach that far across the screen (a
    play-testing report against the tutorial's second room). This is a per-frame decision, not
    sticky state, so the toast can visibly hop sides if the learner walks across the midpoint
    while it is still up; that is judged less confusing than a toast that stays put over the room
    once the learner has moved well past the midpoint.

    Body blocks are wrapped through `_wrap_block_lines` (not a bare `_wrap` of the joined text),
    so a block whose `spans` carry a `**bold**` run (`RunState._poll_toast`, via `content.markup.
    inline_spans`) renders bold here too, the same as any other panel's styled text, instead of
    showing the literal asterisks a model occasionally reaches for."""
    rows, cols = stdscr.getmaxyx()
    width = min(cols, map_cols)
    left = 0 if player_x >= width // 2 else max(0, width - TOAST_W)
    col = left + 2
    lines = [line for block in view.body for line in _wrap_block_lines(block, TOAST_TEXT_W)]
    max_lines = max(1, (rows - 3) - TOAST_TOP - 4)   # never run into the status/hint rows
    lines = lines[:max_lines]
    height = 4 + len(lines)
    _box(stdscr, TOAST_TOP, left, height, TOAST_W)
    _put(stdscr, TOAST_TOP + 1, col, view.title[:TOAST_TEXT_W], curses.A_BOLD)
    for i, segs in enumerate(lines):
        _put_line(stdscr, TOAST_TOP + 3 + i, col, False, segs)


def draw_toast_loading(stdscr, text: str, map_cols: int, player_x: int = 0) -> None:
    """The toast's own "still generating" spinner window (DELVE-0082), shown by `ui/render.py` in
    place of `draw_toast` while the call behind it is still running: the same corner-anchoring
    logic as `draw_toast` (top-left/top-right, whichever side the learner isn't standing on), but
    smaller (no title row, since there is nothing yet to title) and with the spinner glyph
    prefixing the wrapped text's first line; every continuation line indents to sit under it."""
    rows, cols = stdscr.getmaxyx()
    width = min(cols, map_cols)
    left = 0 if player_x >= width // 2 else max(0, width - TOAST_W)
    col = left + 2
    glyph = _spinner_glyph(time.monotonic() * 1000)
    lines = _wrap(text, TOAST_TEXT_W - 2) or [""]
    max_lines = max(1, (rows - 3) - TOAST_TOP - 2)   # never run into the status/hint rows
    lines = lines[:max_lines]
    height = 2 + len(lines)
    _box(stdscr, TOAST_TOP, left, height, TOAST_W)
    _put(stdscr, TOAST_TOP + 1, col, f"{glyph} {lines[0]}")
    for i, line in enumerate(lines[1:], start=1):
        _put(stdscr, TOAST_TOP + 1 + i, col + 2, line)


def _draw_menu(stdscr, view: MenuView, top: int, col: int) -> None:
    r = top + 2
    for line in _wrap(view.prompt, TEXT_W):
        _put(stdscr, r, col, line)
        r += 1
    r += 1
    for i, item in enumerate(view.items):
        lines = _wrap(item.text, TEXT_W - 4)
        # Pet strike and paid elimination both dim the text; elimination additionally dims the
        # badge, so a removed option reads as gone rather than merely crossed off (DELVE-0018).
        base = curses.A_DIM if (item.struck or item.eliminated) else curses.A_NORMAL
        if item.eliminated:
            badge = curses.A_DIM
        else:
            badge = attrs.bar_attr(Colour.CYAN) if i == view.selected else curses.A_NORMAL
        _put(stdscr, r, col, f" {item.key} ", badge)
        for dr, line in enumerate(lines):
            _put(stdscr, r + dr, col + 4, line, base)
        r += len(lines)
    r += 1
    _put(stdscr, r, col, view.footer)


def _draw_amount(stdscr, view: AmountView, top: int, col: int) -> None:
    r = top + 2
    for line in _wrap(view.prompt, TEXT_W):
        _put(stdscr, r, col, line)
        r += 1
    r += 1
    # A single-line input box, mimicking a form field: the typed digits sit inside it with a block
    # cursor after them, so it reads as somewhere to type rather than a number that just changes.
    s = _FIELD
    fw = 22
    _put(stdscr, r, col, s["tl"] + s["h"] * (fw - 2) + s["tr"])
    _put(stdscr, r + 1, col, s["v"] + " " * (fw - 2) + s["v"])
    _put(stdscr, r + 1, col + 2, view.typed, curses.A_BOLD)
    _put(stdscr, r + 1, col + 2 + len(view.typed), " ", curses.A_REVERSE)   # the cursor
    _put(stdscr, r + 2, col, s["bl"] + s["h"] * (fw - 2) + s["br"])
    r += 4
    _put(stdscr, r, col, view.footer)                                        # the range, "1 to N"


def _draw_freetext(stdscr, view: FreeTextView, top: int, col: int) -> None:
    """A free-text question: the prompt, then a wide single-line input box holding the typed answer
    with a block cursor (Phase 2). The same field look as the amount box, but spanning the panel so
    a short sentence fits; the tail of a long answer scrolls into view rather than overflowing."""
    r = top + 2
    for line in _wrap(view.prompt, TEXT_W):
        _put(stdscr, r, col, line)
        r += 1
    r += 1
    s = _FIELD
    fw = TEXT_W
    inner = fw - 4                                       # writable width between the padding
    shown = view.typed[-inner:] if len(view.typed) > inner else view.typed
    _put(stdscr, r, col, s["tl"] + s["h"] * (fw - 2) + s["tr"])
    _put(stdscr, r + 1, col, s["v"] + " " * (fw - 2) + s["v"])
    _put(stdscr, r + 1, col + 2, shown, curses.A_BOLD)
    _put(stdscr, r + 1, col + 2 + len(shown), " ", curses.A_REVERSE)          # the cursor
    _put(stdscr, r + 2, col, s["bl"] + s["h"] * (fw - 2) + s["br"])
    r += 4
    _put(stdscr, r, col, view.footer)                                        # the question counter


def _draw_grading(stdscr, view: GradingView, top: int, col: int) -> None:
    """The pending-grade pause: the title, the learner's answer quoted, and a 'thinking' body while
    a slow (LLM) grade runs on a worker. Static; the UI polls for the verdict (PHASE2.md 5.3)."""
    r = top + 2
    _put(stdscr, r, col, view.title, curses.A_BOLD)
    r += 2
    for line in _wrap(f'"{view.answer}"', TEXT_W):
        _put(stdscr, r, col, line, attrs.attr_for(Colour.BRIGHT_CYAN))
        r += 1
    r += 1
    for line in _wrap(view.body, TEXT_W):
        _put(stdscr, r, col, line)
        r += 1


def _draw_prompt(stdscr, view: PromptView, top: int, col: int) -> None:
    """An assertion is a numbered-style list, the same look and navigation as an MCQ (its answers
    are few, so buttons bought nothing over a list). Each choice is a key badge (its first letter,
    the key that answers it) then the label; only the focused choice's badge is highlighted, the
    same treatment as the MCQ list, and a pet-struck choice is dimmed."""
    r = top + 2
    for line in _wrap(view.text, TEXT_W):
        _put(stdscr, r, col, line)
        r += 1
    r += 1
    struck = view.struck or (False,) * len(view.choices)
    elim = view.eliminated or (False,) * len(view.choices)
    for i, choice in enumerate(view.choices):
        lines = _wrap(choice, TEXT_W - 4)
        gone = i < len(elim) and elim[i]
        ruled = i < len(struck) and struck[i]
        base = curses.A_DIM if (ruled or gone) else curses.A_NORMAL
        if gone:
            badge = curses.A_DIM
        else:
            badge = attrs.bar_attr(Colour.CYAN) if i == view.selected else curses.A_NORMAL
        _put(stdscr, r, col, f" {choice[:1].lower()} ", badge)
        for dr, line in enumerate(lines):
            _put(stdscr, r + dr, col + 4, line, base)
        r += len(lines)
    r += 1
    _put(stdscr, r, col, view.footer)
