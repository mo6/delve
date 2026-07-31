# Information screen: charts, tabs, and LLM status

**Status: promoted to an epic, [DELVE-0035](../issues/DELVE-0035-information-screen.md); tab strip (DELVE-0040), tab pills/arrow-keys/title (DELVE-0041), Scoring → Now's bars (DELVE-0042), Scoring's coloured bars plus its rename from "Progress" (DELVE-0043), and a fourth primary tab, Status, with app/run diagnostics (DELVE-0044), have landed; the rest of §9's table has not.** This file stays the design essay (the *why* and the constraints); the issue is the *what*, with its own child stories cut per §9 below.

The prompt is real: the inventory panel is correct and thin. Claude Code's Stats UI (tabs, a contribution heatmap, token charts, coloured chrome) shows how much more a terminal panel can carry when it stops being only a list. This note asks what of that belongs in Delve, what would fight the dungeon, and how to grow an *information screen* without turning a NetHack-style pack into a dashboard that eats the room.

---

## 1. What we draw today

`i` opens a right-anchored double-line panel titled **Your pack** (`item.inv_title`). The session builds a `TextView`: coins as one plain line, then each carriable as a bold name plus its `look` body. Empty pack gets `item.inv_empty`. Esc closes. Drop stays on `d`. The map stays visible on the left (the standing rule: a lesson is a panel beside the room, never a full-screen takeover).

```
                            ╔══════════════════════════════════════════╗
                            ║ Your pack                                ║
                            ║                                          ║
                            ║ 136 coins                                ║
                            ║ urgent memo                              ║
                            ║ A printed email that wants you hurried.  ║
                            ║ The sender almost looks right…           ║
                            ║                                          ║
                            ║ (end)                                    ║
                            ╚══════════════════════════════════════════╝
```

That is the whole surface: a list and a description. Progress lives only on the status line (`Rooms:0/3`, `HP:12(12)`, `$:136`, `T:174`). The local LLM, when configured, grades free-text answers and is otherwise invisible (`delve doctor` / `delve setup` are the only status UIs; [PHASE2.md](PHASE2.md)).

So the gap is not "inventory lacks items." It is that **`i` is the only mid-run panel that is about the learner rather than a keeper**, and it currently holds only objects.

---

## 2. What Claude Code is doing (and what to steal)

The reference UIs (Stats → Overview / Models) are useful as a *pattern library*, not a product to clone:

| Pattern | Why it works in a TUI | Delve translation |
|---|---|---|
| **Primary tabs** (`Settings` / `Status` / `Usage` / `Stats`) | One key family switches mode without leaving the screen | A short top row inside the panel: `Pack` · `Scoring` · `Grader` · `Status` |
| **Sub-tabs** (`Overview` / `Models`) | Second axis without a deeper menu tree | Under Scoring: `Now` · `Rooms` · `History`; under Grader: `Live` · `Run` |
| **ASCII / block chart** (tokens-per-day step lines) | Dense history in ~20 rows | Score-by-chapter bars, HP bleed, grade latency sparkline |
| **Distribution / heatmap** (GitHub-style contribution grid) | Instant "where did effort land" gestalt | Room-pass grid by chapter, or floor item scatter (see §6) |
| **Coloured selection chrome** (filled pill on the active tab) | Selection without a mouse | Reverse-video or solid `bar_attr` pills (BUTTONS.md already uses this) |
| **Coloured borders** | Mode identity at a glance | Tint the double-line frame by active tab (§8) |
| **Footer key chord** | Discoverability | Already Delve's habit: the hint line owns keys |

What **not** to steal:

- **Calendar contribution graphs.** Delve is a sitting inside one run, not a year of commits. A week-of-year heatmap would mostly be empty and would invent a product Delve is not.
- **Multi-model token markets.** One local grader model per run (`--grader-model`), not a fleet.
- **Full-screen dashboards.** The map must stay in view; a 73-column panel is the budget (`windows.PANEL_W` / `TEXT_W` = 69). Charts that need 120 columns do not fit.
- **Live network telemetry as a game feature.** The grader is local and optional; the screen must degrade cleanly when the model is off (keyword floor), the same way `doctor` already does.

---

## 3. Constraints that shape any expansion

Same non-negotiables as the rest of the UI (CLAUDE.md):

