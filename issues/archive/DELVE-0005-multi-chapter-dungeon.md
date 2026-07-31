---
id: DELVE-0005
title: Multi-chapter dungeon and the scroll
status: implemented
area: [session, engine, gate]
milestone: M5
version: 0.5.0
created: 2026-07-18
updated: 2026-07-18
commits: [a56be86]
related: [DELVE-0006, DELVE-0008]
supersedes: []
docs: [docs/PLAN.md]
changelog: "0.5.0"
---

# Multi-chapter dungeon and the scroll

## Summary

Grow the single slice into a full dungeon: a pack becomes several floors (chapters), connected
by stairs, every room gated. Finishing the pack awards a scroll, presented on a pedestal. This
is where `new_game` builds the whole multi-chapter dungeon from a parsed pack.

## Motivation / problem

A real training is more than one lesson. The dungeon needs depth (a `Dlvl` per chapter), a way
down, and a payoff at the bottom that stands in for completion.

## Requirements

1. `new_game` MUST build a full multi-chapter dungeon from a parsed pack, every room gated.
2. Each chapter MUST be one floor with its own `Dlvl` in the status line; the word "level"
   MUST NOT be used for either a floor or a lesson.
3. Chapters MUST be connected by stairs the learner descends.
4. Completing the pack MUST award a scroll, presented on a pedestal (`scroll.md`).
5. The scroll's numbers and date MUST be formatted from the locale `[format]` table, never via
   `locale.setlocale` or `strftime('%B')`.

## Non-goals

- Persistence, snapshot, resume, and the trophy case (DELVE-0006).
- The tutorial floor at Dlvl 0 (DELVE-0008).

## Design notes / links

The generator (smallest cell partition, serpentine order, L-shaped corridors, connected by
construction) and terminal/layout rules are in `CLAUDE.md`. Formatting is locale data, not
translation: `progress/scrolls.py` takes the `[format]` table as an argument (PLAN section 8).

## Acceptance / verification

- A multi-chapter run descends through every floor and reaches the scroll.
- A pack with N rooms generates the expected gated layout deterministically from
  `(seed, cols, rows)`.
- Scroll formatting tests pass for en and nl (currency, thousands, month case).
