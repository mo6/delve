---
id: DELVE-0044
title: Add a Status tab to the Info panel, a fourth primary tab
status: implemented
area: [ui, session, docs]
type: story
epic: DELVE-0035
effort: medium
milestone:
version: 1.18.0
version_span:
created: 2026-07-26
updated: 2026-07-26
accepted_by: George Moses
accepted_at: 2026-07-26
commits: [9cde471]
related: [DELVE-0040, DELVE-0041, DELVE-0042, DELVE-0043]
supersedes: []
docs: [docs/INFOSCREEN.md]
changelog: "1.18.0"
reason:
---

# Add a Status tab to the Info panel, a fourth primary tab

## Summary

A fourth primary tab, `Pack` / `Scoring` / `Grader` / `Status`, on the model of Claude Code's own `Status` tab (a reference screenshot is attached, showing `Version`, `Session name`, `Session ID`): plain key/value rows of app and run diagnostics that have a real Delve analogue and need no new plumbing. First slice: `delve`'s version (`delve.__version__`), the pack name and active locale, the terminal size (rows x cols, the same numbers `windows._geom` already reads), and the grader model/host if one is configured (`--grader-model`/`--grader-host`, already known at launch). Live grader health (warm/cold, last-grade latency) is explicitly deferred; it needs `assess/llm.py:OllamaClient.chat` to stop discarding Ollama's timing fields first, the same open dependency already blocking the separate `Grader` tab's own live-status story.

## Motivation / problem

A learner or a maintainer troubleshooting a session today has no in-game way to see which pack/locale/grader is actually active, or confirm the terminal is at the size the layout locked in at; all of that currently requires reading `delve doctor` output or the command line the session was launched with, outside the game entirely. `Status` is the natural fourth tab: it is the one place that is about the *session and app*, as distinct from `Pack` (the learner's inventory), `Scoring` (their performance), and `Grader` (the LLM's health, once that tab has real content).

## Stories

### As a learner or maintainer, I want a Status tab showing app and run diagnostics, so that I can check what's actually running without leaving the game.

- Given the Info panel opens, when the tab strip renders, then a fourth tab, `Status`, appears after `Grader`, reachable the same way every other tab is (`Tab`/`Shift-Tab`, arrow keys, or a direct-jump key per INFOSCREEN.md §5's key table).
- Given the Status tab is active, when it renders, then it shows: the app version (`delve.__version__`), the active pack's name and locale, the current terminal size in rows x cols (the same values `ui.windows._geom` already derives from `stdscr.getmaxyx()`), and, if a grader is configured, its model name and host (`--grader-model`/`--grader-host`, already resolved at launch); if no grader is configured, that row is omitted rather than shown blank.
- Given the same rule 2 boundary every other tab already respects, when this data is assembled, then `session` computes the values (an `InfoView`/`Frame`-reachable field or a new small view model) and `ui` only paints them; terminal size specifically is a `ui`-only fact (`session` has never read `stdscr`), so it must reach `ui` as a value `ui` already owns (e.g. drawn at paint time from `stdscr.getmaxyx()` directly in `windows._draw_info`, not threaded through `session`), while every other field is session/launch-side data reaching the view the normal way.
- Given both locales, when the tab renders under `--lang nl`, then its row labels are localised through `Strings` the same as every other new label in this epic; the *values* (a version string, a model name, a row/col count) are not translated content.

## Non-goals

- No live grader health (warm/cold, last-grade latency, token counts); that stays the separate `Grader` tab's own future story (INFOSCREEN.md §7), gated on `OllamaClient.chat` surfacing Ollama's timing fields.
- No editable session name (Claude Code's own `Session name: /rename to add a name` has no Delve analogue; a Delve run's identity is the player's name, already on the status line, not a separate renameable session label).
- No session/run ID surfaced; Delve has no equivalent concept exposed to a learner today (`runs` rows have a database id, not a user-facing one), and inventing one only to fill this row is out of scope.
- No settings or config editing from this tab; it is read-only diagnostics, the same "not a CRM" principle INFOSCREEN.md §9 already states for the whole epic.
- No change to how the grader is invoked, selected, or its confidence floor; this only surfaces the model/host it was already given.

## Design notes / links

- [docs/INFOSCREEN.md](../docs/INFOSCREEN.md) §5's tab table and §9's priority table should gain a `Status` row once this lands (update the same way DELVE-0042/DELVE-0043 are expected to mark their own rows).
- `ui/windows.py:_geom`/`_body` already computes from `rows, cols = stdscr.getmaxyx()`; the Status tab's terminal-size row is the first place in this panel that shows a `ui`-owned fact rather than a `session`-computed one, so it is drawn directly in `windows._draw_info`'s Status branch, not passed through `InfoView`.
- `delve.__version__` (`delve/__init__.py`) is the version string; do not hand-roll a second copy.
- Grader model/host: check how `--grader-model`/`--grader-host` reach `RunState` today (`session/launch.py` / wherever `grader_runner` is constructed) before adding a new field; the values likely already exist on an object the session holds.

## Acceptance / verification

- A session-level test asserts the Status tab's `InfoView` body includes the version string, pack name, and locale, and omits a grader row when none is configured.
- A `tests/test_render.py` case confirms the Status tab shows the live terminal size (using the test harness's own `stdscr` dimensions), proving it is read at paint time rather than staled from run start.
- `tests/test_languages.py` confirms the new tab label and row labels exist and differ per locale.
- `./run-tests.sh` is green.
