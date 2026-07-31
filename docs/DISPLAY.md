# Enhanced display: emoji, wide glyphs, and a 2026 look

Future-reference design note, not scheduled work. Delve renders like NetHack today: one ASCII
character per tile, sixteen colours, box-drawing walls. This plan sketches how it could grow a
richer visual layer, emoji and other expressive Unicode glyphs, without throwing away the roguelike
core or the headless-session discipline that makes it testable. §11 holds hand-sketched mock-ups of
that look: rooms, keepers, pets, money, and pack objects, beside the ASCII they replace. For the
same look in a browser (CSS tiles, no double-width arithmetic), see [WEBDISPLAY.md](WEBDISPLAY.md).
For the opposite move, keeping the map but *hiding it from the screen* and driving the dungeon by
typed prose instead (an LLM parses instructions into discrete commands), see
[TEXTMODE.md](TEXTMODE.md): this file and WEBDISPLAY.md re-skin the grid; TEXTMODE.md removes it.

It is deliberately a **reversal of two standing rules**, taken with eyes open. CLAUDE.md today says
**"Map glyphs are ASCII"** and **"Never emoji"**, and SCREENS.md §9.4 spells out the arithmetic
reason: emoji are double-width, astral-plane, and often multi-codepoint, which breaks a grid that
assumes one cell is one character. None of that arithmetic is wrong. This plan is about **paying for
it on purpose** in a later major version, behind capability detection, with the ASCII look kept as
the fallback. Until it ships, the rules stand; this file is the argument for changing them, not the
change.

---

## 1. The one hard fact: display width is not string length

Every hard problem below is a corollary of a single fact. In a monospace terminal, a character
occupies **1 or 2 columns**, and which one is not visible from the string:

- Plain ASCII and Latin text: **1 column**.
- CJK ideographs, and most emoji: **2 columns** (East Asian *Wide* / *Fullwidth*).
- Box-drawing and many symbols: **East Asian *Ambiguous*** (1 column in a Western terminal, 2 in a
  CJK-configured one). This is the bet SCREENS.md §9.3 already takes for walls and window frames.
- Emoji are worse than "wide": many are **astral-plane** (beyond U+FFFF), some are **grapheme
  clusters** of several codepoints (a base, a variation selector, a skin-tone modifier, ZWJ
  sequences like family emoji). So a single visible glyph may be several codepoints and 2 columns,
  and `len(s)` tells you neither.

Delve's whole rendering rests on the opposite assumption: `Cell.glyph: str` is one character, the
map is a fixed grid where **one cell means one column** (CLAUDE.md), and the panel wraps text with
`textwrap`, which counts characters. Everything in this plan is about replacing "count characters"
with "count display columns", and doing it in as few places as possible.

**Stdlib note, and a tension to flag now.** `unicodedata.east_asian_width(ch)` (stdlib) classifies
`W`/`F` as wide and covers the common cases, so a first cut needs no dependency and keeps the
stdlib-only line (the same line that rejected gettext and Pydantic). But it is **not** a complete
emoji-width oracle: emoji presentation selectors (U+FE0F), ZWJ sequences, and some newer emoji need
a real width table (the job the `wcwidth` package does). Adopting emoji fully may force the choice
between vendoring a width table and relaxing stdlib-only for one small data module. Decide that when
it matters; do not pretend `east_asian_width` alone is enough for arbitrary emoji.

---

## 2. Two surfaces, two very different answers

The user's framing is exactly right and worth stating as the organising principle:

- **The map is a fixed grid.** A wide glyph there **changes the geometry**: it eats two columns of a
  layout that was laid out in single-column tiles. This is the expensive surface.
- **The panels are flowed text.** A wide glyph there **needs no resizing**: it simply takes more
  room inside the same wrapped paragraph, the way a longer word would. The panel box stays 73
  columns; only the wrap accounting has to learn to count columns instead of characters.

So the plan splits cleanly. Panels are a contained, low-risk change (§4). The map is the real design
work (§5), because "one tile is now two columns" ripples into the terminal minimum, the walls, and
the generator's relationship to the screen.

---

## 3. Keep the boundary: session stays glyph-agnostic, ui owns the look

