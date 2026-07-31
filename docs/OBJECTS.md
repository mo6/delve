# Objects: design plan

**Status: fully implemented (1.1.0 money, 1.2.0 companion, 1.3.0 pack objects).** Adds
pickup-and-drop **objects** to Delve: a generic engine item model, money
that finally means something and lies on the floor as a reason to explore, and pack-authored
objects with flavour effects (the Monty Python coconuts). The **companion** (dog or cat) and how it
*moves* and competes for money is a sibling plan, [PETS.md](PETS.md); this document owns items and
money, that one owns the pet. Target releases: **1.1.0** (money) then **1.2.0** (companion, with
pets) then **1.3.0** (pack objects).

This plan made assumptions rather than asking mid-flight; the confirmed decisions are in §15.

---

## 1. Goals

- **Generic objects** the engine understands (money above all), and **pack-specific objects** an
  author defines and places (coconuts, a found USB stick, a pillow).
- **Pick up and drop, item by item.** A learner can carry things, look at what they hold, and put
  single things down. Two coconut shells are two things; a hundred coins are a hundred coins.
- **Money on the floor.** A keeper can drop coins **on a tile**; the learner collects them by
  **walking onto that tile**. This is a concrete reason to move around and explore, not just a
  number that ticks up. It gives the dead `$:0` in the status line its first real source.
- **Companion choice** (dog or cat), each better at a different thing, and each able to grab money
  off the floor too, so there is a friendly race for it. Movement and competition: [PETS.md](PETS.md).
- **Make the shipped packs more interesting** with a few well-chosen objects.

## 2. The one hard constraint

**Objects never gate mandatory progress.** A sealed door opened by a keeper is the *only* gate in
Delve, on purpose (CLAUDE.md rule 2: "Sealed doors are structural. Never add path validation"). An
object that were *required* to pass a room or open a way would reintroduce exactly the
inventory-and-path validation the design deleted, and could soft-lock a learner who dropped it.

So objects are **flavour, teaching moments, and optional bonuses only.** A found-USB stick can
*teach* (picking it up prints a cautionary line); it can never be the key a door demands. This
constraint is load-bearing and shapes everything below.

## 3. Where objects live (the five rules)

The item model is **generic and lives in `engine`** (like `Player`, `Pet`, `Keeper`): an item is
pure data, and the engine can place, move, pick up and drop items with no idea *why* an item
exists. This keeps rule 1 (`engine` imports no content).

Pack-specific objects are **content** (`content/`): an author writes item definitions and places
them. The **session** is the assembler that already imports both engine and content (`new_game`
parses a pack and builds the dungeon); it translates content item-definitions into engine items on
the floor, exactly as it already translates parsed rooms into a laid-out chapter.

