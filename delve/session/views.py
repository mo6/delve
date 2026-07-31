"""The view models the UI paints, and nothing it doesn't. The output half of the frontend
contract (PLAN.md section 4).

No display types cross this line: Colour is one of sixteen names, not a curses attribute; a
test asserting on a Frame never imports curses. The core models no presentation state (no
scroll offset, no cursor). M1 has no overlay; TextView/MenuView/PromptView arrive at M2.
"""

from dataclasses import dataclass, field
from enum import Enum


class Colour(Enum):
    """The sixteen names, the floor on every target platform and NetHack's own palette. M1
    renders monochrome; the palette is wired at M8. Set now so view models are complete."""

    BLACK = "black"
    RED = "red"
    GREEN = "green"
    YELLOW = "yellow"
    BLUE = "blue"
    MAGENTA = "magenta"
    CYAN = "cyan"
    WHITE = "white"
    BRIGHT_BLACK = "bright_black"
    BRIGHT_RED = "bright_red"
    BRIGHT_GREEN = "bright_green"
    BRIGHT_YELLOW = "bright_yellow"
    BRIGHT_BLUE = "bright_blue"
    BRIGHT_MAGENTA = "bright_magenta"
    BRIGHT_CYAN = "bright_cyan"
    BRIGHT_WHITE = "bright_white"


@dataclass(frozen=True)
class Cell:
    glyph: str = " "
    colour: Colour = Colour.WHITE
    dim: bool = False


@dataclass
class MapView:
    cols: int
    rows: int
    cells: list[list[Cell]]


@dataclass
class StatusView:
    name: str
    dlvl: int
    rooms_done: int
    rooms_total: int
    gold: int
    hp: int
    max_hp: int
    turn: int
    # Localised labels, so `ui` paints the status line without importing the strings catalogue
    # (rule 2). `Dlvl`, `HP` and `T` stay as they are: NetHack's own labels, not translated.
    rooms_label: str = "Rooms"
    gold_symbol: str = "$"


@dataclass(frozen=True)
class TextBlock:
    kind: str   # 'para' | 'bullet' | 'quote' | 'plain' | 'code' | 'table' | 'bar' | 'kv'
    text: str
    # Inline (text, strong) runs for bold, and a table's cell grid (rows -> cells -> runs). Empty
    # `spans` means render `text` plain. compare=False so constructing a TextBlock by (kind, text)
    # still equals a styled one in tests that only care about the text.
    spans: tuple = field(default=(), compare=False)
    table: tuple = field(default=(), compare=False)
    # A 'bar' block's (label, frac, tail): `frac` is 0..1 or None ("not yet attempted", never a
    # misleading 0%). `ui` owns the bar's column width and how `frac` rounds to a filled glyph
    # count (DELVE-0043); `text` still carries a plain-text fallback for tests and any surface that
    # only reads text.
    bar: tuple = field(default=(), compare=False)
    # A 'kv' block's lines are each "Label: value" (DELVE-0078): `ui` colon-splits every line at
    # its first ": " and colours the label half, independent of `spans`. Used only where every line
    # genuinely is a label/value pair (Keys, Objectives, Grader, Status); a 'plain' block with an
    # incidental colon in its prose is never colon-split.


@dataclass(frozen=True)
class InfoTab:
    """One entry in the `i` panel's primary tab strip: a stable id (never localised, so tests and
    session logic can key off it) and the label `ui` paints (localised, through `Strings`)."""

    key: str      # 'pack' | 'progress' | 'grader', stable across locales
    label: str


