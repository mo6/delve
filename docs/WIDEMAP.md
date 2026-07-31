# The wide-tile emoji map, kept inside 100 columns

Future-reference design note, not scheduled work. This is the implementation plan for the rich
look sketched in [DISPLAY.md](DISPLAY.md), taken with **one constraint fixed by decision**: every
tile paints to **two terminal columns wide and one row high**, the map carries **emoji**, and the
terminal minimum **stays 100x30**. We do not widen the requirement. That reverses two of DISPLAY's
recommendations and is the whole reason this note exists.

**What it supersedes.** DISPLAY.md §5.1 recommends *widening the rich minimum to 160-200 columns*
and keeping "the layout in tile-space, identical between modes; only the rendered width differs".
DISPLAY.md §9.1 leaves "widen the requirement or shrink the dungeon" open. This note answers both:
**keep 100 columns, and change the layout so a rich floor is less wide.** The clean "same dungeon,
wider paint" model does not survive the 100-column constraint; a rich floor is a *narrower* dungeon,
not the same one repainted. Everything else in DISPLAY.md (the boundary in §3, the width-aware
panels in §4, the theme table in §11.1, the portability warning in §6) stands unchanged.

---

## 1. The constraint, made concrete

At the 100x30 minimum the playable map is `map_w = min(100, 160) = 100` tiles wide and
`map_h = 27` tiles tall (`layout.map_dimensions`, minus the three text rows). Rooms go one per cell
in a partition sized to that width, cells clamped to `[18x9, 40x15]` (`layout.CELL_MIN/MAX`).

The horizontal footprint is `wide x cell_w`, and it is already near the edge:

| Rooms | Partition | `cell_w` | Tiles across | At 2 col/tile |
|---|---|---|---|---|
| 3 | 3x1 | `clamp(33,18,40)=33` | 99 | **198** |
| 4 | 2x2 | `clamp(50,18,40)=40` | 80 | **160** |
| 6 | 3x2 | `clamp(33,18,40)=33` | 99 | **198** |
| 12 | 4x3 | `clamp(25,18,40)=25` | 100 | **200** |

So a rich floor cannot keep today's partition: every multi-room chapter already spends the full
100-column width at one column per tile, and doubling paints it off the screen (DISPLAY §11.5 shows
the two-room composite breaking 100). There is no camera to fall back on and none is wanted
(PLAN §7: "no scrolling viewport"). The dungeon has to *become narrower in tiles*, not just paint
wider.

---

## 2. The decision: halve the tile budget, let the layout absorb it

In rich mode the generator lays the dungeon out in a **halved tile-width budget**:
`tile_budget_w = map_w // tile_width` (50 tiles at the minimum terminal), and the renderer paints
each of those tiles to two columns, filling 100 columns exactly. The vertical budget is unchanged
(one row per tile): `map_h = 27` tiles.

Three levers reclaim the horizontal space. We use the second as the load-bearing one and offer the
third as enrichment; the first alone is not enough.

### Lever A: narrower rooms (necessary, not sufficient)

Shrinking `cell_w` is the obvious move, but it hits a floor fast. At 50 tiles across you cannot fit
three rooms in a row: `3 x CELL_MIN_W = 3 x 18 = 54 > 50`. Two fit (`2 x 18 = 36`). Lowering
`CELL_MIN_W` below 18 makes rooms cramped (a room's own box floor is `ROOM_MIN_W = 7`, and the cell
needs margin for corridors), so this lever caps at "**at most two rooms across**" and then stops.
That cap is the real content, and it forces lever B.

### Lever B: a tall-preferring partition (the fix)

Today `layout.partition` prefers *wide* (`tall=isqrt(n)`, `wide=ceil(n/tall)`: 3->3x1, 6->3x2). Rich
mode inverts it: **cap `wide` at 2 and grow downward**, `wide = min(2, n)`, `tall = ceil(n/wide)`.
The dungeon stops marching sideways and starts stacking, which is exactly the "less linear" shape
the constraint wants. The serpentine walk still connects consecutive cells (`_serpentine` already
handles any `wide x tall`), so the chain stays connected by construction. Worked sizes at 100x30:

| Rooms | Rich partition | `cell_w` (of 50) | `cell_h` (of 27) | Fits |
|---|---|---|---|---|
| 3 | 2x2 (one empty) | `clamp(25,18,40)=25` -> 50 | `clamp(13,9,15)=13` -> 26 | yes |
| 4 | 2x2 | 25 -> 50 | 13 -> 26 | yes |
| 6 | 2x3 | 25 -> 50 | `clamp(9,9,15)=9` -> 27 | exactly |

