---
id: DELVE-0043
title: Scoring tab, take 2, coloured bars, a rename from Progress, and a stale hint fix
status: implemented
area: [ui, session, docs]
type: story
epic: DELVE-0035
effort: medium
milestone:
version: 1.16.0
version_span:
created: 2026-07-26
updated: 2026-07-26
commits: [0bb816f]
related: [DELVE-0040, DELVE-0041, DELVE-0042]
supersedes: []
docs: [docs/INFOSCREEN.md]
changelog: "1.16.0"
reason:
---

# Scoring tab, take 2, coloured bars, a rename from Progress, and a stale hint fix

## Summary

Three playtesting findings on DELVE-0042 (the Progress tab's bars), folded into one story since the first two touch the same rows and the third is the same class of stale label. First: the bar rows currently draw with plain `#`/`·` ASCII; they should draw as real coloured blocks (`█` filled, `░` empty), the way Claude Code's own `Usage` tab renders its session/week bars (a solid coloured run against a muted one), reusing `ui/attrs.py`'s existing colour machinery rather than text characters standing in for colour. Second: the tab is named "Progress", but what it shows is *scoring* (how many of the answers given were correct), not *progress* (how many rooms have been attempted); rename the tab, its key, and every reference to "Scoring" so the label matches what the bars actually measure. Third, unrelated to the bars but the same "a label didn't keep up with what `i` now does" class of bug: the walking hint line still reads `Inventory: i` (`hint.carrying`, both locales), left over from before DELVE-0040 grew `i` into the tabbed Info panel; it should read `Info: i` to match the panel's own fixed title (DELVE-0041).

## Motivation / problem

**Colour.** DELVE-0042 shipped `#`/`·` deliberately (its own non-goals list left "colour the bar `#` run by score threshold" out of scope), but a bare ASCII run is a weaker "how am I doing" signal than the coloured bar Claude Code itself uses for the same kind of number, and `ui/attrs.py:attr_for`/`bar_attr` already exist for exactly this. The DELVE-0042 bar-building logic also lives in `session/run.py` as pre-built strings, which puts a presentation decision (how wide is a bar, how is a fraction rounded to a glyph count) on the session side of rule 2; this story is also the chance to move that layout math to `ui`, where the rest of the panel's column-width decisions (`TEXT_W`, wrapping) already live, leaving session responsible only for the numbers (a label, a fraction or `n/a`, a tail string).

**Rename.** "Progress" reads as "how far have I gotten" (rooms attempted), but every row is actually a *score*: the mean `passed_score` of a chapter's passed gates, or HP remaining. A learner glancing at "Progress: 71%" for a chapter they've fully cleared but scored poorly on could easily misread that as "71% of the chapter is done" rather than "this chapter was scored 71% correct". "Scoring" says what the number is, not how far something has advanced.

**The hint line.** `hint.carrying` was written when `i` only opened a flat "Your pack" list (before DELVE-0040); it still says `Inventory: i`, but `i` opens a panel now titled `Info` with three (soon four, DELVE-0044) tabs, of which the pack listing is only the first. The mismatch is the same kind DELVE-0041 already fixed once (adding the `Info` title precisely so the tab strip named itself); this is the one remaining place outside the panel that still calls it "Inventory".

## Stories

### As a learner, I want the Scoring tab's bars to render in colour, so that the chart reads at a glance the way a coloured bar reads anywhere else.

- Given the Scoring tab is active on a colour terminal, when a bar row renders, then its filled portion draws as `█` glyphs in a fixed colour (`Colour.BRIGHT_CYAN`, the same family INFOSCREEN.md §8 already assigns this tab's border) via `attrs.attr_for`, and its unfilled portion draws as `░` glyphs in the plain attribute, both within the same row, without breaking the fixed-column alignment across rows.
- Given a terminal with no colour support, when the same row renders, then the glyphs still render (`█`/`░` remain visually distinct shapes even without colour, unlike the old `#`/`·` which relied on density alone), so nothing is lost by dropping to monochrome.
- Given the layout math (label width, bar width, how a fraction rounds to a filled glyph count), when reviewed, then it lives in `ui/windows.py` beside `TEXT_W`/`PANEL_W`, not in `session/run.py`; `session` hands over only a label, a fraction (`float | None`), and a tail string per row.
- Given all bar rows in this tab (every chapter, and HP), when they render, then they use the same single colour; this story does not add threshold-based colouring (green/yellow/red), matching the reference screenshot's own flat single-colour bars.

### As a learner, I want the tab that shows my chapter scores to be named for what it shows, so that I don't read a score as a completion count.

- Given the Info panel opens, when the tab strip renders, then the second tab reads "Scoring" (English) / a Dutch equivalent, not "Progress"/"Voortgang", in both the tab strip and every hint line that names it.
- Given the tab's stable key (used by session logic and tests, never localised), when it is read anywhere in code, then it is `"scoring"`, not `"progress"` (a pure rename; the tab's position, index, and cycling behaviour are unchanged).
- Given `docs/INFOSCREEN.md` and `issues/DELVE-0035-information-screen.md`, when they reference this tab, then they say "Scoring" throughout (the design doc's §8 border-colour table, §9 priority table, and the epic's child-story list); the *archived* DELVE-0040/DELVE-0041/DELVE-0042 issue files are left as they are (an implemented issue is a record of what shipped at the time, not rewritten after the fact).

### As a learner, I want the walking hint to call the `i` key what it now does, so that the hint line matches the panel it opens.

- Given the learner is carrying gold or an item (the condition `hint.carrying` already gates on), when the hint line renders, then it reads `Info: i` in place of `Inventory: i` (English), with the Dutch string updated the same way (`Rugzak: i` -> an "Info" equivalent), both still naming the same key.
- Given this is a single-string rename, when reviewed, then no other hint (`hint.inventory`, the panel-open hint) needs a change; it already never said "Inventory".

## Non-goals

- No threshold-based bar colouring (green/yellow/red by score); flat single colour only, per the first story's last criterion.
- No sub-tab row (`Now`/`Rooms`/`History`); this story only re-skins and renames the body DELVE-0042 already shipped.
- No new data: still only `passed_score` per gate and `player.hp`/`max_hp`; no new field on any model.
- No change to `pack_score`, `Gate`, or any scoring rule.
- Does not touch the new "Status" tab (DELVE-0044, filed separately): that is new data and a new tab, not a rename or re-skin of this one.

## Design notes / links

- `ui/attrs.py:attr_for`/`bar_attr` are the existing primitives; this story is expected to use `attr_for(Colour.BRIGHT_CYAN)` for the filled run (a plain foreground colour on a solid block glyph reads as a filled bar without needing the black-on-solid `bar_attr` pairing that the tab pill and message bar use for *text on a highlight*, which is a different visual job).
- The `░`/`▒`/`▓`/`█` shade ramp is already established vocabulary in this codebase (INFOSCREEN.md §6.4A's room pass map legend, `docs/DISPLAY.md`), so reusing `█`/`░` here is consistent rather than a new glyph choice.
- Moving bar layout into `ui/windows.py` likely means: `TextBlock` gains a new `kind == "bar"` (or a new field carrying `(label, frac, tail)`) that `windows._blocks` special-cases, bypassing the existing paragraph word-wrap path entirely; word-wrap already collapses multiple spaces, which would destroy a bar row's fixed-column padding if routed through the prose wrapper, so do not try to fit this through `_wrap_spans`.
- `_put_line`'s `(text, strong)` segment convention needs to carry a `Colour` as a third style option alongside its existing `bool`; keep the existing bool-based bold/quote behaviour unchanged for every other caller.
- The rename touches: `_INFO_TABS` in `session/run.py`, `item.tab_progress` -> `item.tab_scoring` in both `strings/*.toml`, `InfoTab.key` usages in tests, and prose in `docs/INFOSCREEN.md` / `issues/DELVE-0035-information-screen.md`.
- `hint.carrying` in `strings/en.toml` and `strings/nl.toml`.

## Acceptance / verification

- A `tests/test_render.py` case renders a Scoring-tab `TextBlock` (or its `InfoView`) and asserts the filled/unfilled glyphs (`█`/`░`) appear, distinct colour attributes are used for each (via a fake/stub curses surface the way existing render tests already check attributes), and the row stays column-aligned.
- `tests/test_items.py`'s existing Progress-tab tests are updated for the new key (`"scoring"` not `"progress"`) and the new data shape (asserting on structured bar data rather than substring-matching a pre-rendered ASCII string).
- `tests/test_languages.py` asserts `item.tab_scoring` (not `item.tab_progress`) exists and differs per locale, and that `hint.carrying` reads `Info: i` / its Dutch equivalent in both locales.
- `./tools.sh screens --check` unaffected (the Scoring tab body is not in `all_screens()`, same as DELVE-0042).
- `./run-tests.sh` is green.
- Manual verification: run `./delve.sh`, open `i`, tab to Scoring, confirm the bars render in colour on a colour terminal; note in the commit that this was eyeballed (curses colour pairs are not assertable headlessly, the same caveat DELVE-0041 already recorded).
