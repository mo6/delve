"""RunState: the headless application loop. `apply(Command) -> Frame`, never blocking, no
curses, no I/O (PLAN.md section 4). A test plays a whole run as a list of Commands and asserts
on Frames; that replayability is what makes the slice the go/no-go it is meant to be.

A run is a chain of chapters (M5). Each `ChapterRun` bundles one engine floor with its gates,
keepers and discovered tiles; RunState holds the list and a current index, delegating `chapter`,
`gates`, `keepers` and `discovered` to whichever chapter the learner stands on. Stairs (`>`/`<`)
carry between chapters; the final chapter's last keeper reveals a pedestal with the scroll.

`new_run` builds the hard-coded M2 slice (one chapter, only Ada gated), still the golden test;
`new_game` builds a full multi-chapter dungeon from a parsed pack. Both produce the same RunState.
An optional `recorder` (session-side, holds the store) is notified on the transitions worth
persisting: a room passed, a chapter changed, the scroll taken. It stays None in tests.
"""

import textwrap
import time
import zlib
from dataclasses import dataclass, field
from datetime import datetime

import delve

# DELVE-0066: the ambient toast gets its own GraderMetrics instance, separate from whatever the
# configured LLMGrader accumulates, so the Grader tab can report each model's workload on its own
# rather than one blended total. `session/grading.py` already imports this same module directly
# (rule 1's diagram predates that; the boundary that matters is engine/ui, not session/assess).
from delve.assess.grader import GraderMetrics

# The M2 slice: the pilot's first room is gated; the rest of the Sorting Office is walkable but
# has no keeper. It is kept exactly as it was, the independent reference the parser is checked
# against, while the full pack loads through new_game below.
from delve.content.markup import inline_spans, tokenize
from delve.content.pack import Pack
from delve.content.pilot import PHISHING_ROOM
from delve.engine import actions, layout, vision
from delve.engine import pet as petmod
from delve.engine.entities import Pet, Player
from delve.engine.items import (
    ANY_CHARGE,
    MONEY,
    TORCH,
    TORCH_DURATION_STEPS,
    ItemDef,
    Stack,
    can_place,
    merged,
    register,
    taken,
)
from delve.engine.rng import Rng
from delve.engine.world import Chapter, Direction, Point, TileKind
from delve.gate import Gate, GateState, install_chapter_gates, install_gates
from delve.progress.scrolls import format_money, render_scroll
from delve.session import backstory, flavour
from delve.session import help as help_catalogue
from delve.session.commands import (
    Answer,
    AnswerText,
    Ascend,
    Backspace,
    BuyRemoval,
    Confirm,
    Consult,
    Descend,
    Digit,
    Dismiss,
    Drop,
    FocusRow,
    GradeReady,
    Help,
    Inventory,
    Move,
    Pickup,
    Rest,
    Select,
    SubTabCycle,
    TabCycle,
    Talk,
    Type,
    Wait,
)
from delve.session.grading import InlineGrader
from delve.session.views import (
    AmountView,
    Cell,
    Colour,
    Frame,
    FreeTextView,
    GradingView,
    HelpView,
    InfoTab,
    InfoView,
    MapView,
    MenuItem,
    MenuView,
    PromptView,
    StatusView,
    TextBlock,
    TextView,
    ToastView,
)
from delve.strings import Strings
from delve.strings import load as load_strings

_SLICE_IDS = [PHISHING_ROOM.id, "sorting-2", "sorting-3"]
_SLICE_GATED = [PHISHING_ROOM]

# How many turns a top-line message stays up before it blanks. Two: it shows on the turn it is
# posted and one more, then clears, so an old message is never read as fresh (a play-testing note).
_MSG_TTL = 2

# How many turns the ambient room-entry toast (DELVE-0060) stays up before it fades on its own; a
# longer budget than `_MSG_TTL` since it holds several sentences to read, not one status line.
_TOAST_TTL = 8

# A firm character cap on a generated toast passage (DELVE-0070): `backstory.PROMPT` only *asks*
# for "a very short (2-3 sentence)" reply, and the model doesn't reliably comply, so this is the
# backstop that keeps an overlong reply from ever reaching `draw_toast`'s own line-count
# truncation, which would otherwise cut it off mid-sentence with no indication anything was cut.
# Roughly 3-4 generous sentences: past `_TOAST_TTL`'s point, this is a rendering backstop, not a
# style choice, so it errs a little loose rather than clipping a reply that is merely a bit long.
_TOAST_TEXT_CAP = 480

# How many real seconds a first-time learner may stand still in the starting room, after its toast
# has appeared, before a one-shot nudge regenerates it suggesting the arrow keys (DELVE-0061).
# Wall-clock, not turns: turns never advance while the learner does nothing, so this is the one
# place `RunState` reads a real clock rather than the turn counter. Raised from an initial 10s
# (a play-testing note: it fired too soon, before someone genuinely reading the first toast had
# even finished it).
_NUDGE_DELAY_SECONDS = 20.0

# Case-insensitive substrings that count as "the arrow keys were named", per locale, for the
# nudge's deterministic fallback (`RunState._ensure_arrow_keys_mentioned`). English also accepts
# "cursor keys", a common synonym; Dutch covers both the compound and the bare "pijltjes".
_ARROW_KEYWORDS = {
    "en": ("arrow key", "arrow keys", "cursor key", "cursor keys"),
    "nl": ("pijltjestoets", "pijltjestoetsen", "pijltjes"),
}

# The ambient toast's own model, deliberately not whatever the grader is configured with: a
# side-by-side comparison of both models pulled locally found this one's English noticeably
# richer and its Dutch dramatically more fluent, worth the extra latency since generation never
# blocks play (`RunState._backstory_client`).
_BACKSTORY_MODEL = "qwen3.5:9b"

# Overlays that are a keeper encounter: while one is open the message line carries the encounter's
# own text ('X examines you', 'Correct.') and its clock is frozen. Every *other* overlay, the pack
# and inventory panels and the message log, lets the map message age out as normal, so opening the
# backpack after a line has expired never resurrects it (a play-testing note).
_ENCOUNTER_OVERLAYS = frozenset({"lesson", "question", "explanation", "grading"})

# How many recent lines the message log (the `p` key) shows at most, newest first.
_HISTORY_MAX = 10

# The `i` panel's primary tabs, in strip order (DELVE-0040): stable keys the session and tests key
# off, paired with the strings key for the localised label `ui` paints. Pack is index 0 (the
# default tab, so the key's meaning never rotates); Scoring (DELVE-0042/0043, renamed from
# "Progress" since it shows score, not completion), Grader (DELVE-0054) and Status (DELVE-0044)
# all have real content now. Messages (a playtesting request) folds the former standalone message
# log panel (once its own `p` key) in here; that key is retired, reachable only via this tab now.
# Trophies (DELVE-0085) shows finished packs from before this run started. Status moved to the
# last position (an addendum to DELVE-0097): it's app/run diagnostics, the least gameplay-relevant
# tab, so it belongs at the far end of the strip rather than ahead of Messages/Trophies.
_INFO_TABS = (("pack", "item.tab_pack"), ("scoring", "item.tab_scoring"),
              ("grader", "item.tab_grader"), ("messages", "item.tab_messages"),
              ("trophies", "item.tab_trophies"), ("status", "item.tab_status"))

# A sentinel `def_id` for a Pack-tab drop only, never a real `ItemDef.id`: the currently-burning
# torch is never a `Stack` (DELVE-0062, a steps-remaining counter, not a spare count), so it can't
# share `TORCH.id` with an ordinary carried torch in `_pack_droppable` without the two colliding on
# drop. Dropping it is its own path (`_do_drop_lit_torch`), not `_do_drop`'s generic one.
_LIT_TORCH_ID = "torch:lit"

# The Scoring tab's own sub-tab strip (DELVE-0055, INFOSCREEN.md §5): 'Now' (the DELVE-0042/0043
# bars, unchanged) and 'Rooms' (the pass map). No other primary tab has sub-tabs yet, so this is
# looked up only when the active primary tab's key is 'scoring'.
_SCORING_SUBTABS = (("now", "item.tab_now"), ("rooms", "item.tab_rooms"))

# The `?` help panel's own two tabs (DELVE-0028): Keys (the context's command catalogue) and
# Objectives (pack/chapter/room orientation, plus an optional cached LLM passage).
_HELP_TABS = (("keys", "help.tab_keys"), ("objectives", "help.tab_objectives"))

# The four room pass-map glyph states (DELVE-0055): sealed (never sat), sat (sat, not passed), ok
# (passed after at least one failed sitting), clear (passed on the first sitting). Never coloured
# here (this story's non-goals); `ui` paints them in the plain attribute.
_GLYPH_SEALED, _GLYPH_SAT, _GLYPH_OK, _GLYPH_CLEAR = "·", "░", "▒", "█"

# Leading articles (en + nl) that are not a name. `_keeper_ref` uses them to tell a first name from
# a role-title: "Ada the Suspicious" -> "Ada", but "De Marskramer" / "The Peddler" stay whole rather
# than collapsing to the bare article the split-on-first-word used to give.
_ARTICLES = frozenset({"the", "a", "an", "de", "het", "een"})


def _room_glyph(gate: Gate) -> str:
    """One room's pass-map glyph (DELVE-0055): sealed (never sat), sat (sat, not yet passed), ok
    (passed, but needed a failed sitting first), clear (passed on the first sitting).
    `attempts_used` is not reset on a pass (only on a REPELLED reset), so at read time after a pass
    it already holds exactly the failed-sitting count immediately before the pass (0 for a clean
    first try)."""
    if not gate.passed:
        return _GLYPH_SAT if gate.sittings > 0 else _GLYPH_SEALED
    return _GLYPH_OK if gate.attempts_used > 0 else _GLYPH_CLEAR


def _keeper_ref(name: str) -> str:
    """A short way to name a keeper in a message or hint. The first word for a "<Name> the
    <Epithet>" keeper (Ada), but the whole title when it opens with an article (De Marskramer, The
    Peddler), so a role-name is never truncated to just its article."""
    words = name.split()
    if not words:
        return name
    if words[0].lower() in _ARTICLES:
        return name.strip()
    return words[0].rstrip(",.;:!?'\"")   # drop a trailing comma etc. ("Grigor," -> "Grigor")

# The least number of grade-poll ticks the 'Checking...' overlay (and its "you hand your answer
# over" line) is held before a *ready* verdict is folded in, so a fast grade does not flash past
# unread (a play-testing note). The UI polls at app._GRADE_POLL_MS (120ms), so sixteen ticks is
# roughly two seconds. It only bites when the grade finishes sooner than that; a slower grade lands
# on the tick it is ready, and the instant keyword floor never shows the overlay at all.
_GRADE_MIN_TICKS = 16

# Carry flavour (an item's `on_move`) is ambient: it speaks on only about half your steps, never
# over a more important line, and after a few full utterances it drops to its short form if the
# item defines one (a coconut says the whole "You bang..." line a few times, then just "Clip-clop").
_FLAVOUR_CHANCE = 50      # percent of eligible steps on which a carried kind speaks
_FLAVOUR_FULL_TIMES = 3   # full-line utterances before it abbreviates (needs an on_move_short)

# The English catalogue, loaded once and shared by runs that are handed no locale (the M2 slice
# and most tests). A real play passes the `--lang` catalogue in through new_game.
_DEFAULT_STRINGS: Strings | None = None


def _default_strings() -> Strings:
    global _DEFAULT_STRINGS
    if _DEFAULT_STRINGS is None:
        _DEFAULT_STRINGS = load_strings("en")
    return _DEFAULT_STRINGS


@dataclass
class ChapterRun:
    """One floor in play: the engine grid, its gates and keepers, and which of its tiles the
    learner has seen. `final` marks the last chapter of the pack, whose last keeper reveals the
    pedestal rather than stairs down."""

    chapter: Chapter
    gates: dict[str, Gate]
    content_chapter_id: str = ""
    title: str = ""
    intro: str = ""
    final: bool = False
    # A tutorial floor (Dlvl 0) is unscored: passing its keepers writes no room_result and its
    # rooms never count toward the scroll (PLAN.md section 9). Pack floors are scored.
    scored: bool = True
    discovered: set[Point] = field(default_factory=set)
    # Objects lying on the floor: a tile maps to its pile of stacks (OBJECTS.md). Mutable run
    # state, like `discovered`, so it lives on the ChapterRun and is carried by the snapshot.
    items: dict[Point, list[Stack]] = field(default_factory=dict)
    # Room ids the learner has already stood inside this run (DELVE-0060): a room leaving this set
    # is what queues its one ambient toast; re-entering one already here queues nothing. Carried by
    # the snapshot like `discovered`, so a resume never re-triggers a toast for ground already
    # covered.
    visited_rooms: set[str] = field(default_factory=set)
    keepers: dict[Point, Gate] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        self.keepers = {g.keeper.pos: g for g in self.gates.values()}


def new_run(seed: int, cols: int, rows: int, name: str = "Adventurer",
            difficulty: str = "standard", strings: Strings | None = None,
            pet_species: str = "cat", pet_name: str | None = None,
            grader_runner=None) -> RunState:
    """Lock the M2 chapter to (seed, cols, rows), seal Ada's exit, place the learner and the pet.
    `difficulty` sets the stakes a failed sitting carries (M4); the slice runs at standard.
    `pet_species` is 'cat', 'dog', or 'none' for a soloist (PETS.md). `grader_runner` grades free
    text; the default is the inline keyword floor (Phase 2)."""
    strings = strings or _default_strings()
    chapter = layout.generate(seed, cols, rows, len(_SLICE_IDS), room_ids=_SLICE_IDS)
    gates = install_gates(chapter, _SLICE_GATED, difficulty)
    cr = ChapterRun(chapter=chapter, gates=gates, content_chapter_id="sorting-office",
                    title="The Sorting Office")
    player = Player(pos=chapter.start, name=name, torch_charge=TORCH_DURATION_STEPS)
    welcome = strings("msg.no_exit", keeper=_SLICE_GATED[0].keeper_name)
    return RunState([cr], player, Rng(seed), welcome=welcome, strings=strings,
                    pet_rng=Rng(seed * 100 + 777), flavour_rng=Rng(seed * 100 + 333),
                    seed=seed,
                    pet_species=pet_species, pet_name=pet_name, grader_runner=grader_runner)


def new_game(pack: Pack, seed: int, cols: int, rows: int, name: str = "Adventurer",
             difficulty: str | None = None, recorder=None, *, strings: Strings | None = None,
             tutorial: Pack | None = None, skip_tutorial: bool = False,
             pet_species: str = "cat", pet_name: str | None = None,
             grader_runner=None, observe: bool = True,
             trophy_rows: list[tuple[str, str, str]] | None = None) -> RunState:
    """Build a full multi-chapter dungeon from a parsed pack. Every pack room is gated; each
    chapter is generated from a seed derived from `seed` so the whole run is reproducible, and
    only the last chapter's final keeper reveals the pedestal. `recorder`, if given, persists it.

    `tutorial`, when given, is prepended as the engine's Dlvl 0 orientation floor (PLAN.md
    section 9): unscored, with its stairs down standing open from the start. It is always built
    into the chapter list so a resumed run's chapter count is stable; `skip_tutorial` only starts
    the learner below it, on the pack's first floor. The pack's first floor gains stairs up
    whenever a tutorial sits above it, so a learner can always climb back for a reminder.
    `observe=False` defers the constructor's `_observe` (DELVE-0094); `launch.resume` uses it so
    the ambient toast is queued for the restored position, not the transient pre-restore spawn.
    """
    strings = strings or _default_strings()
    difficulty = difficulty or pack.difficulty
    for defn in pack.items:                       # make the pack's kinds resolvable by id, so a
        register(defn)                            # placed or carried stack round-trips (OBJECTS.md)
    item_defs = {d.id: d for d in pack.items}
    tut_item_defs = {d.id: d for d in tutorial.items} if tutorial else {}
    for defn in tut_item_defs.values():           # the tutorial ships its own kinds too (the stone
        register(defn)                            # the objects room hands you to practise with)
    chapters: list[ChapterRun] = []

    tut_chapters = tutorial.chapters if tutorial else ()
    n_tut = len(tut_chapters)
    for j, cc in enumerate(tut_chapters):
        ids = [r.id for r in cc.rooms]
        eng = layout.generate(seed * 100 + 900 + j, cols, rows, len(cc.rooms), dlvl=0,
                              room_ids=ids, paint_stairs_down=True, stairs_up=(j > 0))
        gates = install_chapter_gates(eng, cc.rooms, tutorial.difficulty, final=False)
        cr = ChapterRun(chapter=eng, gates=gates, content_chapter_id=cc.id,
                        title=cc.title, intro=cc.intro, scored=False)
        _scatter_tutorial_coins(cr, Rng(seed * 100 + 950 + j))
        _scatter_placements(cr, cc.rooms, tut_item_defs, Rng(seed * 100 + 960 + j))
        chapters.append(cr)

    last = len(pack.chapters) - 1
    for i, cc in enumerate(pack.chapters):
        ids = [r.id for r in cc.rooms]
        eng = layout.generate(seed * 100 + i, cols, rows, len(cc.rooms), dlvl=i + 1,
                              room_ids=ids, paint_stairs_down=False, stairs_up=(i > 0 or n_tut > 0))
        final = i == last
        gates = install_chapter_gates(eng, cc.rooms, difficulty, final=final)
        cr = ChapterRun(chapter=eng, gates=gates, content_chapter_id=cc.id,
                        title=cc.title, intro=cc.intro, final=final)
        _scatter_placements(cr, cc.rooms, item_defs, Rng(seed * 100 + 600 + i))
        _scatter_torch(cr, Rng(seed * 100 + 700 + i))
        chapters.append(cr)

    start_idx = n_tut if (skip_tutorial and n_tut) else 0
    player = Player(pos=chapters[start_idx].chapter.start, name=name,
                    torch_charge=TORCH_DURATION_STEPS)
    welcome = _first_line(chapters[start_idx].intro) or pack.title
    return RunState(chapters, player, Rng(seed), pack=pack, welcome=welcome, recorder=recorder,
                    idx=start_idx, strings=strings, pet_rng=Rng(seed * 100 + 777),
                    flavour_rng=Rng(seed * 100 + 333), seed=seed,
                    pet_species=pet_species, pet_name=pet_name, grader_runner=grader_runner,
                    observe=observe, trophy_rows=trophy_rows)


