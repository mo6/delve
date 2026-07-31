---
id: DELVE-0009
title: Polish, ACS walls, bump-to-act
status: implemented
area: [ui, session]
milestone: M8
version: 0.8.0
version_span: 0.8.0-0.8.4
created: 2026-07-18
updated: 2026-07-18
commits: [2d5dd3e, 3980617, ef4e20b, 52fb161, f9edcae]
related: [DELVE-0002]
supersedes: []
docs: [docs/PLAN.md, docs/SCREENS.md]
changelog: "0.8.0"
---

# Polish, ACS walls, bump-to-act

## Summary

The M8 polish pass: a portable 16-colour palette, keeper voices, a formatted win screen, room
walls drawn with ACS line-drawing, and NetHack bump-to-act interaction (walking into a keeper
talks to it).

## Motivation / problem

The slice worked but read as a prototype. Colour, voice, real borders, and familiar NetHack
interaction turn it into something a first-time player recognises and enjoys.

## Requirements

1. Colour MUST use only the portable 16 colours; 256-colour and extended-colour APIs MUST NOT
   be used.
2. Room walls MUST be drawn with `ACS_` line-drawing constants (portable by construction),
   not literal Unicode box characters.
3. Walking into a keeper MUST talk to it (bump-to-act): the step routes onto the keeper's tile
   to `_talk`, the keeper still blocks the tile, and a bump costs a turn.
4. Re-reading a passed keeper via `t` MUST be free, and re-bumping a passed keeper MUST be a
   brush-off, not a re-lesson.
5. The win screen MUST be formatted session-side (`outcome_lines`); `ui` MUST NOT touch
   `scrolls`.
6. When two hints compete underfoot, the stair hint MUST win over the talk hint.

## Non-goals

- Emoji or wide glyphs (later arc, DELVE-0014); map glyphs stay ASCII.
- Double-line window frames beyond the deliberate Unicode bet with an ACS fallback.

## Design notes / links

The cross-platform and colour rules, bump-to-act (rule 3 interaction), and the status/hint
line design are in `CLAUDE.md`. The win line running off the edge was later fixed by wrapping
centred screens (55c2ab2, see DELVE-0012 arc).

## Acceptance / verification

- Screen self-check passes with ACS walls (`python tools/screens.py --check`).
- A bump-into-keeper test asserts the turn cost and that the learner never moves onto the tile.
- A passed-keeper re-bump asserts no re-examination.
