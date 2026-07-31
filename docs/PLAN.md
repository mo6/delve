# Delve — Project Plan

> A training application that wears NetHack's clothes. Learners descend a dungeon; keepers
> teach a topic, then examine the learner on it. Passing an examination makes a door appear
> in the wall, opening the way to the next room. Reaching the final chamber awards a scroll,
> collected across many training dungeons over time.

*Named for both meanings: dungeon delving, and delving into a subject.*

---

## 1. The shape of the problem

This project is two applications wearing one coat:

- **A roguelike** — spatial, exploratory, emergent, driven by the player wandering around.
- **An assessment engine** — linear, stateful, verifiable, driven by a content author's script.

These pull in opposite directions. If they bleed into each other, content authors end up
writing game code and the engine ends up hard-coding lesson logic. Every structural
decision below exists to keep them apart.

**The load-bearing idea:** the dungeon is a *shell* that gates a *content pack*. They
communicate through one narrow interface:

```
    ┌──────────────────┐                      ┌────────────────────┐
    │  DUNGEON SHELL   │                      │   CONTENT PACK     │
    │                  │                      │                    │
    │  maps, movement  │   Gate.state ==      │  lessons,          │
    │  rendering, pet  │  ───UNLOCKED?───▶    │  questions,        │
    │  HP, doors       │   ◀──HP penalty──    │  explanations      │
    │  items, scrolls  │                      │                    │
    └──────────────────┘                      └────────────────────┘
         knows nothing                             knows nothing
       about phishing                          about doors or maps
```

The shell never parses a question. The pack never places a door. `Gate` is the only thing
that touches both, and it is deliberately small.

**And a third thing, which is not an application at all:** the screen. Neither of the two above
should know what draws it — not because the screen might change, but because a loop that lives
inside curses can only be tested through curses. §4 keeps it out.

---

## 2. The three-tier structure

The single most important thing to keep straight:

```
  PACK        a training           →  a dungeon
   └── CHAPTER   a module          →  one dungeon floor (Dlvl)
        └── ROOM    one lesson     →  one room + one keeper + one gate
```

| Tier | Is | Connected by | Authored as |
|---|---|---|---|
| **Pack** | The whole training | — | A folder |
| **Chapter** | A module or theme | **Stairs** (`>`) | A subfolder |
| **Room** | One lesson + its examination | **Doors** that appear | One Markdown file |

**Doors carry you within a chapter. Stairs carry you between chapters.** A single-chapter
training therefore has no stairs at all — you walk from room to room and finish in the
scroll chamber.

**Why this matters:** an earlier draft of this plan conflated "dungeon floor" with "one
lesson", which burned an entire 80×21 floor to hold one keeper. Real NetHack floors have
six or eight rooms. This structure restores that shape, and it means the author's chapter
boundaries are *semantic* — a chapter break is a break in the material, chosen by a human,
not by a packing algorithm running out of grid.

### Sealed doors, and the subsystem they delete

A room's exit is a **sealed wall**. Pass the keeper's examination and a door *appears* in
the stone.

This is not just flavour — it removes the hardest constraint in the design. The obvious
failure mode for the whole premise is a learner walking past the lesson to the exit. An
earlier draft prevented this with a flood-fill invariant: delete the keeper's tile, verify
the entrance can no longer reach the exit, reroll the map if it fails.

**If the door does not exist until you pass, there is nothing to walk past.** The invariant
becomes structural rather than validated. The generator loses a reroll loop, the validator
loses its hardest rule, and a hand-drawn map cannot accidentally break it.

---

## 3. Settled decisions

| Decision | Choice | Why |
|---|---|---|
| Language / runtime | Python 3.14 (Homebrew) in a venv | Installed and verified; `match`, modern typing |
| Platforms | **macOS, Linux, Windows** | All three are first-class targets |
| TUI | `curses` — stdlib on macOS/Linux, `windows-curses` on Windows | One API everywhere; authentic; verified to have cp314 wheels |
| Loop location | **Headless `session` core**; `ui` maps input → `Command` and paints a `Frame` | A loop inside curses can only be tested through a pty. This is a testing decision |
| Save / resume | Run **snapshot** in `runs` | 12 rooms is more than one sitting. Falls out of the seeded layout for almost free |
| Colours | **16 only** | The floor on all three platforms — and NetHack's own palette |
| Glyphs | **ASCII only** (`-` `\|` `.` `#` `@` `<` `>` `+`) | Identical on every platform; Unicode box-drawing is a per-platform fight |
| Terminal | **100×30 minimum, adaptive above** | Fits Windows Terminal's 120×30 default exactly — no resize on first run |
| Authoring format | Markdown-first | Readability was the stated top constraint |
| Unit of authoring | Room = file, chapter = folder | Every lesson file stays short; structure visible in the tree |
| Question syntax | GitHub task-list checkboxes | Renders on GitHub, authorable by anyone |
| Question type | Inferred from **option count** | 2 = assertion, 3+ = choice. Locale-independent — see below |
| Languages | English + Dutch, locale subtree per pack | Identical file trees; only content translates |
| Tutorial | Engine-provided **Dlvl 0**, skippable, never scored | Teaches the interface, which is identical across every pack |
| Progression | Sealed doors within a chapter, stairs between | Makes the gate structural, not policed |
| Room graph | Linear chain (v1) | Zero authoring overhead; branching stays additive |
| Maps | **Generated only** in v1 | Authors write lessons, not mazes; adapts to terminal |
| Backtracking | Free, through any door already earned | Re-reading a lesson must never be punished |
| Chapter splitting | Author decides; validator warns on overflow | A packing algorithm can't pick a meaningful break |
| Map reveal | Current room lit, visited dimmed, unexplored black | NetHack default; scope stays legible via `Rooms: n/m` |
| Failure model | Roguelike stakes (HP cost, door stays sealed) | Answers should have weight |
| Question types v1 | Multiple choice, true/false assertion | Both map onto native NetHack UI idioms |
| Free text | Deferred to Phase 2, local LLM grader | Syntax reserved now for forward compatibility |
| Pet | Hint companion, consulting costs gate score | Gives the companion pedagogical weight |
| Endgame | Final chamber, scroll on a pedestal | The reward is an object you collected, not a popup |
| Progress store | SQLite from day one | Multi-user hall of fame later is a view, not a migration |
| Pilot pack | Security awareness / compliance | Highest upside genre; assertions fit it natively |

### Notes on the consequential ones

**Why `curses` and not Textual.** Textual would give prettier lesson panels for free. But the
lesson panel is the one part we can afford to hand-build, and the dungeon grid is the part
that has to feel exactly right. NetHack itself renders through curses. The cost is a small
window/menu layer we write once (`ui/windows.py`) and reuse everywhere.

(Textual would also put the loop back inside a UI framework, which is the thing §4 is avoiding.)