@dataclass
class InfoView:
    """The `i` panel (DELVE-0035/DELVE-0040): a tab strip plus the active tab's body. Pack is the
    default and only tab with real content so far; Progress and Grader are reachable but render a
    placeholder body until their own child stories land. Reuses `TextBlock`/pagination the same way
    `TextView` does, so the pager treats both alike; unlike `TextView`'s title (page 1 only, since
    it is content), the tab strip is chrome like the hint line and is drawn on every page, so a
    learner paging through a long pack listing never loses sight of which tab is active."""

    tabs: list[InfoTab]
    active: int
    body: list[TextBlock]
    # A second-tier strip beneath the primary one (DELVE-0055, INFOSCREEN.md §5): empty/zero for
    # every tab but Scoring so far, so `ui` draws no sub-tab row and reserves no extra height for
    # Pack/Grader/Status (`windows._draw_info`/`_text_pages` branch on `subtabs` being non-empty).
    subtabs: list[InfoTab] = field(default_factory=list)
    active_sub: int = 0
    # Which row currently has keyboard focus (DELVE-0056): False (default) is the primary row,
    # True the sub-tab row; left/right cycle whichever one this points at. Meaningless (always
    # False) on a tab with no `subtabs`, the same "never matters without a second row" default
    # `active_sub` already follows.
    sub_focus: bool = False
    # The Pack tab's own compact list/detail split (DELVE-0069): non-empty `pack_rows` means the
    # Pack tab is showing its row list instead of `body` (one plain label per carried kind, "ui"
    # only lays them out and highlights `pack_selected`, rule 2); empty on every other tab, and on
    # Pack's own detail view (an empty pack, and a selected row's description, both render through
    # `body` instead, reusing the ordinary paginated text path). `pack_selected` is -1 whenever
    # `pack_rows` is empty, the same "-1 means no focus" convention `MenuView.selected` already
    # uses.
    pack_rows: list[str] = field(default_factory=list)
    pack_selected: int = -1
    title: str = "Info"   # the fixed panel name shown before the tab strip (DELVE-0041)
    more_label: str = "--More--"
    end_label: str = "(end)"
    page_fmt: str = "(page {page} of {total})"


@dataclass
class HelpView:
    """The `?` panel (DELVE-0028): a Keys tab (the context's command list, mirroring the `[hint]`
    line but complete and explained) and an Objectives tab (pack/chapter/room orientation, plus an
    optional cached LLM scene-setting passage). Mirrors `InfoView`'s tab-strip/pager shape field for
    field, so `ui/windows.py` draws both with the same code, but stays a distinct type on purpose:
    `i` (`InfoView`) is "what has happened in my run", `?` (`HelpView`) is "how do I play right
    now", and a `Frame`-level test can tell the two apart without inspecting tab labels. `subtabs`
    is always empty here (neither Keys nor Objectives has a second tier); the field only exists so
    the shared pager code (which reads `.subtabs`/`.active_sub`/`.sub_focus` off any view it draws)
    never has to special-case which of the two types it was handed."""

    tabs: list[InfoTab]
    active: int
    body: list[TextBlock]
    subtabs: list[InfoTab] = field(default_factory=list)
    active_sub: int = 0
    sub_focus: bool = False
    title: str = "Help"
    more_label: str = "--More--"
    end_label: str = "(end)"
    page_fmt: str = "(page {page} of {total})"


@dataclass
class TextView:
    """A lesson or an explanation: the whole text, as semantic blocks. The UI paginates it and
    holds the panel height; the core never wraps text or tracks a scroll offset (PLAN.md
    section 4). The pager chrome is localised data the session fills, so `ui` never spells a word
    (rule 2): `more_label`/`end_label` cap a page, and `page_fmt` is a '{page}/{total}' template the
    UI fills. Defaults are English, so a directly-built view still renders."""

    title: str
    body: list[TextBlock]
    more_label: str = "--More--"
    end_label: str = "(end)"
    page_fmt: str = "(page {page} of {total})"


@dataclass(frozen=True)
class MenuItem:
    key: str
    text: str
    struck: bool = False   # the pet ruled this one out; still selectable, shown crossed off


@dataclass
class MenuView:
    """A multiple-choice question, drawn as a numbered list. Items are already shuffled and carry no
    hint of which is correct; the explanation only arrives after an answer. A `struck` item is one
    the pet ruled out on consultation, never the correct answer revealed. `selected` is the option
    the keyboard focus sits on (moved with the arrows, confirmed with Enter, or bypassed by pressing
    its number), owned by the session so `ui` only paints it (rule 2); -1 means no focus (an item
    menu answered purely by number, like drop/pickup)."""

    prompt: str
    items: list[MenuItem]
    footer: str = ""
    selected: int = -1


