# Delve — implementation notes

A NetHack-style training application. Learners descend a dungeon; keepers teach a topic and
examine them on it; passing makes a door appear. Design in [docs/PLAN.md](docs/PLAN.md), the
content format in [docs/AUTHORING.md](docs/AUTHORING.md), voice and the LLM pack-generation
brief in [docs/STYLE.md](docs/STYLE.md), verified 100×30 screen mock-ups of the M2 slice in
[docs/SCREENS.md](docs/SCREENS.md). This file is the short list of things that are expensive to
get wrong.

**The mock-ups are generated, not drawn** — `./tools.sh screens` (add `--check` for
assertions only). Change a screen there and re-paste into SCREENS.md; never hand-edit the frames,
or they stop being evidence. Its assertions have already caught four real bugs.

**Issues live in [issues/](issues/README.md)** — one Markdown file per change
(front matter plus testable prose), stating *what* a change must do, distinct from `docs/` (*why*)
and CHANGELOG (*when*). Implemented ones move to `issues/archive/` carrying their commit ids,
rejected ones to `issues/rejected/`; the seed set (`DELVE-0001`–`DELVE-0014`) was backfilled from
history by feature arc. The index in `issues/README.md` is generated and gate-checked by
`./tools.sh issues` (`--check`), the same way `screens.py` guards the mock-ups. **Before adding
an issue, run `./tools.sh issues --check`** — it prints the next free id (`DELVE-NNNN`) to
name the new file, then regenerate the index with `./tools.sh issues` once the file is written.
**To list or filter issues (e.g. "what's proposed", "what's left to pick up"), use
`./tools.sh effort_table`** rather than grepping front matter by hand — it defaults to
`status: proposed` sorted low effort first, and `--status all` or `--status
proposed,in-progress` covers the rest.

**Every change to the system gets an issue first.** Before writing code for a change (a feature, a
fix, a refactor, a bug someone reported), create its `DELVE-NNNN` file in `issues/` with
`status: proposed`, *then* implement against it, *then* archive it with the commit id. This is not
bureaucracy for its own sake: the issue is the *what* the code is answerable to, and writing it first
is what keeps the acceptance criteria honest rather than reverse-engineered from the diff. The one
standing exception is a change that is itself only about an issue (fixing a typo in an issue file,
regenerating the index); those need no meta-issue. When in doubt, write the issue. The `type` is
one of `epic | feature | story | bug` (a reported defect is `type: bug`, and may still hang off an
`epic:` like a story does).

**A drafted issue is not yet approved to build.** Between `status: proposed` and starting
implementation sits a peer-review gate (DELVE-0045, [issues/AGILE.md](issues/AGILE.md)'s Definition
of Ready): show the issue to a peer (in this solo, no-remote project, the human maintainer) and ask
outright whether it is accepted. Never infer acceptance from silence or move straight from drafting
to coding. Only once the answer is yes, fill `accepted_by:`/`accepted_at:` on the issue's front
matter and move `status:` to `in-progress`, in that order, and only then start writing code against
it. `./tools.sh issues --check` enforces the fields are present from `in-progress` onward, the same
way it already enforces `effort:`.

**Markdown paragraphs are single lines, never hard-wrapped.** This applies to every Markdown file
this project generates or edits (`issues/`, `docs/`, `CHANGELOG.md`), and it matters most for
issues, since those get written and re-written the most often: a hard line break part-way through
a paragraph (the classic "wrap at ~95 columns and hit enter" habit, which is what this very file
does) looks fine in a narrow editor pane but leaves a ragged, broken-looking flow when the file is
read on a wider screen or in a viewer that doesn't rejoin soft-wrapped lines. Write each paragraph
as one continuous line and let the reader's own editor or viewer wrap it; only break the line for
an actual new paragraph, a list item, or a heading. This is a source-formatting rule, not a voice
rule: it doesn't change what the prose says, only how the `.md` file's newlines are placed.

**The house style is agile** ([issues/AGILE.md](issues/AGILE.md), the default in
`TEMPLATE.md`): user stories (`As a <learner|pack author|maintainer>, I want ..., so that ...`) with
Given/When/Then acceptance criteria, grouped into **epic → feature → story** tiers that map onto the
`DELVE-NNNN` files (an epic is a `type: epic` issue; its children point up via an `epic:` field, which
`tools/issues.py` rolls up into an Epics table in the index). A shared Definition of
Ready and Definition of Done live there too, tied to Delve's real gates (`run-tests.sh`, the five
rules, both locales). A small change may still use a plain numbered MUST list; the two forms coexist.

Status: **released at `1.10.2`**, developed on macOS, playing end to end in English and Dutch.
Everything through M8 is built, plus post-1.0 arcs: objects (`1.0.1`–`1.3.x`), the companion pet
(`1.2.0`, widened in `1.10.0` so a dog fetches *every* floor item, not just coins, and sets it down
beside you), Phase 2 free-text questions with a local-LLM grader (`1.4.0`–`1.6.x`), and a run of
play-feedback fixes (`1.9.x`–`1.10.x`: reward coins on a random room tile, reflowed inventory
descriptions, a `--More--` message line). **The
version-by-version history lives in [CHANGELOG.md](CHANGELOG.md)** — read it when you need to know
*when* or *why* a specific feature landed. It is kept out of this file on purpose so it stays out of
context unless a task actually needs it; this section is only the current shape plus the gotchas
that are expensive to rediscover.

