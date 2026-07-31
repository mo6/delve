"""Keymap: a keypress -> a Command. The only thing the UI knows about intent.

Walking keys are the four arrow keys (DELVE-0038: no NetHack hjkl/yubn, and no diagonals,
since Delve's audience isn't NetHack veterans), t to talk, s to rest (M4), and '>'/'<' to
take the stairs between chapters (M5). The stairs commands are inert unless the learner
stands on the matching stairs, which the session decides, not the keymap.
Panel keys depend on the open overlay, so `panel_command` takes it: letters pick a menu option,
the two derived keys answer an assertion, @ consults the pet on a question (DELVE-0028 moved this
off ?, which now always means help), ? opens/closes help everywhere, Esc dismisses. Space and '-'
page the lesson and are handled in the app, which owns the page counter; they are not Commands.
Everything returned is a session Command, so nothing here reaches past `session` (PLAN.md
section 4, rule 2).
"""

import curses

from delve.session.commands import (
    Answer,
    Ascend,
    Backspace,
    Command,
    Confirm,
    Consult,
    Descend,
    Digit,
    Direction,
    Dismiss,
    Drop,
    FocusRow,
    Help,
    Inventory,
    Move,
    Pickup,
    Quit,
    Rest,
    Select,
    SubTabCycle,
    TabCycle,
    Talk,
    Wait,
)
from delve.session.views import AmountView, HelpView, InfoView, MenuView, PromptView

ESC = 27

_WALK: dict[int, Command] = {
    curses.KEY_LEFT: Move(Direction.W),
    curses.KEY_RIGHT: Move(Direction.E),
    curses.KEY_UP: Move(Direction.N),
    curses.KEY_DOWN: Move(Direction.S),
    ord("t"): Talk(),
    ord("s"): Rest(),
    ord(">"): Descend(),
    ord("<"): Ascend(),
    ord(","): Pickup(),
    ord("d"): Drop(),
    ord("i"): Inventory(),     # the message log lives inside here now, as the Messages tab
    ord(" "): Wait(),          # stand still a turn; the pet moves. Space pages inside an overlay.
    ord("q"): Quit(),
    ord("Q"): Quit(),
    ord("?"): Help(),
}


def walk_command(ch: int) -> Command | None:
    return _WALK.get(ch)


def panel_command(ch: int, overlay) -> Command | None:
    """A Command for a keypress while a panel is open, or None (space/'-'/unbound: app handles).

    Quit is intentionally absent here: inside a panel, q is an ordinary key, and Esc (Dismiss)
    is how you back out. `?` (Help) is checked ahead of every overlay-specific branch below, since
    it now means the same thing everywhere a panel can be open (DELVE-0028).
    """
    if ch == ESC:
        return Dismiss()
    if ch == ord("?"):
        return Help()   # always means help now (DELVE-0028), in every panel, over any overlay
    if isinstance(overlay, (InfoView, HelpView)):
        # While the Pack tab shows its compact row list (DELVE-0069, `overlay.pack_rows` non-empty
        # only there), up/down move the row focus instead of the tab-row FocusRow below: Pack has
        # no sub-tab strip to focus into, so this claims the same keys for its own list navigation
        # (reusing `Select` rather than a new Command). The focused row's description shows
        # alongside the list at all times (DELVE-0075), so there is no separate detail step for
        # Enter to open; Tab/Shift-Tab and '['/']' still fall through to cycle tabs regardless.
        if isinstance(overlay, InfoView) and overlay.pack_rows:
            if ch == curses.KEY_UP:
                return Select(-1)
            if ch == curses.KEY_DOWN:
                return Select(1)
        else:
            # Up/down move keyboard focus between the primary and sub-tab rows (DELVE-0056), always
            # a FocusRow regardless of whether the active tab has any sub-tab row to focus (rule 2:
            # `ui` maps a keypress to a Command, `session.apply` decides whether it does anything).
            # HelpView never carries any sub-tab, so FocusRow/SubTabCycle are harmless no-ops there;
            # only TabCycle (Keys <-> Objectives) does anything (`RunState._tab_cycle`).
            if ch == curses.KEY_UP:
                return FocusRow(-1)
            if ch == curses.KEY_DOWN:
                return FocusRow(1)
        # Tab/Shift-Tab and the left/right arrows (DELVE-0040/0041's horizontal-choice convention,
        # matching PromptView's two buttons) cycle whichever row `overlay.sub_focus` currently
        # points at, so the same keys reach the sub-tab strip once focus has moved there. '['/']'
        # keep their own direct, focus-independent route to the sub-tab strip (DELVE-0055).
        if ch in (ord("\t"), curses.KEY_RIGHT):
            return SubTabCycle(1) if overlay.sub_focus else TabCycle(1)
        if ch in (curses.KEY_BTAB, curses.KEY_LEFT):
            return SubTabCycle(-1) if overlay.sub_focus else TabCycle(-1)
        if ch == ord("]"):
            return SubTabCycle(1)
        if ch == ord("["):
            return SubTabCycle(-1)
        return None
    if isinstance(overlay, AmountView):
        # The drop-amount field: type digits, Backspace to fix, Enter to drop, Esc to cancel. A
        # typed number is easier than nudging a stepper for large counts (a play-testing note).
        if ord("0") <= ch <= ord("9"):
            return Digit(ch - ord("0"))
        if ch in (curses.KEY_BACKSPACE, 127, 8):
            return Backspace()
        if ch in (ord("\n"), ord("\r"), curses.KEY_ENTER):
            return Confirm(True)
        return None
    if ch == ord("@") and isinstance(overlay, (MenuView, PromptView)):
        return Consult()   # ask the pet about this question; costs its score (moved off ? at 0028)
    if isinstance(overlay, MenuView):
        # An MCQ list takes arrow focus + Enter as well as its direct number keys (the item menus
        # for drop/pickup ignore the focus, being answered purely by number).
        if ch in (curses.KEY_UP, curses.KEY_LEFT):
            return Select(-1)
        if ch in (curses.KEY_DOWN, curses.KEY_RIGHT):
            return Select(1)
        if ch in (ord("\n"), ord("\r"), curses.KEY_ENTER):
            return Confirm(True)
        idx = ch - ord("1")            # options and drop items are numbered 1..n (OBJECTS.md)
        if 0 <= idx < len(overlay.items):
            return Answer(idx)
    elif isinstance(overlay, PromptView):
        # The assertion's two buttons: arrows move the focus, Enter answers the focused one. Only
        # the arrows drive focus (not hjkl), since a label's own first letter is its direct key and
        # a label could start with h/j/k/l. Pressing that letter still answers straight away.
        if ch in (curses.KEY_LEFT, curses.KEY_UP):
            return Select(-1)
        if ch in (curses.KEY_RIGHT, curses.KEY_DOWN):
            return Select(1)
        if ch in (ord("\n"), ord("\r"), curses.KEY_ENTER):
            return Confirm(True)
        keys = [c[0].lower() for c in overlay.choices]
        if 0 <= ch < 0x110000 and chr(ch).lower() in keys:
            return Answer(keys.index(chr(ch).lower()))
    return None