Rule 2 (the loop lives in `session`, `ui` only paints) is what keeps a second look tractable, so it
must survive. The map today already flows the right way: the session hands `ui` a `Cell(glyph,
colour, dim)` view model, and `ui/attrs.py` turns the colour name into a curses attribute. The
richer look is **presentation**, so it belongs on the `ui` side of that line.

Concretely, the session keeps emitting **semantic, ASCII-first** cells, and `ui` gains a **theme
layer** that maps a cell's identity to a glyph:

- The session's `Cell` grows (or is read for) a stable **identity**: it already carries a glyph
  (`@`, `f`, `$`, `+`, `>`); that glyph, plus the tile kind and entity kind it already knows, is
  enough of a key. Prefer a small explicit `kind`/`role` on the view model over pattern-matching the
  ASCII glyph, so the theme is a lookup, not a guess.
- `ui` holds one or more **themes**: `ascii` (today's look, the fallback) and `rich` (emoji and wide
  glyphs). A theme is a table from cell identity to `(glyph, width)`. Tests keep asserting the ASCII
  theme, so the golden slice and the screen mock-ups do not move unless we want them to.
- **Packs never ship raw terminal glyphs for the map.** A pack object still declares an ASCII
  object-class char (OBJECTS.md's `$ ( % ! ? [ * ) = "`); the *theme* upgrades that to an emoji.
  This keeps a downloaded pack from smuggling in an astral-plane, double-width surprise, and keeps
  the map-glyph-is-an-alphabet principle: the alphabet just gets a nicer font.

This means the map's **semantic content is theme-independent and testable**, and switching to emoji
is a `ui`-local change plus a capability check, not an engine change.

---

## 4. Panels: width-aware wrapping, and nothing else

The panels (lesson, question, explanation, scroll, inventory, the drop field) are the easy win and a
good first phase, because they unlock wide **text** without touching the map at all.

- **Replace character counting with column counting in the wrap.** `windows.py` uses
  `textwrap.wrap`, which counts characters. Introduce a `display_width(s)` helper (sum of per-char
  widths, §1) and a width-aware wrapper that breaks on the same rules already in place
  (`break_on_hyphens=False`, never split a URL/domain, break on paragraph boundaries). The panel
  width (`TEXT_W = 69`) is a **column** budget, not a character budget.
- **The panel box does not move.** A wide glyph inside a line consumes two of the 69 columns; the
  line simply holds fewer glyphs. No panel resizes, exactly as the user notes. The double-line frame
  is unchanged.
- **Height stays computed the same way** (the minimise-wasted-rows sweep, SCREENS §8.2): it counts
  wrapped lines, and a line is still a line whatever its glyphs weigh.
- **Emoji in lesson prose already validate** as far as the format goes (prose is UTF-8, CLAUDE.md);
  the only thing missing is that the wrap must weigh them correctly, which this phase adds.
- **The cursor and struck-option drawing** (the assertion prompt writes labels then advances `x` by
  `len(choice)`) must advance by `display_width(choice)`, not `len`. Small, local, and the same
  fix as the wrap.

A pack could then write a lesson with a warning emoji or a euro-with-flair and it would wrap
correctly. This phase is shippable on its own and is the natural place to start.

---

## 5. The map: every tile is two columns

The clean model for a rich map is **the whole grid goes double-width**: each logical tile occupies
**exactly two terminal columns**, always, whatever it holds.

- An emoji tile fills its two columns natively.
- A narrow glyph (padded ASCII, a 1-column box char, the `@`) is **padded to two columns** (the
  glyph plus a trailing space, or centred). So alignment is uniform and the renderer never has to
  reason about a ragged mix of 1- and 2-column tiles mid-row.

This is the key simplification: **fixed 2-columns-per-tile** keeps "one tile is a fixed width",
which is the property the current 1-column grid relies on. The cost is horizontal: a map that was
`N` tiles wide is now `2N` terminal columns.

### 5.1 Consequences, in order of pain

1. **The terminal minimum changes.** Today it is 100x30 (Windows Terminal's default, chosen so
   Windows needs no resize). At two columns per tile, either the dungeon holds half as many tiles
   across, or the minimum widens. Options, to decide when this is real:
   - **Rich mode requires a wider terminal** (say 160-200 columns), and the **ASCII mode stays the
     100-column default**. Capability-and-size detection picks the mode. This keeps the promise that
     the app runs on a stock terminal, and treats rich as an upgrade for those who can show it.
   - Or **keep 100 columns and accept fewer tiles across**, i.e. smaller/ taller dungeons in rich
     mode. This interacts with the generator (below) and is probably worse, because it changes the
     dungeon, not just its skin.
   Recommend the first: **mode is chosen by capability and size; the layout stays in tile-space and
   is identical between modes; only the rendered width and the minimum differ.**

2. **The generator is unaffected, by construction.** Generation works in **tile coordinates**
   (PLAN §3, §7: cell partitions clamped to `[18x9, 40x15]`, serpentine order, L-corridors). A tile
   grid does not care how many terminal columns a tile paints to. The renderer maps tile `(x, y)` to
   terminal column `(2*x + originX, y + originY)`. So **the dungeon is the same dungeon**; the layout
   invariant (regenerable tile-for-tile from `(seed, cols, rows)`) holds if we store the **tile**
   dimensions, not the terminal columns, in `runs` (a small migration to make the record
   mode-independent). Resize-larger still re-centres; resize-below still overlays.

3. **Walls are the subtle one.** The ACS_ line-drawing set (`ui/walls.py`) draws single-column
   pieces, and a room wall today is a run of single-column `-`/`|` glyphs that join into corners and
   tees. In a 2-column-per-tile grid, a horizontal wall tile must fill **both** its columns to look
   continuous (two `ACS_HLINE`s, or a horizontal run drawn across the doubled span), while a vertical
   wall tile draws its line in one column and pads the other. Corners and tees need care so the join
   still reads. This is real work and the place a naive "just pad everything" falls down: padding a
   horizontal wall with a space breaks the line. So walls need a **wide-aware wall renderer**, not
   the generic pad. Keep ACS as the wall alphabet (it stays portable); the change is how a wall tile
   fills its two columns. An emoji-themed wall (a brick, a hedge) is an alternative that sidesteps
   ACS entirely for rich mode, at the cost of the crisp line look.

4. **The status and hint lines** are flowed text on a single row, so they follow §4 (width-aware),
   not the grid model. A heart for HP or a coin for gold is fine there as long as widths are counted.

### 5.2 What does not change

- The **session** and the **generator**: both are tile-space and glyph-agnostic (§3).
- The **panel** placement math keys off the map's tile width; it needs the doubled column figure at
  paint time, but that is one multiply, not a redesign.
- The **fallback**: a terminal that cannot do wide/emoji (or is too narrow) renders the ASCII theme
  at one column per tile, i.e. exactly today. Nothing regresses.

---

## 6. Portability: this is where it can die

SCREENS.md §9 and CLAUDE.md are blunt about the risk, and it is the same risk, larger:

- **Windows / PDCurses** is the weak link. It is a reimplementation, not ncurses; wide-char and
  astral-plane support is where it is thinnest, and it is already the platform this project has not
  verified. Rich mode must be **opt-in and capability-gated**, and the ASCII fallback must be a
  first-class, tested path, not an afterthought. Assume rich mode is a modern-terminal feature
  (recent Windows Terminal, iTerm2, kitty, foot, GNOME Terminal) and that the classic look is what
  everyone else keeps.
- **Grapheme clusters.** If the map admits ZWJ/skin-tone emoji, `Cell.glyph: str` can still hold
  them (it is a string), but width and cursor advancement must treat the cluster as one 2-column
  unit. Simplest defensive rule for a first cut: **curate a fixed emoji set that is single-codepoint
  (or codepoint + VS16) and width-2**, and forbid ZWJ sequences in the theme, so `glyph` stays "one
  visible thing, two columns". Widen later only with evidence.
- **The CJK ambiguous-width trap still applies** (SCREENS §9.1): the box-drawing chars are
  *Ambiguous*, so a CJK-configured terminal already doubles them. Rich mode does not add CJK
  support; it stays en/nl-scoped. If CJK is ever a target, it collides with both the borders and this
  plan, and needs its own reckoning.

---

## 7. Testing the un-testable-looking

The headless discipline still buys us most of it, because the **content** is theme-independent:

- **Session tests are unchanged.** They assert on the semantic `Frame` (cells, messages, overlays),
  which stays ASCII-first. Emoji are a `ui` concern.
- **`tools/screens.py` grows a width model.** Today it asserts every frame is exactly 100x30 by
  counting characters. A rich mock must measure **display columns** (the same `display_width` helper,
  shared or mirrored), assert the map is `2 * tiles` wide, and assert panel lines fit their column
  budget. The mock stays the evidence; it just learns to weigh glyphs. Keep an ASCII mock and a rich
  mock so both looks are verified, the way en and nl are both verified now.
- **A width-unit test** for `display_width` against known cases (ASCII 1, `é` 1, `€` 1, a CJK char 2,
  a curated emoji 2, a box char 1-in-Western) is the small cheap net that catches the whole class.

---

## 8. Phasing (when it is scheduled)

Each phase is shippable and reversible, and each keeps the ASCII look working the whole way.

- **Phase 1: width-aware panels (§4).** Add `display_width` and a column-counting wrapper; switch
  `windows.py` and the prompt-label advance to columns. No visible change with ASCII content, but
  wide text now wraps correctly. Lowest risk, unlocks emoji in lessons/scrolls.
- **Phase 2: the theme layer (§3), still ASCII glyphs.** Introduce the `ui` theme table and a
  capability check, with only the `ascii` theme populated. Pure plumbing; the golden tests do not
  move.
- **Phase 3: the wide map renderer (§5), ASCII-in-wide.** Render every tile at two columns using
  padded ASCII and a wide-aware wall renderer, behind the capability/size gate, with the tile
  dimensions stored in `runs`. This proves the geometry (minimum size, centring, walls, panel
  placement) before any emoji exist. The look is "spaced ASCII", which is ugly but correct, and that
  is the point: verify the grid, then paint it.
- **Phase 4: the rich theme.** Populate the `rich` theme with a curated, single-codepoint,
  width-2 emoji set for tiles and entities; add the rich screen mock (§11 is the sketch of what
  that mock asserts). Revise CLAUDE.md's "Map glyphs are ASCII" / "Never emoji" rules to "ASCII is
  the portable fallback theme; the rich theme is emoji, gated by capability", and update SCREENS §9.
- **Phase 5 (optional): pack-authored rich glyphs.** Let a pack suggest a theme glyph for its
  objects, still declared alongside a mandatory ASCII fallback, validated against the curated set.

---

## 9. Decisions to make before starting (open questions)

1. **Minimum terminal in rich mode.** Widen the requirement (recommended, §5.1) or shrink the
   dungeon. This is the load-bearing choice; everything else follows.
2. **Emoji width source.** Stdlib `east_asian_width` for a curated set (keeps stdlib-only), or a
   vendored `wcwidth` table for arbitrary emoji (breaks it for one data module). Tied to how open the
   theme is.
3. **Walls in rich mode.** Keep ACS line-drawing widened to two columns (crisp, portable, more
   renderer work), or theme walls as emoji tiles (simpler, less crisp, a real look change).
4. **Who owns the mode switch.** Auto-detect from terminal capability and size, an explicit `--rich`
   flag, or both. Auto with an override is the friendly default.
5. **How curated the emoji set is.** Locked single-codepoint width-2 glyphs (safe, testable) versus
   open ZWJ sequences (expressive, fragile). Start locked.

---

## 10. What stays true regardless

- **The pack format is the portable asset, not the Python** (PLAN §13.5). A pack's map glyphs stay
  an ASCII alphabet with an optional theme hint; the rich look is a rendering choice, so a pack keeps
  working on a classic terminal. Nothing in this plan makes a pack require emoji.
- **The session never learns what a glyph looks like.** Rule 2 holds: the richer look is entirely on
  the `ui` side of `session -> ui`, which is what keeps the golden slice and the headless harness
  valid across both looks.
- **ASCII is never dropped, only demoted to the fallback theme.** The reason the app runs on any
  terminal is the reason to keep it.

---

## 11. Mock-ups: the same screens, enriched

Hand sketches of Phase 4, **not** generated by `tools/screens.py` (that comes when the rich mock is
real). Each frame is the rich twin of a screen already locked in [SCREENS.md](SCREENS.md): same
room, same entities, same moment. The map is **two terminal columns per tile** (§5); narrow glyphs
are padded (`. ` for floor, `# ` for corridor); emoji fill their two columns natively. Walls stay
ACS line-drawing, widened (§5.1). The status line is flowed text (§4), so a coin or heart there is
fine.

These assume a terminal wide enough for rich mode (§5.1); they are vignettes of the map area, not
asserted 100×30 frames. When Phase 4 ships, `tools/screens.py` grows a rich twin of each and
asserts **display columns**, the way SCREENS.md asserts character columns today.

### 11.1 Curated theme (locked set)

| Identity | ASCII today | Rich glyph | Notes |
|---|---|---|---|
| Learner | `@` | 🧑 | Solves SCREENS §8.8 (three `@`s, colour only) |
| Wizard | `@` | 🧙 | Ada, and other wizard keepers |
| Gatekeeper | `@` | 💂 | Grigor's kind |
| Shopkeeper | `@` | 🧔 | Ives |
| Cat | `f` | 🐈 | Default companion |
| Dog | `d` | 🐕 | PETS.md companion choice |
| Money | `$` | 🪙 | Floor stack; auto-collect unchanged |
| Door | `+` | 🚪 | The payoff glyph, still one tile |
| Stairs up / down | `<` `>` | 🔼 🔽 | |
| Coconut half | `(` | 🥥 | Pack object (1.3.0) |
| USB stick | `?` | 💾 | Pack object (1.3.0) |
| Floor / corridor | `.` `#` | `. ` `# ` | Padded ASCII, not emoji |
| Wall | ACS | ACS×2 | Horizontal tile paints `──`; vertical `│ ` |

Single-codepoint, width-2 only (§6, §9.5). No ZWJ, no skin tones. Packs still declare the ASCII
column; the theme upgrades it at paint time (§3).

### 11.2 Arrival on Dlvl 1 — SCREENS §1

Same room, same positions: stairs, Ada at the sealed east wall, George, the kitten trailing. The
east wall is still unbroken. What changes is that Ada is no longer another `@`.

```
Ada the Suspicious does not look up. There is no way out of this room.


    ┌──────────────────────────────────────────┐
    │ . . . . . . . . . . . . . . . . . . . .  │ 
    │ . . 🔼. . . . . . . . . . . . . . . . .  │ 
    │ . . . . . . . . . . . . . . . . . . . .  │ 
    │ . . . . . . . . . . . . . . . . . . . 🧙 │ 
    │ . . . . . . . . . . . . . . . . . . . .  │ 
    │ . . . . . . . 🧑. . . . . . . . . . . .  │ 
    │ . . . . . . 🐈. . . . . . . . . . . . .  │ 
    └──────────────────────────────────────────┘


George the Novice   Dlvl:1  Rooms:0/3  🪙:0  💛12(12)  T:14
Move: arrows    Talk: t    Look: ;    Help: ?    Quit: Q
```

ASCII original (SCREENS §1), for the eye test:

```
    ┌────────────────────┐
    │....................│
    │..<.................│
    │....................│
    │...................@│
    │....................│
    │.......@............│
    │......f.............│
    └────────────────────┘
```

### 11.3 Ada instructs — SCREENS §2

The panel is unchanged in job and placement: beside the room, held height, page break on paragraph
boundaries. Wide glyphs inside lesson prose would consume two of the 69 columns (§4); this frame
keeps the pilot's ASCII prose so the panel geometry matches SCREENS. The map beside it is what
enriched.

```
Ada the Suspicious, wizard, teaches.
                                                 ╔═══════════════════════════════════════════════════════╗
                                                 ║                                                       ║
                                                 ║ Recognising a Phish                                   ║
    ┌──────────────────────────────────────────┐ ║                                                       ║
    │ . . . . . . . . . . . . . . . . . . . .  │ ║ Ada does not look up. She is holding a letter         ║
    │ . . 🔼. . . . . . . . . . . . . . . . .  │ ║ to the lamp, and she keeps holding it while           ║
    │ . . . . . . . . . . . . . . . . . . . .  │ ║ she talks.                                            ║
    │ . . . . . . . . . . . . . . . . . . 🧑🧙 │ ║                                                       ║
    │ . . . . . . . . . . . . . . . . 🐈. . .  │ ║ "Everyone wants me to teach them the tell,"           ║
    │ . . . . . . . . . . . . . . . . . . . .  │ ║ she says. "The spelling mistake. The odd              ║
    │ . . . . . . . . . . . . . . . . . . . .  │ ║ greeting. They want a checklist so they can           ║
    └──────────────────────────────────────────┘ ║ stop thinking."                                       ║
                                                 ║                                                       ║
                                                 ║ --More--                              (page 1 of 4)   ║
                                                 ╚═══════════════════════════════════════════════════════╝
George the Novice   Dlvl:1  Rooms:0/3  🪙:0  💛12(12)  T:14
Next page: space        Back: -            Put it down: Esc
```


### 11.4 The door appears — SCREENS §5

The design's payoff is still one tile. In ASCII it is `+`; here it is 🚪. Same finding as SCREENS
§8.1, just readable without the hint line explaining "the door is a +".

```
The wall grinds. Where there was stone, there is a door.


    ┌──────────────────────────────────────────┐
    │ . . . . . . . . . . . . . . . . . . . .  │
    │ . . 🔼. . . . . . . . . . . . . . . . .  │
    │ . . . . . . . . . . . . . . . . . . . .  │
    │ . . . . . . . . . . . . . . 🐈🧑. . . 🧙 🚪
    │ . . . . . . . . . . . . . . . . . . . .  │
    │ . . . . . . . . . . . . . . . . . . . .  │
    │ . . . . . . . . . . . . . . . . . . . .  │
    └──────────────────────────────────────────┘


George the Novice   Dlvl:1  Rooms:1/3  🪙:0  💛12(12)  T:14
Move: arrows    The door is open. Walk through it.
```

### 11.5 Two rooms and a corridor — SCREENS §7

The screen that answers "does it feel like a dungeon?". Room 1 remembered (Ada still there,
re-instructs forever); the L-corridor; room 2 lit with Grigor. Keepers are different glyphs;
colour is no longer the only tell.

```
Grigor, Who Was Impersonated, looks up. There are two nameplates on his desk.


                                                           ┌────────────────────────────────────────────────┐
    ┌──────────────────────────────────────────┐           │ . . . . . . . . . . . . . . . . . . . . . . .  │
    │ . . . . . . . . . . . . . . . . . . . .  │           │ . . . . . . . . . . . . . . . . . . . . . . .  │
    │ . . 🔼. . . . . . . . . . . . . . . . .  │           │ . . . . . . . . . . . . . . . . . . . . . . .  │
    │ . . . . . . . . . . . . . . . . . . . .  │     ######│ . . . . . . . . . . . . . . . . . . . . . 🧑💂 │
    │ . . . . . . . . . . . . . . . . . . . 🧙 🚪#####     │ . . . . . . . . . . . . . . . . . . . 🐈. . .  │
    │ . . . . . . . . . . . . . . . . . . . .  │           │ . . . . . . . . . . . . . . . . . . . . . . .  │
    │ . . . . . . . . . . . . . . . . . . . .  │           │ . . . . . . . . . . . . . . . . . . . . . . .  │
    │ . . . . . . . . . . . . . . . . . . . .  │           └────────────────────────────────────────────────┘
    └──────────────────────────────────────────┘
George the Novice   Dlvl:1  Rooms:1/3  🪙:0  💛12(12)  T:14
Talk to Grigor: t          Move: arrows              Help: ?
```

At two columns per tile this composite is already past 100 columns, which is why rich mode wants a
wider minimum (§5.1) rather than a smaller dungeon: the tile layout is identical to SCREENS §7; only
the paint is wider.

### 11.6 The coin reward — SCREENS §11

Ada's door is open; the scaled reward sits **in the room, away from the exit** (OBJECTS.md, the
play-testing placement). In ASCII it is `$`; here it glints. `🪙:0` until the learner walks onto
it — same pull to explore.

