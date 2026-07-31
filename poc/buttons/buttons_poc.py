#!/usr/bin/env python3
"""A stand-alone proof of concept for the answer buttons proposed in docs/BUTTONS.md.

It is deliberately self-contained: it imports nothing from `delve`, opens its own curses screen,
and draws the examination panel for every question type so you can feel them before any of it is
built into the game. Run it and press Tab to cycle; nothing here touches the real UI.

    python3 poc/buttons/buttons_poc.py

  Demos (Tab cycles):
    1. MCQ (3+ options) - a plain numbered list; the button style is not used here      (BUTTONS.md 5)
    2. Assertion        - two boxed buttons side by side (True / False)                  (BUTTONS.md 4)
    3. Yes / No prompt  - the same two buttons for a [yn] confirmation
    4. Free text        - a boxed input line you type an answer into                     (Phase 2)

Buttons are for **binary** questions only (an assertion, a yes/no prompt); a 3+ option MCQ stays a
list, and a free-text question is a typed input line.

  Keys (choice demos):
    arrows / hjkl   move the selection
    1-4 / w n / y   jump straight to an option (also selects it)
    Enter / Space   choose the selected option
    Tab next   c colour on/off   q quit

  Keys (the free-text demo):
    type   the answer   Backspace delete   Enter submit   Tab next   Esc quit

**Only the selected choice gets a background** on its key badge (black-on-cyan, or reverse video with
colour off), so the selection stands out even in black and white; resting choices are plain. 16
colours only; no emoji.
"""

import curses

PANEL_W = 73
TEXT_W = 69  # inner writable width, matching windows.PANEL_W / TEXT_W

# Sample content, lifted from docs/SCREENS.md and packs/freetext-demo so the widths are realistic.
MCQ_PROMPT = ("An email appearing to come from your CEO asks you to urgently buy gift cards for a "
              "client, and to keep it quiet until the deal closes. What is the strongest single "
              "signal that this is an attack?")
MCQ_OPTIONS = [
    "Gift cards are an unusual business expense",
    "It combines manufactured urgency with a request to bypass normal purchasing",
    "A CEO would not normally email someone in your role directly",
    "The message came by email rather than in person",
]
ASSERT_TEXT = "Bad spelling and grammar are a reliable way to spot phishing."
ASSERT_LABELS = ["True", "False"]
YESNO_TEXT = "You left this training unfinished. Descend again where you stood?"
YESNO_LABELS = ["Yes", "No"]
FREETEXT_PROMPT = "In one word, name the feeling a phishing email manufactures to stop you thinking."

_FOCUS = 1   # the selected badge: black on cyan


def _init_colours():
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(_FOCUS, curses.COLOR_BLACK, curses.COLOR_CYAN)


def _badge_attr(colour_on, selected=False):
    """Only the selected choice gets a background, so the selection is visible even in black and
    white: selected is black-on-cyan (reverse video with colour off), a resting choice is plain."""
    if not selected:
        return curses.A_NORMAL
    if colour_on:
        return curses.color_pair(_FOCUS) | curses.A_BOLD
    return curses.A_REVERSE | curses.A_BOLD


def _wrap(text, width):
    words, lines, line = text.split(), [], ""
    for w in words:
        if len(line) + len(w) + (1 if line else 0) <= width:
            line = f"{line} {w}" if line else w
        else:
            lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines or [""]


