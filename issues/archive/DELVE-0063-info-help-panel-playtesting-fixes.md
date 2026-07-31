---
id: DELVE-0063
title: Five playtesting fixes to the Info/Help panels and the torch
status: implemented
area: [session, ui, delve]
type: bug
epic:
effort: low
milestone:
version: 1.25.1
version_span:
created: 2026-07-30
updated: 2026-07-30
accepted_by: George Moses
accepted_at: 2026-07-30
commits: [10c4543]
related: [DELVE-0028, DELVE-0040, DELVE-0059, DELVE-0062]
supersedes: []
docs: []
changelog: "1.25.1"
---

# Five playtesting fixes to the Info/Help panels and the torch

## Summary

A playtesting pass over the Info (`i`) and Help (`?`) panels found five separate rough edges:
reopening either panel landed on whatever tab was last visited instead of the first one; the
Scoring tab's Now and Rooms sub-tabs still wasted a blank row between every entry even after
DELVE-0059 condensed the Keys tab; the Status tab had one more wasted gap than necessary; the
message log (`p`) was a second, separate read-only panel instead of living inside Info; and the
currently-burning torch could never be dropped, so the unlit ambient scene (DELVE-0062) was only
reachable by waiting roughly 150 steps for it to burn out. This issue is a retroactive record of
the five fixes, written and archived together since the work was already directed, implemented,
tested, and committed in the same sitting.

## Motivation / problem

Each of these was found by hand while playing, not by a test:

- **Sticky tabs read as broken navigation.** Tabbing over to Status, closing the panel, and
  reopening it later landed straight back on Status, which felt like the panel had lost track of
  what the learner actually wanted (the default view), not like a helpful remembered preference.
- **Scoring/Now and Scoring/Rooms were still spaced out.** DELVE-0059 condensed the Keys tab's
  dense one-liner list into a single block so `ui/windows.py`'s generic pager (a blank line between
  every top-level block, right for prose) wouldn't waste rows on it, and DELVE-0059's own
  follow-up widened that trick to Status/Grader/Objectives/Messages. Scoring's two sub-tabs were
  missed: `_scoring_now_body` builds one `TextBlock(kind="bar")` per chapter (plus one for HP), and
  `_scoring_rooms_body` builds one `TextBlock(kind="plain")` per Dlvl row, so both still burned a
  blank row after every single entry.
- **Status still had an avoidable gap.** Its grader row was appended as its own trailing block
  after the terminal-size row, rather than folded in with the other condensed facts.
- **No light in the inventory to test with.** The lit torch is deliberately never a `Stack`
  (DELVE-0062: it is a steps-remaining counter, not a spare count), so it never appeared in the
  drop menu; there was no way to reach the unlit ambient prose on demand short of walking it out.
- **Two panels for "what's happened."** `i` (Info) and `p` (the message log) were two separate
  read-only panels doing adjacent jobs; playtesting found this one panel too many.

## Stories

### As a learner, I want the Info and Help panels to always open on their first tab, so that reopening either one is predictable rather than depending on where I last left it.

- Given the Info panel was last closed on the Status tab,
  when it is reopened with `i`,
  then it opens on the Pack tab, not Status; `Tab`/`Shift-Tab` still remembers the active tab
  while the panel stays open.
- Given the Help panel was last closed on the Objectives tab,
  when it is reopened with `?`,
  then it opens on the Keys tab, not Objectives.

### As a learner, I want the Scoring tab's bar and room-glyph rows packed tightly, so that I am not paging past blank space to see my own progress.

- Given the Scoring > Now sub-tab's per-chapter bars and the HP bar,
  when rendered,
  then consecutive bar rows have no blank line between them (`ui/windows.py`'s `_blocks` batches
  consecutive `kind="bar"` entries the same way it already batches bullets).
- Given the Scoring > Rooms sub-tab's per-chapter Dlvl/glyph rows and the legend line,
  when rendered,
  then they fold into one condensed block via the existing `_condensed` helper, with no blank
  line between rows.

### As a learner, I want the Status tab's remaining facts packed as tightly as the size-row substitution allows, so that the panel doesn't waste a row it doesn't need to.

