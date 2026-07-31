"""Actors on the floor: the Player, the learner's Pet, and the Keeper family. Position is the
learner's mark and is owned by the session's RunState, but the types live here per PLAN.md
section 5. Nothing here imports content or assess; the pet is handed a question at call time and
only reads its options, so `engine` stays ignorant of the assessment format (CLAUDE.md rule 1).
"""

from dataclasses import dataclass, field

from delve.engine.items import Stack
from delve.engine.world import Point


@dataclass
class Player:
    pos: Point
    name: str = "Adventurer"
    hp: int = 12
    max_hp: int = 12
    gold: int = 0
    # Carriable objects held (OBJECTS.md). Money is not here: it banks to `gold`. A stack is a
    # kind and a count, so what a learner carries is a short list of stacks.
    inventory: list[Stack] = field(default_factory=list)
    # Steps remaining on the torch currently burning (DELVE-0062); 0 means unlit. Not a `Stack`
    # count, which counts identical spares, not steps left on the one alight. A fresh run starts
    # a learner with this already at `TORCH_DURATION_STEPS` (`new_run`/`new_game` set it).
    torch_charge: int = 0


@dataclass
class Pet:
    """The learner's companion, a cat ('f') or a dog ('d'). It moves for itself each turn (see
    engine/pet.py), can be consulted for a hint on the current question at the cost of that
    question's score (the cat's first per room is free, OBJECTS.md section 8), and picks money off
    the floor into its own purse until the learner retrieves it (PETS.md). Flavour and help; it
    never grades, and the dungeon never harms it (rule 4)."""

    pos: Point
    name: str = "your kitten"
    species: str = "cat"        # 'cat' | 'dog'; a soloist has no Pet at all (session pet is None)
    carried: int = 0            # coins in the pet's purse, banked to the learner only on retrieval
    # A single non-money stack the dog is fetching (DELVE-0016): it carries one object at a time and
    # sets it down beside the learner. None when empty-pawed or carrying only coins. The cat never
    # touches objects, so this stays None for a cat.
    carried_item: Stack | None = None
    cooldown: int = 0           # turns it leaves money alone after a hand-over, so it wanders off

    def hint_for(self, question) -> int:
        """The option, in the question's own order, the kitten rules out: the first wrong one.
        Narrowing the field is the whole help. On a two-way assertion, ruling one out points
        straight at the answer, which is why consulting costs the question's score."""
        return next(i for i, opt in enumerate(question.options) if not opt.correct)


@dataclass
class Keeper:
    """A teacher standing beside a sealed exit. Rendered as '@', told from the learner by colour
    (bright magenta, NetHack-style; the palette is M8). `kind` is voice-only flavour (wizard,
    shopkeeper, gatekeeper), driving the keeper's teach line, not mechanics. The gate owns the
    keeper's lesson and examination."""

    pos: Point
    name: str
    kind: str = "wizard"
