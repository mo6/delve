# Text mode: a spoken dungeon, no map on screen

Future-reference design note, not scheduled work. The third of the display siblings, and the most
radical. [DISPLAY.md](DISPLAY.md) and [WEBDISPLAY.md](WEBDISPLAY.md) both keep the map and change how
it is *drawn* (emoji tiles in a terminal, CSS tiles in a browser). This plan does the opposite: it
**removes the map from the screen entirely** and turns the interface into prose. The dungeon still
exists, tile for tile, seed for seed, exactly as today; the learner just never sees the grid. They
read where they are, and they type what they want to do, in their own words.

The motivating complaint is real and worth stating plainly: **the NetHack look is aging.** A wall of
`- | . # @` reads as *a place* to people who grew up on roguelikes, and as line noise to nearly
everyone else. Delve's audience is "not developers and most run this once" (CLAUDE.md); the ASCII
grid asks that audience to learn a visual language before they can learn the actual lesson. Text mode
proposes to spend the LLM we already added in Phase 2 on removing that barrier, and to turn the
removal into a *second thing worth learning*: how to say clearly to a small local model what you
want. Delve stops being only security training in a dungeon costume, and becomes, on top of that, **a
low-stakes gym for talking to LLMs.**

This is a large bet with a real downside (below, §7). It is written down so the idea is captured with
its costs attached, not so it ships.

---

## 0. Read PLAN §13.5 first

Everything the web doc says about the boundary applies here, doubled, because text mode is a *whole
new frontend* rather than a re-skin of the existing one:

- **The durable asset is the pack format, not the Python.** A text frontend that eats the same packs
  is legitimate. A text frontend that needs the packs rewritten is a different product wearing
  Delve's name.
- **`session/` is built for the tests, not for this.** Text mode is tractable *because* rule 2
  already forced a headless core (`session.apply(Command) -> Frame`, no curses, no I/O). That it
  makes a second frontend cheap is the designed-in side effect finally being spent, not a
  justification for anything.
- **The dungeon is still the product.** If text mode quietly becomes "a chatbot that asks quiz
  questions," it has thrown away the core bet that M2 was a go/no-go on: that *being in a place*
  makes training land better than a slide deck. Prose is a place too, in interactive fiction; the
  work is keeping it one.

Text mode is additive. The curses grid does not die for it (§7 argues for shipping both), and no
pack, no lesson, no `room_results` row changes shape.

---

## 1. The core idea: the model parses, it does not narrate

The one architectural decision everything else hangs on, and the one the user's brief gets exactly
right:

> **The LLM's only job is to turn what the player typed into one discrete engine command. It never
> decides what happens in the world.**

