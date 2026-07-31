---
id: DELVE-0002
title: "Vertical slice: the door appears"
status: implemented
area: [session, gate, assess, ui]
milestone: M2
version: 0.2.0
created: 2026-07-17
updated: 2026-07-17
commits: [pre-reset]
related: [DELVE-0001, DELVE-0003]
supersedes: []
docs: [docs/PLAN.md, docs/SCREENS.md]
changelog: "0.2.0"
---

# Vertical slice: the door appears

## Summary

The go/no-go slice. With hard-coded content and no parser, a learner walks to a keeper, reads
a lesson in a panel beside the room, sits an examination, and on passing sees a sealed door
turn into an open one. This exists to answer the core bet: does a dungeon make training land
better than a slide deck?

## Motivation / problem

Everything downstream is wasted effort if the central experience is boring. M2 is a decision
point, not a checkpoint: if the slice does not land, the right move is to rethink, not to
proceed to M3.

## Requirements

1. The learner MUST be able to walk to a keeper and trigger a lesson.
2. A lesson MUST render as a panel beside the room, keeping the room, the keeper, and the
   learner visible, never a full-screen takeover.
3. The examination MUST share the keeper's panel and accept answers.
4. Passing the examination MUST make the room's exit appear (a sealed door becomes passable).
5. The exit MUST remain solid stone until the examination is passed; there MUST be no path
   around the lesson.
6. The slice MUST run through the headless harness without curses.

## Non-goals

- Parsing packs from Markdown (DELVE-0003); the slice is hard-coded on purpose.
- Stakes, scoring, persistence, multiple chapters.

## Design notes / links

Sealed doors are structural (`CLAUDE.md` rule 2): no path validation, no flood fill. The
panel-beside-the-room layout and its column math are verified in `docs/SCREENS.md`; the panel
is 69 columns, which is the real reason the minimum is 100 columns.

## Acceptance / verification

- Headless harness: walk to keeper, answer correctly, assert the exit tile becomes passable.
- Screen mock-ups in `docs/SCREENS.md` match (`python tools/screens.py --check`).
- The box-fill curses bug (interior fill wrapping to the next row) is fixed (ba42389).
