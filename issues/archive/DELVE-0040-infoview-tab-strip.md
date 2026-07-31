---
id: DELVE-0040
title: Grow the pack overlay into a tabbed InfoView, Pack as the default tab
status: implemented
area: [ui, session, docs]
type: story
epic: DELVE-0035
effort: high
milestone:
version: 1.14.0
version_span:
created: 2026-07-26
updated: 2026-07-26
commits: [00d4dc1]
related: []
supersedes: []
docs: [docs/INFOSCREEN.md, docs/SCREENS.md]
changelog: "1.14.0"
---

# Grow the pack overlay into a tabbed InfoView, Pack as the default tab

## Summary

This is child story 1 of the epic [DELVE-0035](DELVE-0035-information-screen.md), per its own priority order ("every other child depends on this one landing first"). The `i` overlay stops being a single-purpose `TextView` of pack contents and becomes an `InfoView` carrying a primary tab strip (`Pack` / `Progress` / `Grader`). Pack keeps exactly its current job and content (coins, then each carriable's name and `look` text); Progress and Grader are wired into the tab strip and are reachable with Tab/Shift-Tab, but render only a placeholder body ("coming soon"-shaped, localised) until DELVE-0035's later child stories give them real content. No new numbers are computed in this story; it is the navigation shell.

## Motivation / problem

Today `i` opens a plain `TextView` (`session/run.py:_inventory_overlay`) with no concept of a mode; every future information-screen slice (coloured borders, progress bars, the room pass map, grader metrics per [docs/INFOSCREEN.md](../docs/INFOSCREEN.md)) needs a tab strip and a view model that knows which tab is active before it can add its own content. Building that foundation once, with Pack's existing behaviour preserved byte-for-byte, unblocks every later child of the epic and is itself independently testable and shippable.

## Stories

### As a learner, I want `i` to keep showing my pack by default, so that the key's meaning does not change for anyone who only checks their coins.

- Given a learner presses `i` with no prior tab selection this run, when the overlay opens, then the active primary tab is **Pack** and its body is byte-for-byte the same list of coins and carriables (name + `look` text) that today's `_inventory_overlay` produces.
- Given the pack is empty, when `i` opens on the Pack tab, then `item.inv_empty` still renders exactly as it does today.
- Given the learner presses `Esc`, when the overlay is open on any tab, then it closes exactly as `i` does today (unchanged binding).

### As a learner, I want to cycle to the Progress and Grader tabs, so that the tab strip is real navigation and not a static label row.

- Given the overlay is open, when the learner presses `Tab`, then the active primary tab advances (`Pack` → `Progress` → `Grader` → `Pack`, wrapping); `Shift-Tab` cycles the other direction.
- Given the active tab is `Progress` or `Grader`, when the overlay renders, then the body is a short, localised placeholder line (through `Strings`, not a hard-coded English string in `ui`) rather than an empty box or a crash; no chart, bar, or grader number is computed or shown yet (that is later child stories' scope).
- Given the hint line while the overlay is open, when any tab is active, then it names the tab-cycling chord (`Tab`/`Shift-Tab`) alongside the existing close chord, replacing today's `hint.inventory` ("Put it away: Esc") with a hint that also documents the new keys.

### As a maintainer, I want the pack panel's view model to carry a tab identity, so that later epic children can add sub-tabs and real content without another rewrite of the view model.

- Given the session builds the overlay, when it constructs the view, then it is a new `InfoView` (or equivalent) dataclass in `session/views.py` carrying at minimum the ordered list of primary tabs, which one is active, and a body per tab; `TextView` itself is not overloaded with tab fields (INFOSCREEN.md §4 explicitly warns against this).
- Given the headless harness (rule 2), when a test opens `i` and sends tab-cycle commands, then it asserts on `InfoView` fields directly (active tab id, body content) without touching curses or painted glyphs.
- Given `ui/windows.py` / `ui/render.py` draw the overlay, when the active tab changes, then the tab strip's active-tab indicator (`[ Pack ]` vs plain `Progress`, per the epic's mock-up screen A) is drawn without `ui` importing anything beyond `session` (rule 2 unchanged).

## Non-goals

- No sub-tab row yet (`Progress > Now/Rooms/History`, `Grader > Live/Run`); this story's tab strip is primary-tab-only. Sub-tabs are scoped to the child stories that give Progress/Grader real content.
- No coloured borders or tab pills (DELVE-0035's child 2); the tab strip may render with the existing default frame attributes in this story.
- No progress bars, room pass map, or grader metrics (DELVE-0035's children 3-5); Progress and Grader render a placeholder body only.
- No change to how `,`/`d` (pickup/drop) work; those stay bound exactly as today, unaffected by the tab strip.

## Design notes / links

- Builds directly on [docs/INFOSCREEN.md](../docs/INFOSCREEN.md) §4, §5, §9 (row 1), and §10's architecture sketch: new commands (`InfoTab(delta)` or equivalent), one overlay kind (`inventory`, renamed or aliased to `info` if that reads better, but the existing `_overlay_kind in ("inventory", ...)` call sites in `run.py` must be updated consistently, not left partially matching the old string).
- Mock-up screen A in [DELVE-0035](DELVE-0035-information-screen.md#a-pack-default-tab) is the target frame for the Pack tab once the strip is added (`[ Pack ]  Progress  Grader` header row, unchanged body below it); regenerate `docs/SCREENS.md`'s inventory screen via `./tools.sh screens` once this ships (`tools/screens.py:screen_inventory`), since the panel gains a header row it does not have today.
- Every new label (tab names, the placeholder body text, the new hint line) goes through `Strings` (`en.toml` and `nl.toml`), per rule 2's locale boundary; no per-room fallback, both locales complete together.
- `ui` still never imports `delve.strings` (rule 2); the tab labels and placeholder text reach `ui` through the `InfoView`/`Frame` fields the same way every other localised chrome word already does.

## Acceptance / verification

- New/updated tests in `tests/test_items.py` (or a new `tests/test_infoview.py`) cover: default tab is Pack with unchanged content, Tab/Shift-Tab cycling wraps both directions, Progress/Grader render their placeholder, Esc closes from any tab.
- `tests/test_render.py` covers the tab strip's active-tab rendering (the `[ Tab ]` vs plain distinction) without asserting on raw curses calls.
- `tests/test_languages.py` confirms the new strings exist and render in both `en` and `nl`.
- `./tools.sh screens --check` passes after `docs/SCREENS.md`'s inventory frame is regenerated to match the new header row.
- `./run-tests.sh` is green.