Effects are **data, never code.** A pack cannot ship behaviour; it selects from a small, closed
vocabulary of effect kinds the session knows how to run (a flavour message on move, a message on
pickup, a money value). This keeps packs as data (rule 5's spirit), keeps us stdlib-only, and keeps
a downloaded pack from being a program.

`gate.py` stays the *training* seam and is **not** touched for objects: money-on-pass is a session
policy, not a gate mechanic (§7). Nothing new crosses the `ui → session` line: items ride existing
view-model types, and the companion choice flows in as a start parameter like the learner's name.

## 4. The item model (engine): counted stacks

The unit that lies on a tile or sits in the pack is a **stack**: an item kind plus a count.
Identical kinds merge into one stack (a hundred single coins are one `$` stack of 100; two coconut
halves are one stack of 2), and pickup and drop **adjust the count**, so "drop one" and "drop
fifty" are the same operation with a different number. This is the standard roguelike model and it
covers both refinements (many items per tile, granular money) without tracking a hundred separate
objects or a per-instance id.

```python
# engine/items.py
@dataclass(frozen=True)
class ItemDef:
    """A *kind* of thing. Generic ($ money) or pack-authored (a coconut half)."""
    id: str                 # 'money', 'coconut-half', 'usb-stick'
    glyph: str              # one ASCII object-class char: $ ( % ! ? [ * ) = "
    colour: str             # a Colour name (view-model), e.g. 'bright_yellow'
    name: str               # singular; a stack renders as "coconut half (2)" (localised)
    carriable: bool = True  # money is False: it banks to gold, never an inventory slot
    value: int = 0          # worth per unit; money is 1 ($1 a coin), objects 0
    bulky: bool = False      # fills the whole tile: nothing else may share it
    on_move: str = ""       # flavour printed each step while carried (localised)
    on_pickup: str = ""     # flavour printed once, when taken (localised)

@dataclass(frozen=True)
class Stack:
    defn: ItemDef
    count: int              # >= 1; identical defns merge; pickup/drop change this
```

- **A tile holds a pile:** `Chapter.items: dict[Point, list[Stack]]`. Usually one stack; several
  when different kinds share a tile. A pile paints as its **top** stack's glyph.
- **Stacking, and the exception.** Any number of stacks may share a tile, **except a `bulky` item,
  which fills the tile alone**: nothing stacks onto a bulky item and a bulky item cannot be dropped
  onto an occupied tile. That is the "fills up an entire tile" case; everything else piles freely.
- **`Player.inventory: list[Stack]`** holds carriable stacks; **`Player.gold: int`** (already
  there) holds money. Money is never an inventory slot: collected, it is gold; dropped, it becomes
  a `$` stack on the floor again (§5).
- Money is the built-in `ItemDef('money', '$', 'bright_yellow', carriable=False, value=1)`; every
  pack gets it for free. A `$` stack's worth is `count` (in $1 units).
- Object glyphs are **map glyphs, so ASCII only** (CLAUDE.md), drawn from NetHack's object classes:
  `$` coin, `(` tool, `%` food, `!` potion, `?` scroll-like, `[` armour, `*` gem, `)` weapon, `=`
  ring, `"` amulet. The validator restricts to this set so a glyph never collides with a wall or the
  `@`/`f`/`d` actors and never smuggles in a non-ASCII cell.

## 5. Money: on the floor, granular, auto-collected

- **Money lies on tiles, not in rooms.** A keeper drops coins **on a specific tile** (§7); loose
  coins can sit on any floor tile. Collecting them means **walking onto the tile**, which is the
  point: money is a concrete pull to move and explore, not a passive counter.
- **Auto-collected.** Stepping onto a tile with a `$` stack banks the whole stack: `gold += count`,
  the stack vanishes, a message prints ("You collect 40 coins." / localised). No key, no inventory
  slot. This is the "money should be auto-picked up" requirement, and NetHack's behaviour for `$`.
- **Granular.** `$100` is a stack of 100 `$1`; you can **drop any amount** (§6). Dropping splits the
  count off your gold onto the tile; coins dropped onto a tile that already has coins **merge**.
- **Pets grab money too.** A companion that reaches a coin tile first carries it off, so there is a
  race: a dog heels back and hands it over, a cat flees until you catch it. The mechanics live in
  [PETS.md](PETS.md); the only thing the item layer owns is that a `$` stack can be picked up by the
  pet-step as well as by the player.
- **What money is for (decided: collectible + score only):** it accrues, is shown in the status
  line and on the **win screen / scroll** as wealth earned, and does not yet buy anything. A spend
  sink (gold buys a free consult) is a **later release**, not v1.

## 6. Pick up, drop, inventory

Three new commands and one new overlay, all NetHack-keyed:

| Key | Command | Behaviour |
|---|---|---|
| `,` | `Pickup` | Take carriable items off your tile. A pile of several kinds, or a stack you want to split, opens a small menu; a single stack is taken whole. Money never needs this (it auto-collects). |
| `d` | `Drop` | Put something down onto your tile: a menu of your inventory stacks plus, when `gold > 0`, a **coins** entry that asks an amount. Dropping onto a tile that holds a bulky item, or dropping a bulky item onto an occupied tile, is refused with a message. |
| `i` | `Inventory` | Open a read-only panel listing what you carry (stack names and counts). |

- **Item by item.** Because a pile is a list of stacks and each stack has a count, pickup and drop
  work on a single kind and a chosen amount: pick up one coconut half of two, drop fifty coins of a
  hundred. "Individually" falls straight out of the counted-stack model.
- `d` is free on the map (the `a`–`d` answer keys only bind inside a question overlay); `,` and `i`
  are unused today. The inventory and drop menus are `Overlay` variants painted by the existing
  panel machinery (rule 2 untouched).
- **Turn cost:** pickup and drop cost a turn (they are actions), consistent with the bump-to-talk
  precedent, and so a pet takes its step while you rummage (PETS.md). Opening the inventory to
  *look* is free.
- The **hint line** gains the keys contextually: standing on a pile, "Pick up: ,"; carrying
  something, "Drop: d   Inventory: i".

**Multiple-choice answers move from letters to numbers** (`1`, `2`, `3`, …). Today an MCQ is a
lettered menu (`a`–`d`); giving the map a `d` (drop) makes the letter answers a mental collision
even though the two never bind at the same time (answers only inside a question overlay, `d` only on
the map), and numbers are simply faster to hit. So the MCQ menu renders `1 - …`, the `_answer`
header uses the digit, and the hint becomes "Answer: 1-{n}". This is a small edit to the **question
format**, so it also touches CLAUDE.md's "Question format" rule ("lettered menu" → "numbered menu"),
the `answer_many` hint string in both locales, `session/run.py`'s header formatting, and the message
tests that assert on the lettering. **Two-way assertions are unchanged**: they keep the author's two
labels and the keys derived from them (CLAUDE.md's settled two-way design), which never collide with
a map command for the same reason. It ships in **1.1.0** with the commands that motivate it.

## 7. The reward: a keeper drops coins on a tile

- On passing a room that carries a **`reward:`**, the keeper **drops coins on the floor of the
  room**, which the learner walks over and auto-collects. Amount from frontmatter: a pack-level
  `reward:` default with a per-room override; a room with no reward pays nothing.
- **In the room, off the exit, not on the way out** (a play-testing correction). Coins on the
  opened door sit on the path the learner is already taking, and the learner is always nearer the
  exit than a roaming pet, so there is no race and no reason to explore. Dropped on a **random
  interior tile** of the room (DELVE-0015; it was the tile farthest from the exit, which always
  filed the reward into the same corner and gave the room's shape away), they are a detour worth
  taking now and a coin a pet could reach first once it roams (1.2.0, [PETS.md](PETS.md)). The
  draw is deterministic, seeded from the run seed and the room id so the run stays regenerable
  tile-for-tile.
- **Scaled by the passing score** (a play-testing correction): the coins are `round(reward ×
  score)`, so answering well pays more than scraping the pass mark. The reward line still names the
  amount actually dropped.
- **Any keeper kind can reward** (decided); the **shopkeeper is the natural default flavour** ("the
  shopkeeper pays you for the lesson"), not a requirement, so a wizard's room can pay too.
- Because the coins are a real `$` stack on a tile, a pet may reach the reward first and carry it off
  (PETS.md): a dog heels back and sets it down beside you (a floor drop now, DELVE-0016, so you still
  step over to collect), a cat makes you chase it down, so dawdling has a small, funny stake. A dog
  fetches scattered pack objects the same way, not just coins.
- **Placement in the code:** the session's pass handler (`_record_pass` / the passed branch of
  `_confirm`), **not** `gate.py`. Turning the sealed wall into a door is the gate's job; dropping a
  reward is a session policy that reads the room's `reward`, leaving `gate.py` the pure training
  seam. The reward is paid **once** (guarded like `passed_at` is write-once), never farmed by
  re-entering (rule 3).

## 8. The companion (choice, and question help)

The pet stops being a fixed kitten and becomes a **dog or a cat**, chosen at the start. Two aspects
of that split live here because they are about *this* plan's systems; the rest is [PETS.md](PETS.md).

- **Selection.** The learner picks a species (dog or cat), **names it**, or chooses **no pet at
  all**, at start (like "Who are you?"); the full selection flow, the no-pet path, and the future
  species (parrot, bunny) are [PETS.md](PETS.md) §2. It **defaults to a cat** named as today, so
  existing behaviour and the golden tests are preserved, and flows `ui → session` as start
  parameters (like the name).
- **Glyphs:** cat `f` (feline, unchanged), dog `d`; both canonical NetHack and ASCII.
- **Question help (the cat's edge).** The cat is the clever one: its **first consult in each room is
  free** (no score cost); further consults cost the question as today. The dog's consult still
  strikes one wrong option but is **never free**. "Cats are more intelligent, help more with
  questions."
- **Objects and money (the pet's role)**: both pets move on their own each turn and pick things up; a
  dog fetches **any** floor item (DELVE-0016) and sets it down beside you, a cat sweeps coins and
  flees until you catch it (a bump). All of that, plus the **wait** key, is [PETS.md](PETS.md). The
  item layer only needs to expose that a pet-step can pick up a stack and set it back down on a tile.

The exact numbers (free-consult count, dog hold size, pickup radius) are **balance knobs** tuned in
play-testing, like the M4 stakes.

## 9. Pack-defined objects (authoring)

**Definitions** live in the locale subtree so localisation and the tree-parity check come for free,
one file per item kind, using the existing flat `key: value` frontmatter (no YAML, no nesting):

```
packs/holy-grail/en/items/coconut-half.md
---
id: coconut-half
glyph: (
colour: yellow
name: coconut half
on_pickup: You pick up an empty half-coconut. Suspiciously horse-like.
on_move: You bang the coconuts together. Clip-clop, clip-clop.
---
Half of a tropical coconut, hollow and dry. One of a pair, by the look of it.
```

The body is the item's "look" description (shown in the inventory panel). The Dutch tree carries
`packs/holy-grail/nl/items/coconut-half.md` with the translated `name`, `on_pickup`, `on_move` and
body; the validator diffs the trees and errors on a missing translation, as it does for rooms.

**Placement** is a room's frontmatter, since content rooms already map one-to-one onto grid rooms.
A count places a stack; the two coconut halves are one placement of two:

```
place: coconut-half x2      # a stack of two on this room's floor; several kinds comma-separated
```

The session scatters placed stacks on free interior floor tiles of that room, **deterministically
from the run seed**, so the dungeon stays regenerable tile-for-tile (the layout invariant) and a
snapshot need only record what the learner *changed*.

**Effect vocabulary (v1), closed:** `on_pickup` (message once, when a kind first enters your hands),
`on_move` (message each step while carried), and `value` (currency; implies auto-collect,
non-carriable). Effect messages **dedupe by kind per step**, so carrying two coconut halves prints
one "clip-clop", not two. That is enough for the coconuts, a cautionary USB, and reward coins. A
richer set (a lantern that widens vision, an item that buys a free hint) is a documented extension,
added by growing the vocabulary, never by letting a pack ship code.

**Validation (schema.py, gathering Issues):** glyph is a single ASCII char from the object-class
set; `colour` is a known Colour name; effect keys are from the closed vocabulary; `place:` names a
defined kind, a valid count, and a real room; ids are unique; the `en`/`nl` item trees match and
every localised string is present. A room over-full of objects is a **warning**, not an error (like
the 7-room capacity warning): clutter is a taste smell, not a broken pack.

## 10. Persistence (snapshot)

The snapshot records the learner's *mark* on a regenerable dungeon (CLAUDE.md). Objects add mutable
state, so it gains:

- `player.inventory`: carried stacks, as `(def-id, count)`. No instance ids: a stack is a kind and a
  count, so the snapshot is a short list of pairs.
- per chapter, the **current floor state**: for each tile that differs from the freshly scattered
  layout, its stacks as `(def-id, count)`. Item counts are tiny, so the snapshot stores the floor
  outright and resume overwrites the scattered items with it (the same shape as re-opening earned
  gates).
- pet **species** (top level), so a resumed run keeps your dog.
- gold is already saved.

**A pre-1.1 unfinished run will not resume** (the snapshot shape changed), the same call made for
the M6 tutorial change: local dev data only, no migration written. Documented, not fixed.

## 11. Rendering (view models)

- `_cell` priority becomes: player `@` > pet `f`/`d` > keeper `@` > **top floor stack** > tile. A
  stack shows its `glyph` in its `colour` (a Colour name; `ui/attrs.py` already maps Colour to a
  curses attribute, so nothing new crosses into `ui`).
- New `InventoryView` / drop-menu overlays ride the existing panel painter; the drop amount prompt
  reuses the numeric-entry pattern the resize overlay already implies, or a simple `[- +]` stepper.
- `tools/screens.py` has the object mock-ups (SCREENS.md §11, screens 12-14): the coin reward on
  the door, the pack panel, and the drop-amount stepper, so the object look is verified evidence, not
  a guess, and `--check` holds them to 100×30. The coconut and other pack-authored kinds join them
  at 1.3.0.

## 12. Localisation

- Engine-owned strings (money collected, pick up, drop, empty inventory, the reward line, the amount
  prompt) get an `[item]` block in `delve/strings/{en,nl}.toml`, like every other message.
- Pack-owned strings (a kind's `name`, `on_move`, `on_pickup`, look) live in the pack's item files,
  per locale. English `en.toml` values remain verbatim test fixtures; the pack strings are free.

## 13. Making the shipped packs more interesting (proposals)

Kept deliberately light: objects are seasoning. One or two per pack, none required to progress.

- **holy-grail (Monty Python): the coconuts.** A stack of two coconut halves in an early room; pick
  them up and every step prints one "clip-clop" (`on_move`, deduped). Pure iconic flavour, and the
  reference implementation of `on_move`; dropping one half and keeping one is possible and, in
  character, pointless. Optional second object: the **Holy Hand Grenade** `*`, a collectible trophy
  with a mock-portentous pickup line.
- **security-onboarding (the pilot): a teaching object and a reward.** A **found USB stick** `(` on
  the floor: picking it up prints a cautionary line ("You pocket a USB stick you found on the floor.
  In real life, this is how they get in."), turning a NetHack reflex (grab the loot) into the
  lesson. Plus a **`reward:`** on a room so passing drops coins, so the `$` counter finally moves and
  "compliance pays" lands literally, with a coin race against a cat as a bonus.
- **ethics-of-ai: a reflective token.** A **black-box `(`** or a **weighing-scales** whose pickup
  line poses the chapter's question in one sentence. Light, optional, thematic.
- **friends-nap-partners: a comfort object.** A **coffee `%`** or **pillow `(`** with a warm pickup
  line. Flavour only, matching the pack's gentle tone.

## 14. Phasing and delivery

Each phase is a shippable slice with its own tests, ruff, screen-check and (from phase 4) pack
validation; each is a commit (or a few). **Decided: money ships first**, then the companion, then
pack objects.

**→ 1.1.0 (money and carrying):**
1. **Engine item model + money + pickup/drop/inventory.** `engine/items.py` (`ItemDef`, `Stack`),
   floor piles, inventory, the three commands (`,` `d` `i`), auto-collect, granular drop, the bulky
   rule, the inventory/drop overlays, item cells, strings, snapshot, a screen mock-up. Coins placed
   by a test fixture; no pack content yet.
2. **Reward on a pass. (Done, 1.1.0; tile randomised DELVE-0015.)** Keeper drops coins on the floor
   of the room, on a random interior tile (`_reward_tile`; was the tile farthest from the exit),
   **scaled by the passing score** (`round(reward × passed_score)`), which the learner walks over
   and auto-collects; `reward:`
   frontmatter, a pack-level default any room may override (`Pack.reward` / `Room.reward`), paid
   once via a `Gate.rewarded` guard, and never on the unscored tutorial floor. `$` now moves in real
   play; the win screen shows wealth earned (`launch.outcome_lines` + `scrolls.format_money`). The
   pilot sets a pack default of 20 and Ives the shopkeeper overrides it to 50; the Holy Grail pack
   pays 5. (Placement moved into the room, and the amount became score-scaled, after play-testing;
   the on-the-way-out drop gave the pet nothing to race for. See §7 and §16.)

   Also in 1.1.0, folded in because the drop key motivates it: **MCQ answers become numbers**
   (`1`–`n`) instead of letters, updating the menu render, the hint string, the `_answer` header,
   the "Question format" rule in CLAUDE.md, and the lettering tests. Two-way assertions keep their
   author-label keys.

**→ 1.2.0 (companion, with movement). Done.** The dog/cat choice **and** [PETS.md](PETS.md) in full:
the pet moves on its own each turn (`engine/pet.py`), the **wait** key (space) passes a turn so the
pet can act while you stand still, the **cat's free consult** (its first per room, no score cost,
`Examination.freebies` + `Gate.free_consult_used`), the dog fetching and the cat keeping money, and
the coin competition (`pet.carried`, retrieved by bumping the pet). Selection (species / name / none)
flows in as a start parameter (`--pet`/`--pet-name` or a prompt) and rides the snapshot. Money picked
up by pets was the join point built here.

**→ 1.3.0 (pack objects). Done.**
3. **Pack-authored objects.** Item files (`<locale>/items/*.md`) parse into engine `ItemDef`s; a
   room's `place: <id> xN` scatters stacks on interior floor tiles, deterministically from a
   dedicated rng. The closed effect vocabulary runs in the session: `on_pickup` once per kind
   entering the hand, `on_move` each carried step (deduped by kind), `value` as a currency that
   banks like money. `schema.py` validates the glyph/colour sets, the closed key vocabulary, unique
   non-reserved ids, and every `place:` naming a defined kind; item-tree parity falls out of the
   existing locale diff. Snapshot round-trips carried and floor stacks by id via a registry the
   session populates at load. AUTHORING.md gained section 14; STYLE.md a section-5 flavour note.
4. **Pack content.** The section-13 objects, both locales: holy-grail's coconut halves (the
   `on_move` reference), security-onboarding's found USB stick (the `on_pickup` teaching
   reference), a black box in ethics-of-ai, a Central Perk coffee in friends-nap-partners. All four
   packs validate clean.

## 15. Decisions (confirmed)

1. **Money's purpose**: *collectible + score only.* No spend sink in v1.
2. **Money lives on tiles, granular.** A keeper drops coins on a specific tile; the learner collects
   by walking onto it (a reason to move); `$100` is 100 `$1` and any amount can be dropped.
3. **Many items per tile, item by item.** A tile holds a pile of counted stacks; pickup and drop act
   on one kind and a chosen amount (two coconut halves are two, handled singly). The exception is a
   **`bulky`** item, which fills the whole tile and does not share it.
4. **Companion split**: *cat = questions (free consult), dog = objects/money.* Numbers are
   play-testing knobs. Movement, the wait key, and money competition are specified in
   [PETS.md](PETS.md).
5. **Scope / sequencing**: *money first.* 1.1.0 money; 1.2.0 companion (with pets); 1.3.0 pack
   objects and content.
6. **Reward source**: *any keeper can reward* a room that sets `reward:`; the shopkeeper is the
   default flavour, not a requirement.
7. **MCQ answers are numbers** (`1`–`n`), not letters, so they neither collide mentally with the new
   map letters (`d` drop) nor slow the learner down; two-way assertions keep their author-label
   keys. A small "Question format" change, shipped in 1.1.0.

## 16. Rejected / deferred

- **Objects as keys** (required to open a way): rejected, §2 (soft-lock, re-adds path validation).
- **Code in packs** (a scripting hook for effects): rejected; effects are a closed data vocabulary
  (security, stdlib-only, packs-are-data).
- **Per-instance object identity:** rejected in favour of counted stacks; nothing in v1 needs to
  tell one coconut half from the other, and stacks make granular money and the snapshot trivial.
- **256-colour item glyphs / emoji objects:** rejected; ASCII object classes only (the map-glyph
  rule).
- **A lantern that widens vision, a shop you spend gold at:** deferred; both are vocabulary/system
  growth on top of this, not part of the first cut.
- **A locked chest for larger rewards / escalating rewards on deeper floors:** deferred (a
  play-testing idea). Once the pet roams and races for coins (1.2.0), a big reward left loose is a
  big reward a cat can steal; the idea is to store a large or late-floor reward in a **chest** the
  learner opens but a pet cannot, and/or to grow the reward on deeper floors. Both are pack-content
  choices plus one new object behaviour (a container), so they wait for pack-authored objects
  (1.3.0); noted here so the placement-and-scaling work above leaves room for them.
