"""The chapter generator (PLAN.md section 7).

Deliberately unambitious: the linear chain removes the hard part. Rooms go one per cell in
a partition sized to the terminal; consecutive cells are walked in serpentine order and
joined by an L-shaped corridor. The chain is connected by construction, so there is no
spanning tree, no reroll loop, and no connectivity flood fill.

Sealed doors are M2. At M1 every corridor is open, so the whole chapter is walkable.
"""

import math

from delve.engine.rng import Rng
from delve.engine.world import Chapter, Grid, Point, Room, TileKind

# The map area is the terminal minus three rows (message, status, hint), capped so a wide
# terminal does not turn the dungeon into a hike. See PLAN.md section 7.
STATUS_ROWS = 3
MAP_CAP_W, MAP_CAP_H = 160, 44

# Cells are clamped so a 3-room chapter on a huge terminal stays compact, not sprawling.
CELL_MIN_W, CELL_MIN_H = 18, 9
CELL_MAX_W, CELL_MAX_H = 40, 15

# A room's bounding box (walls included) never shrinks below this.
ROOM_MIN_W, ROOM_MIN_H = 7, 4


def _clamp(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, v))


def map_dimensions(cols: int, rows: int) -> tuple[int, int]:
    """The playable map size for a terminal, capped. rows-3 leaves the three text lines."""
    return min(cols, MAP_CAP_W), min(rows - STATUS_ROWS, MAP_CAP_H)


def partition(n: int) -> tuple[int, int]:
    """Smallest cell grid holding n rooms, preferring wide over tall.

    tall = floor(sqrt(n)), wide = ceil(n / tall). Reproduces the worked examples in
    PLAN.md section 7: 1->1x1, 3->3x1, 4->2x2, 6->3x2, 8->4x2, 12->4x3.
    """
    tall = max(1, math.isqrt(n))
    wide = math.ceil(n / tall)
    return wide, tall


def _serpentine(wide: int, tall: int) -> list[tuple[int, int]]:
    """Cell coordinates in boustrophedon order, so consecutive cells are always adjacent."""
    order = []
    for r in range(tall):
        cols = range(wide) if r % 2 == 0 else range(wide - 1, -1, -1)
        for c in cols:
            order.append((c, r))
    return order


def _place_room(rng: Rng, cx: int, cy: int, cw: int, ch: int, room_id: str) -> Room:
    """One room, jittered in size and position, with at least a one-tile margin inside its
    cell so neighbouring rooms never share a wall and corridors have somewhere to run."""
    rw = rng.randint(ROOM_MIN_W, max(ROOM_MIN_W, cw - 2))
    rh = rng.randint(ROOM_MIN_H, max(ROOM_MIN_H, ch - 2))
    ox = rng.randint(1, max(1, cw - rw - 1))
    oy = rng.randint(1, max(1, ch - rh - 1))
    return Room(id=room_id, x=cx + ox, y=cy + oy, w=rw, h=rh)


def _carve_room(grid: Grid, room: Room) -> None:
    for yy in range(room.y, room.y + room.h):
        for xx in range(room.x, room.x + room.w):
            t = grid.at(xx, yy)
            top_bottom = yy in (room.y, room.y + room.h - 1)
            left_right = xx in (room.x, room.x + room.w - 1)
            if top_bottom or left_right:
                t.kind = TileKind.WALL
                t.glyph = "-" if top_bottom else "|"  # NetHack corners are '-'
            else:
                t.kind = TileKind.FLOOR
                t.glyph = "."


def _door(grid: Grid, x: int, y: int) -> None:
    t = grid.at(x, y)
    t.kind = TileKind.DOOR
    t.glyph = "+"


def _corr(grid: Grid, x: int, y: int) -> None:
    """Dig one corridor tile, but only through void. The port pattern below keeps corridors
    entirely in the gap between rooms, so a corridor never grazes a wall into a row of doors."""
    t = grid.at(x, y)
    if t.kind is TileKind.VOID:
        t.kind = TileKind.CORRIDOR
        t.glyph = "#"


def _connect_h(grid: Grid, left: Room, right: Room) -> dict[str, Point]:
    """A door on each facing wall, joined by a corridor with one bend in the void gap. The
    bend column sits strictly between the rooms, so every corridor tile is void. Returns each
    room's door position so the gate layer can seal the outgoing one."""
    ly = left.y + left.h // 2
    ry = right.y + right.h // 2
    lx, rx = left.x + left.w - 1, right.x
    _door(grid, lx, ly)
    _door(grid, rx, ry)
    mid = (lx + rx) // 2
    for x in range(lx + 1, mid + 1):
        _corr(grid, x, ly)
    for y in range(min(ly, ry), max(ly, ry) + 1):
        _corr(grid, mid, y)
    for x in range(mid, rx):
        _corr(grid, x, ry)
    return {left.id: Point(lx, ly), right.id: Point(rx, ry)}


