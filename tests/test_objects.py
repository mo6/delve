"""Pack-authored objects (OBJECTS.md 1.3.0): item-file parsing, `place:` frontmatter, schema
policy, deterministic scatter, and the closed effect vocabulary (`on_pickup` once, `on_move` each
carried step, `value` as currency). The item *model* (stacks, pickup, drop, money) is phase 1 and
lives in test_items; this covers the pack format built on top of it.

Parsing and schema are unit-level; the effects run headless against `session` the way test_items
drives money, with a pack object placed on the player's tile so no navigation is needed.
"""

from pathlib import Path

import pytest
from test_items import _free_step, _opposite

from delve.content.errors import PackError
from delve.content.parser import parse_item, parse_room
from delve.content.schema import validate_pack
from delve.engine.items import MONEY, ItemDef, Stack, register
from delve.session.commands import Confirm, Digit, Drop, Inventory, Move, Pickup, Select
from delve.session.run import new_game, new_run
from delve.session.snapshot import apply_dict, to_dict
from delve.session.views import AmountView

COCONUT_MD = (
    "---\n"
    "id: coconut-half\n"
    "glyph: (\n"
    "colour: yellow\n"
    "name: coconut half\n"
    "on_pickup: You pick up an empty half-coconut.\n"
    "on_move: You bang the coconuts together. Clip-clop.\n"
    "---\n"
    "Half of a tropical coconut, hollow and dry.\n"
)

COCONUT = ItemDef("coconut-half", "(", "coconut half", "yellow",
                  on_pickup="You pick up an empty half-coconut.",
                  on_move="Clip-clop, clip-clop.")


# -- parsing an item file ------------------------------------------------------------------------


def test_parse_item_reads_the_vocabulary_and_the_look():
    defn = parse_item("coconut-half.md", COCONUT_MD)
    assert defn.id == "coconut-half" and defn.glyph == "(" and defn.colour == "yellow"
    assert defn.name == "coconut half"
    assert defn.on_pickup.startswith("You pick up") and "Clip-clop" in defn.on_move
    assert defn.look == "Half of a tropical coconut, hollow and dry."
    assert defn.carriable and defn.value == 0 and not defn.bulky


def test_a_value_makes_a_currency_that_banks():
    defn = parse_item("token.md", "---\nid: token\nglyph: *\ncolour: cyan\nname: token\n"
                                  "value: 5\n---\nA shiny token.\n")
    assert defn.value == 5 and defn.carriable is False   # currency banks, never an inventory slot


def test_bulky_flag_parses():
    defn = parse_item("crate.md", "---\nid: crate\nglyph: (\ncolour: white\nname: crate\n"
                                  "bulky: true\n---\nA crate.\n")
    assert defn.bulky is True


def test_item_file_requires_the_core_keys():
    with pytest.raises(PackError):
        parse_item("bad.md", "---\nid: x\nglyph: (\n---\nlook\n")   # no name/colour


def test_unknown_item_key_is_a_pack_error():
    with pytest.raises(PackError, match="unknown item key"):
        parse_item("typo.md", "---\nid: x\nglyph: (\ncolour: red\nname: n\non_moove: oops\n---\n")


def test_multi_char_glyph_and_negative_value_are_errors():
    with pytest.raises(PackError, match="single character"):
        parse_item("g.md", "---\nid: x\nglyph: ((\ncolour: red\nname: n\n---\n")
    with pytest.raises(PackError, match="zero or more"):
        parse_item("v.md", "---\nid: x\nglyph: (\ncolour: red\nname: n\nvalue: -1\n---\n")


# -- placement frontmatter -----------------------------------------------------------------------


_ROOM = ("---\nid: r\nplace: {place}\n---\n# T\n\nProse.\n\n## Questions\n\n"
         "### Q?\n\n- [ ] a\n- [x] b\n\n> because\n")


