"""The curses bootstrap and the input loop: key -> Command -> Frame -> draw.

The only place curses is touched. It holds no game logic: it asks the learner's name, opens the
pilot pack and the store through `session.launch`, offers to resume an unfinished run, then pumps
commands into `session`, painting whatever Frame comes back. Lesson pagination is the one bit of
state the UI owns (PLAN.md section 4 keeps scroll offset out of the core): the app tracks the page
and emits Confirm only when space is pressed on the last page.

Everything below `session.launch` (the store, the pack, the RunState) is held opaquely and passed
straight back; the UI never imports `progress` or `content` (rule 2).
"""

import curses
import locale
import textwrap

from delve.session import launch
from delve.session.commands import Backspace, Confirm, Dismiss, GradeReady, Quit, Type
from delve.session.views import (
    FreeTextView,
    GradingView,
    HelpView,
    InfoView,
    MenuView,
    PromptView,
    TextView,
)
from delve.ui import attrs, keys, render, terminal, windows

# How often (ms) the UI wakes to poll a pending free-text grade running on a worker (PHASE2.md
# 5.3). Short enough to feel instant when the model answers, long enough not to spin the CPU.
_GRADE_POLL_MS = 120

# How often (ms) the UI wakes to check for a resolved ambient room-entry toast (DELVE-0060) while
# walking. Less urgent than a grade (nothing is waiting on it, unlike "Checking your answer..."),
# so a slower tick than _GRADE_POLL_MS is enough not to spin the CPU during ordinary idle walking.
_TOAST_POLL_MS = 300

# ncurses' ESCDELAY (DELVE-0079): how long it waits after reading a lone `\x1b` for more bytes to
# follow (an arrow/function key's own escape sequence) before delivering it as a standalone Esc.
# The default is 1000ms, which makes every panel's Esc-to-close feel like the app hung; 25ms is
# short enough to feel instant and still comfortably above a real terminal's own escape-sequence
# byte gap (the same value commonly recommended for this exact trade-off, e.g. Vim's own
# `ttimeoutlen` default guidance).
_ESC_DELAY_MS = 25


def _set_esc_delay() -> None:
    """Shrink ncurses' default ESCDELAY once at startup. Guarded: on a platform whose curses build
    lacks the `set_escdelay` extension, this is a no-op and the app just keeps that platform's
    default delay, exactly as it did before this fix."""
    try:
        curses.set_escdelay(_ESC_DELAY_MS)
    except AttributeError:
        pass


