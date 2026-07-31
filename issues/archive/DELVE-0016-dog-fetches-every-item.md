---
id: DELVE-0016
title: The dog fetches every item, one at a time, and delivers it to the learner
status: implemented
area: [engine, session]
type: story
epic: DELVE-0011
milestone:
version: 1.10.0
version_span:
created: 2026-07-25
updated: 2026-07-25
commits: [pre-reset]
related: []
supersedes: []
docs: [docs/PETS.md, docs/OBJECTS.md]
changelog:
---

# The dog fetches every item, one at a time, and delivers it to the learner

## Summary

Today the dog only chases and delivers `MONEY`; any other object a pack scatters on the floor it
walks straight past. Widen the dog so it fetches *every* kind of floor item, not just coins, and
makes fetching-and-delivering its first priority on every floor: whenever a reachable item exists,
the dog heads for it, picks it up, heels back to the learner, and hands it over before it does
anything else. It carries one stack at a time; it delivers what it holds, then goes back for the
next. **Delivery is a floor drop for both kinds** (decided with the reporter): the dog sets what it
carries down on its own tile beside the learner and walks off, so coins land as a `$` pile the
learner auto-collects by stepping over (the old direct bank was surprising, "it vanished the instant
it arrived") and a non-money item waits for `,`. Each is announced on the message line ("Rex trots
back and drops the smooth stone beside you"). Only the **dog** changes; the cat keeps its
sweep-and-hover behaviour.

## Motivation / problem

The companion (DELVE-0011) was written when `MONEY` was the only object kind. Objects (DELVE-0010) then
gave packs the ability to place other `ItemDef` stacks on the floor, but the pet's retrieval was
never widened: `engine/pet.py`'s `seek_coins` and its grab-underfoot both filter to `MONEY.id`, so
the dog ignores every non-coin item. A learner who has taken a dog reasonably expects it to fetch a
dropped object the same way it fetches coins. Making retrieval the dog's dominant drive, across all
item kinds and every chapter, matches how a fetch-happy dog reads and removes the "why did it walk
past that" surprise.

## Stories

### As a learner, I want my dog to fetch any item it can reach, so that objects come to me instead of my having to walk to each one.

- Given a walkable floor tile within the dog's interest range holds a non-money item stack,
  when the dog takes its step,
  then it moves along the shortest unblocked path toward that item, exactly as it already does for a
  `$` pile.
- Given the dog is standing on a tile that holds any item stack (money or not) and is not cooling
  down,
  when it steps,
  then it picks that stack up into what it carries and reports a pickup event.
- Given the dog is carrying an item and is adjacent to the learner,
  when it steps,
  then it hands the item over and reports a delivery event, going empty-pawed again.
- Given the dog has just delivered,
  when the fetch cooldown is active,
  then it leaves items alone and drifts, so it does not pounce straight back onto what it handed over
  (unchanged `FETCH_COOLDOWN` behaviour).

### As a learner, I want the dog to prioritise fetching over wandering and heeling, so that a reachable item is always its next move.

- Given a reachable item exists in range and the dog carries nothing,
  when it steps,
  then seeking that item is chosen ahead of milling and ahead of heeling on a loose leash.
- Given the learner has walked into a different room,
  when the dog steps,
  then following the learner through the door still takes precedence over starting a fresh fetch, so
  the dog never dawdles a room behind (unchanged from DELVE-0011).
- Given the dog is carrying an item,
  when it steps,
  then it heels toward the learner to deliver rather than chasing a second item; it carries one
  stack at a time.

### As a learner, I want a fetched item to arrive where it belongs, so that coins and objects each land in the right place.

- Given the dog delivers a `MONEY` stack,
  when the handover resolves,
  then the coins are **set down on the dog's tile beside the learner** as a `$` pile (a floor drop,
  decided with the reporter), not banked directly; the learner banks them by stepping over, through
  the ordinary auto-collect. The engine never touches `Player.gold`.
- Given the dog delivers a non-money stack,
  when the handover resolves,
  then that stack is set down on the same tile beside the learner (an adjacent floor tile), not
  banked as gold and not stowed silently into the pack; the learner picks it up with `,`.
