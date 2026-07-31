"""The content tiers, one dataclass each: a Room (one lesson + its examination), a Chapter (a
floor's worth of rooms), and a Pack (the whole training). This is the shape PLAN.md section 2
describes; the parser (parser.py) fills it from Markdown and the M2 slice hard-codes one Room, so
both must produce the same object. The shape is frozen at M3.

Nothing here knows about grids, doors, or curses: a Chapter is an ordered list of rooms, not a
map. `layout.py` turns a room count into a floor, and `gate.py` seals the doors. Keeping the
content chapter and the engine `Chapter` (the grid) as separate types in separate modules is the
whole content/engine split (CLAUDE.md rule 1).
"""

from dataclasses import dataclass, field

from delve.assess.question import Question
from delve.content.lesson import Lesson
from delve.engine.items import ItemDef


@dataclass(frozen=True)
class Room:
    id: str
    keeper_name: str
    keeper_kind: str
    lesson: Lesson
    questions: tuple[Question, ...]
    pass_mark: float
    # Per-room overrides of the pack difficulty; both are M4 stakes, parsed and frozen now so a
    # pack written today keeps working. None means 'inherit the pack default'.
    attempts: int | None = None
    penalty: int | None = None
    # Coins the keeper drops on a pass, on the newly opened way onward (OBJECTS.md 1.1.0). None
    # inherits the pack-level default; 0 pays nothing. A per-room override of `Pack.reward`.
    reward: int | None = None
    # Objects scattered on this room's floor at run start (OBJECTS.md 1.3.0): a `place: <id> xN`
    # frontmatter line becomes (def-id, count) pairs the session turns into engine stacks. Empty
    # unless the author placed something. `compare=False` so the M2 golden `Room` still matches.
    placements: tuple[tuple[str, int], ...] = field(default=(), compare=False)


@dataclass(frozen=True)
class Chapter:
    id: str
    title: str
    intro: str                       # shown on arrival at the floor
    rooms: tuple[Room, ...]
    slug: str = ""                   # the folder name; order comes from it, not from frontmatter


@dataclass(frozen=True)
class Pack:
    id: str
    title: str
    difficulty: str                  # 'relaxed' | 'standard' | 'strict'
    scroll_name: str
    intro: str                       # the dungeon's opening screen
    chapters: tuple[Chapter, ...]
    scroll: str                      # scroll.md body, with {name}/{score}/{date}/{pack} intact
    locale: str = "en"
    # Default coins a passed room pays; a room may override it (OBJECTS.md).
    reward: int = 0
    # The kinds this pack defines, one per `items/*.md` file (OBJECTS.md 1.3.0). Money is built in
    # and never appears here. The session registers these so a placed or carried stack round-trips.
    items: tuple[ItemDef, ...] = ()
