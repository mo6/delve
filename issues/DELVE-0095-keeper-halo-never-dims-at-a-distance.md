---
id: DELVE-0095
title: A visited room's keeper halo never dims, so going dark shows it brighter than a lit torch would
status: proposed
area: [engine, session]
type: bug
epic:
effort: medium
milestone:
version:
version_span:
created: 2026-08-02
updated: 2026-08-02
accepted_by:
accepted_at:
commits: []
related: [DELVE-0086, DELVE-0065]
supersedes: []
docs: []
changelog:
reason:
---

# A visited room's keeper halo never dims, so going dark shows it brighter than a lit torch would

## Summary

Once a room has been visited, its keeper's candle halo (DELVE-0065, extended floor-wide by
DELVE-0086) renders at full brightness on every frame, no matter how far the learner has since
wandered. A learner carrying a working torch, by contrast, sees that same remembered room dimmed
the moment they leave it (DELVE-0062's `discovered`-but-not-currently-`lit` rendering). The net
effect: a torchless learner sees a remembered keeper rendered *brighter* than a torch-carrying
learner does. Going dark should never look better than having light.

## Motivation / problem

`RunState._cell` (`delve/session/run.py:2572`) decides dimness with `dim = p not in lit`. For a
lit-torch learner, once they leave a room, that room's tiles remain only in `self.discovered`, not
in the current frame's `lit` set, so they render dimmed (the ordinary "remembered but not currently
seen" treatment). But `RunState._lit_tiles` (`delve/session/run.py:2136-2141`) recomputes every
*visited* room's keeper halo into `lit_now` unconditionally, every frame, regardless of the
learner's current distance from that room. So a keeper in a room the learner left long ago is
always in `lit`, never dimmed: full brightness forever, torchless.

This was surfaced during peer review of DELVE-0086 (which widened the halo's range from "same
room" to "anywhere on the floor, once visited"): the wider range made a pre-existing DELVE-0065
inconsistency visible for the first time, because it now puts a remembered-but-distant keeper
directly in visual contrast with the lit-torch dimming of the same room. DELVE-0065's own tests
never exercised this, since without DELVE-0086 the halo only showed while already in a dark room,
with no lit-torch counterpart to compare against in the same moment.

## Stories

### As a learner, I want a torchless view to never look brighter than a lit one, so that losing my torch always reads as strictly worse, never an upgrade.

- Given a learner has visited a room and left it, with a working torch,
  when they view the map from elsewhere on the floor,
  then that room's keeper renders dimmed, same as the rest of the remembered room.
- Given a learner has visited a room and left it, now torchless,
  when they view the map from elsewhere on the floor,
  then that room's keeper renders dimmed too, not brighter than the lit-torch case above.
- Given a torchless learner is still inside (or immediately beside) a room whose keeper's halo
  covers their position,
  when they view the map,
  then the keeper and halo render at full brightness, exactly as DELVE-0065 intended (this story
  is unaffected; only the "elsewhere, remembered" case changes).

## Non-goals

- Not changing whether a keeper's halo is computed at all for a visited room (DELVE-0086's
  visited-rooms filter stays as is); this is purely about the brightness/dim flag on tiles that
  are already correctly included.
- Not folding the halo into `discovered` (DELVE-0086's MUST 4 still holds): a halo tile's
  persistence is unchanged, only which frames render it dim vs. bright.
- Not touching DELVE-0062's torch burn-down mechanic or DELVE-0065's halo shape.

## Design notes / links

- `delve/session/run.py:2564` `_cell`: `dim = p not in lit` is the rendering rule; a keeper tile's
  dimness today depends only on `lit`, which `_lit_tiles` currently always includes it in once the
  room is visited.
- `delve/session/run.py:2127` `_lit_tiles` would need to distinguish "the learner is close enough
  that this halo is a real, current reveal" from "this halo is remembered from a past visit,
  render like any other discovered-but-not-lit tile." The simplest version: keep a visited room's
  keeper in `lit` (bright) only while the learner is within that same room or its immediate
  neighbourhood (i.e., roughly where DELVE-0065 originally scoped it), and otherwise let the
  keeper tile fall back to ordinary `discovered` dimming, which requires the keeper tile to have
  been folded into `discovered` at least once during a visit, since a tile that was never `lit`
  while lit-torch can't already be dimmed-remembered.
- That last point is the crux open question: today a keeper's own tile is never added to
  `discovered` while torchless (DELVE-0086's MUST 4), and while lit-torch it *would* already be
  folded into `discovered` as part of the room reveal (DELVE-0062). So the fix may already fall out
  for a room the learner visited *with* a working torch; the harder case is a room visited
  *while already torchless* (DELVE-0065's original scenario), whose keeper tile has never been in
  `discovered` and so has nothing to dim to: it would need to disappear entirely once the learner
  leaves, or `discovered` would need to gain the keeper tile the first time its halo is seen.
  Settle this before implementing.

## Acceptance / verification

- A new session test: a learner with a working torch visits a room with a keeper, leaves, and
  views the map from elsewhere on the floor; assert the keeper's tile renders dimmed, matching the
  rest of that remembered room.
- A new session test: a learner goes torchless, visits a room with a keeper (satisfying
  DELVE-0086's visited-rooms filter), leaves, and views the map from elsewhere on the floor;
  assert the keeper's tile renders the same way (dimmed, or absent, whichever the settled design
  note above lands on) as the lit-torch case, not brighter.
- A regression test confirming DELVE-0065's original "elsewhere in the same room, torchless" case
  still renders the keeper and halo at full brightness (unaffected).
- `./run-tests.sh` green.
