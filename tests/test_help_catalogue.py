"""The drift guard for DELVE-0028's help catalogue: `session/help.py`'s `CATALOGUE` and
`ui/keys.py`'s actual bindings must agree, or the Keys tab could silently omit a reachable key or
invent one that does nothing. Checked in both directions for every key `ui.keys` can mechanically
be driven with a synthetic overlay; the pager chrome (space/'-', handled directly in `ui/app.py`,
never a session Command per that module's own docstring) is `chrome=True` in the catalogue and
exempt, since there is nothing in `ui.keys` to cross-check it against.
"""

import curses

from delve.session import help as help_catalogue
from delve.session.commands import (
    Answer,
    Ascend,
    Confirm,
    Consult,
    Descend,
    Dismiss,
    Drop,
    Help,
    Inventory,
    Move,
    Pickup,
    Rest,
    Select,
    Talk,
    Wait,
)
from delve.session.views import AmountView, HelpView, MenuItem, MenuView, PromptView
from delve.ui import keys

ESC = keys.ESC

# Walking: ui.keys._WALK's key -> the catalogue's own (multi-arrow) label for it, so the two
# tables can be compared despite the catalogue describing all four arrows as one row.
_WALK_LABEL = {
    curses.KEY_LEFT: "←↑→↓", curses.KEY_RIGHT: "←↑→↓",
    curses.KEY_UP: "←↑→↓", curses.KEY_DOWN: "←↑→↓",
    ord("t"): "t", ord("s"): "s", ord(">"): ">", ord("<"): "<", ord(","): ",",
    ord("d"): "d", ord("i"): "i", ord(" "): "Space", ord("q"): "q",
    ord("?"): "?",
}


def test_every_walk_binding_is_documented_in_the_walking_context():
    entries = {e.key for e in help_catalogue.entries_for("walking") if not e.chrome}
    for ch, label in _WALK_LABEL.items():
        assert keys.walk_command(ch) is not None
        assert label in entries, f"{label!r} ({ch}) is bound but not documented for walking"


def test_every_documented_walking_key_is_actually_bound():
    codes_by_label: dict[str, list[int]] = {}
    for ch, label in _WALK_LABEL.items():
        codes_by_label.setdefault(label, []).append(ch)
    for e in help_catalogue.entries_for("walking"):
        if e.chrome:
            continue
        codes = codes_by_label.get(e.key)
        assert codes, f"{e.key!r} is documented for walking but ui.keys has no such binding"
        assert all(keys.walk_command(c) is not None for c in codes)


def test_walk_command_matches_are_the_expected_commands():
    """Not just "bound", but bound to what the description implies (a light sanity check that a
    label and a Command haven't drifted apart, e.g. a key repurposed without updating help.py)."""
    expect = {
        curses.KEY_LEFT: Move, ord("t"): Talk, ord("s"): Rest, ord(">"): Descend,
        ord("<"): Ascend, ord(","): Pickup, ord("d"): Drop, ord("i"): Inventory,
        ord(" "): Wait, ord("?"): Help,
    }
    for ch, cls in expect.items():
        assert isinstance(keys.walk_command(ch), cls)


def test_p_is_retired_the_message_log_lives_in_the_info_panel_now():
    # A playtesting request: the message log merged into Info as its own tab, so its former
    # standalone 'p' shortcut is gone, not repurposed.
    assert keys.walk_command(ord("p")) is None
    assert not any(e.key == "p" for e in help_catalogue.entries_for("walking"))


# -- the universal keys: ? (help) and Esc (dismiss), everywhere the catalogue claims them --------


_OVERLAY_FOR_CONTEXT = {
    "lesson": lambda: HelpView(tabs=[], active=0, body=[]),  # any TextView-shaped stand-in works;
    "explanation": lambda: HelpView(tabs=[], active=0, body=[]),  # Esc/? never branch on content
    "scroll": lambda: HelpView(tabs=[], active=0, body=[]),
    "repelled": lambda: HelpView(tabs=[], active=0, body=[]),
    "info": lambda: HelpView(tabs=[], active=0, body=[]),
    "drop_menu": lambda: MenuView(prompt="", items=[MenuItem("1", "x")]),
    "pickup_menu": lambda: MenuView(prompt="", items=[MenuItem("1", "x")]),
    "drop_amount": lambda: AmountView(prompt="", typed="", maximum=9, footer=""),
    "pickup_amount": lambda: AmountView(prompt="", typed="", maximum=9, footer=""),
    "question_mcq": lambda: MenuView(prompt="", items=[MenuItem("1", "x")]),
    "question_assertion": lambda: PromptView(text="", choices=("Yes", "No")),
}


