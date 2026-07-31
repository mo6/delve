"""The M1 headless harness: generate a chapter, prove it is connected by construction, and
walk it end to end as a list of Commands with no terminal at all (PLAN.md section 4). This
is the test the rest of the milestones lean on.
"""

from collections import deque

import pytest

from delve.engine import layout
from delve.engine.world import Direction, Point
from delve.session.commands import Move
from delve.session.run import new_run

SIZES = [(100, 30), (120, 30), (160, 44)]
ROOM_COUNTS = [1, 3, 4, 6, 8]

_CARDINALS = {
    Point(0, -1): Direction.N,
    Point(0, 1): Direction.S,
    Point(1, 0): Direction.E,
    Point(-1, 0): Direction.W,
}


def _walkable_neighbours(grid, p):
    for d in _CARDINALS:
        x, y = p.x + d.x, p.y + d.y
        if grid.walkable(x, y):
            yield Point(x, y)


def _reachable(grid, start):
    seen = {start}
    q = deque([start])
    while q:
        cur = q.popleft()
        for nxt in _walkable_neighbours(grid, cur):
            if nxt not in seen:
                seen.add(nxt)
                q.append(nxt)
    return seen


def _path(grid, start, goal):
    """Cardinal BFS path start->goal as a list of Points, or None."""
    prev = {start: None}
    q = deque([start])
    while q:
        cur = q.popleft()
        if cur == goal:
            break
        for nxt in _walkable_neighbours(grid, cur):
            if nxt not in prev:
                prev[nxt] = cur
                q.append(nxt)
    if goal not in prev:
        return None
    out = []
    cur = goal
    while cur is not None:
        out.append(cur)
        cur = prev[cur]
    return list(reversed(out))


def _moves_along(path):
    for a, b in zip(path, path[1:], strict=False):
        yield Move(_CARDINALS[Point(b.x - a.x, b.y - a.y)])


def _grid_text(grid):
    return "\n".join("".join(grid.at(x, y).glyph for x in range(grid.width))
                     for y in range(grid.height))


# -- the generator --------------------------------------------------------------------------


@pytest.mark.parametrize("n,expected", [(1, (1, 1)), (3, (3, 1)), (4, (2, 2)),
                                        (6, (3, 2)), (8, (4, 2)), (12, (4, 3))])
def test_partition_matches_the_spec(n, expected):
    assert layout.partition(n) == expected


@pytest.mark.parametrize("cols,rows", SIZES)
@pytest.mark.parametrize("n", ROOM_COUNTS)
def test_chapter_is_connected_by_construction(cols, rows, n):
    ch = layout.generate(seed=7, cols=cols, rows=rows, n_rooms=n)
    assert len(ch.rooms) == n
    reachable = _reachable(ch.grid, ch.start)
    for room in ch.rooms:
        interior = set(room.interior())
        assert interior & reachable, f"room {room.id} unreachable from start"
    assert ch.stairs_down in reachable


@pytest.mark.parametrize("cols,rows", SIZES)
@pytest.mark.parametrize("n", ROOM_COUNTS)
def test_layout_is_deterministic(cols, rows, n):
    a = layout.generate(seed=42, cols=cols, rows=rows, n_rooms=n)
    b = layout.generate(seed=42, cols=cols, rows=rows, n_rooms=n)
    assert _grid_text(a.grid) == _grid_text(b.grid)


def test_different_seeds_differ():
    a = layout.generate(seed=1, cols=120, rows=30, n_rooms=6)
    b = layout.generate(seed=2, cols=120, rows=30, n_rooms=6)
    assert _grid_text(a.grid) != _grid_text(b.grid)


def test_rooms_stay_inside_the_map():
    ch = layout.generate(seed=3, cols=100, rows=30, n_rooms=6)
    g = ch.grid
    for room in ch.rooms:
        assert 0 <= room.x and room.x + room.w <= g.width
        assert 0 <= room.y and room.y + room.h <= g.height


# -- the run, headlessly --------------------------------------------------------------------
# new_run builds the M2 slice: room 1's exit is sealed until Ada is passed, so the whole-chapter
# walk lives in test_slice.py now. Here we only check the movement mechanics the run still owns.


def test_start_room_is_sealed_until_passed():
    run = new_run(seed=99, cols=100, rows=30, name="Ada")
    goal = run.chapter.rooms[-1].center
    # The gate has not been passed, so no path leaves room 1.
    assert _path(run.chapter.grid, run.player.pos, goal) is None


def test_blocked_move_costs_no_turn_and_reports():
    # Walk west until something blocks it (a wall or the map edge); that step must cost
    # nothing and say so. Which direction blocks first is geometry, so we don't assert it.
    run = new_run(seed=5, cols=100, rows=30)
    saw_block = False
    for _ in range(80):
        turn_before = run.turn
        pos_before = run.player.pos
        frame = run.apply(Move(Direction.W))
        if run.player.pos == pos_before:
            assert run.turn == turn_before, "a blocked move charged a turn"
            assert frame.messages[-1] == "You can't go that way."
            saw_block = True
            break
    assert saw_block, "expected to hit a wall walking west across the map"


def test_frame_carries_only_view_types():
    run = new_run(seed=8, cols=100, rows=30)
    frame = run.frame()
    cell = frame.map.cells[0][0]
    assert isinstance(cell.glyph, str)
    # Colour is one of sixteen names, never a curses attribute.
    assert isinstance(cell.colour.value, str)
    assert isinstance(frame.hint, str)
