---
id: DELVE-0004
title: "Stakes: HP, attempts, REPELLED"
status: implemented
area: [session, gate, engine]
milestone: M4
version: 0.4.0
created: 2026-07-17
updated: 2026-07-17
commits: [4ce7fc9, 68de4f4]
related: [DELVE-0011]
supersedes: []
docs: [docs/PLAN.md]
changelog: "0.4.0"
---

# Stakes: HP, attempts, REPELLED

## Summary

Give the dungeon tension without punishing slow learning. A learner sits a whole room, sees
every explanation, and gets a score; missing the pass mark charges HP once per sitting. Running
out of attempts pushes the learner back (REPELLED); HP hitting zero respawns them at the
chapter entrance with every earned door still open. This arc also introduced the consultable
companion, later expanded in DELVE-0011.

## Motivation / problem

Tension must come from the dungeon, never from the material. An earlier "HP per wrong answer"
model made REPELLED unreachable and punished learning; the unit of stakes has to be the
sitting, not the answer.

## Requirements

1. HP MUST be charged once per sitting that misses the pass mark, never per wrong answer.
2. A single wrong answer MUST cost nothing beyond its explanation.
3. A room's total bleed MUST be `penalty x attempts`, capped below starting HP, so REPELLED
   lands before HP reaches zero.
4. Running out of attempts MUST push the learner back (REPELLED), not end the game.
5. HP reaching zero MUST respawn the learner at the chapter entrance with every earned door
   still open.
6. REPELLED and respawn MUST NOT close any earned door or erase any passed result.

## Non-goals

- HP regeneration policy (open question, PLAN section 6).
- The full pet species/behaviour system (DELVE-0011); this arc only made a companion
  consultable.

## Design notes / links

`CLAUDE.md` rule 4 (REPELLED is not death; the sitting is the unit of stakes) and the settled
wrong-answer model (4ce7fc9). The penalty arithmetic is why the published numbers make REPELLED
reachable and HP:0 the rarer path.

## Acceptance / verification

- Tests assert HP drops once per failed sitting and not per wrong answer.
- A run that exhausts attempts asserts REPELLED with all earned doors still open.
- A respawn test confirms re-entry at the chapter entrance with progress intact.