def _scatter_tutorial_coins(cr: ChapterRun, rng: Rng) -> None:
    """A handful of coins strewn on the tutorial floor, so following the Porter's directions pays a
    little and the learner meets auto-pickup for free, before money matters (a play-testing note).
    Random interior floor tiles from a dedicated `rng` (so it never perturbs the exam shuffles), and
    captured in the first snapshot like any other floor state, so a resumed run keeps what is left.

    At least one coin always lands in the *starting* room, which is the only one reachable before a
    keeper is passed; otherwise, on a multi-room tutorial, a seed can strew them all behind sealed
    doors and the learner meets no coin at all until they have already passed someone."""
    def free_in(room):
        return [p for p in room.interior()
                if cr.chapter.grid.at(p.x, p.y).kind is TileKind.FLOOR
                and p not in cr.keepers and p != cr.chapter.start]
    spots = [p for room in cr.chapter.rooms for p in free_in(room)]
    if not spots:
        return
    rng.shuffle(spots)
    chosen = spots[:min(rng.randint(4, 6), len(spots))]
    start_room = next((r for r in cr.chapter.rooms if r.contains(cr.chapter.start)), None)
    if start_room and not any(start_room.contains(p) for p in chosen):
        here = [p for p in free_in(start_room) if p not in chosen]
        if here:
            chosen[0] = rng.choice(here)
    for p in chosen:
        cr.items[p] = [Stack(MONEY, rng.randint(3, 12))]


def _scatter_placements(cr: ChapterRun, rooms, defs: dict[str, ItemDef], rng: Rng) -> None:
    """Scatter a chapter's `place:` objects on free interior floor tiles, one stack per placement,
    deterministically from a dedicated `rng` (OBJECTS.md section 9). Each content room's placements
    land in the matching grid room (rooms are laid out in content order), so the dungeon stays
    regenerable and the snapshot records only what the learner then moved. An id with no defined
    kind, or a room too tight to hold another stack, is skipped rather than raising."""
    grid = cr.chapter.grid
    for content_room, grid_room in zip(rooms, cr.chapter.rooms, strict=True):
        if not content_room.placements:
            continue
        spots = [p for p in grid_room.interior()
                 if grid.at(p.x, p.y).kind is TileKind.FLOOR
                 and p not in cr.keepers and p != cr.chapter.start and p not in cr.items]
        rng.shuffle(spots)
        for def_id, count in content_room.placements:
            defn = defs.get(def_id)
            if defn is None or not spots:
                continue
            cr.items[spots.pop()] = [Stack(defn, count)]


def _scatter_torch(cr: ChapterRun, rng: Rng) -> None:
    """One spare torch per pack chapter (DELVE-0062), a random free interior tile in a random room,
    the same shape as `_scatter_tutorial_coins`/`_scatter_placements`. Never called for the tutorial
    (it stays exactly as lit as it is today, no torch mechanic), and on its own dedicated `rng`
    stream so it never perturbs the exam, pet, carry-flavour, or placement scatters."""
    def free_in(room):
        return [p for p in room.interior()
                if cr.chapter.grid.at(p.x, p.y).kind is TileKind.FLOOR
                and p not in cr.keepers and p != cr.chapter.start and p not in cr.items]
    rooms = [r for r in cr.chapter.rooms if free_in(r)]
    if not rooms:
        return
    room = rng.choice(rooms)
    spot = rng.choice(free_in(room))
    cr.items[spot] = [Stack(TORCH, 1)]


def _first_line(text: str) -> str:
    for line in text.split("\n"):
        if line.strip():
            return line.strip()
    return ""


def _reflow(text: str) -> str:
    """Join a block's soft-wrapped source lines into paragraphs, so the panel re-wraps them to its
    own width instead of inheriting the author's line breaks (DELVE-0029). Lines within a paragraph
    are joined by a space; a blank line stays a paragraph break (`\\n\\n`). This mirrors the lesson
    parser's paragraph rule (`content/markup.py`), applied to an item's `look` at render time."""
    paras: list[str] = []
    cur: list[str] = []
    for line in text.split("\n"):
        if line.strip():
            cur.append(line.strip())
        elif cur:
            paras.append(" ".join(cur))
            cur = []
    if cur:
        paras.append(" ".join(cur))
    return "\n\n".join(paras)


def _sentence_ends(text: str):
    """Yield the index just past each sentence-ending `. `/`! `/`? ` (or one at the very end of
    `text`): a small hand-rolled scan rather than pulling in `re` for this one job."""
    for i, ch in enumerate(text):
        if ch in ".!?" and (i + 1 == len(text) or text[i + 1].isspace()):
            yield i + 1


def _cap_toast_text(text: str, limit: int = _TOAST_TEXT_CAP) -> str:
    """Trim an ambient toast passage to `limit` characters at a clean boundary, never mid-word
    (DELVE-0070). Prefers the last complete sentence that still fits the cap; falls back to the
    last whole word (`textwrap.shorten`, `break_on_hyphens=False` as elsewhere in this file) only
    if even the first sentence alone overruns it, e.g. a long run-on with no punctuation."""
    if len(text) <= limit:
        return text
    kept = ""
    for end in _sentence_ends(text):
        candidate = text[:end]
        if len(candidate) > limit:
            break
        kept = candidate
    if kept:
        return kept.rstrip()
    return textwrap.shorten(text, width=limit, placeholder="…", break_on_hyphens=False)


def _colour_for(kind: TileKind) -> Colour:
    if kind is TileKind.DOOR:
        return Colour.YELLOW
    if kind in (TileKind.STAIRS_DOWN, TileKind.STAIRS_UP):
        return Colour.CYAN
    if kind is TileKind.PEDESTAL:
        return Colour.BRIGHT_YELLOW
    return Colour.WHITE


