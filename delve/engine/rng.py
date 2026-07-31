"""The one seeded RNG. Centralised so a run is reproducible tile-for-tile from its seed
(PLAN.md section 7): everything random in the engine draws from here, never from `random`
directly.
"""

import random


class Rng:
    def __init__(self, seed: int):
        self._r = random.Random(seed)

    def randint(self, a: int, b: int) -> int:
        """Inclusive on both ends, like random.randint."""
        return self._r.randint(a, b)

    def choice(self, seq):
        return self._r.choice(seq)

    def shuffle(self, seq: list) -> None:
        """In-place, like random.shuffle. Used to shuffle MCQ options reproducibly."""
        self._r.shuffle(seq)