def _connect_v(grid: Grid, top: Room, bottom: Room) -> dict[str, Point]:
    """The vertical twin of _connect_h: doors on the facing top/bottom walls, bend row in the
    void gap between them."""
    tx = top.x + top.w // 2
    bx = bottom.x + bottom.w // 2
    ty, by = top.y + top.h - 1, bottom.y
    _door(grid, tx, ty)
    _door(grid, bx, by)
    mid = (ty + by) // 2
    for y in range(ty + 1, mid + 1):
        _corr(grid, tx, y)
    for x in range(min(tx, bx), max(tx, bx) + 1):
        _corr(grid, x, mid)
    for y in range(mid, by):
        _corr(grid, bx, y)
    return {top.id: Point(tx, ty), bottom.id: Point(bx, by)}


def generate(
    seed: int,
    cols: int,
    rows: int,
    n_rooms: int,
    dlvl: int = 1,
    room_ids: list[str] | None = None,
    *,
    paint_stairs_down: bool = True,
    stairs_up: bool = False,
) -> Chapter:
    """Build a serpentine chapter, reproducible from (seed, cols, rows, n_rooms).

    `paint_stairs_down=False` leaves the last room bare floor while still recording where the
    stairs belong: a gated run reveals them only when the last keeper is passed (PLAN.md
    section 6), so painting `>` at generation would show the way out before it is earned.
    `stairs_up=True` opens a `<` at the entrance, the tile the learner lands on when descending
    into this chapter and steps onto to climb back out; the first chapter has nothing above it.
    """
    if n_rooms < 1:
        raise ValueError("a chapter needs at least one room")
    rng = Rng(seed)
    map_w, map_h = map_dimensions(cols, rows)
    grid = Grid.blank(map_w, map_h)

    wide, tall = partition(n_rooms)
    cell_w = _clamp(map_w // wide, CELL_MIN_W, CELL_MAX_W)
    cell_h = _clamp(map_h // tall, CELL_MIN_H, CELL_MAX_H)
    off_x = (map_w - cell_w * wide) // 2
    off_y = (map_h - cell_h * tall) // 2

    order = _serpentine(wide, tall)
    rooms: list[Room] = []
    cell_rows: list[int] = []
    for i in range(n_rooms):
        cc, cr = order[i]
        room_id = room_ids[i] if room_ids else f"r{i + 1}"
        room = _place_room(rng, off_x + cc * cell_w, off_y + cr * cell_h, cell_w, cell_h, room_id)
        _carve_room(grid, room)
        rooms.append(room)
        cell_rows.append(cr)

    # Consecutive serpentine cells share a row (a sideways step) or a column (the drop between
    # rows). Connect each accordingly, ordering the pair so left/top comes first. `a` is always
    # the earlier room, so its door is the outgoing exit toward the rest of the chapter.
    exits: dict[str, Point] = {}
    for a, b, ra, rb in zip(rooms, rooms[1:], cell_rows, cell_rows[1:], strict=False):
        if ra == rb:
            left, right = sorted((a, b), key=lambda r: r.center.x)
            doors = _connect_h(grid, left, right)
        else:
            top, bottom = sorted((a, b), key=lambda r: r.center.y)
            doors = _connect_v(grid, top, bottom)
        exits[a.id] = doors[a.id]

    start = rooms[0].center
    up = None
    if stairs_up:
        up = _place_up_stairs(grid, rooms[0])
    down = _place_stairs(grid, rooms[-1], avoid=start, paint=paint_stairs_down)
    return Chapter(grid=grid, rooms=rooms, dlvl=dlvl, start=start, stairs_down=down,
                   stairs_up=up, exits=exits)


def _place_stairs(grid: Grid, last: Room, avoid: Point, paint: bool = True) -> Point:
    """The tile where the stairs down belong, on a floor tile of the final room, never on the
    player's start (which only collides in a one-room chapter). When `paint` is False the tile
    stays floor and only its position is returned, so a gate can reveal the stairs on a pass."""
    spot = last.center
    if spot == avoid:
        for p in last.interior():
            if p != avoid:
                spot = p
                break
    if paint:
        t = grid.at(spot.x, spot.y)
        t.kind = TileKind.STAIRS_DOWN
        t.glyph = ">"
    return spot


def _place_up_stairs(grid: Grid, first: Room) -> Point:
    """The `<` at the chapter entrance, on the first room's centre floor. Always open: the stairs
    up are never sealed, so a learner may always retreat to an earlier floor (PLAN.md section 7)."""
    spot = first.center
    t = grid.at(spot.x, spot.y)
    t.kind = TileKind.STAIRS_UP
    t.glyph = "<"
    return spot
