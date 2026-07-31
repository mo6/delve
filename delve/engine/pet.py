"""The pet's step: one tile of movement the companion chooses for itself, once per player turn.

Engine mechanics, pure of everything above it (rule 1): it reads the grid and the floor's `$`
stacks, moves the pet, fills or empties its purse, and reports a small `PetEvent` the session turns
into a localised, named message. It never touches strings, content, or the session; a dog crediting
the learner's gold is the session's job, done from the `gave` event, so this needs only the player's
position, not the Player (PETS.md sections 6-7).

What the pet wants depends on whether it is carrying something. A **dog** fetches *any* floor item,
money or object (DELVE-0016), one stack at a time: it heels back and, at your side, sets the stack
down on its own tile for you to collect (coins auto-bank as you step over, an object waits for `,`),
then slinks off on a cooldown. A **cat** cares only for coins: it sweeps up every purse in range,
then hovers in the learner's close surroundings (it no longer bolts to a corner), still holding the
coins until the learner bumps it to take them back (the session). Empty-pawed, either pet seeks a
nearby item, heels if it has drifted past its leash, or mills. Movement draws from a dedicated pet
RNG (never the exam-shuffle RNG), so it is reproducible and leaves examination order untouched (sec.
8); a dog crediting nothing directly, the delivered stack goes onto the floor here and the session
narrates it, keeping `engine` clear of `Player.gold` (rule 1).
"""

from collections import deque
from dataclasses import dataclass

from delve.engine.items import MONEY, Stack, merged, taken
from delve.engine.world import Direction, Point


@dataclass(frozen=True)
class Species:
    glyph: str
    interest: int      # money it will chase, in Chebyshev tiles (both go for coins in range)
    leash: int         # how far it drifts before heeling back; loose, about a room
    p_wander: int      # percent chance to mill to a random tile when it has nothing better to do


# species -> knobs. The registry is the extension point: a parrot or a bunny (PETS.md section 12) is
# a new entry plus its behaviour, not a rewrite. Numbers are play-testing knobs (section 14).
SPECIES: dict[str, Species] = {
    "cat": Species("f", interest=4, leash=6, p_wander=50),
    "dog": Species("d", interest=4, leash=6, p_wander=50),
}


# After the pet parts with a purse (a dog delivering, or a cat caught), it leaves money alone for
# this many of its own steps and wanders off, rather than pouncing straight back onto the coins it
# just handed over (play-testing note). Long enough to clear a small room.
FETCH_COOLDOWN = 8

# How close a carrying cat keeps to the learner once it has swept up the room's money: it no longer
# bolts to a corner, it hovers within this many tiles and mills, so you can bump it when you like
# (play-testing note). Smaller than the empty-pawed leash, so carrying reads as staying near you.
KEEP_CLOSE = 2


@dataclass(frozen=True)
class PetEvent:
    """What a step meant to the world (the session narrates it):

    - ``""`` nothing worth saying.
    - ``"grabbed"`` N coins into the purse (money).
    - ``"grabbed_item"`` an object stack into the dog's paws (`item` names it).
    - ``"gave"`` N coins a dog set down on the tile beside the learner (DELVE-0016: it is a *floor*
      drop now, not a direct bank; the learner walks over and auto-collects it).
    - ``"gave_item"`` an object stack a dog set down on the tile beside the learner (`item` names
      it); picked up with `,`, not banked.

    A dropped stack (money or object) is placed on the floor by the engine here; the session only
    narrates, so `engine` never touches `Player.gold` (rule 1)."""

    kind: str = ""
    coins: int = 0
    item: Stack | None = None


def glyph_for(species: str) -> str:
    spec = SPECIES.get(species)
    return spec.glyph if spec else "f"


def _cheby(a: Point, b: Point) -> int:
    return max(abs(a.x - b.x), abs(a.y - b.y))


def _room_of(rooms, p: Point) -> str | None:
    """The id of the room whose interior floor `p` stands on, or None (a corridor, a door, the
    void). Rooms are disjoint boxes, so at most one matches."""
    for r in rooms:
        if r.contains(p):
            return r.id
    return None


def _adjacent_tiles(grid, p: Point, blocked: set, player_pos: Point) -> set:
    out = set()
    for d in Direction:
        n = Point(p.x + d.delta.x, p.y + d.delta.y)
        if grid.walkable(n.x, n.y) and n not in blocked and n != player_pos:
            out.add(n)
    return out


def _first_step(grid, start: Point, goals: set, blocked: set, player_pos: Point) -> Point | None:
    """The first tile of a shortest path from `start` to the nearest of `goals`, over walkable tiles
    that are neither blocked (a keeper) nor the player's. None when no goal is reachable, or the pet
    already stands on one."""
    if not goals or start in goals:
        return None
    prev = {start: None}
    q = deque([start])
    found = None
    while q and found is None:
        cur = q.popleft()
        for d in Direction:
            n = Point(cur.x + d.delta.x, cur.y + d.delta.y)
            if n in prev or not grid.walkable(n.x, n.y) or n in blocked or n == player_pos:
                continue
            prev[n] = cur
            if n in goals:
                found = n
                break
            q.append(n)
    if found is None:
        return None
    cur = found
    while prev[cur] != start:
        cur = prev[cur]
    return cur