Six rooms is the natural ceiling of a rich floor at the minimum terminal: `2 wide x 3 tall`, the
vertical budget spent to the row. That is not a regression dressed up as a feature; it is the
**pedagogy the validator already enforces** (PLAN §7, CLAUDE.md: warn at 7, error at 9, "nine
lessons without a break is a lecture"). A rich floor simply lands on the low end of that range. A
larger chapter either renders in ASCII (the fallback is first-class) or the author splits it; the
engine never splits a chapter.

### Lever C: branching and circular corridors (enrichment, gated by rule 2)

The user's second idea is topology: **corridors that split, and loops the learner can walk around**,
so lessons are not answered in one strict line. This is a genuine improvement and it packs rooms
more tidily than a rigid grid, but it collides head-on with the sealed-door rules and must be built
so that **no route bypasses a lesson by construction**, never proved so by a flood fill. That is the
line CLAUDE.md draws in rule 2: "If you find yourself writing a flood fill to prove the keeper
blocks the route, you've reintroduced a problem the design deleted." So:

- **Branching is safe as a tree.** Root the chapter at the entrance; every edge is one gated door;
  a room may have two or more child corridors. The learner then answers in a *partial* order (pick
  any open branch) instead of a line, and the dungeon fans out vertically rather than sideways. A
  tree has no cycles, so there is no bypass to check: each locked door still fronts exactly one
  unpassed lesson, and "no path around a lesson" holds by construction. This is the recommended
  form of lever C, and it composes with lever B (a tree is naturally tall and narrow).
- **Circular traversal is safe only among passed rooms.** A loop is an *extra, ungated* corridor.
  Add one only between two rooms that are already reachable without crossing an unpassed gate, i.e.
  a back-edge into territory the learner has cleared (rule 3: re-reading is free, backtracking is
  the behaviour we want). A loop edge that shortcuts toward a *deeper, unpassed* room is a rule-2
  violation: it is a path around a lesson. The safe construction is "loops close backward, never
  forward"; it needs no validation because the generator only ever draws a back-edge, the same way
  it only ever draws corridors through void today. If a loop cannot be shown safe by construction,
  it does not ship. Given the risk-for-polish ratio, **cycles are deferred**; the tree already
  solves the width problem.

---

## 3. Rule 2 and rule 1 under the new topology

The reason the current generator has no connectivity check is that a serpentine line is trivially
connected and trivially gated. A tree keeps both properties *if built that way*: connected because
every room is carved with exactly one parent corridor, gated because that corridor's door is the
room's gate. `gate.install_chapter_gates` already gates "a whole chapter, the last room revealing
the stairs" off the room list and the exits map; it keys off `exits[room.id]`, not off the
serpentine shape, so a tree that populates `exits` per edge needs no gate-layer change. This is the
seam holding: `gate.py` stays the pure training boundary (rule 1), the generator stays pure geometry
(rule 1: `engine` imports nothing above it), and the non-linear shape lives entirely in
`layout.py`.

**The record must carry the mode.** Because the rich dungeon is a *different* tile-space layout from
the ASCII one (different partition), the mode is part of the layout identity, alongside
`(seed, cols, rows)` in `runs`. A run is fixed to a mode at start and regenerates tile-for-tile from
its record; you do not switch a run between ASCII and rich mid-play, because that would relayout the
dungeon under the player. This is a small migration (one column, or a `tile_width` field) and is the
honest cost of reversing DISPLAY's "identical between modes".

---

## 4. Revised phasing

Phases 0-2 and 4-5 are exactly as in the earlier plan; only the map phase (Phase 3) changes, because
it no longer widens the terminal, it narrows the dungeon. Each phase is shippable and reversible and
keeps the ASCII look working.

- **Phase 0: the width primitive.** `ui/width.py` `display_width(s)` (stdlib `east_asian_width`,
  W/F -> 2, plus a curated width-2 emoji set) and `tests/test_width.py`. No visible change.
- **Phase 1: width-aware panels (DISPLAY §4).** Swap `len` for `display_width` in `windows.py`
  (`_seg_width`, the wrap, the `_put_line` / `_draw_prompt` / field-cursor advances). `TEXT_W = 69`
  becomes a column budget. No change with ASCII content; unlocks emoji in lessons and scrolls.
  Check: tests green, `tools/screens.py --check` unchanged, an emoji dropped into a lesson wraps
  right.
- **Phase 2: cell identity + theme layer, still ASCII (DISPLAY §3).** Add `Cell.role: str`
  (`compare=False`), filled in `session/run.py:_cell` (`self.keepers[p].keeper.kind` already gives
  wizard/gatekeeper/shopkeeper). Add `ui/theme.py`, `role -> (glyph, width)`, only the `ascii` theme
  populated. Golden tests do not move.
- **Phase 3: the narrow, wide-painted map (this note).** Two independent pieces, each checkable:
  - **3a, the layout.** In rich mode, budget `map_w // tile_width` tiles across, cap `wide` at 2, and
    grow `tall`. Store the mode in `runs`. The dungeon regenerates identically; the ASCII path is
    untouched. Check headless: a rich 6-room floor lays out `2x3` inside 50 tiles and 27 rows, and
    reloads tile-for-tile from its record. No paint involved yet, so this is a pure `layout.py` +
    snapshot test.
  - **3b, the paint.** `render.py` maps tile `(x,y)` to column `(2*x + origin)` and pads a narrow
    glyph to two columns; a **wide-aware wall renderer** in `walls.py` fills a horizontal wall's two
    columns (`--`) and pads a vertical one (`|` then space), corners and tees joined. Behind the
    capability gate, ASCII glyphs still. Check by eye: "spaced ASCII" map, continuous walls, panel
    placed right off the doubled `map_cols`, all inside 100 columns; the ASCII default is unchanged.
  - **Optional 3c, the tree.** Replace the serpentine chain with a rooted tree (lever C), branches
    populating `exits` per edge so the gate layer is untouched. Cycles stay out (deferred). Check:
    every leaf still gated, no ungated path deeper, and it is connected by construction (no flood
    fill anywhere in the diff).
- **Phase 4: the emoji theme (DISPLAY §11.1).** Populate the `rich` theme with the curated,
  single-codepoint, width-2 set; add a rich `tools/screens.py` mock asserting *display columns*;
  revise CLAUDE.md's "Map glyphs are ASCII" / "Never emoji" to "ASCII is the portable fallback
  theme; the rich theme is emoji, capability-gated", and update SCREENS §9.
- **Phase 5 (optional): pack-authored rich glyphs**, declared beside a mandatory ASCII fallback,
  validated against the curated set.

---

## 5. Mock-ups: layouts in 50 tiles

The room-making space is really **50 tiles wide by 27 tall** (100 columns halved, minus nothing
vertically). These are faithful schematics generated with the same cell maths as §2, not hand-drawn.
The first pair is **tile-space** (what the generator carves, one character per tile, the ASCII
alphabet). The last is the same 4-room floor **painted in rich mode** (two columns per tile, walls
box-drawn, entities as emoji), which comes out at exactly 100 columns.

**Four rooms.** Partition `2x3` collapses to `2x2` here (four rooms fill the grid), cells `25x13`,
footprint `50 wide x 26 tall`. The serpentine walk is `r1 (top-left) -> r2 (top-right) -> r3
(bottom-right) -> r4 (bottom-left)`, a loop shape rather than a sideways march. `@` is the learner's
start in r1; `+` are the gated doors.

```
tile-space, x runs 0..49 (50 wide):

  --------------------     --------------------
  |..................|     |..................|
  |..................|     |..................|
  |..................|     |..................|
  |.........@........+#####+..................|
  |..................|     |..................|
  |..................|     |..................|
  |..................|     |..................|
  --------------------     ----------+---------
                                     #
                                     #
                                     #
                                     #
  --------------------     ----------+---------
  |..................|     |..................|
  |..................|     |..................|
  |..................|     |..................|
  |..................+#####+..................|
  |..................|     |..................|
  |..................|     |..................|
  |..................|     |..................|
  --------------------     --------------------
```

**Three rooms.** Same `2x2` cells, but the bottom-left cell is empty (three rooms, four cells), so
the chain is `r1 (top-left) -> r2 (top-right) -> r3 (bottom-right)`. The empty quarter is where a
branch or a fourth room would go; it is not wasted so much as headroom.

```
tile-space, x runs 0..49 (50 wide):

  --------------------     --------------------
  |..................|     |..................|
  |..................|     |..................|
  |..................|     |..................|
  |.........@........+#####+..................|
  |..................|     |..................|
  |..................|     |..................|
  |..................|     |..................|
  --------------------     ----------+---------
                                     #
                                     #
                                     #
                                     #
                           ----------+---------
                           |..................|
                           |..................|
                           |..................|
                           |..................|
                           |..................|
                           |..................|
                           |..................|
                           --------------------
```

**The 4-room floor painted (rich mode, 2 columns per tile = 100 columns).** Ada is 🧑's start, a
gatekeeper 💂 stands inside r2, the cat 🐈 trails, doors are 🚪. Walls are ACS line-drawing widened
so a horizontal tile fills both its columns and the line stays continuous (§4, Phase 3b). This is a
map-area vignette, not an asserted 100x30 frame; the status and hint rows follow §4 (flowed text).

```
    ┌─────────────────────────────────────┐           ┌─────────────────────────────────────┐
    │ . . . . . . . . . . . . . . . . . . │           │ . . . . . . . . . . . . . . . . . . │
    │ . . . . . . . . . . . . . . . . . . │           │ . . . . . . . . . . . . . . . . . . │
    │ . . . . . . . . . . . . . . . . . . │           │ . . . . . . . . . . . . . . . . . . │
    │ . . . . . . . . . 🧑. . . . . . . . 🚪# # # # # 🚪. 💂. . . . . . . . . . . . . . . . │
    │ . . . . . . . . 🐈. . . . . . . . . │           │ . . . . . . . . . . . . . . . . . . │
    │ . . . . . . . . . . . . . . . . . . │           │ . . . . . . . . . . . . . . . . . . │
    │ . . . . . . . . . . . . . . . . . . │           │ . . . . . . . . . . . . . . . . . . │
    └─────────────────────────────────────┘           └───────────────────🚪────────────────┘
                                                                           #
                                                                           #
                                                                           #
                                                                           #
    ┌─────────────────────────────────────┐           ┌───────────────────🚪────────────────┐
    │ . . . . . . . . . . . . . . . . . . │           │ . . . . . . . . . . . . . . . . . . │
    │ . . . . . . . . . . . . . . . . . . │           │ . . . . . . . . . . . . . . . . . . │
    │ . . . . . . . . . . . . . . . . . . │           │ . . . . . . . . . . . . . . . . . . │
    │ . . . . . . . . . . . . . . . . . . 🚪# # # # # 🚪. . . . . . . . . . . . . . . . . . │
    │ . . . . . . . . . . . . . . . . . . │           │ . . . . . . . . . . . . . . . . . . │
    │ . . . . . . . . . . . . . . . . . . │           │ . . . . . . . . . . . . . . . . . . │
    │ . . . . . . . . . . . . . . . . . . │           │ . . . . . . . . . . . . . . . . . . │
    └─────────────────────────────────────┘           └─────────────────────────────────────┘
```

**Six rooms in two rows, smaller rooms, with objects.** Six rooms fit two ways. §2's lever B keeps
room *width* and stacks three rows (`2x3`); the alternative here trades width for a shorter floor:
relax `CELL_MIN_W` to about 14 and three rooms fit across (`3 x 16 = 48 <= 50`), so six rooms sit in
`3x2`, two rows. Rooms then jitter between roughly 11 and 14 tiles wide, which reads fine and shows
real size variation. Objects are scattered on interior floor tiles the way OBJECTS.md places them,
`$` a coin, `(` a coconut half, `?` a USB stick (the theme upgrades each to 🪙 🥥 💾 in rich mode).
Two seeds, to show the variation:

```
seed 7:                                          seed 31:

   -------------  -----------      -----------                     ------------    ------------
   |...........|  |.........|      |.........|      -----------     |..........|    |..........|
   |...........|  |.........|      |.........|      |.........|     |..........|    |..........|
   |...........|  |.........|      |.........|      |.........|  ###+......?...+##  |..........|
   |.....@.....+# |.........|      |.........|      |.........|  #  |..........| ###+..........|
   |...........|##+.........+######+.........|      |.........|  #  |..........|    |..........|
   |..........$|  |.........|      |(........|      |....@....+###  ------------    |..........|
   -------------  |.........|      |.........|      |...(.....|                     ------+-----
                  |.........|      |.........|      |.........|                           #
                  |.........|      |.........|      |.........|                           #
                  -----------      -----+-----      -----------                           #
                                        ###                                               #
                                          #                                               #
  -----------                        -----+-----      -----------   --------------        #
  |.........|                        |.........|        |......(..|   |............|      #
  |.........|                        |.........|        |.........|   |...........$|      #
  |.........|       ------------     |.........|        |.........|   |............|   -----+-----
  |.........|       |..........|     |.........|        |.........| ##+............+## |.........|
  |.........+####   |?.........|  ###+.........|        |.........+## |............| # |...$.....|
  |.........|   ####+..........+###  |.........|        |.........|   |............| # |.........|
  |.........|       |..........|     |.........|        |.........|   |............| ##+.........|
  |$........|       ------------     -----------        |.........|   -------------- ##+.........|
  -----------                                           |.........|                    |.........|
                                                        -----------                    -----------
```

**A tree of corridors: one answer, two doors, a choice (lever C).** When the learner passes the
parent keeper, *two* doors open on the parent room, each running to a different child. The learner
picks a branch; both children are gated by their own keepers, so nothing is skipped (§2, §3). Here
the parent holds a coin, one child a USB, the other a coconut, first in tile-space then painted:

```
tile-space:                                        rich paint (2 cols/tile):

               --------------------                              ┌─────────────────────────────────────┐
               |..................|                              │ . . . . . . . . . . . . . . . . . . │
               |..................|                              │ . . . . . . . . . . . . . . . . . . │
               |..................|                              │ . . . . . . . . . . . . . . . . . . │
               |.........@........|                              │ . . . . . . . . . 🧑. . . . . . . . │
               |.......$..........|                              │ . . . . . . . 🪙. . . . . . . . . . │
               |..................|                              │ . . . . . . . . . . . . . . . . . . │
               |..................|                              │ . . . . . . . . . . . . . . . . . . │
               -----+--------+-----                              └─────────🚪────────────────🚪────────┘
                    #        #                                             #                 #
                    #        #                                             #                 #
            #########        ##########                    # # # # # # # # #                 # # # # # # # # # #
            #                         #                    #                                                   #
            #                         #                    #                                                   #
   ---------+--------        ---------+--------      ┌─────🚪──────────────────────────┐ ┌─────────────────────🚪──────────┐
   |................|        |................|      │ . . . . . . . . . . . . . . . . │ │ . . . . . . . . . . . . . . . . │
   |................|        |................|      │ . . . . . . . . . . . . . . . . │ │ . . . . . . . . . . . . . . . . │
   |....?...........|        |................|      │ . . . . 💾. . . . . . . . . . . │ │ . . . . . . . . . . . . . . . . │
   |................|        |................|      │ . . . . . . . . . . . . . . . . │ │ . . . . . . . . . . . . . . . . │
   |................|        |................|      │ . . . . . . . . . . . . . . . . │ │ . . . . . . . . . . . . . . . . │
   |................|        |...............(|      │ . . . . . . . . . . . . . . . . │ │ . . . . . . . . . . . . . . . 🥥│
   |................|        |................|      │ . . . . . . . . . . . . . . . . │ │ . . . . . . . . . . . . . . . . │
   ------------------        ------------------      └─────────────────────────────────┘ └─────────────────────────────────┘
```

Four things these show. **It fits**: 50 tiles paints to exactly 100 columns, no wider terminal
asked for (§2). **Keeper identity reads without colour**: 💂 is not another 🧑, which was DISPLAY
§8.8's complaint. **The floor is less linear**: the plain serpentine already loops, and the tree
fans into a genuine choice of room, the "not necessarily answered in a line" shape the constraint
wanted. **Objects give the floor texture**: a 🪙 across the room pulls the learner to explore and a
🥥 or 💾 reads as a thing to pick up, the same pull SCREENS §11 gets from `$` but self-explanatory.
When Phase 4 ships, `tools/screens.py` grows a rich twin of these and asserts display columns, the
way SCREENS.md asserts character columns today.

---

## 6. Open decisions

1. **Mode selection.** Auto-detect (terminal capability plus width) with a `--rich` / `--ascii`
   override. A run is pinned to its mode at start (§3).
2. **The rich room-per-floor ceiling.** Six at the minimum terminal (§2). Confirm the shipped packs'
   floors fit, or mark the ones that only render rich on a taller terminal.
3. **How far to lower `CELL_MIN_W`.** Staying at 18 caps rich at two rooms across (fine); dropping it
   buys nothing without also relaxing `ROOM_MIN_W`, and cramped rooms read worse than tall floors.
   Recommend: leave the minimums, let lever B carry it.
4. **Whether cycles ever ship.** Deferred here on the risk-for-polish ratio; revisit only with a
   back-edge-only construction that needs no connectivity check (§2, lever C).

---

## 7. What stays true regardless

- **The session never learns what a glyph looks like, or how wide a tile paints** (rule 2). The
  narrower layout is `engine`/`layout` geometry; the doubled paint and the emoji are `ui`. The
  headless harness and the golden slice stay valid across both looks.
- **Sealed doors stay structural** (rule 2). Branching keeps "no path around a lesson" true by
  construction; a cycle only ever closes backward. No flood fill enters the generator.
- **ASCII is never dropped, only demoted to the fallback theme**, and it keeps today's wide
  serpentine at one column per tile. Nothing regresses on a classic terminal.
- **The pack format is the portable asset** (PLAN §13.5). A pack's map glyphs stay an ASCII
  alphabet; the layout mode and the emoji are rendering choices, so a pack keeps working on a
  classic terminal and never requires the rich look.
