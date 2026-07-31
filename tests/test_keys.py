"""Arrow-key-only navigation (DELVE-0038): walk_command's key -> Command mapping had no direct
test before this; NetHack's hjkl/yubn letters used to work here and must now be unbound.
"""

import curses

from delve.engine.world import Direction
from delve.session.commands import Move
from delve.ui import keys


def test_arrow_keys_move_in_the_four_cardinal_directions():
    assert keys.walk_command(curses.KEY_UP) == Move(Direction.N)
    assert keys.walk_command(curses.KEY_DOWN) == Move(Direction.S)
    assert keys.walk_command(curses.KEY_LEFT) == Move(Direction.W)
    assert keys.walk_command(curses.KEY_RIGHT) == Move(Direction.E)


def test_nethack_letters_no_longer_move():
    for letter in "hjklyubn":
        assert keys.walk_command(ord(letter)) is None
