---
id: DELVE-0062
title: A torch that lights the room, runs out after a limited number of steps, and darkens ambient prose without one
status: implemented
area: [engine, session, ui, delve, docs]
type: feature
epic:
effort: high
milestone:
version: 1.25.0
version_span:
created: 2026-07-30
updated: 2026-07-30
accepted_by: George Moses
accepted_at: 2026-07-30
commits: [0956d13]
related: [DELVE-0060]
supersedes: []
docs: [docs/PLAN.md]
changelog: "1.25.0"
---

# A torch that lights the room, runs out after a limited number of steps, and darkens ambient prose without one

## Summary

Vision (`engine/vision.py:lit_tiles`) today always reveals the whole current room the instant the
learner stands in it, and every tile it has ever lit stays remembered (dimmed) forever
(`ChapterRun.discovered`). This introduces a torch: the learner starts with one, it lights the
current room exactly as vision already behaves, and it burns down over roughly 150 steps of actual
movement. Each chapter (pack floors only, not the tutorial) hides one spare torch in a random
room, so running out is a recoverable setback, not a dead end: the next spare in the backpack
lights automatically. Without a working torch, vision shrinks to the immediate few tiles around the
learner (the same radius a corridor already reveals one step at a time) and, critically, none of it
is remembered once the learner moves on: a torchless tile goes dark again the moment it is no
longer in that radius. A room already fully lit while a torch was burning stays lit forever, exactly
like today; only torchless exploration is temporary. Ambient prose (DELVE-0060) is told whether the
learner currently has working light and describes the room accordingly, darker and gloomier without
one.

## Motivation / problem

The dungeon's whole atmosphere (CLAUDE.md's own "no sunlight or happiness, only torchlight" framing
DELVE-0060's ambient prose already commits to) has had no mechanical stakes behind it: the room is
always lit, however the learner got there, so "torchlight" was purely descriptive colour with
nothing the learner could lose. A torch that can run out gives that atmosphere a real, resource-like
edge, and losing it entirely changes what the learner can see, not just what the ambient text says
about it, tying the mechanic to the same "no sunlight, only scarce torchlight" premise the ambient
prose has been describing since DELVE-0060.

## Stories

### As a learner, I want a torch that lights my room the way the game already lights it, so that carrying one changes nothing about how exploring normally feels.

- Given the learner is carrying a lit torch,
  when they stand in a room,
  then the whole room is lit exactly as every room is lit today, and a corridor still reveals one
  step at a time.
- Given a room the learner has fully lit while carrying a lit torch,
  when they leave it,
  then it stays remembered (dimmed), exactly like today; nothing about the torch mechanic changes
  a room already lit this way.

### As a learner without a working torch, I want to see only a little around myself, and forget it again once I move on, so that a run out of light is a real, felt loss.

- Given the learner has no lit torch (none ever carried yet run out, or all spares exhausted),
  when they stand anywhere,
  then only the immediate few tiles around them are lit (the same radius a corridor already uses),
  never the whole room, however large.
- Given a tile was lit this way (torchless) a moment ago,
  when the learner moves far enough that it is no longer in that immediate radius,
  then it goes dark again; unlike a torch-lit room, a torchless tile is never remembered.
- Given the learner picks up or re-lights a torch while standing in a room they are currently only
  torchlessly seeing a corner of,
  when the torch catches,
  then the whole room lights and, from that point on, is remembered like any torch-lit room.

### As a learner, I want to start with a torch and find a spare on every floor, so that running out is a setback, not a dead end.

- Given a fresh run,
  when it begins,
  then the learner already has one torch, lit, at full duration.
- Given any pack floor (not the tutorial),
  when it is generated,
  then exactly one spare torch is placed in one of its rooms, at a random free floor tile, the same
  way the tutorial's coins and a pack's `place:` objects already scatter (`_scatter_tutorial_coins`/
  `_scatter_placements`).
- Given the learner's current torch burns out and at least one spare is already in the backpack,
  when the next step is taken,
  then the next torch lights automatically, no key or menu needed.
- Given the learner's current torch burns out and no spare is in the backpack,
  when they later pick one up,
  then it lights immediately on pickup.
- Given a torch has just burned out,
  when the next step is taken,
  then it is simply gone, not kept as a spent husk item; a burned-out torch never sits in the
  backpack or the message log as something to drop or look at.

### As a learner, I want a message every time my torch's state actually changes, so that I always know why my vision just changed, the same way every other stakes-bearing event already speaks up.

- Given the learner's torch burns out,
  when it happens,
  then the top message line says so (a `msg.torch_out`-style line, the same status-message
  convention `msg.respawn`/`msg.repelled` already use), whether or not a spare then relights.