1. **Rule 2.** `session.apply(Command) -> Frame`; `ui` only paints. Charts are *presentation* of numbers the session (or progress store) already knows. `ui` must not open SQLite or call Ollama. If a chart needs a new number, add a view-model field.
2. **Panel beside the room.** Right-anchored, ~73 columns, height minimises wasted rows. Growing content means more *pages* or denser chrome inside the box, not a takeover.
3. **Sixteen colours only.** Portable palette via `ui/attrs.py`. No 256-colour charts; encode series with the bright/base eight plus bold (NetHack's own trick).
4. **Double-line frame, ASCII map.** Borders may take colour; they must not look like room walls (`ACS_` single-line). Windows already use Unicode double-line with an ACS fallback path for Windows (CLAUDE.md cross-platform).
5. **Both locales.** Every new label goes through `Strings` (`en.toml` / `nl.toml`). Chart axis words and tab names are UI chrome, not pack content.
6. **Objects never gate progress** ([OBJECTS.md](OBJECTS.md) §2). A fancier pack view must not invent "you need the USB stick to open the door." Progress charts show *what happened*; they do not become a second gate.
7. **Passing is final; re-reading is free** (rule 3). Room scores on a progress tab are write-once history, not a grind meter.

---

## 4. Name the surface: pack vs information screen

Two product readings, and they should stay distinct in the design even if they share one key:

- **Pack (inventory).** What you hold: coins, memos, coconuts. Read-only look, drop elsewhere. This is what `i` means in NetHack and what learners already expect.
- **Information screen.** How the *run* is going: rooms cleared, score trajectory, grader health, maybe a tiny chronicle of messages. Claude Code's Stats is this class of surface.

**Recommendation.** Grow `i` into a **tabbed information panel** whose *default* tab is still **Pack**, so the key's meaning does not rotate under people who only want to check coins. Extra tabs are additive. Alternative: keep `i` pure and bind a second key (e.g. `C` chronicle / `S` scoring). That is cleaner semantically and costs a hint-line slot; prefer it only if playtests show Pack and Scoring fighting for attention.

Either way, the view model should stop being "a `TextView` of item blocks" and become something like an `InfoView(tab, subtab, …)` the pager and tab strip both understand. Menus and lessons stay on their own overlay kinds; do not overload `TextView` until it breaks.

---

## 5. Sub-navigation

Borrow Claude Code's two-tier strip, drawn *inside* the panel so the outer double-line frame stays the mode boundary.

```
╔══════════════════════════════════════════════════════════════════════╗
║ [ Pack ]  Scoring  Grader                                           ║
║           [ Now ]  Rooms  History                                    ║
║                                                                      ║
║   …body for the active sub-tab…                                      ║
║                                                                      ║
║ (end)                                                                ║
╚══════════════════════════════════════════════════════════════════════╝
```

**Keys (shipped, DELVE-0055/DELVE-0056).** While the overlay is open, map keys are already suspended for inventory, so a small reserved set is free. `↑`/`↓` move keyboard focus *between* the two rows rather than cycling within one, the same two-level split Claude Code's own tab UI uses; `←`/`→` (and `Tab`/`Shift-Tab`) then cycle whichever row currently has focus, so the same keys reach the sub-tab strip once focus has moved there:

| Key | Action |
|---|---|
| `↑` / `↓` | Move focus between the primary row and the active tab's sub-tab row (a no-op with nothing to focus, e.g. Pack/Grader/Status) |
| `Tab` / `Shift-Tab` or `←`/`→` | Cycle whichever row currently has focus |
| `[` / `]` | Cycle sub-tabs directly, regardless of which row has focus |
| `1`–`n` | Jump to primary tab *or* select a listed item on Pack (pick one; do not dual-bind) |
| `Esc` | Close (unchanged) |

The row under focus draws its active tab as the filled pill (DELVE-0041's `bar_attr` treatment); the other row's active tab stays visible but plain (bold colour, no fill), so the two can never look identical (DELVE-0056). Hint line carries the chord for the active tab only (`hint.inventory` today is just "Put it away: Esc"), e.g. `Tabs: left/right  Rows: up/down  Put away: Esc`.

**Primary tabs worth shipping eventually**

| Tab | Job | Data already in reach |
|---|---|---|
| **Pack** | Hold / look | `player.gold`, `player.inventory`, item `look` |
| **Scoring** | Am I answering correctly? | `Rooms a/b`, chapter list, per-gate `passed_score` / sittings from the run (and `room_results` for history across runs) |
| **Grader** | Is the local model alive? | Model name from launch, last grade latency, fallback count; see §7 |
| **Status** — **done, DELVE-0044** | What's actually running? | App version, active pack/locale, terminal size, grader model/host if configured |

Optional later: **Log** (today's message history on its own overlay) folding in as a fifth tab so `i` becomes the one "about me" key. Only if the message log's current binding feels redundant.

---

## 6. ASCII charts that fit 69 columns

The panel inner width is **69**. Charts must be readable at that width and at the panel heights SCREENS.md already budgets (often ~18 body rows when a map strip remains). Prefer *one* chart per sub-tab plus a short legend; Claude Code's density works because the whole terminal is the chart.

### 6.1 Horizontal bars (best first chart)

Score per chapter, or HP remaining vs start:

```
 Chapters
 1 Sorting office   ####################········  92%
 2 The archive      ##############··············  71%
 3 The vault        ····························   — 
 HP                 ############········  12/12
```

Implementation is trivial string padding; colour the `#` run green/yellow/red by threshold. No new dependency. Works with colour off (density still reads).

### 6.2 Sparkline / step strip

Grade latency or gold over turns, one row:

```
 Grade ms  ▁▂▁▃▅▂▁▁▄█▃▂   last 520ms  avg 480ms
```

Unicode block elements (`▁▂▃▄▅▆▇█`) are one column each and survive the same East-Asian-Ambiguous bet the window frames already take (Western terminals). Keep an ASCII fallback (`.:-=+#`) behind the same capability bit DISPLAY.md argues for.

### 6.3 Step / line chart (Claude Code "Tokens per Day")

Possible, but hungry: axis labels, legend, 3 series → 12+ rows. Only worth it for **Grader → Run** if we accumulate per-sitting token counts (§7). Cap series at two (prompt vs completion, or LLM vs keyword fallback share). Y-axis as short SI labels (`0`, `1k`, `2k`), X as sitting index not calendar dates.

### 6.4 Distribution map (the nice-looking one)

Claude Code's Overview heatmap is a **calendar of intensity**. Delve has no calendar of play inside a run. Useful analogues that still look like a "distribution map":

**A. Room grid (recommended).** One cell per room, grouped by chapter, filled by pass score or attempts:

```
 Pass map                         less ░ ▒ ▓ █ more
 Dlvl 1  ░░██▒▒██░░░░
 Dlvl 2  ░░▒▒░░░░····
 Dlvl 3  ············   · sealed   ░ sat  ▒ ok  █ clear
```

This is honest Delve data (`gates` / `room_results`), reads at a glance, and teaches the chapter shape without spoiling the floor plan (it is not the dungeon map; it is a progress glyph row).

**B. Floor scatter (flavour).** A tiny ASCII of the *current* chapter showing where coins / objects still lie vs collected. Cute, and dangerous: it can spoil exploration, which is why money is on tiles in the first place ([OBJECTS.md](OBJECTS.md) §5). If ever built, gate it behind an explicit "reveal loot map" after the chapter is cleared, or show only *collected* tiles.

**C. Attempt histogram.** Bars of sittings-to-pass per room. Teaching signal ("phishing took three sittings; passwords took one") without a calendar fiction.

**D. Do not build.** A GitHub-style year heatmap of "days you played Delve." Wrong product; empty for a one-sitting pilot; belongs in a trainer dashboard outside the dungeon if anywhere.

---

## 7. Local LLM status (tokens, response times)

Phase 2 already runs a local Ollama model for free-text grading ([PHASE2.md](PHASE2.md)). Until DELVE-0053, `assess/llm.py:OllamaClient.chat` returned **only** `message.content` and discarded the rest of the JSON body; it now returns a `ChatReply(text, metrics)`, and `LLMGrader.metrics` (a `GraderMetrics` accumulator) folds every call's numbers in as the run plays. Ollama's non-streaming `/api/chat` reply commonly includes:

| Field | Meaning | UI use |
|---|---|---|
| `model` | Model that answered | Header: `qwen2.5:3b` |
| `total_duration` | Wall ns for the call | "Last grade: 520 ms" |
| `load_duration` | Model load ns | Distinguish cold vs warm |
| `prompt_eval_count` | Prompt tokens | "In: 180" |
| `eval_count` | Completion tokens | "Out: 40" |
| `prompt_eval_duration` / `eval_duration` | Phase timings | Optional detail / tok/s |

None of this is on the `Frame` yet; `GraderMetrics` lives on `LLMGrader` only, reachable via `ThreadedGrader.grader.metrics` (DELVE-0053). A Grader tab still needs a story to copy a summary onto the view each render:

- model name and host (from launch flags; already known at the edge)
- reachable? (last `available()` / last grade outcome)
- last latency ms, max (`GraderMetrics.last_latency_ms` / `.max_latency_ms`; no rolling average kept yet)
- tokens in/out this run (`GraderMetrics.prompt_tokens` / `.completion_tokens`, already summed)
- grades via LLM vs keyword fallback (`GraderMetrics.llm_verdicts` / `.keyword_verdicts`)
- last confidence value when the LLM path won (not yet in `GraderMetrics`; add if a story wants it)

```
╔══════════════════════════════════════════════════════════════════════╗
║   Pack   Scoring  [ Grader ]                                        ║
║            [ Live ]  Run                                             ║
║                                                                      ║
║  Model     qwen2.5:3b @ localhost:11434                              ║
║  Status    warm · last grade 520 ms                                  ║
║  This run  In 2.1k   Out 480   LLM 7   keyword 1                     ║
║                                                                      ║
║  Latency   ▁▁▂▃▂▁▄█▂▁  (sittings)                                    ║
║                                                                      ║
║  Below 0.65 confidence falls to keywords; that is normal.            ║
║ (end)                                                                ║
╚══════════════════════════════════════════════════════════════════════╝
```

**Rules for this tab**

- **Never block `apply` to refresh.** Poll cached stats from the last grade; a "refresh" key may re-hit `/api/tags` only if we accept a short stall, or push it to `doctor` and keep the in-game tab passive.
- **Offline is a first-class state.** "Keyword floor · model not configured" is success, not an error banner, matching PHASE2's no-model policy.
- **No per-token cost anxiety.** Local model, zero marginal money (PHASE2 §7). Show tokens as *engineering honesty* and teaching ("this is what a small judge costs"), not as a bill.
- **Seam stays in `assess/llm`.** Extend `chat` to return a small `LLMReply(text, metrics)` (or a side-channel on the client); `LLMGrader` / `ThreadedGrader` record metrics; session copies summaries onto the view. `ui` still never imports `assess`.

`delve doctor` remains the deep diagnostic; the in-game tab is the *during play* glance.

---

## 8. Coloured borders

Today `_box` in `windows.py` draws the double-line frame with default attributes (white / terminal foreground). Colouring the frame is a low-cost, high-signal upgrade and matches what makes the Claude Code chrome feel intentional.

**Proposal.** Tint the entire frame (corners + edges) by active primary tab:

| Tab | Border colour | Rationale |
|---|---|---|
| Pack | `BRIGHT_YELLOW` | Matches the selected-item highlight already used in lists |
| Scoring | `BRIGHT_CYAN` | Same family as quote / teaching chrome |
| Grader | `BRIGHT_MAGENTA` | Distinct from teaching and loot; "machine" cue |

Selection pills for tabs use `bar_attr` (black-on-colour), already proven for the correct/not-quite bar and sketched for answer buttons (BUTTONS.md). Borders stay double-line; only the attribute changes. With colour disabled, borders fall back to bold vs normal so the active tab still reads from the pill, not the frame.

**Care.** Do not colour room walls this way; `ACS_` walls and panel frames must stay distinguishable. A coloured panel frame on an uncoloured map is exactly the separation the double-line bet was for.

---

## 9. Suggested uses and expansion paths

Rough priority if this ever becomes an epic; each row could be its own story.

| # | Slice | Why | Depends on |
|---|---|---|---|
| 1 | Tab strip + Pack as default | Unlocks everything else without changing pack content | `InfoView`, keys, strings |
| 2 | Coloured borders by tab | Cheap delight; proves chrome | `attrs` + `_box(colour=)` |
| 3 | Scoring → Now (bars for Rooms/HP/score) — **done, DELVE-0042/DELVE-0043** | Uses status-line numbers learners already know | Frame fields from run |
| 4 | Scoring → Rooms (pass distribution map) — **done, DELVE-0055** | The "nice" visual; teaching feedback | Per-room scores on the view model |
| 5 | Grader → Live (model, last ms, fallback) | Makes Phase 2 visible instead of magical | `ChatReply` metrics — **available, DELVE-0053**; tab itself still unbuilt |
| 6 | Grader → Run (token totals + latency sparkline) | Honest local-AI literacy | `GraderMetrics` accumulator — **available, DELVE-0053**; tab itself still unbuilt |
| 7 | Scoring → History (scrolls / prior runs) | Trophy case data mid-run | `progress` summaries into Frame (read-only) |
| 8 | Floor loot scatter | Flavour only; easy to spoil | Explicit spoiler policy |
| 9 | Status tab (version, pack/locale, terminal size, grader model/host) — **done, DELVE-0044** | Diagnostics with no new plumbing | `delve.__version__`, `Pack`/`Strings`, `stdscr.getmaxyx()`, launch-time grader config |

**Uses beyond "looks nice"**

- **Orientation after skip-tutorial.** A Scoring tab teaches what `Rooms:2/3` means with a bar.
- **Debrief after a hard room.** Distribution map shows which lessons bled attempts (without naming this a failure; REPELLED is not death).
- **Trust in the grader.** Showing confidence and fallback rate makes the 0.65 floor legible instead of a silent quality drop.
- **Author / maintainer playtests.** Latency sparkline catches a cold model without leaving the dungeon for `doctor`.
- **Not a CRM.** Resist adding settings, pack picker, or pet rename here; those stay start-of-run prompts.

---

## 10. Architecture sketch (so it stays testable)

```
 ui ──▶ session ──▶ progress (read summaries for History)
         │
         ├─▶ gate / examination (scores, sittings)
         └─▶ assess (grader metrics via existing runner seam)
```

- New commands: `InfoTab(delta)`, `InfoSub(delta)`, or reuse `Page` carefully; keep inventory open as one overlay kind (`inventory` / rename to `info`).
- Frame grows an `InfoView` with tab id, subtab id, pack list, progress chart model, grader stats.
- Headless harness opens `i`, sends tab commands, asserts on view-model fields (not on painted glyphs). Chart *strings* can be built in session (pure) or in `ui` from numeric series; prefer **numeric series on the Frame, paint in `ui`**, so locales do not bake English axis labels into session accidentally; pass label strings from `Strings` through the view.
- SCREENS.md frames regenerate via `tools/screens.py` once any of this ships; hand-drawn figures in this file are argument only (same rule as BUTTONS.md §10).

---

## 11. Hand sketches (argument only)

**Scoring / Rooms distribution**

```
╔══════════════════════════════════════════════════════════════════════╗
║  Pack  [ Scoring ]  Grader                                          ║
║         Now  [ Rooms ]  History                                      ║
║                                                                      ║
║  Pass map                    less · ░ ▒ ▓ █ more                     ║
║  Dlvl 1  ░ █ ▒                                                       ║
║  Dlvl 2  · · ·                                                       ║
║  Dlvl 3  · · · ·                                                     ║
║                                                                      ║
║  phishing ……… 100%  1 sitting                                        ║
║  passwords ……  83%  2 sittings                                       ║
║  links …………   —    sealed                                            ║
║ (end)                                                                ║
╚══════════════════════════════════════════════════════════════════════╝
```

**Pack tab unchanged in job, richer chrome**

```
╔══════════════════════════════════════════════════════════════════════╗
║ [ Pack ]  Scoring  Grader                                           ║
║                                                                      ║
║  136 coins                                                           ║
║  urgent memo                                                         ║
║  A printed email that wants you hurried. The sender almost looks     ║
║  right, the link almost looks right, and the deadline is always      ║
║  one hour from whenever you found it.                                ║
║ (end)                                                                ║
╚══════════════════════════════════════════════════════════════════════╝
```

(Yellow double-line border when Pack is active.)

---

## 12. Recommendation

Ship nothing yet. If an epic is cut, take this order:

1. **Tabbed `InfoView` with Pack default** (§5), so the key stays honest.
2. **Coloured borders + tab pills** (§8), pure `ui` delight on the existing 16 colours.
3. **Scoring bars + room pass map** (§6.1, §6.4A), the charts that use data Delve already records and that reinforce learning rather than mimic a coding-agent billing UI.
4. **Grader metrics** (§7) only after `OllamaClient` returns timings/tokens; keep the tab kind when the model is off.

Leave Claude Code's calendar heatmap and multi-model token markets alone. The distribution map worth wanting in Delve is **rooms by chapter**, not days by year.

When this moves from research to work: one `DELVE-NNNN` epic, stories per slice in the table in §9, regenerate SCREENS.md through `tools/screens.py`, never by hand.
