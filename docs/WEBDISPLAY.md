# Web display: a browser look for Delve

Future-reference design note, not scheduled work. Companion to [DISPLAY.md](DISPLAY.md)
(terminal rich theme) and [SCREENS.md](SCREENS.md) (locked ASCII frames). This plan is about
**how Delve could look in a browser**: the same rooms, keepers, pets, money and panels, painted
with CSS tiles and emoji rather than a character grid.

**Open the mock-ups:** [webdisplay/index.html](webdisplay/index.html) (double-click or open in a
browser). They are static HTML, not wired to the engine.

---

## 0. Read PLAN §13.5 first

A web Delve is **not an architecture excuse**. PLAN §13.5 is blunt:

- The durable asset is the **pack format**, not the Python. A TypeScript session that eats the same
  packs is legitimate; bolting a browser onto Python is the instinct, not the requirement.
- **Do not build `session/` "for the web".** Build it for the tests. A second frontend is a side
  effect of rule 2, not a goal.
- The question that would *force* a served build is auditability of scrolls (server-held state and
  grades), not "should training look nicer in Chrome."
- **React is the wrong reflex for the dungeon.** The map is a tile grid, a text overlay, and a
  menu: the least component-shaped UI there is. A grid of cells, a keydown handler, and a colour
  theme. The trophy case is app-shaped; the dungeon is the product.

This file plans the **visual layer** and keeps that boundary. It does not schedule a rewrite, an
SSO stack, or a React SPA.

---

## 1. Why the web is a different (easier) display problem

[DISPLAY.md](DISPLAY.md) spends most of its pages on one fact: in a terminal, emoji are
double-width and break a one-cell-one-column grid. The web **does not have that problem**.

| Terminal (DISPLAY.md) | Browser (this plan) |
|---|---|
| One char = one column (or two, and geometry breaks) | One **tile** = one CSS grid cell of fixed `px`/`rem` |
| Emoji force a 2-column-per-tile mode and a wider minimum | Emoji sit centred in a square cell; width is the cell, not the glyph |
| ACS line-drawing, PDCurses, ambiguous-width traps | Borders are CSS; fonts and emoji are the platform's problem |
| 100×30 hard floor (Windows Terminal default) | Responsive shell; map scales; panel reflows |
| `textwrap` counts characters | CSS wraps on pixels; `break-word` / `overflow-wrap` as needed |

So the terminal rich theme and the web look **share a vocabulary** (the curated emoji set in
DISPLAY §11.1) and **diverge on geometry**. On the web, Phase 4 of DISPLAY (emoji on the map) is
cheap; the expensive terminal work (wide ACS walls, minimum-size gate) does not transfer.

The web's hard problems are elsewhere: input (keyboard + optional on-screen), layout of panel
beside room on a phone, and (only if served) identity. This document focuses on **visual display**.

---

## 2. What stays true from the terminal product

Steal these without renegotiating them:

1. **A lesson is a panel beside the room, never a full-screen takeover.** The learner must see
   themselves, the keeper, and the room while the keeper talks (SCREENS §8.2, PLAN §3).
2. **Message / map / status / hints** — the four-band layout. The hint line is the safety net, not
   decoration.
3. **Session emits Frames; UI only paints.** A web client consumes the same `Command → Frame`
   contract (or a JSON projection of it). It never grades, never opens doors, never imports
   `engine`.
4. **Semantic cells, theme at paint time.** Session keeps ASCII-first identities (`$`, `@`, `f`);
   the web theme maps them to emoji or SVG. Packs never ship raw presentation glyphs for the map
   (DISPLAY §3).
5. **Passing is final; REPELLED is not death; sealed doors are structural.** Tone and rules do not
   change because the pixels are prettier.

---

## 3. Visual direction

Not a second NetHack port in a `<pre>`, and not a generic "AI dashboard." The mock-ups aim for:

- **Dungeon atmosphere:** deep slate ground, warm candlelight accents, stone walls as tiles — not
  purple gradients, not cream-and-serif marketing, not a card grid.
- **Readable training:** lesson panels use a calm serif for prose; the map and status stay
  utilitarian. The product is compliance training that happens to be a dungeon.
- **Emoji as the map alphabet** (same curated set as DISPLAY §11.1): 🧑 learner, 🧙 wizard, 💂
  gatekeeper, 🧔 shopkeeper, 🐈/🐕 pet, 🪙 money, 🚪 door, 🔼/🔽 stairs, 🥥/💾 pack objects.
- **One composition per screen:** map + optional panel + chrome. No stat strips, badge clusters, or
  floating promo chips over the dungeon.

Colour tokens used in the mock-ups:

| Token | Role |
|---|---|
| `#12161c` | Page ground |
| `#1a1f28` | Floor tile |
| `#2a3140` | Wall / stone |
| `#e8a84a` | Amber accent (focus, stairs glow) |
| `#f0d060` | Gold (coins, wealth) |
| `#e85d6a` | HP |
| `#8eb4c8` | Panel cool edge / quotes |
| `#c8d0dc` | Primary text |

---

## 4. Layout model (CSS, not columns)

```
┌─────────────────────────────────────────────────────────────┐
│  message line                                               │
├─────────────────────────────────┬───────────────────────────┤
│                                 │                           │
│  map (CSS grid of tiles)        │  panel (lesson / exam /   │
│  fixed tile size, e.g. 28×28)   │  pack / REPELLED)         │
│                                 │                           │
├─────────────────────────────────┴───────────────────────────┤
│  status: name · Dlvl · Rooms · 🪙 · 💛 · T                  │
│  hints: contextual keys                                     │
└─────────────────────────────────────────────────────────────┘
```