- Given a spare then lights automatically in that same step,
  when it happens,
  then the message reflects both in one line (burned out, then relit), not two separate lines
  competing for the one-line message slot; if there is no spare, the line says only that the
  learner is now without light.
- Given the learner picks up a torch while their current one is still burning,
  when it is added to the backpack,
  then the message says it was stowed away, not lit (they already have working light).
- Given the learner picks up a torch while they have no working light,
  when it is added to the backpack,
  then the message says it catches/lights immediately, distinct from the "stowed" wording above,
  since this is the one pickup that actually changes what they can see.

### As a learner, I want the ambient room-entry toast to reflect whether I actually have light, so that its mood matches what I can see.

- Given the learner has a working torch when a room's ambient passage (DELVE-0060) is generated,
  when it is shown,
  then it reads the way ambient passages already do (torchlit, somber, cold).
- Given the learner has no working torch when a room's ambient passage is generated,
  when it is shown,
  then it describes the room as darker and gloomier still, unable to make out most of what is
  around them, rather than the usual torchlit framing.

## Non-goals

- The tutorial floor (Dlvl 0): it stays exactly as lit as it is today, no torch mechanic, no
  scattered spare, per this issue's own accepted scope, so a first-timer learns the interface
  without also learning a resource-management mechanic in the same breath.
- Any HP, stakes, or examination penalty for having no torch; darkness changes what is seen and
  what the ambient prose says, nothing about scoring, attempts, or health.
- Pack-authorable torch behaviour (a frontmatter switch to disable it, tune its duration, or place
  extra ones). Purely an engine/session mechanic layered uniformly under every pack; no existing
  pack (the pilot, holy-grail, friends-nap-partners, ethics-of-ai) needs any authoring change.
- A manual "light a torch" action, an equip/unequip choice between multiple carried kinds, or
  stacking/combining light sources for a brighter or wider radius. One torch burns at a time; the
  next lights only once the current one is fully spent.
- Any change to the pet, keeper, or item glyph render precedence already established; only which
  tiles are lit at all changes, not what draws on top of a lit tile.

## Design notes / links

**Vision.** `engine/vision.py:lit_tiles(chapter, p)` gains a `lit: bool` (or similarly named)
parameter: `True` behaves exactly as today (whole current room via `room_at`, else the 3x3
neighbourhood); `False` always returns only the 3x3 neighbourhood, never the room lookup, so a
torchless learner gets the same reveal a corridor already has. This is a small, additive change to
a pure function already shaped for it.

**Discovered/remembered tiles.** `RunState._observe()` already does `self.cur.discovered |=
vision.lit_tiles(...)`, and `_cell()` already renders a tile as fully lit if it is in the *current*
frame's lit set, dimmed if only in `discovered`, else black. That existing split is exactly the
mechanism this issue needs: only union into `discovered` when the learner currently has a working
torch; when they don't, `_observe()` skips the union entirely, so a torchless tile that leaves the
current frame's lit set (recomputed fresh every frame regardless) simply has nothing left placing
it in `discovered`, and `_cell()` renders it black again next frame, no new state to track. This
means the "torch-lit rooms stay remembered forever, torchless ones don't" story falls out of the
existing rendering split almost for free; the real work is in `_observe()`'s one conditional and in
threading "does the learner currently have working light" down to it.

**Torch state.** A new built-in `ItemDef` (`engine/items.py`, alongside `MONEY`, since this is a
core mechanic under every pack, not pack content) plus a duration counter that isn't naturally a
`Stack.count` (a stack counts *identical spares*, not *remaining steps on the one currently
burning*). A `Player` field for steps remaining on the current torch (0 meaning "unlit"), decremented
once per successful step in `_move` (mirroring how HP/turn bookkeeping already happens there), is
the natural home; when it hits 0 and the backpack holds a spare (`Stack` count > 0), consume one and
reset to full duration, otherwise stay dark. ~150 steps per torch (roughly a floor's worth of
walking under normal play), tunable without redesigning the mechanic.

**Messages.** New `[msg]` strings in both locales, in the same voice as `msg.respawn`/
`msg.repelled`/`item.pickup`: one for burning out with a spare ready (relit in the same breath),
one for burning out with none, and two pickup variants (stowed vs. lit on the spot) distinguished by
whether the learner currently has working light at the moment of pickup. All four are ordinary
`self.messages.append(...)` calls at the exact points `_move` (burnout/relight) and the pickup
handler (`_pickup`) already narrate other events, no new message plumbing.