A small local model (`qwen2.5:3b`, the Phase 2 default) does not have the association or deductive
reach of a frontier model. Handed an open task ("run this dungeon"), it will hallucinate rooms,
invent doors, and contradict itself. Handed a **closed** task ("the player can currently do one of
these eight things; which did they mean, and with what argument?"), a 3B model is reliable, because
the task is classification with slot-filling, not world-modeling. So the design shrinks the model's
job to fit the model we have:

```
  player types free text
        │
        ▼
  ┌───────────────┐   the current Frame already knows the *legal* actions:
  │ intent parser │◀──  which exits exist, whether a keeper is adjacent, whether
  └───────────────┘     an exam is open, what is on the floor. That menu is the
        │               prompt. The model picks from it and fills the blanks.
        ▼
  a discrete Command  (Move(NORTH) · Talk() · AnswerText("...") · Pickup(...) · Descend() · ...)
        │
        ▼
  session.apply(Command) -> Frame   ← unchanged, deterministic, already tested
        │
        ▼
  Frame -> prose   (the description layer, §3)
```

The Command vocabulary this targets **already exists** and is already closed:
`Move · Talk · Answer · AnswerText · Confirm · Consult · Rest · Wait · Descend · Ascend · Pickup ·
Drop · Inventory · Dismiss · Quit` (`session/commands.py`). Text mode adds no engine actions. It adds
one input path that produces the same commands the keyboard produces today.

**This is the grader stack again, and that symmetry is the strongest argument for it.** Phase 2's
grading is a two-layer stack: an `LLMGrader` on top, a deterministic `KeywordGrader` floor beneath,
the model trusted only above a confidence floor and otherwise falling through
([PHASE2.md](PHASE2.md), `assess/grader.py`). Intent parsing wants the exact same shape:

| Grading (exists) | Intent parsing (proposed) |
|---|---|
| `LLMGrader` asks the model ACCEPT/REJECT + confidence | `LLMParser` asks the model for a command id + confidence |
| Below the floor → `KeywordGrader` (normalise, match) | Below the floor → verb parser (`go`/`north`/`talk`/`take`) |
| Empty answer short-circuits to REJECT | Empty / unparseable line → re-prompt, no model call |
| Strict JSON, `temperature 0`, `format:"json"` | Same, and the legal-action set is enumerated in the prompt |
| Offline default is the keyword floor | Offline default is the verb parser: `go north`, `talk`, `take coins` still work |

So text mode is not a new kind of thing in the codebase. It is the parsing half of the same
LLM-on-a-deterministic-floor pattern, pointed at input instead of answers, reusing the same
`assess/llm.py` socket seam (the one place a socket is opened) and the same "the model gives data,
the engine decides" discipline.

### 1.1 Why this keeps the model honest

- **The legal-action menu is computed by the engine, not the model.** If the wizard's door is sealed,
  `Move(EAST)` is simply not in the menu the parser is offered, so no phrasing ("barge through the
  door", "kick it down") can produce it. Rule 2 holds without a single new check: *sealed doors are
  structural; there is no path to validate* (CLAUDE.md rule 2). The model cannot route around a
  lesson because the command that would isn't on the list.
- **The model never sees the map and never invents geography.** It sees a short list of the exits and
  actors the Frame already reports, phrased as options. It returns one. Everything spatial stays in
  the engine.
- **Determinism survives where it matters.** Runs are regenerable tile-for-tile from `(seed, ...)`
  (PLAN §7). LLM parsing is not reproducible across model versions, so the *reproducible record* of a
  run becomes the **resolved command stream**, not the raw typing: log the `Command` each line
  parsed to, and the run replays exactly. The NL is the lossy human layer on top of a deterministic
  spine (this is worth being honest about, like identity-is-trust-based; see §8).

---

## 2. What the maze becomes when you cannot see it

The grid does not go away; the *granularity of navigation* changes. Stepping one tile at a time
(an arrow key) is fine when you can see the corridor and tedious when you cannot ("you walk east. you walk
east. you walk east."). Interactive fiction solved this decades ago: navigate by **place and
direction**, not by cell.

So text mode reads a **room-and-corridor graph** off the existing tile layout (the layout already
knows rooms, doors, corridors, and stair positions; `engine/layout.py`) and lets the player move at
that granularity:

- `go north` / `north` / `head down the passage` → the engine walks the corridor to the next junction
  or room and narrates the transit, stopping at the first thing worth stopping for (a keeper, a fork,
  a pile of coins, the stairs).
- `approach the wizard` / `go to the door` → path to a named feature the Frame currently reports.
- `go back` → retrace to the previous room (backtracking is free; rule 3).

The maze is thus **represented, not drawn**: the player builds a mental model from descriptions and
exit lists, the way an IF player maps a game on graph paper. Because Delve floors are small
(validator errors at nine rooms; "nine lessons without a break isn't a floor, it's a lecture",
CLAUDE.md) and linear-ish (serpentine chain), the graph a player must hold in their head is a few
rooms deep, not a sprawling labyrinth. That smallness, a pedagogical choice made for other reasons,
is what makes text navigation humane.

**A "look" and an on-demand map are the safety net.** `look` re-prints the current room and its
exits. `where am I` restates the floor and progress. And because throwing the grid away entirely is
the riskiest part (§7), an optional `map` command can still paint the familiar ASCII minimap on
request, for the learner who wants it. The grid becomes a tool you can reach for, not the primary
surface.

---

## 3. The description layer: static skeleton, dynamic skin

The user's framing is the right one: **descriptions are statically generated, but vary, to a point,
with actions and state.** The engine already holds every fact a description needs; text mode adds a
`Frame -> prose` renderer that is the exact sibling of today's `Frame -> grid` renderer
(`ui/render.py`). Nothing new is computed; the same Frame is spoken instead of painted, so rule 2 is
untouched (the text UI imports only `session`, reads a `Frame`, prints prose).

A room's prose is assembled from layers, cheapest first:

1. **Static skeleton (per tile-model).** Engine-generated from the room's shape and contents: "a low
   stone room", the exits that exist, the keeper's kind and position, the floor objects. This works
   for *every pack for free*, the way the tutorial floor's interface description is engine-owned so no
   author can forget it (CLAUDE.md, "The tutorial floor"). A pack that writes nothing still speaks.
2. **State overlays (dynamic).** The same room reads differently as the world changes, all from Frame
   state that already exists:
   - the door is **shut** and immovable / **grinds open** the turn the exam is passed / **stands
     open** on a revisit;
   - coins **glint by the west wall** / are **gone** once banked;
   - the keeper **blocks the only way deeper** / **turns back to the desk** once you have passed them
     (the `bump_passed` brush-off, already a string);
   - **first visit** ("You step into...") vs **revisit** ("You are back in the room where...").
3. **Authored flavour (optional, additive).** A pack *may* enrich a room's look with a sentence or two
   of its own, but this is where the design must resist itself: **content lives in the body, not
   frontmatter** (rule 5), and a description the author is *required* to write is a per-pack tax that
   the engine-generated skeleton exists precisely to avoid. Recommendation: engine-generated is the
   default and the contract; authored flavour is a later, optional sugar, never a prerequisite for a
   pack to play in text mode. (Open question, §9.)

The tone can even flex with stakes without new state: at low HP the prose can tighten ("the dark
presses closer"), REPELLED can narrate the push back to the entrance rather than flashing a panel.
This is skin over the same numbers, and it is where a text interface can carry *more* mood than a
grid, not less.

**Localisation is inherited, and it is the real cost.** Delve is en + nl, both first-class, every
string in `strings/{en,nl}.toml`. A prose renderer means the *description templates* join that
catalogue, and Dutch prose generation (tutoyeer, sentence-case, inversion; STYLE.md) is more surface
area than Dutch grid labels. This is the largest content cost of text mode and is discussed in §7.

---

## 4. Where the pieces live (the five rules still bind)

Text mode threads through the existing seams without bending them:

```
  text-ui ──▶ session ──▶ (intent parser) ──▶ assess.llm   [the socket seam, reused]
     │                │
     │                ├──▶ gate ──▶ assess/content/progress   [unchanged]
     │                └──▶ engine                              [unchanged]
     └──▶ reads a Frame, prints prose; reads a line, sends it on   [rule 2]
```

- **The text UI is paint-plus-readline, nothing more.** It prints the prose the session hands over
  and reads a line of input. It imports only `session` (rule 2). It never parses the line itself and
  never opens a socket; parsing is not its job any more than grading is.
- **The parse is input, and input with I/O belongs in `session`, not `ui` and not `engine`.** There is
  a clean precedent: the free-text answer already sends a *whole string* into the core as
  `AnswerText(text)`, which the session grades through a runner it owns (`session/grading.py`,
  `submit`/`poll`, inline floor vs threaded LLM). Text mode generalises exactly this: a new
  `Instruction(text)` command carries the raw line to the session, which resolves it to a concrete
  `Command` through an **intent-parser runner** shaped like the grader runner (an `InlineParser`
  verb-floor that resolves in the same `apply` for the headless tests; a `ThreadedParser` that runs
  the blocking LLM off-thread and folds the result in on a poll, so the loop stays non-blocking).
- **`engine` and `gate` do not move.** They already speak `Command`. Whether a `Move(NORTH)` came from
  the `k` key or from the model parsing "wander off north" is invisible to them. `gate.py` remains the
  one module touching both dungeon and training; text mode adds nothing to it.
- **The headless harness still works.** Tests drive text mode the way they drive everything: a list of
  commands. `Instruction("go north")` with the deterministic floor resolves inline, so a whole
  text-mode run is still a flat, model-free command list on the CI gate. The LLM is opt-in for humans,
  absent in tests, exactly as the grader is.

The single genuinely new outward behaviour is that a *core interaction* (moving) can now depend on the
model. That is the bet in the next two sections.

---

## 5. The visible UI mockup

A terminal session, English, mid-run. This is the whole screen: a scrolling transcript, a status
strip, and a prompt. No grid.

```
┌─ Delve ──────────────────────────────────── The Sorting Office · Dlvl 1 ─┐
│                                                                          │
│  Chamber one. You stand on cold flagstones in a low, close room. A       │
│  wizard in a grey robe waits by a heavy iron door to the east; the       │
│  door is shut and does not give. A passage runs north into the dark.     │
│  A few coins glint against the west wall. Your cat pads in behind you.   │
│                                                                          │
│  Exits:  north — a passage      east — the wizard's door (shut)          │
│                                                                          │
│  > grab the coins                                                        │
│  You gather five coins from the floor.                          (+$5)    │
│                                                                          │
│  > talk to the wizard                                                    │
│  He looks up. "Before this door opens, you answer for what you know      │
│  of phishing. A moment; I will teach first."                             │
│                                                                          │
│  > go on                                                                 │
│  "A phishing mail works by rushing you. It wants you moving before       │
│  you think, because thinking is what kills the attack..."                │
│  ( lesson, 1 of 3 — say 'go on', or 'quiz me' when you're ready )        │
│                                                                          │
│  > quiz me                                                               │
│  "In one word: what feeling does the mail manufacture to stop you        │
│  thinking?"                                                              │
│                                                                          │
│  > i guess it makes you feel rushed                                      │
│  (the wizard weighs your words…)                                         │
│  "Urgency. Just so." The iron door grinds back into the wall.            │
│                                                                    ✓     │
│  > head east                                                             │
│  You pass through into a narrow corridor. It bends left after a few      │
│  paces and opens on stairs going down.                                   │
│                                                                          │
├──────────────────────────────────────────────────────────────────────────┤
│  ♥ 20/20   $10   T:41   ·   your kitten is here                          │
│  what do you do?  ▏                                                      │
└──────────────────────────────────────────────────────────────────────────┘
```

**Two things the mockup is deliberately showing.**

*Ambiguity becomes a teachable exchange, not an error.* When the parse is unsure, the game asks rather
than guesses, and the asking is the LLM-communication lesson happening in miniature:

```
  > go over there
  Which way do you mean? north (the passage), or east (the door)?
  > the passage
  You head north into the dark...
```

*The deterministic floor is always under you.* With no model (or an unreachable one), the same run
still plays; the phrasing just has to be plainer. This is the grader floor's twin, and it is what
keeps text mode from being hard-blocked on Ollama:

```
  > mosey on up yonder                              [ no model: not understood ]
  I didn't catch that. Try: go north, go east, talk, look, take coins, down.
  > north
  You head north into the dark...
```

---

## 6. Possibilities this opens

- **Accessibility, for real.** A curses grid is hostile to screen readers; prose is their native
  format. Text mode is very likely the single largest accessibility win available to the project, and
  it comes as a by-product rather than a separate effort.
- **A familiar front door.** Everyone who has typed at ChatGPT already knows how to use a text box.
  The interaction that reads as "old and nerdy" in a grid reads as "obvious" in a chat-shaped
  transcript, without dumbing anything down.
- **A second curriculum, for free-ish.** Learning to instruct a small model clearly, to notice when it
  misread you, to rephrase, is a genuine 2026 skill, and text mode *is* practice at it, wrapped around
  whatever the pack teaches. A pack about phishing becomes, incidentally, reps at talking to an LLM.
  This is the reframing the user is reaching for and it is the most interesting thing here.
- **The most portable frontend yet.** Prose over a line-reader runs anywhere text goes: a bare
  terminal, a web chat, a Slack thread, a voice assistant. The pack format was always the portable
  asset; a text frontend is the thinnest possible shell around it.
- **Mood a grid can't hold.** Low-HP tension, a keeper's voice, the door "grinding open" — a sentence
  can carry atmosphere that sixteen colours cannot. Done well, text mode is *more* of a place, not
  less.
- **Content stays put.** Same packs, same `room_results`, same trophy case, same seeds. The bet is on
  the shell, and it is reversible: the grid is still there.

---

## 7. Costs and risks (the honest half)

- **The LLM stops being optional for the intended experience.** Today the model is pure upside: absent,
  you lose meaning-grading and nothing else. In text mode the *full* experience wants it, because the
  verb floor, while playable, is stiff. The design keeps the floor so text mode is never hard-blocked
  offline, but "install a local model to get the good version" is a real adoption tax on an app whose
  audience "runs this once." This is the central trade and it should be decided with eyes open.
- **Latency changes the feel.** A keypress is instant; a local parse is roughly half a second to two
  seconds per action. A dungeon that felt like a game starts to feel like a chat. Mitigations: a
  deterministic fast-path for unambiguous lines (a bare `north` never troubles the model), and the
  same "(thinking…)" hold the grader already uses. But the felt tempo does change, and no amount of
  engineering makes a 3B model as fast as a keycode.
- **Spatial legibility is genuinely lost.** The grid gives instant, whole-floor understanding; prose is
  linear and forgetful, and players *will* get lost in a way they never do with a visible map.
  Mitigations (small floors, `look`, `where am I`, an on-demand `map`) reduce it; they do not delete
  it. Some people navigate worlds spatially and text mode is simply worse for them. Shipping both
  frontends (§8, alt E) is the honest answer to this, not pretending prose is strictly better.
- **The slide-deck risk, back with new teeth.** PLAN names the project's top risk as a lesson feeling
  like a slide deck reached by walking. A chat transcript is *even closer* to a slide deck than a
  grid; if the room prose is thin and every turn is "keeper talks, you answer," the dungeon
  evaporates and Delve is a quiz bot. Keeping text mode a *place* is the hard design work, not a
  detail.
- **Dutch prose is a real content project.** Grid mode localises labels; text mode localises
  *narration*, in a language with inversion rules that a heuristic cannot fake (CLAUDE.md, "Editing
  content"). Every state overlay in §3 needs a correct Dutch twin. This is the largest single cost and
  it is content, not code.
- **Reproducibility gets an asterisk.** Runs stay replayable from the resolved command stream, but the
  *raw input* to *command* mapping is model-dependent and not reproducible across model versions. Fine
  for training; state it plainly rather than implying bit-for-bit input replay (same register as
  "identity is trust-based", PLAN §10–11).

---

## 8. Alternatives

Ordered roughly from least to most divergent from Delve-as-it-is.

**A. NL command bar over the existing grid (smallest step).** Keep the visible dungeon; add an
optional input line where a player can *type* "go talk to the wizard" and have the LLM parse it into
the moves it already makes. This tests the intent-parser tech and buys accessibility and
approachability *without* giving up the map. Lowest risk, and a natural staging step toward full text
mode. It does not, by itself, solve "the ASCII look is aging" for people who bounce off the grid on
sight.

**B. Hybrid: text-primary, map-on-demand.** Text mode as designed above, but the ASCII minimap is a
first-class toggle, not a hidden `map` command; the learner chooses their surface per taste or per
moment. This is probably the *right* shape if text mode is pursued at all, because it keeps the
spatial safety net (§7) for the people who need it while defaulting to prose for the people the grid
loses. Costs: two renderers to keep in step.

**C. Modernise the look, keep the grid (the DISPLAY/WEBDISPLAY path).** The other two display docs
already answer "the ASCII look is aging" *without* an LLM dependency or the loss of spatial legibility:
emoji/CSS tiles make the same dungeon look like 2026. If the only goal were "not grey and nerdy", this
is the cheaper, lower-risk answer and it is already sketched. Text mode is worth more than a re-skin
*only if* the LLM-communication curriculum (§6) is a goal in its own right. If it isn't, do C instead.

**D. Ship both frontends on one core (the hedge).** Rule 2 makes a text frontend and the curses
frontend siblings over the same `session`. Offer `--text` (or a first-run choice) and let the learner
pick. This is the honest response to "some people navigate spatially and some read": stop choosing for
them. Cost: two `Frame`-renderers and two localisations of the same content, maintained together, plus
the discipline to keep the `session` core the single source of truth so neither frontend grows logic
(the exact failure rule 2 exists to prevent).

**E. Drop the dungeon; become a conversational tutor (the far end).** Take the reframing to its
conclusion: no rooms, no map, no navigation, just keepers you converse with while progress is tracked
underneath. This is the simplest to build and the most 2026, and it is listed **to be rejected on the
record**: it discards the core bet that a *place* teaches better than a chat, which M2 was staked on.
If Delve becomes a chat tutor, it is a good chat tutor and no longer Delve. Name it so no one arrives
there by accident, one convenience at a time.

---

## 9. Open questions

1. **Engine-generated prose, authored prose, or both?** The tutorial-floor precedent argues hard for
   engine-owned descriptions (no author can forget one, every pack speaks for free). But engine prose
   is generic. Is optional per-room authored flavour worth the per-pack tax and the second thing to
   localise? Leaning: engine-generated is the contract; authored is later sugar, never required.
2. **Where does the room graph come from?** Derived from the tile layout at run start (no new authoring;
   the layout already knows rooms and corridors), which is the rule-2-clean answer. Confirm the
   junction/stopping heuristics ("walk until something worth stopping for") produce navigation a human
   finds predictable.
3. **How much state may a description depend on before it needs its own store?** §3's overlays all read
   from the existing Frame. Anything richer (remembered per-visit prose, "the coins you left here")
   risks a parallel narrative state the snapshot would have to carry. Keep descriptions a pure function
   of the Frame for as long as possible.
4. **Confidence floor and clarify-vs-guess.** What confidence does the parser act on, and when does it
   ask instead (the §5 clarification)? Too eager and it misreads; too timid and every turn is a
   twenty-questions. This is the tuning that decides whether text mode feels smart or exhausting.
5. **Is the LLM-communication curriculum explicit or ambient?** Does Delve ever *teach* "how to phrase
   an instruction", or does the interface just quietly reward clarity? Ambient is truer to the app;
   explicit might be a genuinely valuable pack of its own.

---

## 10. If it were ever pursued (staged, not scheduled)

Not a plan of record. A dependency order, so the risky part is proven before the expensive part is
built:

1. **Intent-parser runner, deterministic floor only.** `Instruction(text)` → verb parser → `Command`,
   inline, no model. Prove text-driven navigation and the room graph on the headless harness, in the
   existing grid UI (alternative A). No prose renderer yet, no LLM. This de-risks the whole idea for
   almost no cost and is independently shippable.
2. **`LLMParser` on top of the floor.** The grader stack again: model picks from the legal-action menu,
   trusted above a confidence floor, clarifies when unsure. Still in the grid UI. Now "type what you
   mean" works.
3. **The prose renderer (English).** `Frame -> prose`, static skeleton plus state overlays (§3). The
   text frontend becomes real. Ship it behind `--text`, grid still default (alternative D).
4. **Dutch prose.** The real content lift (§7). Text mode is not "complete" in a second language until
   this lands, and a half-Dutch narration is worse than an English one (the locale-complete rule).
5. **Only then**, if the spatial-loss evidence from real play demands it, the on-demand map / hybrid
   (alternative B).

Steps 1–2 are worth doing *regardless* of whether text mode ever ships, because a natural-language
command bar over the existing grid (alternative A) is a real feature with a low ceiling of risk, and
it is the whole of text mode's engine-facing work. The prose renderer is where the commitment, and the
cost, actually begins.