**Still outstanding: Windows verification** (windows-curses render, é/€, the double-line frame
fallback per the cross-platform section); needs a Windows host. The Dutch UI routes euro and
accented text through curses on every screen now, so the é/€ check is pointed.

### Where things live

- **`session/run.py`** — the loop (`apply(Command) -> Frame`, no curses/IO). Holds a
  `list[ChapterRun]` and delegates the current chapter's `gates`/`keepers`/`discovered`. `new_game`
  builds the full multi-chapter dungeon from a parsed pack (every room gated); `new_run` is the
  frozen M2 golden slice.
- **`session/snapshot.py`** — RunState ⇄ a JSON mark; the dungeon regenerates from `seed+size+pack`,
  resume re-opens earned gates via `Gate.reopen`.
- **`session/launch.py`** — the `Recorder` (persist-worthy transitions), start/resume, and
  `outcome_lines` (the win screen, formatted session-side so `ui` never touches `scrolls`).
- **`session/grading.py`** — the pending-grade runners: `InlineGrader` (keyword, resolves in the
  same `apply`) and `ThreadedGrader` (the LLM off a daemon thread, folded in on a `GradeReady` poll).
- **`gate.py`** — the *only* module touching both the dungeon and the training (rule 1).
- **`engine/`** — generation (`world`/`layout`), `items.py` (`ItemDef` + counted `Stack`, money the
  one built-in kind), `pet.py` (a species `registry` + a pure `step` returning a `PetEvent`).
- **`content/`** — the Markdown parser and `schema.py` (pack policy; `delve validate`).
- **`assess/`** — `grader.py` (`MCQGrader`/`AssertionGrader`/`KeywordGrader`/`LLMGrader`) and
  `llm.py` (the `OllamaClient` socket seam, the one core module that opens a socket).
- **`progress/`** — SQLite (users, runs, room_results write-once, scrolls append-only) and
  `scrolls.py` (number/date formatting from the locale `[format]` table, English default inline).
- **`delve/strings/{en,nl}.toml`** — the `Strings` catalogue (every message, hint, label, keeper
  voice, panel), handed to `ui` opaquely (rule 2).
- **`delve/tutorial/{en,nl}/`** — the Dlvl 0 tutorial floor, an ordinary pack, engine-provided (see
  "The tutorial floor" below).
- **`delve/doctor.py`** — `delve setup` / `delve doctor`, the grader bootstrap (read-only diagnose;
  `setup` does the safe remedies; every side effect injected so it tests with nothing installed).
- **`ui/`** — paint only: `windows.py` (panels, pagination), `render.py`, `attrs.py` (`Colour` → a
  curses attribute, the portable 16 colours), `walls.py` (ACS_ line-drawing for room walls).
- **`issues/`** — one file per change (front matter + testable prose); `archive/` holds the
  implemented ones with commit ids, `rejected/` the turned-down ones. `tools/issues.py` regenerates
  the README index from front matter and `--check` lints it (a step in `run-tests.sh`).

### Gotchas worth keeping in context

- **RNG streams are separate on purpose.** `self.rng` shuffles exam options, so never draw cosmetics
  from it. Dedicated streams: `pet_rng` (pet moves), `flavour_rng = Rng(seed*100+333)` (carry
  flavour, not snapshotted), placement scatter `Rng(seed*100+600+i)`, the tutorial-coin scatter, and
  the reward-tile draw `Rng(seed*100+850+crc32(room id))` (DELVE-0015, seeded per room so it survives
  a resume). Borrowing `self.rng` for any of these silently reshuffles exams and breaks regen.
