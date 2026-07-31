---
id: DELVE-0060
title: An asynchronous ambient toast on first entering a room, replacing Objectives' buried passage
status: implemented
area: [session, ui, delve, docs]
type: feature
epic:
effort: high
milestone:
version: 1.23.0
version_span:
created: 2026-07-30
updated: 2026-07-30
accepted_by: George Moses
accepted_at: 2026-07-30
commits: [pre-reset]
related: [DELVE-0028, DELVE-0057, DELVE-0059]
supersedes: []
docs: [docs/SCREENS.md, docs/PHASE2.md]
changelog: "1.23.0"
---

# An asynchronous ambient toast on first entering a room, replacing Objectives' buried passage

## Summary

The optional LLM scene-setting passage (DELVE-0028, fixed to actually produce prose by DELVE-0057)
is easy to miss: it only shows on the Objectives tab, and once a run has any static facts at all it
routinely lands on page 2 behind a `--More--`, so a learner who never opens `?` twice never sees it.
This replaces that placement with an unobtrusive, non-blocking **toast**: a small right-anchored
block, several lines tall, that appears near the top of the screen the first time the learner steps
into *any* room this run (gated or not), giving that room its own short ambient passage rather than
one passage for the whole run. It appears asynchronously, whenever the background call for that
room resolves, and never pauses play; the learner can keep moving, talk to a keeper, or open a
panel while it is up. The Objectives tab keeps its static pack/chapter/room/progress summary but
drops the passage entirely, since the toast is now the one place ambient prose appears.

## Motivation / problem

Confirmed directly: at 100x30 with even a small pack, Objectives' static facts (pack, chapter,
progress, next keeper) already fill most of page 1, so the passage appended after them almost
always lands on page 2, and a learner has no way to know page 2 holds anything worth reading.
Burying the one piece of content designed to add atmosphere behind a page flip the learner has no
reason to make defeats its own purpose. Moving it to something that appears on its own, exactly
when it is narratively relevant (stepping somewhere new), fixes the discoverability problem and
makes the feature's value legible without asking the learner to go looking for it. Generating one
passage per room instead of one per run also fits "ambient" much better: a fresh mood beat as the
dungeon changes around the learner, not a single fixed passage repeated in spirit (even if not
literally shown again) for an entire pack.

## Stories

### As a learner, I want a short ambient passage to appear when I first step into a room, so that the dungeon feels atmospheric without me having to go looking for it.

- Given the learner steps onto a tile inside a room they have not stood in before this run
  (`engine.world.Room.contains`, the same check `_pet_step`'s fetch logic and the reward-tile pick
  already use elsewhere in `session/run.py`),
  when a grader model is configured and reachable,
  then a background call is started for that room, and once it resolves, a toast appears: a small
  bordered block anchored near the top-right of the screen, titled with the room's chapter/keeper
  context, holding the passage over several wrapped lines.
- Given the learner re-enters a room already visited this run,
  when they step back into it,
  then no new call is made and no toast reappears; "first time" is tracked per room, per run.
- Given the call has not resolved yet (the model is slow, or a cold load),
  when the learner is already elsewhere,
  then nothing blocks: movement, talk, panels and the hint line all work exactly as if the call
  were not in flight, and the toast simply appears later, still labelled for the room it was about.

### As a learner, I want the toast to go away on its own, so that it never becomes something I have to manage.

- Given a toast is showing,
  when several turns pass with no new one queued,
  then it fades (clears) on its own, the same "ages out, never needs dismissing" shape the top
  message line already has (`_MSG_TTL`, `RunState._visible_message`), just with its own, longer
  budget since it is more to read.
- Given the learner opens a blocking panel (a lesson, an examination, the backpack, Help) while a
  toast is up,
  then the toast does not fight that panel for the screen (design notes below settle exactly how);
  either way, no key is required to put the toast away on its own account.

### As a learner, I want no model configured (or an unreachable one) to simply mean no toasts, so that this stays optional exactly like the passage it replaces.

- Given no grader model is configured, or a room's call fails or times out,
  when the room is entered,
  then no toast appears, no error is shown, and nothing about play is blocked or delayed
  (DELVE-0033's grading requirement does not extend to this, the same non-goal DELVE-0028 already
  established for the single per-run passage).

### As a learner, I want the Objectives tab to stay useful without the passage it used to carry, so that removing it does not leave a gap.

- Given the Objectives tab,
  when it is shown,
  then it renders only the static facts (`RunState._objectives_facts`, unchanged): pack, chapter
  position and title, rooms passed, and the next unpassed gate's keeper and requirement, without
  the appended passage block DELVE-0028 added and DELVE-0057 fixed.
- Given a resumed run,
  when it is rebuilt from a snapshot,
  then which rooms have already shown their toast this run is restored too, so resuming never
  re-triggers a toast for a room the learner already stood in before quitting.

## Non-goals

- A dismiss key for the toast. It is read-only ambience; it ages out on its own, the same as the
  message line, rather than adding another panel a learner must remember how to close (and Keys
  gains no new entry for it).
- Any change to how the tutorial floor plays; its rooms get toasts on the same "any room" rule as
  a pack floor, with no special-casing, since the tutorial already treats itself as an ordinary
  pack for everything except scoring (CLAUDE.md, "The tutorial floor").
- Rate-limiting or restricting which rooms trigger a call beyond "not visited yet this run". A
  chapter with many rooms means many calls over the course of playing it; that cost is accepted as
  the point of "ambient," not a problem to design around here. If it proves too chatty or too slow
  in practice, throttling is a follow-up, not a blocker to shipping this.
