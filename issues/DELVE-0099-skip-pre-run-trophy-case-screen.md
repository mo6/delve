---
id: DELVE-0099
title: Skip the pre-run trophy case screen, now that Info/Trophies covers it in-run
status: proposed
area: [ui, session]
type: bug
epic:
effort: low
milestone:
version:
version_span:
created: 2026-08-03
updated: 2026-08-03
accepted_by:
accepted_at:
commits: []
related: [DELVE-0085]
supersedes: []
docs: [docs/PLAN.md]
changelog:
reason:
---

# Skip the pre-run trophy case screen, now that Info/Trophies covers it in-run

## Summary

Launching `delve` today, for anyone who has finished a pack before, shows a "press any key"
trophy-case screen (`ui/app.py:_show_trophies`) before the name/resume/tutorial-skip prompts even
start. Since DELVE-0085, the exact same rows are one keypress away at any point during play, in the
Info panel's own Trophies tab. The pre-run screen is now a redundant extra keypress standing
between a returning learner and actually starting; drop it from the startup sequence.

## Motivation / problem

`_begin` (`delve/ui/app.py:253`) calls `_show_trophies(stdscr, launch.trophies(...), strings)`
unconditionally, before asking for a name (if not given), before the resume prompt, before the
tutorial-skip prompt. `_show_trophies` itself is a no-op when the collection is empty (a
first-time learner sees nothing), so this only affects a learner who has completed at least one
pack before, which after a few sessions is the common case, not the exception. Before DELVE-0085
this screen was the *only* place a learner could see their trophy case at all, so blocking startup
on it made sense; now it duplicates the Trophies tab (`i` then Trophies, any time during a run),
built from the exact same `launch.trophy_rows` data. Forcing every launch through a stale
"here's what you've already told me you've done" screen, with no new information and no choice to
make, adds friction for no remaining benefit.

## Stories

### As a learner who has finished packs before, I want to start playing without an extra keypress, so that the pre-run flow only asks me things I actually need to answer.

- Given a learner has one or more completed runs in their trophy case,
  when they launch `delve` (or resume/start a fresh run),
  then no trophy-case screen appears; the next prompt is the resume offer (if a superseded-free
  unfinished run exists, DELVE-0084) or, for a fresh run, the tutorial-skip prompt, exactly the
  flow a first-time learner already gets today.
- Given a learner has no completed runs yet,
  when they launch `delve`,
  then the startup flow is unchanged (it already showed nothing for this case).

### As a learner, I want my trophy case still reachable, so that removing the startup screen doesn't take anything away.

- Given a learner mid-run,
  when they open `i` and select the Trophies tab,
  then their full trophy case still renders exactly as before (DELVE-0085), unaffected by this
  change.

## Non-goals

- Not changing `launch.trophies`/`launch.trophy_rows` or any progress-store query; both stay,
  since the Trophies tab still consumes them (`RunState` threads `trophy_rows` in at start/resume,
  `delve/session/run.py:509`).
- Not adding a flag to bring the pre-run screen back; if a future need for a startup-time trophy
  glance resurfaces, that is a fresh issue, not a revert of this one.
- Not changing the resume prompt, the tutorial-skip prompt, or anything else in `_begin`'s
  sequence; only the trophy-case screen and its call are removed.

## Design notes / links

- `delve/ui/app.py:253` `_begin`: delete the `_show_trophies(...)` call. `_show_trophies` itself
  (`delve/ui/app.py:218`) becomes dead code once its only caller is gone; delete the function too,
  not just the call, per the repo's habit of removing dead code outright rather than leaving an
  unused helper (see DELVE-0097 for the same pattern with dead locale keys).
- `strings("ui.trophy_title")`/`strings("ui.press_any")` (`delve/strings/en.toml`, `nl.toml`) are
  read only from `_show_trophies`; grep the rest of the tree for other readers before deleting
  the keys (`ui.press_any` in particular, check it is not shared with `_show_win` or another
  screen before removing it).
- docs/PLAN.md section 10 ("Progression, scrolls, and the trophy case") describes the pre-run
  screen as the trophy case's home; update its wording to point at the Trophies tab instead once
  this lands, so the design doc does not describe a screen that no longer exists.
- No `./tools.sh screenshot` scenario shows the pre-run trophy screen today (it is a plain
  `_draw_centered` block, not one of the built `all_screens()` scenarios), so there is no mock-up
  to update; the Trophies tab's own `trophies` scenario is unaffected.

## Acceptance / verification

- An app-level test (in the style of the existing `_ask_yn`/`_pick_companion` curses-fake tests)
  asserting `_begin` never calls a trophy-screen render when `launch.trophies(...)` is non-empty,
  and that the very next prompt shown is the resume/tutorial-skip one.
- Confirm no other reader of `ui.trophy_title`/`ui.press_any` exists before deleting either key
  (`grep -rn` across `delve/`); remove both from `en.toml` and `nl.toml` together if clear, and
  `tests/test_languages.py`'s locale-parity check stays green.
- `./run-tests.sh` green, both locales.
