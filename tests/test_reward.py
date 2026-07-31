"""Objects, phase 2 (OBJECTS.md 1.1.0 section 7): the on-pass money reward.

A passed room drops coins on a random interior tile of the keeper's room (DELVE-0015, was the far
corner), scaled by how well the room was passed; the learner collects them by walking over them, so
`$` moves in real play.
Driven end to end against the real pilot pack (whose pack.md sets a default `reward:` and whose
shopkeeper room overrides it), reusing the dungeon test's play-through helpers. Also the parser's
`reward` frontmatter, and the win screen's wealth line.
"""

from pathlib import Path

import pytest
from test_dungeon import _approach, _clear_chapter, _correct_index, _pass_room, _stand_on

from delve.content.errors import PackError
from delve.content.parser import load_pack, parse_pack_md, parse_room
from delve.engine.items import MONEY, Stack
from delve.engine.world import TileKind
from delve.progress.scrolls import format_money
from delve.session.commands import Answer, Confirm, Descend, Talk
from delve.session.launch import outcome_lines
from delve.session.run import new_game
from delve.session.snapshot import apply_dict, to_dict
from delve.session.views import MenuView, PromptView
from delve.strings import load as load_strings

PILOT = Path(__file__).resolve().parent.parent / "packs" / "security-onboarding"

_ROOM = ("---\nid: r\nreward: {reward}\n---\n# T\n\nProse.\n\n## Questions\n\n"
         "### Q?\n\n- [ ] a\n- [x] b\n\n> because\n")
_PACK = "---\nid: p\ntitle: T\ndifficulty: standard\nscroll: S\nreward: {reward}\n---\nintro\n"


# -- the reward frontmatter (parser) -------------------------------------------------------------


def test_room_reward_parses_and_pack_default_parses():
    assert parse_room("r.md", _ROOM.format(reward=50)).reward == 50
    assert parse_room("r.md", _ROOM.replace("reward: {reward}\n", "")).reward is None  # inherits
    _values, _intro, reward = parse_pack_md("p.md", _PACK.format(reward=15))
    assert reward == 15
    _values, _intro, reward = parse_pack_md("p.md", _PACK.replace("reward: {reward}\n", ""))
    assert reward == 0                                   # absent means the pack pays nothing


def test_negative_reward_is_a_pack_error():
    with pytest.raises(PackError):
        parse_room("r.md", _ROOM.format(reward=-5))
    with pytest.raises(PackError):
        parse_pack_md("p.md", _PACK.format(reward=-1))


# -- the drop, in real play ----------------------------------------------------------------------


def test_passing_a_room_drops_the_reward_on_a_random_interior_tile():
    pack = load_pack_en()
    run = new_game(pack, seed=99, cols=100, rows=30)
    gate = next(iter(run.gates.values()))
    _pass_room(run, gate)                               # a perfect play, so the full reward
    assert gate.rewarded
    # The reward is coins; a placed pack object may share the floor, so isolate the money.
    coins = {p: [s for s in pile if s.defn.id == MONEY.id] for p, pile in run.items.items()}
    coins = {p: stacks for p, stacks in coins.items() if stacks}
    assert gate.door_pos not in coins                  # not on the exit, where nothing races you
    (coin_pos, stacks), = coins.items()                # exactly one coin pile, in the room
    assert stacks == [Stack(MONEY, pack.reward)]       # round(20 * 1.0)
    room = next(r for r in run.chapter.rooms if r.contains(gate.keeper.pos))
    # A walkable interior tile of the keeper's room, not on a keeper and not the farthest corner
    # the reward used to file itself into (DELVE-0015).
    assert room.contains(coin_pos)
    assert run.chapter.grid.walkable(coin_pos.x, coin_pos.y)
    assert coin_pos not in run.keepers
    farthest = max(room.interior(),
                   key=lambda p: abs(p.x - gate.door_pos.x) + abs(p.y - gate.door_pos.y))
    assert coin_pos != farthest


def test_reward_scales_with_the_passing_score():
    pack = load_pack_en()
    run = new_game(pack, seed=99, cols=100, rows=30)
    gate = next(iter(run.gates.values()))
    _approach(run, gate.keeper.pos)
    frame = run.apply(Talk())
    frame = run.apply(Confirm(True))                   # reading -> the first question
    missed = False
    while isinstance(frame.overlay, (MenuView, PromptView)):
        correct = _correct_index(run.active)
        n = len(run.active.display_options())
        choice = correct if missed else (correct + 1) % n   # miss the first question, pass the rest
        missed = True
        frame = run.apply(Answer(choice))
        frame = run.apply(Confirm(True))
    assert gate.passed
    assert gate.passed_score == 0.75                   # 3 of 4
    coins = [s for pile in run.items.values() for s in pile if s.defn.id == MONEY.id]
    assert len(coins) == 1                             # one coin pile; a placed object is not money
    assert coins[0].count == round(pack.reward * 0.75)  # 15, the reward scaled by the score


