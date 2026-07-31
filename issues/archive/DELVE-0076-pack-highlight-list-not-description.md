---
id: DELVE-0076
title: Info/Pack highlights the focused item's name in the list, not its description
status: implemented
area: [ui]
type: bug
epic:
effort: low
milestone:
version: 1.27.2
version_span:
created: 2026-07-31
updated: 2026-07-31
accepted_by: George Moses
accepted_at: 2026-07-31
commits: [pre-reset]
related: [DELVE-0075]
supersedes: []
docs: []
changelog: "1.27.2"
reason:
---

# Info/Pack highlights the focused item's name in the list, not its description

## Summary

DELVE-0075 highlights the focused row's *description* in the right column of the Pack tab's
two-column layout. Playtesting feedback (a screenshot of the running panel) says the highlight
belongs on the focused item's *name* in the left column's list instead, leaving the description
column plain.

## Motivation / problem

DELVE-0075's own acceptance criteria explicitly called for highlighting the description rather
than the list row, on the reasoning that it kept the list itself uncluttered. Seeing it running
changes that call: a solid highlighted block filling most of the right column reads heavier than
intended, and it is the list that a learner scans to find "which one am I looking at", so the
highlight is more useful sitting next to the name it marks.

## Stories

### As a learner, I want the focused item's name highlighted in the list, so that I can tell which row's description I'm reading at a glance.

- Given the Pack tab's two-column layout is showing,
  when a row is focused,
  then that row's name in the left column is highlighted, and the right column's description is
  plain text.
- Given the selection moves,
  when the frame is rebuilt,
  then the highlight moves to the newly-focused row's name; only one row is highlighted at a time.

## Non-goals

- No change to the list's scrolling behaviour (DELVE-0075's `_pack_scroll_offset`) or to the
  live-updating description itself; only which column carries the highlight changes.

## Design notes / links

- `ui/windows.py:_draw_pack_columns` (DELVE-0075): swap which loop applies `attrs.bar_attr`, so
  the list-row loop gains it for `i == view.pack_selected`, and the description-block loop drops
  it back to plain `curses.A_NORMAL`.

## Acceptance / verification

- Update the DELVE-0075 render tests in `tests/test_render.py` that assert the highlight's
  location (`test_pack_views_focused_description_is_highlighted_not_the_list_row`) to the new,
  opposite expectation.
- `./run-tests.sh` passes.