**Placement.** A new `_scatter_torch(cr, rng)`, one call per pack chapter only (skipped for the
tutorial's own chapters in `new_game`), mirroring `_scatter_tutorial_coins`'s exact shape: pick one
random room, one random free interior floor tile in it (excluding the start tile and any keeper),
place a single-count torch `Stack`. A dedicated `Rng` stream, its own offset, so it never perturbs
the exam, pet, carry-flavour, or existing placement streams (CLAUDE.md's RNG-separation rule).

**Ambient prose.** `backstory.build_prompt` gains a fact (e.g. `has_light: bool`), read from
`RunState._room_prompt` off the player's current torch state, adding a clause to the shared
`_SETTING` (or a sibling sentence) that swaps the "scarce, flickering torchlight" framing for
"no light of your own at all; only the few paces you can feel your way through, everything else
impenetrable black" when false. `RoomBackstoryRunner`'s existing queue/cross-chapter-drop machinery
needs no change; this is one more fact riding into a prompt that already carries several.

**Dutch vocabulary for the torch itself.** The verification run against the current ambient prose
(no torch object existed yet) already caught the model inventing inconsistent or malformed Dutch
words for "torch"/"torchlight" ("felkinderende torchtjes"); once a torch is a named object in the
prompt, that risk becomes concrete and worth closing the same way the je/u rule was (a play-feedback
correction to `_SETTING`, not a new mechanism): the shared setting clause should name the exact
Dutch word to use ("fakkel", plural "fakkels"; "fakkellicht" for its glow), explicitly ruling out
"toorts" as a synonym the model must not reach for, mirroring the existing "if replying in Dutch,
say 'je', never 'u'" sentence. The item's own Dutch display name (`ItemDef.name`, e.g. an
`nl.toml`-style localisation if the torch needs one, or a name passed at registration) should also
be "fakkel", so anything the *session* itself renders (an inventory line, a pickup message) is
guaranteed consistent independent of the prompt instruction, the same way the arrow-keys nudge
combines an instruction with a deterministic fallback (DELVE-0061): a prompt instruction alone is
never a hard guarantee for free-form prose, so if this drifts in practice a deterministic
"toorts(en)/toortslicht" -> "fakkel(s)/fakkellicht" substitution on the resolved ambient text
(mirroring `_ensure_arrow_keys_mentioned`'s shape) is the fallback worth adding if it does.

**Snapshot.** One new scalar (torch steps remaining) on top of what already round-trips: the
learner's inventory (a spare torch `Stack` is just another carried kind) and floor items (a
scattered, not-yet-picked-up torch is just another placed `Stack`, already persisted). No new
persistence mechanism, one new field.

## Acceptance / verification

- A `vision.lit_tiles` test asserts `lit=True` behaves byte-identical to today (existing tests
  should need no change beyond the new parameter's default); `lit=False` returns only the 3x3
  neighbourhood even while standing inside a large room.
- A session test walks into a room torchless, asserts only the immediate tiles render lit and
  nothing added to `discovered`; walks back out and confirms those tiles render black again (not
  dimmed).
- A session test does the same while carrying a lit torch and confirms the whole room lights and
  is still dimmed after leaving (unchanged existing behaviour).
- A test drains a torch over its full step budget, confirms vision narrows the step after it hits
  zero, confirms a spare in the backpack lights automatically with no command needed, and confirms
  running out with no spare leaves the learner torchless.
- A test confirms a burned-out torch leaves nothing behind: it is not a droppable/visible spent
  item in the backpack, the floor, or any message.
- A test asserts a burnout-with-relight message, a burnout-with-nothing-left message, a
  stowed-while-still-lit pickup message, and a lit-on-pickup-while-torchless message are each
  distinct and appear only in their own triggering situation.
- A test asserts the torch's Dutch display name is "fakkel", and that `backstory.build_prompt`'s
  Dutch output names "fakkel", never "toorts", for at least the fixed instruction text (the
  free-form passage itself can only be checked probabilistically against a real model, so this is
  a prompt-content assertion, not a generation one).
- A test asserts exactly one torch is scattered per pack chapter, on a free interior tile, and that
  the tutorial's own chapters get none.
- A test asserts a fresh run starts with one torch already lit at full duration.
- A `backstory.build_prompt`/`RunState._room_prompt` test asserts the darker, lightless clause
  appears only when the learner currently has no working torch.
- A snapshot round-trip test asserts torch charge survives a resume.
- `./run-tests.sh` passes; `docs/SCREENS.md` gains a torchless-vision mock-up if the map rendering
  changes enough to be worth showing (a judgement call for the accepted issue's implementation, not
  fixed here).
