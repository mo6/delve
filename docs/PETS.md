# Pets: design plan

**Status: implemented in 1.2.0; dog fetch widened to all items in DELVE-0016.** The companion is a
chosen cat or dog (or none), moving for itself each turn via a pure engine step (`engine/pet.py`, a
species registry + `step`), racing for money and objects (a dog fetches any floor item and sets it
down beside you, a cat sweeps coins and is caught by a bump), with the wait key (space), the cat's
free consult (OBJECTS.md §8), selection at start (`--pet`/`--pet-name` or a prompt) and in the
snapshot. Future species (parrot, bunny, §12) remain a registry entry away, deliberately undesigned.
The plan below is kept as the design record.

Draft for review. Turns the fixed trailing kitten into a **named companion that moves on its own**
each turn, the way a NetHack pet does; lets the learner **name it, or go without one**; adds a
**wait** key so the learner can stand still and let it act; and makes the pet **race the learner for
money** on the floor. The companion *choice* and its help with questions also touch
[OBJECTS.md](OBJECTS.md) §8; this document owns how the pet is **chosen, moves, and competes**, and
sketches the **future species** (a parrot, a killer bunny). Ships in **1.2.0**, with the companion.

This plan made assumptions rather than asking mid-flight; the forks that were flagged for review are
now confirmed in §13.

---

## 1. What this plan owns

Today's pet is a fixed kitten (`f`) that teleports into the tile you just left: a shadow, not an
actor. This plan makes it a real companion, and the brief has grown it in several directions:

- a **choice** of animal (dog or cat now; parrot and bunny later), each with its own strengths;
- a **name** the learner gives it;
- the **option of no pet at all**;
- **movement of its own** each turn ("a degree of freedom, like NetHack");
- a **wait** key so you can stand still while it acts;
- a **race for money** lying on the floor (OBJECTS.md §5).

The cat's edge at questions (a free consult per room) is specified in [OBJECTS.md](OBJECTS.md) §8,
because it is about that plan's examination system; everything else is here.

## 2. Choosing a companion: species, name, or none

At the start, after "Who are you?", the learner chooses a companion, the same NetHack-flavoured way:

- **Species.** Dog (`d`) or cat (`f`) in 1.2.0, chosen by a `[cd]` prompt or `--pet dog|cat`.
- **Or none.** "Go alone" is a real option (`--pet none`, or a choice in the prompt). A soloist has
  no `f`/`d` on the map, no pet step, and no consult; `?` answers "You have no companion to ask."
  The **wait** key still works (it just passes a turn). This is a first-class path, not a
  degraded one.
