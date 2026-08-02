---
id: DELVE-0094
title: Resuming a run queues an ambient toast for the pre-restore spawn room, then silently discards it
status: implemented
area: [session, progress]
type: bug
epic:
effort: medium
milestone:
version: 1.34.1
version_span:
created: 2026-08-02
updated: 2026-08-02
accepted_by: George Moses
accepted_at: 2026-08-02
commits: [968adf7]
related: [DELVE-0060, DELVE-0083]
supersedes: []
docs: []
changelog: "1.34.1"
reason:
---

# Resuming a run queues an ambient toast for the pre-restore spawn room, then silently discards it

## Summary

Reported by the maintainer: reopening a saved run past the tutorial shows the toast-loading
spinner ("You hear a distant muttering, growing clearer...") for a while, then it just vanishes,
never replaced by a toast. Root cause is construction order in `session/launch.py:resume`: it
builds a brand-new `RunState` via `new_game` (spawning at chapter 0, turn 0, an empty
`visited_rooms`) before laying the snapshot over it with `apply_dict`. `RunState.__init__` already
calls `_observe()` unconditionally, which queues a real ambient-toast background call for that
pre-restore spawn room (DELVE-0060's `_maybe_enter_room`). `apply_dict` then overwrites `idx`,
position, and `visited_rooms` with the actual resumed state, but never touches or cancels
`_room_backstory`, so that call keeps running for a room/chapter context that no longer exists by
the time it resolves. When it does, `RunState._poll_toast`'s existing cross-chapter guard
(`chapter_idx != self.idx: return`, `session/run.py:2263`) silently drops it, exactly as it is
meant to for a genuinely stale item, since the queued chapter almost never matches wherever the
snapshot actually resumes to. `Frame.toast_loading` (DELVE-0082) has no way to know this particular
call is doomed the moment it was queued, so the spinner shows for the whole call, then resolves
into nothing.

## Motivation / problem

DELVE-0060 already built resume specifically so it never *re-triggers* a toast for a room already
stood in (`visited_rooms` persisted through the snapshot); DELVE-0083 already handled the one
known case of a loading spinner promising a toast that is guaranteed to be dropped (the idle
nudge outrun by the learner's own first move). This is a third, previously-unconsidered instance
of that same "spinner promises something already doomed" shape, except it isn't rare: it fires on
essentially every resume of a run that has progressed past the pack's starting chapter, because
`resume()`'s own construction order guarantees the queued call's chapter and the restored chapter
will not match. DELVE-0083's own non-goals explicitly assumed the chapter-mismatch drop case was
"much rarer" and "already-eventually-correct"; resume turns out to make it the common case, not
the rare one.

## Stories

### As a learner, I want resuming a saved run not to promise a toast that was never really queued for the room I'm actually standing in, so that the loading spinner never resolves into nothing.

- Given a saved run whose current chapter differs from the pack's starting chapter (the ordinary
  case for anyone who has descended past Dlvl 0/1),
  when the run is resumed (`session/launch.py:resume`),
  then no ambient-toast call is queued for the pre-restore spawn room at all; `_room_backstory` has
  nothing in flight immediately after `resume()` returns unless the restored room genuinely hasn't
  shown its own toast yet.
- Given a saved run resumed while still on the pack's very first, unvisited room (an edge case:
  quit before that room's own toast ever resolved),
  when the run is resumed,
  then exactly one call is queued, for the *restored* room/chapter/turn context, not the transient
  pre-restore one `new_game` briefly held.
- Given the restored room has already shown its toast before the run was saved (`visited_rooms`
  from the snapshot includes it, the common case),
  when the run is resumed and a `Frame` is built,
  then `toast_loading` is `None` from the first frame onward: nothing was ever queued to promise.

## Non-goals

- No change to `_poll_toast`'s cross-chapter drop rule itself; a genuinely stale item from ordinary
  play (the learner has since taken the stairs) still drops silently, unchanged. This issue is only
  about `resume()` manufacturing that same stale condition on every restore, not about how a truly
  stale item is handled once queued.
- No change to `apply_dict`'s snapshot shape or to what a snapshot stores.
- No change to the fresh-start path (`session/launch.py:start`): a brand-new run's first-room toast
  is exactly the case DELVE-0060 built this for, and is unaffected.

## Design notes / links

- The fix most in keeping with `new_game`/`resume`'s existing split (build generic, then lay the
  mark back over it, per `session/snapshot.py`'s own module docstring) is to stop `_observe()` from
  running a doomed `_maybe_enter_room()` before restore: either have `resume()` reconstruct the run
  without the constructor's implicit `_observe()` firing an ambient call (e.g. a flag threaded
  through `new_game`, or restoring state before the first `_observe()` runs at all), or have
  `resume()` explicitly drop/replace whatever `_room_backstory` queued during construction once
  `apply_dict` has run, then call `_observe()` again for the real, restored position so the correct
  room still gets queued if it genuinely hasn't shown a toast yet.
- `session/run.py:_maybe_enter_room` (2139) and `_poll_toast` (2224) need no change under either
  approach; the fix is entirely about not calling them with a transient, about-to-be-discarded
  state in the first place.
- Related: DELVE-0060 (`visited_rooms` persistence, the mechanism this bug quietly defeats),
  DELVE-0083 (the prior, narrower instance of a doomed call still showing its loading spinner).

## Acceptance / verification

- A test resumes a snapshot on a chapter past the pack's starting one and asserts
  `_room_backstory.pending()` is `False` immediately after `resume()` returns (nothing was queued
  for the discarded pre-restore spawn room).
- A test resumes a snapshot whose current room is *not* yet in the restored `visited_rooms` (the
  edge case above) and asserts exactly one call is queued, keyed to the restored room, not the
  transient spawn one.
- A test resumes a snapshot whose current room *is* already in `visited_rooms` and asserts the
  first `Frame` built has `toast_loading is None` and `toast is None`.
- `./run-tests.sh` passes in both locales.

## Peer review

- Auto (implementing agent), 2026-08-02: fix matches the issue's preferred shape (`observe=False` through `new_game`/`RunState`, then `_observe` after `apply_dict`); `_poll_toast` and the snapshot shape are untouched; the three acceptance tests cover past-start quiet resume, unvisited-restored-room re-queue keyed to the restored chapter, and `toast_loading is None` when the room was already visited. `./run-tests.sh` green (668). Ready to land once you say so.
- Claude (agent), 2026-08-02: verified `_observe()` fires exactly once under both `observe` values (no double-fire, no dropped unvisited-room case); confirmed every other `new_game` call site is unaffected by the new default; checked the new tests' `RoomBackstoryRunner` internals and helpers are real, not fabricated. `./run-tests.sh` green (668 tests, ruff, pip-audit, issues index, all packs). No findings; matches the issue's design notes and stays inside its non-goals.