def test_place_parses_ids_counts_and_bare_ids():
    room = parse_room("r.md", _ROOM.format(place="coconut-half x2, usb-stick"))
    assert room.placements == (("coconut-half", 2), ("usb-stick", 1))


def test_place_count_must_be_a_positive_whole_number():
    with pytest.raises(PackError, match="whole number"):
        parse_room("r.md", _ROOM.format(place="coconut-half xtwo"))
    with pytest.raises(PackError, match="one or more"):
        parse_room("r.md", _ROOM.format(place="coconut-half x0"))


def test_a_room_without_place_has_no_placements():
    room = parse_room("r.md", _ROOM.replace("place: {place}\n", ""))
    assert room.placements == ()


# -- schema policy (cross-file) ------------------------------------------------------------------


def _write_pack(root: Path, item_fm: str, place: str) -> None:
    """A tiny two-locale pack with one item file and one room placing it, for schema checks."""
    for loc in ("en", "nl"):
        base = root / loc
        (base / "items").mkdir(parents=True)
        (base / "c").mkdir(parents=True)
        (base / "pack.md").write_text(
            "---\nid: p\ntitle: T\ndifficulty: standard\nscroll: S\n---\nintro\n")
        (base / "c" / "chapter.md").write_text("---\nid: c\ntitle: C\n---\nintro\n")
        (base / "c" / "01-r.md").write_text(_ROOM.format(place=place))
        (base / "items" / "thing.md").write_text(item_fm)


def _messages(issues) -> str:
    return " | ".join(i.message for i in issues)


def test_schema_flags_a_bad_glyph_and_colour(tmp_path):
    _write_pack(tmp_path, "---\nid: thing\nglyph: Z\ncolour: teal\nname: n\n---\nlook\n",
                place="thing")
    msgs = _messages(validate_pack(tmp_path))
    assert "object-class char" in msgs and "unknown colour" in msgs


def test_schema_flags_a_place_naming_no_defined_kind(tmp_path):
    _write_pack(tmp_path, "---\nid: thing\nglyph: (\ncolour: red\nname: n\n---\nlook\n",
                place="ghost")
    assert "no items/ file" in _messages(validate_pack(tmp_path))


def test_schema_flags_the_reserved_money_id(tmp_path):
    _write_pack(tmp_path, "---\nid: money\nglyph: (\ncolour: red\nname: n\n---\nlook\n",
                place="money")
    assert "reserved" in _messages(validate_pack(tmp_path))


def test_a_well_formed_object_pack_validates_clean(tmp_path):
    _write_pack(tmp_path, "---\nid: thing\nglyph: (\ncolour: red\nname: n\n"
                          "on_pickup: hi\n---\nA thing.\n", place="thing x2")
    assert [i for i in validate_pack(tmp_path) if i.level == "error"] == []


# -- scatter (session) ---------------------------------------------------------------------------


def test_scatter_is_deterministic_and_lands_in_the_room(tmp_path):
    _write_pack(tmp_path, "---\nid: thing\nglyph: (\ncolour: red\nname: n\n---\nlook\n",
                place="thing x2")
    from delve.content.parser import load_pack
    pack = load_pack(tmp_path, "en")

    a = new_game(pack, seed=7, cols=100, rows=30, pet_species="none")
    b = new_game(pack, seed=7, cols=100, rows=30, pet_species="none")
    placed_a = {p: [(s.defn.id, s.count) for s in pile] for p, pile in a.items.items()}
    placed_b = {p: [(s.defn.id, s.count) for s in pile] for p, pile in b.items.items()}
    assert placed_a == placed_b                          # same seed, same scatter

    piles = [pile for pile in a.items.values() if pile[0].defn.id == "thing"]
    assert len(piles) == 1 and piles[0][0].count == 2    # one stack of two, as placed


# -- effects (session) ---------------------------------------------------------------------------


