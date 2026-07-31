"""The torch (DELVE-0062): a light source that starts lit, burns down over a limited number of
steps, and changes both what is currently seen (`engine/vision.py`) and what stays remembered
(`ChapterRun.discovered`) once the learner has no working one. One spare is scattered per pack
chapter (never the tutorial), a burned-out torch leaves nothing behind, and the ambient prose
(DELVE-0060) is told whether the learner currently has light.
"""

import json
from pathlib import Path

from test_dungeon import _path, _walk

from delve.engine import actions, layout, vision
from delve.engine.items import TORCH, TORCH_DURATION_STEPS, Stack
from delve.engine.world import Direction, Point
from delve.session import backstory
from delve.session.commands import Move, Pickup
from delve.session.launch import load_tutorial
from delve.session.run import new_game, new_run
from delve.session.snapshot import apply_dict, to_dict
from delve.strings import load as load_strings

PILOT = Path(__file__).resolve().parent.parent / "packs" / "security-onboarding"


# -- pure vision function -------------------------------------------------------------------------


def test_lit_tiles_lit_true_matches_the_room():
    chapter = layout.generate(1, 100, 30, 3)
    room = chapter.rooms[0]
    lit = vision.lit_tiles(chapter, room.center)
    assert set(room.tiles()) <= lit


def test_lit_tiles_lit_false_stays_to_the_immediate_neighbourhood():
    chapter = layout.generate(1, 100, 30, 3)
    room = chapter.rooms[0]
    lit = vision.lit_tiles(chapter, room.center, lit=False)
    assert not (set(room.tiles()) <= lit)          # not the whole room
    p = room.center
    assert lit <= {Point(p.x + dx, p.y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)}


def test_keeper_halo_lights_the_keepers_own_tile_and_neighbourhood():
    chapter = layout.generate(1, 100, 30, 3)
    p = Point(chapter.rooms[0].center.x + 3, chapter.rooms[0].center.y)
    halo = vision.keeper_halo(chapter, [p])
    assert p in halo
    assert halo <= {Point(p.x + dx, p.y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)}


def test_keeper_halo_unions_every_keeper_given():
    chapter = layout.generate(1, 100, 30, 3)
    a, b = chapter.rooms[0].center, chapter.rooms[1].center
    halo = vision.keeper_halo(chapter, [a, b])
    assert a in halo
    assert b in halo


# -- starting state ---------------------------------------------------------------------------


def test_fresh_run_starts_with_a_torch_lit_at_full_duration():
    run = new_run(seed=1, cols=100, rows=30, pet_species="none")
    assert run.player.torch_charge == TORCH_DURATION_STEPS
    assert run.has_light


def test_the_lit_torch_shows_in_the_pack_even_though_it_is_not_a_stack():
    run = new_run(seed=1, cols=100, rows=30, pet_species="none")
    rows = run._pack_rows()
    assert any(str(TORCH_DURATION_STEPS) in r for r in rows)
    run.player.torch_charge = 0
    rows = run._pack_rows()
    assert not any("torch" in r.lower() or "fakkel" in r.lower() for r in rows)


def test_the_pack_body_omits_the_torch_line_on_the_tutorial_floor():
    from delve.content.parser import load_pack
    tutorial = load_tutorial("en")
    pack = load_pack(PILOT, "en")
    run = new_game(pack, seed=1, cols=100, rows=30, tutorial=tutorial, pet_species="none")
    assert not run.cur.scored                          # standing on the tutorial floor
    assert run.player.torch_charge == TORCH_DURATION_STEPS
    rows = run._pack_rows()
    assert not any("torch" in r.lower() for r in rows)


# -- torchless vision ---------------------------------------------------------------------------


def _far_corner(run):
    room = next(r for r in run.chapter.rooms if r.contains(run.player.pos))
    corners = sorted(room.interior(), key=lambda p: -(abs(p.x - run.player.pos.x)
                                                       + abs(p.y - run.player.pos.y)))
    return corners[0]


