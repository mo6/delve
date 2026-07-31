"""The static dungeon: points, directions, tiles, rooms, a chapter.

Pure data with a little geometry. No mutation of the learner's mark lives here (that is the
session's RunState); a Chapter, once generated, is the fixed floor. Glyphs are ASCII, the
game's alphabet (CLAUDE.md 'Map glyphs are ASCII').
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import NamedTuple


class Point(NamedTuple):
    x: int  # column
    y: int  # row


class Direction(Enum):
    """The eight compass moves. hjkl are the cardinals; yubn the diagonals (NetHack)."""

    N = (0, -1)
    S = (0, 1)
    E = (1, 0)
    W = (-1, 0)
    NE = (1, -1)
    NW = (-1, -1)
    SE = (1, 1)
    SW = (-1, 1)

    @property
    def delta(self) -> Point:
        dx, dy = self.value
        return Point(dx, dy)


class TileKind(Enum):
    VOID = 0          # outside any room or corridor: black, impassable
    FLOOR = 1         # '.'
    WALL = 2          # '-' or '|' (glyph set at carve time)
    CORRIDOR = 3      # '#'
    DOOR = 4          # '+'
    STAIRS_DOWN = 5   # '>'
    STAIRS_UP = 6     # '<'
    SEALED = 7        # a gated exit: looks like wall ('-'/'|'), becomes a DOOR when passed
    PEDESTAL = 8      # '_': the scroll rests on it (revealed when the final chapter is completed)


_WALKABLE = frozenset(
    {TileKind.FLOOR, TileKind.CORRIDOR, TileKind.DOOR, TileKind.STAIRS_DOWN, TileKind.STAIRS_UP,
     TileKind.PEDESTAL}
)


@dataclass
class Tile:
    kind: TileKind = TileKind.VOID
    glyph: str = " "

    @property
    def walkable(self) -> bool:
        return self.kind in _WALKABLE


@dataclass
class Grid:
    width: int
    height: int
    tiles: list[list[Tile]]

    @classmethod
    def blank(cls, width: int, height: int) -> Grid:
        return cls(width, height, [[Tile() for _ in range(width)] for _ in range(height)])

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def at(self, x: int, y: int) -> Tile:
        return self.tiles[y][x]

    def walkable(self, x: int, y: int) -> bool:
        return self.in_bounds(x, y) and self.tiles[y][x].walkable


@dataclass
class Room:
    """A room's bounding box, walls included. Interior is the box inset by one."""

    id: str
    x: int
    y: int
    w: int
    h: int

    @property
    def center(self) -> Point:
        return Point(self.x + self.w // 2, self.y + self.h // 2)

    def interior(self):
        for yy in range(self.y + 1, self.y + self.h - 1):
            for xx in range(self.x + 1, self.x + self.w - 1):
                yield Point(xx, yy)

    def tiles(self):
        for yy in range(self.y, self.y + self.h):
            for xx in range(self.x, self.x + self.w):
                yield Point(xx, yy)

    def contains(self, p: Point) -> bool:
        """True when p is on the interior floor, not the wall."""
        return self.x < p.x < self.x + self.w - 1 and self.y < p.y < self.y + self.h - 1


@dataclass
class Chapter:
    grid: Grid
    rooms: list[Room]
    dlvl: int
    start: Point
    stairs_down: Point | None = None
    # Where the learner arrives when descending into this chapter, and steps onto to climb back
    # out. Absent on the first chapter (there is nothing above it); the gate layer never touches
    # it, so the stairs up are always open (you may always retreat, PLAN.md section 7).
    stairs_up: Point | None = None
    # Each non-last room's outgoing door position (toward the next room in the chain). The gate
    # layer seals the doors of gated rooms; the engine itself stays ignorant of why.
    exits: dict[str, Point] = field(default_factory=dict)
