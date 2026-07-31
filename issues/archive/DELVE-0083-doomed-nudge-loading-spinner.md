---
id: DELVE-0083
title: The toast loading spinner can show, then resolve into nothing, for a doomed idle nudge
status: implemented
area: [session]
type: bug
epic:
effort: low
milestone:
version: 1.32.1
version_span:
created: 2026-07-31
updated: 2026-07-31
accepted_by: George Moses
accepted_at: 2026-07-31
commits: [0b15cac]
related: []
supersedes: []
docs: []
changelog: "1.32.1"
reason:
---

# The toast loading spinner can show, then resolve into nothing, for a doomed idle nudge

## Summary

Reported after DELVE-0082 shipped: in a room that already showed its own toast, the loading
spinner can reappear later with no toast ever following it. Root cause is the one-shot idle nudge
(DELVE-0061): it fires only for the very first room, and once fired it keeps running even after
the learner moves, at which point `RunState._poll_toast` silently drops its result
(`is_nudge and self.turn != 0`) rather than showing it, since it would no longer make sense once
the learner has already acted on it. `Frame.toast_loading` (DELVE-0082) does not know this call is
already doomed, so it keeps naming it as "generating" for however long the call takes to actually
finish, then the spinner just vanishes with nothing to show for it, exactly the confusing gap
DELVE-0082 was meant to close.

## Motivation / problem

The nudge exists to prompt an idle learner to move (PLAN.md, DELVE-0061); moving is the intended,
correct reaction, and is also precisely what makes its own result undeliverable a moment later. So
the one call this feature is *designed* to have the learner trigger and then immediately outrun is
also the one call the loading spinner cannot tell apart from a real, deliverable one. If the room's
own earlier toast has since aged out (DELVE-0070's TTL, `_TOAST_TTL` turns after the first move)
by the time this happens, the spinner is the only thing on screen, promising a toast that the code
has already decided will never come.

## Stories

### As a learner, I want the loading spinner to only promise a toast that will actually arrive, so that it never disappears with nothing to show for it.

- Given the idle nudge has fired (`_nudge_state == "queued"`) and the learner has since moved
  (`self.turn != 0`), so its result is now guaranteed to be dropped on arrival,
  and nothing else is queued or in flight behind it,
  when a `Frame` is built,
  then `toast_loading` is `None`; no spinner shows for a call already known to be a dead end.
- Given that same doomed nudge is still in flight, but a genuine room toast is also queued behind
  it (the learner kept walking into new rooms),
  when a `Frame` is built,
  then `toast_loading` still names it: something real is still coming, even though the item
  currently running is not it.
- Given the nudge is still merely `"waiting"` (armed, not yet queued) or has already resolved
  either way (`"fired"`/`"cancelled"`),
  when a `Frame` is built,
  then this issue's change makes no difference to `toast_loading` (both are outside the case being
  fixed).

## Non-goals

- No change to the nudge's own drop rule itself (`is_nudge and self.turn != 0` still governs
  whether its text is ever shown); this issue is only about what the *loading* indicator claims
  while that call is in flight.
- No change to `RoomBackstoryRunner`'s scheduling, threading, or one-at-a-time processing.
- No attempt to predict or suppress the (much rarer, already-eventually-correct) chapter-mismatch
  drop case, where a stale same-run item resolves for a floor the learner has since left: unlike
  the nudge, that item is not silently discarded when something else is queued behind it, and even
  alone, it is a narrower, already-documented case than the nudge's own by-design race.

## Design notes / links

- `session/backstory.py:RoomBackstoryRunner` gains a small query, `pending_other_than(room_id)`:
  whether anything besides the named room/call id is queued, in flight, or resolved-undelivered
  (checked against `_current`, `_queue`, and `_ready`), so a caller can tell "something else is
  still coming" apart from "only this one specific call is what's left."
- `session/run.py:RunState.frame()` (or `_poll_toast`) computes a `doomed_nudge_only` condition:
  `self._nudge_state == "queued" and self.turn != 0 and not
  self._room_backstory.pending_other_than(self._nudge_room_id)`, and folds it into the existing
  `toast_loading=` expression as `and not doomed_nudge_only`.

## Acceptance / verification

- A test asserting `toast_loading` goes back to `None` once the idle nudge has fired and the
  learner has moved, even while that call is still in flight and nothing else is queued.
- A test asserting `toast_loading` stays set while that same doomed nudge is in flight if a
  genuine room toast is also queued behind it.
- A test asserting the existing DELVE-0082 behaviour (spinner while a real call runs, cleared the
  instant the toast resolves) is unaffected outside the nudge case.
- `./run-tests.sh` passes in both locales.
