---
id: DELVE-0093
title: Fix the toast-loading spinner's redraw cadence so it steps one adjacent glyph at a time
status: in-progress
area: [ui]
type: bug
epic:
effort: low
milestone:
version:
version_span:
created: 2026-08-02
updated: 2026-08-02
accepted_by: George Moses
accepted_at: 2026-08-02
commits: []
related: [DELVE-0082, DELVE-0083]
supersedes: []
docs: []
changelog:
reason:
---

# Fix the toast-loading spinner's redraw cadence so it steps one adjacent glyph at a time

## Summary

The toast-loading spinner (DELVE-0082) is meant to look like a single dot orbiting the edge of a
braille cell, one adjacent step at a time. It doesn't: the redraw poll interval that repaints it,
`_TOAST_POLL_MS = 300` (`delve/ui/app.py`), and the spinner's own per-glyph hold time,
`_SPINNER_MS = 120` (`delve/ui/windows.py`), aren't multiples of each other, so most redraws land
mid-way through the 8-glyph cycle instead of on the next glyph in it. The learner sees the empty
dot hop around unevenly rather than orbit smoothly. Fix the cadence so every redraw while the
spinner is up advances the glyph by exactly one adjacent step.

## Motivation / problem

`_SPINNER = "⣾⣽⣻⢿⡿⣟⣯⣷"` (`delve/ui/windows.py:71`) is correctly ordered: read one character at a
time, the missing dot walks a clean lap around the cell's edge (top-left, down the left column,
across the bottom, up the right column, across the top, back to top-left), each step landing on a
dot adjacent to the last. That part of the design is fine and does not need to change.

What's wrong is when a new glyph is actually shown. `draw_toast_loading` (`delve/ui/windows.py:658`)
picks the glyph from wall-clock time: `_SPINNER[int(time.monotonic() * 1000 / _SPINNER_MS) %
len(_SPINNER)]`. But it's only ever *called* when `ui/app.py`'s main loop redraws, and while walking
with a toast pending that redraw is gated on a poll timeout, `_TOAST_POLL_MS = 300`
(`delve/ui/app.py:37,352`). Since 300 isn't a multiple of 120, consecutive redraws sample the
120ms-stepped cycle 2 or 2.5 steps apart on average, never a steady 1. Simulating the actual
redraw-to-redraw sequence a learner sees (`⣾ ⣻ ⣟ ⣷ ⣻ ⡿ ⣷ ⣽ ⡿ ⣯ ⣽ ⢿ ...`) and checking each
transition against the glyphs' real dot positions: 9 of the first 11 transitions land on a
non-adjacent dot. The spinner was designed to orbit; what ships jitters and doubles back.

## Stories

### As a learner, I want the loading spinner to visibly rotate, so that the "something is happening" affordance reads as intentional rather than glitchy.

- Given the toast-loading window is showing and the learner stands still long enough for two or
  more redraws, when each redraw happens, then the glyph shown is the very next one in
  `_SPINNER`'s cycle (wrapping after the last), never one further ahead and never repeated.
- Given the redraw poll interval and the spinner's per-glyph hold time, when their relationship is
  checked, then the poll interval is an exact multiple (commonly 1x) of the hold time, so no redraw
  can land strictly between two glyphs.

### As a maintainer, I want the two timing constants to stay in relationship, not just individually reasonable, so that a future tweak to either doesn't reintroduce the drift.

- Given `_TOAST_POLL_MS` (`ui/app.py`) and `_SPINNER_MS` (`ui/windows.py`) live in different
  modules today, when the fix lands, then their relationship is either enforced (one derived from
  the other, or a shared constant) or, if they must stay separate for layering reasons, a comment
  on each names the other and a test asserts the divisibility relationship directly, so a later
  change to one alone fails loudly instead of silently reintroducing the jitter.

## Non-goals

- No change to the glyph set or its order (`_SPINNER`'s own sequence is already correct).
- No change to `_GRADE_POLL_MS` or the free-text grading spinner/poll path; this is scoped to the
  toast-loading window only.
- Not a general animation-framework change; this is a two-constant timing fix.

## Design notes / links

Two ways to close the gap, either acceptable:

- Slow `_SPINNER_MS` to match `_TOAST_POLL_MS` (e.g. 300ms/glyph): simplest, no new coupling, but
  the spinner turns visibly slower than it was designed to feel (DELVE-0082 picked 120ms
  deliberately, "the well-known set" default cadence).
- Speed `_TOAST_POLL_MS` down to 120ms (or another exact divisor, e.g. 60ms) so a redraw happens on
  every glyph boundary: keeps the spinner's intended pace, at the cost of a livelier idle-walking
  poll loop; DELVE-0082's own comment on `_TOAST_POLL_MS` already weighs this against CPU use while
  idle-walking with a toast pending, so re-check that reasoning holds at the faster rate before
  picking this branch over the first.

Either way, `ui/app.py` and `ui/windows.py` are both `ui`-layer (rule 2), so no cross-layer import
is needed to couple the two constants directly if that's the chosen fix; a plain shared constant
(e.g. moved into one module and imported by the other) is in-bounds.

## Acceptance / verification

- A test drives `draw_toast_loading` (or the glyph-selection logic factored out of it) across a
  simulated sequence of redraw timestamps spaced `_TOAST_POLL_MS` apart and asserts every
  consecutive pair of glyphs shown is adjacent in the cell's dot grid (reusing the adjacency check
  worked out in review: each glyph's missing dot is a unit step, row or column, from the previous
  one), covering the first story.
- A test (or a direct assertion near the constants) checks `_TOAST_POLL_MS % _SPINNER_MS == 0` (or
  the inverse, whichever constant is now derived), so a future edit to either alone fails
  `./run-tests.sh` instead of silently drifting again. Covers the second story.
- `./run-tests.sh` passes.