- Given a grader is configured,
  when the Status tab renders,
  then the grader row condenses into the same block as version/pack/locale, ahead of the
  terminal-size row, leaving only one gap (the size row's own block) instead of two.
- Given the terminal-size row must stay paint-time-substitutable by `kind` (`ui/windows.py`'s
  `_fill_status_size`, which matches by kind regardless of position),
  when the body is built,
  then it remains its own distinct block regardless of where the other rows sit.

### As a learner, I want to be able to drop the torch I'm carrying, so that I can reach the unlit ambient scene deliberately instead of only by waiting it out.

- Given the learner has a working torch (`torch_charge > 0`) on a scored floor,
  when they open the drop menu,
  then the torch appears as an entry, appended after gold and every inventory stack so it never
  shifts an existing item's menu number.
- Given the learner drops the torch,
  when the drop resolves,
  then `has_light` becomes false immediately, vision darkens on the spot, and an ordinary torch
  `Stack(1)` is left on the floor tile.
- Given that dropped torch is picked back up,
  when it is not already lit,
  then it relights exactly as any dark-pickup torch already does (`_do_pickup_torch`), full
  duration restored.
- Given the tutorial floor, where `has_light` always reads true regardless of charge,
  when the drop menu is built,
  then the torch never appears there, since dropping it would claim an effect that doesn't
  actually happen.

### As a learner, I want the recent-messages log to live inside the Info panel, so that I have one panel for "what's happened" instead of two.

- Given the learner presses `p`,
  when nothing else is open,
  then the Info panel opens directly on a new "Messages" tab (index 4, after Status), with the
  same recent-lines-condensed-into-one-block content the standalone panel used to show.
- Given the Info panel is already open on some other tab,
  when the learner tabs to Messages,
  then it shows the same content `p` would have opened directly on.
- Given the message log is showing,
  when Esc or Enter is pressed,
  then it closes exactly as every other Info tab does (the panel closes; `session/help.py`'s
  `"messages"` overlay-kind context is retired, since it is `"info"` now).

## Non-goals

- No change to how many recent lines the message log keeps (`_HISTORY_MAX` stays 5) or how
  repeats are deduplicated.
- No change to the torch's burn-down mechanic itself (`TORCH_DURATION_STEPS`, per-step
  decrement); this only adds a deliberate way to zero it early.
- No re-triggering of a room's ambient toast on dropping the torch; `_observe`'s existing
  `_maybe_enter_room` guard (first-visit-only per run) is unchanged, so darkening the map is
  immediate but a fresh ambient passage for the *current* room is not forced.
- No screen mock-up regeneration: the existing `docs/SCREENS.md` Info/Help frames already show an
  abbreviated tab strip that predates this change (missing "Status" already), and none of the
  committed mock-ups depict the Status or new Messages tab, so nothing in `tools/screens.py`
  needed updating for this issue specifically.

## Design notes / links

- `_info_tab`/`_help_tab` remain run-scoped instance state, mutated by `_tab_cycle` while a panel
  stays open (unchanged); only the *open* actions (`_inventory`, `_help`, `_history`) now reset
  them, reversing DELVE-0040's and DELVE-0028's original "sticky across opens" design intent.
- The bar-batching fix lives entirely in `ui/windows.py:_blocks` (rule 2: paint-only), mirroring
  the pre-existing bullet-batching branch; no `session` change was needed for Scoring/Now.
- `_scoring_rooms_body` and the Status tab both reuse `RunState._condensed` (DELVE-0059), the same
  helper Keys/Objectives/Grader/Messages already use.
- The torch-drop path is `_do_drop_lit_torch`, dispatched from `_do_drop` on a sentinel `def_id`
  (`_LIT_TORCH_ID = "torch:lit"`, never a real `ItemDef.id`) rather than `TORCH.id`, since a
  carried spare torch (an ordinary `Stack(TORCH, n)`) and the one currently burning must stay
  distinguishable in the drop menu.
- Messages becomes `_INFO_TABS`'s fifth entry (`"messages"`); `_history_overlay` (a `TextView`
  builder) is replaced by `_messages_body` (a `list[TextBlock]` builder), reused by `_info_overlay`
  the same way every other tab's body method is.

## Acceptance / verification

- `test_info_panel_reopens_on_pack_not_the_last_tab_visited` /
  `test_help_panel_reopens_on_keys_not_the_last_tab_visited` (`tests/test_items.py`).
- `test_scoring_rooms_body_groups_by_chapter_with_dlvl_labels` /
  `test_scoring_rooms_body_ends_with_a_legend_line` (updated for the condensed shape) and the
  existing Scoring/Now bar-block tests (`tests/test_items.py`).
- `test_status_body_condenses_facts_but_keeps_the_size_row_separate` (updated,
  `tests/test_items.py`).
- `test_the_lit_torch_appears_last_in_the_drop_menu_and_can_be_dropped`,
  `test_the_dropped_torch_relights_on_pickup`,
  `test_the_tutorial_floor_never_offers_the_lit_torch_to_drop` (`tests/test_items.py`).
- `test_the_message_log_shows_recent_lines_and_closes` (updated for `InfoView`,
  `tests/test_dungeon.py`); `test_message_log_is_condensed_too` (`tests/test_help_pagination.py`).
- `test_every_catalogue_context_is_a_real_overlay_kind` and the rest of
  `tests/test_help_catalogue.py` (updated: `"messages"` retired as a context).
- `./run-tests.sh` passes (572 tests, ruff, screens, issues index, all pack validations).
