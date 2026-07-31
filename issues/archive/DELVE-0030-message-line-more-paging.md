---
id: DELVE-0030
title: The top message line silently truncates a message wider than the terminal
status: implemented
area: [ui]
type: bug
epic:
milestone:
version: 1.10.2
version_span:
created: 2026-07-25
updated: 2026-07-25
commits: [pre-reset]
related: []
supersedes: []
docs: [docs/SCREENS.md]
changelog:
---

# The top message line silently truncates a message wider than the terminal

## Summary

When a status message is longer than the terminal is wide, the top line is cut off at the right
edge with no indication that there is more ("You peel a sticky note off the underside of a desk.
Someone wrote their passphrase on it. Clevernes" and then nothing). Text is lost with no way to
read it. Instead, a message that does not fit should show as much as fits followed by a `--More--`
prompt, and reveal the rest on a keypress, the way NetHack pages a long message and the way Delve
already pages a long lesson panel.

## Motivation / problem

`ui/render.py:draw` paints the top line as `msg[: cols - 1]`, a hard truncation. A message wider
than the terminal (100 columns at the minimum) loses its tail; the sticky-note flavour line is 130+
characters and reads as ending mid-word. The message log (`p`) can show a line that has already
aged off the top, but it cannot show the hidden half of a line that is on screen right now, and a
learner has no signal that anything was cut. The fix mirrors the overlay pager: the app already
owns a `page` counter for a `TextView` and only emits `Confirm` on the last page (a UI-owned scroll
offset, PLAN.md section 4). The message line needs the same treatment, and for the same reason the
paging must live in the UI: the run does not know the terminal width (it stores only the map's
locked size, not the message line's), so only the frontend can measure whether a message fits and
split it.

## Stories

### As a learner, I want a long message paged with a --More-- prompt, so that no status text is lost off the right edge.

- Given a message longer than the terminal is wide is posted while no panel is open,
  when the frame is painted,
  then the top line shows as much of the message as fits, ending with a `--More--` prompt, and the
  remainder is held for the next keypress rather than truncated away.
- Given a `--More--` prompt is showing on the message line,
  when the learner presses any key that is not Quit,
  then the next page of the message is shown (with `--More--` again if more remains), and that
  keypress does **not** move the player or advance a turn.
- Given the last page of a paged message is showing,
  when the learner presses a movement or action key,
  then the `--More--` is gone, the key acts normally, and the turn advances as usual.
- Given a message that fits the terminal width,
  when it is painted,
  then it shows exactly as today, with no `--More--` and no change in behaviour.

### As a learner, I want to leave at any time, so that a long message never traps me.

- Given a `--More--` prompt is showing,
  when the learner presses the Quit key,
  then the game quits as it would from the map, rather than the key being swallowed by the pager.

## Non-goals

- Changing message wording, the two-turn ageing of the top line (`_MSG_TTL`), or the message log
  (`p`).
- Paging the message line while a keeper encounter or other panel is open; the panel owns the
  screen there and the frozen encounter text is short. This story is the map message line only.
- Moving message state or ageing into the UI: the run keeps owning the messages and their ageing;
  the UI owns only the presentational page offset, exactly like the overlay `page`.
- Wrapping by display column rather than codepoint (the status and message lines already truncate
  by codepoint); emoji-width correctness on the message line is out of scope.

## Design notes / links

The paging is UI-owned because the run has no terminal width to split against (rule 2, and the same
call PLAN.md section 4 makes for the overlay scroll offset). Add a pure `message_pages(msg, cols)`
helper beside the other pagination in `ui/windows.py` (where `page_count` and `_wrap` already live),
unit-testable without curses. `ui/render.py:draw` takes a `msg_page` and, when no overlay is open,
renders that page plus a trailing `--More--` when earlier than the last. `ui/app.py:_play` holds a
`msg_page` next to its `page`, resets it when the visible message changes, advances it on a
non-Quit key while pages remain (swallowing the key so no turn passes), and lets Quit through. The
`--More--` suffix width is reserved when splitting, so a page plus its prompt always fits. Screen
evidence and the 100x30 minimum: `docs/SCREENS.md`.

## Acceptance / verification

- A `windows.message_pages` unit test: a short message is one page unchanged; a long message splits
  into pages that each fit `cols - 1` including the `--More--` suffix, and no word is broken.
  Covers the fit/no-fit split.
- A render test (the `CursesEmu` fake) posts a long message with no overlay and asserts page 1 ends
  with `--More--` on the top row, and that rendering `msg_page=2` shows the continuation. Covers the
  first learner story.
- `./run-tests.sh` passes (pytest, ruff, screen and issues-index checks). The `--More--` paging of
  the app loop itself is curses glue, exercised the same way the overlay pager is (not through a
  pty), so the pure `message_pages` split carries the test weight.