def test_torchless_only_lights_the_immediate_tiles_and_forgets_them():
    run = new_run(seed=1, cols=100, rows=30, pet_species="none")
    run.player.torch_charge = 0
    run.cur.discovered.clear()          # construction already lit the starting room at full torch
    far = _far_corner(run)
    path = _path(run.chapter.grid, run.player.pos, far, blocked=set(run.keepers))
    assert path is not None
    _walk(run, path)
    frame = run.frame()
    far_cell = frame.map.cells[far.y][far.x]
    assert far_cell.glyph == "@"                    # the learner is standing on it: still visible
    assert far not in run.discovered                # but never remembered without a torch

    start = path[0]
    # Stepping away, the tile just left is no longer in the immediate radius and was never
    # remembered: it must render black again, not dimmed.
    back = _path(run.chapter.grid, run.player.pos, start, blocked=set(run.keepers))
    _walk(run, back)
    frame = run.frame()
    left_cell = frame.map.cells[far.y][far.x]
    assert left_cell.glyph == " "
    assert far not in run.discovered


def test_a_lit_torch_room_stays_remembered_after_leaving():
    run = new_run(seed=1, cols=100, rows=30, pet_species="none")
    far = _far_corner(run)
    path = _path(run.chapter.grid, run.player.pos, far, blocked=set(run.keepers))
    _walk(run, path)
    assert far in run.discovered
    back = _path(run.chapter.grid, run.player.pos, path[0], blocked=set(run.keepers))
    _walk(run, back)
    assert far in run.discovered                     # unchanged existing behaviour: still dimmed


def test_relighting_while_only_torchlessly_seeing_a_corner_lights_the_whole_room():
    run = new_run(seed=1, cols=100, rows=30, pet_species="none")
    run.player.torch_charge = 0
    run.cur.discovered.clear()          # construction already lit the starting room at full torch
    far = _far_corner(run)
    path = _path(run.chapter.grid, run.player.pos, far, blocked=set(run.keepers))
    _walk(run, path)
    assert far not in run.discovered
    run.items[run.player.pos] = [Stack(TORCH, 1)]
    run.apply(Pickup())
    assert run.has_light
    assert far in run.discovered                      # the room the learner stood in now lit


# -- keeper candle halo (DELVE-0065) -----------------------------------------------------------


def test_torchless_keeper_halo_lights_the_keepers_own_neighbourhood():
    run = new_run(seed=1, cols=100, rows=30, pet_species="none")
    run.player.torch_charge = 0
    run.cur.discovered.clear()
    keeper_pos = next(iter(run.keepers))
    frame = run.frame()
    keeper_cell = frame.map.cells[keeper_pos.y][keeper_pos.x]
    assert keeper_cell.glyph == "@"                      # the keeper, lit by their own candle
    assert not keeper_cell.dim
    halo_tile = Point(keeper_pos.x + 1, keeper_pos.y)
    assert frame.map.cells[halo_tile.y][halo_tile.x].glyph != " "  # neighbour lit too


def test_torchless_keeper_halo_does_not_persist_into_discovered():
    run = new_run(seed=1, cols=100, rows=30, pet_species="none")
    run.player.torch_charge = 0
    run.cur.discovered.clear()
    keeper_pos = next(iter(run.keepers))
    halo_tile = Point(keeper_pos.x + 1, keeper_pos.y)
    run._observe()
    assert halo_tile not in run.discovered                # mirrors the player's own non-persistence
    assert keeper_pos not in run.discovered


def test_torchless_halo_does_not_light_a_tile_far_from_every_keeper():
    run = new_run(seed=1, cols=100, rows=30, pet_species="none")
    run.player.torch_charge = 0
    far = _far_corner(run)
    near_keeper = any(abs(far.x - k.x) <= 1 and abs(far.y - k.y) <= 1 for k in run.keepers)
    near_player = abs(far.x - run.player.pos.x) <= 1 and abs(far.y - run.player.pos.y) <= 1
    assert not near_keeper and not near_player          # the far corner picked by _far_corner
    lit = run._lit_tiles()
    assert far not in lit


def test_a_lit_torch_room_is_unaffected_by_the_keeper_halo():
    run = new_run(seed=1, cols=100, rows=30, pet_species="none")
    lit = run._lit_tiles()
    assert lit == vision.lit_tiles(run.chapter, run.player.pos, lit=True)


# -- draining and relighting -------------------------------------------------------------------


