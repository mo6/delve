---
id: DELVE-0075
title: Info/Pack becomes a two-column list-plus-description layout with a scrolling list
status: implemented
area: [session, ui]
type: feature
epic:
effort: medium
milestone:
version: 1.27.1
version_span:
created: 2026-07-31
updated: 2026-07-31
accepted_by: George Moses
accepted_at: 2026-07-31
commits: [bd504ee]
related: [DELVE-0069]
supersedes: []
docs: []
changelog: "1.27.1"
reason:
---

# Info/Pack becomes a two-column list-plus-description layout with a scrolling list

## Summary

DELVE-0069 gave the Pack tab a compact row list with the focused row's full description reached
by confirming it (Enter/space), then backing out to the list with Esc. This issue replaces that
list-then-detail toggle with a permanent two-column layout: the compact list stays on the left at
all times, and the right column always shows the currently-focused row's full description,
updating live as the selection moves, with no separate confirm/back step. The focused row itself
is marked by highlighting its full description on the right, not a leading cursor glyph on the
left. If the carried-kind count grows past what the left column can show at once, the list
scrolls to keep the focused row in view.

## Motivation / problem

The confirm-then-back interaction DELVE-0069 shipped works, but costs an extra keypress each way
to see what a row actually is, and hides the list while reading a description, so a learner
can't see "what else do I have" and "what is this one" at the same time. A permanent two-column
split (list, description) removes both costs: moving the selection alone is enough to read every
item's description in turn, and the list stays visible the whole time. This also better matches
the design notes' original precedent (a list feeding a detail pane) without the extra modal step.

## Stories

### As a learner, I want the Pack tab's list and the selected item's description on screen together, so that I can browse what I carry without losing sight of the list.

- Given the Pack tab is open and carries two or more kinds,
  when it is shown,
  then the panel is split into two columns: a compact list of carried kinds on the left, and the
  currently-focused kind's full description on the right, both visible at once.
- Given the selection moves (up/down, wrapping, as today),
  when the frame is rebuilt,
  then the right column's description updates to the newly-focused row immediately, with no
  separate confirm keypress required to see it.
- Given money or the lit torch is focused,
  when its description is shown,
  then it is the same generic, honest description DELVE-0069 already gives it (no blank panel).

### As a learner, I want the focused item marked by highlighting its description, so that the list itself stays uncluttered.

- Given a row is focused,
  when the panel is drawn,
  then the right column's description is highlighted (not the left column's row, and not a
  leading indicator glyph the way DELVE-0069's badge worked).
- Given no row is focused (only possible on an empty pack),
  when the panel is drawn,
  then it falls back to the existing single `item.inv_empty` message, unchanged from DELVE-0069.

### As a learner, I want the list to scroll once I carry more kinds than fit, so that I can still reach every item with the list's own limited height.

- Given the carried-kind count exceeds the left column's visible row budget,
  when the focused row moves past the currently visible window,
  then the list scrolls (up or down, whichever direction the focus moved) just enough to bring
  the focused row back into view, never losing track of which row is focused.
- Given the carried-kind count fits within the visible row budget,
  when the panel is drawn,
  then no scrolling occurs and every row is shown at once, unchanged from DELVE-0069's behaviour
  at typical carried-kind counts.

## Non-goals

- No change to how the list is populated (`RunState._pack_entries`/`_pack_rows`, DELVE-0069) or to
  the generic torch/money descriptions; this issue is a display and interaction change only.
- No change to how items are picked up, dropped, or merged; still a read-only view.
- No change to any other Info tab, or to the Pack tab's position among them.
- `docs/SCREENS.md`'s Info/Pack mock-up stays deferred, per standing guidance (already stale since
  DELVE-0073; not touched by DELVE-0069 either).

## Design notes / links

- Removes DELVE-0069's `_pack_detail` toggle and the Confirm/Dismiss special-casing built around
  it (`RunState._confirm`/`_dismiss`'s "info" branches, `session/run.py`): with both columns always
  showing, Enter/space and the two-stage Esc no longer have anything to switch between, so those
  branches revert to the plain "close the panel" behaviour every other tab already has.
  `_pack_select` (Select command, up/down) stays exactly as DELVE-0069 built it for moving the row
  focus; `_pack_row` stays the one piece of state, resetting the same way (fresh panel open, tab
  change) it already does.
- `InfoView.pack_rows`/`pack_selected` stay; `body` becomes, whenever `pack_rows` is non-empty, the
  focused row's own detail block (`RunState._pack_detail_body`, unchanged from DELVE-0069),
  rebuilt on every `_pack_select` call the same way the row list already is, rather than only on
  confirm.
- Rule 2 (`ui` paints only): the two-column split, its column widths, and the list's scroll
  offset are all a `ui/windows.py` concern; `session` keeps handing over the plain row labels and
  the focused row's detail body, same shape as today, and never tracks a scroll position itself
  (PLAN.md section 4: "the core never wraps text or tracks a scroll offset", the same rule the
  message-page and overlay-page counters already follow, both owned by `ui/app.py`).
- Right-column highlight: likely the same `attrs.bar_attr`/reverse-video treatment DELVE-0069's
  row badge used, applied to the description block instead of a left-column glyph.
- List scrolling: compute the visible window from `pack_selected`, the list's own row budget, and
  the previous frame's scroll offset (or recompute fresh each frame from `pack_selected` alone,
  clamping so the focused row is always inside `[offset, offset + visible_rows)`; a stateless
  "focused row must be visible" recomputation is simplest and avoids `ui` needing to remember
  anything across frames beyond what `page` already remembers today).

## Acceptance / verification

- A test asserting the Pack tab's `InfoView` carries both `pack_rows` and the focused row's detail
  body simultaneously (no confirm step required), and that moving the selection changes the detail
  body without any Confirm command.
- A test asserting Esc on the Pack tab closes the panel directly (no intermediate "back to list"
  step, since there is no longer a separate detail mode to back out of).
- A test or windows-level check asserting a carried-kind count larger than the list's visible row
  budget keeps the focused row inside the visible window as selection moves past either edge.
- A regression test asserting an empty pack still shows `item.inv_empty`, unchanged.
- `./run-tests.sh` passes.