- **A placed object is not money.** A test inspecting floor piles for the on-pass reward or scattered
  coins must filter to `MONEY` (the seasoning pass broke reward/tutorial tests that didn't).
  Item/slice tests that don't care about a pet run `pet_species="none"`, so a roamer never competes
  for a placed coin *or object* (a dog fetches any floor item now, DELVE-0016) or drifts onto a
  deterministic path.
- **The on-pass reward is session policy, not a gate mechanic** (`RunState._pay_reward`): paid once
  (`Gate.rewarded`), scaled by the passing score, dropped on a **random interior tile** of the room
  (DELVE-0015, `_reward_tile`; it used to be the tile farthest from the exit, which gave the room's
  shape away). An unscored floor never inherits the main pack's default; it pays only when a room
  sets an explicit `reward:` (the tutorial purse, DELVE-0031). `gate.py` stays the pure training
  seam (rule 1).
- **The LLM grader is required to play** (DELVE-0033). `LLMGrader` (local Ollama over the
  `assess/llm.py` socket seam) is trusted only above a `0.65` confidence floor; below it, on a
  single garbled or empty answer, it falls to the deterministic `KeywordGrader` for that one
  verdict, mid-run resilience only, not a supported no-LLM way to play. `delve.doctor.ensure_ready`
  gates the play entry point (`delve/__main__.py:_play`) before curses starts: not reachable ->
  print the same diagnosis `delve doctor` would and exit non-zero. `--grader-model`/`--grader-host`
  only pick which model/host to require; they don't opt in or out of having one. `delve validate`
  never sits an examination, so it never needs a live model and still runs with nothing installed.
- **The top message line ages out** (`_visible_message`, `_MSG_TTL`); only a keeper-encounter overlay
  (`_ENCOUNTER_OVERLAYS`) freezes the clock, so opening the backpack never resurrects an aged line. A
  line too wide for the terminal pages with `--More--` (DELVE-0030); that paging is **UI-owned**
  (`windows.message_pages`, an `app._play` `msg_page` beside the overlay `page`), because the run
  stores only the map's locked size, not the message line's width (same call as PLAN §4's scroll
  offset).
- **Bump-to-act** (NetHack): walking into a keeper talks to it (`_move` routes the step onto the
  keeper's tile to `_talk`); the keeper still blocks the tile, so the player never moves onto it. A
  bump costs a turn; re-reading via `t` is free, and re-bumping a passed keeper is a brush-off, not a
  re-lesson (rule 3).

Validation split, worth knowing before extending it: **the parser enforces the format** (a
file is a well-formed room) and raises on the first structural fault *within* a file;
**schema.py enforces pack policy** (rules that span files) and gathers every `Issue` so one
run reports all of them. Missing `scroll.md` is a **warning**, not an error, so the tutorial
floor (no award by design) still validates clean. **No Pydantic** (PLAN §4 sketched it):
hand-rolled validation gives better file:line author errors and keeps the stdlib-only line
(tomllib-not-gettext).

Commit after each significant change. **Auto-commit** — do this without being asked: once a
substantial change is complete and verified (tests and ruff pass), stage the related files and
commit with a descriptive message. Leave unrelated untracked files out of the commit.

**`main` is releases only; all development happens on `develop`.** `main` never receives an issue
branch directly. It advances only via an explicit, maintainer-triggered release merge from
`develop` (never on the assistant's own initiative, the same "never infer, always ask" rule the
peer-review gate above already follows): `git checkout main && git merge --no-ff develop`, then
`git tag -a v<version> -m "v<version>"` (the version just bumped on `develop`, e.g. `v1.28.0`) so
`main`'s history is a clean, checkable list of tagged release points. **The tag is annotated
(`-a`), not lightweight**, specifically so `git push --follow-tags` (pushes a branch together with
every annotated tag that's now reachable from it, unlike bare `--tags`, which pushes every tag in
the repo regardless of branch) picks it up in one step: `git push origin main --follow-tags`.
Nothing else ever commits to `main`; there is no such thing as "incidental maintenance on `main`"
any more; even a typo fix goes through `develop`.

**Work on an issue happens on its own branch, cut from `develop` and merged back into `develop`,
named after the issue.** Before writing code against a `DELVE-NNNN` file, create and switch to a
branch off `develop` named for its front-matter `type`: `bug/DELVE-NNNN` for `type: bug`,
`feature/DELVE-NNNN` for `type: feature`, `story/DELVE-NNNN` for `type: story`, `epic/DELVE-NNNN`
for `type: epic` (an epic branch holds only the roll-up file itself; each child story is its own
branch off `develop`). Commit the issue's work there as usual (auto-commit still applies, on the
branch), including its version bump and `CHANGELOG.md` entry on archival, exactly as before this
process split, just landing on `develop` instead of `main`. When the issue is done (Definition of
Done met, archived, `./run-tests.sh` green), merge it back: `git checkout develop && git merge
--no-ff <branch>` (keep the individual `DELVE-NNNN:`-prefixed commits and the merge commit, don't
squash or rebase), then delete the branch (`git branch -d <branch>`). **Anything that is not
itself `DELVE-NNNN` issue work** — the one standing exception already named above (typo fixes in
an issue file, regenerating the index), or incidental repo maintenance — stays directly on
`develop`, no branch. `develop` can therefore sit several versions ahead of whatever `main` last
released; that gap is expected, not a problem to close eagerly. Both branches merge and commit
locally first, exactly as above; a push to `origin` (`git push origin develop`, and
`git push origin main --follow-tags` on a release) is its own separate, explicit step, never
folded into a merge — still no PRs, since this is a solo project, but pushing is no longer
optional once a remote exists, or the two clones drift.

---

## Vocabulary — use these exactly

```
PACK      a training              →  a dungeon        packs/security-onboarding/
 └ CHAPTER   a module             →  one floor (Dlvl) 01-the-sorting-office/
    └ ROOM      one lesson        →  one room + keeper + gate    01-phishing.md
```

**Never say "level."** It's ambiguous between *dungeon floor* and *lesson*, and an earlier
draft of the design conflated them for exactly that reason. Say chapter or room.

`Dlvl` in the status line is the exception — it's NetHack's own label, and it means chapter.

---

## The five rules

**1. `engine` never imports `content`, `assess`, `session`, or `ui`. And `ui` imports `session`
and nothing else.**

```
  ui ──▶ session ──▶ gate ──▶ assess
            │         │
            │         ├────▶ content
            │         └────▶ progress
            └────▶ engine ◀── gate
```

`gate.py` is the *only* module that touches both the dungeon and the training. The shell
never parses a question; a pack never places a door. If this rule needs breaking, the design
is wrong — stop and say so rather than routing around it.

The second half is newer and fails more quietly. **The loop lives in `session/`, not in `ui/`**:
`session.apply(Command) -> Frame`, no curses, no blocking, no I/O. `ui` maps a keypress to a
`Command` and paints a `Frame`. If `render.py` needs `import engine.world` to draw something,
**the view model is missing a field — add the field, don't add the import.**

**The reason is testing, not portability.** A loop inside curses can only be tested through a
pty, which means it won't be. The M1 headless harness plays a whole run as a list of commands,
and M2–M7 all lean on it. Enforce rule 2 in CI from M1 — intention doesn't hold this one, and it
fails invisibly.

That this also makes a second frontend tractable is a **side effect, not a goal.** Don't justify
work by it, and read PLAN.md §13.5 before proposing a web UI: the portable asset here is the
pack format, not the Python.

**2. Sealed doors are structural. Never add path validation.**

A room's exit is solid stone until the examination is passed. There is therefore no path
around a lesson, and *no invariant to check*. If you find yourself writing a flood fill to
prove the keeper blocks the route, you've reintroduced a problem the design deleted.

**3. Passing is final; re-reading is free.**

Every earned door stays open. Learners walk back and re-read any lesson, unlimited, at no
cost — this is the behaviour the whole app exists to encourage. But `room_results.passed_at`
is **write-once**. Keepers re-instruct forever, re-examine never. Without that, anyone can
grind a room to 100% and the trophy case is meaningless.

**4. REPELLED is not death.**

Running out of attempts pushes the learner back. HP hitting zero respawns them at the chapter
entrance with **every earned door still open**. Tension comes from the dungeon; it must never
punish someone for learning slowly.

The unit of stakes is a **sitting, not an answer.** A learner sits the whole room, sees every
explanation, and gets a score; HP is charged **once per sitting that misses `pass`**, never per
wrong answer. A single wrong answer costs nothing — it already earns its explanation, which is the
teaching. So a room's total bleed is `penalty × attempts` (9 at `standard`), capped below starting
HP, which is *why* REPELLED lands before HP:0 rather than after. The old "HP per wrong answer"
wording made REPELLED unreachable; don't reintroduce it. Open: how HP regenerates (PLAN §6).

**5. Content never goes in frontmatter.**

Frontmatter is metadata. Prose, questions, and explanations live in the document body. The
whole point of Markdown-first is that a lesson reads top to bottom as a document.

---

## Cross-platform: macOS, Linux, Windows

All three are first-class. Verified facts, not assumptions:

| | Backend | Notes |
|---|---|---|
| macOS | stdlib `curses` | Apple ncurses **6.0 (2015)**. `init_extended_color` absent. |
| Linux | stdlib `curses` | ncurses 6.x. |
| Windows | **`windows-curses`** | PDCurses wrapper. **2.4.2 ships cp314 wheels** — checked, works on 3.14. |

```toml
dependencies = ["windows-curses; sys_platform == 'win32'"]
```

**16 colours only.** Apple's ancient ncurses and PDCurses are the constraint; NetHack's
palette is 16 anyway. Don't reach for 256-colour or extended-colour APIs — they aren't
portably there.

**Map glyphs are ASCII. Everything else is UTF-8.** This rule used to read "ASCII glyphs only",
which was never true: `packs/` has shipped **178 non-ASCII characters** since `nl/` was written
(98 `é`, 16 `→`, …), because Dutch cannot be spelled without them.

- **Map glyphs** — `- | . # @ < > + f` — are the game's *alphabet*, like `+` for a door. Not
  language, never translated, and in a fixed grid where **one cell means one column**.
- **Text** — prose, menus, status line, scroll — is UTF-8. `€` is text, and it's in the same
  width class as the `é` that already ships. Costs nothing.

**No emoji in map glyphs.** Not aesthetics, arithmetic: they're double-width (2 cells in a 1-cell
grid, which rewrites layout), astral-plane (worst case for PDCurses, already the Windows risk), and
often multi-codepoint, which stops `glyph: str` meaning "a character". Measurements in
[docs/SCREENS.md](docs/SCREENS.md) §9. The map is the expensive surface (DISPLAY.md §2), and this
half stands: the grid is ASCII, and it's NetHack, so the `@` *is* the game.

