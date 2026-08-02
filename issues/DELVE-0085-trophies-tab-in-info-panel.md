---
id: DELVE-0085
title: Add a Trophies tab to the Info panel showing finished packs and their scores
status: in-progress
area: [session, progress, ui]
type: feature
epic:
effort: medium
milestone:
version:
version_span:
created: 2026-07-31
updated: 2026-08-02
accepted_by: George Moses
accepted_at: 2026-08-02
commits: []
related: []
supersedes: []
docs: []
changelog:
reason:
---

# Add a Trophies tab to the Info panel showing finished packs and their scores

## Summary

A learner can currently only see their trophy case (the packs they've completed and the score
earned each time) once, in the pre-run screen shown before a new or resumed run starts
(`_show_trophies`). While actually playing, there is no way to look at it again. Add a tab to the
in-game Info (`i`) panel that shows the same trophy case: every finished run of every pack, newest
first, with its score and date.

## Motivation / problem

The Info panel already has five tabs (Pack, Scoring, Grader, Status, Messages) covering the
learner's current run in detail, but nothing about runs before this one. Once a learner is mid-run,
there is no way to check "which packs have I finished, and what did I score", short of quitting
back to the pre-run trophy screen. That screen is also easy to blink past (`ui.press_any`,
dismissed by any key with no way to reopen it), so the only durable view of that history is gone
the moment the learner presses a key. This is exactly the kind of long-lived, come-back-to-it
information the Info panel already exists for, so it belongs there rather than only at the start.

## Stories

### As a learner, I want to see the packs I've finished and their scores while I'm playing, so that I don't have to quit and restart to check my own history.

- Given a learner has one or more finished runs recorded (any pack, including the one they're
  currently playing),
  when they open the Info panel and select the new trophies tab,
  then they see one row per finished run, newest first, each showing the pack's title, the score,
  and the date, in the same format as the existing pre-run trophy case (`launch.trophies`).
- Given a learner has never finished any pack,
  when they open the trophies tab,
  then it shows the same empty-state message the pre-run trophy screen would (no completed runs
  yet), not a blank panel.
- Given a learner finishes the pack they are currently playing (claims the scroll) mid-session,
  when they check the trophies tab afterwards,
  then it does not need to reflect that run's own reward within the same session (see Non-goals);
  it is acceptable for the list to reflect only what was true when the run started.

## Non-goals

- Not a live-updating view: the trophy case is fetched once, the same way the pre-run screen
  already does, and threaded into the run at start. A pack finished *during* the current session
  does not need to appear in its own trophies tab before the learner quits and restarts; this
  matches how `_show_trophies` already only ever reflects runs finished before the current one
  began.
- Not replacing or changing the pre-run trophy screen (`_show_trophies` in `delve/ui/app.py`);
  both continue to exist, the new tab is an additional way to reach the same information.
- Not changing what counts as a finished run, or the "keep both" append-only trophy semantics
  (CLAUDE.md's "Re-taking a pack" section); this issue only adds a read path, no data model
  change.

## Design notes / links

- `delve/session/launch.py:118` `trophies()` already builds the exact list of ready-to-print lines
  this tab needs (locale-formatted score and date), given a `store`, `pack`, `name`, and
  `strings`. `delve/ui/app.py:217` `_show_trophies` is today's only caller, before `_begin` starts
  the run.
- `RunState` (`delve/session/run.py`) does not currently hold a `store` reference or the trophy
  list; `_info_overlay` and `_INFO_TABS` (`run.py:161`) are session-side and must stay so (rule 2:
  `ui` never touches `progress`). The natural shape is to compute the trophy lines once in
  `delve/session/launch.py` (`start`/`resume`, right where `trophies()` is already called from
  `app.py`) and pass them into `new_game`/`RunState` as a plain `list[str]`, the same
  already-rendered, opaque-to-`ui` shape `outcome_lines` uses elsewhere, rather than threading a
  live `Store` into the run.
- Name it "Trophies" (`item.tab_trophies`), not "Pack" or "Scores": `item.tab_pack` already names
  the inventory tab (NetHack's "pack" sense) and `item.tab_scoring` already names this run's own
  score breakdown; reusing either word for finished-pack history would collide with an existing,
  differently-scoped tab.
- Follows the same tab-addition shape as Messages folding in (DELVE-0056 et al.): extend
  `_INFO_TABS`, add a `_trophies_body()` alongside `_status_body()`/`_messages_body()`, no new
  sub-tabs needed.

## Acceptance / verification

- A session-level test alongside the existing Info-tab tests in `tests/`: build a run with a
  non-empty trophy list, open the Info panel, select the trophies tab, and assert the rendered
  body matches the same lines `launch.trophies()` would have produced.
- A second test for the empty-state case (no finished runs).
- A new `trophies` scenario in `tools/screenshot.py`'s `SCENARIOS` (`docs/SCREENS.md`/`./tools.sh
  screens` were retired by DELVE-0092; the current on-demand tool is `./tools.sh screenshot
  <scenario>`), reaching the Info panel with the new tab selected, confirming the tab strip and
  body still fit the panel's fixed layout.
- `./run-tests.sh` green, both locales (`item.tab_trophies` added to both `en.toml` and `nl.toml`).

## Peer review

- Auto (implementing agent), 2026-08-02: `trophy_rows` threaded into `RunState` via `new_game`/`launch.start`/`resume` (score/title/date, newest `awarded_at` first); Info/Trophies renders them as a Date/Pack/Score `table` TextBlock with localised headers; empty state `item.trophies_empty`; pre-run `_show_trophies` still uses the line form from `launch.trophies`. Session/locale/progress tests and a `trophies` screenshot scenario. Tab strip still fits at 100×30. `./run-tests.sh` green.
