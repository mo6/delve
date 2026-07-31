---
id: DELVE-0042
title: Progress tab, take 1, horizontal bars for chapter score and HP
status: implemented
area: [ui, session, docs]
type: story
epic: DELVE-0035
effort: medium
milestone:
version: 1.15.0
version_span:
created: 2026-07-26
updated: 2026-07-26
commits: [e3b4dd4]
related: [DELVE-0040, DELVE-0041]
supersedes: []
docs: [docs/INFOSCREEN.md]
changelog: "1.15.0"
reason:
---

# Progress tab, take 1, horizontal bars for chapter score and HP

## Summary

The `i` panel's Progress tab has shown only `item.tab_soon` since DELVE-0040 built the tab strip. This story gives it real content: the horizontal-bar chart INFOSCREEN.md §6.1 sketches, one row per chapter (its passing score as a filled bar, `n/a` if no gate in it has been passed yet) plus one row for current HP vs max. This is the first Progress child cut from DELVE-0035's priority list; the room pass map (§6.4A) and any Now/Rooms/History sub-tab split stay a later story, so this one ships Progress's whole body directly, no sub-tab row yet, the same scoping note DELVE-0041 left for its own tab strip.

## Motivation / problem

`Rooms a/b` on the status line is the only progress signal today, and it is a single number for the whole pack; a learner partway through a multi-chapter dungeon has no way to see which chapter is going well and which is still shaky, and HP only shows as a bare `HP:12(12)` on the status line already visible beside the map. The data already exists on `RunState`: `Gate.passed_score` per gate, `ChapterRun.gates` per chapter, `player.hp`/`max_hp`. This story only surfaces it in the one panel that is already about the learner rather than a keeper.

## Stories

### As a learner, I want to see my score per chapter in the Progress tab, so that I know which chapter I am weakest in without re-deriving it from memory.

- Given the Progress tab is active and a chapter has at least one passed gate, when the panel renders, then that chapter's row shows a filled/empty bar proportional to the mean `passed_score` of its passed gates (matching `RunState.pack_score`'s own averaging rule, but scoped to one chapter) and the percentage alongside it, e.g. `1 Sorting office   ####################········  92%`.
- Given a chapter has no passed gate yet, when the panel renders, then its bar shows empty and `n/a` in place of a percentage, never `0%` (a chapter not yet attempted is not the same as a chapter failed).
- Given the tutorial floor (Dlvl 0, `ChapterRun.scored = False`) is part of the run, when the Progress tab renders, then it is omitted from the chapter list entirely, the same way it is omitted from `pack_score` (rule: an unscored chapter has no score to show).
- Given chapter titles are longer than the row budget, when the panel renders, then the title is truncated with the same convention `windows.py` already uses elsewhere for a fixed-width label, never wrapping the bar onto a second line.

### As a learner, I want to see my current HP in the Progress tab as a bar, so that the same "how am I doing" panel covers both the training and the stakes.

- Given the Progress tab renders, when it draws the chapter rows, then a final `HP` row follows using the same bar style, filled proportional to `player.hp / player.max_hp`, with the raw numbers alongside (`12/12`).

### As a maintainer, I want the bar row a plain string builder, so that a later story can lift the room pass map or a Now/Rooms sub-tab split without touching this one's chart.

- Given the implementation, when reviewed, then the bar-row construction (glyph run + label + percentage/fraction) is a small, separately testable function, not inlined into `_info_overlay`, so DELVE-0035's remaining children (room pass map, grader tabs) can each add their own body builder beside it without growing one function.

## Non-goals

- No sub-tab row (`Now` / `Rooms` / `History`) yet; this story's bars are the Progress tab's whole body. Splitting into sub-tabs is deferred to whichever later story adds the room pass map, since that is the point two sub-tabs become necessary.
- No room pass map (§6.4A); that is DELVE-0035's next listed child.
- No colouring the bar `#` run by score threshold (green/yellow/red, §6.1's aside); §6.1 calls it optional and `ui/attrs.py` colour wiring for a threshold ramp is its own small decision, left out here to keep this story to the plain-string chart.
- No change to `pack_score`, `Gate`, or any scoring rule; this story only reads `passed_score` and `hp`/`max_hp`, never recomputes them differently.
- No change to how HP is calculated, regenerated, or charged; the bar is a read of `player.hp`/`max_hp`, not a new HP rule (rule 4 is untouched).

## Design notes / links

- [docs/INFOSCREEN.md](../docs/INFOSCREEN.md) §6.1 is the exact chart shape and the source of the example row above.
- `RunState.pack_score` (`delve/session/run.py`) is the existing averaging rule to mirror per-chapter rather than reinvent; read it before writing the per-chapter version so the two stay consistent (pack score is the pack-wide mean of the same per-chapter numbers).
- `Gate.passed_score` (`delve/gate.py`) and `ChapterRun.gates`/`scored` are the only new reads this story needs; no new field is added to either.
- The bar row goes on `InfoView.body` as `TextBlock`s the same way `_pack_body` already builds Pack's body, so the pager and both locales' pagination keep working unchanged (rule 2: `ui` still just paints `TextBlock`s, no new import).
- Percentage/fraction formatting should go through the same locale `[format]` table `progress/scrolls.py` already uses if it needs number formatting beyond a bare integer percentage; a plain `92%` needs no locale table, but do not hand-roll one if a helper already exists.
- Update `docs/INFOSCREEN.md`'s own priority table (§9) to mark this row done, the same mark DELVE-0040/DELVE-0041 left behind them.

## Acceptance / verification

- A new session-level test (alongside the existing `_pack_body`/`_info_overlay` tests) asserts: a chapter with a passed gate shows its bar and percentage; a chapter with no passed gate shows `n/a`; the tutorial floor never appears; the HP row is always present and matches `player.hp`/`max_hp`.
- A `tests/test_render.py` case (or extension of the existing `InfoView` render test) confirms the Progress tab's body paints as plain `TextBlock` rows, no truncation past `windows.TEXT_W` (69 columns).
- `tests/test_languages.py` needs no new string if the bar glyphs and numbers are locale-free; if any new label is added (e.g. an "HP" row header, though `HP` is already an untranslated NetHack label per the status line), confirm it follows the same untranslated convention rather than adding a redundant `Strings` key.
- `./tools.sh screens --check` unaffected (Progress is not in `all_screens()`); `./tools.sh infoscreen_mockups --check` is regenerated if `tools/infoscreen_mockups.py`'s Progress > Now mock-up is updated to match the shipped body instead of the aspirational sub-tab version.
- `./run-tests.sh` is green.
