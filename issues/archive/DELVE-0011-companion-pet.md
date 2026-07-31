---
id: DELVE-0011
title: The companion pet
status: implemented
area: [engine, session, ui]
type: epic
milestone:
version: 1.2.0
created: 2026-07-19
updated: 2026-07-23
commits: [pre-reset]
related: [DELVE-0004, DELVE-0010]
supersedes: []
docs: [docs/PETS.md]
changelog: "1.2.0"
---

# The companion pet

## Summary

Give the learner an optional companion (a dog or a cat, or none), chosen at start. The pet is
a pure step function over its own RNG stream, roaming the floor and, for a cat, carrying and
retrieving coins. This expands the consultable companion introduced in the M4 stakes arc
(DELVE-0004).

## Motivation / problem

A NetHack pet is company and a little life on the floor. It must add warmth without ever
disturbing the deterministic dungeon or the exam shuffle.

## Requirements

1. The learner MUST pick a species at start: dog, cat, or none.
2. The pet MUST be a species `registry` plus a pure `step` returning a `PetEvent`.
3. Pet moves MUST draw from a dedicated `pet_rng`, never `self.rng`.
4. A carrying cat MUST keep collecting coins rather than freezing on the first, and MUST stay
   near the learner rather than camping a corner.
5. The pet MUST follow the learner through doors between rooms.
6. Item and slice tests that do not care about a pet MUST be able to run `pet_species="none"`
   so a roamer never competes for a placed coin or drifts onto a deterministic path.
7. The pet-picker keys MUST be localised (Dutch `[k]`/`[h]`).

## Non-goals

- An LLM driving pet behaviour or banter (research note only, not built).
- Any pet effect on scoring, HP, or the gate.

## Design notes / links

`engine/pet.py` (species registry, pure step) and the separate-RNG-streams rule are in
`CLAUDE.md`; the design is `docs/PETS.md`. The carry refinements (ad13120, 905d2f4) came from
real play in Dutch.

## Acceptance / verification

- A carrying-cat test asserts it collects more than one coin and stays near the learner.
- A `pet_species="none"` run leaves placed coins and deterministic paths untouched.
- Pet moves are reproducible from `pet_rng` alone; exam order is unaffected.
