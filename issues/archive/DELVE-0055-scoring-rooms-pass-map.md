---
id: DELVE-0055
title: Scoring tab grows a Now/Rooms sub-tab strip; Rooms shows the room pass map
status: implemented
area: [session, ui, delve, docs]
type: story
epic: DELVE-0035
effort: high
milestone:
version: 1.20.0
version_span:
created: 2026-07-29
updated: 2026-07-30
accepted_by: George Moses
accepted_at: 2026-07-30
commits: [pre-reset]
related: [DELVE-0040, DELVE-0041, DELVE-0042, DELVE-0043]
supersedes: []
docs: [docs/INFOSCREEN.md]
changelog: "1.20.0"
reason:
---

# Scoring tab grows a Now/Rooms sub-tab strip; Rooms shows the room pass map

## Summary

DELVE-0035's last unfiled child from its priority list (INFOSCREEN.md §6.4A, mock-up C): the Scoring tab, which has shown only its chapter/HP bars (DELVE-0042/0043) since it shipped, grows the two-tier tab strip INFOSCREEN.md §5 sketches: a sub-tab row (`Now` / `Rooms`) beneath the primary tab strip. `Now` is exactly today's bar body, unchanged; `Rooms` is a new room pass map, one glyph per room grouped by chapter, filled by whether it has been attempted, passed, or passed cleanly. DELVE-0042 explicitly deferred introducing sub-tabs to "whichever later story adds the room pass map" (its own non-goals); this is that story. No other primary tab grows sub-tabs here.

## Motivation / problem

The Scoring bars answer "how am I doing" at the chapter level; they cannot show *which room* took a retry without naming it, and INFOSCREEN.md §6.4A's distribution-map sketch is the visual DELVE-0035's own non-goals contrast against a calendar heatmap: "the room pass map is the distribution visual Delve actually wants." The data already exists per room (`Gate.passed`, `.sittings`, `.attempts_used`) and is honest, write-once history (rule 3); nobody has read it into a chart yet.

## Stories

### As a learner, I want a room-by-room pass map in the Scoring tab, so that I can see at a glance which lessons needed more than one try without it being spelled out as a score.

- Given the Scoring > Rooms sub-tab is active, when it renders, then it shows one row per scored chapter (`Dlvl {n}`, `n` from `ChapterRun.chapter.dlvl`, tutorial chapters excluded the same way `_scoring_body` already excludes them), each row a run of one glyph per room in that chapter, in the chapter's own room order (`ChapterRun.gates` iteration order, unchanged from how Scoring > Now already iterates it).
- Given a room's gate has had no sitting yet (`not gate.passed and gate.sittings == 0`), when its cell renders, then the glyph is `·` (sealed).
- Given a room's gate has been sat at least once but not yet passed (`not gate.passed and gate.sittings > 0`), when its cell renders, then the glyph is `░` (sat).
- Given a room's gate is passed and needed at least one failed sitting first (`gate.passed and gate.attempts_used > 0`), when its cell renders, then the glyph is `▒` (ok).
- Given a room's gate is passed on the first sitting (`gate.passed and gate.attempts_used == 0`), when its cell renders, then the glyph is `█` (clear).
- Given the Rooms sub-tab renders, when the body is built, then a legend line follows the chapter rows: `· sealed   ░ sat   ▒ ok   █ clear` (localised labels, glyphs unchanged), so the four states are never left for the learner to reverse-engineer.

### As a learner, I want to switch between Scoring's Now and Rooms views without losing my place in the primary tab strip, so that the sub-tab feels like part of the same panel, not a second overlay.

- Given the `i` panel is open on the Scoring tab, when the learner presses `[` or `]`, then the active sub-tab moves to the other one (two sub-tabs: wraps between them) and the body redraws immediately, the same "no extra confirm" feel `Tab`/`Shift-Tab` already has for primary tabs.
- Given the active primary tab is Pack, Grader, or Status (no sub-tabs), when the learner presses `[` or `]`, then nothing happens (the key is inert, not an error), matching how an unbound key elsewhere in a panel is silently ignored.
- Given the learner cycles away from Scoring to another primary tab and back, when Scoring becomes active again, then its sub-tab resets to `Now` (index 0), so re-entering the tab never surprises the learner with whichever sub-tab they last left on a different visit; a sub-tab choice is not run state worth persisting across a primary-tab round trip.
- Given the hint line while the `i` panel is open, when the active primary tab has sub-tabs (Scoring), then the hint includes the sub-tab chord (`Sub: []`) alongside the existing `Tab`/`Put away` chords; when it does not, the hint omits it, so the hint line never advertises a key that does nothing on the current tab.

### As a maintainer, I want the sub-tab strip to be a generic `InfoView` feature, so that a later tab (Grader's own Live/Run split, or a future Scoring > History) can reuse it without another structural change.