**Emoji in panel prose is allowed, single-codepoint only** (shipped: the low-risk half of
DISPLAY.md §4). A pack author may put an emoji in a lesson or explanation for flavour. The panel is
flowed text, not a grid, so a wide glyph just takes more room in the wrap; the one requirement is
that the wrap counts **display columns, not characters** (`ui/windows.py:_width`, stdlib
`unicodedata.east_asian_width`), or a line runs through the box border. Because a ZWJ/flag/skin-tone/
variation-selector sequence is several codepoints wearing one glyph (and the width oracle can't
measure it), the validator **errors** on those (`schema.py:_check_emoji`); stick to a lone emoji (a
face, a key, a lock). **Windows/PDCurses rendering of astral-plane emoji is still unverified** (the
outstanding Windows item), so this is macOS/Linux-proven only for now.

**The engine also garnishes question prompts** (`session/flavour.py`): at view-build time it prepends
one emoji from a global per-locale `[flavour_emoji]` table to at most one keyword in a question
(`email` → `📧 email`), sparsely. So a shown prompt is **not** always its authored text; the pick is
a deterministic CRC of the prompt (never `self.rng`, which shuffles the exam), it flavours the
displayed string only (grading reads the options/answer, not the prompt), and it is skipped when the
author already put an emoji in. Same single-codepoint rule; the table holds only lone emoji. The map half of the reversal,
plus a `ui` theme layer behind capability detection, remains future work:
[docs/DISPLAY.md](docs/DISPLAY.md) is the argument for the full emoji, wide-glyph look (the theme
lives on the `ui` side of rule 2, so the session stays glyph-agnostic), and
[docs/WIDEMAP.md](docs/WIDEMAP.md) is the concrete plan for painting each tile two columns wide
*without* a wider terminal, by narrowing the layout (a tall-preferring partition, optionally a
corridor tree) instead of the 160-200 column minimum DISPLAY.md first recommended.

