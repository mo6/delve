---
id: DELVE-0065
title: A keeper's own candle lights their immediate surroundings regardless of the player's torch
status: implemented
area: [engine, session]
type: feature
epic:
effort: medium
milestone:
version: 1.26.7
version_span:
created: 2026-07-31
updated: 2026-07-31
accepted_by: George Moses
accepted_at: 2026-07-31
commits: [d53f1f4]
related: [DELVE-0062]
supersedes: []
docs: []
changelog: "1.26.7"
reason:
---

# A keeper's own candle lights their immediate surroundings regardless of the player's torch

## Summary

Every keeper is assumed to be holding a lit candle at all times, so their own tile and its
immediate neighbourhood are always visible to the learner, whether or not the learner is
carrying a working torch. Today, a torchless learner (DELVE-0062) sees only the immediate
neighbourhood around their own position; a keeper standing elsewhere in a dark room is
invisible until the learner has stumbled right up to them.

## Motivation / problem

DELVE-0062 made losing the torch a real cost: without one, `lit_tiles` never reveals a whole
room, only the player's own immediate radius, the same reveal a corridor already gets. That is
the right stakes for exploring a room, but it also makes a keeper unreachable to *see* in a dark
room bigger than one step across, since nothing about the keeper's own tile is currently
special-cased. A keeper is dungeon furniture that exists to be found and talked to; a candle at
their own post is the natural, in-fiction fix, and removes an accidental "wander blind until you
bump into someone" failure mode that has nothing to do with the torch mechanic's intended
stakes (running low on turns/light for exploring, not losing track of who to talk to).

## Stories

### As a learner, I want a keeper's own position to always be lit, so that I can still find who to talk to even if my torch has burned out.

- Given the learner has no working torch (`has_light` is False) and a keeper stands elsewhere in
  the same room, out of the learner's immediate one-tile radius,
  when vision is computed for the current frame,
  then the keeper's own tile is included as lit, regardless of the player's torch state.
- Given the same torchless state,
  when vision is computed,
  then the tiles immediately around the keeper (the same one-tile radius the player's own
  position already gets) are also lit, not just the keeper's exact tile.
- Given the learner does have a working torch,
  when in a room with a keeper,
  then behaviour is unchanged: the whole room is already lit as today, and the keeper's halo adds
  nothing new to check for regressions.

### As a maintainer, I want the keeper's halo to behave like the existing torchless reveal, so that it doesn't quietly become a second, differently-behaved light source.

- Given a torchless learner standing outside a keeper's halo,
  when the frame is rendered,
  then the halo tiles are visible this frame but are not added to `discovered` (they darken again
  once out of range), the same non-persistence rule DELVE-0062 already applies to the player's
  own torchless radius.
- Given an ungated room (no keeper),
  when torchless,
  then no halo appears; behaviour there is exactly as DELVE-0062 left it.

## Non-goals

- No change to the ambient backstory prompt's `has_light` wording (`session/backstory.py`); that
  flag describes the player's own torch state for the generated prose and is untouched here.
- No change to `TORCH_DURATION_STEPS` or the burn-down mechanic itself.
- No halo around a keeper the player hasn't discovered the room of yet; this only changes what is
  lit *within* the current chapter's already-generated geometry, not what map tiles the player has
  ever seen.

## Design notes / links

- The likely seam is `engine/vision.py:lit_tiles`, which already branches on `lit: bool` for the
  player's own radius; the keeper halo is a second, unconditional union of tiles, sourced from
  `Gate.keeper.pos` for every gate in the current chapter (or just the current room, whichever
  keeps the change smallest; `session/run.py:_observe` is where `lit_tiles` is actually called
  and has access to `self.gates`).
- CLAUDE.md rule 1: `engine` never imports `content`/`assess`/`session`; if the halo needs gate
  positions, either pass them in as plain `Point`s from `session` (preferred) or compute the union
  in `session/run.py:_observe` itself rather than reaching into `session` from `engine`.

## Acceptance / verification

- A new vision test asserting a keeper's tile and its immediate neighbours are lit when
  `has_light` is False and the player is elsewhere in the room.
- A new vision test asserting the halo does not persist into `discovered` once the player (and
  the halo) move away, mirroring the existing torchless non-persistence test for the player's own
  radius (DELVE-0062).
- A regression check that a torch-lit room's full-room reveal is unchanged.
- `./run-tests.sh` passes.