def _draw_centered(stdscr, lines: list[str], rows: int, cols: int) -> None:
    """Draw pre-built lines centred, wrapping any that would overrun the width so a whole sentence
    stays on screen (blank lines are kept, as vertical spacing). Truncation used to silently cut the
    win screen's outcome line off the right edge; wrapping fixes that and every other centred screen
    at once. `break_on_hyphens=False` so a hyphenated title like 'Free-Text Demo' stays whole."""
    width = min(max(cols - 4, 1), 76)
    wrapped: list[str] = []
    for line in lines:
        wrapped.extend(textwrap.wrap(line, width=width, break_on_hyphens=False) if line else [""])
    top = max(0, (rows - len(wrapped)) // 2)
    for i, line in enumerate(wrapped):
        y = top + i
        if y >= rows:
            break
        x = max(0, (cols - len(line)) // 2)
        try:
            stdscr.addstr(y, x, line[: max(0, cols - x - 1)])
        except curses.error:
            pass


def _ensure_size(stdscr, need_cols: int, need_rows: int) -> bool:
    while True:
        rows, cols = stdscr.getmaxyx()
        if cols >= need_cols and rows >= need_rows:
            return True
        stdscr.erase()
        _draw_centered(stdscr, terminal.overlay_lines(cols, rows, need_cols, need_rows),
                       rows, cols)
        stdscr.refresh()
        if stdscr.getch() in (ord("q"), ord("Q")):
            return False


def _put(stdscr, y: int, x: int, text: str, attr: int = 0) -> None:
    try:
        stdscr.addstr(y, x, text, attr)
    except curses.error:
        pass


def _line_edit(buf: str, key, max_len: int) -> tuple[str, str]:
    """Apply one keypress to a text buffer. Returns (buffer, action) where action is 'edit',
    'submit' or 'cancel'. `key` is a str (a typed character, from get_wch) or an int (a special
    key). Kept pure and separate from curses so the editing rules are unit-testable."""
    if key in ("\n", "\r", curses.KEY_ENTER):
        return buf, "submit"
    if key == "\x1b":
        return buf, "cancel"
    if key in ("\x7f", "\b", curses.KEY_BACKSPACE):
        return buf[:-1], "edit"
    if isinstance(key, str) and key.isprintable() and len(buf) < max_len:
        return buf + key, "edit"
    return buf, "edit"


def _input_box(stdscr, prompt_lines: list[str], hint: str, *, max_len: int = 20,
               default: str = "", initial: str = "") -> str:
    """A boxed single-line text field, the same look as the drop-amount box: the prompt centred
    above, a single-line box holding the typed text with a block cursor, a hint below. Enter
    submits (a blank entry falls back to `default`); Backspace edits; Esc takes the default. Text
    comes through get_wch, so an accented name (Dutch) types correctly. `initial` pre-fills the box
    with an editable value (an env-var default), still shown as a prompt so the learner can accept
    or edit it."""
    curses.curs_set(0)
    buf = initial[:max_len]
    fw = max_len + 4
    while True:
        rows, cols = stdscr.getmaxyx()
        stdscr.erase()
        block_h = len(prompt_lines) + 5 + (1 if hint else 0)
        top = max(0, (rows - block_h) // 2)
        for i, line in enumerate(prompt_lines):
            _put(stdscr, top + i, max(0, (cols - len(line)) // 2), line)
        fy = top + len(prompt_lines) + 1
        fx = max(0, (cols - fw) // 2)
        shown = buf[:max_len]
        _put(stdscr, fy, fx, "┌" + "─" * (fw - 2) + "┐")
        _put(stdscr, fy + 1, fx, "│" + " " * (fw - 2) + "│")
        _put(stdscr, fy + 1, fx + 2, shown)
        _put(stdscr, fy + 1, fx + 2 + len(shown), " ", curses.A_REVERSE)      # the cursor
        _put(stdscr, fy + 2, fx, "└" + "─" * (fw - 2) + "┘")
        if hint:
            _put(stdscr, fy + 4, max(0, (cols - len(hint)) // 2), hint)
        stdscr.refresh()
        try:
            key = stdscr.get_wch()
        except curses.error:
            continue
        buf, action = _line_edit(buf, key, max_len)
        if action == "submit":
            return buf.strip() or default
        if action == "cancel":
            return default


def _ask_name(stdscr, strings, name_default: str | None = None) -> str:
    """NetHack's opening question, in a boxed input field (the same look as the drop-amount box). A
    blank answer falls back to a default, so the game always starts. `name_default` (from
    $DELVE_NAME) pre-fills the box as an editable value, in front of the built-in default."""
    return _input_box(stdscr, [strings("ui.who_are_you")], strings("ui.name_hint"),
                      max_len=20, default=name_default or strings("ui.default_name"),
                      initial=name_default or "")


def _ask_pet(stdscr, strings) -> str:
    """Choose a companion after the name, NetHack-style: a cat, a dog, or no one (PETS.md). The keys
    are localised (Dutch takes 'k'/'h' for kat/hond); English c/d/n stay accepted as a fallback."""
    rows, cols = stdscr.getmaxyx()
    cat = (strings("ui.pet_key_cat") or "c")[0]
    dog = (strings("ui.pet_key_dog") or "d")[0]
    none = (strings("ui.pet_key_none") or "n")[0]
    hint = strings("ui.pick_pet_hint", cat=cat, dog=dog, none=none)
    stdscr.erase()
    _draw_centered(stdscr, [strings("ui.pick_pet"), "", hint], rows, cols)
    stdscr.refresh()
    accept = {"cat": {ord(cat), ord(cat.upper()), ord("c")},
              "dog": {ord(dog), ord(dog.upper()), ord("d")},
              "none": {ord(none), ord(none.upper()), ord("n")}}
    while True:
        ch = stdscr.getch()
        for species, codes in accept.items():
            if ch in codes:
                return species


def _ask_yn(stdscr, question: str, strings, default_yes: bool) -> bool:
    """A one-key [yn] prompt, used for the resume offer. Enter/space take the default. The letters
    are localised (Dutch shows [Jn] and takes 'j'); 'y'/'n' stay accepted as a fallback."""
    rows, cols = stdscr.getmaxyx()
    yes = (strings("ui.yes_key") or "y")[0]
    no = (strings("ui.no_key") or "n")[0]
    suffix = f" [{yes.upper()}{no}]" if default_yes else f" [{yes}{no.upper()}]"
    accept_yes = {ord(yes), ord(yes.upper()), ord("y"), ord("Y")}
    accept_no = {ord(no), ord(no.upper()), ord("n"), ord("N")}
    stdscr.erase()
    _draw_centered(stdscr, [question + suffix], rows, cols)
    stdscr.refresh()
    while True:
        ch = stdscr.getch()
        if ch in accept_yes:
            return True
        if ch in accept_no:
            return False
        if ch in (ord("\n"), ord(" ")):
            return default_yes


def _show_win(stdscr, run) -> None:
    """The end-of-run screen (M8), shown once the scroll is put down. Lines come formatted and
    localised from the session (rule 2); this only centres them and waits for a key."""
    rows, cols = stdscr.getmaxyx()
    stdscr.erase()
    _draw_centered(stdscr, launch.outcome_lines(run), rows, cols)
    stdscr.refresh()
    stdscr.getch()


def _show_trophies(stdscr, lines: list[str], strings) -> None:
    """The trophy case across runs, shown at the start for anyone who has finished a pack before.
    Skipped silently when the collection is empty (a first-time learner sees nothing)."""
    if not lines:
        return
    rows, cols = stdscr.getmaxyx()
    body = [strings("ui.trophy_title"), ""] + lines + ["", strings("ui.press_any")]
    stdscr.erase()
    _draw_centered(stdscr, body, rows, cols)
    stdscr.refresh()
    stdscr.getch()


def _pick_companion(stdscr, strings, pet_species, pet_name, pet_name_defaults=None):
    """The companion choice for a fresh run: honour --pet if given, else ask. Returns (species,
    name); a chosen animal with a blank name falls back to its species default. `pet_name_defaults`
    (from $DELVE_CAT_NAME/$DELVE_DOG_NAME, keyed by species) pre-fills the name box as an editable
    value, chosen only once the species is known."""
    species = pet_species if pet_species is not None else _ask_pet(stdscr, strings)
    if species == "none":
        return "none", None
    name = pet_name
    if name is None:
        env = (pet_name_defaults or {}).get(species)
        name = _input_box(stdscr, [strings("ui.pet_name_" + species)], strings("ui.name_hint"),
                          max_len=20, default=env or strings("pet.default_" + species),
                          initial=env or "")
    return species, name


def _begin(stdscr, seed, name, pack, strings, tutorial, pet_species, pet_name, grader_runner,
           name_default=None, pet_name_defaults=None):
    """Resolve the learner, then start or resume their run. Returns (run, store)."""
    store = launch.open_store()
    if not name:
        name = _ask_name(stdscr, strings, name_default)
    _show_trophies(stdscr, launch.trophies(store, pack, name, strings), strings)
    pending = launch.pending_run(store, pack, name)
    rows, cols = stdscr.getmaxyx()
    if pending is not None and _ask_yn(
            stdscr, strings("ui.resume", name=name, pack=pack.title), strings, default_yes=True):
        # The companion is restored from the snapshot, so a resumed run asks nothing about it.
        run = launch.resume(store, pack, run_row=pending, name=name, strings=strings,
                            tutorial=tutorial, grader_runner=grader_runner)
    else:
        # A fresh run: offer to skip the orientation floor, defaulting to yes for a learner who
        # has finished a training before, to no for a newcomer (PLAN.md section 9).
        skip = False
        if tutorial is not None:
            skip = _ask_yn(stdscr, strings("ui.skip"), strings,
                           default_yes=launch.has_completed_run(store, name))
        species, pname = _pick_companion(stdscr, strings, pet_species, pet_name, pet_name_defaults)
        run = launch.start(store, pack, name=name, seed=seed, cols=cols, rows=rows,
                           strings=strings, tutorial=tutorial, skip_tutorial=skip,
                           pet_species=species, pet_name=pname, grader_runner=grader_runner)
    return run, store


def _run(stdscr, seed, name, pack, strings, tutorial, pet_species, pet_name, grader_runner,
         name_default=None, pet_name_defaults=None) -> None:
    curses.curs_set(0)
    stdscr.keypad(True)
    _set_esc_delay()
    attrs.init()                       # allocate the 16-colour pairs (no-op without colour)

    if not _ensure_size(stdscr, terminal.MIN_COLS, terminal.MIN_ROWS):
        return
    run, store = _begin(stdscr, seed, name, pack, strings, tutorial, pet_species, pet_name,
                        grader_runner, name_default, pet_name_defaults)

    try:
        _play(stdscr, run)
    finally:
        run.checkpoint()
        store.close()


def _freetext_command(stdscr):
    """One keypress on a free-text answer field -> a Command (Phase 2). Read through get_wch, so an
    accented answer (Dutch) types correctly: Enter submits, Esc puts it down, Backspace edits, and a
    printable character is appended. The session owns the buffer; this only names the intent."""
    try:
        key = stdscr.get_wch()
    except curses.error:
        return None
    if key in ("\n", "\r", curses.KEY_ENTER):
        return Confirm(True)
    if key == "\x1b":
        return Dismiss()
    if key in ("\x7f", "\b", curses.KEY_BACKSPACE):
        return Backspace()
    if isinstance(key, str) and key.isprintable():
        return Type(key)
    return None


def _play(stdscr, run) -> None:
    frame = run.frame()
    need_cols, need_rows = frame.map.cols, frame.map.rows + 3
    page = 1
    # `msg_page` is the UI-owned page offset for a top-line message too wide to fit (DELVE-0030),
    # the same kind of presentational state as the overlay `page` (PLAN.md section 4). It resets
    # when the visible message changes; while it lags the last page a --More-- is up and a keypress
    # advances it instead of acting.
    msg_page = 1
    last_overlay = id(frame.overlay) if frame.overlay is not None else None
    last_msg = frame.messages[-1] if frame.messages else ""
    render.draw(stdscr, frame, page, msg_page)

    while True:
        overlay = frame.overlay
        msg_pages = windows.message_pages(
            frame.messages[-1] if frame.messages else "", stdscr.getmaxyx()[1])

        # While a free-text answer is graded on a worker (the LLM), wake on a short timeout and poll
        # for the verdict rather than blocking on a key, so 'Checking...' can give way the instant
        # the grade lands (PHASE2.md 5.3). On the instant keyword floor this overlay never appears.
        if isinstance(overlay, GradingView):
            stdscr.timeout(_GRADE_POLL_MS)
            stdscr.getch()                     # wake on the timeout (or a stray key); ignore it
            frame = run.apply(GradeReady())
        # A free-text field reads UTF-8 characters, not the int keymap the rest of the loop uses,
        # then falls through to the shared win/resize/redraw tail below.
        elif isinstance(overlay, FreeTextView):
            stdscr.timeout(-1)
            cmd = _freetext_command(stdscr)
            if cmd is not None:
                frame = run.apply(cmd)
        else:
            # While walking with a room's ambient toast still in flight, wake on a short timeout
            # and rebuild the Frame rather than blocking on a key, so it appears the instant it
            # resolves (DELVE-0060's own follow-up): otherwise nothing rebuilds the Frame until the
            # learner's next keypress, so a toast that finished while they stood still only showed
            # up once they happened to move. `ch == -1` is curses' own "the timeout elapsed, no key
            # was pressed" signal, never a real key code, so it can't misfire on genuine input.
            if overlay is None and frame.toast_pending:
                stdscr.timeout(_TOAST_POLL_MS)
            else:
                stdscr.timeout(-1)
            ch = stdscr.getch()
            if overlay is None:
                if ch == -1:
                    frame = run.frame()
                else:
                    cmd = keys.walk_command(ch)
                    if isinstance(cmd, Quit):
                        break
                    if msg_page < len(msg_pages):
                        msg_page += 1      # a --More-- is up: this key reads on, it does not act
                    elif cmd is not None:
                        frame = run.apply(cmd)
            elif isinstance(overlay, (TextView, InfoView, HelpView)) and ch == ord(" "):
                if page < windows.page_count(overlay, stdscr.getmaxyx()[0]):
                    page += 1
                else:
                    frame = run.apply(Confirm(True))
            elif isinstance(overlay, (TextView, InfoView, HelpView)) and ch == ord("-"):
                page = max(1, page - 1)
            elif isinstance(overlay, (MenuView, PromptView)) and ch == ord(" "):
                pass  # space does nothing on a question; you answer it
            else:
                cmd = keys.panel_command(ch, overlay)
                if cmd is not None:
                    frame = run.apply(cmd)

        # The run is won once the scroll is lifted and then put down: the panel is gone and the
        # run reports finished. Show the win screen and end, rather than dropping back to the map.
        if run.finished and frame.overlay is None:
            render.draw(stdscr, frame, page, msg_page)
            _show_win(stdscr, run)
            break

        # A new panel (or none) resets the page counter; a repaint of the same one keeps it.
        new_overlay = id(frame.overlay) if frame.overlay is not None else None
        if new_overlay != last_overlay:
            page = 1
            last_overlay = new_overlay
        # A fresh top-line message restarts its --More-- paging; the same line keeps its place.
        new_msg = frame.messages[-1] if frame.messages else ""
        if new_msg != last_msg:
            msg_page = 1
            last_msg = new_msg

        if not _ensure_size(stdscr, need_cols, need_rows):
            break
        render.draw(stdscr, frame, page, msg_page)


def main(seed: int, name: str | None = None, pack=None, *, strings=None, tutorial=None,
         pet_species: str | None = None, pet_name: str | None = None, grader_runner=None,
         name_default: str | None = None, pet_name_defaults=None) -> int:
    """`python -m delve` entry: ask who you are, choose a companion, then play `pack` under curses.
    `pack`, `strings`, `tutorial` and `grader_runner` are handed in by the entry point, all held
    opaquely so ui imports only session (rule 2). `pet_species`/`pet_name` come from
    --pet/--pet-name; None asks at the start (PETS.md). `grader_runner` grades free text (Phase 2);
    the entry point has already required a reachable LLM grader before ui is ever reached
    (DELVE-0033), so ui has nothing to warn about here. `name_default`/`pet_name_defaults` are
    env-var defaults (resolved at the edge) that pre-fill the startup prompts as editable values;
    the prompt is still shown, so the ritual is unchanged."""
    if pack is None:                       # direct callers (tests) may omit it; default to pilot
        pack = launch.load_pilot()
    if strings is None:
        strings = launch.default_strings()
    # Enable UTF-8 output so the panel's double-line frame renders. This is the documented
    # curses idiom for non-ASCII output, distinct from the number/date formatting use CLAUDE.md
    # forbids (that one is process-global locale for %B month names; this is terminal encoding).
    locale.setlocale(locale.LC_ALL, "")
    curses.wrapper(_run, seed, name, pack, strings, tutorial, pet_species, pet_name, grader_runner,
                   name_default, pet_name_defaults)
    return 0