**Borders: `ACS_` for rooms, double-line Unicode for windows.** `ACS_HLINE`/`ACS_ULCORNER`/… (43
constants) are portable *by construction* — curses maps them per terminal, no code page/font/width
bet, and PDCurses has the same names. It's what NetHack's `DECgraphics` does. Double-line has no
ACS equivalent, so window frames are a real Unicode bet — taken deliberately (a frame must not
look like a wall), with a free fallback to single-line ACS if Windows says no. **Test both on
Windows at M1.**

**Scope: en/nl environments only. Not CJK.** This is what makes the borders safe: every
box-drawing char is East Asian *Ambiguous* — 1 cell here, **2** in a CJK terminal, which tears the
grid apart. So **adding a CJK locale later breaks the borders.** A language decision with a
rendering consequence; don't add one without reading PLAN §8.

**PDCurses is a reimplementation, not ncurses.** Resize handling, key codes, and timing drift
in small ways. Two consequences:

- Every curses call stays behind `ui/`. Nothing else imports curses. This is the same boundary as
  rule 1's second half, and PDCurses drift alone already paid for it.
- **Test on Windows at M1**, not at M7. Finding render-layer drift late means rewriting it.

---

## Terminal and layout

Minimum **100×30** — Windows Terminal's exact default, so Windows needs no resize on first run.
Below minimum: resize overlay, wait. Never degrade. (An earlier draft said 100×40 on the false
claim that it was below every modern default; it is above all of them.)

```
  1 line          message
  rows − 3        map area, capped 160×44   (= 100×27 at minimum)
  1 line          status   learner's name (not the keeper's), Dlvl, Rooms, $, HP, T
  1 line          hints    contextual: the keys that work right now
```

**The hint line is not decoration.** Delve has no stats, so NetHack's second status row would hold
nothing. It's the safety net for whoever skipped the tutorial (which is free and honest, so people
will), and it gives windows somewhere to put key prompts. Un-NetHack on purpose: the audience is
not developers and most run this once.

