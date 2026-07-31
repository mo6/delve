---
id: DELVE-0061
title: A regenerated nudge toast if a first-time player hasn't moved a few seconds in
status: implemented
area: [session, ui, delve, docs]
type: feature
epic:
effort: medium
milestone:
version: 1.24.0
version_span:
created: 2026-07-30
updated: 2026-07-30
accepted_by: George Moses
accepted_at: 2026-07-30
commits: [3245e52]
related: [DELVE-0060]
supersedes: []
docs: [docs/SCREENS.md]
changelog: "1.24.0"
---

# A regenerated nudge toast if a first-time player hasn't moved a few seconds in

## Summary

If a learner is sitting in the very first room of a brand-new run (never having taken a single
step yet) and the room's ambient toast (DELVE-0060) has been showing for about ten real seconds
with still no movement, a second passage is generated to replace it: the same keeper's voice,
nudging the learner to try the arrow keys. This is a one-shot hint aimed squarely at the person who
skipped the tutorial and is staring at the screen unsure what to press, the same audience the hint
line and the tutorial floor already exist for (CLAUDE.md, "The hint line is not decoration").

## Motivation / problem

The hint line already says `Move: arrows` from the first frame, so this is not the only signal a
stuck learner has; but a static line easy to skim past is exactly the gap DELVE-0028's whole `?`
help effort exists to close, and the ambient toast has already proven (DELVE-0060, the "appears
without a keypress" and the cross-chapter fixes) that this game pays attention to a learner who
hasn't acted yet. A second, keeper-voiced nudge that only fires when someone has genuinely sat
still for several seconds is a small, cheap way to catch the person the hint line's own justification
names, without nagging anyone who is simply reading the first toast at a normal pace.

## Stories

### As a first-time learner who hasn't moved yet, I want a nudge after sitting still a few seconds, so that I'm not stuck wondering what to press.

- Given a brand-new run, before any `Move`/`Wait`/other turn-advancing command has ever been
  applied (`self.turn == 0`), and the starting room's ambient toast has already appeared,
  when about ten real seconds pass with the learner still not having moved,
  then a new background call replaces the toast with a short passage, still in that room's keeper
  voice (or the chapter title, for an ungated starting room, the same fallback DELVE-0060's toast
  title already uses), that suggests trying the arrow keys.
- Given the learner moves (or otherwise advances a turn) at any point before the ten seconds are
  up,
  when the timer would have fired,
  then it never does: the ordinary ambient toast (or its natural ageing-out) is unaffected, and no
  nudge is generated for a learner who was never actually stuck.
- Given the nudge has already fired once this run,
  when the learner later stands still again (in this room or any other),
  then it does not fire again; this is a one-shot first-impression hint, not a recurring idle
  timer.

### As a learner who isn't new (an unfinished run being resumed, or one already past its first room), I want this to never apply to me, so that it stays a first-room-only kindness.

- Given a resumed run, or any point in a run other than the very first room before the first move,
  when the learner stands still for any length of time,
  then no nudge is ever generated; this feature is scoped to the single earliest possible moment a
  learner could be stuck, not a general "idle too long" mechanic.

### As a learner with no grader model configured, I want nothing to change for me, so that this stays optional exactly like the ambient toast itself.

- Given no model is configured, or the nudge call fails or times out,
  when the ten seconds pass,
  then nothing happens: no nudge, no error, and the ordinary toast (or nothing, if none was ever
  generated) is left exactly as it was.

## Non-goals

- A general "learner has been idle N seconds" mechanic reusable beyond this one moment. Scoped
  strictly to the first room, before the first move, once per run.
- Any change to the hint line, the tutorial floor, or the `?` help screen; this is additive, a
  second toast content swap, using machinery DELVE-0060 already built.
- A fallback hand-written nudge string when no model is configured. Consistent with every other
  ambient-prose feature so far (DELVE-0028/0057/0060): silence, not a canned substitute.
- Repeating or escalating nudges (a second, more insistent one after another idle stretch). One
  shot only.

## Design notes / links

**Wall-clock, not turns.** `_TOAST_TTL`'s existing ageing is turn-based (`self.turn - self
._toast_turn`), which cannot express "ten seconds of standing still", since `self.turn` never
advances while the learner does nothing. This needs a real timestamp captured when the qualifying
toast first appears (`time.monotonic()`, not `datetime.now()`: monotonic is immune to a system
clock adjustment happening to land mid-run) and compared against on every `frame()` poll.

**Keeping the poll loop alive.** DELVE-0060's own "appears without a keypress" follow-up added
`Frame.toast_pending`/`ui/app.py`'s short-timeout wake loop, but that loop only stays active while
`RoomBackstoryRunner.pending()` is true; once the first toast is delivered, polling reverts to
blocking on the next keypress, so a ten-second wall-clock deadline would never be checked while the
learner sits idle. `RunState` needs its own "still waiting to decide about the nudge" flag folded
into `toast_pending` alongside the runner's own `pending()`, armed the moment the qualifying toast
is shown and cleared once the nudge fires, is cancelled by a move, or the deadline is judged not to
apply (any room but the first, or turn > 0 already).

**Reusing `RoomBackstoryRunner`.** The nudge call is a second, distinct submission to the same
queue-of-one-in-flight runner (DELVE-0060), keyed by something that cannot collide with the
starting room's own id (e.g. `f"{room_id}::nudge"`), carrying its own opaque context
`(title, chapter_idx)` exactly like every other submission, so the existing "drop it if the
learner has since changed chapters" guard (the cross-chapter fix) applies here for free.

**The prompt.** A new template, sibling to `backstory.PROMPT`, asking for a very short passage in
the same keeper's voice that naturally suggests trying the arrow keys to move, reusing
`build_prompt`'s existing pack/chapter/keeper facts rather than a whole new fact-gathering path.
Exact wording is an implementation detail for the accepted issue, not fixed here.

**Mock-up.** Once accepted, a mock-up will be built the same way DELVE-0060's own toast was staged
before landing (`./tools.sh toast_mockups`, promoted into `docs/SCREENS.md` once shipped), showing
the replaced toast text; not drawn here since the exact prompt/wording isn't settled yet.

## Acceptance / verification

- A test constructs a fresh run, settles the starting room's toast, advances a fake clock past the
  ten-second threshold with `self.turn` still 0, and asserts a second call is queued and, once
  resolved, replaces the toast.
- A test asserts moving before the threshold (`self.turn` no longer 0) prevents the nudge from
  ever firing, even if the fake clock is later advanced past ten seconds.
- A test asserts the nudge never fires a second time even if the learner stands still again later
  in the same run.
- A test asserts nothing happens (no nudge, no error) with no grader model configured.
- A test asserts a resumed run (idx/turn restored from a snapshot past the first room) never
  arms the nudge at all.
- `./run-tests.sh` passes.
