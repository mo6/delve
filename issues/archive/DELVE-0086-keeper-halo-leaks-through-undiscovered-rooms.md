---
id: DELVE-0086
title: A burned-out torch reveals every keeper's candle halo, including in rooms never visited
status: implemented
area: [engine, session]
type: bug
epic:
effort: low
milestone:
version: 1.34.2
version_span:
created: 2026-07-31
updated: 2026-08-02
accepted_by: George Moses
accepted_at: 2026-08-02
commits: [01ba4b2]
related: [DELVE-0065, DELVE-0062]
supersedes: []
docs: []
changelog: "1.34.2"
reason:
---

# A burned-out torch reveals every keeper's candle halo, including in rooms never visited

## Summary

The moment a learner's torch burns out, every keeper on the current chapter appears on the map,
each with its one-tile halo, even in rooms the learner has never entered or seen any part of.
Going dark should make navigation harder, not hand over the floor layout by lighting up every
keeper's post regardless of distance or discovery.

## Motivation / problem

DELVE-0065 added the keeper candle halo specifically so a torchless learner could still find who
to talk to *in a dark room they are already in*, and its own Non-goals section says explicitly:
"No halo around a keeper the player hasn't discovered the room of yet; this only changes what is
lit within the current chapter's already-generated geometry, not what map tiles the player has
ever seen." The implementation doesn't honour that: `RunState._lit_tiles`
(`delve/session/run.py:2047`) calls `vision.keeper_halo(self.chapter, (g.keeper.pos for g in
self.gates.values()))`, unconditionally over *every* gate in the chapter, with no filter for
whether the learner has been anywhere near that keeper's room. So a torchless learner standing in
room 1 sees the keeper (and its halo) in room 6 pop into view too, spoiling both "a keeper is
there" and roughly "where that room is", which is exactly what DELVE-0065 said this change must
not do.

## MUST / MUST NOT

1. MUST NOT light a keeper's halo (`vision.keeper_halo`) for a keeper whose room the learner has
   not yet visited (`room.id not in self.cur.visited_rooms`, the same set `_maybe_enter_room`
   already maintains), even while torchless.
2. MUST still light a keeper's halo, exactly as today, once the learner has visited that keeper's
   room, whether or not the learner currently stands in it. (Whether "visited" or "currently
   present" is the right scope beyond that is a design question worth confirming; see Design
   notes.)
3. MUST NOT change behaviour for a learner carrying a working torch: a lit room already reveals
   everything, unaffected by this fix.
4. MUST NOT change what is folded into `discovered`: a halo tile is exactly as persistent (or not)
   after the fix as it was before; this is a filter on which keepers contribute a halo, not a
   change to persistence.

## Non-goals

- Not changing the halo's shape (still the same one-tile neighbourhood, DELVE-0065) or the torch
  burn-down mechanic (DELVE-0062).
- Not adding any new vision concept; the fix should reuse whatever the engine already has for
  "has the learner discovered this room" rather than introducing a second notion of visitedness.

## Design notes / links

- `delve/engine/vision.py:keeper_halo` is pure and takes whatever `keeper_positions` it's handed;
  the bug is entirely in the caller's filtering (or lack of it), not in `vision.py` itself.
- `delve/session/run.py:2047` `_lit_tiles` is the call site to fix, and `delve/session/run.py:2073`
  `_maybe_enter_room`'s `self.cur.visited_rooms` already tracks exactly the "has the learner been
  in this room" fact the fix needs; `vision.room_at` can map a keeper's `Point` back to its `Room`
  to check membership.
- Settled on accept (2026-08-02): once a room has been visited, that keeper's halo stays visible from anywhere on the floor while torchless; it does not also require the learner to currently stand in that room. Never-visited rooms stay dark.

## Acceptance / verification

- A new vision/session test: a torchless learner in room A, with a keeper in never-visited room B;
  assert the keeper's tile and halo are absent from the current frame's lit set and from
  `discovered`.
- A regression test confirming DELVE-0065's original behaviour still holds: a torchless learner
  elsewhere in a room they *have* visited still sees that room's keeper and halo.
- A regression test confirming a lit (torch-working) room's full reveal is unaffected.
- `./run-tests.sh` green.

## Peer review

- Auto (implementing agent), 2026-08-02: `_lit_tiles` filters `keeper_halo` to keepers whose room is in `visited_rooms`; `vision.py` untouched; four new torch tests cover never-visited skip, elsewhere-in-visited-room, visited-not-presence, and lit-torch unchanged. `./run-tests.sh` green (672).
- George Moses (maintainer), 2026-08-02: peer-reviewed; implementation accepted.