- Persisting the toast's *text* itself through a snapshot (unlike DELVE-0028's single passage,
  which had to survive a resume since Objectives could be reopened at any time). Only the *set of
  rooms already shown one* needs to survive resume (so it isn't re-triggered); the passage text
  itself is transient, shown once, then gone, exactly like a fresh room's would be if the learner
  simply hadn't quit.
- Choosing a separate, more advanced model for this (DELVE-0058, still proposed separately); this
  issue reuses whatever client the grader is already configured with, same as DELVE-0028 did.

## Design notes / links

**Trigger.** `RunState._move` already resolves the destination tile; add a lookup
`next((r for r in self.chapter.rooms if r.contains(dest)), None)` (the same idiom
`_pay_reward`/`_pet_step`'s room lookups already use) and compare its `id` against a new
per-chapter `visited_rooms: set[str]` on `ChapterRun` (sibling to `discovered`/`items`, carried by
the snapshot the same way). A room not yet in that set, first entered, queues a call; the chapter's
starting room counts as entered at chapter arrival (`new_game`/chapter-change), not deferred to the
first step.

**Generation and caching.** `session/backstory.py`'s `BackstoryRunner` (DELVE-0028/DELVE-0057)
was one passage per run; this generalises it to one *in-flight* call at a time (mirroring
`ThreadedGrader`'s "one grade in flight" simplicity, since a learner can only be entering one new
room at a time in practice) keyed by room id, with a small pending queue for the rare case a second
new room is entered before the first call resolves. `chat(prompt, json_mode=False,
temperature=0.8)` (DELVE-0057) is unchanged; only the prompt's room/keeper facts and the cache key
change from "once per run" to "once per room id". A completed call's `(room_id, text)` is what
`RunState.apply`/`frame()` polls for and turns into a toast the next time a `Frame` is built.

**Display.** A new `ToastView` in `session/views.py` (title, `list[TextBlock]` body, distinct from
`Overlay`) and a new `Frame.toast: ToastView | None` field, independent of `Frame.overlay`: unlike
every existing overlay, a toast must coexist with ordinary walking (or even a panel) rather than
being the one blocking thing shown, so it cannot reuse the `overlay` slot's exclusive-panel
machinery (`_move`/`_talk`/etc. all early-return when `self._overlay is not None`; a toast must
never trip that guard). `ui/windows.py` gains a small top-anchored drawing routine (unlike every
panel's vertically-centred box, so it visibly reads as "weather over the room," not a paused
dialogue); whether it is suppressed while a blocking panel is open (simplest: just don't draw it
that frame, it is still ageing and will have expired or not depending on when the panel closes) or
drawn regardless (their geometries do not collide today, since a toast sits high and every existing
panel is vertically centred lower) is an implementation choice for the accepted issue to settle,
not fixed here.

**Ageing.** A new, longer-budget counterpart to `_MSG_TTL`/`_visible_message` (a toast holds more
to read than one status line, so it should hold longer; an exact turn count is a tuning choice for
implementation, informed by the pilot pack's play-testing the same way `_MSG_TTL`'s value of 2 was).

**Mock-up** (generated, not hand-drawn: `./tools.sh toast_mockups`, kept out of
`all_screens()`/`docs/SCREENS.md` on purpose, the same convention `tools/infoscreen_mockups.py`
already set for DELVE-0035's proposed screens, since neither exists yet):

```
You step into the archive.

                                                      ╔══════════════════════════════════════════╗
                                                      ║ The Archive                              ║
                                                      ║                                          ║
                                                      ║ Dust motes drift through the dim         ║
                                                      ║ afternoon light as ledgers stack in      ║
                                                      ║ uneven towers, waiting for someone       ║
                                                      ║ patient enough to set them straight.     ║
    ┌────────────────────┐                            ╚══════════════════════════════════════════╝
    │....................│
    │..<.................│
    │....................│
    │.................@..│
    │................f...│
    │....................│
    │....................│
    └────────────────────┘




George the Novice   Dlvl:1  Rooms:1/3  $:70  HP:12(12)  T:119
Move: arrows    Talk: t    Help: ?    Quit: q
```

A second mock-up (`tools/toast_mockups.py`'s `screen_toast_fading_while_walking_on`) shows the
learner having moved to the far side of the room while the toast is still up, the concrete proof
this is non-blocking: the hint line and every key still behave exactly as an ordinary walking frame.

## Acceptance / verification

- A test walks into a fresh room and asserts a background call is started, keyed by that room's
  id; walking back out and in again asserts no second call is made.
- A test asserts `frame().toast` is `None` while a call is pending, becomes the resolved passage
  once the fake client's call completes, and that `frame().overlay`/hint/turn are completely
  unaffected by a pending or resolved toast (the non-blocking story).
- A test asserts the toast clears itself after its ageing budget elapses with no further input,
  the same shape `_MSG_TTL` is already tested with.
- A test asserts a snapshot round-trip preserves which rooms have already shown a toast (no
  re-trigger on resume), without needing the passage text itself to survive.
- A test asserts the Objectives tab's body no longer contains any passage text, only the static
  facts, and that a fake client configured to fail is never even queried by Objectives anymore
  (that call site is gone; only room entry queries it).
- `./tools.sh toast_mockups --check` passes; once built, an equivalent frame moves from there into
  `docs/SCREENS.md`'s real gallery via `tools/screens.py`, the same promotion `docs/INFOSCREEN.md`'s
  mock-ups are expected to get once DELVE-0035's remaining tabs ship.
- `./run-tests.sh` passes.
