---
id: DELVE-0010
title: Objects, money, on-pass reward
status: implemented
area: [engine, session, content, ui]
type: epic
milestone:
version: 1.0.1
version_span: 1.0.1-1.3.4
created: 2026-07-19
updated: 2026-07-20
commits: [9bceb2a, 3afcc4a, ddd36dc]
related: [DELVE-0011]
supersedes: []
docs: [docs/OBJECTS.md]
changelog: "1.3.0"
---

# Objects, money, on-pass reward

## Summary

Add objects to the dungeon: an item model with counted stacks, money as the one built-in kind,
pickup and drop, an on-pass money reward, and pack-authored objects placed in rooms. Delivered
across `1.0.1` (item model, money), `1.1.0` (the reward), and `1.3.0` (pack-authored objects).

## Motivation / problem

A NetHack floor has things on it. Objects give a room texture, a reward gives passing a
tangible payoff, and pack-authored objects let an author seat a topic-relevant prop in a lesson.

## Requirements

1. The engine MUST provide an `ItemDef` plus a counted `Stack`, with money the one built-in
   kind.
2. The learner MUST be able to pick up and drop objects; the object keys (`d`/`,`/`i`) MUST NOT
   clash with the map or answer keys.
3. Passing a scored room MUST pay a money reward once (`Gate.rewarded`), scaled by the passing
   score, dropped on the interior tile farthest from the exit.
4. The on-pass reward MUST be session policy (`RunState._pay_reward`), not a gate mechanic;
   `gate.py` MUST stay the pure training seam.
5. The unscored tutorial floor MUST NOT pay a reward.
6. A pack MUST be able to author objects that are placed in its rooms.
7. Any test inspecting floor piles for a reward or scattered coins MUST filter to `MONEY`; a
   placed object is not money.
8. Cosmetic placement MUST use its own RNG stream, never `self.rng` (which shuffles exams).

## Non-goals

- Object use beyond pickup, drop, and count-aware flavour.
- The companion pet's carry-and-retrieve behaviour (DELVE-0011).

## Design notes / links

The item model, the reward-is-session-policy rule, the "a placed object is not money" gotcha,
and the separate RNG streams are all in `CLAUDE.md`; the design is `docs/OBJECTS.md`. Digit
answer keys were chosen so they never collide with the object keys (OBJECTS.md 1.1.0).

## Acceptance / verification

- Reward test asserts a single MONEY pile on the farthest interior tile, scaled by score, and
  none on the tutorial floor.
- Pickup/drop tests over the item model and counted stacks pass.
- `delve validate` accepts pack-authored objects across all four shipped packs.
