---
id: DELVE-0082
title: Show a small spinner window while the ambient toast is still generating
status: in-progress
area: [session, ui]
type: feature
epic:
effort: low
milestone:
version:
version_span:
created: 2026-07-31
updated: 2026-07-31
accepted_by: George Moses
accepted_at: 2026-07-31
commits: []
related: []
supersedes: []
docs: []
changelog:
reason:
---

# Show a small spinner window while the ambient toast is still generating

## Summary

The ambient room-entry toast (DELVE-0060) currently gives no feedback while its background LLM
call is in flight: the learner sees nothing at all until the passage resolves and pops in (or
never resolves, and nothing ever shows). This issue adds a small status window, shown only while
a toast call is genuinely running, carrying a short in-world line ("You hear a distant muttering,
growing clearer...") plus an animated spinner, the same kind of "something is happening in the
background" affordance Claude Code's own tool-call indicator gives. The moment the real toast is
ready, this window is replaced by it in place.

## Motivation / problem

`RunState._room_backstory`'s call can take anywhere from under a second to several seconds
depending on the model and host. Today a learner standing still in a fresh room sees nothing
change until the passage appears (or doesn't); there is no way to tell "it's coming" from "there
is nothing for this room." A lightweight loading indicator closes that gap without claiming to be
the content itself.

## Stories

### As a learner, I want to see that a room's ambient passage is being written, so that I know to expect it rather than wondering if anything is happening.

- Given I am walking with no panel open and a room's ambient toast call is queued or in flight
  (not yet resolved),
  when a `Frame` is built,
  then it carries a short, localised loading line and I see a small window with that line and an
  animated spinner, anchored the same corner the real toast would use.
- Given that call resolves,
  when the next `Frame` is built,
  then the loading window is replaced by the real toast in the same place; the two are never both
  shown at once.
- Given a panel is open (a lesson, the pack, help, ...), or the idle-nudge timer is merely
  counting down and has not actually queued a call yet,
  when a `Frame` is built,
  then no loading window shows, the same "nothing visible until there is something to show"
  restraint the real toast already follows.

## Non-goals

- No change to `RoomBackstoryRunner`'s own threading, queueing, or failure handling.
- No change to how long a call actually takes, or any attempt to estimate/show progress; this is
  an indeterminate spinner, not a progress bar.
- No sound, no change to the message line or hint line.

## Design notes / links

- `session/views.py`: `Frame` gains one new field, `toast_loading: str | None`, the loading line
  to show or `None` when there is nothing to show one for. Keeps the existing `toast_pending: bool`
  as-is (it already drives `ui/app.py`'s short-timeout poll cadence, and must keep covering the
  idle-nudge timer's own "armed but not yet queued" wait, which is not itself a running call);
  `toast_loading` is the narrower "a call is actually in flight right now" signal a render can act
  on directly, computed in `RunState.frame()` alongside the existing `toast_pending=` line:
  `self.strings("toast.loading") if self._overlay_kind is None and self._toast is None and
  self._room_backstory.pending() else None`.
- `strings/{en,nl}.toml`: a new `[toast]` table, one key, `loading`, holding the line itself (the
  user's own suggested English wording is a reasonable default: "You hear a distant muttering,
  growing clearer..."), plus its Dutch translation (tutoyeer, sentence case, no em-dash, per
  STYLE.md, matching this being in-world flavour text like the toast body itself).
- `ui/render.py`: a third branch alongside the existing `overlay is not None` / `toast is not
  None` chain: `elif frame.toast_loading is not None: windows.draw_toast_loading(...)`, so the
  three states (panel, toast, loading) stay mutually exclusive exactly as toast/panel already are.
- `ui/windows.py`: a new `draw_toast_loading(stdscr, text, map_cols, player_x)`, reusing
  `draw_toast`'s own corner-anchoring logic (top-left/top-right, whichever side the learner isn't
  standing on) and `_box`, but smaller (no title row) and with the spinner glyph prefixing the
  first line of wrapped text. The spinner's animation frame is derived from `time.monotonic()` at
  paint time (no new state threaded through `ui/app.py`'s loop or the `Frame`, since this is
  cosmetic-only and `ui/app.py` already wakes on a short timeout while `toast_pending` is set,
  DELVE-0060). Glyph sequence: the "dots" braille spinner, `⣾⣽⣻⢿⡿⣟⣯⣷` (one of the
  well-known set at <https://stackoverflow.com/questions/2685435>, and the default in most modern
  CLI spinner libraries). Single-codepoint, BMP, narrow (not East Asian Ambiguous like the double-
  line window borders already in `_WIN`), so it is the same class of Unicode bet this codebase has
  already made for those borders: proven on macOS/Linux, not yet verified on Windows/PDCurses,
  tracked under this project's existing outstanding Windows-verification item rather than blocking
  on it here.

## Acceptance / verification

- A test asserting `Frame.toast_loading` is set while `RunState._room_backstory.pending()` is
  true and no toast/overlay is showing, and `None` once the toast resolves.
- A test asserting `Frame.toast_loading` is `None` while a panel is open, and while the idle-nudge
  timer is merely armed and waiting (not yet queued).
- A test asserting `Frame.toast` and `Frame.toast_loading` are never both non-`None` at once.
- `./run-tests.sh` passes in both locales.