class RunState:
    def __init__(self, chapters: list[ChapterRun], player: Player, rng: Rng, *,
                 pack: Pack | None = None, welcome: str = "", recorder=None, idx: int = 0,
                 strings: Strings | None = None, pet_rng: Rng | None = None,
                 flavour_rng: Rng | None = None, seed: int = 0,
                 pet_species: str = "cat", pet_name: str | None = None,
                 grader_runner=None, observe: bool = True,
                 trophy_rows: list[tuple[str, str, str]] | None = None):
        self.chapters = chapters
        self.idx = idx
        self.player = player
        self.rng = rng
        # The run seed, kept so the reward drop can spin a dedicated stream from it at pass time
        # (DELVE-0015). Not the exam stream `self.rng`: borrowing that reshuffles the exam.
        self.seed = seed
        self.pet_rng = pet_rng or Rng(0)
        # A dedicated stream for ambient carry flavour, so its coin-flip never touches the exam or
        # pet streams; not snapshotted (purely cosmetic, a resume just re-shows the full form a
        # couple of times). `_carry_said` counts how often each kind has spoken, to abbreviate it.
        self.flavour_rng = flavour_rng or Rng(0)
        self._carry_said: dict[str, int] = {}
        self.pack = pack
        self.recorder = recorder
        self.strings = strings or _default_strings()
        # The learner's trophy case as `(score, title, date)` rows (DELVE-0085), computed once at
        # start/resume via `launch.trophy_rows` (newest `awarded_at` first) and never refreshed
        # mid-run; empty means no completions yet (the Trophies tab shows `item.trophies_empty`).
        # Not snapshotted: resume re-reads the store the same way start does.
        self._trophy_rows: list[tuple[str, str, str]] = list(trophy_rows or ())
        self.turn = 0
        self.messages: list[str] = [welcome] if welcome else []
        self._greeted: set[str] = set()
        self.active: Gate | None = None
        self._overlay = None          # a TextView | MenuView | PromptView | AmountView, or None
        # kinds: lesson|question|explanation|repelled|scroll|info|drop_amount
        self._overlay_kind: str | None = None
        # The `i` panel's active primary tab, remembered only while the panel stays open
        # (`_tab_cycle` mutates this); `_inventory` resets it to Pack (index 0) on every fresh
        # open (a playtesting reversal of DELVE-0040's original "sticky across opens" choice,
        # which read as broken navigation rather than a remembered preference).
        self._info_tab: int = 0
        # The active sub-tab within whichever primary tab has any (DELVE-0055): reset to 0 ("Now")
        # every time the primary tab changes, per that story's own acceptance criteria, so it is
        # never persisted across a primary-tab round trip the way `_info_tab` itself is.
        self._info_subtab: int = 0
        # Which tab row currently has keyboard focus (DELVE-0056): False (default) is the primary
        # row. Resets to False alongside `_info_subtab` resetting to 0, same rule, same reason.
        self._info_sub_focus: bool = False
        # The Pack tab's focused row in its compact carried-kinds list (DELVE-0069, DELVE-0075):
        # the list and the focused row's own description show side by side at all times, so this
        # is the one piece of state the tab needs. Resets the same way `_info_subtab`/
        # `_info_sub_focus` do: on every fresh panel open and on any primary-tab change, never
        # carried across a round trip.
        self._pack_row: int = 0
        # The `?` help panel (DELVE-0028): its active tab, reset to Keys on every fresh open by
        # `_help`, the same reversal `_info_tab` gets from `_inventory`.
        # `_prior_overlay(_kind)` remembers what was showing before help opened (a lesson, a menu,
        # nothing while walking), since help can stack over any context and must hand it back
        # unchanged on dismiss, rather than behaving like every other panel's Esc (which acts on
        # `self.active`/clears drop state).
        self._help_tab: int = 0
        self._prior_overlay = None
        self._prior_overlay_kind: str | None = None
        # The pickup menu's transient state, and the amount field shared by pickup and a Pack-tab
        # drop (DELVE-0081): the kind pending in the amount field, and the digits typed into it so
        # far, all cleared when either closes. (def-id, label, available, charge) - charge is None
        # except for a torch of known charge (DELVE-0067), threaded through so a menu/row choice
        # picks the exact floor/pack stack it named.
        self._pickables: list[tuple[str, str, int, int | None]] = []    # to pick up
        self._pending: tuple[str, str, int, int | None] | None = None    # kind, label, max, charge
        self._amount_buf: str = ""                           # digits typed into the amount field
        # The free-text answer buffer (Phase 2): the session owns it and rebuilds the FreeTextView
        # each keystroke, so the UI stays paint-only. The grader-runner grades a submitted answer,
        # inline (the keyword floor, the default) or on a worker (the LLM); `_pending_answer` holds
        # the answer while a slow grade runs, so `_resolve_text` can title the explanation with it.
        self._answer_buf: str = ""
        self._grader_runner = grader_runner or InlineGrader()
        # The ambient room-entry toast (DELVE-0060): one short LLM passage per room, queued the
        # first time the learner stands inside it (`_maybe_enter_room`, called from `_observe`) and
        # shown once it resolves (`_poll_toast`, called from `frame()`). `None` forever on a run
        # with no grader model configured, or if a room's call fails; entering it then simply grows
        # no toast (no error, no gating, DELVE-0033's opposite: this is flavour, not required to
        # play). Reuses whichever `OllamaClient` the free-text grader is already configured with,
        # so this needs no config of its own. `_ambient_metrics` (DELVE-0066) is its own
        # `GraderMetrics`, separate from the configured `LLMGrader`'s own, so the Grader tab can
        # report the ambient model's tokens/latency/call count apart from grading's.
        self._ambient_metrics = GraderMetrics()
        self._room_backstory = backstory.RoomBackstoryRunner(
            self._backstory_client(), model=_BACKSTORY_MODEL, metrics=self._ambient_metrics)
        self._toast: ToastView | None = None
        self._toast_turn: int = 0             # the turn `_toast` was shown, for ageing it out
        # DELVE-0070: the TTL only starts counting down once the learner has taken a turn since the
        # toast appeared, so one left frozen mid-read never ages out from under them. `None` while
        # `self.turn` still equals `_toast_turn` (not moved since); set to the turn of the first
        # move after that, the point `_TOAST_TTL` is measured from.
        self._toast_ttl_start: int | None = None
        # The one-shot idle nudge (DELVE-0061): 'unarmed' until the starting room's own toast is
        # shown with the learner still on turn 0, then 'waiting' for `_NUDGE_DELAY_SECONDS` real
        # seconds, then 'queued' (a second call submitted) until it resolves into 'fired', or
        # 'cancelled' the moment the learner moves before it does. Every state but 'waiting'/
        # 'queued' is inert, so this never fires twice and never outlives the learner's first move.
        self._nudge_state: str = "unarmed"
        self._nudge_deadline: float | None = None   # a time.monotonic() timestamp, once armed
        self._nudge_room_id: str | None = None       # the queued nudge's own key, once submitted
        self._pending_answer: str | None = None
        self._grade_ticks = 0                                # poll ticks since a slow grade started
        self._selected_option = 0                     # the focused assertion/MCQ option (arrows)
        # Message ageing: the top line blanks a couple of turns after the news it carries, so an
        # old message is never mistaken for a fresh one (a play-testing note). We remember how many
        # messages had been posted when the line last changed, and on which turn.
        self._msg_len_seen = 0
        self._msg_turn = 0
        # Highlight colour per message index (green/red behind Correct./Not quite.); most messages
        # are plain and absent here. The visible line's colour rides the Frame to the UI (rule 2).
        self._msg_styles: dict[int, Colour] = {}
        self.finished = False
        self._scroll_claimed = False
        # The companion: a cat or a dog placed beside the learner, or None for a soloist (PETS.md).
        self.pet = self._make_pet(pet_species, pet_name)
        if self.pet is not None:
            self.pet.pos = self._pet_spot()
        # `observe=False` is resume's path (DELVE-0094): `launch.resume` builds via `new_game`,
        # then lays the snapshot over with `apply_dict`, then calls `_observe` itself for the
        # restored position. Running it here would queue an ambient toast for the pre-restore
        # spawn room that `apply_dict` is about to discard, leaving a doomed loading spinner.
        if observe:
            self._observe()

    def _make_pet(self, species: str, name: str | None) -> Pet | None:
        if species == "none":
            return None
        if species not in ("cat", "dog"):
            species = "cat"
        return Pet(pos=self.player.pos, species=species,
                   name=name or self.strings("pet.default_" + species))

    # -- delegation to the current chapter ----------------------------------------------

    @property
    def cur(self) -> ChapterRun:
        return self.chapters[self.idx]

    @property
    def chapter(self) -> Chapter:
        return self.cur.chapter

    @property
    def gates(self) -> dict[str, Gate]:
        return self.cur.gates

    @property
    def keepers(self) -> dict[Point, Gate]:
        return self.cur.keepers

    @property
    def discovered(self) -> set[Point]:
        return self.cur.discovered

    @property
    def has_light(self) -> bool:
        """Whether the learner currently has working light (DELVE-0062); gates both how much of the
        current frame is lit and whether any of it is remembered afterwards. The tutorial floor is
        exempt from the whole mechanic (its own non-goal): any unscored chapter reads as always lit,
        the same as before this issue, regardless of the torch's charge."""
        return not self.cur.scored or self.player.torch_charge > 0

    @property
    def items(self) -> dict[Point, list[Stack]]:
        return self.cur.items

    # -- command handling ---------------------------------------------------------------

    def apply(self, command) -> Frame:
        if self._overlay_kind == "repelled":
            # The push-back panel is an informational pause: the next action dismisses it. Move,
            # Talk and Rest then act on the map below; Confirm/Dismiss just put the panel down.
            self._overlay = None
            self._overlay_kind = None
            if isinstance(command, (Confirm, Dismiss)):
                return self.frame()
        if self._overlay_kind == "scroll":
            # The scroll is the last thing shown; the run is already won. Any acknowledgement puts
            # it down, and nothing else on the map responds until it does. Help is the one
            # exception: `?` still opens/closes over the scroll like every other panel (a learner
            # can still check what a key does before putting the scroll down), never confused with
            # Confirm/Dismiss putting the scroll itself away.
            if isinstance(command, Help):
                self._help()
                return self.frame()
            if isinstance(command, (Confirm, Dismiss)):
                self._close("")
            return self.frame()
        match command:
            case Move(direction=d):
                self._move(d)
            case Talk():
                self._talk()
            case Answer(choice=c):
                self._answer(c)
            case AnswerText(text=t):
                self._submit_text(t)
            case Type(char=ch):
                self._type_char(ch)
            case GradeReady():
                self._poll_grade()
            case Confirm():
                self._confirm()
            case Consult():
                self._consult()
            case BuyRemoval():
                self._buy_removal()
            case Rest():
                self._rest()
            case Wait():
                self._wait()
            case Descend():
                self._descend()
            case Ascend():
                self._ascend()
            case Pickup():
                self._pickup()
            case Drop():
                self._drop()
            case Inventory():
                self._inventory()
            case TabCycle(delta=d):
                self._tab_cycle(d)
            case SubTabCycle(delta=d):
                self._sub_tab_cycle(d)
            case FocusRow(delta=d):
                self._focus_row(d)
            case Select(delta=d):
                self._select(d)
            case Digit(value=v):
                self._type_digit(v)
            case Backspace():
                self._backspace()
            case Help():
                self._help()
            case Dismiss():
                self._dismiss()
            case _:  # Quit and anything else: no state change
                pass
        return self.frame()

    def _move(self, direction) -> None:
        if self.active or self._overlay is not None:   # reading, examining, or a panel is open
            return
        dest = actions.step(self.chapter, self.player.pos, direction)
        if dest is not None and dest in self.keepers:
            # Walking into a keeper is NetHack's bump-to-act: it costs a turn like an attack (the
            # keeper blocks the tile, so the player stays put and the pet has nowhere to trail to).
            # Bumping an unpassed keeper opens the lesson; bumping one you've already passed is just
            # a brush-off, not a re-lesson (re-reading stays a deliberate `t`, rule 3). Pressing `t`
            # is free by contrast; only the bump spends a turn.
            gate = self.keepers[dest]
            self.turn += 1
            self._pet_step()
            if gate.passed:
                self.messages.append(
                    self.strings("msg.bump_passed", first=_keeper_ref(gate.keeper.name)))
            else:
                self._talk(gate)
            return
        if dest is not None and self.pet is not None and dest == self.pet.pos:
            # Walking into your pet is retrieval: take any coins it carries (how you catch a fleeing
            # cat), costs a turn like a keeper bump, and does not swap places (PETS.md section 5).
            self.turn += 1
            self._retrieve()
            self._pet_step()
            return
        if dest is None:
            self.messages.append(self.strings("msg.cant_go"))
            return
        self.player.pos = dest
        self.turn += 1
        self._tick_torch()
        self._observe()
        spoke = len(self.messages)
        self._collect_money(dest)
        self._see_here(dest)
        # Carry flavour is lowest priority: it speaks only when nothing more important did this step
        # (a collect, a sighting), and a later pet or greet line still overrides it by recency.
        if len(self.messages) == spoke:
            self._carry_flavour()
        self._pet_step()
        if self.chapter.grid.at(dest.x, dest.y).kind is TileKind.PEDESTAL:
            self._claim_scroll()
            return
        self._maybe_greet()

    def _talk(self, gate: Gate | None = None) -> None:
        if self.active:
            return
        # `t` finds whichever keeper is adjacent; a bump (below) names the keeper walked into.
        if gate is None:
            gate = self._adjacent_gate()
        if gate is None:
            self.messages.append(self.strings("msg.no_one"))
            return
        self.active = gate
        if not gate.passed:
            gate.state = GateState.INSTRUCTION
        self._overlay = self._lesson_overlay(gate)
        self._overlay_kind = "lesson"
        self.messages.append(self.strings.teach(gate.keeper.kind, name=gate.keeper.name))

    def _confirm(self) -> None:
        if self._overlay_kind == "help":
            # Space past the last page closes help the same way it closes the info/message panels
            # below (`_close_help`, not `_close_item`, since help must hand back whatever it was
            # stacked over rather than clearing it). Checked first: help can be stacked over a
            # lesson or a question, and `self.active` would otherwise still be set, which would
            # wrongly fall through to the lesson/question branches further down.
            self._close_help()
            return
        if self._overlay_kind == "drop_amount":
            self._drop_confirm()
            return
        if self._overlay_kind == "pickup_amount":
            self._pickup_confirm()
            return
        if self._overlay_kind == "info":
            # The Pack tab shows its focused row's description alongside the list at all times now
            # (DELVE-0075), so Confirm has nothing left to switch into there; every info tab just
            # closes the panel, like DELVE-0069 before it added the now-removed detail toggle.
            self._close_item()
            return
        if not self.active:
            return
        gate = self.active
        if self._overlay_kind == "question":
            # Confirm on a question is Enter: submit a free-text field, or answer the focused option
            # of an assertion or MCQ (both take arrow focus + Enter, as well as the direct key).
            kind = gate.current_question().kind
            if kind == "freetext":
                self._submit_text(self._answer_buf)
            else:
                self._answer(self._selected_option)
            return
        if self._overlay_kind == "lesson":
            if gate.passed:
                self._close(self.strings("msg.put_down"))
            else:
                gate.begin_exam(self.rng)
                self._present_question(gate)
                self.messages.append(self.strings("msg.examines", name=gate.keeper.name))
        elif self._overlay_kind == "explanation":
            # Whether the tile the pass reveals was already standing open (the tutorial's stairs
            # down are painted from the start), read before `proceed` reveals it, so the message
            # can say 'was open all along' rather than claim a wall just opened.
            already_open = (self.chapter.grid.at(gate.door_pos.x, gate.door_pos.y).kind
                            is gate.unlock_kind)
            result = gate.proceed(self.rng, self.chapter.grid)
            if result.outcome == "next":
                self._present_question(gate)
                self._clear_message()   # the last Correct./Not quite. must not linger onto the next
            elif result.outcome == "passed":
                self._record_pass(gate)
                self._close(self._pass_message(gate, already_open))
                self._pay_reward(gate)
                self._observe()
                self._save()
            else:  # failed or repelled: a missed sitting costs HP, charged once
                self._fail_sitting(gate, result)

    def _post(self, text: str, bg: Colour) -> None:
        """Append a message and remember a highlight colour for it (green Correct., red Not quite.).
        Plain messages just use `self.messages.append`; only a coloured line needs this."""
        self.messages.append(text)
        self._msg_styles[len(self.messages) - 1] = bg

    def _clear_message(self) -> None:
        """Blank the top line. The message clock is frozen while an overlay is open, so a
        Correct./Not quite. would otherwise linger onto the next question's screen; a fresh blank
        clears it (and carries no highlight)."""
        if self.messages and self.messages[-1] != "":
            self.messages.append("")

    def _answer(self, choice: int) -> None:
        if self._overlay_kind == "pickup_menu":
            self._pickup_select(choice)
            return
        if not self.active or self._overlay_kind != "question":
            return
        gate = self.active
        options = gate.display_options()
        if not 0 <= choice < len(options):
            return
        if choice in gate.eliminated:
            return   # a paid removal took this option; digits and focus skip it (DELVE-0018)
        q = gate.current_question()
        # MCQ options are numbered 1..n (not lettered), so the keys never clash with the map's
        # d/,/i and are faster to hit (OBJECTS.md); an assertion echoes its chosen label.
        header = f"{choice + 1} - {options[choice]}" if q.kind == "mcq" else options[choice]
        correct = gate.answer(choice)
        self._overlay = self._explanation_overlay(header, q.explanation)
        self._overlay_kind = "explanation"
        self._post(self.strings("msg.correct" if correct else "msg.not_quite"),
                   Colour.GREEN if correct else Colour.RED)

    def _present_question(self, gate: Gate) -> None:
        """Show the current question and reset the free-text buffer, so a fresh field is empty (the
        one place a new answer starts). Shared by the lesson->exam and explanation->next steps."""
        self._answer_buf = ""
        self._selected_option = self._first_standing(gate)
        self._overlay = self._question_overlay(gate)
        self._overlay_kind = "question"

    def _select(self, delta: int) -> None:
        """Move the option focus (the arrows) on an assertion's buttons or an MCQ's list, or, while
        the Pack tab's compact list is showing (DELVE-0069), the focused carried-kind row: the same
        command, dispatched on which one is actually open, since both are "move a list focus by
        +1/-1, Enter/space confirms it" in the same shape. Wraps either way, skipping options a
        paid removal eliminated (DELVE-0018). The number/label keys still answer a question
        directly, so this is an alternative way in there, not the only one; free text has no focus
        to move."""
        if self._overlay_kind == "info":
            self._pack_select(delta)
            return
        if not self.active or self._overlay_kind != "question":
            return
        if self.active.current_question().kind == "freetext":
            return
        n = len(self.active.display_options())
        if n == 0:
            return
        # Walk past eliminated options; if somehow every option is gone, stay put.
        cur = self._selected_option
        for _ in range(n):
            cur = (cur + delta) % n
            if cur not in self.active.eliminated:
                self._selected_option = cur
                break
        self._overlay = self._question_overlay(self.active)

    def _pack_select(self, delta: int) -> None:
        """Move the Pack tab's list-row focus (DELVE-0069): the description shown alongside it
        (DELVE-0075) rebuilds to match on every call. Wraps; a no-op off the Pack tab or with
        nothing carried, mirroring `_select`'s own guards above."""
        if _INFO_TABS[self._info_tab][0] != "pack":
            return
        n = len(self._pack_entries())
        if n == 0:
            return
        self._pack_row = (self._pack_row + delta) % n
        self._overlay = self._info_overlay()

    def _type_char(self, char: str) -> None:
        """Append one printable character to the free-text answer buffer and rebuild the field
        (Phase 2). Bounded so a runaway paste can't grow it without limit; longer than any real
        short answer. Ignored unless a free-text question is open."""
        if self._overlay_kind != "question" or not self.active:
            return
        if self.active.current_question().kind != "freetext":
            return
        if len(char) == 1 and char.isprintable() and len(self._answer_buf) < 200:
            self._answer_buf += char
            self._overlay = self._question_overlay(self.active)

    def _submit_text(self, answer: str) -> None:
        """Submit a typed free-text answer for grading, the string twin of `_answer` (PHASE2.md
        sections 4, 5.3). The grader-runner grades it inline (the keyword floor: the verdict is
        ready at once and the explanation shows immediately, so a headless run is one step) or on a
        worker (the LLM: a 'grading' overlay shows and the verdict is folded in later by a poll)."""
        if not self.active or self._overlay_kind != "question":
            return
        gate = self.active
        if gate.current_question().kind != "freetext":
            return
        self._answer_buf = answer
        self._pending_answer = answer
        verdict = self._grader_runner.submit(gate.current_question(), answer)
        if verdict is not None:
            self._resolve_text(verdict)
        else:
            self._overlay = self._grading_overlay(answer)
            self._overlay_kind = "grading"
            self._grade_ticks = 0
            self.messages.append(self.strings("msg.grading"))

    def _poll_grade(self) -> None:
        """A grading tick: if the worker has a verdict ready *and* the overlay has been up long
        enough to read, fold it into the explanation; else stay on the 'grading' overlay (PHASE2.md
        section 5.3). Holding a ready verdict for `_GRADE_MIN_TICKS` keeps a fast grade from
        flashing past unread. A no-op unless a grade is pending."""
        if self._overlay_kind != "grading":
            return
        self._grade_ticks += 1
        verdict = self._grader_runner.poll()
        if verdict is not None and self._grade_ticks >= _GRADE_MIN_TICKS:
            self._resolve_text(verdict)

    def _resolve_text(self, verdict) -> None:
        """Fold a free-text verdict into the explanation: record the score, show the explanation,
        and colour the message line green/red. Shared by the inline and worker paths, so a grade
        lands the same way whether it took a microsecond or a second."""
        gate = self.active
        correct = verdict.correct
        gate.record_text_verdict(correct)
        q = gate.current_question()
        header = (self._pending_answer or "").strip() or self.strings("question.blank")
        self._overlay = self._explanation_overlay(header, q.explanation)
        self._overlay_kind = "explanation"
        self._post(self.strings("msg.correct" if correct else "msg.not_quite"),
                   Colour.GREEN if correct else Colour.RED)
        self._pending_answer = None

    def _consult(self) -> None:
        if self.pet is None:                                  # a soloist has no one to ask
            self.messages.append(self.strings("msg.no_companion"))
            return
        if not self.active or self._overlay_kind != "question":
            self.messages.append(self.strings("msg.pet_nothing", name=self.pet.name))
            return
        gate = self.active
        if gate.current_question().kind == "freetext":
            # There is no option to nose aside on a free-text question; the pet just shrugs.
            self.messages.append(self.strings("msg.pet_nothing", name=self.pet.name))
            return
        if gate.assisted_here:
            self.messages.append(self.strings("msg.pet_already", name=self.pet.name))
            return
        # The cat is the clever one: its first consult in each room is free, no score cost; a dog's
        # consult always costs the question (OBJECTS.md section 8).
        free = self.pet.species == "cat" and not gate.free_consult_used
        q = gate.current_question()
        gate.consult(self.pet.hint_for(q), free=free)
        self._overlay = self._question_overlay(gate)
        self._overlay_kind = "question"
        self.messages.append(self.strings("msg.pet_free" if free else "msg.pet_strike",
                                          name=self.pet.name))

    def _reward_basis(self, gate: Gate) -> int:
        """The room's unscaled reward basis `R`: the room's own `reward`, or the pack default when
        the room sets none. An unscored floor (the tutorial) never inherits the pack default
        (same rule as `_pay_reward`). Used for the paid-removal price (DELVE-0018); the paid
        reward itself still scales by sitting score after a pass."""
        reward = gate.content.reward
        if reward is None:
            reward = self.pack.reward if (self.cur.scored and self.pack is not None) else 0
        return reward

    def _removal_price(self, gate: Gate) -> int | None:
        """Gold cost to eliminate one wrong option now, or None when the lifeline is unavailable:
        unscored floor, free-text/assertion, fewer than three options still standing, or a zero
        reward basis. Price is `round(R / (n - 1))` with `n` still standing (DELVE-0018)."""
        if not self.cur.scored or self._overlay_kind != "question":
            return None
        if gate.current_question().kind != "mcq":
            return None
        reward = self._reward_basis(gate)
        if reward <= 0:
            return None
        standing = gate.standing_count()
        if standing < 3:
            return None
        return round(reward / (standing - 1))

    def _first_standing(self, gate: Gate) -> int:
        """The lowest display index that is still selectable (not eliminated)."""
        for i in range(len(gate.display_options())):
            if i not in gate.eliminated:
                return i
        return 0

    def _buy_removal(self) -> None:
        """Spend gold to eliminate one wrong MCQ option. The coin is the price; the question keeps
        counting toward the score (unlike a pet consult). Immediate on the keypress; the hint line
        shows the price beforehand (DELVE-0018)."""
        if not self.active or self._overlay_kind != "question":
            self.messages.append(self.strings("msg.buy_nothing"))
            return
        gate = self.active
        price = self._removal_price(gate)
        if price is None:
            self.messages.append(self.strings("msg.buy_nothing"))
            return
        if self.player.gold < price:
            self.messages.append(self.strings("msg.buy_poor", coins=self._coins(price)))
            return
        original = gate.next_wrong_to_eliminate()
        if original is None:
            self.messages.append(self.strings("msg.buy_nothing"))
            return
        self.player.gold -= price
        gate.eliminate(original)
        if self._selected_option in gate.eliminated:
            self._selected_option = self._first_standing(gate)
        self._overlay = self._question_overlay(gate)
        self._overlay_kind = "question"
        self.messages.append(self.strings("msg.buy_remove", coins=self._coins(price)))

    def _rest(self) -> None:
        if self.active or self._overlay is not None:
            return
        if self.player.hp >= self.player.max_hp:
            self.messages.append(self.strings("msg.already_whole"))
            return
        self.player.hp = self.player.max_hp
        self.turn += 1
        self.messages.append(self.strings("msg.rested"))
        self._pet_step()

    def _wait(self) -> None:
        """Stand still for a turn so the companion can act while you hold position (PETS.md
        section 4): send a dog after a distant coin, or let a fleeing cat run out of room."""
        if self.active or self._overlay is not None:
            return
        self.turn += 1
        self._observe()
        self._pet_step()

    def _descend(self) -> None:
        if self.active or self._overlay is not None:
            return
        if self.chapter.grid.at(*self.player.pos).kind is not TileKind.STAIRS_DOWN:
            self.messages.append(self.strings("msg.no_stairs_down"))
            return
        if self.idx + 1 >= len(self.chapters):
            return
        self.idx += 1
        arrival = self.chapter.stairs_up or self.chapter.start
        self.player.pos = arrival
        if self.pet is not None:
            self.pet.pos = self._pet_spot()
        self.turn += 1
        self._observe()
        self.messages.append(self.strings("msg.descend", title=self.cur.title))
        self._save()

    def _ascend(self) -> None:
        if self.active or self._overlay is not None:
            return
        if self.chapter.grid.at(*self.player.pos).kind is not TileKind.STAIRS_UP:
            self.messages.append(self.strings("msg.no_stairs_up"))
            return
        if self.idx == 0:
            return
        self.idx -= 1
        self.player.pos = self.chapter.stairs_down or self.chapter.start
        if self.pet is not None:
            self.pet.pos = self._pet_spot()
        self.turn += 1
        self._observe()
        self.messages.append(self.strings("msg.ascend", title=self.cur.title))
        self._save()

    def _dismiss(self) -> None:
        if self._overlay_kind == "help":
            self._close_help()
            return
        if self._overlay_kind == "drop_amount":
            # DELVE-0081: the amount field is only ever reached from Info/Pack now, so Esc backs
            # out to Pack (updated if anything changed), not out of the panel entirely.
            self._close_pack_drop()
            return
        if self._overlay_kind in ("info", "pickup_menu", "pickup_amount"):
            # The Pack tab has no separate detail mode to back out of any more (DELVE-0075): its
            # list and the focused row's description show together at all times, so Esc always
            # just closes the panel here, same as every other tab.
            self._close_item()
            return
        if not self.active:
            return
        self.active.abandon()
        self._close(self.strings("msg.put_down"))

    # -- objects: money, pickup, drop, inventory (OBJECTS.md) ----------------------------

    def _collect_money(self, pos: Point) -> None:
        """Step onto a tile and every currency stack there banks straight to gold, no key
        (OBJECTS.md). Currency is `carriable=False`: money, and any pack kind with a `value`, banks
        by worth rather than filling an inventory slot. Carriable objects are left for `,`."""
        pile = self.items.get(pos)
        if not pile:
            return
        keep = [s for s in pile if s.defn.carriable]
        banked = sum(s.worth for s in pile if not s.defn.carriable)
        if banked <= 0:
            return
        self.player.gold += banked
        self._set_pile(pos, keep)
        self.messages.append(self.strings("item.collect", coins=self._coins(banked)))

    def _pay_reward(self, gate: Gate) -> None:
        """On a pass, a keeper may drop coins on the floor of the room, for the learner to walk over
        and auto-collect (OBJECTS.md section 7). The amount is the room's `reward`, or the pack
        default when the room sets none, **scaled by how well the room was passed** (a play-testing
        note: a better score earns more). Paid once (a re-read never re-pays, rule 3); if a bulky
        item sits on the chosen tile it is skipped rather than lost.

        The coins land on a random interior tile of the room (`_reward_tile`), not on the way out:
        on the exit the learner is always nearer than a roaming pet, so there is no race for them;
        inside the room there is (and, before the pet roams, at least a detour worth taking,
        section 5). The tile is random rather than the far corner so a room never gives its shape
        away by always filing the reward into the same spot (DELVE-0015).

        An unscored floor (the tutorial) must not inherit the *main* pack's reward default
        (PLAN §9); it still pays when a room sets an explicit `reward:` (DELVE-0031)."""
        if gate.rewarded:
            return
        reward = self._reward_basis(gate)
        coins = round(reward * gate.passed_score)
        if coins <= 0:
            return
        pos = self._reward_tile(gate)
        pile = self.items.get(pos, [])
        if not can_place(pile, MONEY):
            return
        gate.rewarded = True
        self._set_pile(pos, merged(pile, Stack(MONEY, coins)))
        self.messages.append(self.strings("item.reward", name=gate.keeper.name,
                                           coins=self._coins(coins)))

    def _reward_tile(self, gate: Gate) -> Point:
        """A walkable floor tile chosen at random from the keeper's room interior, so the coins
        scatter rather than always filing into the same far corner (DELVE-0015). The keeper's and
        the learner's tiles are excluded; falls back to the door if the room is somehow too tight
        to hold an eligible tile.

        The draw is deterministic so a run stays regenerable tile-for-tile: it spins a dedicated
        stream seeded from the run seed and the room's content id, which is stable across a resume
        (a `room_results`-grade key, not turn-order state). It never touches `self.rng`, which
        shuffles the exam, keeping every RNG family separate (CLAUDE.md)."""
        room = next((r for r in self.chapter.rooms if r.contains(gate.keeper.pos)), None)
        if room is None:
            return gate.door_pos
        grid = self.chapter.grid
        eligible = [p for p in room.interior()
                    if grid.walkable(p.x, p.y) and p not in self.keepers and p != self.player.pos]
        if not eligible:
            return gate.door_pos
        eligible.sort(key=lambda p: (p.y, p.x))          # a stable order to draw from
        rng = Rng(self.seed * 100 + 850 + zlib.crc32(gate.content.id.encode()))
        return rng.choice(eligible)

    def _carry_flavour(self) -> None:
        """Ambient carry flavour: a carried kind's `on_move` line, but low-priority and occasional
        (OBJECTS.md section 9, refined in play). It only speaks on about half your steps (a coin
        flip on `flavour_rng`), the caller has already suppressed it when a real message spoke this
        step, and after `_FLAVOUR_FULL_TIMES` full utterances it drops to the item's short form if
        it has one (a coconut says the whole line a few times, then just "Clip-clop"). Deduped by
        kind for free (one inventory stack per kind), and silent below `on_move_min` (a lone coconut
        half has nothing to bang against)."""
        for s in self.player.inventory:
            d = s.defn
            if not d.on_move or s.count < d.on_move_min:
                continue
            if self.flavour_rng.randint(0, 99) >= _FLAVOUR_CHANCE:
                continue                       # this step it stays quiet
            said = self._carry_said.get(d.id, 0)
            self._carry_said[d.id] = said + 1
            abbreviate = bool(d.on_move_short) and said >= _FLAVOUR_FULL_TIMES
            self.messages.append(d.on_move_short if abbreviate else d.on_move)

    def _see_here(self, pos: Point) -> None:
        """After a step, name any carriable object underfoot, so it is noticed and the `,` key has a
        reason to exist. Currency is not named: it auto-banks and already prints its own line."""
        piles = [s for s in self.items.get(pos, []) if s.defn.carriable]
        if piles:
            what = ", ".join(self._item_phrase(s.defn, s.count) for s in piles)
            self.messages.append(self.strings("item.here", what=what))

    def _pickup(self) -> None:
        """Take carriable objects off the tile. One kind goes straight to a how-many choice;
        several kinds open a menu first, so you say which and then how many (play-testing note: a
        stack of two should ask, not grab both). Currency is not here; it auto-banks on the step."""
        if self.active or self._overlay is not None:
            return
        pos = self.player.pos
        carriable = [s for s in self.items.get(pos, []) if s.defn.carriable]
        if not carriable:
            self.messages.append(self.strings("item.pickup_none"))
            return
        self._pickables = [(s.defn.id, self._label(s.defn.id, s.defn.name, s.count, s.charge),
                            s.count, s.charge) for s in carriable]
        if len(self._pickables) == 1:
            self._pickup_select(0)
            return
        self._overlay = self._pickup_menu_overlay()
        self._overlay_kind = "pickup_menu"

    def _pickup_select(self, choice: int) -> None:
        if not 0 <= choice < len(self._pickables):
            return
        def_id, label, available, charge = self._pickables[choice]
        if available <= 1:                       # a single unit: nothing to count, take it
            self._do_pickup(def_id, 1, charge)
            return
        self._pending = (def_id, label, available, charge)
        self._amount_buf = ""
        self._overlay = self._amount_overlay("pickup")
        self._overlay_kind = "pickup_amount"

    def _pickup_confirm(self) -> None:
        amount = int(self._amount_buf) if self._amount_buf else 0
        if self._pending is None or amount <= 0:      # nothing typed: treat Enter as a cancel
            self._close_item()
            return
        self._do_pickup(self._pending[0], amount, self._pending[3])

    def _do_pickup(self, def_id: str, count: int, charge=ANY_CHARGE) -> None:
        """Lift `count` of a kind off the tile into the pack. `on_pickup` fires only when the kind
        first enters your hands (OBJECTS.md section 9), so the USB lesson lands on the first grab,
        not on every re-pickup of one you already carry. `charge` (DELVE-0067) picks which floor
        stack to take when the tile holds more than one differently-charged torch; every other kind
        passes its own `charge`, always `None`, which matches trivially."""
        pos = self.player.pos
        if def_id == TORCH.id:
            self._do_pickup_torch(pos, count, charge)
            return
        took, rest = taken(self.items.get(pos, []), def_id, count, charge)
        if took is None:
            self._close_item()
            return
        newly = def_id not in {s.defn.id for s in self.player.inventory}
        self.player.inventory = merged(self.player.inventory, took)
        self._set_pile(pos, rest)
        self.turn += 1
        # The first grab of a kind shows its `on_pickup` flavour *instead of* the plain line (the
        # coconut's "Suspiciously horse-like." is the pickup message), count-aware via an authored
        # plural form; every later grab, and any kind without flavour, gets the plain "You pick up".
        flavour = self._pickup_flavour(took.defn, count) if newly else ""
        self.messages.append(flavour or
                             self.strings("item.pickup", what=self._item_phrase(took.defn, count)))
        self._pet_step()
        self._close_item()

    def _do_pickup_torch(self, pos: Point, count: int, charge=ANY_CHARGE) -> None:
        """A torch is never just another carried kind (DELVE-0062): picked up while already lit, it
        stows as a spare like anything else; picked up dark, it catches immediately instead, which
        is the one pickup that changes what the learner can see, so it re-observes on the spot.
        Relighting now carries over the taken stack's own remembered `charge` (DELVE-0067) rather
        than always jumping to full duration; a never-lit stack's `charge` is `None`, which reads
        as full duration, so a fresh torch still catches at `TORCH_DURATION_STEPS` as before."""
        took, rest = taken(self.items.get(pos, []), TORCH.id, count, charge)
        if took is None:
            self._close_item()
            return
        self._set_pile(pos, rest)
        self.turn += 1
        if self.has_light:
            self.player.inventory = merged(self.player.inventory, took)
            self.messages.append(self.strings("item.torch_pickup_stowed"))
        else:
            self.player.torch_charge = took.charge if took.charge is not None \
                else TORCH_DURATION_STEPS
            spare = took.count - 1
            if spare > 0:
                self.player.inventory = merged(self.player.inventory,
                                               Stack(TORCH, spare, took.charge))
            self.messages.append(self.strings("item.torch_pickup_lit"))
            self._observe()
        self._pet_step()
        self._close_item()

    def _pickup_flavour(self, defn, count: int) -> str:
        """A kind's `on_pickup` line for this many, or "" if it has none. More than one uses the
        authored `on_pickup_plural` (its `{count}` slot filled with the number word); one, or a kind
        with no plural form, uses `on_pickup`."""
        if count > 1 and defn.on_pickup_plural:
            return defn.on_pickup_plural.format(count=self._number(count))
        return defn.on_pickup

    def _inventory(self) -> None:
        # Always opens on Pack (a playtesting request reversing DELVE-0040's original "sticky
        # across opens" choice): a learner reopening the panel kept landing on whatever tab they
        # last happened to leave it on, which read as broken navigation rather than a remembered
        # preference. `_tab_cycle` still remembers the active tab while the panel stays open.
        if self.active or self._overlay is not None:
            return
        self._info_tab = 0
        self._info_subtab = 0
        self._info_sub_focus = False
        self._pack_row = 0
        self._overlay = self._info_overlay()
        self._overlay_kind = "info"

    def _help(self) -> None:
        """Open help over whatever is showing (walking, a lesson, a question, the backpack, ...),
        or close it back to exactly that on a second `?` (DELVE-0028). Unlike every other panel,
        help can stack over an already-open overlay rather than requiring none be open, since the
        whole point is to be reachable from any context; `_prior_overlay(_kind)` is what makes
        that a real stack of depth one rather than help simply replacing what was there. Always
        opens on Keys (a playtesting request reversing DELVE-0028's original "sticky across opens"
        choice, the same reversal `_inventory` makes for `i`)."""
        if self._overlay_kind == "help":
            self._close_help()
            return
        self._help_tab = 0
        self._prior_overlay, self._prior_overlay_kind = self._overlay, self._overlay_kind
        self._overlay = self._help_overlay()
        self._overlay_kind = "help"

    def _close_help(self) -> None:
        self._overlay, self._overlay_kind = self._prior_overlay, self._prior_overlay_kind
        self._prior_overlay, self._prior_overlay_kind = None, None

    def _active_subtabs(self) -> tuple:
        """The active primary tab's own sub-tabs, or `()` if it has none. Only Scoring has any so
        far; shared by `_sub_tab_cycle` and `_focus_row` so neither hard-codes the check twice."""
        is_scoring = _INFO_TABS[self._info_tab][0] == "scoring"
        return _SCORING_SUBTABS if is_scoring else ()

    def _tab_cycle(self, delta: int) -> None:
        """Move the info panel's active primary tab by `delta`, wrapping (Tab/Shift-Tab, or
        left/right when the primary row has focus). Only the panel's tab strip changes; other
        overlays (a menu, a question) ignore this command. The sub-tab index and row focus both
        reset (DELVE-0055/DELVE-0056): neither is run state worth carrying across a primary-tab
        round trip, so re-entering Scoring always lands back on Now with the primary row focused."""
        if self._overlay_kind == "help":
            self._help_tab = (self._help_tab + delta) % len(_HELP_TABS)
            self._overlay = self._help_overlay()
            return
        if self._overlay_kind != "info":
            return
        self._info_tab = (self._info_tab + delta) % len(_INFO_TABS)
        self._info_subtab = 0
        self._info_sub_focus = False
        self._pack_row = 0
        self._overlay = self._info_overlay()

    def _sub_tab_cycle(self, delta: int) -> None:
        """Move the info panel's active sub-tab by `delta` (DELVE-0055, '['/']', or left/right
        when the sub-tab row has focus, DELVE-0056), wrapping. A no-op, not an error, on a primary
        tab with no sub-tabs (INFOSCREEN.md §5: the hint never advertises a key that does nothing,
        and `ui` maps the key to this command regardless of which tab is active, rule 2; deciding
        whether it does anything is `session`'s job)."""
        if self._overlay_kind != "info":
            return
        subtabs = self._active_subtabs()
        if not subtabs:
            return
        self._info_subtab = (self._info_subtab + delta) % len(subtabs)
        self._overlay = self._info_overlay()

    def _focus_row(self, delta: int) -> None:
        """Move the info panel's keyboard focus between its tab rows (up/down, DELVE-0056):
        negative moves to the primary row unconditionally; positive moves to the active tab's
        sub-tab row, but only when it has one (a no-op elsewhere, the same shape `_sub_tab_cycle`
        already uses). Left/right (and Tab/Shift-Tab) then cycle whichever row this leaves
        focused; `ui` maps the arrow keys to this command regardless of the active tab (rule 2)."""
        if self._overlay_kind != "info":
            return
        if delta > 0:
            if not self._active_subtabs():
                return
            self._info_sub_focus = True
        else:
            self._info_sub_focus = False
        self._overlay = self._info_overlay()

    def _drop(self) -> None:
        """Drop the Info/Pack tab's currently focused row (DELVE-0081, replacing the old
        standalone drop menu that made the learner pick the same kind a second time): a lone unit
        (including the currently-burning torch) drops at once; a multi-count pile (coins, spare
        torches) still asks how many first, the same amount field the old flow already had. A
        no-op off the Pack tab, or with nothing carried to focus a row on."""
        if self._overlay_kind != "info" or _INFO_TABS[self._info_tab][0] != "pack":
            return
        entries = self._pack_entries()
        if not entries:
            return
        def_id, label, available, charge = self._pack_droppable(self._pack_row)
        if available <= 1:                       # a single unit: no amount to type, drop it
            self._do_drop(def_id, 1, charge)
            return
        self._pending = (def_id, label, available, charge)
        self._amount_buf = ""
        self._overlay = self._amount_overlay("drop")
        self._overlay_kind = "drop_amount"

    def _type_digit(self, value: int) -> None:
        """Append a typed digit to the amount, dropping leading zeros and clamping to the maximum,
        so typing past the amount involved just pins it there rather than erroring. Shared by the
        drop and pickup amount fields."""
        if self._overlay_kind not in ("drop_amount", "pickup_amount") or self._pending is None:
            return
        raw = (self._amount_buf + str(value)).lstrip("0")
        self._amount_buf = str(min(int(raw), self._pending[2])) if raw else ""
        self._rebuild_amount()

    def _backspace(self) -> None:
        if self._overlay_kind == "question" and self.active \
                and self.active.current_question().kind == "freetext":
            self._answer_buf = self._answer_buf[:-1]
            self._overlay = self._question_overlay(self.active)
            return
        if self._overlay_kind not in ("drop_amount", "pickup_amount"):
            return
        self._amount_buf = self._amount_buf[:-1]
        self._rebuild_amount()

    def _rebuild_amount(self) -> None:
        action = "pickup" if self._overlay_kind == "pickup_amount" else "drop"
        self._overlay = self._amount_overlay(action)

    def _drop_confirm(self) -> None:
        amount = int(self._amount_buf) if self._amount_buf else 0
        if self._pending is None or amount <= 0:      # nothing typed: treat Enter as a cancel
            self._close_pack_drop()
            return
        self._do_drop(self._pending[0], amount, self._pending[3])

    def _do_drop(self, def_id: str, count: int, charge=ANY_CHARGE) -> None:
        """Put `count` of a kind onto the player's tile, from gold (money) or the pack (a carriable
        stack). Refused, with a message, if a bulky item would have to share the tile. `charge`
        (DELVE-0067) picks which pack stack to drop when the pack holds more than one
        differently-charged torch spare; every other kind passes its own `charge`, always `None`.
        Only ever reached from the Info/Pack tab now (DELVE-0081), so every exit rebuilds Pack
        (`_close_pack_drop`) rather than closing the panel outright."""
        if def_id == _LIT_TORCH_ID:
            self._do_drop_lit_torch()
            return
        pos = self.player.pos
        pile = self.items.get(pos, [])
        if def_id == MONEY.id:
            defn, count, charge = MONEY, min(count, self.player.gold), None
        else:
            stack = next((s for s in self.player.inventory if s.defn.id == def_id
                         and (charge is ANY_CHARGE or s.charge == charge)), None)
            if stack is None:
                self._close_pack_drop()
                return
            defn, count, charge = stack.defn, min(count, stack.count), stack.charge
        if count <= 0:
            self._close_pack_drop()
            return
        if not can_place(pile, defn):
            self.messages.append(self.strings("item.no_room"))
            self._close_pack_drop()
            return
        if def_id == MONEY.id:
            self.player.gold -= count
        else:
            _, self.player.inventory = taken(self.player.inventory, def_id, count, charge)
        self._set_pile(pos, merged(pile, Stack(defn, count, charge)))
        self.turn += 1
        self.messages.append(self.strings("item.drop", what=self._item_phrase(defn, count)))
        self._pet_step()
        self._close_pack_drop()

    def _do_drop_lit_torch(self) -> None:
        """Drop the currently-burning torch itself (a playtesting request, to reach the unlit
        ambient prose deliberately rather than only by waiting `TORCH_DURATION_STEPS` out): unlike
        every other carried thing, it's not a `Stack` (DELVE-0062's own steps-remaining counter,
        not a spare count), so it needs its own path rather than `_do_drop`'s generic one that reads
        `player.inventory`. Extinguishes on the spot (`has_light` reads False immediately, so
        `_observe` re-darkens vision) and leaves a torch `Stack(1)` carrying its own remaining
        `charge` (DELVE-0067) on the tile, exactly what picking it back up unlit relights at
        (`_do_pickup_torch`'s own `else` branch), rather than silently refilling it."""
        pos = self.player.pos
        pile = self.items.get(pos, [])
        if not can_place(pile, TORCH):
            self.messages.append(self.strings("item.no_room"))
            self._close_pack_drop()
            return
        # Normalised to `None` at exactly full duration, so a torch dropped the instant it is lit
        # merges with an untouched fresh one on the same tile instead of rendering as a spuriously
        # distinct "full duration" charge (DELVE-0067's merge-by-charge rule in `items.merged`).
        n = self.player.torch_charge
        charge = None if n == TORCH_DURATION_STEPS else n
        self.player.torch_charge = 0
        self._set_pile(pos, merged(pile, Stack(TORCH, 1, charge)))
        self.turn += 1
        self.messages.append(self.strings("item.drop", what=self._torch_noun(1)))
        self._observe()
        self._pet_step()
        self._close_pack_drop()

    def _close_item(self) -> None:
        self._overlay = None
        self._overlay_kind = None
        self._pickables = []
        self._pending = None
        self._amount_buf = ""

    def _close_pack_drop(self) -> None:
        """Where every Pack-tab drop lands (DELVE-0081), whether it dropped something, was
        cancelled, or was refused: back on Info/Pack rather than closed outright, since the whole
        flow now starts there. `_pack_row` is clamped to the rebuilt list, which may have lost a
        row (the dropped kind's only stack) or shrunk a pile without losing the row entirely."""
        self._pending = None
        self._amount_buf = ""
        entries = self._pack_entries()
        self._pack_row = min(self._pack_row, max(0, len(entries) - 1))
        self._overlay = self._info_overlay()
        self._overlay_kind = "info"

    def _set_pile(self, pos: Point, pile: list[Stack]) -> None:
        if pile:
            self.items[pos] = pile
        else:
            self.items.pop(pos, None)

    def _coins(self, n: int) -> str:
        return self.strings("item.coin_one") if n == 1 else self.strings("item.coins", n=n)

    def _torch_noun(self, n: int) -> str:
        # The torch is engine-owned, not pack content (DELVE-0062), so its name never comes from
        # `ItemDef.name`: bypassing it here, the same way `_coins` bypasses money's, is what pins
        # the Dutch word to "fakkel"/"fakkels" regardless of what the ambient prose model says.
        return self.strings("item.torch_one") if n == 1 else self.strings("item.torches", n=n)

    def _torch_charge_label(self, count: int, charge: int | None) -> str:
        """An unlit torch's label, spare or on the floor (DELVE-0067): always names its remaining
        steps, so a never-lit stack (`charge=None`) reads as full duration rather than blank or
        charge-less, and two stacks that differ only in charge (never merged, see `items.merged`)
        show up as visibly distinct entries instead of folding into one indistinguishable pile."""
        n = charge if charge is not None else TORCH_DURATION_STEPS
        if count == 1:
            return self.strings("item.torch_charge_one", n=n)
        return self.strings("item.torch_charge_many", n=n, count=count)

    def _label(self, def_id: str, name: str, count: int, charge: int | None = None) -> str:
        if def_id == MONEY.id:
            return self._coins(count)
        if def_id == TORCH.id:
            return self._torch_charge_label(count, charge)
        return name if count == 1 else f"{name} ({count})"

    def _item_phrase(self, defn, count: int) -> str:
        """A natural noun phrase for prose messages: "a coconut half", "two coconut halves". Money
        keeps its coin wording. The article and the number word come from the locale (item.one /
        item.many), so English says "a"/"two" and Dutch "een"/"twee"; a/an is not distinguished
        (no shipped kind needs "an")."""
        if defn.id == MONEY.id:
            return self._coins(count)
        if defn.id == TORCH.id:
            return self._torch_noun(count)
        if count == 1:
            return self.strings("item.one", name=defn.name)
        plural = defn.plural or f"{defn.name}s"
        return self.strings("item.many", count=self._number(count), plural=plural)

    def _number(self, n: int) -> str:
        """A small count as a word ("two"), from the locale's number list, falling back to digits
        for anything past the end (no pack places that many, so it stays a graceful tail)."""
        words = self.strings("item.numbers")
        return words[n] if 0 <= n < len(words) else str(n)

    def _pack_droppable(self, idx: int) -> tuple[str, str, int, int | None]:
        """The (def_id, label, available, charge) a Pack-tab row drops (DELVE-0081), in exactly
        `_pack_entries`'s own order (lit torch, gold, inventory stacks), so a row's focus and its
        drop target always name the same carried thing."""
        out: list[tuple[str, str, int, int | None]] = []
        if self.cur.scored and self.player.torch_charge > 0:
            out.append((_LIT_TORCH_ID,
                       self.strings("item.torch_lit_menu", n=self.player.torch_charge), 1, None))
        if self.player.gold > 0:
            out.append((MONEY.id, self._coins(self.player.gold), self.player.gold, None))
        out += [(s.defn.id, self._label(s.defn.id, s.defn.name, s.count, s.charge), s.count,
                s.charge) for s in self.player.inventory]
        return out[idx]

    def _title_block(self, label: str, look: str) -> TextBlock:
        """One item's block: a bold title, then its description on the next line (a '\\n' hard
        break, so there is no blank row between them), the shape every carried item shares
        (DELVE-0073: money and the torch used to be bare plain-text lines with no description,
        unlike a pack-authored item's own `look`)."""
        look = _reflow(look)
        spans = ((label, True), ("\n" + look, False))
        return TextBlock("para", f"{label}\n{look}", spans=spans)

    def _pack_entries(self) -> list[tuple[str, str | None]]:
        """Every carried kind as (label, look) pairs, in the order the Pack tab lists them
        (DELVE-0069, replacing the old single-block-per-item `_pack_body`): the lit torch first,
        then gold, then inventory stacks. `look` is a generic description for the torch/money
        (they carry no `ItemDef`), the item file's own authored body for a pack-authored kind that
        has one, or `None` for a kind with no `look` at all (its detail view then shows only the
        bold label, exactly as before this issue).

        The currently-burning torch is never a `Stack` (DELVE-0062: it's a steps-remaining
        counter, not a spare count), so without this it never appeared anywhere the learner could
        see it, unlike every other thing they carry. Exempt on the tutorial floor (`self.cur.
        scored`), which never uses the mechanic (`has_light` reads True there regardless of
        charge), so the pack there stays exactly as it was before this issue."""
        entries: list[tuple[str, str | None]] = []
        if self.cur.scored and self.player.torch_charge > 0:
            label = self.strings("item.torch_lit_menu", n=self.player.torch_charge)
            entries.append((label, self.strings("item.torch_look")))
        if self.player.gold > 0:
            entries.append((self._coins(self.player.gold), self.strings("item.money_look")))
        for s in self.player.inventory:
            label = self._label(s.defn.id, s.defn.name, s.count, s.charge)
            entries.append((label, s.defn.look or None))
        return entries

    def _pack_rows(self) -> list[str]:
        """Just the labels from `_pack_entries`, the Pack tab's compact list content (DELVE-0069)
        and a convenience for tests that only care what shows, not each row's description."""
        return [label for label, _ in self._pack_entries()]

    def _pack_detail_body(self, idx: int) -> list[TextBlock]:
        """One selected carried kind's own detail view (DELVE-0069): a bold title, then its
        description reflowed as a paragraph, the same shape `_title_block` has always given a
        carried item (DELVE-0073); a kind with no `look` at all shows only the bold label, same as
        before this issue. `look` is stored verbatim for a pack-authored kind (the item file's
        body, wrapped at the author's source width); `_title_block` reflows its soft-wrapped lines
        into paragraphs, or the source line breaks would show as hard breaks in the panel
        (DELVE-0029)."""
        entries = self._pack_entries()
        label, look = entries[idx]
        if look is None:
            return [TextBlock("para", label, spans=((label, True),))]
        return [self._title_block(label, look)]

    def _scoring_now_body(self) -> list[TextBlock]:
        """The Scoring > Now sub-tab's body (DELVE-0042/0043, INFOSCREEN.md §6.1; renamed from
        `_scoring_body` at DELVE-0055 when Scoring grew a sub-tab strip, output unchanged): one bar
        row per scored chapter (its mean `passed_score` across passed gates, mirroring
        `pack_score`'s own averaging rule but scoped to one chapter; `n/a` if the chapter has no
        passed gate yet, never a misleading `0%`), then one bar row for current HP vs max. The
        tutorial floor (`scored=False`) is never listed, the same rule `pack_score` already
        follows. Each row is a `kind="bar"` block carrying `(label, frac, tail)`; `ui` owns the
        bar's column width and glyph colouring (rule 2), so `text` here is only a plain-text
        fallback."""
        body = [TextBlock("plain", self.strings("item.progress_chapters"))]
        for cr in self.chapters:
            if not cr.scored:
                continue
            scores = [g.passed_score for g in cr.gates.values() if g.passed]
            frac = sum(scores) / len(scores) if scores else None
            tail = f"{round(frac * 100)}%" if frac is not None else "n/a"
            body.append(TextBlock("bar", f"{cr.title} {tail}", bar=(cr.title, frac, tail)))
        hp_frac = self.player.hp / self.player.max_hp if self.player.max_hp else 0.0
        hp_tail = f"{self.player.hp}/{self.player.max_hp}"
        body.append(TextBlock("bar", f"HP {hp_tail}", bar=("HP", hp_frac, hp_tail)))
        return body

    def _scoring_rooms_body(self) -> list[TextBlock]:
        """The Scoring > Rooms sub-tab's body (DELVE-0055, INFOSCREEN.md §6.4A mock-up C): one row
        per scored chapter, `Dlvl {n}` ('Dlvl' stays the bare NetHack label, never localised, same
        as the status line) followed by one glyph per room in the chapter's own gate order, then a
        legend line. The tutorial floor is excluded the same way `_scoring_now_body` excludes it.
        Never coloured (this story's non-goals; a plain-text fallback the same as the bar rows).
        Condensed into one block via `_condensed` (DELVE-0059), a playtesting fix: a dense list of
        one-liners the same shape as Keys/Objectives/Status/Messages, wasting a row per chapter."""
        lines = []
        for cr in self.chapters:
            if not cr.scored:
                continue
            glyphs = "".join(_room_glyph(g) for g in cr.gates.values())
            lines.append(f"Dlvl {cr.chapter.dlvl}  {glyphs}")
        lines.append(self.strings("item.rooms_legend"))
        return self._condensed(lines)

    def _grader_info(self) -> tuple[str, str] | None:
        """The configured grader's model/host (DELVE-0044), or None when no model was given (the
        default `InlineGrader`/`KeywordGrader` floor). Reached by duck-typing the runner rather
        than importing `assess.grader`/`assess.llm` types, so this stays a plain attribute read,
        not a new cross-layer dependency."""
        client = getattr(getattr(self._grader_runner, "grader", None), "client", None)
        return (client.model, client.host) if client is not None else None

    def _grader_body(self) -> list[TextBlock]:
        """The Grader tab's body content (DELVE-0054/DELVE-0066/DELVE-0087). Offline (no model
        configured) is a single explanatory line. Online returns the two columns flattened
        left-then-right so existing content tests can still read every row from one list; the
        Info overlay itself carries them as `grader_left`/`grader_right` via `_grader_columns`
        so `ui` can paint them side by side."""
        cols = self._grader_columns()
        if cols is None:
            return [TextBlock("plain", self.strings("item.grader_offline"))]
        left, right = cols
        return left + right

    def _grader_columns(self) -> tuple[list[TextBlock], list[TextBlock]] | None:
        """The Grader tab's two side-by-side sections (DELVE-0087), or None when no model is
        configured (the offline single-line state still goes through `_grader_body`/`body`, not a
        half column). Each column is one condensed `kind="kv"` block whose first line is the
        section heading, so the pager never inserts a blank row between the heading and its data
        (the blank that used to appear when they were two separate `TextBlock`s). Both columns
        always render when a model is configured, including a zeroed ambient section
        (DELVE-0066)."""
        grader = self._grader_info()
        if grader is None:
            return None
        model, host = grader
        metrics = getattr(self._grader_runner.grader, "metrics", None)
        left = self._grader_metrics_lines(model, host, metrics)
        ambient = self._ambient_info()
        model, host = ambient if ambient is not None else ("", "")
        right = self._ambient_metrics_lines(model, host, self._ambient_metrics)
        return left, right

    def _grader_metrics_lines(self, model: str, host: str, metrics) -> list[TextBlock]:
        """The grading model's own headed `Model`/`Status`/`This run`/`Avg latency`/`Latency`
        column (DELVE-0066/DELVE-0087), factored out of `_grader_columns` so the same shape (bar
        the verdict-count row, `_ambient_metrics_lines`'s own concern) is not duplicated across
        the two sections. `Model` and `This run` each occupy two string keys so the narrower
        column width fits without mid-word wraps."""
        lines = [
            self.strings("item.grader_section_grading"),
            self.strings("item.grader_model", model=model),
            self.strings("item.grader_model_host", host=host),
        ]
        if metrics is None or metrics.last_latency_ms is None:
            lines.append(self.strings("item.grader_status_none"))
        else:
            key = "item.grader_status_warm" if metrics.last_warm else "item.grader_status_cold"
            lines.append(self.strings(key, ms=metrics.last_latency_ms))
        tin = metrics.prompt_tokens if metrics else 0
        tout = metrics.completion_tokens if metrics else 0
        llm = metrics.llm_verdicts if metrics else 0
        keyword = metrics.keyword_verdicts if metrics else 0
        lines.append(self.strings("item.grader_run", tin=tin, tout=tout))
        lines.append(self.strings("item.grader_run_verdicts", llm=llm, keyword=keyword))
        avg = metrics.avg_latency_ms if metrics else None
        if avg is not None:
            lines.append(self.strings("item.grader_avg", ms=avg))
        spark = metrics.latency_sparkline if metrics else None
        if spark is not None:
            lines.append(self.strings("item.grader_latency", spark=spark))
        return self._condensed(lines, kv=True)

    def _ambient_metrics_lines(self, model: str, host: str, metrics) -> list[TextBlock]:
        """The ambient toast model's own headed `Model`/`Status`/`This run`/`Avg latency`/
        `Latency` column (DELVE-0066/DELVE-0087): the same shape `_grader_metrics_lines` renders,
        but `This run` reports a single call count (`ambient_calls`) rather than an LLM/keyword
        verdict split, since an ambient passage is never graded. Always renders, even with
        `model`/`host` blank (no grader configured) and every count at zero, so the section's
        presence never depends on whether a room with a toast has been entered yet this run."""
        lines = [
            self.strings("item.grader_section_ambient"),
            self.strings("item.ambient_model", model=model),
            self.strings("item.ambient_model_host", host=host),
        ]
        if metrics.last_latency_ms is None:
            lines.append(self.strings("item.ambient_status_none"))
        else:
            key = "item.ambient_status_warm" if metrics.last_warm else "item.ambient_status_cold"
            lines.append(self.strings(key, ms=metrics.last_latency_ms))
        lines.append(self.strings(
            "item.ambient_run", tin=metrics.prompt_tokens, tout=metrics.completion_tokens))
        lines.append(self.strings("item.ambient_run_calls", calls=metrics.ambient_calls))
        avg = metrics.avg_latency_ms
        if avg is not None:
            lines.append(self.strings("item.ambient_avg", ms=avg))
        spark = metrics.latency_sparkline
        if spark is not None:
            lines.append(self.strings("item.ambient_latency", spark=spark))
        return self._condensed(lines, kv=True)

    def _status_body(self) -> list[TextBlock]:
        """The Status tab's body (DELVE-0044, INFOSCREEN.md §9): plain key/value rows of app and
        run diagnostics that already exist elsewhere, no new plumbing. Version, pack, locale, and
        terminal size only; the Grader/Ambient model rows that used to sit here (DELVE-0066) moved
        out at DELVE-0097, since the Grader tab already shows both models' full detail.

        Every row, including the terminal-size one, condenses into a single `kind="kv"` block via
        `_condensed(kv=True)` (DELVE-0059/DELVE-0078): a playtesting fix closed the tab's last
        remaining gap, and each row reads `Label: value` so `ui` can colour the label. The
        size row's live "RxC" value is still filled in at paint time by `ui`
        (`windows._fill_status_size`), since `session` has never read `stdscr` (rule 2); it used
        to be a structurally separate `kind="size"` block swapped wholesale, the only way to
        substitute it without touching the rest. `ui` now splices the live value into just the
        *last line* of this tab's sole body block instead: a private position-based contract
        between the two functions (this method always appends the size row last, and always
        returns exactly one block, since `lines` is never empty), not a block-level `kind` match
        any more. The size row's own text still carries only its localised `"Terminal:"` label
        here, colon included, so the spliced value lands after it like every other row."""
        lines = [
            self.strings("item.status_version", version=delve.__version__),
            self.strings("item.status_pack", pack=self.pack.title if self.pack else ""),
            self.strings("item.status_locale", locale=self.strings.lang),
            self.strings("item.status_size"),
        ]
        return self._condensed(lines, kv=True)

    def _info_overlay(self) -> InfoView:
        """The `i` panel: a tab strip, Scoring's own sub-tab strip, and the active (tab, sub-tab)
        body (DELVE-0035/DELVE-0040/DELVE-0042/DELVE-0043/DELVE-0044/DELVE-0054/DELVE-0055/
        DELVE-0056, plus Messages folding in the `p` key's former standalone panel, plus the
        Trophies tab at DELVE-0085). All six primary tabs have real content; the `else` branch is
        now unreachable (kept as the safe fallback for `_INFO_TABS`, same as before adding a
        sixth key). Dispatch is keyed by `(active primary key, active sub key)` rather than a
        growing string if/elif chain, per DELVE-0055's own maintainer story, so a later tab's
        sub-tab keys can't collide with Scoring's. `sub_focus` only ever carries through when
        `subtabs` is non-empty, so a row-focus toggle set while Scoring was active can't leak a
        stale True onto another tab."""
        tabs = [InfoTab(key=key, label=self.strings(label_key)) for key, label_key in _INFO_TABS]
        active_key = _INFO_TABS[self._info_tab][0]
        subtabs: list[InfoTab] = []
        active_sub = 0
        pack_rows: list[str] = []
        pack_selected = -1
        grader_left: list[TextBlock] = []
        grader_right: list[TextBlock] = []
        if active_key == "pack":
            # The two-column layout (DELVE-0075, replacing DELVE-0069's list/detail toggle): an
            # empty pack keeps the old single-message body; a non-empty one always carries both
            # `pack_rows` (the list) and `body` (the focused row's own detail, `_pack_detail_body`)
            # together, so `ui` can draw list and description side by side with no confirm step.
            entries = self._pack_entries()
            if not entries:
                body = [TextBlock("para", self.strings("item.inv_empty"))]
            else:
                idx = min(self._pack_row, len(entries) - 1)
                body = self._pack_detail_body(idx)
                pack_rows = [label for label, _ in entries]
                pack_selected = idx
        elif active_key == "scoring":
            subtabs = [InfoTab(key=key, label=self.strings(label_key))
                      for key, label_key in _SCORING_SUBTABS]
            active_sub = self._info_subtab % len(_SCORING_SUBTABS)
            sub_key = _SCORING_SUBTABS[active_sub][0]
            body = self._scoring_rooms_body() if sub_key == "rooms" else self._scoring_now_body()
        elif active_key == "grader":
            # Two-column layout when a model is configured (DELVE-0087); the offline single line
            # stays on `body` alone so it is never squeezed into a half column.
            cols = self._grader_columns()
            if cols is None:
                body = self._grader_body()
            else:
                grader_left, grader_right = cols
                body = []
        elif active_key == "status":
            body = self._status_body()
        elif active_key == "messages":
            body = self._messages_body()
        elif active_key == "trophies":
            body = self._trophies_body()
        else:
            body = [TextBlock("para", self.strings("item.tab_soon"))]
        sub_focus = self._info_sub_focus and bool(subtabs)
        return InfoView(tabs=tabs, active=self._info_tab, body=body,
                        subtabs=subtabs, active_sub=active_sub, sub_focus=sub_focus,
                        pack_rows=pack_rows, pack_selected=pack_selected,
                        grader_left=grader_left, grader_right=grader_right,
                        title=self.strings("item.info_title"),
                        more_label=self.strings("ui.more"), end_label=self.strings("ui.end"),
                        page_fmt=self.strings("ui.page_fmt"))

    def _backstory_client(self):
        """The same `OllamaClient` the free-text grader is already configured with (duck-typed
        like `_grader_info`), or `None` on the default keyword-only floor. The ambient toast then
        asks that same client for a *different* model per call (`_BACKSTORY_MODEL`, via
        `OllamaClient.chat`'s own `model` override, `RoomBackstoryRunner`), rather than building a
        second client, so a run with no model configured stays exactly as silent as before, never
        required to play (DELVE-0033's opposite), and a test double swapped in for the grader
        still works unchanged here too."""
        return getattr(getattr(self._grader_runner, "grader", None), "client", None)

    def _ambient_info(self) -> tuple[str, str] | None:
        """The ambient toast's own model/host (DELVE-0066), the same shape `_grader_info` returns:
        `_BACKSTORY_MODEL` (the fixed override `RoomBackstoryRunner` asks the shared client for)
        paired with that client's host, or `None` on the same default keyword-only floor
        `_grader_info`/`_backstory_client` already treat as absent, since the ambient toast reuses
        the grader's own client and never runs without one."""
        client = self._backstory_client()
        return (_BACKSTORY_MODEL, client.host) if client is not None else None

    def _next_gate(self) -> Gate | None:
        """The current chapter's next unpassed gate, in room order: the learner's next objective,
        shown on the Objectives tab. `None` once every gate in the chapter is passed."""
        return next((g for g in self.gates.values() if not g.passed), None)

    def _help_context(self) -> str:
        """Which row of the command catalogue (`session/help.py`) applies right now: the current
        `_overlay_kind`, `'walking'` when nothing is open, or, uniquely, `_overlay_kind` split by
        question kind (the real key differs between an assertion, an MCQ and free text, the same
        distinction `_hint()` already makes for the one-line hint)."""
        if self._overlay_kind == "question" and self.active is not None:
            return f"question_{self.active.current_question().kind}"
        return self._overlay_kind or "walking"

    def _condensed(self, lines: list[str], kv: bool = False) -> list[TextBlock]:
        """Fold a dense list of one-line facts into a single `TextBlock`, each line joined by a
        literal `"\\n"` in its `spans` (DELVE-0059, generalised past its original Keys tab):
        `ui/windows.py`'s pager inserts a blank row between distinct top-level blocks (right for
        prose, a lesson's paragraphs), which for a list of short one-liners roughly doubles the row
        count for no reason. One block sidesteps that rule entirely, so entries pack tight with no
        wasted rows, while each still word-wraps on its own if it runs long (`_wrap_spans` treats
        each `"\\n"`-separated segment independently, so pagination still only ever breaks between
        whole entries, never mid-one). An empty `lines` returns `[]`; the caller supplies its own
        fallback line for that case, since the wording differs per tab.

        `kv` (DELVE-0078) tags the block `kind="kv"` instead of `"plain"` when every line is
        genuinely a `"Label: value"` pair (Keys, Objectives, Grader, Status); `ui` then colon-splits
        each line and colours the label. Left False for a block like Scoring > Rooms's glyph
        legend, which has no label/value shape."""
        if not lines:
            return []
        spans = tuple((("\n" if i else "") + line, False) for i, line in enumerate(lines))
        return [TextBlock("kv" if kv else "plain", "\n".join(lines), spans=spans)]

    def _keys_body(self) -> list[TextBlock]:
        """The Keys tab: every catalogue row active in the current help context, each a plain key
        plus its localised explanation. Never empty in practice (every reachable context has at
        least `?` and, everywhere but walking, Esc); the fallback line only guards a context the
        catalogue doesn't know, so a gap shows as a message rather than a blank panel. Condensed
        into one block via `_condensed` (DELVE-0059)."""
        entries = help_catalogue.entries_for(self._help_context())
        if not entries:
            return [TextBlock("plain", self.strings("help.no_keys"))]
        return self._condensed([f"{e.key}: {self.strings(e.string_id)}" for e in entries], kv=True)

    def _objectives_facts(self) -> list[TextBlock]:
        """The Objectives tab's static half (DELVE-0028): pack title, chapter position and title,
        rooms done/total (matching `StatusView`'s own figures), and the next unpassed gate's
        keeper and pass requirement, if any is left this chapter. Assembled entirely from data the
        session already holds; no new pack frontmatter (this issue's non-goals). Condensed into
        one block via `_condensed` (DELVE-0059)."""
        lines = [
            self.strings("help.obj_pack", pack=self.pack.title if self.pack else ""),
            self.strings("help.obj_chapter", dlvl=self.chapter.dlvl,
                        total=len(self.chapters), title=self.cur.title),
            self.strings("help.obj_progress", done=self.rooms_done,
                        total=len(self.chapter.rooms)),
        ]
        gate = self._next_gate()
        if gate is not None:
            lines.append(self.strings("help.obj_keeper", name=gate.keeper.name,
                                      pct=round(gate.content.pass_mark * 100)))
        return self._condensed(lines, kv=True)

    def _help_overlay(self) -> HelpView:
        """The `?` panel: a two-tab strip (Keys, Objectives) over whichever tab is active,
        mirroring `_info_overlay`'s own shape (DELVE-0028). Objectives shows only the static facts
        (DELVE-0060 moved the optional LLM passage off this tab and onto a room-entry toast, since
        it routinely landed on page 2 here, behind a `--More--` a learner had no reason to
        press)."""
        tabs = [InfoTab(key=key, label=self.strings(label_key)) for key, label_key in _HELP_TABS]
        active_key = _HELP_TABS[self._help_tab][0]
        body = self._keys_body() if active_key == "keys" else self._objectives_facts()
        return HelpView(tabs=tabs, active=self._help_tab, body=body,
                        title=self.strings("help.title"),
                        more_label=self.strings("ui.more"), end_label=self.strings("ui.end"),
                        page_fmt=self.strings("ui.page_fmt"))

    def _messages_body(self) -> list[TextBlock]:
        """The Messages tab's body (folded into the Info panel, a playtesting request): recent
        non-blank lines, newest first in a numbered list, each distinct line only once (a repeat
        is not listed twice). Capped so the panel stays bounded. Condensed into one block via
        `_condensed` (DELVE-0059), the same trick the Keys tab uses for a dense list of
        one-liners, so a long log doesn't burn a blank row after every entry."""
        seen: set[str] = set()
        recent: list[str] = []
        for m in reversed(self.messages):                 # newest first, each line only once
            if m and m not in seen:
                seen.add(m)
                recent.append(m)
                if len(recent) >= _HISTORY_MAX:
                    break
        return (self._condensed([f"{i}. {m}" for i, m in enumerate(recent, 1)])
                or [TextBlock("para", self.strings("ui.no_messages"))])

    def _trophies_body(self) -> list[TextBlock]:
        """The Trophies tab's body (DELVE-0085): a Date/Pack/Score table from the
        `(score, title, date)` rows threaded in at start/resume (`self._trophy_rows`), newest
        date first. Empty (no completions yet) is a single explanatory line rather than a blank
        panel, since the pre-run screen itself skips entirely when the case is empty and the tab
        still needs something to show."""
        if not self._trophy_rows:
            return [TextBlock("para", self.strings("item.trophies_empty"))]
        header = (
            ((self.strings("item.trophies_col_date"), False),),
            ((self.strings("item.trophies_col_pack"), False),),
            ((self.strings("item.trophies_col_score"), False),),
        )
        data = tuple(
            (((when, False),), ((title, False),), ((score, False),))
            for score, title, when in self._trophy_rows
        )
        text = "\n".join(f"{when}  {title}  {score}" for score, title, when in self._trophy_rows)
        return [TextBlock("table", text, table=(header,) + data)]

    def _text(self, title: str, body) -> TextView:
        """A TextView carrying the localised pager chrome, so every paginated panel (lesson,
        explanation, inventory, log, scroll) shows '(einde)' not '(end)' in Dutch (rule 2: `ui`
        fills the '{page}/{total}' template, it never spells the words)."""
        return TextView(title=title, body=body,
                        more_label=self.strings("ui.more"),
                        end_label=self.strings("ui.end"),
                        page_fmt=self.strings("ui.page_fmt"))

    def _pickup_menu_overlay(self) -> MenuView:
        items = [MenuItem(str(i + 1), label) for i, (_, label, _, _) in enumerate(self._pickables)]
        return MenuView(prompt=self.strings("item.pickup_prompt"), items=items)

    def _amount_overlay(self, action: str) -> AmountView:
        """The boxed how-many field, shared by drop and pickup; only the prompt differs."""
        maximum = self._pending[2] if self._pending else 0
        prompt = self.strings("item.amount_prompt" if action == "drop" else "item.pickup_amount")
        return AmountView(prompt=prompt, typed=self._amount_buf,
                          maximum=maximum, footer=self.strings("item.amount_range", max=maximum))

    def _claim_scroll(self) -> None:
        """Step onto the pedestal in the final chamber: lift the scroll, and the run is won. Not a
        popup but an object you hold (PLAN.md section 10); the overlay is the scroll's own text."""
        self._scroll_claimed = True
        self.finished = True
        self.active = None
        self._overlay = self._scroll_overlay()
        self._overlay_kind = "scroll"
        self.messages.append(self.strings("msg.scroll_taken"))
        if self.recorder is not None:
            self.recorder.finished(self, self.pack_score())
        self._save()

    def _fail_sitting(self, gate: Gate, result) -> None:
        """A sitting that missed `pass`: charge its HP once, then push back or, if the loss has
        finally emptied the bar, respawn at the entrance with every earned door intact."""
        keeper = gate.keeper
        if result.penalty:
            self.player.hp = max(0, self.player.hp - result.penalty)
        if self.player.hp <= 0:
            self._respawn()
        elif result.outcome == "repelled":
            self._repelled(keeper)
        else:
            self._close(self.strings("msg.fail", first=_keeper_ref(keeper.name)))

    def _repelled(self, keeper) -> None:
        """Attempts are spent: pushed back from the door, but nothing earned is lost (CLAUDE.md
        rule 4). The keeper's own panel says so; the door is stone again and re-sittable."""
        self.active = None
        self._overlay = self._repelled_overlay(keeper)
        self._overlay_kind = "repelled"
        self.messages.append(self.strings("msg.repelled", name=keeper.name))

    def _respawn(self) -> None:
        """HP reached zero from accumulated loss across the floor. Not death: wake at the chapter
        entrance, whole again, with every door already earned still open (PLAN.md section 6)."""
        self.player.hp = self.player.max_hp
        self.player.pos = self.chapter.start
        if self.pet is not None:
            self.pet.pos = self._pet_spot()
        self.active = None
        self._overlay = None
        self._overlay_kind = None
        self.messages.append(self.strings("msg.respawn"))
        self._observe()
        self._save()

    def _close(self, message: str) -> None:
        self.active = None
        self._overlay = None
        self._overlay_kind = None
        if message:
            self.messages.append(message)

    # -- persistence hooks (no-ops without a recorder) ----------------------------------

    def _record_pass(self, gate: Gate) -> None:
        # The tutorial floor is never scored (PLAN.md section 9): its passes write no room_result.
        if self.recorder is not None and self.cur.scored:
            self.recorder.room_passed(self.cur.content_chapter_id, gate)

    def _save(self) -> None:
        if self.recorder is not None:
            self.recorder.save(self)

    def checkpoint(self) -> None:
        """Persist the learner's exact position now, over and above the transition snapshots. The
        UI calls this on quit so resuming lands where the learner actually stopped, not at the
        last gate or chapter change (PLAN.md section 10)."""
        self._save()

    def _pass_message(self, gate: Gate, already_open: bool = False) -> str:
        if gate.unlock_kind is TileKind.STAIRS_DOWN:
            # On the tutorial floor the stairs are painted open from the start, so passing the last
            # keeper reveals nothing new; say so instead of claiming a wall opened onto them.
            return self.strings("pass.stairs_open" if already_open else "pass.stairs")
        if gate.unlock_kind is TileKind.PEDESTAL:
            return self.strings("pass.pedestal")
        return self.strings("pass.door")

    # -- world bookkeeping --------------------------------------------------------------

    def _tick_torch(self) -> None:
        """Burn one step off the current torch (DELVE-0062), called once per successful move. A
        burned-out torch leaves nothing behind (no spent-husk item); a spare already in the pack
        relights automatically, in the same message as the burnout, or the learner is left dark."""
        if not self.cur.scored or self.player.torch_charge <= 0:
            return
        self.player.torch_charge -= 1
        if self.player.torch_charge > 0:
            return
        spare, self.player.inventory = taken(self.player.inventory, TORCH.id, 1)
        if spare is not None and spare.count > 0:
            self.player.torch_charge = TORCH_DURATION_STEPS
            self.messages.append(self.strings("msg.torch_burnout_relit"))
        else:
            self.messages.append(self.strings("msg.torch_burnout_dark"))

    def _lit_tiles(self) -> set[Point]:
        """The current frame's lit set: the player's own light (DELVE-0062), plus, while
        torchless, every *visited* keeper's own candle halo (DELVE-0065, narrowed by
        DELVE-0086). A lit room already reveals everything a halo would add, so the halo is
        only computed when torchless. Never-visited rooms stay dark even torchless; a room
        visited once keeps its keeper halo from anywhere on the floor."""
        lit = vision.lit_tiles(self.chapter, self.player.pos, lit=self.has_light)
        if not self.has_light:
            visited = self.cur.visited_rooms
            keepers = (
                g.keeper.pos for g in self.gates.values()
                if (room := vision.room_at(self.chapter, g.keeper.pos)) is not None
                and room.id in visited
            )
            lit |= vision.keeper_halo(self.chapter, keepers)
        return lit

    def _observe(self) -> None:
        # Only a working torch's light is ever remembered (DELVE-0062): a torchless tile leaves
        # nothing in `discovered`, so it goes dark again next frame the moment it is recomputed
        # fresh and no longer in the immediate radius; `_cell` needs no change for this to hold.
        # A torchless keeper halo (DELVE-0065) is included in `lit_now` for the same reason but,
        # like the rest of the torchless reveal, is never folded into `discovered` here.
        lit_now = self._lit_tiles()
        if self.has_light:
            self.cur.discovered |= lit_now
        self._maybe_enter_room()

    def _maybe_enter_room(self) -> None:
        """Queue a room's one ambient toast the moment the learner first stands inside it this run
        (DELVE-0060): every place `_observe` already runs (chapter arrival, a step, descend/ascend,
        respawn) is exactly every place worth checking, so this needs no call site of its own.
        Gated or not (this issue's own "any room" story); a room without a keeper still gets one,
        just with no keeper clause in its prompt (`_room_prompt`)."""
        room = next((r for r in self.chapter.rooms if r.contains(self.player.pos)), None)
        if room is None or room.id in self.cur.visited_rooms:
            return
        self.cur.visited_rooms.add(room.id)
        gate = next((g for g in self.gates.values() if room.contains(g.keeper.pos)), None)
        title = gate.keeper.name if gate is not None else self.cur.title
        # The chapter index rides along too (not just the title): a call can resolve turns after
        # it was queued, by which point the learner may have already descended to a different
        # floor entirely, and a toast for a keeper/room on a floor already left behind reads as an
        # outright mismatch (a play-testing note), not just mildly late the way a still-lingering
        # toast for an earlier room on the *same* floor does. `_poll_toast` drops it silently then.
        self._room_backstory.submit(room.id, (title, self.idx), self._room_prompt(gate, room))

    def _item_bullet(self, defn, count: int) -> str:
        """One item's ambient-prompt bullet (DELVE-0064): its natural phrase (`_item_phrase`, "a
        coconut half", "70 coins") plus, when the kind has one, its own authored description (the
        item file's body, `ItemDef.look`), so the model gets real material to draw on instead of a
        bare noun phrase. Money and the torch carry no `look`, so they bullet with the phrase
        alone. `look` is a pack author's own prose and, unlike issues/docs/CHANGELOG, is not bound
        by CLAUDE.md's single-line rule; an authored body may still be hard-wrapped across several
        source lines (`urgent-memo.md`'s is), so its whitespace is collapsed here to keep one
        bullet on one flowing line rather than splicing a raw mid-sentence newline into the
        prompt."""
        phrase = self._item_phrase(defn, count)
        look = " ".join(defn.look.split())
        return f"- **{phrase}**: {look}" if look else f"- **{phrase}**"

    def _backpack_description(self) -> str:
        """The learner's backpack as one bullet per kind (a play-feedback request: "include the
        objects in the backpack, to give more context" to the ambient passage), blank for an empty
        one. Reuses `_item_phrase`/`_coins`, the same natural noun phrases the pickup/drop messages
        already use, via `_item_bullet`."""
        bullets = []
        if self.player.gold > 0:
            bullets.append(f"- **{self._coins(self.player.gold)}**")
        bullets.extend(self._item_bullet(s.defn, s.count) for s in self.player.inventory)
        return "\n".join(bullets)

    def _room_items_description(self, room) -> str:
        """What is really on this room's floor right now, one bullet per kind (a play-feedback
        request: mandatory context, not the random `OBJECTS` focus DELVE-0060 used to gate this
        behind, which just invited the model to invent generic clutter). Blank if the floor is
        bare; `backstory.build_prompt` then states that truthfully rather than leaving the model
        to guess."""
        bullets = [self._item_bullet(stack.defn, stack.count)
                  for pos, pile in self.items.items() if room.contains(pos)
                  for stack in pile]
        return "\n".join(bullets)

    def _pet_description(self) -> str:
        """The learner's companion, species and name, for the ambient prompt's context; blank for
        a soloist (`pet_species="none"`). Locale-aware (`pet.noun_cat`/`pet.noun_dog`,
        `pet.phrase`): this used to hardcode English ("named") regardless of locale, so a Dutch
        run's prompt said "hond named Rex" instead of "hond genaamd Rex", the one fact fed into
        the otherwise fully-localized ambient prompt that wasn't actually localized."""
        if self.pet is None:
            return ""
        noun = self.strings(f"pet.noun_{self.pet.species}")
        return self.strings("pet.phrase", species=noun, name=self.pet.name)

    def _room_prompt(self, gate: Gate | None, room) -> str:
        """The prompt for one room's ambient passage: every fact available, always included,
        rather than one randomly chosen focus (a play-feedback request for comprehensive context).
        The room's own keeper and lesson topic if it has one (`Gate.lesson.title`), the real
        objects on its floor (mandatory, `_room_items_description`), the learner's own backpack
        and companion, all on top of the shared dungeon setting. An ungated room omits the
        keeper/lesson clauses entirely rather than naming an empty keeper."""
        return backstory.build_prompt(
            pack=self.pack.title if self.pack else "", dlvl=self.chapter.dlvl,
            chapter_title=self.cur.title,
            keeper=gate.keeper.name if gate is not None else "",
            requirement=(f"{round(gate.content.pass_mark * 100)}%" if gate is not None else ""),
            lesson_topic=gate.lesson.title if gate is not None else "",
            room_objects=self._room_items_description(room),
            carrying=self._backpack_description(),
            pet=self._pet_description(),
            has_light=self.has_light,
            language="Dutch" if self.strings.lang == "nl" else "English")

    def _poll_toast(self) -> None:
        """Called once per built `Frame` (DELVE-0060): ages out a toast that has been up too long,
        arms/fires the idle nudge (DELVE-0061), then checks whether a room's background call has
        resolved, replacing whatever was showing (a fresher room's passage always wins over an
        older, still-lingering one). `(title, idx)` rode along in the queue rather than being
        re-derived now, since a call can resolve turns after it was queued, by which point the
        learner may already be elsewhere. A different room on the *same* floor is shown anyway
        (still merely late, not wrong); a different *chapter* (the learner has since taken the
        stairs) is dropped silently instead of shown, since a passage for a keeper or floor already
        left behind reads as a mismatch, not just lateness; the nudge applies that same drop rule
        plus its own (never shown once the learner has actually moved, `self.turn != 0`).

        Once any overlay is open (a lesson, an examination, the backpack, ...), the ambient moment
        has passed: `_toast` is cleared outright here, not merely left undrawn the way `ui/render.
        py` already hides it while a panel is up, so it can never resurface once that panel closes
        (a play-testing report: a keeper's lesson finished and the same toast was still there, or
        came straight back). Nudge/backstory polling is simply deferred, not lost, while an overlay
        is open: a call already in flight keeps running on its own thread regardless, and is picked
        up the next time `_poll_toast` runs with no overlay open, whenever that is."""
        if self._overlay_kind is not None:
            self._toast = None
            return
        if self._toast is not None:
            # DELVE-0070: frozen until the learner has taken at least one turn since the toast
            # appeared (so idly reading it never ages it out), then `_TOAST_TTL` more turns from
            # that first move, not from the toast's own creation turn.
            if self._toast_ttl_start is None:
                if self.turn != self._toast_turn:
                    self._toast_ttl_start = self.turn
            elif self.turn - self._toast_ttl_start >= _TOAST_TTL:
                self._toast = None
        self._poll_nudge_timer()
        ready = self._room_backstory.poll()
        if ready is None:
            return
        room_id, (title, chapter_idx), text = ready
        is_nudge = room_id == self._nudge_room_id
        if is_nudge:
            self._nudge_state = "fired"     # a one-shot: resolved means done, shown or not
        if chapter_idx != self.idx:
            return
        if is_nudge and self.turn != 0:
            return
        if is_nudge:
            text = self._ensure_arrow_keys_mentioned(text)
        # DELVE-0070: the prompt only *asks* for a short passage; nothing enforces that on the
        # reply, so a firm cap is applied here, before the text ever reaches `draw_toast`, rather
        # than relying on that function's own line-count truncation to silently hide an overrun.
        text = _cap_toast_text(text)
        # `**bold**` is the one markdown mark this prompt invites (backstory.PROMPT), parsed the
        # same way a pack author's own `**bold**` is (`content.markup.inline_spans`) so `ui/
        # windows.py:draw_toast` can render it, rather than showing the literal asterisks a model
        # occasionally reaches for (confirmed in the qwen3.5:9b comparison run).
        spans = inline_spans(text)
        self._toast = ToastView(title=title, body=[TextBlock("para", text, spans=spans)])
        self._toast_turn = self.turn
        self._toast_ttl_start = None
        if (not is_nudge and self._nudge_state == "unarmed" and self.turn == 0
                and self._room_backstory.client is not None):
            self._nudge_state = "waiting"
            self._nudge_deadline = time.monotonic() + _NUDGE_DELAY_SECONDS

    def _ensure_arrow_keys_mentioned(self, text: str) -> str:
        """The nudge's one deterministic guarantee (a play-testing report: a generated line said
        only "urging you to explore further", with no key named at all, useless to someone who
        genuinely does not know what to press). `NUDGE_PROMPT` already asks the model to name the
        arrow keys explicitly, but an instruction is not a guarantee; if the reply doesn't mention
        them (checked in whichever locale it was asked to reply in), a short, plain, localised
        sentence is appended so the one thing this feature exists to say is never left to chance."""
        keywords = _ARROW_KEYWORDS.get(self.strings.lang, _ARROW_KEYWORDS["en"])
        if any(k in text.lower() for k in keywords):
            return text
        return f"{text} {self.strings('help.nudge_fallback')}"

    def _poll_nudge_timer(self) -> None:
        """Armed only once, by `_poll_toast` above, the moment the very first room's own toast is
        shown while the learner is still on turn 0. Cancelled the instant a move happens before the
        deadline; otherwise, once `_NUDGE_DELAY_SECONDS` real seconds pass with the learner still on
        turn 0, queues a second call in the same room's keeper voice (or the chapter title,
        ungated) suggesting the arrow keys, keyed distinctly (`f"{room_id}::nudge"`) so it can never
        collide with that room's own already-delivered toast in `RoomBackstoryRunner`'s queue."""
        if self._nudge_state != "waiting":
            return
        if self.turn != 0:
            self._nudge_state = "cancelled"
            return
        if time.monotonic() < self._nudge_deadline:
            return
        room = next((r for r in self.chapter.rooms if r.contains(self.player.pos)), None)
        gate = (next((g for g in self.gates.values() if room.contains(g.keeper.pos)), None)
               if room is not None else None)
        title = gate.keeper.name if gate is not None else self.cur.title
        room_id = f"{room.id}::nudge" if room is not None else "nudge"
        prompt = backstory.build_nudge_prompt(
            pack=self.pack.title if self.pack else "", dlvl=self.chapter.dlvl,
            chapter_title=self.cur.title,
            keeper=gate.keeper.name if gate is not None else "",
            language="Dutch" if self.strings.lang == "nl" else "English")
        self._nudge_room_id = room_id
        self._nudge_state = "queued"
        self._room_backstory.submit(room_id, (title, self.idx), prompt)

    def _pet_step(self) -> None:
        """The companion takes its own step, once per player turn (PETS.md section 3), and the
        session narrates the event. A dog fetches any floor item now (DELVE-0016) and *sets it
        down beside you* rather than handing it over: the engine drops the stack on the floor, so
        the session only narrates and never banks gold itself (rule 1). Coins the dog drops
        auto-collect when you step over them (`_collect_money`); an object waits for `,`."""
        if self.pet is None:
            return
        ev = petmod.step(self.chapter.grid, self.items, self.player.pos, self.pet,
                         set(self.keepers), self.pet_rng, rooms=self.chapter.rooms)
        if ev.kind == "grabbed":
            self.messages.append(self.strings("item.pet_grab", name=self.pet.name,
                                              coins=self._coins(ev.coins)))
        elif ev.kind == "grabbed_item":
            self.messages.append(self.strings("item.pet_grab_item", name=self.pet.name,
                                              what=self._item_phrase(ev.item.defn, ev.item.count)))
        elif ev.kind == "gave":
            self.messages.append(self.strings("item.pet_give", name=self.pet.name,
                                              coins=self._coins(ev.coins)))
        elif ev.kind == "gave_item":
            self.messages.append(self.strings("item.pet_give_item", name=self.pet.name,
                                              what=self._item_phrase(ev.item.defn, ev.item.count)))

    def _retrieve(self) -> None:
        """Take what the pet carries when you bump it: a fleeing cat is cornered, a dog just hands
        it over; an empty-pawed pet is only ruffled. The player stays put (PETS.md section 5).
        Bumping is a deliberate catch, so coins bank straight away here; a dog's fetched object
        (DELVE-0016) can't bank, so it is set on the pet's tile beside you to pick up with `,`."""
        if self.pet.carried:
            coins, self.pet.carried = self.pet.carried, 0
            self.pet.cooldown = petmod.FETCH_COOLDOWN   # caught: it slinks off, ignores money
            self.player.gold += coins
            key = "msg.retrieve_cat" if self.pet.species == "cat" else "msg.retrieve_dog"
            self.messages.append(self.strings(key, name=self.pet.name, coins=self._coins(coins)))
        elif self.pet.carried_item is not None:
            stack, self.pet.carried_item = self.pet.carried_item, None
            self.pet.cooldown = petmod.FETCH_COOLDOWN
            self._set_pile(self.pet.pos, merged(self.items.get(self.pet.pos, []), stack))
            self.messages.append(self.strings("msg.retrieve_dog_item", name=self.pet.name,
                                              what=self._item_phrase(stack.defn, stack.count)))
        else:
            self.messages.append(self.strings("msg.pet_pat", name=self.pet.name))

    def _pet_spot(self) -> Point:
        """A walkable tile beside the player for the pet to sit on at the start, and to return to
        on a chapter change or respawn. Falls back to the player's own tile if somehow boxed in."""
        for d in Direction:
            n = Point(self.player.pos.x + d.delta.x, self.player.pos.y + d.delta.y)
            if self.chapter.grid.walkable(n.x, n.y) and n not in self.keepers:
                return n
        return self.player.pos

    def _adjacent_gate(self) -> Gate | None:
        p = self.player.pos
        for pos, gate in self.keepers.items():
            if max(abs(pos.x - p.x), abs(pos.y - p.y)) == 1:
                return gate
        return None

    def _maybe_greet(self) -> None:
        gate = self._adjacent_gate()
        if gate and not gate.passed and gate.content.id not in self._greeted:
            self._greeted.add(gate.content.id)
            self.messages.append(self.strings("msg.greet", name=gate.keeper.name))

    @property
    def rooms_done(self) -> int:
        return sum(1 for g in self.gates.values() if g.passed)

    def pack_score(self) -> float:
        """The overall score carried onto the scroll: the mean of every room's passing score
        across the whole pack. Reaching the pedestal means every room was passed, so this is
        always defined; an assisted question lowers the room score it sits in (PLAN section 5).
        The tutorial floor is unscored and never counts (PLAN.md section 9)."""
        scores = [g.passed_score for cr in self.chapters if cr.scored
                  for g in cr.gates.values() if g.passed]
        return sum(scores) / len(scores) if scores else 0.0

    # -- overlay builders ---------------------------------------------------------------

    def _lesson_overlay(self, gate: Gate) -> TextView:
        body = [TextBlock(b.kind, b.text, spans=b.spans, table=b.table)
                for b in gate.lesson.blocks]
        return self._text(title=gate.lesson.title, body=body)

    def _question_overlay(self, gate: Gate):
        q = gate.current_question()
        options = gate.display_options()
        idx, total = gate.progress()
        footer = self.strings("question.counter", idx=idx, total=total)
        # Garnish the *displayed* prompt only; grading reads the options/answer, never this string,
        # so an added emoji cannot change what is correct (session/flavour.py).
        prompt = flavour.augment(q.prompt, self.strings.flavour_emoji())
        struck = gate.struck
        elim = gate.eliminated
        if q.kind == "freetext":
            return FreeTextView(prompt=prompt, typed=self._answer_buf, footer=footer)
        if q.kind == "assertion":
            marks = tuple(i == struck for i in range(len(options)))
            gone = tuple(i in elim for i in range(len(options)))
            return PromptView(text=prompt, choices=options, footer=footer, struck=marks,
                              eliminated=gone, connector=self.strings("question.or"),
                              selected=self._selected_option)
        items = [MenuItem(str(i + 1), text, struck=(i == struck), eliminated=(i in elim))
                 for i, text in enumerate(options)]
        return MenuView(prompt=prompt, items=items, footer=footer,
                        selected=self._selected_option)

    def _grading_overlay(self, answer: str) -> GradingView:
        """The 'Checking your answer…' pause shown while a slow (LLM) grade runs on a worker; never
        seen on the instant keyword floor (PHASE2.md section 5.3)."""
        return GradingView(title=self.strings("grading.title"), answer=answer,
                           body=self.strings("grading.body"))

    def _explanation_overlay(self, header: str, explanation: str) -> TextView:
        body = [TextBlock("plain", header)]
        body += [TextBlock("para", p) for p in explanation.split("\n\n")]
        return self._text(title="", body=body)

    def _repelled_overlay(self, keeper) -> TextView:
        """The keeper's own panel, still, saying the same thing in fewer words: not yet, read it
        again, nothing is lost. The tone is the point: a pause, not a
        defeat. The keeper's pronoun is unknown to the engine, so the English keeps 'they' and the
        Dutch is phrased around a pronoun entirely (delve/strings/nl.toml)."""
        first = _keeper_ref(keeper.name)
        paras = self.strings("overlay.repelled_body", name=keeper.name, first=first)
        body = [TextBlock("para", p) for p in paras]
        return self._text(title=self.strings("overlay.repelled_title"), body=body)

    def _scroll_overlay(self) -> TextView:
        """The award, rendered from the pack's scroll.md with the four placeholders filled. The
        H1 in the source is the scroll's title, so it becomes the panel title rather than a block,
        and the `---` rule is dropped (the panel has no horizontal rule)."""
        if self.pack is None:
            return self._text(title=self.strings("overlay.scroll_fallback_title"),
                            body=[TextBlock("para", self.strings("overlay.scroll_fallback_body"))])
        filled = render_scroll(self.pack.scroll, name=self.player.name, score=self.pack_score(),
                               date=datetime.now(), pack=self.pack.title, fmt=self.strings.fmt)
        cleaned = "\n".join("" if ln.strip() == "---" else ln for ln in filled.split("\n"))
        title = self.pack.scroll_name
        body: list[TextBlock] = []
        for t in tokenize(cleaned):
            if t.kind == "heading":
                if t.level == 1:
                    title = title or t.text
                    continue
                body.append(TextBlock("plain", t.text))
            elif t.kind in ("para", "bullet", "quote"):
                body.append(TextBlock(t.kind, t.text, spans=t.spans))
            elif t.kind == "code":
                body.append(TextBlock("plain", t.text))
        return self._text(title=title, body=body)

    # -- view -----------------------------------------------------------------------------

    def frame(self) -> Frame:
        lit = self._lit_tiles()
        g = self.chapter.grid
        cells = [[self._cell(Point(x, y), lit) for x in range(g.width)] for y in range(g.height)]
        status = StatusView(
            name=self.player.name,
            dlvl=self.chapter.dlvl,
            rooms_done=self.rooms_done,
            rooms_total=len(self.chapter.rooms),
            gold=self.player.gold,
            hp=self.player.hp,
            max_hp=self.player.max_hp,
            turn=self.turn,
            rooms_label=self.strings("status.rooms"),
            gold_symbol=self.strings.fmt["currency"],
        )
        visible = self._visible_message()
        # The highlight follows the visible line: green/red only while Correct./Not quite. shows.
        message_bg = self._msg_styles.get(len(self.messages) - 1) if visible else None
        self._poll_toast()
        return Frame(
            map=MapView(g.width, g.height, cells),
            status=status,
            messages=visible,
            message_bg=message_bg,
            hint=self._hint(),
            overlay=self._overlay,
            toast=self._toast,
            toast_pending=(self._room_backstory.pending()
                          or self._nudge_state in ("waiting", "queued")),
            # DELVE-0082: only while a call is genuinely running (queued, in flight, or resolved
            # but not yet delivered) and there is no fresher toast or panel already showing; the
            # idle-nudge timer's own "waiting" (armed, not yet queued) state names nothing yet.
            # DELVE-0083: a fired nudge whose text is now guaranteed to be dropped on arrival
            # (`_poll_toast`'s own `is_nudge and self.turn != 0` rule, since the learner has since
            # moved, which is exactly what the nudge exists to prompt) must not keep naming itself
            # here too, unless something else is queued behind it that genuinely will show.
            toast_loading=(self.strings("toast.loading")
                          if self._overlay_kind is None and self._toast is None
                             and self._room_backstory.pending()
                             and not self._doomed_nudge_only()
                          else None),
        )

    def _doomed_nudge_only(self) -> bool:
        """Whether the sole thing keeping `_room_backstory.pending()` true is a fired idle nudge
        that will be dropped the instant it resolves (DELVE-0083): fired (`"queued"`, its one-shot
        name for "submitted") and the learner has since moved, mirroring `_poll_toast`'s own drop
        condition exactly, with nothing else queued behind it to still show for."""
        return (self._nudge_state == "queued" and self.turn != 0
               and not self._room_backstory.pending_other_than(self._nudge_room_id))

    def _visible_message(self) -> list[str]:
        """The top line, aged: a message shows on the turn it is posted and briefly after, then
        blanks, so a stale line is never mistaken for fresh news (a play-testing note). A keeper
        encounter freezes the clock (the line is the encounter's own text); every other overlay,
        the backpack included, lets it age out, so opening a panel never resurrects an old line."""
        if len(self.messages) > self._msg_len_seen:
            self._msg_len_seen = len(self.messages)
            self._msg_turn = self.turn
        if not self.messages:
            return []
        frozen = self._overlay_kind in _ENCOUNTER_OVERLAYS
        if not frozen and self.turn - self._msg_turn >= _MSG_TTL:
            return []
        return self.messages[-1:]

    def _cell(self, p: Point, lit: set[Point]) -> Cell:
        # Precedence: the learner, then the pet, then a keeper, then a floor object, then the tile
        # (OBJECTS.md). Anything but the learner shows only where the tile is lit or remembered.
        if p == self.player.pos:
            return Cell("@", Colour.WHITE, dim=False)
        seen = p in lit or p in self.discovered
        if not seen:
            return Cell(" ", Colour.BLACK, dim=False)
        dim = p not in lit
        if self.pet is not None and p == self.pet.pos:
            return Cell(petmod.glyph_for(self.pet.species), Colour.WHITE, dim=dim)
        if p in self.keepers:
            return Cell("@", Colour.BRIGHT_MAGENTA, dim=dim)
        pile = self.items.get(p)
        if pile:
            top = pile[-1].defn
            return Cell(top.glyph, Colour(top.colour), dim=dim)
        t = self.chapter.grid.at(p.x, p.y)
        return Cell(t.glyph, _colour_for(t.kind), dim=dim)

    def _hint(self) -> str:
        if self._overlay_kind == "lesson":
            return self.strings("hint.read")
        if self._overlay_kind == "explanation":
            return self.strings("hint.more")
        if self._overlay_kind == "repelled":
            return self.strings("hint.repelled")
        if self._overlay_kind == "grading":
            return self.strings("hint.grading")
        if self._overlay_kind == "scroll":
            return self.strings("hint.scroll")
        if self._overlay_kind == "question":
            kind = self.active.current_question().kind
            if kind == "freetext":
                return self.strings("hint.answer_text")
            options = self.active.display_options()
            if kind == "assertion":
                return self.strings("hint.answer_two", k1=options[0][0].lower(),
                                    k2=options[1][0].lower())
            price = self._removal_price(self.active)
            if price is not None:
                return self.strings("hint.answer_many_buy", last=len(options),
                                    price=format_money(price, self.strings.fmt))
            return self.strings("hint.answer_many", last=len(options))
        if self._overlay_kind == "info":
            if _INFO_TABS[self._info_tab][0] == "scoring":
                return self.strings("hint.inventory_sub")
            # DELVE-0081: `d` only ever does anything on the Pack tab, and only once there is a
            # row to drop, so it's only named here in that one case; every other tab (and an empty
            # Pack) keeps the plain hint with no key that would do nothing if pressed.
            if _INFO_TABS[self._info_tab][0] == "pack" and self._pack_entries():
                return self.strings("hint.inventory_pack")
            return self.strings("hint.inventory")
        if self._overlay_kind == "help":
            return self.strings("hint.help")
        if self._overlay_kind == "drop_amount":
            return self.strings("hint.drop_amount")
        # The tile underfoot comes first: a keeper often stands beside the stairs (the last one
        # always does, and the tutorial's are open from the start), and standing *on* a stair, the
        # way down or up is the action the player most needs named, ahead of the talk prompt.
        here = self.chapter.grid.at(*self.player.pos).kind
        if here is TileKind.STAIRS_DOWN:
            return self.strings("hint.descend")
        if here is TileKind.STAIRS_UP:
            return self.strings("hint.ascend")
        pile = self.items.get(self.player.pos)
        if pile and any(s.defn.carriable for s in pile):
            return self.strings("hint.pickup")
        gate = self._adjacent_gate()
        if gate is not None:
            return self.strings("hint.talk", first=_keeper_ref(gate.keeper.name))
        if self.player.hp < self.player.max_hp:
            return self.strings("hint.rest")
        # Once the learner is carrying anything (money after the first reward, or an object), name
        # the pack and drop keys so they are discoverable without the tutorial (play-testing note).
        if self.player.gold > 0 or self.player.inventory:
            return self.strings("hint.carrying")
        return self.strings("hint.walk")