- **A name.** Having chosen an animal, the learner names it ("What is your dog's name?",
  or `--pet-name <name>`); the name is used in every message the pet appears in ("Rex trots back
  with 30 coins."). Empty input falls back to a per-species default ("your kitten", "your dog"),
  which is also what the non-interactive default and the tests use.

**Default (no flags, non-interactive): a cat named as today**, so the golden tests and existing
behaviour are preserved. Species, name, and the none-choice flow `ui → session` as start parameters,
exactly like the learner's name, and never through a `Frame` (rule 2).

The species is modelled as a small **registry** (species → glyph, default name, and the three
behaviour knobs of §6), so adding the parrot and the bunny later (§12) is a data entry plus its
behaviour, not a rewrite.

## 3. The change: a pet that steps for itself

We replace `_advance_pet` with a **pet step**: a single tile of movement the pet chooses for itself,
taken **once per player turn**. A "player turn" is any action that advances `T`: **Move, Wait,
bump-to-talk, Pickup, Drop, Rest**. Free actions (talk with `t`, consult with `?`, turning a lesson
page, opening the inventory to look, descending or ascending) pass no time, so the pet does not step
on them, mirroring NetHack, where the world moves when you do and holds still while you read a menu.

A soloist (no pet) simply has no step.

## 4. The wait key (space)

A new **`Wait`** command, bound to **space on the map**: the learner stands still, `T` advances, and
the pet takes its step. It is the "waiting moment so the player is not moving but pets can" from the
brief, and it lets you send a dog after a distant coin or hold position while a cat wanders off the
money you want.

**Space is already the page-turn key inside an overlay**, and that is fine because the two never
overlap: with a panel open, space means "next page / continue" (as now); on the bare map, with no
overlay, space means Wait. The `ui` already picks a key's meaning by context, so it maps space to
`Confirm` while a panel is up and to `Wait` otherwise. The hint line names it on the map ("Wait:
space") so it is discoverable.

## 5. Money and the race

**Both species pick money up and carry it; you get it back by retrieving it from the pet** (decided).
When a pet's step lands it on a `$` stack it adds the coins to its own **carried purse**
(`pet.carried`), not your gold; the coins are yours only once the pet hands them over. How that
happens splits by species, in character:

- **Dog: sets it down beside you.** While carrying, a dog *heels to deliver*: it heads for you, and
  the moment it stands adjacent it **drops what it carries on its own tile**, right beside you ("Rex
  trots back and drops 30 coins beside you."), and slinks off on its cooldown. You collect by
  stepping over the drop: coins auto-bank (OBJECTS.md §5), an object waits for `,`. It is a *floor*
  drop, not a hand-over into your gold (DELVE-0016; the earlier build banked coins directly, which
  read as the reward vanishing the instant it arrived). Left alone the dog always returns, so it is
  an assist with a delay: coins and objects you could not reach still end up at your feet. It fetches
  **any** floor item, not only coins, one stack at a time (§ objects below).
- **Cat: makes you catch it.** A cat *flees while it carries*: on its step it moves away from you if
  it can. To get the coins you must **catch it**, by walking into its tile (a bump, like bumping a
  keeper), which takes back the purse ("You corner Minou and prise 30 coins loose."). A cat with
  nowhere to flee is easy to bump; one with room to run is a real game, and one you never catch keeps
  the coins. That is the competition.

**Retrieval is a bump.** Walking into your pet's tile takes any coins it carries (and is how you
catch a cat); it does not swap places and, like the keeper bump, costs a turn. A dog gives freely
without needing the bump; the bump is there for when you want to hurry it, or to corner a cat. Money
the **player** reaches first is still auto-collected straight to gold (OBJECTS.md §5); first to the
tile wins, and after that it is a question of prising it loose.

## 6. Architecture and the rules

The pet is an `engine` entity and the **pet step is engine mechanics**: it reads the grid and the
floor's item stacks, moves the pet, and **sets a delivered stack down on the floor** (never touching
`Player.gold`; the session banks it when the learner steps over, DELVE-0016), all types the engine
already owns, so it stays inside rule 1 (`engine` imports no content, session, or strings).

- The step is a **pure function** of `(grid, floor items, player pos, pet state, rng)` returning the
  new position and a small **event** (`grabbed N` / `grabbed_item` into its paws, `gave N` /
  `gave_item` set down beside you, `spoke <line>` for a future parrot). The session turns the event
  into a localised, named message; the pet never touches the strings catalogue, exactly as the gate
  returns a `SittingResult` the session narrates.
- It draws from a **dedicated pet RNG**, separate from the examination-shuffle RNG (§8). Nothing in
  `ui` changes beyond mapping space to `Wait` and painting `f`/`d`; the pet already reaches the UI
  through the `Frame` (rule 2).

## 7. The step algorithm

Each pet step is one tile, chosen for itself. **Carrying coins changes what it wants**, which is what
makes retrieval (§5) a game:

- A **dog that carries** *heels to deliver*: stepping toward the player is its top priority, and it
  hands the purse over the moment it is adjacent.
- A **cat that carries** *flees*: its top priority is the reachable adjacent tile that puts the most
  distance between it and you, so you have to corner it to bump it.

Empty-pawed (or just delivered), it falls to the ordinary priorities:

1. **Seek money.** If a `$` tile lies within the species' **interest radius** and a step moves the
   pet closer, take it (first step of the BFS the codebase already uses). Dogs have a wide radius
   (they fetch); cats about one (they grab only what they mill into).
2. **Heel.** Else, if the pet is beyond its **leash radius**, step toward the player. The leash is
   **loose** (about a room), so the pet ranges freely and can drift out of sight in the dark before
   it turns back, which is the "degree of freedom" the brief asks for.
3. **Wander.** Else, with probability `p_wander`, step to a random adjacent walkable tile; otherwise
   stay put. Near you, it mills instead of standing at heel.

Never steps onto the player, a keeper, or a non-walkable tile. May step onto floor, corridor, door,
stairs, pedestal, and item tiles. One tile per turn. Radii and `p_wander` are **tunable knobs**
(§12), sane defaults tuned in play.

## 8. Determinism and the golden tests

- **Separate RNG stream.** The pet draws from its own RNG, seeded from the run seed but distinct from
  `self.rng` (which shuffles exam options). Shared, pet wandering would change every question's
  shuffle and silently break the golden slice; a dedicated `pet_rng` keeps movement reproducible and
  leaves examination order untouched.
- **The golden slice moves.** Tests that assert the pet trails into the vacated tile are rewritten in
  1.2.0 to the new behaviour (or relaxed to "walkable, near, never on the player"), and a focused
  `test_pets.py` covers species selection, none, seek / heel / wander, and dog-fetch / cat-steal on a
  hand-built grid, no terminal.

## 9. Snapshot

Store the pet **species** (or `none`), its **name**, its **position** (already saved), and its
**carried purse** (`pet.carried`), since both species now hold coins until you retrieve them and a
cat may be carrying yours across a save. The `pet_rng` re-seeds deterministically on load, so
wandering after a resume is deterministic-from-load (not necessarily tile-identical to an
uninterrupted run past the resume point); the pet is flavour, and serialising its RNG is not worth
it. Noted, not fixed.

## 10. Rendering

The pet is drawn `f` or `d` at its position, only when that tile is lit or already discovered (as
today), so a pet that wanders into the dark is unseen until you find it again. A soloist draws
nothing. `tools/screens.py` gains a frame with the pet off to one side of the player (not glued
behind it) so the new look is verified evidence.

## 11. Edge cases

- **No pet.** No step, no glyph, no consult (`?` explains there is no companion); the wait key and
  everything else are unaffected.
- **Chapter change.** The pet follows through the stairs: placed beside the player on the new floor
  (`_pet_spot`), not made to path there, and it does not step on the turn the stairs are taken.
- **Keepers and sealed doors** are not walkable to the pet; it never blocks a keeper or slips through
  a sealed door, and can sit in a room with an unpassed keeper without interfering.
- **Overlays freeze it.** No turn passes while a panel is open, so it holds still; consult (`?`) works
  wherever it stands (consult is about the companion, not its tile).
- **REPELLED / respawn.** The pet is replaced beside the player at the chapter entrance, so the two
  never separate across a push-back or an HP:0 respawn.

## 12. Future species (planned, specifics TBD)

The registry (§2) is built so these drop in later without reworking the engine; their behaviour and
numbers are **to be determined**, listed here so the model leaves room for them:

- **Parrot (talking).** A bird companion that *speaks*: a `spoke` event carries a flavour line the
  session prints (idle chatter, or perhaps echoing a keeper's teaching, or a rare nudge on a
  question). Glyph likely `B` (NetHack's bird class) or another ASCII bird; a talking pet is a good
  fit for a *third* question-helper flavour. Open: what exactly it says, and whether it helps or is
  pure colour.
- **Bunny (vicious killer).** The Monty Python Killer Rabbit, all teeth. The tension to resolve: the
  dungeon has **no monsters** and HP is the *learner's* stake, not a combatant's (rule 4), so there
  is nothing for it to kill yet. Its "vicious" bite therefore needs a target that does not exist
  today; its design waits on whatever introduces one (a hazard? a rival pet? pure menacing flavour on
  move?). Glyph likely `r` (rodent). Genuinely open, and deliberately not designed here.

Adding either is: a registry entry (glyph, default name, knobs), a behaviour branch in the pet step
or event set, its strings, and a selection option. The choice prompt and `--pet` grow to include
them; nothing else moves.

## 13. Decisions (confirmed)

1. **Money (§5): both carry, you retrieve.** Both species pick coins up into a carried purse; a dog
   heels back and gives them when adjacent, a cat flees and must be caught by bumping it. Retrieval
   is a bump into the pet. This adds `pet.carried` state (persisted, §9) but makes both species
   compete, which is the point.
2. **Wait on space.** Space = Wait on the bare map, and still page-turn inside an overlay (the
   contexts never overlap).
3. **Loose leash.** The pet ranges about a whole room and can drift out of sight in the dark before
   heeling back; more life, occasionally off-screen.

## 14. Tunable knobs (defaults, tuned in play)

| Knob | Cat | Dog | Note |
|---|---|---|---|
| Interest radius | ~1 (grabs coins it mills into) | ~4 (fetches any item) | Chebyshev tiles from the pet. |
| Leash radius | ~room | ~room | Loose: heel back only when it drifts a room away. |
| `p_wander` | ~0.5 | ~0.5 | Chance to mill vs. hold when near you. |
| Carrying | coins only; flees you, catch by bumping | any item; heels back, sets it down beside you | Cat holds coins in `pet.carried`; a dog's object is `pet.carried_item` (DELVE-0016). |

## 15. Rejected / deferred

- **A pet that takes damage or that the dungeon punishes:** rejected; HP is the learner's stake, not
  the pet's (rule 4). The pet is flavour and help.
- **Serialising the pet RNG across a save** for tile-exact resume: deferred; not worth it for flavour
  movement (§9). A **fetch** is exempt without it: seek then heel then deliver is pure BFS and draws
  no RNG, so a resumed dog finishes a fetch on the identical tile; only idle milling (which consumes
  the pet RNG) diverges after a resume (DELVE-0016 leans on this).
- **A pet that carries objects** (not just money): ~~deferred~~ **done (DELVE-0016).** The dog now
  fetches any floor item, one stack at a time, and sets it down beside you like coins; delivery
  became a floor drop for both money and objects, so nothing banks straight into gold. The **cat**
  stays money-only. See §5/§7 and `engine/pet.py`.
- **A command to call / stay / fetch on demand:** deferred; automatic seek / heel / wander covers the
  brief without new keys. A `Fetch` key could come later.
- **The killer bunny's bite:** deferred by necessity (§12); nothing to kill yet.
