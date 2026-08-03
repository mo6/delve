---
id: DELVE-0101
title: A two-stage loading toast, a shorter line first, the growing-clearer one after 5 seconds
status: proposed
area: [session, ui]
type: feature
epic:
effort: low
milestone:
version:
version_span:
created: 2026-08-03
updated: 2026-08-03
accepted_by:
accepted_at:
commits: []
related: [DELVE-0082, DELVE-0083, DELVE-0093]
supersedes: []
docs: []
changelog:
reason:
---

# A two-stage loading toast, a shorter line first, the growing-clearer one after 5 seconds

## Summary

The "still generating" spinner window shown while an ambient room toast is on its way (DELVE-0082)
always names itself with the same one line, `toast.loading` ("You hear a distant muttering, growing
clearer..."). Split it into two stages instead: a shorter line the moment the spinner first appears
("You hear a distant muttering..."), and today's existing "growing clearer" line only once the call
has been pending five seconds without resolving. A quick reply never shows the second line at all;
only a genuinely slow one does.

## Motivation / problem

`RunState._frame` (`delve/session/run.py:2607`) fills `Frame.toast_loading` with a single
`strings("toast.loading")` string for as long as `self._room_backstory.pending()` is true, however
long that ends up being. Most calls resolve quickly enough that the learner barely sees the spinner;
naming it with a line that already claims the mutter is "growing clearer" reads oddly for something
that just started, and gives the line nowhere to go if a call does take a while. A two-stage line,
vague first, more specific only once it has actually been a few seconds, better matches what is
really happening, and gives a slow call an escalation instead of a static placeholder.

## Stories

### As a learner waiting on a room's ambient toast, I want the loading line to reflect how long I've actually been waiting, so that a quick reply doesn't get an odd "growing clearer" line it never earned.

- Given a room's ambient toast has just started generating (the spinner has been showing for less
  than 5 seconds),
  when the loading line renders,
  then it reads "You hear a distant muttering..." (`en`) / "Je hoort een ver gemompel..." (`nl`).
- Given the same call is still pending 5 seconds or more after it started,
  when the loading line renders,
  then it reads "You hear a distant muttering, growing clearer..." (`en`) / "Je hoort een ver
  gemompel, dat steeds duidelijker wordt..." (`nl`), today's existing line, unchanged in wording.
- Given a call resolves in under 5 seconds (the common case),
  when the toast finishes and its text is delivered,
  then the learner never saw the second-stage line at all; only the first line showed, for
  whatever brief moment the spinner was up.

## Non-goals

- Not changing the spinner glyph, its animation cadence, or the window's layout (DELVE-0082's
  frame, DELVE-0093's redraw-cadence fix); only which of two strings fills the loading line, and
  when.
- Not changing anything about the idle-nudge's own prompt content or the ambient toast's own
  generated text once delivered; this is the placeholder line shown only while nothing has
  arrived yet.
- Not making the 5-second threshold configurable; one fixed constant, matching how
  `_NUDGE_DELAY_SECONDS` and `_SPINNER_MS` are already plain module constants, not settings.

## Design notes / links

- `delve/session/backstory.py:216` `RoomBackstoryRunner` tracks no timestamp today; `submit`
  (line 250) and `_pump` (line 258) would need to record a `time.monotonic()` when a call starts
  (submission time reads more honestly as "how long has the learner been waiting" than thread-start
  time, since a call can sit queued behind another one first). Expose it as something like
  `pending_ms(now: float) -> float | None`, mirroring the pure, testable style `_spinner_glyph`
  already uses for its own clock read, returning `None` when nothing is pending.
- `RunState._frame` (`delve/session/run.py:2607`), where `toast_loading` is currently filled, picks
  between `strings("toast.loading")` and the slow-stage key based on
  `self._room_backstory.pending_ms(time.monotonic())` against a new `_TOAST_SLOW_MS = 5000`
  constant defined alongside the file's other such constants.
- `delve/strings/en.toml:324` / `nl.toml:276` (`[toast]` section): the existing `loading` value,
  "You hear a distant muttering, growing clearer..." / "Je hoort een ver gemompel, dat steeds
  duidelijker wordt...", is already exactly the wording wanted for the *slow* stage, so move it
  under a new key (e.g. `toast.loading_slow`) rather than retyping it, to avoid a copy-paste drift
  between the two locales; add a new `toast.loading` (or `toast.loading_first`, name to taste) for
  the immediate stage: "You hear a distant muttering..." / "Je hoort een ver gemompel...".
- No screen-layout change (same window, same wrapping budget), so no `./tools.sh screenshot`
  scenario needs a new mock-up; the existing `toast` scenario is unaffected since it shows a
  resolved toast, not the loading spinner.

## Acceptance / verification

- A `RoomBackstoryRunner`-level test asserting `pending_ms` is `None` with nothing queued, and
  reports elapsed time (via an injected/fake clock, not a real `sleep`) once a call is submitted.
- A `RunState`-level test asserting `toast_loading` reads the first-stage line just after a room
  entry queues a call, and the slow-stage line once elapsed time crosses the 5-second threshold
  (both driven by a fake clock, not a real timer).
- A locale test (`tests/test_languages.py`) asserting both `en`/`nl` carry both keys, non-empty,
  and that the slow-stage value in each locale is byte-identical to today's pre-change
  `toast.loading` value (so the visible wording for a slow call does not drift as part of this
  split).
- `./run-tests.sh` green, both locales.