def test_on_pickup_fires_once_per_kind():
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    run.items[run.player.pos] = [Stack(COCONUT, 1)]

    frame = run.apply(Pickup())
    assert any("empty half-coconut" in m for m in frame.messages)

    run.items[run.player.pos] = [Stack(COCONUT, 1)]      # a second, into an already-holding hand
    frame = run.apply(Pickup())
    assert not any("empty half-coconut" in m for m in frame.messages)   # not re-announced


_PAIR = ItemDef("coconut-half", "(", "coconut half", "yellow", on_move="Clip-clop.",
                on_move_min=2, plural="coconut halves")
_CLAPPER = ItemDef("clapper", "(", "clapper", "yellow", on_move="You bang them. Clip-clop.",
                   on_move_short="Clip-clop.", plural="clappers")


def _shuttle_clops(run, steps: int) -> list[str]:
    """Step back and forth `steps` times, then return the clip-clop lines actually posted, in order.
    Reads the run's message log rather than each frame's visible line, which lingers for the message
    TTL and would double-count a single utterance across the turns it stays up."""
    d, _ = _free_step(run)
    for i in range(steps):
        run.apply(Move(d if i % 2 == 0 else _opposite(d)))
    return [m for m in run.messages if "clop" in m.lower()]


def test_on_move_is_ambient_not_every_step():
    """The clip-clop speaks on only some steps, not every one (a coin flip on the flavour rng)."""
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    run.player.inventory = [Stack(_PAIR, 2)]
    clops = _shuttle_clops(run, 40)
    assert clops                                         # it does clip-clop
    assert len(clops) < 40                               # but not on every single step


def test_on_move_needs_the_minimum_count():
    """A lone coconut half is silent over any number of steps; the pair bangs (on_move_min)."""
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    run.player.inventory = [Stack(_PAIR, 1)]
    assert not _shuttle_clops(run, 40)                   # one half: nothing to bang against

    run.player.inventory = [Stack(_PAIR, 2)]
    assert _shuttle_clops(run, 40)                       # two: it speaks


def test_on_move_abbreviates_after_a_few_full_lines():
    """The first few utterances are the full line; then it drops to the short form."""
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    run.player.inventory = [Stack(_CLAPPER, 1)]
    clops = _shuttle_clops(run, 80)
    assert clops[:3] == ["You bang them. Clip-clop."] * 3   # full while it is still novel
    assert "Clip-clop." in clops[3:]                        # then abbreviated
    assert "You bang them. Clip-clop." not in clops[3:]     # and never the long line again


def test_on_pickup_flavour_is_count_aware():
    """Picking up more than one uses the authored plural flavour, with the number word; one uses the
    singular. The flavour stands in for the plain 'You pick up' line, not alongside it."""
    coco = ItemDef("coconut-half", "(", "coconut half", "yellow", plural="coconut halves",
                   on_pickup="You pick up an empty half-coconut. Suspiciously horse-like.",
                   on_pickup_plural="You pick up {count} empty half-coconuts. Suspiciously "
                                    "horse-like.")
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    run.items[run.player.pos] = [Stack(coco, 2)]

    run.apply(Pickup())
    run.apply(Digit(2))
    frame = run.apply(Confirm())
    assert frame.messages == ["You pick up two empty half-coconuts. Suspiciously horse-like."]


def test_carry_flavour_yields_to_a_real_message():
    """Ambient flavour never overrides a substantive line: stepping onto coins shows the collect,
    not the clip-clop, even while carrying the pair."""
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    run.player.inventory = [Stack(_PAIR, 2)]
    d, dest = _free_step(run)
    run.items[dest] = [Stack(MONEY, 25)]
    frame = run.apply(Move(d))
    assert frame.messages == [run.strings("item.collect", coins="25 coins")]


def test_stepping_onto_an_object_names_it():
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    d, dest = _free_step(run)
    run.items[dest] = [Stack(_PAIR, 1)]
    frame = run.apply(Move(d))
    assert any("a coconut half" in m and "lying here" in m for m in frame.messages)


