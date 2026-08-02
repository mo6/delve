---
id: DELVE-0088
title: The pet chases a keeper's dropped reward coin even after you've already left for the next room
status: proposed
area: [engine]
type: bug
epic:
effort: medium
milestone:
version:
version_span:
created: 2026-07-31
updated: 2026-07-31
accepted_by:
accepted_at:
commits: []
related: []
supersedes: []
docs: [docs/PETS.md]
changelog:
reason:
---

# The pet chases a keeper's dropped reward coin even after you've already left for the next room

## Summary

When a keeper pays out the on-pass reward (a coin pile dropped on a random tile of the room,
DELVE-0015) and the learner walks straight on into the next room without waiting for the pet, the
pet ignores that the learner has moved on: it keeps going for the coins first, and only starts
following the learner again once it has actually picked the reward up. The pet is supposed to drop
whatever it's doing and follow you through a door "before all else" (the existing cross-room
follow behaviour, shipped well before this issue and reconfirmed by `engine/pet.py:step`'s own
`following` branch); this case defeats it.

## Motivation / problem

The intended, already-shipped rule is that the moment the learner is in a different room than the
pet, the pet abandons whatever it was doing and heads for the door after them (`step`'s `following`
check, computed from `_room_of`, `delve/engine/pet.py`). A reward coin appearing right as the
learner is about to leave the room is exactly the case that should exercise this: the pet should
give up on the coin the instant the learner crosses into the next room, not finish the fetch first.
That it doesn't means either the room-crossing detection doesn't fire promptly in this situation, or
something about a freshly-dropped reward pile overrides it; either way the observable result is the
pet visibly lagging behind on an errand the learner already walked away from, which reads as the pet
not caring where you went, the opposite of PETS.md's whole "a companion that behaves like it's
following you" premise. Notably, there is no existing automated test that exercises "reward drops in
the room the learner is about to leave", so this specific interaction isn't guarded today.

## MUST / MUST NOT

1. MUST have the pet abandon a reward-coin fetch (or any in-room item fetch) the moment the learner
   has moved to a different room than the pet currently occupies, exactly like the general
   cross-room follow rule already does for other in-progress errands.
2. MUST have the pet, once it has given up the fetch to follow, resume heading for the reward coins
   only after it has caught back up to the learner (i.e. the existing "follow first, fetch after"
   priority order, not fetch-then-follow).
3. MUST NOT change what happens when the learner stays in the same room as the reward drop: the pet
   still goes and fetches it exactly as today.
4. MUST NOT change the reward mechanic itself (drop tile choice, DELVE-0015; reward amount); this is
   about the pet's movement priority only.

## Non-goals

- Not changing the general "dog fetches, cat sweeps" identity behaviours (PETS.md), only the
  priority between "keep fetching" and "the learner just left the room".
- Not adding any new pet species behaviour or leash/interest tuning.

## Design notes / links

- `delve/engine/pet.py:step` and its `following = bool(rooms) and _room_of(rooms, pet.pos) !=
  _room_of(rooms, player_pos)` check is where this should already be handled; a likely candidate
  worth checking first is `_room_of` returning `None` for a tile in a corridor or doorway (neither
  the pet's nor the learner's position is inside any `Room.contains`), which makes `following`
  compare `None != None` as `False` and treat "both currently in a corridor, actually rooms apart"
  as "same room, keep fetching". A freshly-dropped reward pile sitting on the pet's route while the
  learner is mid-corridor is exactly this shape.
- No existing test in `tests/test_pets.py` covers a reward-style drop with the learner leaving the
  room before the pet reaches it; the closest, `test_a_cat_chases_money_from_several_tiles_away`,
  keeps the learner in the room throughout.
- `RunState._pay_reward` (`delve/session/run.py`) is where the reward is actually dropped; useful
  for constructing the repro in a session-level test rather than only a bare `engine.pet.step` unit
  test, since the room-crossing case needs the chapter's real room geometry.

## Acceptance / verification

- A new `engine/pet.py` test: place a reward coin pile in room A, the pet in room A, the learner
  about to step from room A into room B; step the pet once the learner has moved to room B, and
  assert the pet's next move heads toward the learner (heels), not toward the coins.
- A companion regression test confirming the pet still fetches a same-room drop when the learner
  stays put (today's behaviour, unchanged).
- A session-level test around `_pay_reward`/`Descend` covering the concrete reported scenario: pass
  a gated room's questions, then immediately move to the next room before the pet reaches the
  reward, and assert the pet ends up following rather than delivering first.
- `./run-tests.sh` green.