**Why curses still works with Windows in scope.** Python's `curses` is stdlib on macOS and
Linux but *not* on Windows, where it needs `windows-curses` (a PDCurses wrapper). That
package historically lags new Python releases, which would be a real blocker on 3.14 — so it
was checked rather than assumed: **windows-curses 2.4.2 ships cp314 wheels.** The dependency
is platform-conditional and invisible on Unix:

```toml
dependencies = ["windows-curses; sys_platform == 'win32'"]
```

Two constraints follow, and both happen to be free because we wanted them anyway:

- **16 colours.** macOS ships Apple's ncurses 6.0 from 2015 (`init_extended_color` is
  absent); Windows gets PDCurses. 16 is the common floor — and it's NetHack's palette, so
  the authentic choice and the portable one are the same choice.
- **ASCII glyphs.** `-|.#@<>+` render identically on all three. Unicode box-drawing would be
  a per-platform argument about fonts and code pages, for a game whose whole aesthetic is
  ASCII anyway.

The real Windows risk isn't rendering, it's **behavioural drift**: PDCurses is a
reimplementation, not ncurses, so resize handling, key codes, and timing differ in small
ways. Mitigation is to keep every curses call behind `ui/`, and to test on Windows at M1 — not
at M7, when it's expensive.

Note this is the *same* boundary the paragraph below asks for. "Isolate curses so PDCurses drift
is containable" and "isolate curses so the loop is testable" are one line drawn in one place, and
either reason pays for it alone.

**Why the loop is not in the UI.** An earlier draft put the main loop in `ui/app.py` and had
`ui` import `engine` directly to render the map. That is the ordinary shape for a curses game
and it is wrong here, for a reason that has nothing to do with the web: **a loop that lives
inside curses can only be tested through curses.** Every test of "walk to the keeper, answer
wrong, lose 3 HP, answer right, door appears" would need a pty, a fake terminal, and a screen
scrape. That is the kind of test suite people quietly stop running.

So the loop moves down into a `session` package that never imports curses, and `ui` becomes what
it should always have been: something that turns a keypress into a `Command` and a `Frame` into
pixels. Tests then play a whole run as a list of commands and assert on view models. M1's
headless harness is that, and it exists at M1 because M2 through M7 all lean on it — this is the
project whose central bet is unproven (§12), so the loop being cheap to iterate on is not a
luxury.

The cost today is a package boundary drawn before any code exists to move. That it would also
make a second frontend tractable is a side effect, and **not a reason** — read §13.5 before
treating it as one.

**Why Markdown-first and not YAML.** YAML-with-Markdown-attached splits every lesson across
two files in two syntaxes. A trainer writing a lesson should open one file and read it top
to bottom: prose, then questions. Frontmatter stays metadata-only, never content.

**Why linear rooms in v1.** A chain needs no graph authoring, no cycle detection, and no
layout solver — room order is file order. It also makes the unfolding map a legible progress
bar. Branching (`requires:`, optional rooms) is purely additive later; packs written against
a chain keep working.

**Why generated maps only, and no hand-drawn option.** An earlier draft offered a
hand-drawn chapter map as the "high ceiling for craft". It has to go, because it fights both
stated goals at once. It fights *ease of authoring*: nobody writing security onboarding wants
to draw an ASCII maze, and the feature drags in a map legend, digit-to-room binding,
flood-filled room extents, and a set of validation rules — a whole subsystem serving almost
nobody. And it fights *adaptivity*: a hand-drawn map is a fixed rectangle, so the moment one
exists, every terminal is that map's size forever. Generation is what lets a floor breathe on
a 200-column display and still fit at 100×30.

It's deferred, not deleted — if a set-piece floor is ever genuinely wanted, a drawn map can
return as a fixed-size chapter letterboxed on larger terminals. Nothing in the design blocks
that. It just isn't worth its weight in v1.

**Why 100×30 and not NetHack's 80×24.** NetHack's map is 80×21 because a VT100 was 80×24. That
constraint is forty years dead, and inheriting it would cost real content space.

An earlier version of this paragraph said the reason was that *"a lesson window at 100 columns is
a meaningfully better reading surface than one at 80"*. **The screen mock-ups disproved that**
([SCREENS.md](SCREENS.md) §8.5): the lesson panel is 69 columns of prose, narrower than 80, so
that argument died the moment the panel stopped being a full-screen takeover. The decision
survives on a better reason:

> **100 columns is what lets a readable lesson panel sit *beside* a visible room instead of on
> top of it.** At 80 the panel and the dungeon cannot coexist and the lesson becomes a
> full-screen takeover, which is a slide deck with extra steps. The whole premise is that the
> learner is in a *place*; the terminal minimum is what keeps the place on screen while the
> keeper talks.

An earlier draft said 100×**40**, justified as "the smallest size safely below any modern
default." That was simply false. Windows Terminal defaults to 120×**30** and macOS Terminal to
80×24, so 100×40 would have demanded "please resize your terminal" on first launch from
essentially every learner — the worst possible place to put friction, in an app most people run
exactly once, and whose audience is not developers.

100×30 fits Windows Terminal's default exactly, and still yields a 100×27 map against NetHack's
80×21. Above the minimum the floor uses what's there, up to a cap (see §7).

**Why type inference by option count.** The format originally defined an assertion as "exactly
two options, `True` then `False`". Writing the Dutch pack broke it immediately: the options are
`Waar` / `Niet waar`, and the validator rejected them. English was baked into the format and it
took a second language ten minutes to find. The rule is now **2 options = assertion, 3+ =
multiple choice**, labels are whatever the author wrote, and the engine renders a two-way prompt
using those labels. Simpler than what it replaced, and it has no opinion about language.

**Why SQLite before we need it.** The hall of fame is explicitly a later phase, but
retrofitting multi-user onto JSON save files means rewriting persistence. A SQLite file with
a one-row `users` table costs nothing today and makes Phase 3 additive.

---

## 4. Architecture