def test_question_mark_opens_help_in_every_context_the_catalogue_claims():
    entries = help_catalogue.entries_for("walking")
    assert any(e.key == "?" for e in entries)   # walking checked separately, via walk_command
    for context, build in _OVERLAY_FOR_CONTEXT.items():
        assert any(e.key == "?" for e in help_catalogue.entries_for(context)), context
        assert keys.panel_command(ord("?"), build()) == Help(), context


def test_esc_dismisses_in_every_context_the_catalogue_claims():
    for context, build in _OVERLAY_FOR_CONTEXT.items():
        assert any(e.key == "Esc" for e in help_catalogue.entries_for(context)), context
        assert keys.panel_command(ESC, build()) == Dismiss(), context


# -- per-widget contexts: drop/pickup menus, the amount field, the two question kinds -------------


def test_drop_and_pickup_menu_keys_match_the_catalogue():
    for context in ("drop_menu", "pickup_menu"):
        entries = {e.key for e in help_catalogue.entries_for(context)}
        assert "1-9" in entries
        view = MenuView(prompt="", items=[MenuItem("1", "a"), MenuItem("2", "b")])
        assert keys.panel_command(ord("1"), view) == Answer(0)
        assert keys.panel_command(ord("2"), view) == Answer(1)


def test_amount_field_keys_match_the_catalogue():
    for context in ("drop_amount", "pickup_amount"):
        entries = {e.key for e in help_catalogue.entries_for(context)}
        assert entries == {"0-9", "Backspace", "Enter", "?", "Esc"}
        view = AmountView(prompt="", typed="", maximum=9, footer="")
        assert keys.panel_command(ord("5"), view) is not None
        assert keys.panel_command(ord("\n"), view) == Confirm(True)


def test_question_mcq_keys_match_the_catalogue():
    entries = {e.key for e in help_catalogue.entries_for("question_mcq")}
    assert entries == {"1-9", "←→ / Enter", "@", "?", "Esc"}
    view = MenuView(prompt="", items=[MenuItem("1", "a")])
    assert keys.panel_command(ord("1"), view) == Answer(0)
    assert keys.panel_command(ord("@"), view) == Consult()
    assert keys.panel_command(curses.KEY_UP, view) == Select(-1)


def test_question_assertion_keys_match_the_catalogue():
    entries = {e.key for e in help_catalogue.entries_for("question_assertion")}
    assert entries == {"←→ / Enter", "@", "?", "Esc"}
    view = PromptView(text="", choices=("Yes", "No"))
    assert keys.panel_command(ord("@"), view) == Consult()
    assert keys.panel_command(ord("y"), view) == Answer(0)


def test_question_freetext_has_no_consult_entry():
    # Free text is typed raw through a separate path (app.py's _freetext_command), never
    # panel_command, so @ has no meaning there; the catalogue must not claim it does.
    entries = {e.key for e in help_catalogue.entries_for("question_freetext")}
    assert "@" not in entries


def test_info_and_help_tab_strip_keys_match_the_catalogue():
    for context in ("info", "help"):
        # Only 'info' actually carries subtab_cycle/focus_row; both share tab_cycle.
        entries = {e.key for e in help_catalogue.entries_for(context)}
        assert "Tab / →←" in entries
    view = HelpView(tabs=[], active=0, body=[])
    from delve.session.commands import TabCycle
    assert keys.panel_command(ord("\t"), view) == TabCycle(1)
    assert keys.panel_command(curses.KEY_BTAB, view) == TabCycle(-1)


# -- every catalogue context is a context `RunState._help_context` can actually produce -----------


def test_every_catalogue_context_is_a_real_overlay_kind():
    real = {
        "walking", "lesson", "explanation", "question_mcq", "question_assertion",
        "question_freetext", "grading", "scroll", "info", "help", "drop_menu", "drop_amount",
        "pickup_menu", "pickup_amount", "repelled",
    }
    seen = {c for e in help_catalogue.CATALOGUE for c in e.contexts}
    assert seen <= real
