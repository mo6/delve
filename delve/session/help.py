"""The `?` help catalogue (DELVE-0028): one table pairing each command with its key label, a
localised description string id, and the contexts it is active in. `ui/keys.py` owns the actual
key -> Command bindings; this module owns what each key *means*. `test_help_catalogue.py`
(`tests/`) imports both and asserts they agree for the keys it can mechanically check, so a new
command can't quietly reach one without the other.

Contexts mirror `RunState._overlay_kind` (plus `"walking"` for no overlay), except that
`"question"` is split three ways (`question_mcq`/`question_assertion`/`question_freetext`,
`RunState._help_context`) since the real key differs by question kind, the same distinction
`_hint()` already makes.

An entry's `key` is the literal key label `ui` paints, duplicating `keys.py`'s binding by
convention, exactly as the `[hint]` strings already do (`session` cannot import `ui`, rule 2).
`chrome=True` marks a key `ui/app.py` handles directly on a paginated panel (space/'-' to page)
rather than through a session `Command`; those carry no keymap counterpart to check.
"""

from dataclasses import dataclass

# Keys shared by every paginated, TextView-shaped overlay: handled directly in `ui/app.py`'s page
# counter (space/'-'), never a session Command (`ui/keys.py`'s own docstring), so `chrome=True`.
_PAGER_CONTEXTS = frozenset({
    "lesson", "explanation", "repelled", "scroll", "info", "help",
})

# Every overlay Esc dismisses (Dismiss, checked before any overlay-specific handling in
# `panel_command`), and every one `?` opens help from (checked right after Esc).
_DISMISSIBLE = frozenset({
    "lesson", "explanation", "question_mcq", "question_assertion", "question_freetext",
    "scroll", "info", "drop_menu", "drop_amount", "pickup_menu", "pickup_amount",
    "repelled",
})
_HELP_REACHABLE = _DISMISSIBLE | {"walking"}


@dataclass(frozen=True)
class CommandEntry:
    key: str
    string_id: str
    contexts: frozenset[str]
    chrome: bool = False


CATALOGUE: tuple[CommandEntry, ...] = (
    # Walking (ui/keys.py's _WALK dict)
    CommandEntry("←↑→↓", "help.move", frozenset({"walking"})),
    CommandEntry("t", "help.talk", frozenset({"walking"})),
    CommandEntry("s", "help.rest", frozenset({"walking"})),
    CommandEntry(">", "help.descend", frozenset({"walking"})),
    CommandEntry("<", "help.ascend", frozenset({"walking"})),
    CommandEntry(",", "help.pickup", frozenset({"walking"})),
    CommandEntry("d", "help.drop", frozenset({"walking"})),
    CommandEntry("i", "help.inventory", frozenset({"walking"})),
    CommandEntry("Space", "help.wait", frozenset({"walking"})),
    CommandEntry("q", "help.quit", frozenset({"walking"})),
    # Universal: ? opens help everywhere it can be reached from; Esc dismisses every panel.
    CommandEntry("?", "help.help", _HELP_REACHABLE),
    CommandEntry("Esc", "help.dismiss", _DISMISSIBLE),
    # Pagination chrome, shared by every TextView/InfoView/HelpView-shaped overlay.
    CommandEntry("Space", "help.page_next", _PAGER_CONTEXTS, chrome=True),
    CommandEntry("-", "help.page_prev", _PAGER_CONTEXTS, chrome=True),
    # The lesson panel: Enter starts the examination.
    CommandEntry("Enter", "help.lesson_continue", frozenset({"lesson"})),
    # Examinations, split by question kind (the real key differs, same split `_hint()` makes).
    CommandEntry("1-9", "help.answer_many", frozenset({"question_mcq"})),
    CommandEntry("←→ / Enter", "help.answer_select", frozenset({"question_mcq"})),
    CommandEntry("←→ / Enter", "help.answer_two", frozenset({"question_assertion"})),
    CommandEntry("Enter", "help.answer_text", frozenset({"question_freetext"})),
    CommandEntry("@", "help.consult", frozenset({"question_mcq", "question_assertion"})),
    # The `i`/`?` panel's own tab strip (DELVE-0040/0041/0055/0056).
    CommandEntry("Tab / →←", "help.tab_cycle", frozenset({"info", "help"})),
    CommandEntry("[ ]", "help.subtab_cycle", frozenset({"info"})),
    CommandEntry("↑↓", "help.focus_row", frozenset({"info"})),
    # The drop/pickup amount field.
    CommandEntry("0-9", "help.amount_digit", frozenset({"drop_amount", "pickup_amount"})),
    CommandEntry("Backspace", "help.amount_backspace",
                frozenset({"drop_amount", "pickup_amount"})),
    CommandEntry("Enter", "help.amount_confirm", frozenset({"drop_amount", "pickup_amount"})),
    # The drop/pickup menu.
    CommandEntry("1-9", "help.menu_choose", frozenset({"drop_menu", "pickup_menu"})),
)


def entries_for(context: str) -> list[CommandEntry]:
    """The catalogue rows active in `context`, in table order (declaration order is display
    order: walking's movement/talk/etc. first, then the universal `?`/Esc, matching how the hint
    line already orders its own most-relevant-first list)."""
    return [e for e in CATALOGUE if context in e.contexts]