def test_pickup_asks_how_many_and_messages_read_grammatically():
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    run.items[run.player.pos] = [Stack(_PAIR, 2)]

    assert isinstance(run.apply(Pickup()).overlay, AmountView)   # a stack of two asks how many
    run.apply(Digit(2))
    frame = run.apply(Confirm())
    assert any("two coconut halves" in m for m in frame.messages)   # plural, number word

    frame = run.apply(Inventory())                       # DELVE-0081: drop from Info/Pack now
    idx = next(i for i, label in enumerate(frame.overlay.pack_rows) if "coconut half" in label)
    while frame.overlay.pack_selected != idx:
        frame = run.apply(Select(1))
    run.apply(Drop())
    run.apply(Digit(1))
    frame = run.apply(Confirm())
    assert any("You drop a coconut half" in m for m in frame.messages)   # singular, article


def test_a_valued_kind_auto_collects_like_money():
    token = ItemDef("token", "*", "token", "cyan", carriable=False, value=5)
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    d, dest = _free_step(run)
    run.items[dest] = [Stack(token, 3)]                  # 3 tokens worth 5 each

    before = run.player.gold
    run.apply(Move(d))
    assert run.player.gold == before + 15 and dest not in run.items


# -- snapshot ------------------------------------------------------------------------------------


def test_a_carried_pack_object_round_trips():
    register(COCONUT)                                    # new_game does this for a real pack
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    run.player.inventory = [Stack(COCONUT, 2)]
    step = to_dict(run)

    restored = new_run(seed=99, cols=100, rows=30, pet_species="none")
    apply_dict(restored, step)
    assert restored.player.inventory == [Stack(COCONUT, 2)]


# -- the shipped packs' objects (OBJECTS.md section 13) ------------------------------------------

_PACKS = Path(__file__).resolve().parent.parent / "packs"
_SHIPPED_OBJECTS = {
    "holy-grail": {
        "coconut-half", "duck", "shrubbery", "holy-hand-grenade", "unladen-swallow",
    },
    "security-onboarding": {          # one object per room, all twelve rooms
        "urgent-memo", "spear-letter", "suspicious-attachment",
        "sticky-note", "vault-keyring", "hardware-token",
        "classification-stamp", "open-share-link", "usb-stick",
        "visitor-badge", "oracle-transcript", "report-slip",
    },
    "ethics-of-ai": {
        "black-box", "principles-card", "do-no-harm-plaque", "signed-ledger",
        "weighing-scales",
    },
    "friends-nap-partners": {
        "coffee", "maid-of-honor-bag", "smelly-cat-lyric", "die-hard-tape", "nap-pillow",
    },
}


@pytest.mark.parametrize("name,expected", sorted(_SHIPPED_OBJECTS.items()))
@pytest.mark.parametrize("loc", ("en", "nl"))
def test_shipped_packs_scatter_their_objects(name, expected, loc):
    """Each shipped pack defines its object in both locales, and `new_game` actually scatters it on
    the floor and registers it so a stack round-trips. Guards the section-13 content itself, not
    just the mechanism."""
    from delve.content.parser import load_pack
    from delve.engine.items import by_id

    pack = load_pack(_PACKS / name, loc)
    assert {d.id for d in pack.items} == expected
    run = new_game(pack, seed=7, cols=100, rows=30, pet_species="none")
    # `run.items` is only the current chapter; an object may sit in a deeper one, so scan them all.
    # Money and the torch are both engine-owned, not pack content (DELVE-0062), so neither belongs
    # to a pack's own expected object set.
    scattered = {s.defn.id for cr in run.chapters for pile in cr.items.values()
                 for s in pile if s.defn.id not in ("money", "torch")}
    assert scattered == expected                         # placed, on the floor, ready to pick up
    assert all(by_id(i) is not None for i in expected)   # registered, so it persists