def _a_free_step(run):
    return next((d, dest) for d in Direction
                for dest in [actions.step(run.chapter, run.player.pos, d)]
                if dest is not None and dest not in run.keepers)


def test_torch_drains_and_relights_automatically_from_a_spare():
    run = new_run(seed=1, cols=100, rows=30, pet_species="none")
    run.player.torch_charge = 1
    run.player.inventory = [Stack(TORCH, 1)]
    d, dest = _a_free_step(run)
    frame = run.apply(Move(d))
    assert run.player.torch_charge == TORCH_DURATION_STEPS   # relit from the spare
    assert run.player.inventory == []                        # the spare is consumed
    assert "gutters out" in frame.messages[-1] or "catches at once" in frame.messages[-1]


def test_torch_runs_dark_with_no_spare_left():
    run = new_run(seed=1, cols=100, rows=30, pet_species="none")
    run.player.torch_charge = 1
    run.player.inventory = []
    d, dest = _a_free_step(run)
    run.apply(Move(d))
    assert run.player.torch_charge == 0
    assert not run.has_light


def test_burned_out_torch_leaves_nothing_behind():
    run = new_run(seed=1, cols=100, rows=30, pet_species="none")
    run.player.torch_charge = 1
    run.player.inventory = []
    d, dest = _a_free_step(run)
    run.apply(Move(d))
    assert run.player.inventory == []                     # no spent-husk item in the pack
    assert all(TORCH.id not in {s.defn.id for s in pile} for pile in run.items.values())


# -- messages ------------------------------------------------------------------------------------


def test_burnout_messages_are_distinct_relit_vs_dark():
    strings = load_strings("en")
    relit = strings("msg.torch_burnout_relit")
    dark = strings("msg.torch_burnout_dark")
    assert relit != dark
    assert "gutters out" in relit and "catches" in relit
    assert "gutters out" in dark and "no light" in dark.lower()


def test_pickup_messages_differ_stowed_vs_lit():
    run = new_run(seed=1, cols=100, rows=30, pet_species="none")
    # Already lit: picking one up stows it.
    run.items[run.player.pos] = [Stack(TORCH, 1)]
    frame = run.apply(Pickup())
    assert "stow" in frame.messages[-1].lower()
    assert run.player.inventory == [Stack(TORCH, 1)]

    # Now torchless: picking one up lights it on the spot, no stow wording.
    run.player.torch_charge = 0
    run.player.inventory = []
    run.items[run.player.pos] = [Stack(TORCH, 1)]
    frame = run.apply(Pickup())
    assert "catches" in frame.messages[-1].lower()
    assert run.player.inventory == []
    assert run.player.torch_charge == TORCH_DURATION_STEPS


# -- Dutch vocabulary -----------------------------------------------------------------------------


def test_torch_display_name_is_dutch_fakkel():
    run = new_run(seed=1, cols=100, rows=30, strings=load_strings("nl"), pet_species="none")
    assert run._torch_noun(1) == "een fakkel"
    assert "fakkel" in run._torch_noun(2)
    assert "toorts" not in run._torch_noun(1) and "toorts" not in run._torch_noun(2)


def test_build_prompt_dutch_instruction_names_fakkel_never_toorts():
    # The instruction itself must name "fakkel" as the word to use, and rules "toorts" out by name
    # (so it necessarily appears once, as the forbidden word) rather than never mentioning it.
    prompt = backstory.build_prompt(pack="Test", dlvl=1, chapter_title="Kamer",
                                    language="Dutch", has_light=True)
    assert "call it 'fakkel'" in prompt
    assert "never the word 'toorts'" in prompt


def test_build_prompt_english_prompt_never_contains_the_dutch_torch_words():
    # a9a25bb scoped the "call it 'fakkel'" clause with prose alone ("if replying in Dutch, ...
    # In English, the word is simply 'torch'"), but a three-model comparison run still showed
    # English replies occasionally parroting the literal word "fakkel" straight out of the
    # prompt, regardless of the conditioning sentence around it. The only durable fix is
    # structural: the Dutch vocabulary words must not appear anywhere in an English-language
    # prompt's text at all, lit or unlit, gated or not.
    for has_light in (True, False):
        prompt = backstory.build_prompt(pack="Test", dlvl=1, chapter_title="Room",
                                        language="English", keeper="Ada", requirement="70%",
                                        has_light=has_light)
        low = prompt.lower()
        assert "fakkel" not in low
        assert "toorts" not in low
        assert "'je'" not in prompt and "'u'" not in prompt
    nudge = backstory.build_nudge_prompt(pack="Test", dlvl=1, chapter_title="Room",
                                         language="English", keeper="Ada")
    assert "fakkel" not in nudge.lower()
    assert "toorts" not in nudge.lower()


