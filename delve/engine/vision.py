"""What the learner can see: current room lit, visited tiles dimmed, unexplored black
(PLAN.md section 7). Pure functions; the accumulating `discovered` set is the session's to
own and persist.
"""

from collections.abc import Iterable

from delve.engine.world import Chapter, Point, Room


def room_at(chapter: Chapter, p: Point) -> Room | None:
    """The room whose interior floor p stands on, or None (a corridor, a doorway)."""
    for room in chapter.rooms:
        if room.contains(p):
            return room
    return None


def _neighbourhood(chapter: Chapter, p: Point) -> set[Point]:
    tiles: set[Point] = set()
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            x, y = p.x + dx, p.y + dy
            if chapter.grid.in_bounds(x, y):
                tiles.add(Point(x, y))
    return tiles


def lit_tiles(chapter: Chapter, p: Point, lit: bool = True) -> set[Point]:
    """Everything lit from position p: the whole current room, else the immediate
    neighbourhood, which is what makes a corridor reveal one step at a time.

    `lit=False` (no working torch, DELVE-0062) always stops at the immediate neighbourhood, even
    while standing inside a room: the same reveal radius a corridor already has."""
    tiles = _neighbourhood(chapter, p)
    if lit:
        room = room_at(chapter, p)
        if room:
            tiles.update(room.tiles())
    return tiles


def keeper_halo(chapter: Chapter, keeper_positions: Iterable[Point]) -> set[Point]:
    """Every keeper's own tile and its immediate neighbourhood (DELVE-0065): a keeper is assumed
    to carry a lit candle at their post, so a torchless learner can still find who to talk to in
    a dark room. Callers only need this when the learner has no working light; a lit room already
    reveals everything a keeper's halo would add."""
    tiles: set[Point] = set()
    for pos in keeper_positions:
        tiles |= _neighbourhood(chapter, pos)
    return tiles
