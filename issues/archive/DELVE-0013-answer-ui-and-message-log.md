---
id: DELVE-0013
title: Answer UI and message log
status: implemented
area: [ui, session]
milestone:
version: 1.7.0
created: 2026-07-23
updated: 2026-07-25
commits: [873bc4a, 3c1c7d5, a3cb3f1]
related: [DELVE-0002]
supersedes: []
docs: [docs/BUTTONS.md]
changelog: "1.7.0"
---

# Answer UI and message log

## Summary

Rework how answers are presented and how messages behave. Assertions and MCQs render as the
same numbered list with a highlighted, navigable focus badge; a message log (`p`) keeps past
lines; and a stale top line no longer resurrects when the backpack opens. Boxed buttons were
prototyped in a PoC and then dropped in favour of the list.

## Motivation / problem

From a long session of real play: the answer chrome was inconsistent between question types,
messages scrolled away with no history, and opening the backpack could bring back an aged line.
Small frictions, but they are exactly the slide-deck feeling the project fights.

## Requirements

1. Assertions and MCQs MUST render as the same numbered-style list with a highlighted focus
   badge; arrows MUST move the focus and Enter MUST answer, alongside the direct number keys.
2. A message log MUST be openable with `p`, showing past lines in order.
3. The top message line MUST age out (`_visible_message`, `_MSG_TTL`); only a keeper-encounter
   overlay MUST freeze the clock, so opening the backpack MUST NOT resurrect an aged line.
4. Code blocks and inline code in a lesson MUST render verbatim; a URL, domain, or code span
   MUST NOT be broken across a page (`break_on_hyphens=False`).
5. The answer-drawing (numbered list, focus, two-way prompt) MUST stay a `ui`-only concern on
   the far side of rule 2; the session MUST NOT learn how options are drawn.

## Non-goals

- Boxed buttons as the shipped look; prototyped (4d0b773) then reverted to the list (a3cb3f1).
- Emoji in prose or prompts (DELVE-0014).

## Design notes / links

The message-ageing rule and the URL-wrapping trap are in `CLAUDE.md`; the buttons proposal and
its POC are `docs/BUTTONS.md` and `poc/`. The list-versus-buttons decision is recorded in the
CHANGELOG for 1.7.0.

## Acceptance / verification

- An MCQ and an assertion show the same navigable focus; number keys and Enter both answer.
- Opening the backpack after a message ages out does not redraw it.
- A lesson containing `yourcompany-hr.net` renders it unbroken across a page boundary.