```
delve/
├── engine/            The roguelike. Knows nothing about training.
│   ├── world.py         Dungeon, Chapter, Room, Tile
│   ├── entities.py      Entity, Actor, Player, Pet, Keeper, Item
│   ├── actions.py       Movement, interaction, turn resolution
│   ├── layout.py        Chapter layout: place rooms, carve corridors
│   ├── vision.py        Lit rooms, discovered tiles, dimming
│   └── rng.py           Seeded RNG (reproducible runs)
│
├── content/           The pack format. Knows nothing about rendering.
│   ├── pack.py          Pack, Chapter manifest, Room
│   ├── parser.py        Markdown → lesson + questions
│   ├── markup.py        Markdown → token stream (no display types)
│   ├── schema.py        Pydantic validation
│   └── errors.py        Author-facing errors with file:line
│
├── assess/            The examination. Knows nothing about doors.
│   ├── question.py      Question, MCQ, Assertion  (FreeText → Phase 2)
│   ├── grader.py        Grader protocol + MCQGrader, AssertionGrader
│   └── examination.py   Examination: attempts, scoring, hints, penalties
│
├── gate.py            The seam. The ONLY module that knows both sides.
│
├── session/           The application. Headless: no curses, no HTTP, no I/O.
│   ├── run.py           RunState; apply(Command) → list[Event]
│   ├── commands.py      Move, Talk, Answer, Confirm, Consult, Descend, Dismiss, Quit
│   ├── views.py         Frame: MapView, StatusView, MenuView, TextView, PromptView
│   └── snapshot.py      RunState ⇄ serialisable dict
│
├── ui/                curses. Paints a Frame, emits a Command. That is the whole job.
│   ├── app.py           Input loop: key → Command → Frame → draw
│   ├── render.py        Map + status + message lines
│   ├── windows.py       NetHack-style menu / text / prompt windows
│   ├── attrs.py         Token stream → curses attributes
│   └── keys.py          Keymap (arrows)
│
├── progress/          Persistence.
│   ├── store.py         Store protocol + SQLiteStore
│   ├── models.py        User, Run, RoomResult, Scroll
│   └── scrolls.py       Award logic, trophy case
│
└── __main__.py        Entry point
```

**Dependency rule:** arrows point one way only.

```
  ui ──▶ session ──▶ gate ──▶ assess
            │         │
            │         ├────▶ content
            │         └────▶ progress
            └────▶ engine ◀── gate
```

Two rules, and the second is new:

1. **`engine` imports nothing from `content`, `assess`, `session`, or `ui`.** As before.
2. **`ui` imports `session` and nothing else.** Not `engine`, not `content`. And nothing outside
   `ui/` imports `curses`. If `ui/render.py` needs `import engine.world` to draw a wall, the view
   model is missing a field — add the field, don't add the import.

Rule 2 is mechanically checkable (`ruff`'s banned-import rules, or twenty lines of `ast` in a
test), and it should be checked, because it erodes silently under deadline: one direct import to
save five minutes and the loop is back inside curses, untestable, and nobody notices until the
tests they didn't write don't catch something.

### Commands and Frames

The entire frontend contract, and small on purpose:

```python
# session/commands.py — everything a learner can do.
Move(dir) | Talk | Answer(option_id) | Confirm(yes) | Consult | Descend | Ascend | Dismiss | Quit

# session/views.py — everything the UI needs, and nothing it doesn't.
Cell        glyph: str, colour: Colour, dim: bool
MapView     cols, rows, cells: list[list[Cell]]
StatusView  name, dlvl, rooms_done, rooms_total, gold, hp, max_hp, turn
TextView    title, body: list[Token]              the lesson, or the scroll
MenuView    prompt, items: list[MenuItem]         a question, options already shuffled
PromptView  text, choices: list[str]              [yn], or an assertion's two labels
Frame       map, status, messages: list[str], overlay: TextView|MenuView|PromptView|None
```

`session.apply(command) -> Frame`. That's the API. Three properties of it are load-bearing:

- **No display types cross the line.** `Colour` is one of sixteen names, not a curses attribute.
  `Token` is `Bold("...")`, not `A_BOLD`. A test asserting on a `Frame` should never import
  curses to read it.
- **The core does not model presentation state.** No scroll offset, no `--More--`, no cursor.
  `TextView` hands over the whole lesson and `ui` paginates it. The moment the core knows a
  lesson is "scrolled to line 12", asserting on a `Frame` means asserting on a screen.
- **Nothing blocks.** `apply` returns a `Frame`; it never waits for input. Delve is turn-based
  with no tick and no real-time element, so the loop is literally
  `while True: frame = session.apply(read_command())`. That's what lets a test supply the
  commands from a list instead of a keyboard, and it's why nothing here needs async.

