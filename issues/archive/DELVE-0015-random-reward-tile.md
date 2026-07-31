---
id: DELVE-0015
title: Reward coins land on a random room tile, not the far corner
status: implemented
area: [session]
type: story
epic: DELVE-0010
milestone:
version: 1.9.2
version_span:
created: 2026-07-25
updated: 2026-07-25
commits: [4c7263a]
related: []
supersedes: []
docs: [docs/OBJECTS.md]
changelog:
---

# Reward coins land on a random room tile, not the far corner

## Summary

When a keeper pays the on-pass money reward, the coins currently always appear on the interior
tile farthest from the exit, so they land in the same corner of every room. Change the drop to a
random walkable tile inside the keeper's room instead, so the reward feels scattered rather than
predictably filed in the back.

## Motivation / problem

`RunState._reward_tile` picks the interior tile with the greatest Manhattan distance from the
door. That was chosen so the coins are a detour and a roaming pet could reach them first, but the
side effect is that every reward lands in the same predictable spot, which reads as mechanical and
gives away the room's geometry. A random location keeps the detour and the pet-race property while
removing the tell.

## Stories

### As a learner, I want the reward coins scattered, so that a room does not always drop them in the same corner and give away its shape.

- Given a scored room the learner has just passed,
  when the keeper pays the reward,
  then the coins land on a walkable floor tile chosen at random from that room's interior, not the
  tile farthest from the exit.
- Given the chosen tile is occupied by a keeper or by the player,
  when the tile is picked,
  then that tile is excluded and another eligible interior tile is used.
- Given a room too tight to hold an eligible interior tile, or a bulky item already sitting on the
  chosen tile,
  when the reward is paid,
  then it falls back to the door tile, or is skipped rather than lost (unchanged from DELVE-0010).
- Given the unscored tutorial floor,
  when the learner passes a keeper,
  then no reward is paid.
- Given any scored room,
  when the reward is paid,
  then everything but the tile choice is unchanged: paid once (`Gate.rewarded`), scaled by the
  passing score, and `MONEY` only.

### As a maintainer, I want the random drop to be deterministic, so that a run stays regenerable tile-for-tile.

- Given the same run rebuilt from its identity `(seed, size, pack)`,
  when the reward is paid again,
  then the coins land on the identical tile (see CLAUDE.md "Layout is locked at run start").
- Given a run resumed from its snapshot,
  when the reward is paid,
  then it lands on the same tile as the original run.
- Given the random draw,
  when the tile is chosen,
  then it uses a dedicated RNG stream seeded from the run seed and something stable per reward (the
  room index or the gate), and never draws from `self.rng`, which shuffles exam options.

## Non-goals

- Changing the reward amount, the score scaling, or the pay-once rule.
- Changing where scattered floor coins or pack-authored objects are placed at generation time.
- Any change to the pet's roam or retrieve behaviour.

## Design notes / links

The reward is session policy (`RunState._pay_reward` / `_reward_tile`), not a gate mechanic;
`gate.py` stays the pure training seam (CLAUDE.md, the five rules). The "separate RNG streams"
gotcha is the binding constraint: existing dedicated streams are seeded as `Rng(seed * 100 + …)`
(`pet_rng`, `flavour_rng`, the placement scatter `Rng(seed * 100 + 600 + i)`), and this draw needs
its own offset in the same family so it never borrows `self.rng`. Because the reward is paid at
pass time rather than at generation, the seed must be derived from a value that is stable across a
resume (the room index or the gate), not from turn-order state, or the determinism story fails.
Design essay: `docs/OBJECTS.md`.

## Acceptance / verification

- The DELVE-0010 reward test is updated: it asserts a single `MONEY` pile on a walkable interior
  tile of the keeper's room (not the farthest tile), still scaled by score, and still none on the
  tutorial floor. Covers the learner story.
- A determinism test builds the same run twice from one `(seed, size, pack)` and asserts the
  reward lands on the identical tile both times; a resume-from-snapshot path lands on the same
  tile as the original run. Covers the maintainer story.
- `./run-tests.sh` passes (pytest, ruff, screen and issues-index checks).
