---
id: DELVE-0050
title: Ambient story, take 3 - one line at a time, on room entry and every few steps
status: implemented
area: [assess, content, session, docs]
type: story
effort: low
milestone:
version: 1.18.0
version_span:
created: 2026-07-27
updated: 2026-07-27
accepted_by: George Moses
accepted_at: 2026-07-27
commits: [pre-reset]
related: [DELVE-0048, DELVE-0049]
supersedes: []
docs: []
changelog:
reason:
---

# Ambient story, take 3 - one line at a time, on room entry and every few steps

## Summary

[[DELVE-0049]]'s `story.py` generated a batch of 10-20 ambient one-liners per room, all at once,
right after the room was passed. This take changes the cadence in `story.py` (`ambient.py` stays
untouched, same as before): generate exactly **one** line at two trigger points instead, so the
ambient text reads as a drip of incidental detail alongside play rather than a paragraph dumped at
each doorway:

1. **On entering a room** (arriving at the keeper, before the lesson/examination starts).
2. **Every ~5 steps** while walking between rooms (a configurable step interval), grounded in the
   current floor generically (no specific room, since the player is between keepers).

## Motivation / problem

A 10-20 line batch reads as a report, not an experience; a single line, timed to something the
player is actually doing (arriving somewhere, or having walked a while), is closer to how NetHack's
own occasional flavour messages work, and is cheaper per call besides.

## Proposed approach

- A step counter incremented on every simulated `Move`; when it reaches the interval (default 5),
  generate one line grounded in the current chapter (and, if the player is mid-approach to a
  specific keeper, that room) and reset the counter.
- On arrival at a room's keeper (right before `Pickup`/`Talk`), generate one line grounded in that
  room specifically, and reset the step counter so a room-entry line and a step-tick line don't
  double up back to back.
- `_static_context` gains a "no specific room, walking a corridor on this floor" fallback for the
  step-tick case between rooms, where there is no single room to ground the line in.
- Reuse the existing continuity mechanism (`ambient_log`, `--ambient-window`) and locale handling
  from DELVE-0049 unchanged; only the generation cadence and per-call line count change.
- `--count` still exists but now defaults to `1`; a new `--step-interval <n>` (default `5`)
  controls the walking cadence.

## Findings

Built as planned: a `Pacer` class in `story.py` fires exactly one generation call on room entry
(grounded in that room) and every `--step-interval` (default `5`) simulated steps while walking
between rooms (grounded generically in the current floor via a new corridor fallback in
`_static_context`, since no specific room applies). `--room <id>` was redefined to mean "stop the
walk once this room is reached," since generation is now continuous rather than gated per room.
Verified mechanically correct: entering a room fires exactly one line, corridor walking fires one
every `--step-interval` steps using the corridor-grounded prompt.

The acceptance criterion asking whether DELVE-0049's findings still show up at this cadence has a
clear answer: **yes, and markedly worse.** Tested against the full pilot pack at the default
`--ambient-window` (`24`) and a tighter one (`4`):

- At `24`, the model fixated on a single image partway through chapter 2 ("Ada's voice hums
  softly, stirring the last lingering dust motes...") and repeated it with only cosmetic
  noun-swaps for the rest of the pack, well into chapters 3 and 4, the same cross-chapter
  bleed-through DELVE-0049 found, but now as one obsessive motif instead of a rotating handful.
- At `4`, it got worse: the model locked onto one line and repeated it **verbatim, unchanged**,
  dozens of times through the rest of the run.

Likely cause: at one line per call, the fed-back "ambient so far" list is now dominated by the
model's own immediately-preceding output (calls happen every ~5 steps rather than once per room),
so each call effectively reads as "continue what you just said." This is the opposite of what the
smaller cadence was hoped to fix; it suggests the flat, verbatim continuity mechanism from
DELVE-0049 is the wrong shape once generation happens this frequently, not merely a tuning problem.
Full detail in `poc/ambient-flavour/README.md`'s "Early observations." Not fixed here: candidates
worth trying next (only reminding the model of the last room-entry line rather than every
step-tick line, an explicit "don't just reword your last line" instruction, or no continuity at
all for step-tick generations) are noted but unbuilt.

## Acceptance criteria

Given a full pack walk, when the trail is produced, then each room's arrival yields exactly one
ambient line (not a batch), and additional single ambient lines appear interspersed with gameplay
messages roughly every `--step-interval` simulated steps while walking between rooms.

Given the step-tick case (no specific room), when its prompt is built, then it is grounded in the
chapter's own prose rather than inventing an ungrounded generic dungeon scene.

Given this changes call frequency substantially (many more, much shorter generation calls per
pack), this issue records whether the earlier DELVE-0049 findings (cross-chapter bleed-through,
motif convergence) still show up at this new cadence, or behave differently.

## Non-goals

- Not a change to `ambient.py` (DELVE-0048); `story.py` alone changes.
- Not a fix for DELVE-0049's cross-chapter bleed-through finding; if it recurs at this cadence it
  is still an open problem, not addressed here.
- Not a change to the demo interactions (consult/brush-off/rest) or locale/continuity mechanisms.