# -- ambient prose has_light clause ---------------------------------------------------------------


def test_build_prompt_darkens_only_without_light():
    lit = backstory.build_prompt(pack="Test", dlvl=1, chapter_title="Room", language="English",
                                 has_light=True)
    dark = backstory.build_prompt(pack="Test", dlvl=1, chapter_title="Room", language="English",
                                  has_light=False)
    assert "scarce, flickering torchlight" in lit
    assert "scarce, flickering torchlight" not in dark
    assert "no working light" in dark


# -- scatter ---------------------------------------------------------------------------------------


def test_exactly_one_torch_scattered_per_pack_chapter_and_none_in_tutorial():
    from delve.content.parser import load_pack
    pack = load_pack(PILOT, "en")
    tutorial = load_tutorial("en")
    run = new_game(pack, seed=3, cols=100, rows=30, tutorial=tutorial, pet_species="none")
    n_tut = len(tutorial.chapters)
    for cr in run.chapters[:n_tut]:
        assert all(TORCH.id not in {s.defn.id for s in pile} for pile in cr.items.values())
    for cr in run.chapters[n_tut:]:
        torches = sum(s.count for pile in cr.items.values() for s in pile if s.defn.id == TORCH.id)
        assert torches == 1


# -- snapshot -----------------------------------------------------------------------------------


def test_snapshot_round_trips_torch_charge():
    run = new_run(seed=1, cols=100, rows=30, pet_species="none")
    run.player.torch_charge = 42
    data = json.loads(json.dumps(to_dict(run)))
    run2 = new_run(seed=1, cols=100, rows=30, pet_species="none")
    apply_dict(run2, data)
    assert run2.player.torch_charge == 42


# -- charge preserved across drop/pickup (DELVE-0067) ---------------------------------------------


def test_dropping_a_partially_burned_torch_keeps_its_remaining_charge_not_full_duration():
    from delve.session.commands import Answer, Drop

    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    run.player.torch_charge = 42
    droppables = run._droppable_list()
    run.apply(Drop())
    run.apply(Answer(len(droppables) - 1))          # the lit torch is always the last menu entry
    pile = run.items[run.player.pos]
    torch_stack = next(s for s in pile if s.defn.id == TORCH.id)
    assert torch_stack.charge == 42
    assert torch_stack.charge != TORCH_DURATION_STEPS


def test_picking_up_a_partially_burned_floor_torch_relights_at_its_remembered_charge():
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    run.player.torch_charge = 0
    run.player.inventory = []
    run.items[run.player.pos] = [Stack(TORCH, 1, 37)]
    run.apply(Pickup())
    assert run.player.torch_charge == 37
    assert run.has_light


def test_a_fresh_and_a_partially_burned_torch_on_one_tile_stay_distinct_entries():
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    run.items[run.player.pos] = [Stack(TORCH, 1, None), Stack(TORCH, 1, 10)]
    run.apply(Pickup())                              # two kinds: opens a menu, doesn't merge them
    labels = [label for _, label, _, _ in run._pickables]
    assert len(labels) == 2
    assert labels[0] != labels[1]
    assert any(str(TORCH_DURATION_STEPS) in label for label in labels)   # the fresh one, in full
    assert any("10" in label for label in labels)                        # the partial one


def test_snapshot_round_trips_a_floor_torchs_remembered_charge():
    run = new_run(seed=1, cols=100, rows=30, pet_species="none")
    pos = run.player.pos
    run.items[pos] = [Stack(TORCH, 1, 88)]
    data = json.loads(json.dumps(to_dict(run)))
    run2 = new_run(seed=1, cols=100, rows=30, pet_species="none")
    apply_dict(run2, data)
    assert run2.items[pos] == [Stack(TORCH, 1, 88)]