def _panel(stdscr, rows, cols):
    """A centred box the size of the game's lesson panel; returns the interior window."""
    h = min(rows - 2, 24)
    top = (rows - h) // 2
    left = max(0, (cols - PANEL_W) // 2)
    win = stdscr.derwin(h, PANEL_W, top, left)
    win.erase()
    win.box()
    return win


def _put(win, r, c, text, attr=curses.A_NORMAL):
    try:
        win.addstr(r, c, text, attr)
    except curses.error:
        pass  # a write to the last cell throws; harmless in a POC


def _draw_prompt(win, prompt, top):
    r = top
    for line in _wrap(prompt, TEXT_W):
        _put(win, r, 2, line)
        r += 1
    return r + 1


def _draw_mcq_list(win, state, colour_on):
    """A 3+ option MCQ stays a numbered list (no buttons); only the selected number is highlighted."""
    focus = state["focus"]
    r = _draw_prompt(win, MCQ_PROMPT, 1)
    for i, text in enumerate(MCQ_OPTIONS):
        lines = _wrap(text, TEXT_W - 5)
        _put(win, r, 2, f" {i + 1} ", _badge_attr(colour_on, i == focus))
        for dr, line in enumerate(lines):
            _put(win, r + dr, 6, line)
        r += len(lines)


def _two_buttons(win, r, labels, keys, focus, colour_on):
    """Two boxed buttons side by side (BUTTONS.md 4), for a binary question; only the selected
    button's badge is highlighted, so it stands out with colour on or off."""
    box_w = 33
    for i, label in enumerate(labels):
        left = 2 + i * (box_w + 2)
        inner = box_w - 2
        _put(win, r, left, "┌" + "─" * inner + "┐")
        _put(win, r + 1, left, "│" + " " * inner + "│")
        _put(win, r + 1, left + 2, f" {keys[i]} ", _badge_attr(colour_on, i == focus))
        _put(win, r + 1, left + 6, label)
        _put(win, r + 2, left, "└" + "─" * inner + "┘")


def _draw_assertion(win, state, colour_on):
    r = _draw_prompt(win, ASSERT_TEXT, 1)
    _two_buttons(win, r, ASSERT_LABELS, ["w", "n"], state["focus"], colour_on)


def _draw_yesno(win, state, colour_on):
    r = _draw_prompt(win, YESNO_TEXT, 1)
    _two_buttons(win, r, YESNO_LABELS, ["y", "n"], state["focus"], colour_on)


def _draw_freetext(win, state, colour_on):
    """A free-text question (Phase 2): the prompt, then a boxed single-line input holding the typed
    answer with a block cursor, the same field look the game's _draw_freetext uses."""
    typed = state["typed"]
    r = _draw_prompt(win, FREETEXT_PROMPT, 1)
    fw = TEXT_W
    inner = fw - 4
    shown = typed[-inner:] if len(typed) > inner else typed
    _put(win, r, 2, "┌" + "─" * (fw - 2) + "┐")
    _put(win, r + 1, 2, "│" + " " * (fw - 2) + "│")
    _put(win, r + 1, 4, shown, curses.A_BOLD)
    _put(win, r + 1, 4 + len(shown), " ", curses.A_REVERSE)   # the block cursor
    _put(win, r + 2, 2, "└" + "─" * (fw - 2) + "┘")


# Each demo: title, draw(win, state, colour_on), option count, jump keys, and whether it is a typed
# free-text field rather than a choice.
DEMOS = [
    ("MCQ - list, 3+ options (BUTTONS.md 5)", _draw_mcq_list, 4, ["1", "2", "3", "4"], False),
    ("Assertion - two buttons (BUTTONS.md 4)", _draw_assertion, 2, ["w", "n"], False),
    ("Yes / No prompt - two buttons", _draw_yesno, 2, ["y", "n"], False),
    ("Free text - typed answer (Phase 2)", _draw_freetext, 0, [], True),
]


def main(stdscr):
    curses.curs_set(0)
    has_colour = curses.has_colors()
    if has_colour:
        _init_colours()
    colour_on = has_colour
    demo = 0
    state = {"focus": 0, "typed": ""}
    result = None

    while True:
        title, draw, count, keys, is_text = DEMOS[demo]
        stdscr.erase()
        rows, cols = stdscr.getmaxyx()
        _put(stdscr, 0, 2, f"Delve answer buttons - proof of concept   [{title}]", curses.A_BOLD)
        if is_text:
            hint = "type the answer   Backspace delete   Enter submit   Tab next   Esc quit"
        else:
            hint = ("arrows/hjkl move   Enter choose   1-4/w-n/y jump   Tab next   "
                    "c colour:%s   q quit" % ("on" if colour_on else "off"))
        _put(stdscr, rows - 2, 2, hint)
        if result is not None:
            _put(stdscr, rows - 1, 2, result)
        win = _panel(stdscr, rows, cols)
        draw(win, state, colour_on)
        stdscr.refresh()
        win.refresh()

        ch = stdscr.getch()
        if ch == ord("\t"):                              # next demo (works in every mode)
            demo = (demo + 1) % len(DEMOS)
            state = {"focus": 0, "typed": ""}
            result = None
        elif is_text:
            if ch == 27:                                 # Esc quits (q is a typable letter here)
                return
            elif ch in (ord("\n"), ord("\r"), curses.KEY_ENTER):
                result = f"You answered: {state['typed']!r}"
            elif ch in (curses.KEY_BACKSPACE, 127, 8):
                state["typed"] = state["typed"][:-1]
            elif 32 <= ch < 127:
                state["typed"] += chr(ch)
        else:
            if ch in (ord("q"), 27):
                return
            elif ch == ord("c") and has_colour:
                colour_on = not colour_on
            elif ch in (curses.KEY_DOWN, ord("j"), curses.KEY_RIGHT, ord("l")):
                state["focus"] = (state["focus"] + 1) % count
            elif ch in (curses.KEY_UP, ord("k"), curses.KEY_LEFT, ord("h")):
                state["focus"] = (state["focus"] - 1) % count
            elif ch in (ord("\n"), ord(" ")):
                result = f"You chose: {keys[state['focus']]}"
            else:
                for i, k in enumerate(keys):
                    if ch == ord(k):
                        state["focus"], result = i, f"You chose: {k}"


if __name__ == "__main__":
    curses.wrapper(main)