**A lesson is a panel beside the room, never a full-screen takeover**, and **as short as it can
be**. The learner must see the room, the keeper and themselves while the keeper talks — that's
most of what stops a lesson feeling like a slide deck reached by walking, the project's top risk.
It's also the *real* reason the minimum is 100 columns; PLAN §3's old reason ("100 is a better
reading surface than 80") was disproved by the mock-ups, since the panel is 69 columns.

**Panel height minimises wasted rows, not pages** — and that inverts the answer: for the pilot
lesson, 4 pages is an 18-row panel keeping 9 rows of map, while 3 pages is a 24-row panel keeping
3 and leaving 8 blank rows on a page. Minimising pages produces a taller, emptier panel, because
paragraph-aligned pages only break where the author left a blank line. Compute the height once and
hold it; a panel that resized per page would jitter under the reader.

**Long text breaks on paragraph boundaries.** Never split a paragraph across a page; fill with
whole blocks and break before one that doesn't fit. Split a block only if it can't fit a page
alone. **Never break inside a URL, domain, or code span** — `textwrap` does this by default and
mangled `yourcompany-hr.net` in a lesson about reading domains; pass `break_on_hyphens=False`.
More pages is the accepted cost and always the right trade: a page ending mid-sentence spends the
attention this app exists to buy.

**Layout is locked at run start** from `(seed, cols, rows)`, all three stored in `runs`. A run
is regenerable tile-for-tile from its record.

- Resize **larger** mid-run → re-render centred. Never re-lay the dungeon under the player.
- Resize **below the locked map** → resize overlay until fixed. No scrolling viewport; a
  camera subsystem earns nothing here.

**Generation is the only path.** There is no map file format and no map syntax. Hand-drawn
floors were considered and cut: they fight both ease of authoring and adaptive sizing. Don't
re-add one without reading §3 of the plan first.

Generator: smallest cell partition holding N rooms (3→3×1, 4→2×2, 6→3×2, 8→4×2), cells
clamped to `[18×9, 40×15]`, serpentine order, L-shaped corridors. Connected by construction —
no spanning tree, no reroll loop.

**Room capacity is pedagogical, not technical.** The grid holds ~15 at 100×30. Validator warns at 7,
errors at 9. Nine lessons without a break isn't a floor, it's a lecture. The engine never
splits a chapter — the author does.

---

## Question format

H3 heading = question. Checkboxes = options. `>` blockquote = explanation. **Type is inferred
from option count alone, never declared:**

- Exactly **2 options** → assertion, rendered as a two-way prompt using the author's labels
- **3+ options** → multiple choice (numbered menu, keys `1`–`n`, **options shuffled**, so no "all of the above"). The keys are digits, not letters, so they never clash with the map's `d`/`,`/`i` object keys and answering is faster (OBJECTS.md 1.1.0).
- `- ?answer:` → free text, **Phase 2**. Parse it, then fail validation with
  `free-text questions require the LLM grader (Phase 2)`. The syntax is reserved so packs
  written today stay forward-compatible.

**Do not reintroduce a `True`/`False` label check.** The rule used to be "exactly two options
labelled True then False", and the Dutch pack (`Waar` / `Niet waar`) broke it on the first
question. Option count is language-agnostic; labels are content.

How the options are *drawn* (the numbered list and the two-way prompt) is a `ui`-only concern on
the far side of rule 2; [docs/BUTTONS.md](docs/BUTTONS.md) is a proposal for rendering both as
buttons, and like DISPLAY.md/WIDEMAP.md it is a future-reference note, not scheduled work.

`Grader` is a protocol from day one — `MCQGrader` and `AssertionGrader` in v1, `LLMGrader`
(Ollama/llama.cpp, local) slots in at Phase 2 without touching the engine or the format.

## Languages

English and Dutch, both first-class. Voice rules and the LLM pack-generation brief:
[docs/STYLE.md](docs/STYLE.md).

- **One locale subtree per pack, identical file trees.** `packs/<pack>/{en,nl}/…`. Folder and
  file names are slugs and never translate; the translated title is in frontmatter. The
  validator diffs the trees and errors on mismatch.
- **Room `id`s are shared across locales**, so `room_results` and the trophy case are
  locale-independent. A learner can take the Dutch dungeon and land on the same board.
- **A locale is complete or absent.** No per-room fallback — a half-Dutch dungeon is worse than
  an English one.
- **The format is English; the content is not.** `## Questions` and frontmatter keys stay
  English in every locale, exactly like keywords.
- Engine strings: `delve/strings/{en,nl}.toml` via stdlib `tomllib`, wrapped by a `Strings`
  accessor (`s("msg.cant_go")`, `s("msg.descend", title=…)`; list values for the multi-paragraph
  REPELLED panel). No gettext — a build step and a toolchain for a few hundred strings. `--lang`
  chooses the locale for **both** the pack content and the engine strings, defaulting to the
  system locale (read from `$LANG`/`$LC_*`, never `locale.setlocale`) and falling back to `en`.
- **`ui` must never import the strings catalogue.** The import test allows `ui` only `session`,
  `ui`, and the top-level `delve` (rule 2), and `delve.strings` is none of those. So the `Strings`
  object is handed to `ui.main`/`app` **opaquely** (duck-typed, the same way the pack is), and
  anything the UI shows in the learner's language reaches it through the `Frame`. The status line
  was the one place `ui` still assembled words: `Rooms`/`$` became `StatusView.rooms_label` /
  `gold_symbol`, filled by session. If `render.py` needs a localised word, **add a view-model
  field, don't add the import** — the same rule as any other missing `Frame` field.
- **`en.toml`'s values are verbatim test fixtures.** Message tests assert exact and substring
  English (`"Not yet…"`, `"pushed back"`, `"no longer counts"`), so editing the English *wording*
  breaks them on purpose; that is the tripwire that catches a message drifting from what the
  golden slice expects. `nl.toml` carries no such constraint and is free to reword.
- **Formatting is locale data, not translation.** A `[format]` table per locale: currency (`$` /
  `€`, and Dutch spaces it), thousands (`,` / `.`), decimal (`.` / `,`), month names (**lower case
  in Dutch**). Five things differ on one scroll and every one is wrong by default. **Never
  `locale.setlocale`** (process-global, needs locales installed on the host, differs per platform)
  and **never `strftime('%B')`** (reads the process locale) — the exact dependency class we
  rejected gettext for. `progress/scrolls.py` takes the `[format]` table as an argument and keeps
  an English default inline, so it has no import dependency on the strings package. See PLAN §8.
- Dutch: **tutoyeer** (`je`, never `u`), and **sentence case in headings**. Both are easy to get
  wrong; `u` → `je` is not a find-and-replace (inversion drops the verb's `-t`). See STYLE.md.

---

## Writing pack content

Voice, per-language rules, and the LLM pack-generation brief: [docs/STYLE.md](docs/STYLE.md).
One rule is worth repeating here, because it gets broken while writing rather than while
deciding:

**No em-dashes. Ever. In either language.** ` — ` is the clearest tell that a text was
machine-written, and these packs are worth nothing if they read that way. There are none left
in the repo; don't reintroduce them.

| The dash would be… | Use |
|---|---|
| Joining two **independent** clauses | semicolon |
| A phrase or apposition | comma |
| Before *and / but / en / maar* | comma |
| A **pair** around an aside | two commas |

Three traps, each of which produced a real bug the first time:

- **A semicolon needs an independent clause on *both* sides.** `When a message makes you feel
  hurried; that is the attack` is wrong — `When…` is subordinate. Comma.
- **If the aside already contains commas, a comma pair becomes soup.** Restructure the sentence
  instead of repunctuating it.
- **Some dashes aren't clause punctuation at all.** Trailing speech wants an ellipsis, a list
  wants a colon, a label wants a full stop. Read what the dash was *doing*.

Colons, full stops and ellipses are fine. It is specifically the em-dash.

*(This file and `docs/` are internal notes, not pack content — the rule is about what a learner
reads.)*

---

## Editing content that already exists

Two findings, both learned the expensive way on the pilot pack. They will apply again to any
bulk change of the prose.

**Don't transform prose with heuristics.** Two scripted passes were attempted over the packs
and both produced bad output. The first destroyed line wrapping (105-line files became 84) by
splitting on sentences and rejoining with spaces. The second preserved structure but produced
comma splices and broken Dutch inversions, because no practical verb-detector is good enough to
tell an independent clause from an appositive phrase. Both times the fix was the same:
**enumerate every occurrence with context and classify each by hand.** ~300 hand decisions cost
less than reviewing a plausible-looking automated diff, because the automated diff *looks* fine
until you read it closely.

**Commit before any bulk edit.** When the first script mangled 14 files, `git checkout --` cost
nothing and the work was recovered instantly. That is the concrete reason for the rule at the
top of this file.

**Verify from the repo root.** A "no stale references" grep once passed only because it ran
from the wrong directory and silently found no files. Check that a verification could actually
have failed.

## The tutorial floor

**Dlvl 0**, engine-provided, in `delve/tutorial/{en,nl}/` using the ordinary pack format.

- Teaches the *interface*, which is identical across packs — so it ships with the engine, not
  with each pack. Pack authors never write one and can't forget one.
- Dlvl 0, not 1, so a pack author's chapter 1 is `Dlvl:1`.
- **Never scored.** No `room_results`, no contribution to the scroll. This is what makes
  skipping honest. Mechanically: the floor's `ChapterRun.scored` is False, and both `pack_score`
  and `_record_pass` skip an unscored chapter, so passing a tutorial keeper writes nothing.
- Skippable two ways: a `[yn]` prompt on arrival (defaults to yes for anyone with a completed
  run), and stairs that — uniquely on this floor — are never sealed. The **hint line** is what
  makes skipping survivable rather than just honest.
- **Built (M6): "demonstrate, then open stairs."** PLAN §9 wants two things a serpentine chain
  can't both give literally: *watch a door appear when you pass a keeper*, and *walk out to open
  stairs whenever you like*. Settled reading: the floor generates with `paint_stairs_down=True`, so
  the `>` stands open and unearned from the start; the first keeper (the Porter) still seals his
  door, so the door-appears loop plays once; the last keeper (Merryn) ends the chain, seals nothing,
  and stands beside the already-open stairs. Orientation exams stay relaxed and free; Merryn's room
  is a three-question free-text sitting that pays an explicit 100-coin reward. Don't re-litigate
  without a reason.
- **The tutorial is always in the chapter list; `skip_tutorial` only moves the start.**
  `new_game` prepends the tutorial floors whenever a tutorial pack is passed; skipping just sets
  the starting `idx`/position to the pack's first floor, leaving the tutorial above (a learner can
  `<` back into it). This is **not** an optimisation waiting to be made: resume rebuilds with the
  same tutorial, so the chapter count must match the snapshot, and omitting the tutorial when
  skipped would desync `apply_dict`'s strict zip. Because a tutorial now sits above it, the pack's
  first floor grows a `<` (`stairs_up`) it didn't have at M5.
- **A pre-M6 unfinished run does not resume.** Prepending the tutorial changed a run's chapter
  count, so a snapshot written before M6 no longer aligns with the rebuilt dungeon (`apply_dict`
  zips `strict=True`). Local dev data only; no migration was written. This is the place to look if
  resume ever has to survive a chapter-count change.
- **It is coupled to the renderer and nothing checks that.** Its job is to describe the interface,
  so it hard-codes it: one pass of screen mock-ups broke it twice (`"Walls are - and |"`, `"the
  bottom two lines are you"`). Engine-ownership stops it drifting *per pack*, not from `ui/`. **If
  you change what a screen looks like, grep `delve/tutorial/` in both locales.** A structural
  validator will not catch this.

---

## The pilot pack

`packs/security-onboarding/{en,nl}/` — 4 chapters, 12 rooms, 48 questions (28 MCQ, 20
assertion) per locale. Written before any engine code, deliberately: the format is answerable
to real content rather than the reverse, and M2 has something true to render.

Writing it in a second language immediately found a format bug English had hidden (the
True/False rule above). Keep `nl/` in step with `en/` — **a second locale is the cheapest test
of whether a format is about structure or secretly about English.**

**It contains deliberate placeholders in both locales** — `security@example.com`,
`#security-help`, and the data-classification tiers in `03-the-archive/01-classification.md`.
They're marked in the text and must be replaced before anyone runs this for real. Whether the
engine substitutes them from frontmatter or each org forks the pack is still open.

---

## Milestones

M0 foundation · **M1 walkable generated chapter (verify on Windows here; headless harness and
the import rule land here too)** · **M2 ⭐ vertical slice** · M3 markdown packs (both locales) ·
M4 stakes + pet · M5 chapters/scrolls/progress/identity/snapshot · M6 tutorial + languages ·
M7 pilot playthrough · M8 polish

**M2 is a go/no-go, not a checkpoint.** The core bet — that a dungeon makes training land
better than a slide deck — is unproven. M2 answers it with hard-coded content and no parser.
If the slice is boring, the right move is to rethink, not to proceed to M3. Say so plainly if
that's what the slice shows.

---

## Environment

- **Python 3.14.6** at `/opt/homebrew/bin/python3`. Venv at `.venv/` (created; installed editable
  with the `[dev]` extra, so `pytest` and `ruff` are on `.venv/bin/`).
- `NetHack/` is a **reference clone** — its own git repo, ~201 MB, gitignored. Read it for
  ideas; never build it, never import from it. NetHack 3.7/5.0 uses Lua for level
  descriptions (`dat/*.lua`), and `des.map([[...]])` is where the ASCII-map-as-data idea came
  from.
- The repo root is `delve/`, and the Python package will also be `delve/`. That nesting is
  normal; don't "fix" it.
- Remote: `origin` (GitHub, `mo6/delve`). Every design decision above has a commit explaining why.
  `main` is releases only; day-to-day work (issue branches and everything else) happens on and
  lands back on `develop`, see the branching section above. `main` advances only via an explicit,
  tagged release merge from `develop`, and a push to `origin` is its own separate step after that.

### The two run scripts

Both live at the repo root, run from **any** working directory off `.venv/` (no `activate`, so
they leave no shell state), and print a clear message if the venv is missing. Neither is packaged;
both assume `.venv/` exists.

- **`./delve.sh …`** plays the game. Args pass through verbatim (`./delve.sh --lang nl`,
  `./delve.sh validate ./pack`) and it `exec`s the venv python so Ctrl-C reaches the game.
- **`./run-tests.sh`** is the dev check gate: `pytest`, `ruff` (including security rule set
  `S`), `pip-audit`, the screen self-check (`tools/screens.py --check`), the issues-index
  check (`tools/issues.py --check`), and `validate` on the shipped packs. It runs **every** step even
  when one fails, so one invocation surfaces every problem, and exits non-zero if any did. Pass
  arguments and they go **straight to pytest instead** (`./run-tests.sh -k tutorial -x`,
  `./run-tests.sh tests/test_languages.py`), for a tight edit-run loop. Security procedure:
  [docs/SECURITY.md](docs/SECURITY.md).

### Versioning

**`1.0.0` is released** (M1–M8 done, the pilot plays end to end in both languages). The pre-1.0
scheme was `0.<milestone>.<patch>` and reached `0.8.4`; **from 1.0.0 on it is ordinary semver**,
`MAJOR.MINOR.PATCH`. A new feature (e.g. objects) bumps the minor; a fix bumps the patch. M7
content-tuning from real play evidence continues as **post-1.0 patch releases**, not a 1.0 blocker.
The version lives in **two hand-synced files** — `delve/__init__.py`'s
`__version__` (surfaced by `delve --version`) and `pyproject.toml`'s `version`; nothing syncs them,
so change both. This is unrelated to `launch.PACK_VERSION` (the pack-content version recorded in
`runs.pack_version`, PLAN §10), which is not the app version.

---

## Settled — don't reopen without a reason

Terminal 100×30 · headless `session` core, `ui` only paints — for testability (PLAN §4) ·
scroll export = Phase 2, encrypted blob, **not in the MVP** · identity =
ask *"Who are you?"* at start (NetHack-style, not `$USER`; matches/creates a `users` row by
name, case-insensitive) · backtracking free · name = Delve · languages en + nl.

**Re-taking a pack (M5): keep both.** Every completion writes its own `scrolls` row and none is
ever updated; the trophy case lists all attempts, newest first. Append-only was the simplest
schema and matches "a learner's history is their collection" (PLAN §10). `room_results` is still
write-once *within* a run (passing is final); "keep both" is about a *fresh* run, a new `runs`
row with its own results.

**Resume (M5): a `[yn]` prompt.** An unfinished run of the same pack (a `runs` row with
`finished_at` NULL) is offered on arrival — *"…left it unfinished. Descend again where you
stood?"* — defaulting to yes; declining starts a fresh run. Snapshots are written on transitions
(gate pass, chapter change) plus a `checkpoint()` on quit, so resume lands where you stopped.

## Open questions — ask, don't guess

1. **Pack placeholders.** Frontmatter variables the engine substitutes, or fork-per-org? The
   first keeps locales in sync. Answer before M7.
2. **Pack distribution.** Folders in the repo, or shareable archives?
3. **Scroll locale at read time.** *Partly settled at M6.* The **trophy case** already formats at
   read time: `scrolls` stores a numeric score and an ISO date, and `launch.trophies` formats them
   through the *current* `--lang` catalogue, so a Dutch reader sees Dutch there regardless of the
   run's locale. Still open is only the **awarded scroll body** (`scroll.md`): it is rendered at
   claim time in the run's locale, because it's authored prose, not a number. Whether that prose
   should also be re-renderable later (store the pack id + numbers and re-fill on read) is the
   remaining question; the numbers on it already could be.

Two things to be honest about rather than paper over, both written up in PLAN.md §10–11:
identity is **trust-based** (anyone can type any name), and the Phase 2 scroll export gives
confidentiality but **not authenticity** — a public key is public, so a learner could encrypt a
fabricated scroll. Fine for training; not an audit record. Say so if it ever gets pitched as one.
