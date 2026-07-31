---
id: DELVE-0056
title: Arrow-key row focus and a distinct colour for the Info panel's focused tab strip
status: implemented
area: [session, ui, delve, docs]
type: story
epic: DELVE-0035
effort: medium
milestone:
version: 1.21.0
version_span:
created: 2026-07-30
updated: 2026-07-30
accepted_by: George Moses
accepted_at: 2026-07-30
commits: [bf337fd]
related: [DELVE-0055]
supersedes: []
docs: [docs/INFOSCREEN.md]
changelog: "1.21.0"
reason:
---

# Arrow-key row focus and a distinct colour for the Info panel's focused tab strip

## Summary

A play-feedback refinement to DELVE-0055's sub-tab strip: up/down now move keyboard focus between the primary tab row and the active tab's sub-tab row (so far, only Scoring's Now/Rooms), and left/right (and Tab/Shift-Tab) cycle whichever row currently has focus, the same two-level arrow navigation Claude Code's own tab UI uses. Because two rows can each show an "active" tab at once, the one under keyboard focus is now painted with a distinct filled highlight; the other row's active tab stays visible but in a plainer colour, so a learner can always tell which row the next arrow press will move.

## Motivation / problem

DELVE-0055 shipped the sub-tab strip with its own dedicated `[`/`]` keys, chosen so the existing Tab/Shift-Tab/arrow bindings for the primary strip needed no change. Playing it, that split reads as two unrelated controls rather than one navigable structure, and one row not being reachable by the arrow keys at all is the surprising part. The fix is to make the arrows do double duty the way a two-level tab UI conventionally does: vertical moves change *which row* is being navigated, horizontal moves change *which tab in that row* is active. `[`/`]` still work as a direct shortcut to the sub-tab strip (unchanged, still exercised by DELVE-0055's own tests); this story adds the row-focus layer on top rather than replacing them.

## Stories

### As a learner, I want the up/down arrows to move between the Info panel's tab row and its sub-tab row, so that I can reach Scoring's Rooms sub-tab the same way I reach any other tab.

- Given the `i` panel is open on a tab with no sub-tabs (Pack, Grader, Status), when the learner presses down, then nothing happens (no state change, no crash), the same "inert, not an error" rule an unbound key elsewhere already follows.
- Given the `i` panel is open on Scoring (which has sub-tabs) with the primary row focused, when the learner presses down, then keyboard focus moves to the sub-tab row; the active sub-tab does not change, only which row responds to left/right next.
- Given the sub-tab row is focused, when the learner presses up, then focus returns to the primary row.
- Given the sub-tab row is focused, when the learner presses left or right (or Tab/Shift-Tab), then the active *sub-tab* cycles (wrapping between Now and Rooms), not the primary tab; the reverse holds when the primary row is focused, matching today's DELVE-0040 behaviour exactly.
- Given the learner cycles the primary tab away from Scoring and back, when Scoring becomes active again, then row focus resets to the primary row (not left on the sub-tab row from a previous visit), consistent with DELVE-0055's existing sub-tab-resets-to-Now rule.
- Given `[`/`]` are pressed at any time the `i` panel is open on a tab with sub-tabs, when applied, then the sub-tab still cycles exactly as DELVE-0055 shipped it, unaffected by which row currently has focus.

### As a learner, I want the focused row's active tab to look different from the other row's active tab, so that I can always tell which row the next arrow press will move.

- Given the `i` panel is open on a tab with sub-tabs, when it renders, then the active tab in the *focused* row draws as a filled pill (today's DELVE-0041 highlight, unchanged), and the active tab in the *other* row draws in a plainer, distinguishable style (no fill), so the two never look identical.
- Given a tab with no sub-tabs is active, when it renders, then the primary strip looks exactly as before this story (a single row, one filled pill), since there is only ever one row to focus.
- Given the hint line while a sub-tabbed tab is open, when it renders, then it names both the row-switch keys and the cycle keys, so a learner who has not read the mock-ups can still discover the split.

## Non-goals

- No third row or deeper nesting; this is the two-level strip DELVE-0055 already scoped (INFOSCREEN.md §5), just reachable by arrows now.
- No change to which tabs have sub-tabs; still Scoring only.
- No colouring of the tab *label text* itself beyond the focused/unfocused distinction already described; this is not DELVE-0035 §8's border-colour-by-tab proposal.

## Design notes / links

- `InfoView` (`delve/session/views.py`) gains `sub_focus: bool = False`: which row currently has keyboard focus, mirroring `active_sub`'s "no subtabs, so this never matters" default.
- A new `FocusRow(delta: int)` command (`delve/session/commands.py`), dispatched in `session.apply` to a new `_focus_row` method beside `_tab_cycle`/`_sub_tab_cycle` (`delve/session/run.py`): `delta<0` (up) sets focus to the primary row unconditionally; `delta>0` (down) sets it to the sub-tab row only when the active primary tab actually has any (rule 2: `ui` maps the keypress regardless, `session` decides whether it does anything, the same shape `_sub_tab_cycle` already uses).
- `self._info_sub_focus` resets to `False` alongside `self._info_subtab` resetting to 0 in `_tab_cycle`, per the "never sticky across a primary-tab round trip" rule DELVE-0055 already established for the sub-tab index.
- `panel_command` (`delve/ui/keys.py`): `curses.KEY_UP`/`curses.KEY_DOWN` map to `FocusRow(-1)`/`FocusRow(1)`; the existing Tab/Shift-Tab/left/right bindings route to `TabCycle` or `SubTabCycle` based on `overlay.sub_focus` instead of always `TabCycle`; `[`/`]` keep their direct, focus-independent `SubTabCycle` binding unchanged.
- `windows.py`'s `_draw_info`: factor the primary-row and sub-tab-row drawing loops (currently near-duplicate) into one helper taking `(tabs, active_index, focused)`, painting the active tab as today's filled `bar_attr(Colour.CYAN)` pill when `focused` else a plain coloured (no-fill) attribute.
- New `Strings` keys for the updated hint wording go in both `delve/strings/en.toml` and `delve/strings/nl.toml`, replacing `hint.inventory_sub`'s current `[`-only wording; `en.toml`'s value is a test fixture per CLAUDE.md.

## Acceptance / verification

- A session-level test suite (beside DELVE-0055's own in `tests/test_items.py`) asserts: `FocusRow` moves `InfoView.sub_focus`, is a no-op on tabs without sub-tabs, resets to primary-focused when the primary tab changes away from and back to Scoring, and that left/right route to `SubTabCycle` when sub-focused and `TabCycle` otherwise (driven as `Command`s, not by inspecting `keys.py` directly).
- A `tests/test_render.py` case confirms the focused row's active tab renders with the filled `bar_attr` highlight and the other row's active tab does not, for both focus states, and that a tab with no sub-tabs renders identically to before this story.
- `tests/test_languages.py` covers the updated hint string in both locales.
- `./run-tests.sh` is green.
