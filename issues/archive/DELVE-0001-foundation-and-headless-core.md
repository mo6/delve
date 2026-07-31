---
id: DELVE-0001
title: Foundation and headless core
status: implemented
area: [engine, session, ui, tools]
milestone: M0-M1
version: 0.1.0
created: 2026-07-17
updated: 2026-07-17
commits: [5539cce, 9a1643d]
related: [DELVE-0002]
supersedes: []
docs: [docs/PLAN.md]
changelog: "0.1.0"
---

# Foundation and headless core

## Summary

Stand up the project skeleton and the one architectural bet the whole app rests on: the game
loop lives in `session/`, is pure (`apply(Command) -> Frame`, no curses, no I/O, no blocking),
and `ui/` only maps keypresses to commands and paints frames. A generated dungeon chapter is
walkable end to end through a headless harness, and the layering rule is enforced in CI.

## Motivation / problem

A loop written inside curses can only be tested through a pty, which in practice means it is
not tested. The M1 headless harness plays a whole run as a list of commands, and every later
milestone leans on it. The boundary has to exist and be enforced from the start, because it
fails invisibly if intention is all that holds it.

## Requirements

1. The game loop MUST live in `session/` and expose `apply(Command) -> Frame` with no curses,
   no blocking, and no I/O.
2. `ui/` MUST import only `session`, `ui`, and the top-level `delve` package; it MUST NOT
   import `engine`, `content`, `assess`, or `progress`.
3. `engine/` MUST NOT import `content`, `assess`, `session`, or `ui`.
4. A generated chapter MUST be walkable start to finish through a headless command harness,
   with no curses involved.
5. The import rules above MUST be enforced by an automated test that runs in CI from M1.
6. On a terminal below the 100x30 minimum the app MUST show a resize overlay and wait, never
   degrade or crash.

## Non-goals

- Content parsing, examinations, stakes, or persistence (later milestones).
- A second frontend. Testability is the reason for the boundary; portability is a side effect.

## Design notes / links

The five rules and the loop/ui split are `CLAUDE.md` rule 1 (both halves); rationale and the
milestone framing are in `docs/PLAN.md`. Generation is the only path to a map; there is no
map file format (PLAN section 3).

## Acceptance / verification

- The import-rule test passes and would fail if `render.py` grew an `import engine`.
- The headless harness plays a full generated chapter as a command list.
- `./run-tests.sh` is green (pytest, ruff, screen self-check).