- Given the implementation, when reviewed, then `InfoView` gains `subtabs: list[InfoTab]` and `active_sub: int` fields, both empty/zero by default, so Pack/Grader/Status (which set neither) render exactly as before with no `ui` branch change for them.
- Given the implementation, when reviewed, then `ui/windows.py` draws the sub-tab row only when `view.subtabs` is non-empty (one extra row of panel height reserved only then, via `_text_pages`'s existing `reserve` calculation), so a tab with no sub-tabs keeps today's exact panel geometry and page counts.
- Given the implementation, when reviewed, then the session-side sub-tab index lives beside the existing `self._info_tab` (e.g. `self._info_subtab`), and dispatch in `_info_overlay` picks the body function by `(active primary key, active sub key)`, not a growing if/elif chain keyed only on strings that later conflict across tabs.

## Non-goals

- No `History` sub-tab; INFOSCREEN.md §9 row 7 (scrolls / prior runs mid-run) stays its own unfiled future story. Scoring gets exactly two sub-tabs here.
- No colouring the pass-map glyphs; they render in the plain attribute, the same "ship it monochrome first" scoping DELVE-0042 used for the bars before DELVE-0043 coloured them. A follow-up story may add colour the same way.
- No change to `Gate`, `passed_score`, `attempts_used`, or any scoring/stakes rule; this story only reads existing fields (rule 4 and rule 3 untouched).
- No sub-tabs on Pack, Grader, or Status in this story; the generic `InfoView` mechanism is built, but only Scoring uses it here.
- No jump-to-sub-tab-by-number; the `1`-`n` keys stay reserved for whatever primary-tab or Pack-item binding they already have (INFOSCREEN.md §5's "pick one; do not dual-bind").
- No change to the room capacity or generation rules; the pass map reads whatever chapters/rooms already exist, up to the existing ~9-room warn / validator ceiling, and simply runs wider on a chapter with more rooms (still within the 69-column budget for any pack shipped today).

## Design notes / links

- [docs/INFOSCREEN.md](../docs/INFOSCREEN.md) §5 is the sub-navigation sketch (the two-tier strip, the `[`/`]` key convention, the "hint carries the chord for the active tab only" rule) and §6.4A is the room-grid chart this story ships, both followed as specified; §6.4's options B (floor scatter) and C (attempt histogram) are not built here.
- `Gate.passed` / `.sittings` / `.attempts_used` (`delve/gate.py`) are the only new reads; no new field is added to `Gate`. `attempts_used` is not reset on a pass (only on a REPELLED reset), so at read time after a pass it already holds exactly "failed sittings immediately before this one passed" (0 for a clean first-try pass).
- `_scoring_body` (`delve/session/run.py`) is renamed/split: the existing bar body becomes `_scoring_now_body` (identical output, new name only), and a new `_scoring_rooms_body` is added beside it; check whether any existing test references `_scoring_body` by name and update it to `_scoring_now_body` rather than keeping a redundant alias.
- `InfoTab`, `InfoView` (`delve/session/views.py`) grow the two new fields described above; keep both `@dataclass` (not frozen) consistent with `InfoView`'s existing mutability (`ui/windows.py:_fill_status_size` already relies on `replace()` working on it).
- `TabCycle` (`delve/session/commands.py`) is the existing primary-tab command; add a sibling `SubTabCycle(delta: int)` alongside it rather than overloading `TabCycle` with a second meaning.
- `panel_command` (`delve/ui/keys.py`) is where `[`/`]` get bound, beside the existing `Tab`/arrow bindings for `InfoView`; per the story above, the binding always returns `SubTabCycle`, and `session.apply` is what makes it a no-op when the active tab has no sub-tabs (rule 2: `ui` maps a keypress to a `Command`, it does not decide whether the command does anything).
- `windows.py`'s `_draw_info`/`_text_pages`/`page_count` need the reserve-row and sub-tab-row-drawing changes described in the third story above; read `_fill_status_size`'s existing "copy, don't mutate the shared view" pattern before adding another `InfoView`-shaping helper.
- New `Strings` keys (sub-tab labels, the legend, the conditional hint text) go in both `delve/strings/en.toml` and `delve/strings/nl.toml`, in the same style as the existing `item.tab_*`/`hint.inventory` keys; `en.toml`'s wording is a test fixture per CLAUDE.md, so settle it before writing the acceptance test that pins it.
- Update `docs/INFOSCREEN.md` §9's priority table (row 4) and DELVE-0035's own child-story list to mark this row done, the pattern DELVE-0042/0043/0044/0053/0054 already left behind them.

## Acceptance / verification

- A new session-level test suite (beside the existing `_scoring_body`/Scoring tests in `tests/test_items.py`) asserts each of the four glyph states from a `Gate` in the corresponding condition (never sat, sat-not-passed, passed-after-a-retry, passed-clean), the chapter grouping and `dlvl` labelling, the tutorial floor's exclusion, and the legend line's presence.
- A test asserts `SubTabCycle` toggles `self._info_subtab` while Scoring is active, wraps between the two sub-tabs, is a no-op (no state change, no crash) on Pack/Grader/Status, and resets to `Now` when the primary tab changes away from and back to Scoring.
- A `tests/test_render.py` (or extended `InfoView` render test) case confirms: the sub-tab row draws only when `view.subtabs` is non-empty; panel height/page count for Pack/Grader/Status is byte-for-byte unchanged from before this story (the reserve-row regression this story must not introduce); the Rooms body stays within `windows.TEXT_W` (69 columns) for the pilot pack's largest chapter.
- `tests/test_languages.py` covers the new `Strings` keys in both locales.
- `./tools.sh screens --check` unaffected (Scoring is not in `all_screens()`); `./tools.sh infoscreen_mockups --check` regenerated if `tools/infoscreen_mockups.py`'s Scoring > Rooms mock-up (already sketched, mock-up C) needs adjusting to match the shipped body exactly.
- `./run-tests.sh` is green.