- **Map:** `display: grid` of `.tile` cells. Each cell has a role class (`floor`, `wall`, `door`,
  `entity`) and optional dim/lit. Glyph is a child span (emoji) or a background for walls.
- **Panel:** flows beside the room when there is space; stacks under the map on narrow viewports
  **only if** the map still shows the learner and the keeper (the SCREENS undecided placement
  question, answered here as: shrink tile size before covering the room).
- **Status / hints:** flex rows; emoji for gold and HP are fine (flowed text, same as DISPLAY §4).
- **No character-cell arithmetic.** Tile size is a CSS variable; zooming the map is changing that
  variable, not re-wrapping a string.

Minimum desktop mock: ~960px wide so a 20-tile room at 28px still leaves panel room. Mobile is a
later pass; the mock-ups target the desktop composition SCREENS already proved.

---

## 5. Architecture sketch (when it is real)

Keep PLAN §13.5's options honest; pick only when scheduling:

| Approach | When it fits | Visual implication |
|---|---|---|
| **A. Static / local web UI over Python session** | Play in browser, same process or local server; still trust-based identity | Fastest path to these mock-ups becoming paint; Frame JSON over WebSocket or HTTP |
| **B. Served build** | Scrolls must mean something to an auditor | Same paint; server holds run state and grades |
| **C. Independent TS session** | Long-term second client; pack format only shared | Same paint; grader-drift risk if both grade in production |

For all three, the **display pipeline** is the same:

```
Frame (semantic cells + overlays)
        │
        ▼
  web theme (identity → emoji / CSS class)
        │
        ▼
  DOM grid + panel + chrome
```

That is DISPLAY §3's theme layer with a different backend. Terminal `ascii` / `rich` and web
`web-emoji` are three themes over one Frame.

**Input:** map keys as today (arrows, `t`, `,`, `d`, `i`, `>`, digits in exams). Optional
click-to-talk on an adjacent keeper and click-to-step are web affordances; they must emit the same
`Command`s. Do not invent a parallel verb set.

**What not to build in v1 of a web UI:** React component tree for every tile, canvas/WebGL, asset
packs of sprite sheets (emoji are enough until evidence says otherwise), a design system of cards.

---

## 6. Phasing (visual work only)

1. **Mock-ups (this folder).** Static HTML screens parallel to SCREENS / DISPLAY §11. Done when the
   look is agreed.
2. **Frame JSON fixture.** Dump a real `Frame` from the headless harness to JSON; paint it with the
   same CSS as the mocks. Proves the theme mapping without a network.
3. **Local paint loop.** Thin adapter: keydown → `Command` → existing Python `session.apply` →
   Frame → DOM. Still not "Delve on the internet."
4. **Responsive panel rules.** Codify when the panel sits right / left / below; keep learner+keeper
   visible (SCREENS §8.2 open question).
5. **Only if product asks:** served hosting, SSO, or a TS session. Out of scope for display.

---

## 7. Mock-up index

All screens live in [webdisplay/index.html](webdisplay/index.html). Switch with the top tabs.

| Tab | Parallel | What to look at |
|---|---|---|
| Arrival | SCREENS §1 / DISPLAY §11.2 | Sealed room; distinct 🧑 / 🧙 / 🐈 |
| Lesson | SCREENS §2 / DISPLAY §11.3 | Panel beside the room; map stays visible |
| Exam | SCREENS §3 | Numbered options; keeper still on the map |
| Door | SCREENS §5 / DISPLAY §11.4 | 🚪 as the one-tile payoff |
| Coins | SCREENS §11 / DISPLAY §11.6 | 🪙 in-room reward; pet nearby |
| Dungeon | SCREENS §7 / DISPLAY §11.5 | Two rooms, corridor, 🧙 vs 💂 |
| Pack | SCREENS §11 / DISPLAY §11.7 | Inventory panel with emoji labels |
| Repelled | SCREENS §6 | Tone: pause, not defeat |

These are **hand-authored HTML**, not generated from `tools/screens.py`. If the web look ships, a
generator or a Frame-driven painter should replace them the way SCREENS.md is generated today —
static art is for deciding, not for regressing.

---

## 8. Decisions to make before building

1. **Emoji vs SVG sprites.** Mocks use emoji. If a platform renders them poorly, swap the theme
   table to SVG without touching Frames.
2. **Click vs keyboard-only.** Keyboard must work; click is optional sugar.
3. **Approach A/B/C** (§5) — product decision, not a CSS one.
4. **Mobile.** Defer until desktop composition is loved; do not shrink the dungeon to fit a phone
   at the cost of the panel-beside-room rule.

---

## 9. What stays true regardless

- **Packs stay presentation-agnostic.** ASCII object-class chars in content; themes upgrade them.
- **The session never learns what a glyph looks like.** Rule 2 holds for `web/` the same way it
  holds for `ui/`.
- **The terminal app is not deprecated by this plan.** A browser look is another theme surface.
  DISPLAY.md's ASCII fallback and this file's emoji grid can coexist.
- **PLAN §13.5 is not reopened by prettier tiles.** Build display for clarity and access; reopen
  served identity only for auditability.