def test_reward_is_paid_once_not_on_re_reading():
    pack = load_pack_en()
    run = new_game(pack, seed=99, cols=100, rows=30)
    gate = next(iter(run.gates.values()))
    _pass_room(run, gate)
    _approach(run, gate.keeper.pos)                    # may walk over the coins; that is collection
    before_items = {p: list(v) for p, v in run.items.items()}
    before_gold = run.player.gold
    # Re-read the passed room with `t`; passing is final, so no second reward is dropped.
    run.apply(Talk())
    run.apply(Confirm(True))
    assert run.items == before_items and run.player.gold == before_gold


def _reward_pos(run):
    """The single tile holding a MONEY pile (the on-pass reward), or None before it is paid."""
    for p, pile in run.items.items():
        if any(s.defn.id == MONEY.id for s in pile):
            return p
    return None


def test_reward_tile_is_deterministic_across_rebuilds():
    # Same identity (seed, size, pack) rebuilt twice lands the coins on the identical tile, so a
    # run stays regenerable tile-for-tile (DELVE-0015, the maintainer story).
    pack = load_pack_en()
    tiles = []
    for _ in range(2):
        run = new_game(pack, seed=99, cols=100, rows=30, pet_species="none")
        gate = next(iter(run.gates.values()))
        _pass_room(run, gate)
        tiles.append(_reward_pos(run))
    assert tiles[0] is not None and tiles[0] == tiles[1]


def test_reward_tile_survives_a_resume_from_snapshot():
    # A run resumed from its snapshot pays the reward on the same tile as the original: the draw is
    # seeded from the run seed and the stable room id, both of which the rebuild restores.
    pack = load_pack_en()
    control = new_game(pack, seed=99, cols=100, rows=30, pet_species="none")
    gate = next(iter(control.gates.values()))
    _pass_room(control, gate)
    original = _reward_pos(control)

    fresh = new_game(pack, seed=99, cols=100, rows=30, pet_species="none")
    resumed = new_game(pack, seed=99, cols=100, rows=30, pet_species="none")
    apply_dict(resumed, to_dict(fresh))                # resume a run that has not yet passed a room
    gate = next(iter(resumed.gates.values()))
    _pass_room(resumed, gate)
    assert _reward_pos(resumed) == original


def test_rewards_collected_or_left_conserve_the_total():
    pack = load_pack_en()
    run = new_game(pack, seed=99, cols=100, rows=30, name="Ada")
    for i in range(len(pack.chapters)):
        _clear_chapter(run)
        if i < len(pack.chapters) - 1:
            _stand_on(run, TileKind.STAIRS_DOWN)
            run.apply(Descend())
    _stand_on(run, TileKind.PEDESTAL)
    assert run.finished
    # At a perfect play every reward is its full amount; the shopkeeper's room overrides default.
    expected = sum(r.reward if r.reward is not None else pack.reward
                   for ch in pack.chapters for r in ch.rooms)
    assert expected == 11 * 20 + 50
    floor = sum(s.count for cr in run.chapters for pile in cr.items.values()
                for s in pile if s.defn.id == MONEY.id)   # coins only; a pack object is not money
    purse = run.pet.carried if run.pet is not None else 0
    # Every coin is banked (walked over), still on a floor, or in the pet's purse; none is lost.
    assert run.player.gold + floor + purse == expected


# -- the win screen shows wealth -----------------------------------------------------------------


def test_win_screen_reports_wealth_when_gold_was_earned():
    pack = load_pack_en()
    run = new_game(pack, seed=99, cols=100, rows=30)
    run.player.gold = 270
    lines = outcome_lines(run)
    assert any("$270" in ln for ln in lines)


def test_win_screen_omits_wealth_when_none_was_earned():
    pack = load_pack_en()
    run = new_game(pack, seed=99, cols=100, rows=30)
    run.player.gold = 0
    assert not any("$" in ln for ln in outcome_lines(run))


def test_format_money_is_locale_data():
    assert format_money(1200) == "$1,200"
    nl = load_strings("nl").fmt
    assert format_money(1200, nl) == "€ 1.200"          # euro, a space, a dot for thousands


def load_pack_en():
    return load_pack(PILOT, "en")