def step(grid, items: dict, player_pos: Point, pet, blocked: set, rng, *, rooms=()) -> PetEvent:
    """Move `pet` one tile and return what happened. Mutates `pet.pos`, `pet.carried`,
    `pet.carried_item`, and `items` (a grabbed stack is removed, a delivered one set down).
    `blocked` is the keeper tiles; the pet never steps onto the player, a keeper, or a wall, and
    takes at most one tile.

    `rooms` is the chapter's rooms (empty on a bare grid). When the player has stepped into a
    different room, the pet drops what it is doing and heads for the door after them, so it always
    follows you next door rather than dawdling a room behind (a play-testing fix). Within the same
    room: a **dog** fetches *any* item (money or object, one stack at a time, DELVE-0016), heels
    back, and sets it down on the tile beside you to pick up yourself; a **cat** sweeps up coins
    then stays near you. Empty-pawed, either seeks nearby items, heels past a loose leash, or mills.

    Delivery is a *floor* drop, not a hand-over: the dog puts what it carries on its own tile (which
    is beside you, since it delivers at heel) and wanders off on its cooldown, so coins auto-collect
    and objects wait for `,`. The engine sets the stack down; the session only narrates, so it never
    banks gold here (rule 1)."""
    spec = SPECIES.get(pet.species)
    if spec is None:                                   # a soloist has no Pet, but be defensive
        return PetEvent()
    cooling = pet.cooldown > 0                         # just handed a purse over: leave money be
    if cooling:
        pet.cooldown -= 1
    cands = _adjacent_tiles(grid, pet.pos, blocked, player_pos)
    target = None

    def heel():
        return _first_step(grid, pet.pos, _adjacent_tiles(grid, player_pos, blocked, pet.pos),
                           blocked, player_pos)

    def seek_items():
        """The first step toward the nearest reachable item in interest range, or None (none, or
        cooling). A dog is drawn to any stack; a cat only to money."""
        if cooling:
            return None
        wanted = {p for p, pile in items.items()
                  if _cheby(p, pet.pos) <= spec.interest and pile
                  and (pet.species == "dog" or any(s.defn.id == MONEY.id for s in pile))}
        return _first_step(grid, pet.pos, wanted, blocked, player_pos)

    def deliver():
        """A dog at heel sets what it carries down on its own tile (beside you) and slinks off on a
        cooldown. Coins land as a `$` pile you auto-collect by stepping over; an object waits for
        `,`. Never banks here; the session reads the event."""
        if pet.carried_item is not None:
            dropped, pet.carried_item = pet.carried_item, None
            kind, coins = "gave_item", 0
        else:
            n, pet.carried = pet.carried, 0
            dropped, kind, coins = Stack(MONEY, n), "gave", n
        items[pet.pos] = merged(items.get(pet.pos, []), dropped)
        pet.cooldown = FETCH_COOLDOWN
        return PetEvent(kind, coins=coins, item=dropped)

    carrying = pet.carried or pet.carried_item is not None
    following = bool(rooms) and _room_of(rooms, pet.pos) != _room_of(rooms, player_pos)

    if carrying:
        if pet.species == "dog" and _cheby(pet.pos, player_pos) <= 1:  # at heel: set it down by you
            return deliver()
        if following or pet.species == "dog":          # keep up, or (a dog) heel it back
            target = heel()
        else:                                          # a cat sweeps the room, then stays near you
            target = seek_items()                      # grab every purse in range first
            if target is None:                         # nothing left: hover close and mill
                if _cheby(pet.pos, player_pos) > KEEP_CLOSE:
                    target = heel()
                elif cands and rng.randint(0, 99) < spec.p_wander:
                    target = rng.choice(sorted(cands))
    elif following:                                    # follow you through the door before all else
        target = heel()
    else:
        target = seek_items()
        if target is None and _cheby(pet.pos, player_pos) > spec.leash:
            target = heel()
        if target is None and cands and rng.randint(0, 99) < spec.p_wander:
            target = rng.choice(sorted(cands))

    if target is not None:
        pet.pos = target

    grabbed = _grab_underfoot(items, pet, spec, cooling)
    if grabbed is not None:
        return grabbed
    if pet.species == "dog" and carrying and _cheby(pet.pos, player_pos) <= 1:  # heeled up: deliver
        return deliver()

    return PetEvent()


def _grab_underfoot(items: dict, pet, spec, cooling: bool) -> PetEvent | None:
    """Take what the pet stands on, or None. A **cat** pockets money even while carrying, so it
    accumulates several purses before it is caught (a play-testing fix). A **dog** takes one stack
    only when empty-pawed (it carries one thing at a time, DELVE-0016): money folds into its purse,
    any other kind becomes the object it is fetching."""
    if cooling:
        return None
    pile = items.get(pet.pos)
    if not pile:
        return None
    if pet.species == "dog":
        if pet.carried or pet.carried_item is not None:
            return None                                # already carrying: one thing at a time
        top = pile[0]
        if top.defn.id != MONEY.id:                    # an object: carry the whole stack
            pet.carried_item = top
            _set(items, pet.pos, pile[1:])
            return PetEvent("grabbed_item", item=top)
    took, rest = taken(pile, MONEY.id, 10**9)
    if took is None:
        return None
    pet.carried += took.worth
    _set(items, pet.pos, rest)
    return PetEvent("grabbed", took.count)


def _set(items: dict, pos: Point, pile: list) -> None:
    if pile:
        items[pos] = pile
    else:
        items.pop(pos, None)
