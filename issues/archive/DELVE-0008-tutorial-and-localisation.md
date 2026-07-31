---
id: DELVE-0008
title: Tutorial floor and localisation
status: implemented
area: [delve, session, ui, content]
milestone: M6
version: 0.6.0
created: 2026-07-18
updated: 2026-07-25
commits: [pre-reset]
related: [DELVE-0005, DELVE-0007]
supersedes: []
docs: [docs/PLAN.md, docs/STYLE.md]
changelog: "0.6.0"
---

# Tutorial floor and localisation

## Summary

Add an engine-provided tutorial floor at Dlvl 0 that teaches the interface, and complete the
en/nl localisation so every message, label, and keeper voice is catalogued and locale-chosen.
The tutorial ships with the engine, not with each pack, because the interface is identical
across packs.

## Motivation / problem

Whoever skips onboarding must still be able to play; the interface is the same everywhere, so
a pack author should never have to write (or be able to forget) a tutorial. And a half-Dutch
dungeon is worse than an English one: a locale must be complete or absent.

## Requirements

1. The tutorial MUST be an ordinary pack in `delve/tutorial/{en,nl}/`, engine-provided, at
   Dlvl 0 so a pack's chapter 1 is Dlvl 1.
2. The tutorial MUST be never scored: no `room_results`, no scroll contribution.
3. The tutorial MUST be skippable two ways: a `[yn]` prompt on arrival (defaulting to yes for
   anyone with a completed run) and stairs that are never sealed on this floor.
4. The tutorial MUST demonstrate the door-appears loop once (the first keeper seals his door)
   and then leave open stairs (the last keeper seals nothing).
5. The tutorial MUST always be in the chapter list; `skip_tutorial` MUST only move the start
   position, leaving the tutorial reachable with `<`.
6. Every engine string MUST come from `delve/strings/{en,nl}.toml` via a `Strings` accessor;
   `ui` MUST NOT import the strings catalogue and MUST receive `Strings` opaquely.
7. A locale MUST be complete or absent; there MUST be no per-room fallback.
8. Formatting (currency, thousands, decimal, month case) MUST come from the locale `[format]`
   table.
9. Dutch MUST use tutoyeer (`je`, never `u`) and sentence case in headings.

## Non-goals

- CJK locales; the scope is en/nl only, which is what keeps the box-drawing borders safe.
- A gettext toolchain; strings are stdlib `tomllib` only.

## Design notes / links

The tutorial floor section and the Languages section of `CLAUDE.md`; voice rules in
`docs/STYLE.md`. The tutorial is coupled to the renderer and nothing checks that, so a screen
change means grepping `delve/tutorial/` in both locales. Env-var defaults for the learner and
pet names landed later (92701d6).

## Acceptance / verification

- `tests/test_languages.py` and tutorial tests pass; the tutorial writes no `room_results`.
- Playing `--lang nl` shows Dutch chrome, `[Jn]` prompts, and Dutch number/date formatting.
- `delve validate` is clean on the tutorial despite its missing scroll (warning, not error).