```
Ada the Suspicious leaves 20 coins on the floor.


    ┌──────────────────────────────────────────┐
    │ . . . . . . . . . . . . . . . . . . . .  │
    │ . . 🔼. . . . . . . . . . . . . . . . .  │
    │ . . . . . . . . . . . . . . . . . . . .  │
    │ . . . . . . . . . . . . . . . . . 🧑. 🧙 🚪
    │ . . . . . . . . . . . . . . . . 🐈. . .  │
    │ . . . 🪙. . . . . . . . . . . . . . . .  │
    │ . . . . . . . . . . . . . . . . . . . .  │
    └──────────────────────────────────────────┘


George the Novice   Dlvl:1  Rooms:1/3  🪙:0  💛12(12)  T:14
Move: arrows    Coins collect when you step on them.
```

**The race (PETS.md), same room a moment later.** A dog companion steps toward the stack. First to
the tile wins; this is why the reward is in the room and not on the way out.

```
Rex bolts for the coins.


    ┌──────────────────────────────────────────┐
    │ . . . . . . . . . . . . . . . . . . . .  │ 
    │ . . 🔼. . . . . . . . . . . . . . . . .  │ 
    │ . . . . . . . . . . . . . . . . . . . .  │ 
    │ . . . . . . . . . . . . . . . . . . . 🧙 🚪
    │ . . . . . . . 🧑. . . . . . . . . . . .  │ 
    │ . . . 🪙🐕. . . . . . . . . . . . . . .  │ 
    │ . . . . . . . . . . . . . . . . . . . .  │ 
    └──────────────────────────────────────────┘


George the Novice   Dlvl:1  Rooms:1/3  🪙:0  💛12(12)  T:52
Wait: space    Move: arrows    Rex will bring the coins back
```

