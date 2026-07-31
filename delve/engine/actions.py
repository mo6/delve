"""Turn resolution. At M1 that is only movement: resolve a step against the map and report
where the actor lands, or None when a wall blocks it. Pure; the session decides what a
blocked step means (a message, no turn spent).
"""

from delve.engine.world import Chapter, Direction, Point


def step(chapter: Chapter, pos: Point, direction: Direction) -> Point | None:
    """The tile one step in `direction`, or None if it is not walkable."""
    d = direction.delta
    nx, ny = pos.x + d.x, pos.y + d.y
    if chapter.grid.walkable(nx, ny):
        return Point(nx, ny)
    return None