@dataclass
class PromptView:
    """A two-way assertion, drawn as two buttons. The UI derives the keys from the labels;
    `selected` is the button the keyboard focus sits on (moved with the arrows, confirmed with
    Enter, or bypassed by pressing a label's key directly), owned by the session so `ui` only paints
    it (rule 2). `struck` parallels `choices`: a True there is a label the pet ruled out.
    `connector` is the localised word between the labels ('or'/'of'), kept for any caption."""

    text: str
    choices: list[str]
    footer: str = ""
    struck: tuple[bool, ...] = ()
    connector: str = "or"
    selected: int = 0


@dataclass
class AmountView:
    """A typed amount field: how many of a kind to drop (OBJECTS.md). `typed` is the digits entered
    so far (empty at first), which the UI shows in an input box with a cursor; the core parses and
    clamps it to `maximum`. Typed entry replaced an earlier +/- stepper, which was fiddly for large
    counts."""

    prompt: str
    typed: str
    maximum: int
    footer: str = ""


@dataclass
class FreeTextView:
    """A free-text question (Phase 2): the prompt, and the answer typed so far in a boxed input
    field, the same look as the amount field. `typed` is the buffer the session owns and rebuilds
    each keystroke, so the UI stays paint-only (rule 2); Enter submits it, Esc puts it down. The
    grader is never named here: the rubric is the grader's, not the learner's (PHASE2.md sec. 4)."""

    prompt: str
    typed: str = ""
    footer: str = ""


@dataclass
class GradingView:
    """The pending-grade pause (Phase 2, PHASE2.md section 5.3): a free-text answer is being graded
    on a worker (the local LLM), so the panel shows the answer and a 'Checking…' line while the UI
    polls. On the deterministic keyword floor grading is instant and this is never shown; it appears
    only when the grade is genuinely slow."""

    title: str
    answer: str
    body: str


Overlay = (TextView | MenuView | PromptView | AmountView | FreeTextView | GradingView | InfoView
          | HelpView)


@dataclass
class ToastView:
    """An ambient room-entry passage (DELVE-0060): unlike every `Overlay` above, a toast is not
    exclusive of the map or of walking, so it is its own `Frame` field, never part of `Overlay`.
    `ui` wraps `body` to its own small width at paint time (rule 2, the same as every other
    panel); `session` hands over the whole passage as one unwrapped block. `title` is the room's
    keeper name if it has one, or the chapter title otherwise (most rooms have no keeper of their
    own to name)."""

    title: str
    body: list[TextBlock]


@dataclass
class Frame:
    map: MapView
    status: StatusView
    messages: list[str] = field(default_factory=list)
    # An optional highlight colour for the top message line: green behind "Correct.", red behind
    # "Not quite.", so a right or wrong answer reads at a glance. None is the plain line. It is a
    # background; the UI resolves it in attrs.py (rule 2), as map cells carry a Colour.
    message_bg: Colour | None = None
    # The ambient room-entry toast (DELVE-0060), or None: independent of `overlay` (it must never
    # block walking, talking, or opening a panel), drawn only while no panel is open (`ui/render.py`
    # follows the same "a panel owns the screen" precedent the top message line already set).
    toast: ToastView | None = None
    # True while a room's background passage is queued, in flight, or resolved but not yet turned
    # into `toast` above: `ui/app.py` reads this to decide whether to keep waking on a short
    # timeout rather than blocking on the next keypress, so a toast appears the moment it resolves
    # rather than only once the learner happens to press something (the same non-blocking shape
    # `GradingView`'s poll already uses, but only while there is actually something to wait for).
    toast_pending: bool = False
    # The contextual hint line names the keys that work right now (PLAN.md section 7). It is
    # session state, not decoration, so the core supplies it rather than the UI guessing.
    hint: str = ""
    overlay: Overlay | None = None