### 11.7 Pack objects on the floor — beyond SCREENS §11

SCREENS §11's pack holds only coins today. Pack-authored objects (OBJECTS.md 1.3.0) use the same
theme upgrade: ASCII class char in the pack, emoji at paint time. A coconut half and a found USB
on the floor of Ada's room:

```
You notice a coconut half and a USB stick on the floor.


    ┌──────────────────────────────────────────┐
    │ . . . . . . . . . . . . . . . . . . . .  │ 
    │ . . 🔼. . . . . . . . . . . . . . . . .  │ 
    │ . . . . . 🥥. . . . . . . . . . . . . .  │ 
    │ . . . . . . . . . . . . 💾. . . . . . 🧙 │ 
    │ . . . . . . . . . . . . . . . . . . . .  │ 
    │ . . . . . . . 🧑. . . . . . . . . . . .  │ 
    │ . . . . . . 🐈. . . . . . . . . . . . .  │ 
    └──────────────────────────────────────────┘


George the Novice   Dlvl:1  Rooms:0/3  🪙:0  💛12(12)  T:20
Move: arrows    Pick up: ,    Pack: i
```

**Your pack (`i`), enriched.** Same panel job as SCREENS §11; the glyphs in the list match the
floor.

```
You look through your pack.


    ┌──────────────────────────────────────────┐
    │ . . . . . . . . . . . . . . . . . . . .  │ 
    │ . . 🔼. . . . . . . . . . . . . . . . .  │          ╔══════════════════════════════════════════╗
    │ . . . . . . . . . . . . . . . . . . . .  │          ║                                          ║
    │ . . . . . . . . . . . . . . . . . . 🧑🧙 │          ║ Your pack                                ║
    │ . . . . . . . . . . . . . . . . 🐈. . .  │          ║                                          ║
    │ . . . . . . . . . . . . . . . . . . . .  │          ║ 🪙  70 coins                             ║
    │ . . . . . . . . . . . . . . . . . . . .  │          ║ 🥥  coconut half (2)                     ║
    └──────────────────────────────────────────┘          ║ 💾  USB stick                            ║
                                                          ║                                          ║
                                                          ╚══════════════════════════════════════════╝
George the Novice   Dlvl:1  Rooms:2/3  🪙:70  💛12(12)  T:52
Put it away: Esc        Drop: d              Move: arrows
```

### 11.8 What the sketches already show

1. **Keeper identity is fixed without colour.** SCREENS §8.8's three-`@` problem goes away the
   moment the theme distinguishes learner / wizard / gatekeeper. That alone may be worth Phase 4.
2. **The door payoff is still one tile**, just a legible one. Do not expect emoji to solve SCREENS
   §8.1's "is one glyph enough?"; they only make the glyph self-explanatory.
3. **Money and objects read as things.** A `🪙` across the room pulls harder than a `$`, and a pack
   list that shows 🥥 next to the name matches the floor. The session still emits `$` / `(`; only
   paint changes.
4. **Width is real.** The two-room frame breaks 100 columns at two columns per tile. That is
   evidence for "widen the rich minimum", not "shrink the dungeon" (§5.1, §9.1).
5. **Panels barely move.** Lesson prose, REPELLED, the pack, the drop field: same boxes, width-aware
   wrap. The map is the expensive surface; the sketches keep proving that split (§2).
