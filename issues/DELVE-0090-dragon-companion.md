---
id: DELVE-0090
title: A third companion species, the Dragon, that hunts torches and breathes fire once fed
status: proposed
area: [engine, session, ui]
type: feature
epic: DELVE-0011
effort: high
milestone:
version:
version_span:
created: 2026-07-31
updated: 2026-07-31
accepted_by:
accepted_at:
commits: []
related: [DELVE-0016, DELVE-0062, DELVE-0065, DELVE-0067]
supersedes: []
docs: [docs/PETS.md]
changelog:
reason:
---

# A third companion species, the Dragon, that hunts torches and breathes fire once fed

## Summary

Add a Dragon as a third companion species alongside the existing cat and dog (PETS.md,
`engine/pet.py`'s `SPECIES` registry). Unlike a cat or dog, a Dragon does not care about the
learner's proximity at first: it flies around its current room hunting for torches. Eating a
torch (from the floor, including one the learner deliberately drops for it) gives it a
fire-breathing ability and changes its behaviour to stay near the learner. From then on, each step
it has a small chance to breathe fire down an orthogonal line whose reach grows the longer it's
been since its last breath; hitting the learner costs 1 HP, and hitting a keeper sends that keeper
fleeing through their own door into the next room.

## Motivation / problem

The companion system (DELVE-0011 and its many follow-ups) has so far only ever added benign
companions: a cat and a dog that fetch or find coins and never harm anyone (`Pet`'s own docstring:
"the dungeon never harms it"). A Dragon inverts that: it is the first companion that is dangerous
to be around, consumes a resource the learner also depends on (the torch), and can hurt both the
learner and a keeper. That's a deliberately different kind of companion, chosen for this pack of
requirements as a distinct, higher-risk pet a learner can opt into.

## Stories

### As a learner, I want to choose a Dragon as my companion, so that I can play with this riskier, more chaotic pet.

- Given the pet-choice prompt at the start of a run,
  when the learner presses the Dragon's key,
  then their companion is a Dragon (`species="dragon"`), rendered as `D` on the map.
- Given the pet-choice prompt in English,
  when the learner presses `D` (uppercase), then Dragon is chosen; when they press `d` (lowercase),
  then Dog is chosen, same as today; when they press `c`, `C`, or `f`, then Cat is chosen (`f`
  added as a new accepted key, matching the cat's own map glyph).
- Given the pet-choice prompt in Dutch,
  when the learner presses `d` or `D`, then Dragon is chosen (Dutch "draak" also starts with `d`,
  so it keeps the same letter as English); when they press `h` or `H`, then Dog is chosen (as
  today, "hond"); when they press `k` or `K`, then Cat is chosen (as today, "kat").
- Given either locale,
  when the hint line for the pet prompt is shown,
  then it lists all four choices (cat/dog/dragon/none) with the actual key that works for each,
  the same self-describing pattern `pick_pet_hint` already uses.

### As a learner, I want an untamed Dragon to hunt for torches on its own, so that it reads as a wild, independent creature rather than a leashed pet.

- Given a Dragon that has never eaten a torch,
  when it takes its step,
  then it seeks the nearest torch stack on the floor of its *current room only* (it never crosses
  into another room chasing one, and never heels toward the learner the way a cat or dog does).
- Given no torch is present anywhere in its current room,
  when it takes its step,
  then it wanders within the room (mirroring the existing empty-pawed `p_wander` idea), never
  leaving it.
- Given the learner deliberately drops a torch (lit or spare) in the Dragon's room,
  when the Dragon reaches that tile,
  then it eats it exactly as it would a torch it found unprompted; the learner's own drop is a
  valid, intended way to feed it.

### As a learner, I want the Dragon to actually consume the torch's remaining light, so that dropping mine for it is a real trade-off, not a free trick.

- Given a torch stack with `charge` steps remaining (a fresh floor torch, or one the learner
  dropped mid-burn),
  when the Dragon eats it,
  then that many steps become the Dragon's own remaining torch charge; a fresh, never-lit torch
  transfers `TORCH_DURATION_STEPS` (DELVE-0067's existing charge-transfer rule, reused rather than
  reinvented).
- Given the Dragon is carrying an eaten torch,
  when the learner opens their own backpack/inventory,
  then that torch does not appear there or on the floor; it is gone from anywhere the learner can
  see or interact with it directly, held only by the Dragon.
- Given the Dragon's held torch,
  when the Dragon takes a step (mirroring `RunState._tick_torch`'s one-burn-per-move rule for the
  learner's own torch),
  then its remaining charge decrements by one, reaching 0 when burned out.

### As a learner, I want the Dragon to gain and keep fire-breathing once fed, and to stop hunting and start sticking near me, so that feeding it visibly changes how it behaves.

- Given a Dragon that has just eaten its first torch,
  when its behaviour is next evaluated,
  then it gains its fire-breathing ability and switches from "hunt the room for torches" to
  "stay in the learner's neighbourhood" (the existing leash/heel idea cat and dog already use is
  the right shape to reuse here, tuned to the Dragon's own numbers).
- Given the ability, once gained,
  when the Dragon's held torch later burns out,
  then it is confirmed (not assumed) whether the ability lapses until the Dragon eats another
  torch, or persists permanently once earned; see the open question in Design notes, since the
  brief given for this issue doesn't settle it and getting it wrong changes the Dragon's whole
  difficulty curve.

### As a learner, I want a fire-breathing Dragon to occasionally torch a line of tiles, so that it's a real, unpredictable hazard rather than only a torch thief.

- Given a Dragon with the ability, on each of its own steps,
  when nothing else has just happened, then it has a 10% chance to breathe fire.
- Given it breathes,
  when the direction is chosen,
  then it picks one of the four orthogonal directions and breathes a line of tiles starting
  adjacent to it in that direction, using a dedicated RNG stream (never `self.rng`, the exam
  shuffle stream, and never the pet movement stream either, so exam order and pet movement replay
  stay untouched, mirroring the existing `pet_rng`/`flavour_rng` separation, CLAUDE.md's own
  gotcha).
- Given the reach of that breath,
  when it is computed, then it is `max(1, steps_since_last_breath // 5)` tiles long, so a Dragon
  that hasn't breathed in 10 of its own steps reaches 2 tiles, matching the worked example in the
  brief exactly.
- Given the breath's line of tiles,
  when it reaches a wall or the room/corridor boundary,
  then it stops there rather than passing through (confirm the exact stopping rule; see Design
  notes).

### As a learner, I want the Dragon's fire to actually hurt whoever it hits, so that the hazard has teeth.

- Given the learner's own tile is anywhere along a fire breath's line,
  when the breath resolves,
  then the learner loses exactly 1 HP (and, if that brings HP to 0, the existing respawn rule
  applies unchanged: chapter entrance, full HP, every earned door still open, CLAUDE.md rule 4 -
  this is not a new death path, it's the same HP pool).
- Given a keeper's tile is anywhere along a fire breath's line,
  when the breath resolves,
  then that keeper immediately unseals and opens their own room's door and flees through it into
  an adjacent room, then keeps moving away from the Dragon as far as it can for the rest of the
  run (this effect never wears off, per the brief); see the prominent open design question below,
  since this crosses two of the project's settled rules and needs explicit sign-off before it's
  built as described.

## Non-goals

- Not adding a fourth companion or changing cat/dog behaviour, beyond the key-selection changes
  above (adding `f` for cat, and the `d`/`D` case split with dog).
- Not adding any new pack-authoring surface; the Dragon is an engine/session mechanic, not
  something a room author configures.
- Not deciding here whether a fled keeper's room can still be *entered* and passed normally
  afterward, or what "another room" means if the chapter's layout gives the keeper nowhere sensible
  to flee to (a corner room, a chapter with only one room); these need answering during design, not
  guessed at issue-writing time.

## Design notes / links: read before implementing, several open questions

- **The most consequential open question: a keeper opening their own door on being hit conflicts
  with two settled project rules.** CLAUDE.md rule 2 ("Sealed doors are structural. Never add path
  validation... there is therefore no path around a lesson") and the fact that `gate.py` is
  described as "the only module touching both the dungeon and the training" both assume a door
  opens only by passing its exam (`Gate._unlock`, called from the pass path in
  `delve/gate.py:162`). A keeper unsealing their own door because a Dragon scorched them is a
  second, exam-unrelated way for a door to open, letting a learner potentially walk into a room
  they haven't earned. CLAUDE.md is explicit about this exact situation: "If this rule needs
  breaking, the design is wrong; stop and say so rather than routing around it." Before building
  the keeper-flee story, confirm with the maintainer whether: (a) the fled-from room's door stays
  open permanently (the learner can now walk through unearned), (b) it reseals once the keeper
  keeps moving/reaches the next room (the opening is momentary, cosmetic to the flee animation, not
  a lasting shortcut), or (c) the keeper's own gate is exempted from being a "real" gate in some
  other way. This is not a detail to default silently.
- **Keepers have never moved.** Every existing keeper is static furniture (`Keeper` in
  `delve/engine/entities.py` has no step function, unlike `Pet`). Making a hit keeper flee is a new
  kind of actor movement with its own pathfinding (likely reusing `_first_step`'s BFS shape from
  `engine/pet.py`, "away from the Dragon" being the inverse goal-seeking problem to "toward a
  target"). Where this logic lives (a new `engine/keeper.py`, or inside `gate.py` since it already
  straddles dungeon+training) is an implementation decision worth getting right the first time.
- `engine/pet.py`'s `SPECIES` registry (`interest`/`leash`/`p_wander` per species) is the natural
  extension point for the Dragon's own numbers (post-ability leash distance, hunt radius while
  unfed, wander chance), per the module's own stated design ("a parrot or a bunny is a new entry
  plus its behaviour, not a rewrite"). The pre-ability "hunt the whole room, not just nearby tiles"
  behaviour and the post-ability "breathe fire" behaviour don't fit the existing `interest`-radius
  model cleanly, so `Species`/`step` likely need a per-species behaviour hook rather than only new
  numeric knobs.
- `Pet` (`delve/engine/entities.py`) needs a place for the Dragon's own torch charge (a new field,
  parallel to `Player.torch_charge`) and a "has the ability" flag (or infer it from "has ever eaten
  a torch", if the ability is meant to persist past a burnout, per the open question above) and a
  "steps since last breath" counter for the reach formula.
- The charge-transfer rule to reuse is `RunState._pickup` (`delve/session/run.py:1240`, DELVE-0067):
  `took.charge if took.charge is not None else TORCH_DURATION_STEPS`. The "eaten torch never shows
  in inventory" rule means the Dragon's eat path removes the stack from `items` the same way
  `_grab_underfoot` already does for a dog's fetch (`engine/pet.py`), just without ever setting it
  back down.
- A dedicated RNG stream for fire-breath direction/timing is required by CLAUDE.md's own gotcha
  section (`self.rng` is the exam-shuffle stream only); follow the existing `pet_rng`/
  `flavour_rng`/reward-tile-draw pattern of a separately seeded `Rng`, not a shared one.
- `delve/ui/app.py:163` `_ask_pet` and `pet_key_cat`/`pet_key_dog`/`pet_key_none` in both
  `en.toml`/`nl.toml` are the key-selection seam; a new `pet_key_dragon` string plus the `f`/case-
  split changes to the existing accept sets. `ui.pick_pet_hint` needs a fourth bracketed choice.
- `docs/SCREENS.md` and `docs/PETS.md` will need updating (a new glyph `D`, a new section on the
  Dragon's behaviour) once the design is settled.

## Acceptance / verification

- Engine-level tests (alongside `tests/test_pets.py`) for: torch-hunting confined to the current
  room, charge transfer on eating (including a partially-burned dropped torch), the eaten torch's
  absence from `items`/inventory, the ability-gain transition and post-gain leash behaviour, the
  10%-chance/reach-formula fire breath (seeded, deterministic in a test), and the dedicated RNG
  stream never touching exam order.
- A session-level test for the player-HP-loss path (including the respawn boundary at HP 0) and,
  once the door-opening question above is answered, a test encoding whichever resolution was
  chosen for the fled keeper's own door.
- `./tools.sh screens --check` updated for the new glyph and any new pet-choice hint text.
- `./run-tests.sh` green, both locales (`pet_key_dragon`, `noun_dragon`, `default_dragon`, and the
  hint string added to both `en.toml` and `nl.toml`).