- Given the dog sets any stack down beside the learner,
  when the handover resolves,
  then a status message announces it on the message line, naming what was dropped, for example "Rex
  trots back and drops the smooth stone beside you"; this is a localised string (en/nl), and the
  delivery still reports a delivery event.
- Given the dog delivers by setting the stack on its **own** tile (which it already stands on, so
  the tile is walkable by construction and beside the learner),
  when the drop resolves,
  then it folds into any pile already there (coins merge, an object joins), and the dog walks off on
  its fetch cooldown rather than pouncing straight back onto it.

### As a maintainer, I want the widened fetch to stay pure and deterministic, so that a run still regenerates tile-for-tile.

- Given the dog's step,
  when it chooses a target or picks an item up,
  then it draws only from the dedicated pet RNG (`pet_rng`), never `self.rng`, so exam-option
  shuffling and tile-for-tile regen are untouched (CLAUDE.md "RNG streams are separate").
- Given the same run rebuilt from its identity `(seed, size, pack)`, or resumed from its snapshot,
  when the dog fetches and delivers,
  then it makes the identical moves and the same item lands in the same place.
- Given the fetch mechanic,
  when it is implemented,
  then `engine/pet.py` stays pure of `content`, `assess`, `session`, and `ui` (rule 1); routing a
  delivered non-money item into the pack is the session's job, done from the delivery event, the same
  way crediting gold is today.

## Non-goals

- Changing the **cat**. It keeps sweeping money and hovering; this story widens only the dog.
- Any new UI for the pet, or a change to how the backpack (`i`) is drawn.
- Carrying more than one stack at a time, or fetching from beyond the existing interest range.
- Changing what packs may place on the floor, or the reward-drop and scatter placement (DELVE-0010,
  DELVE-0015).

## Design notes / links

The change is concentrated in `engine/pet.py`: `seek_coins` and the grab-underfoot both filter on
`MONEY.id` and must widen to any stack, while the delivery path sets the carried stack **down on the
floor** (money or object alike) instead of returning a coin total for the session to bank; the
session then only narrates the event, keeping `engine` clear of `Player.gold`.
The current `PetEvent` carries `kind` and an integer `coins`; a delivered object needs to name *what*
was handed over, so the event likely grows to carry the delivered stack (or its `ItemDef` id and
count) rather than only a coin total, both to place it and to fill the drop message. Keep the dog's
"carrying" state a single stack so "one item at a time" holds. The tile the item is set down on must
be chosen deterministically (a fixed scan order over the learner's neighbours), not from `self.rng`,
so a run regenerates tile-for-tile. The drop message is a new localised string in
`delve/strings/{en,nl}.toml`, handed to `ui` opaquely through the `Frame` like every other message
(rule 2). The separate-RNG-streams and rule-1 constraints are the binding ones (see CLAUDE.md
"Gotchas" and the five rules). Design essay: `docs/PETS.md`.

## Acceptance / verification

- A pet test scatters a non-money item in the dog's range and asserts the dog paths to it, picks it
  up (pickup event), heels to the learner, and delivers it (delivery event); the delivered stack
  ends up on a walkable tile beside the learner (not banked as gold), and the drop message fires.
  Covers the first and third learner stories.
- A priority test places both an item and open floor and asserts the dog seeks the item ahead of
  milling and heeling, and, when carrying, heels to deliver rather than chasing a second stack;
  following the learner into a new room still preempts a fresh fetch. Covers the second learner story.
- The DELVE-0011 money-delivery test is updated to the floor drop: a delivered `MONEY` stack lands as
  a `$` pile on the dog's tile beside the learner (`gave` event still fires), rather than banking
  directly; stepping over it banks it through the ordinary auto-collect.
- A determinism test builds the same run twice from one `(seed, size, pack)` and asserts identical
  dog moves and identical delivered-item placement; a resume-from-snapshot path matches the original
  run **through the fetch** (seek/heel/deliver draws no pet RNG, so it is exact even though the pet
  RNG is not snapshotted; only later idle milling diverges). Covers the maintainer story.
- `./run-tests.sh` passes (pytest, ruff, screen and issues-index checks).