A fourth, cheap and worth having: **a `MenuView` carries the options, never which one is
correct** — the explanation enters a `Frame` only after an answer is submitted. This buys no
security today (`packs/` is Markdown on the learner's own disk with `- [x]` marking the answer,
so local Delve is fully cheatable and that's fine — §10 is already trust-based). It's here
because a view model holding data the view must not show is a smell, and because it's free.

### Why `assess.GateSession` is now `assess.Examination`

Not cosmetic. `assess` is specified as knowing nothing about doors, and the old name put "gate"
in the one package forbidden to have the concept. It grades an examination; the *gate* decides
what an examination result means. Renamed before it teaches anyone the wrong boundary.

---

## 5. Object model

```
Entity                      position, glyph, colour, name
├── Actor                   + hp, max_hp, act()
│   ├── Player              + inventory, xp, consult_pet()
│   ├── Pet                 + follow(), hint_for(question)
│   └── Keeper (abstract)   + greet(), instruct(), examine()
│       ├── Wizard              scholarly; long lessons
│       ├── Shopkeeper          transactional; "knowledge for gold"
│       └── Gatekeeper          terse; guards a specific door
└── Item
    ├── Scroll              the award; also the lesson prop
    ├── Potion              restores HP (a second chance)
    └── Gold                pays shopkeepers, buys hints

Tile
├── Floor
├── Wall
│   └── SealedWall          + gate: Gate    ← becomes a Door when passed
├── Corridor
├── Door                    + locked: bool
├── Stairs                  + direction: UP | DOWN   (chapter boundaries only)
├── Pedestal                + item: Scroll           (final chamber)
└── Portal                  → reserved for Phase 2 remedial branches

World
├── Dungeon                 chapters: list[Chapter]
├── Chapter                 rooms: list[Room], grid, stairs_down
└── Room                    bounds, keeper, gate, entrance, sealed_exit
```

The three `Keeper` subclasses differ only in **voice and cost**, not mechanics — they all
instruct then examine. Wizards lecture, shopkeepers charge gold, gatekeepers are blunt.
Deliberately shallow: flavour over one code path, not three code paths.

`SealedWall` → `Door` is the entire progression mechanic, and it lives in `engine` with no
knowledge of why it opened.

---

## 6. The gate lifecycle

The brief calls for discrete phases. This is that, as a state machine:

```
   SEALED ──player steps adjacent──▶ GREETING
                                        │
                                   (talk to keeper)
                                        ▼
                                   INSTRUCTION  ◀──┐
                                        │          │ (re-read; free)
                                  (finish reading) │
                                        ▼          │
                                   EXAMINATION ────┘
                          (whole room sat; score = fraction correct)
                                     │      │
                            (score ≥ pass)  (score < pass)
                                     │      │      HP −= penalty  ← once per failed sitting
                                     │      ├──▶ attempts left?  ──▶ EXAMINATION
                                     │      │                        (re-read free, re-sit)
                                     │      └──▶ out of attempts ──▶ REPELLED
                                     ▼                                  │
                                  UNLOCKED                         (rest / re-read
                          SealedWall becomes Door;                  / consult pet)
                          corridor beyond is walkable                    │
                                     │                                   ▼
                          (last room in chapter?)              INSTRUCTION
                                     │
                            yes ──▶ stairs `>` appear
                            (or, final chapter ──▶ scroll chamber)
```

### What a wrong answer costs

The unit of stakes is a **sitting**, not an answer. A learner sits the whole room, sees every
explanation, and ends with a score; the HP cost is charged **once per sitting that misses `pass`**,
never per wrong answer. So a single wrong answer costs nothing on its own, which is deliberate:
each wrong answer already produces its explanation (§ the question format), and that is the
teaching the app exists for. Making every wrong answer also bleed HP would tax exactly the
exploration the design wants to reward. The weight belongs on *failing the room*, not on *being
wrong once*.

An earlier draft charged HP "per wrong answer" (AUTHORING §4's old wording), and drawing the
REPELLED screen proved that incoherent: at `standard` a sitting could lose 6+ HP, so HP hit zero on
the second failure and REPELLED — which needs a third — could never fire (SCREENS §8.10). Charging
**per failed sitting** fixes it. The numbers now cohere: `standard` is 12 HP, 3 per failed sitting,
3 sittings, so the third miss lands at HP 3 and repels the learner while they're still on their
feet. `strict` (5 × 2) lands at HP 2. `relaxed` (0, unlimited) can neither cost HP nor repel.

**REPELLED is not death.** The learner is pushed back, not deleted, and nothing earned is lost.
Because a room's bleed is capped by its attempt count, HP:0 is reached only by *accumulated* loss
across a floor, at which point the learner respawns at the chapter entrance with **all gate
progress intact** — doors they earned stay open. The roguelike supplies tension, but it must never
punish someone for learning slowly. This is the most important guardrail in the design, and it's
why `difficulty: relaxed | standard | strict` is a pack-level knob rather than a constant. Mock-up:
[SCREENS.md](SCREENS.md) §6.

**Still open for M4: how HP returns.** A learner only loses HP by failing sittings, and REPELLED
caps the loss per room, so a competent run spends nothing — but a struggling one accumulates damage
across the floor and needs it back somehow. Nothing here defines regeneration; a `Potion` (§5) is
the only named source, and the REPELLED mock-up invents a `rest` action to cover the gap. Without
some return, a wounded learner walks a slow path to HP:0, which is the punishment this guardrail
forbids. The penalty *model* is now settled; the heal mechanism is not.

---

## 7. Chapter layout

Full authoring specification: [AUTHORING.md](AUTHORING.md).

**Every floor is generated.** Authors write lessons and group them into chapters; the engine
does the rest. There is no map to draw and no map syntax to learn.

### Screen budget

Mock-ups of the M2 slice at real size, from the real pilot pack: **[SCREENS.md](SCREENS.md)**.
They confirm this budget and the generator geometry, and they found six things this plan hadn't
decided — including that passing an examination changes exactly one character on screen.

```
 ┌────────────────────────────────────────────────────────┐
 │ You hear the footsteps of a guard on patrol.           │  1 line   message
 ├────────────────────────────────────────────────────────┤
 │                                                        │
 │            map area                                    │  rows − 3
 │            (cols × rows−3, capped 160×44)              │  = 100×27 at minimum
 │                                                        │
 ├────────────────────────────────────────────────────────┤
 │ Ada the Novice   Dlvl:1  Rooms:2/3  $:0  HP:12(12) …   │  1 line   status
 │ Move: arrows    Talk: t    Help: ?                     │  1 line   hints
 └────────────────────────────────────────────────────────┘
```

Note the status line carries the **learner's** name. An earlier draft of this diagram put
`Ada the Suspicious` there, who is the *keeper* in `01-phishing.md` — caught by SCREENS §8.9.

### The hint line

The second status row is a **contextual hint line**: it names the keys that do something *right
now*, and changes as you go (`Talk to Ada: t` beside a keeper, `Next page: space` while reading,
`Descend: >` when the stairs open).

Delve has no stats to put in a status block, so NetHack's second line would otherwise hold nothing
— SCREENS §8.8 measured it as a row spent on a lonely name. This is a better use of it than
reclaiming the row for the map:

- It is the **safety net for the learner who skipped the tutorial**, who otherwise gets no
  interface teaching at all. §9 makes skipping honest and free; the hint line makes it survivable.
- It gives windows somewhere to put their key prompts, so `(a-d, or ? to consult your kitten)`
  costs no rows inside the panel.
- §3's audience "is not developers", in an app "most people run exactly once".

It is thoroughly un-NetHack, and right here for exactly that reason. Open: whether a learner with
a completed run can turn it off, the same signal that defaults the tutorial skip to yes (§9).

**Minimum 100×30**, which is Windows Terminal's default. Below that the app shows a resize
overlay and waits — it does not try to degrade. Above it, the floor uses the space available, up
to a **160×44 cap** so that a very wide terminal doesn't turn the dungeon into a hike. The
walking is not the point.

### Layout is locked at run start

The floor depends on terminal size, so the size has to be pinned or a mid-run resize would
re-lay the dungeon under the learner's feet.

- Layout is computed **once at run start** from `(seed, cols, rows)`, clamped to the cap.
- All three go in the `runs` record, so a run is exactly reproducible — `--seed 42` on the
  same size gives the same dungeon, which is what makes a bug reportable.
- Resizing **larger** mid-run re-renders centred. No re-layout.
- Resizing **below the locked map** shows the resize overlay until it's fixed. This is a
  deliberate non-feature: a scrolling viewport would be a camera subsystem earning nothing.

### The generator

Deliberately unambitious, because the linear chain removes most of the hard part:

1. Choose the smallest **cell partition** that holds N rooms, preferring wide over tall
   (1 room → 1×1, 3 → 3×1, 4 → 2×2, 6 → 3×2, 8 → 4×2, 12 → 4×3).
2. Divide the map area by the partition; clamp cell size to **[18×9, 40×15]**. A 3-room
   chapter on a huge terminal therefore stays compact and centred rather than sprawling.
3. Place one room per cell, jittered in size and position within it.
4. Walk cells in **serpentine order**, carving an L-shaped corridor between consecutive
   rooms. This is the chain — no spanning tree, no cycle logic.
5. Place the player at room 1; place each keeper beside its room's sealed exit.
6. Last room: stairs `>` appear on completion. Final chapter: the exit leads to the scroll
   chamber instead.

No connectivity flood fill and no reroll loop — a serpentine chain is connected by
construction, and unearned doors are *supposed* to block passage.

### Capacity

At the 100×30 minimum, with the smallest permitted cells, the grid holds about 15 rooms.
The limits below are lower than that on purpose — they're pedagogical, not technical:

| Rooms in a chapter | Behaviour |
|---|---|
| 1–6 | Comfortable. The target. |
| 7–8 | Validator **warns**. Probably two chapters. |
| 9+ | Validator **errors**. Definitely two chapters. |

**The grid could hold more; the learner can't.** Nine lessons without a break isn't a floor,
it's a lecture. Descending a staircase is the punctuation that says a thought has ended. The engine never splits a chapter itself — a break chosen by a packing
algorithm lands wherever it ran out of grid, which means nothing to a human. The author picks
it, and the validator just tells them when they're kidding themselves.

### The lesson panel, and how long text breaks

Mock-ups: [SCREENS.md](SCREENS.md) §2.

A lesson does **not** take over the screen. It opens as a panel to one side, clear of the current
room, so the learner can see the room, the keeper, the kitten and themselves for the whole time
the keeper is talking. This is not decoration: it is most of what stops a lesson feeling like a
slide deck that happens to be reached by walking, which §12 lists as the project's top risk.

**The examination uses the same panel** — same side, same width, same height. A keeper who teaches
from a side panel and then asks from a box over the room is two interfaces wearing one character.
The panel is the keeper's frame for the whole encounter, so nothing jumps as the gate walks the
states in §6: greet, instruct, examine, explain. Its height is the tallest thing she will show,
computed once.

**The panel is as short as it can be**, because every row it doesn't take is a row of dungeon the
learner can still see. The objective is **wasted rows, not pages** — and that distinction is not
pedantry, it inverts the answer. For the pilot's `01-phishing.md`:

| Pages | Panel | Map rows kept | Worst page |
|---|---|---|---|
| 3 | 24 tall | 3 | 8 rows empty |
| **4** | **18 tall** | **9** | **3 rows empty** |

Four pages is shorter, shows three times the map, *and* packs better. Minimising page count
produces a taller, emptier panel, because paragraph-aligned pages only break where the author left
a blank line. So: sweep candidate heights, take the minimum-waste one, floor of 8 rows so it can't
degenerate. Compute the height **once** and hold it for the whole lesson — a panel that resized
per page would jitter under the reader.

Panel *placement* is **not settled** — the panel is 73 columns and a room's cell can be 40, and
73 + 40 > 100, so "beside the room" is not always satisfiable. SCREENS §8.2 has the candidate
rules. The likely answer is that only the keeper and the player need to stay visible, which is
much cheaper than the whole room.

**Long text breaks on paragraph boundaries.** The rule, in order of precedence:

1. **Never split a paragraph across a page.** Fill each page with whole blocks — paragraph,
   blockquote, or a bullet list — and break before the first block that doesn't fit.
2. **Split a block only if it cannot fit a page alone**, and then only at a line boundary.
3. **Never break inside a URL, a domain, or a code span.** They are content, not prose.
   `textwrap` breaks on hyphens by default; pass `break_on_hyphens=False`. See SCREENS §8.3.

The cost is real and accepted: paragraph-aligned pages waste part of a page, so a lesson runs to
**more** screens than a greedy line-filler would produce. Take that trade every time. A page that
ends mid-sentence makes the reader hold a clause across a keypress, which is precisely the
attention this application is trying to buy. Pages are free; re-reading a mangled sentence is not.

The pilot's `01-phishing.md` is 3 pages at 69 columns under this rule, and would be 3 with a
greedy filler too — the difference is that the greedy version broke `yourcompany-hr.net` in half
across the page break, in a lesson whose entire point is *look at the domain*.

### Vision and backtracking

`Rooms: 2/5` in the status line so scope is never a mystery, plus classic NetHack revelation:
**current room lit, visited tiles dimmed, unexplored black.**

This is a small subsystem (a `discovered: set[Point]` and a lit-room test), not a free one —
an earlier note claiming "zero fog code" was overstated. What *is* free is the mystery: since
unearned doors don't exist, the map genuinely cannot show you what's next.

**Backtracking is free.** Every door you've earned stays open forever. Walk back to any
previous room and ask its keeper to teach you again, as many times as you like; `<` returns
you to earlier chapters. Re-reading a lesson is the single behaviour this application most
wants to encourage, so it costs nothing — no HP, no turns that matter, no score.

**But an examination is sat once.** The score is recorded the moment you pass, and a keeper
whose gate is open will re-instruct on request but never re-examine. Without that rule a
learner could grind any room to 100% and the trophy case would mean nothing. Failing and
retrying is the retry loop in §6 and carries its stakes; *passing* is final.

---

## 8. Languages

English and Dutch are both first-class. Voice and per-language rules live in
[STYLE.md](STYLE.md); this section is the mechanism.

### Pack content

A pack has one subtree per locale, and **the file trees must be identical**:

```
packs/security-onboarding/
├── en/
│   ├── pack.md
│   ├── scroll.md
│   └── 01-the-sorting-office/
│       ├── chapter.md
│       └── 01-phishing.md
└── nl/
    ├── pack.md
    ├── scroll.md
    └── 01-the-sorting-office/     ← same slug, Dutch content
        ├── chapter.md
        └── 01-phishing.md
```

Folder and file names are **slugs, not content** — the translated title lives in the
frontmatter (`title: Het Sorteerkantoor`). Three things fall out of that:

- "Is the Dutch complete?" is answered by `diff <(ls -R en) <(ls -R nl)`. The validator does
  exactly this and errors on any mismatch.
- Room `id`s are shared across locales, so `room_results` and the trophy case are
  **locale-independent**. A learner can take the Dutch dungeon and appear on the same board.
- A locale is complete or absent. There is no per-room fallback, because a half-Dutch dungeon
  is worse than an English one.

### Engine strings

Message line, status line, menus, and keeper stage directions live in TOML catalogues —
`delve/strings/en.toml`, `nl.toml` — read with stdlib `tomllib`. No gettext: `.po`/`.mo`
compilation is a build step and a toolchain for a few hundred strings, and TOML stays readable
and diffable with none of it.

Locale is chosen by `--lang`, defaulting to the system locale, falling back to `en`.

### Formatting is locale *data*, not translation

Mock-ups: [SCREENS.md](SCREENS.md) §7 shows the same scroll in both locales.

Dates, numbers and currency are **not sentences**, so they don't belong in a strings table as
sentences — and they are not the same in every language. Each locale carries a `[format]` table:

```toml
# delve/strings/nl.toml
[format]
currency      = "€"
currency_sep  = " "        # "€ 1.250" — Dutch spaces it, English does not
thousands     = "."        # en: ","
decimal       = ","        # en: "."
date          = "{d} {month} {y}"
months        = ["januari", "februari", "maart", ...]   # lower case: Dutch
```

Five things differ between `en` and `nl` on one scroll, and every one is wrong by default:
`$`→`€`, `1,250`→`1.250`, `91.7%`→`91,7%`, `July`→`juli`, and the space after the symbol.

Three rules about the mechanism, each of which is a trap:

- **Never `locale.setlocale`.** It is process-global, it depends on locales being *installed* on
  the host, and it differs across macOS, Linux and Windows. That is the same class of dependency
  this section rejected gettext for. A TOML table read by `tomllib` costs nothing and is
  reviewable by the translator.
- **Never `strftime('%B')`** for month names — it reads the process locale, for the same reason.
  Month names are locale data and live in the TOML.
- **Dutch month names are lower case.** A rule, not a preference, and the same family as
  STYLE.md's sentence-case-in-headings. `%B` would capitalise them on a Dutch host and nobody
  would notice for a year.

Open: **which locale a scroll is formatted in.** It isn't obviously the run's locale — a scroll
is a durable record, read later, possibly by an administrator in another language. `scrolls`
probably stores a number and a date and formats at read time. Answer with §13.1.

### Map glyphs are ASCII. Everything else is UTF-8.

This is stated here because §3 says "ASCII glyphs only" and that has **never been true of pack
text** — `packs/` has shipped 178 non-ASCII characters since `nl/` was written, including 98 `é`
and 16 `→`. Dutch cannot be spelled without them. The real rule:

> The glyph set `- | . # @ < > + f` is the game's **alphabet**, like `+` for a door. It is not
> language, it does not translate, and it lives in a fixed grid where one cell means one column.
> Lesson prose, menus, the status line and the scroll are **text**, and text is UTF-8.

`€` is text, in the same width class as the `é` that already ships. It costs nothing.

**Emoji are not an option** — see SCREENS §9.4 for the measurements. Briefly: they are
double-width (a 2-cell glyph in a 1-cell grid), astral-plane (the worst case for PDCurses, which
§12 already flags as the Windows risk), and often multi-codepoint, which stops `glyph: str` from
meaning "a character".

### Scope: English and Dutch environments only. Not CJK.

A stated constraint, not an accident, because it is load-bearing for rendering.

Room walls draw with curses' **`ACS_`** alternate character set (`ACS_HLINE`, `ACS_ULCORNER`, …;
43 constants, verified). That is portable *by construction* — curses maps ACS per terminal itself,
so there is no code page bet, no font bet and no width bet, and PDCurses provides the same names.
It is what NetHack's `DECgraphics` option does. Window frames use double-line box-drawing, which
has **no ACS equivalent** and is therefore a real Unicode bet, taken deliberately: it makes a
window frame instantly distinguishable from a room wall, and the terminal must already be UTF-8
for `é`.

**The cost of the scope, named so it isn't a surprise:** every box-drawing character is East Asian
*Ambiguous* — one cell in a Western terminal, **two** in a CJK-configured one, which would tear
the grid apart. So **adding a CJK locale later breaks the borders.** That is a language decision
with a rendering consequence; §13.3 already says an untranslated language is unsupported, and this
is a second reason the answer isn't free.

**Two concrete additions to the M1 Windows test**, neither known to work and both cheap to check
now rather than at M7:

- Render `é` and `€` through `windows-curses`. The packs already require it; Windows is where
  UTF-8 output is least certain.
- Render the **double-line window frame**. If it fails, rooms keep ACS and windows fall back to
  single-line ACS at zero cost — the fallback is one dict. This is the riskiest rendering choice
  in the design, and it has a free escape hatch, which is the only reason it's worth making.

### What the Dutch already caught

Type inference used to be "two options labelled `True`/`False`". Dutch options are `Waar` /
`Niet waar`, so the format had English baked into it and the validator rejected valid content.
Now it's option-count only (§3), which is both simpler and language-agnostic.

That bug existed for as long as there was one language. **A second locale is the cheapest test
of whether a format is really about structure or secretly about English** — which is an
argument for keeping `nl/` in step with `en/` from here on, not letting it lag.

---

## 9. The tutorial floor

Every training opens on **Dlvl 0**, a short orientation floor that explains the screen, the
keys, and what a keeper does. You descend to Dlvl 1 for the pack's first real lesson.

**It belongs to the engine, not the pack.** It teaches the *interface*, which is identical in
every training — if each pack authored its own, twelve packs would drift twelve ways and every
author would have to remember to write one. It ships in `delve/tutorial/{en,nl}/`, written in
the ordinary pack format, so it translates and validates like anything else. Pack authors never
think about it.

**But it is coupled to the renderer, and nothing checks that.** The tutorial's job is to describe
the interface, so it hard-codes it — and a single pass of screen mock-ups broke it twice: it said
*"Walls are `-` and `|`"* (now line-drawing, §8) and *"The bottom two lines are you. Your name, and
then…"* (now one status line plus the hint line, §7). Both were fixed by hand in `en` and `nl`.

The promise above is that engine-ownership stops the tutorial drifting. It does stop it drifting
*per pack*; it does **not** stop it drifting from the renderer, and that failure is invisible to a
validator that only checks structure. Held this time because a human remembered. No fix proposed —
worth knowing before M6, and worth suspecting whenever `ui/` changes what a screen looks like.

The same pass found a bug that had shipped since `nl/` was written: **the Dutch tutorial was
teaching an English status line** (`Rooms:1/2  $:0` instead of `Kamers:1/2  €:0`), so a Dutch
learner was being taught to read a screen they would never see. Found only by rendering the Dutch
status line next to the Dutch tutorial for the first time — which is §8's argument for a second
locale, arriving again from a new direction.

**Dlvl 0, not Dlvl 1.** You start at ground level and descend. That keeps the pack author's
chapter 1 at `Dlvl:1`, where they'd expect it.

**Never scored.** It writes no `room_results` and contributes nothing to the scroll. This is
what makes skipping honest: if the tutorial counted, skipping it would cost you, and it would
stop being a skip.

### Skipping

Two ways out, because they cost nothing and serve different people:

- **A prompt on arrival.** *"You have the look of someone who has done this before. Skip the
  orientation? [yn]"* — defaults to **no** for a new learner, **yes** for anyone with a
  completed run in the store. One keypress.
- **Unsealed stairs.** Uniquely on this floor, `>` is never sealed. If you start the tutorial
  and realise you know it, walk out. Every other floor's stairs must be earned; this one's are
  a door standing open.

### Shape

Four rooms, and it demonstrates the loop rather than describing it:

1. **The Porter** — the screen, the status line, and movement. You have already used movement to
   reach him, which is the point; he just names what you did. His door seals, so passing him is
   where you first watch a door appear.
2. **The Peddler** — objects: `,` picks up, `i` looks in your pack, `d` puts down, and coins are
   the one exception that collects themselves.
3. **Alwin the Patient** — keepers, sealed doors, HP, the pet, backtracking, and that passing is
   final. His question is trivial and unscored, so you experience *approach → instruct →
   examine → the door appears* once, with nothing at stake, before it matters.
4. **Merryn the Teller** — closes the floor with a purse and a paid, perfect-score exam: three
   free-text questions checking what the first three rooms just taught (the message line, the
   pick-up/drop keys, that earned doors stay open), and a lesson that gold later buys a helpline
   downstairs. She seals nothing; the `>` has stood open since the floor was generated (DELVE-0031
   built this as "demonstrate, then open stairs" rather than a fully serpentine chain, so the
   door-appears loop plays exactly once, on the Porter, while the stairs are always there to walk
   out to). Passing her drops 100 gold, scaled by the sitting score, even though the floor is
   otherwise unscored.

---

## 10. Progression, scrolls, and the trophy case

Completing a pack awards a **scroll** — a persistent, dated record with the score achieved.
Scrolls accumulate across packs into a trophy case the learner can browse (`#trophies`).

This is what makes "different instruction dungeons" cohere: the dungeon is disposable, the
scroll is permanent. A learner's history is their collection.

The scroll is picked up from a pedestal in the final chamber, so it enters the world through
the same `Item` path as everything else — the reward is a thing you hold, not a dialog box.

### Data model

```sql
users        (id, name, created_at)
runs         (id, user_id, pack_id, pack_version,
              seed, map_cols, map_rows,          -- reproduces the dungeon exactly
              snapshot,                          -- reproduces the learner's mark on it
              started_at, finished_at, outcome)
room_results (id, run_id, chapter_id, room_id,
              attempts, score, hints_used, passed_at)
scrolls      (id, user_id, pack_id, run_id, score, awarded_at)
```

`pack_version` is recorded so a result stays interpretable after a pack is edited — otherwise
the hall of fame silently compares scores from different exams. `seed` + `map_cols` +
`map_rows` are the full input to layout, so any run can be regenerated tile-for-tile from its
record.

`room_results.passed_at` is written once and never updated — see §7 on why passing is final.

### The snapshot

A run's state is two things, and the first is already free:

```
  the dungeon          (seed, cols, rows, pack_id, pack_version)   regenerated, never stored
  the learner's mark   position, hp, gold, turn, discovered, gate states   ← snapshot
```

Because layout is deterministic, the second part is all that's left, and it's tiny: a point, four
integers, a bitmap of discovered tiles (7 040 bits at the 160×44 cap, so under a kilobyte
base64'd), and an enum per gate. It goes in `runs.snapshot` as JSON, written on gate transitions
and chapter changes rather than every turn.

**The plan as written had no save/resume at all** — the pilot pack is 12 rooms and 48 questions,
which is not one sitting, and "quit and lose the dungeon" is a punishment for stopping that §6's
whole guardrail says we don't do. `session/snapshot.py` is maybe forty lines, because the hard
half of the problem was already solved the day layout was seeded.

### Identity

**Ask the learner their name at the start**, NetHack-style — *"Who are you?"* — rather than
taking `$USER`. It's the right aesthetic, it's one prompt, and it means the trophy case belongs
to a person rather than to a Unix account.

The name matches an existing `users` row case-insensitively, or creates one. That gives
multi-user on a shared machine for free, and makes the Phase 3 hall of fame purely additive.

Worth being honest about the limit: this is **trust-based**. Anyone can type anyone's name, and
there's no authentication behind it. That's fine for training and a trophy case; it is not fine
as an audit record, which is exactly why the export in Phase 2 is a separate mechanism with its
own (also imperfect) properties — see below.

Phase 3's hall of fame is then a `SELECT ... ORDER BY score` across `scrolls`, plus an
identity story. No schema migration.

---

## 11. Milestones

Ordered by risk, not by layer. The vertical slice lands second so the core loop can be
judged before anything is built on top of it.

The pilot pack (`packs/security-onboarding/`) already exists — 4 chapters, 12 rooms, 48
questions, in English and Dutch, written before a line of engine code. That's deliberate: the
format is now answerable to real content instead of the other way round, M2 has something true
to render, and the Dutch has already found one format bug (§8) that a monolingual pack would
have hidden indefinitely.

| # | Milestone | Done when |
|---|---|---|
| **M0** | **Foundation** | Homebrew Python 3.14, venv, package skeleton, pytest, ruff, `windows-curses` as a platform-conditional dep. `python -m delve` opens a curses window, enforces 100×30 with a resize overlay, and quits cleanly **on macOS, Linux, and Windows**. |
| **M1** | **Walkable generated chapter** | `layout.py` builds a serpentine chain from `(seed, cols, rows)`. Rooms, corridors, lit/dim/black vision. Player moves with hjkl+arrows. Message and status lines. Feels like NetHack — **and is confirmed on Windows before M2 builds on it**. The loop is in `session/`; a **headless test walks the chapter** with no terminal at all, and §4's rule 2 is enforced in CI. |
| **M2** | **⭐ Vertical slice** | Walk to a keeper → lesson displays → one MCQ → correct answer makes a door appear → walk the corridor to room 2. **Content hard-coded; no parser yet.** Driven end to end as `Command`s against `session`, so the same slice is replayable in a test. This is the go/no-go moment. |
| **M3** | **Markdown packs** | Chapter folders, room files, parser, schema, capacity rules, author-facing errors. `delve validate` passes on **both locales** of the pilot pack, including the identical-tree check. Format frozen. |
| **M4** | **Stakes and companion** | HP penalties, attempts, REPELLED, respawn-with-doors-intact. Backtracking and re-instruction. Pet follows and can be consulted for a hint at score cost. |
| **M5** | **Chapters, scrolls, progress** | Stairs between chapters, `<` backtracking, final chamber, scroll on a pedestal. "Who are you?" at start. SQLite store, trophy case across runs. `runs.snapshot`: quit mid-pack and resume where you stood. |
| **M6** | **Tutorial and languages** | Dlvl 0 orientation floor, skip prompt, unsealed stairs. `delve/strings/{en,nl}.toml`, `--lang`. Play the pilot in Dutch end to end. |
| **M7** | **Pilot playthrough** | You play all 12 rooms start to finish. Whatever hurts — pacing, lesson length, question quality, the format itself — gets fixed here, while it's still cheap. |
| **M8** | **Polish** | 16-colour palette, keeper voices, death/win screens, README, install instructions. |

### Deferred

| Phase | Scope |
|---|---|
| **Phase 2** | Free-text questions via a locally hosted LLM. `LLMGrader` implements the existing `Grader` protocol against Ollama/llama.cpp. Engine and pack format do not change — only a new question type activates. Needs: prompt design, a rubric per question, and a confidence floor below which it falls back to keyword matching. |
| **Phase 2** | **Scroll export** — see below. Explicitly *not* in the MVP. |
| **Phase 3** | Multi-user + hall of fame. Leaderboards per pack. Identity and schema already support it. |
| **Later** | Branching rooms (`requires:`, optional bonus rooms, hub chapters) — additive to the linear chain. Adaptive remedial branches (`Portal` is reserved). Shops selling hints for gold. A cumulative "boss keeper" exam before the scroll chamber. Hand-drawn set-piece floors, letterboxed on larger terminals — only if a real need appears. |

### Scroll export (Phase 2 — not in the MVP)

On completion the scroll is also emitted as a **base64-encoded, public-key-encrypted blob**,
which the learner either pastes into an email to an administrator, or which is POSTed to an
endpoint that processes it automatically. Both routes off the same artefact; the email path
needs no server, which is what makes it a good MVP-adjacent design.

**One property to be clear-eyed about before building it:** public-key encryption provides
*confidentiality*, not *authenticity*. The public key is public — anyone can encrypt a
well-formed payload with it. A learner who wanted to could produce a scroll claiming a perfect
score they never earned, and the administrator decrypting it would see something perfectly
valid. Combined with trust-based identity (§10), the export proves that *someone* produced a
well-formed claim, not that *this person* completed the training.

For training, that is almost certainly fine — it's a record for people who want the record, not
an access-control decision, and the failure mode is someone cheating themselves. But if it is
ever meant as a compliance artefact that an auditor leans on, the gap is real and closing it
needs a secret the client doesn't hold: a server that issues the attestation, or per-learner
signing keys. That's a different project, and it should be a deliberate choice rather than a
surprise discovered later.

---

## 12. Risks

| Risk | Mitigation |
|---|---|
| **The novelty wears off and it's just a quiz with extra walking.** The core bet is unproven. | M2 exists to answer this early and cheaply. If the slice is boring, cut the maze and rethink before M3. |
| Learners route around lessons. | **Structural.** The door does not exist until the examination is passed. No invariant to check. |
| Roguelike stakes punish struggling learners. | REPELLED ≠ death; earned doors survive respawn; backtracking and re-reading are free; `difficulty` knob per pack. |
| Backtracking lets learners grind a room for a better score. | An examination is sat once — `passed_at` is write-once. Keepers re-instruct freely, re-examine never. |
| A chapter has more rooms than a learner can absorb. | Validator warns at 7+ and errors at 9+. The limit is pedagogical, not technical — the grid would hold 20. |
| Terminal resized mid-run. | Layout is locked at run start from `(seed, cols, rows)`. Growing re-renders centred; shrinking below the locked map shows a resize overlay. Never re-lays the dungeon under the player. |
| Markdown format can't express question type N. | Format frozen at M3 *after* M2 proves the loop, and revisited at M7 after real content is authored. |
| Free-text LLM grading is wrong and unfair. | Phase 2 ships behind a confidence floor with keyword fallback; never the only gate on a room. |
| **PDCurses ≠ ncurses.** Windows behaviour drifts on resize, key codes, and timing. | All curses calls stay behind `ui/`. Windows is tested at **M1**, not M7 — the cost of finding this late is a rewrite of the render layer. |
| `windows-curses` lags a future Python release. | Verified: cp314 wheels exist today. If a later Python outruns it, the options are pin the Python or paint `Frame`s to ANSI instead — the isolation above is what keeps that affordable. |
| **The loop can only be tested through a terminal, so it isn't tested.** On the one project whose core bet is unproven and needs cheap iteration. | The loop is in `session/` and never imports curses. The M1 headless harness plays a run as a list of `Command`s. |
| Rule 2 of §4 erodes — one `import engine.world` in `render.py` and the loop is back inside curses. | Mechanically checkable. **Check it in CI from M1**, not by intention: this rule fails silently, and the failure is invisible until the tests nobody wrote miss something. |
| A learner loses a run by quitting. | `runs.snapshot` from M5. The dungeon regenerates from the seed; only the learner's mark is stored. |
| Terminal too small on first run. | Minimum is 100×30 = Windows Terminal's default, so Windows needs no resize at all. macOS/Linux default to 80×24 and need one; the overlay names the exact size required rather than just complaining. |
| A translated pack drifts out of sync with the original. | Locale subtrees must have **identical file trees**; the validator diffs them and errors on mismatch. Room `id`s are shared, so progress records are locale-independent. |

---

## 13. Open questions

Settled since the first draft: terminal minimum (100×30), scroll export (Phase 2, encrypted
blob, §11), identity ("Who are you?" at start, §10), backtracking (free), the name (Delve).
**Re-taking a pack (settled at M5): keep both** — every completion writes its own `scrolls` row,
none is ever updated, and the trophy case lists all attempts. Append-only is the simplest schema
and matches "a learner's history is their collection"; `room_results` stays write-once *within* a
run, so "keep both" concerns a fresh run, not re-grinding one. The Phase 3 hall of fame is then a
`SELECT ... ORDER BY score` (or `MAX`) across `scrolls`, unchanged.

Still open. None blocks M0–M2.

1. **Pack customisation** — the pilot pack contains deliberate placeholders
   (`security@example.com`, `#security-help`, the classification tiers) in *both* locales. Do
   these become frontmatter variables the engine substitutes, or does each organisation fork
   the pack? The first is nicer and keeps locales in sync; the second is free. **Answer before
   M7**, since M7 is where you'd feel it.
2. **Dutch tutorial parity** — the tutorial ships in `en` and `nl`. If a third language is ever
   added, does a pack in that language fall back to the English tutorial, or is the language
   simply unsupported until the tutorial is translated? (Consistent answer: unsupported — §8.)
3. **Pack distribution** — folders in the repo, or installable/shareable archives?
4. **A web Delve — and note this is not an architecture question.** The instinct is to keep the
   Python core and bolt a browser onto it. Probably wrong. The durable assets here are `packs/`,
   AUTHORING.md, and the schema — Markdown and a written spec, already neutral, already readable
   from any language. The Python core is a couple thousand dependency-free lines of state machine
   and grid geometry; that is not a moat, and a fresh TypeScript implementation eating the same
   packs is entirely legitimate. So the format is the portability story and it is already paid
   for. **Do not build `session/` "for the web" — build it for the tests (§3), and leave this
   question open.**

   Three things to know before anyone reopens it:

   - **The question that would force it is "does a scroll need to mean something to an
     auditor?"** Not "should Delve have a web UI?" §10 identity is trust-based and §11's export
     proves *someone* made a claim, not that *this person* earned it; both gaps root in the
     client holding everything. A **served** build is the only configuration here where the
     server holds the state and grades — the "secret the client doesn't hold" §11 asks for. The
     cost is real identity (SSO), at which point "Who are you?" is aesthetic, not functional.
   - **React is the wrong reflex.** The map is a character grid, a text overlay, and a menu —
     the least component-shaped UI there is. A `<pre>`, a keydown handler, and sixteen colour
     classes. The trophy case is React-shaped; the dungeon isn't, and the dungeon is the product.
   - **Two implementations means grader drift**, and this is compliance training: if a Python
     and a TS grader disagree on a `pass: 0.75` boundary, a learner passes in one and fails in
     the other. Only bites if both run in production at once. That is the one real argument for
     sharing code rather than sharing the format, and it should be weighed honestly.
