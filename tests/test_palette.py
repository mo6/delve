"""The 16-colour map palette (M8): the Colour view-model value maps to a curses attribute.

`ui/attrs` is the one bit of the palette testable without a live terminal, because `curses.COLOR_*`
are plain module constants. We assert the mapping is total over the sixteen names, that bright is
base-plus-bold (the portable 16), and that with colour disabled it degrades to the old monochrome
bold/dim look the M2 renderer relied on.
"""

import curses

from delve.session.views import Colour
from delve.ui import attrs


def test_every_colour_maps_to_a_base_and_brightness():
    assert set(attrs._BASE) == set(Colour), "a Colour is missing from the palette"
    for colour, (base, _bright) in attrs._BASE.items():
        assert 0 <= base <= 7, f"{colour} maps to a non-portable base {base}"


def test_bright_variants_are_base_plus_bold():
    for name, (base, bright) in attrs._BASE.items():
        assert bright is name.name.startswith("BRIGHT_")
        plain = Colour[name.name.removeprefix("BRIGHT_")]
        assert attrs._BASE[plain][0] == base   # bright shares its base colour


def test_attr_degrades_to_monochrome_without_colour():
    # init() has not run in this process, so _enabled is False: no colour pair, just attributes.
    assert not attrs._enabled
    assert attrs.attr_for(Colour.WHITE) == 0
    assert attrs.attr_for(Colour.WHITE, dim=True) == curses.A_DIM
    assert attrs.attr_for(Colour.BRIGHT_MAGENTA) == curses.A_BOLD
    assert attrs.attr_for(Colour.BRIGHT_YELLOW, dim=True) == curses.A_BOLD | curses.A_DIM
