"""Objects, phase 1 (OBJECTS.md 1.1.0): the item model, money auto-collect, pickup/drop, the
inventory panel, the snapshot round-trip, and the move of MCQ answer keys from letters to numbers.

Driven headless as Commands against `session`, plus a few unit checks on the engine item model
and the ui keymap. Money and carriable objects are placed by fixtures here; no pack ships them yet.
"""

import json
from pathlib import Path

from test_dungeon import _pass_room

from delve import strings as strings_pkg
from delve.content.parser import load_pack
from delve.engine import actions
from delve.engine.items import (
    MONEY,
    TORCH,
    TORCH_DURATION_STEPS,
    ItemDef,
    Stack,
    can_place,
    merged,
    taken,
)
from delve.engine.world import Direction
from delve.session.commands import (
    Answer,
    Backspace,
    Confirm,
    Digit,
    Dismiss,
    Drop,
    FocusRow,
    Help,
    Inventory,
    Move,
    Pickup,
    Select,
    SubTabCycle,
    TabCycle,
)
from delve.session.launch import load_tutorial
from delve.session.run import _LIT_TORCH_ID, new_game, new_run
from delve.session.snapshot import apply_dict, to_dict
from delve.session.views import AmountView, InfoTab, InfoView, MenuView, TextBlock
from delve.ui import keys

PILOT = Path(__file__).resolve().parent.parent / "packs" / "security-onboarding"

COCONUT = ItemDef("coconut-half", "(", "coconut half", "yellow")


def _free_step(run):
    """A direction the player can step, and the tile it lands on (never a keeper's)."""
    for d in Direction:
        dest = actions.step(run.chapter, run.player.pos, d)
        if dest is not None and dest not in run.keepers:
            return d, dest
    raise AssertionError("player is boxed in")


def _opposite(d: Direction) -> Direction:
    return next(o for o in Direction if o.delta.x == -d.delta.x and o.delta.y == -d.delta.y)


# -- engine item model ---------------------------------------------------------------------------


def test_stacks_merge_by_kind():
    pile = merged(merged([], Stack(MONEY, 10)), Stack(MONEY, 5))
    assert pile == [Stack(MONEY, 15)]


def test_taken_splits_and_empties():
    took, rest = taken([Stack(MONEY, 100)], "money", 30)
    assert took == Stack(MONEY, 30) and rest == [Stack(MONEY, 70)]
    took, rest = taken([Stack(MONEY, 30)], "money", 100)
    assert took == Stack(MONEY, 30) and rest == []          # the kind is dropped when emptied


def test_merged_keeps_differently_charged_torches_as_distinct_stacks():
    # DELVE-0067: charge is per-unit state, so two torches at different remaining charge must not
    # fold into one indistinguishable count, unlike every other kind (whose charge is always None).
    pile = merged([Stack(TORCH, 1, 40)], Stack(TORCH, 1, 90))
    assert pile == [Stack(TORCH, 1, 40), Stack(TORCH, 1, 90)]
    # Equal charge (including two untouched, charge=None stacks) still merges normally.
    pile = merged([Stack(TORCH, 1, 40)], Stack(TORCH, 1, 40))
    assert pile == [Stack(TORCH, 2, 40)]
    pile = merged([Stack(TORCH, 1)], Stack(TORCH, 1))
    assert pile == [Stack(TORCH, 2)]


def test_taken_can_filter_by_charge():
    pile = [Stack(TORCH, 1, 40), Stack(TORCH, 1, 90)]
    took, rest = taken(pile, TORCH.id, 1, charge=90)
    assert took == Stack(TORCH, 1, 90) and rest == [Stack(TORCH, 1, 40)]
    # The default (no charge given) is charge-blind, taking the first match, as before this issue.
    took, rest = taken(pile, TORCH.id, 1)
    assert took == Stack(TORCH, 1, 40) and rest == [Stack(TORCH, 1, 90)]


def test_bulky_will_not_share_a_tile():
    boulder = ItemDef("boulder", "`", "boulder", "white", bulky=True)
    assert can_place([], boulder) is True                    # a bulky item wants an empty tile
    assert can_place([Stack(MONEY, 5)], boulder) is False    # not onto an occupied one
    assert can_place([Stack(boulder, 1)], MONEY) is False     # and nothing stacks onto it


# -- money ---------------------------------------------------------------------------------------


def test_stepping_onto_coins_banks_them():
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    d, dest = _free_step(run)
    run.items[dest] = [Stack(MONEY, 25)]
    before = run.player.gold
    frame = run.apply(Move(d))
    assert run.player.pos == dest
    assert run.player.gold == before + 25
    assert dest not in run.items                             # collected, not left lying
    assert "25 coins" in frame.messages[-1]


def test_drop_some_coins_then_walk_back_over_them():
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    run.player.gold = 100
    pos = run.player.pos

    assert isinstance(run.apply(Drop()).overlay, MenuView)   # the drop menu
    field = run.apply(Answer(0))                             # coins: >1, so an amount field opens
    assert isinstance(field.overlay, AmountView)
    run.apply(Digit(3))
    assert run.apply(Digit(0)).overlay.typed == "30"         # typed 3 then 0
    run.apply(Confirm())

    assert run.player.gold == 70
    assert run.items[pos] == [Stack(MONEY, 30)]

    d, _ = _free_step(run)
    run.apply(Move(d))                                       # step off; coins stay put
    assert run.items[pos] == [Stack(MONEY, 30)]
    run.apply(Move(_opposite(d)))                            # and back onto them
    assert run.player.pos == pos
    assert run.player.gold == 100                            # 70 + 30, recollected


# -- carriable objects: pickup, inventory, drop --------------------------------------------------


def test_pickup_inventory_and_drop_one():
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    run.items[run.player.pos] = [Stack(COCONUT, 2)]

    # A stack of two asks how many (a single kind goes straight to the amount field); take both.
    assert isinstance(run.apply(Pickup()).overlay, AmountView)
    run.apply(Digit(2))
    run.apply(Confirm())
    assert run.player.inventory == [Stack(COCONUT, 2)]
    assert run.player.pos not in run.items

    inv = run.apply(Inventory())
    assert isinstance(inv.overlay, InfoView)
    assert inv.overlay.active == 0 and inv.overlay.tabs[0].key == "pack"
    assert "coconut half (2)" in " ".join(inv.overlay.pack_rows)
    run.apply(Dismiss())

    run.apply(Drop())
    assert isinstance(run.apply(Answer(0)).overlay, AmountView)   # 2 held -> an amount field
    run.apply(Digit(1))
    run.apply(Confirm())
    assert run.player.inventory == [Stack(COCONUT, 1)]
    assert run.items[run.player.pos] == [Stack(COCONUT, 1)]


def test_drop_with_nothing_to_drop_says_so():
    # A fresh run starts with a lit torch, itself droppable (a playtesting fix), so "nothing to
    # drop" now requires it burned out too, not just an empty pack and no gold.
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    run.player.torch_charge = 0
    frame = run.apply(Drop())
    assert frame.overlay is None
    assert "nothing" in frame.messages[-1].lower()


def test_drop_with_only_one_thing_to_drop_skips_the_menu_and_drops_it_at_once():
    # DELVE-0072: mirrors `_pickup`'s own single-kind shortcut. A lone single-unit item is the
    # only droppable thing (torch burned out, no gold), so Drop should act immediately, no menu.
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    run.player.torch_charge = 0
    run.player.inventory = [Stack(COCONUT, 1)]
    frame = run.apply(Drop())
    assert frame.overlay is None
    assert run.player.inventory == []
    assert run.items[run.player.pos] == [Stack(COCONUT, 1)]


def test_drop_with_only_a_multi_count_pile_still_asks_how_many():
    # Same shortcut, but the lone droppable thing is a pile of more than one, so the amount field
    # still opens (mirroring pickup asking "how many" for a single multi-count kind), skipping
    # straight past the drop menu rather than skipping the amount question too.
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    run.player.torch_charge = 0
    run.player.gold = 50
    frame = run.apply(Drop())
    assert isinstance(frame.overlay, AmountView)


def test_the_lit_torch_appears_last_in_the_drop_menu_and_can_be_dropped():
    # A playtesting request: the currently-burning torch is never a `Stack` (DELVE-0062), so
    # unlike every other carried thing it never appeared in the drop menu, with no way to reach
    # the unlit ambient scene deliberately. Appended last (not first) so it never shifts an
    # existing item's menu number, since a lit torch is present from turn one of most real runs.
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    run.items[run.player.pos] = [Stack(COCONUT, 1)]
    run.apply(Pickup())
    assert run.player.torch_charge > 0 and run.has_light

    droppables = run._droppable_list()
    assert droppables[-1][1] == run.strings("item.torch_lit_menu", n=run.player.torch_charge)
    frame = run.apply(Drop())
    assert [item.text for item in frame.overlay.items][-1] == \
        run.strings("item.torch_lit_menu", n=run.player.torch_charge)

    frame = run.apply(Answer(len(droppables) - 1))     # the last menu entry: the lit torch
    assert run.player.torch_charge == 0
    assert not run.has_light
    assert run.items[run.player.pos] == [Stack(TORCH, 1)]
    assert any("torch" in m.lower() for m in frame.messages)


def test_the_drop_menus_torch_label_matches_every_other_rows_lowercase_unpunctuated_style():
    # DELVE-0071: the drop menu's other rows are bare lowercase noun phrases with no leading
    # article and no trailing period, so the lit-torch entry gets its own wording styled the same.
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    label = run._droppable_list()[-1][1]
    assert label[0].islower()
    assert not label.endswith(".")


def test_the_pack_tab_gives_the_torch_and_coins_a_real_description():
    # DELVE-0073: money and the torch used to render as a bare plain-text line with no
    # description, unlike every pack-authored item's bold title plus its own `look`.
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    run.player.gold = 35
    torch_body = run._pack_detail_body(0)
    torch_label = run.strings("item.torch_lit_menu", n=run.player.torch_charge)
    assert torch_body[0].text == f"{torch_label}\n{run.strings('item.torch_look')}"
    assert torch_body[0].spans[0] == (torch_label, True)
    coin_body = run._pack_detail_body(1)
    coin_label = run._coins(35)
    assert coin_body[0].text == f"{coin_label}\n{run.strings('item.money_look')}"
    assert coin_body[0].spans[0] == (coin_label, True)


def test_the_dropped_torch_relights_on_pickup():
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    run.player.torch_charge = 0
    run.items[run.player.pos] = [Stack(TORCH, 1)]
    run.apply(Pickup())
    assert run.player.torch_charge == TORCH_DURATION_STEPS
    assert run.has_light


def test_the_tutorial_floor_never_offers_the_lit_torch_to_drop():
    # `has_light` reads True on the tutorial floor regardless of charge (DELVE-0062); offering to
    # drop it there would claim an effect (darkening the scene) that doesn't actually happen.
    run = _pilot_game(skip_tutorial=False, pet_species="none")
    assert not run.cur.scored
    assert all(_LIT_TORCH_ID != def_id for def_id, _, _, _ in run._droppable_list())


def _inv_block(run, name):
    # DELVE-0075: the Pack tab's list and the focused row's own description show together, so
    # selecting the matching row is enough; no separate confirm step to reach its detail body.
    inv = run.apply(Inventory())
    assert isinstance(inv.overlay, InfoView)
    idx = next(i for i, label in enumerate(inv.overlay.pack_rows) if name in label)
    while inv.overlay.pack_selected != idx:
        inv = run.apply(Select(1))
    return inv.overlay.body[0]


def test_inventory_reflows_a_wrapped_look_into_a_paragraph():
    # DELVE-0029: a look wrapped at the author's source width must reflow, not keep its line breaks.
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    memo = ItemDef("memo", "?", "urgent memo", "yellow",
                   look="A printed email that wants you hurried. The sender almost looks\n"
                        "right, the link\n"
                        "almost looks right, and the deadline is always one hour from whenever.")
    run.player.inventory = [Stack(memo, 1)]
    block = _inv_block(run, "urgent memo")
    assert "almost looks right, the link almost looks right" in block.text  # soft wraps joined
    assert "looks\nright" not in block.text                                 # no inherited break
    # The bold item name is still its own line above the body, with no blank row between (the
    # single '\n' hard break in the spans), and the name stays strong.
    assert block.spans[0] == (_label_of(run, memo), True)
    assert block.spans[1][0].startswith("\n") and block.spans[1][1] is False


def test_inventory_preserves_a_paragraph_break_in_a_look():
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    stone = ItemDef("stone", "*", "smooth stone", "white",
                    look="First paragraph, wrapped\nacross two lines.\n\nSecond paragraph, alone.")
    run.player.inventory = [Stack(stone, 1)]
    block = _inv_block(run, "smooth stone")
    assert "wrapped across two lines." in block.text     # soft wrap within a paragraph is joined
    assert "\n\nSecond paragraph, alone." in block.text  # the real blank-line break is kept


def _label_of(run, defn):
    return run._label(defn.id, defn.name, 1)


# -- Pack tab list-plus-description layout (DELVE-0069, DELVE-0075) -------------------------------


def test_pack_opens_with_the_list_and_the_first_rows_description_together():
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    run.player.gold = 35
    memo = ItemDef("memo", "?", "urgent memo", "yellow", look="A hurried, suspicious email.")
    run.player.inventory = [Stack(memo, 1)]
    inv = run.apply(Inventory())
    assert isinstance(inv.overlay, InfoView)
    torch_label = run.strings("item.torch_lit_menu", n=run.player.torch_charge)
    coin_label = run._coins(35)
    assert inv.overlay.pack_rows == [torch_label, coin_label, "urgent memo"]
    assert inv.overlay.pack_selected == 0                # the lit torch, listed first
    assert run.strings("item.torch_look") in inv.overlay.body[0].text
    assert "A hurried, suspicious email." not in " ".join(inv.overlay.pack_rows)


def test_moving_the_selection_updates_the_description_with_no_confirm_step():
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    memo = ItemDef("memo", "?", "urgent memo", "yellow", look="A hurried, suspicious email.")
    run.player.inventory = [Stack(memo, 1)]
    run.apply(Inventory())
    moved = run.apply(Select(1))                        # torch (0) -> the memo (1)
    assert moved.overlay.pack_selected == 1
    assert moved.overlay.pack_rows                       # the list is still showing, not replaced
    assert "A hurried, suspicious email." in moved.overlay.body[0].text
    assert moved.overlay.body[0].spans[0] == ("urgent memo", True)


def test_money_and_the_lit_torch_show_a_generic_description_when_selected():
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    run.player.gold = 12
    inv = run.apply(Inventory())
    assert inv.overlay.pack_selected == 0                # the lit torch, listed first
    assert inv.overlay.body[0].text.strip()
    assert run.strings("item.torch_look") in inv.overlay.body[0].text
    coin = run.apply(Select(1))                          # torch (0) -> gold (1)
    assert coin.overlay.body[0].text.strip()
    assert run.strings("item.money_look") in coin.overlay.body[0].text


def test_an_empty_pack_still_shows_the_empty_message_not_an_empty_list():
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    run.player.torch_charge = 0
    inv = run.apply(Inventory())
    assert not inv.overlay.pack_rows
    assert inv.overlay.pack_selected == -1
    assert inv.overlay.body == [TextBlock("para", run.strings("item.inv_empty"))]


def test_pack_row_selection_wraps_both_directions():
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    run.player.gold = 5
    inv = run.apply(Inventory())
    assert inv.overlay.pack_selected == 0
    up = run.apply(Select(-1))
    assert up.overlay.pack_selected == len(up.overlay.pack_rows) - 1
    down = run.apply(Select(1))
    assert down.overlay.pack_selected == 0


def test_dismiss_closes_the_pack_panel_directly_with_no_detail_step():
    # DELVE-0075: the list and the focused row's description show together at all times now, so
    # there is no separate detail mode for Esc to back out of first, unlike DELVE-0069's original
    # toggle; one Esc always closes the whole panel, same as every other tab.
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    run.apply(Inventory())
    closed = run.apply(Dismiss())
    assert closed.overlay is None


# -- snapshot ------------------------------------------------------------------------------------


def test_snapshot_round_trips_gold_and_floor_money():
    run = new_run(seed=1, cols=100, rows=30, pet_species="none")
    run.player.gold = 42
    pos = run.player.pos
    run.items[pos] = [Stack(MONEY, 7)]

    data = json.loads(json.dumps(to_dict(run)))              # through JSON, as the store keeps it
    run2 = new_run(seed=1, cols=100, rows=30, pet_species="none")
    apply_dict(run2, data)

    assert run2.player.gold == 42
    assert run2.items[pos] == [Stack(MONEY, 7)]


# -- MCQ answers are numbers, not letters (OBJECTS.md) -------------------------------------------


def test_map_keys_pick_up_drop_inventory():
    assert keys.walk_command(ord(",")) == Pickup()
    assert keys.walk_command(ord("d")) == Drop()
    assert keys.walk_command(ord("i")) == Inventory()


# -- the i panel's tab strip (DELVE-0040) ---------------------------------------------------------


def test_info_panel_defaults_to_pack_and_cycles_tabs():
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    inv = run.apply(Inventory())
    assert [t.key for t in inv.overlay.tabs] == \
        ["pack", "scoring", "grader", "status", "messages"]
    assert inv.overlay.active == 0                       # Pack, unasked

    frame = run.apply(TabCycle(1))
    assert frame.overlay.active == 1                     # Scoring: its own body, not Pack's
    assert frame.overlay.body != inv.overlay.body

    frame = run.apply(TabCycle(1))
    assert frame.overlay.active == 2                     # Grader

    frame = run.apply(TabCycle(1))
    assert frame.overlay.active == 3                     # Status

    frame = run.apply(TabCycle(1))
    assert frame.overlay.active == 4                     # Messages

    frame = run.apply(TabCycle(1))
    assert frame.overlay.active == 0                      # wraps back to Pack

    frame = run.apply(TabCycle(-1))
    assert frame.overlay.active == 4                      # Shift-Tab wraps the other way


def test_info_panel_tab_cycle_is_ignored_outside_the_panel():
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    frame = run.apply(TabCycle(1))
    assert frame.overlay is None                          # no panel open: nothing to cycle


def test_info_panel_esc_closes_from_any_tab():
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    run.apply(Inventory())
    run.apply(TabCycle(1))
    frame = run.apply(Dismiss())
    assert frame.overlay is None


def test_info_panel_reopens_on_pack_not_the_last_tab_visited():
    # A playtesting reversal of DELVE-0040's original "sticky across opens" choice: navigating to
    # Status, closing, and reopening used to land back on Status, which read as broken navigation.
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    run.apply(Inventory())
    run.apply(TabCycle(1))
    run.apply(TabCycle(1))
    frame = run.apply(TabCycle(1))
    assert frame.overlay.active == 3                      # Status, mid-panel navigation
    run.apply(Dismiss())
    frame = run.apply(Inventory())
    assert frame.overlay.active == 0                      # back to Pack on the fresh open


def test_help_panel_reopens_on_keys_not_the_last_tab_visited():
    # The same reversal as Info, for DELVE-0028's help panel.
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    run.apply(Help())
    frame = run.apply(TabCycle(1))
    assert frame.overlay.active == 1                      # Objectives, mid-panel navigation
    run.apply(Help())                                      # closes (second `?`)
    frame = run.apply(Help())                              # reopens
    assert frame.overlay.active == 0                       # back to Keys on the fresh open


def test_tab_and_shift_tab_cycle_the_info_panel():
    view = InfoView(tabs=[], active=0, body=[])
    assert keys.panel_command(ord("\t"), view) == TabCycle(1)
    assert keys.panel_command(keys.curses.KEY_BTAB, view) == TabCycle(-1)


def test_arrow_keys_also_cycle_the_info_panel():
    # DELVE-0041: left/right cycle tabs the same as Shift-Tab/Tab, matching PromptView's
    # horizontal-choice convention.
    view = InfoView(tabs=[], active=0, body=[])
    assert keys.panel_command(keys.curses.KEY_RIGHT, view) == TabCycle(1)
    assert keys.panel_command(keys.curses.KEY_LEFT, view) == TabCycle(-1)


def test_info_panel_has_a_fixed_title_before_the_tabs():
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    inv = run.apply(Inventory())
    assert inv.overlay.title == "Info"


# -- the Scoring tab's bars (DELVE-0042/0043) ------------------------------------------------


def _pilot_game(skip_tutorial=True, **kw):
    pack = load_pack(PILOT, "en")
    tutorial = load_tutorial("en")
    strings = strings_pkg.load("en")
    return new_game(pack, seed=7, cols=100, rows=30, name="Ada",
                    strings=strings, tutorial=tutorial, skip_tutorial=skip_tutorial, **kw)


def _bar_blocks(body):
    return [b for b in body if b.kind == "bar"]


def test_scoring_body_shows_na_before_any_room_is_passed():
    run = _pilot_game(pet_species="none")
    body = run._scoring_now_body()
    bars = _bar_blocks(body)
    assert body[0].text == "Chapters"
    assert any(frac is None and tail == "n/a" for _, frac, tail in (b.bar for b in bars))
    assert not any(frac is not None for _, frac, tail in (b.bar for b in bars if b.bar[0] != "HP"))
    assert any(label == "HP" for label, _, _ in (b.bar for b in bars))


def test_scoring_body_shows_a_percentage_once_a_gate_is_passed():
    run = _pilot_game(pet_species="none")
    gate = next(iter(run.gates.values()))
    _pass_room(run, gate)
    body = run._scoring_now_body()
    bars = _bar_blocks(body)
    label, frac, tail = next(b.bar for b in bars if b.bar[0] == run.cur.title)
    assert frac == gate.passed_score
    assert tail == f"{round(gate.passed_score * 100)}%"
    # The other rooms in the same chapter are still unattempted.
    assert any(f is None for _, f, _ in (b.bar for b in bars))


def test_scoring_body_omits_the_unscored_tutorial_floor():
    run = _pilot_game(skip_tutorial=False, pet_species="none")
    assert run.chapters[0].scored is False
    body = run._scoring_now_body()
    labels = [b.bar[0] for b in _bar_blocks(body)]
    assert run.chapters[0].title not in labels


def test_scoring_body_hp_row_reflects_current_and_max_hp():
    run = _pilot_game(pet_species="none")
    run.player.hp = run.player.max_hp - 1
    body = run._scoring_now_body()
    label, frac, tail = next(b.bar for b in _bar_blocks(body) if b.bar[0] == "HP")
    assert tail == f"{run.player.hp}/{run.player.max_hp}"
    assert frac == run.player.hp / run.player.max_hp


def test_info_panel_scoring_tab_renders_the_bars():
    run = _pilot_game(pet_species="none")
    run.apply(Inventory())
    frame = run.apply(TabCycle(1))                    # Scoring
    assert frame.overlay.active == 1
    assert frame.overlay.subtabs and frame.overlay.active_sub == 0     # defaults to Now
    assert frame.overlay.body == run._scoring_now_body()


# -- the Scoring > Rooms sub-tab, the room pass map (DELVE-0055) ----------------------------


def test_room_glyph_is_sealed_when_never_sat():
    from delve.session.run import _room_glyph

    run = _pilot_game(pet_species="none")
    gate = next(iter(run.gates.values()))
    assert gate.sittings == 0 and not gate.passed
    assert _room_glyph(gate) == "·"


def test_room_glyph_is_sat_when_attempted_but_not_passed():
    from delve.session.run import _room_glyph

    run = _pilot_game(pet_species="none")
    gate = next(iter(run.gates.values()))
    gate.sittings = 1
    assert _room_glyph(gate) == "░"


def test_room_glyph_is_ok_when_passed_after_a_retry():
    from delve.session.run import _room_glyph

    run = _pilot_game(pet_species="none")
    gate = next(iter(run.gates.values()))
    gate.passed = True
    gate.attempts_used = 1
    assert _room_glyph(gate) == "▒"


def test_room_glyph_is_clear_when_passed_on_the_first_sitting():
    from delve.session.run import _room_glyph

    run = _pilot_game(pet_species="none")
    gate = next(iter(run.gates.values()))
    gate.passed = True
    gate.attempts_used = 0
    assert _room_glyph(gate) == "█"


def test_scoring_rooms_body_groups_by_chapter_with_dlvl_labels():
    # Condensed into one block via `_condensed` (DELVE-0059): its own lines are its `spans`.
    run = _pilot_game(pet_species="none")
    body = run._scoring_rooms_body()
    lines = body[0].text.split("\n")
    rows = [line for line in lines if line.startswith("Dlvl")]
    assert [r.split()[1] for r in rows] == [str(cr.chapter.dlvl)
                                            for cr in run.chapters if cr.scored]
    # one glyph per room in the chapter's own gate order
    first_chapter = next(cr for cr in run.chapters if cr.scored)
    first_row = rows[0]
    glyphs = first_row.split("  ")[-1]
    assert len(glyphs) == len(first_chapter.gates)


def test_scoring_rooms_body_omits_the_unscored_tutorial_floor():
    run = _pilot_game(skip_tutorial=False, pet_species="none")
    assert run.chapters[0].scored is False
    body = run._scoring_rooms_body()
    rows = [b.text for b in body if b.text.startswith("Dlvl 0")]
    assert not rows


def test_scoring_rooms_body_ends_with_a_legend_line():
    run = _pilot_game(pet_species="none")
    body = run._scoring_rooms_body()
    lines = body[0].text.split("\n")
    assert lines[-1] == run.strings("item.rooms_legend")
    assert "·" in lines[-1] and "░" in lines[-1]
    assert "▒" in lines[-1] and "█" in lines[-1]


def test_sub_tab_cycle_wraps_between_now_and_rooms_on_scoring():
    run = _pilot_game(pet_species="none")
    run.apply(Inventory())
    run.apply(TabCycle(1))                              # Scoring, sub-tab Now
    frame = run.apply(SubTabCycle(1))
    assert frame.overlay.active_sub == 1                 # Rooms
    assert frame.overlay.body == run._scoring_rooms_body()
    frame = run.apply(SubTabCycle(1))
    assert frame.overlay.active_sub == 0                  # wraps back to Now
    frame = run.apply(SubTabCycle(-1))
    assert frame.overlay.active_sub == 1                  # Shift wraps the other way


def test_sub_tab_cycle_is_a_no_op_on_tabs_without_subtabs():
    run = _pilot_game(pet_species="none")
    run.apply(Inventory())                                # Pack, no sub-tabs
    frame = run.apply(SubTabCycle(1))
    assert not frame.overlay.subtabs and frame.overlay.active_sub == 0
    run.apply(TabCycle(2))                                # Grader
    frame = run.apply(SubTabCycle(1))
    assert not frame.overlay.subtabs
    run.apply(TabCycle(1))                                # Status
    frame = run.apply(SubTabCycle(1))
    assert not frame.overlay.subtabs


def test_sub_tab_resets_to_now_when_leaving_and_returning_to_scoring():
    run = _pilot_game(pet_species="none")
    run.apply(Inventory())
    run.apply(TabCycle(1))                                # Scoring
    run.apply(SubTabCycle(1))                              # Rooms
    run.apply(TabCycle(1))                                 # Grader
    frame = run.apply(TabCycle(-1))                        # back to Scoring
    assert frame.overlay.active_sub == 0                   # reset to Now, not left on Rooms


def test_sub_tab_cycle_ignored_outside_the_panel():
    run = _pilot_game(pet_species="none")
    frame = run.apply(SubTabCycle(1))
    assert frame.overlay is None


def test_bracket_keys_cycle_the_info_panel_sub_tabs():
    view = InfoView(tabs=[], active=0, body=[])
    assert keys.panel_command(ord("]"), view) == SubTabCycle(1)
    assert keys.panel_command(ord("["), view) == SubTabCycle(-1)


# -- arrow-key row focus between the tab rows (DELVE-0056) ----------------------------------


def test_focus_row_down_moves_focus_to_the_sub_tab_row_on_scoring():
    run = _pilot_game(pet_species="none")
    run.apply(Inventory())
    run.apply(TabCycle(1))                                # Scoring, primary row focused
    frame = run.apply(FocusRow(1))
    assert frame.overlay.sub_focus is True
    assert frame.overlay.active_sub == 0                  # unchanged, only focus moved


def test_focus_row_up_moves_focus_back_to_the_primary_row():
    run = _pilot_game(pet_species="none")
    run.apply(Inventory())
    run.apply(TabCycle(1))                                # Scoring
    run.apply(FocusRow(1))                                 # focus: sub
    frame = run.apply(FocusRow(-1))
    assert frame.overlay.sub_focus is False


def test_focus_row_down_is_a_no_op_on_tabs_without_sub_tabs():
    run = _pilot_game(pet_species="none")
    frame = run.apply(Inventory())                         # Pack, no sub-tabs
    assert frame.overlay.sub_focus is False
    frame = run.apply(FocusRow(1))
    assert frame.overlay.sub_focus is False
    run.apply(TabCycle(2))                                 # Grader
    frame = run.apply(FocusRow(1))
    assert frame.overlay.sub_focus is False


def test_focus_row_ignored_outside_the_panel():
    run = _pilot_game(pet_species="none")
    frame = run.apply(FocusRow(1))
    assert frame.overlay is None


def test_focus_resets_to_primary_when_the_primary_tab_changes_away_and_back():
    run = _pilot_game(pet_species="none")
    run.apply(Inventory())
    run.apply(TabCycle(1))                                 # Scoring
    run.apply(FocusRow(1))                                  # focus: sub
    run.apply(TabCycle(1))                                  # Grader
    frame = run.apply(TabCycle(-1))                         # back to Scoring
    assert frame.overlay.sub_focus is False                 # reset, not left focused on sub


def test_left_right_cycle_the_primary_tab_when_the_primary_row_is_focused():
    run = _pilot_game(pet_species="none")
    run.apply(Inventory())
    frame = run.apply(TabCycle(1))                          # Scoring, primary row focused
    assert frame.overlay.sub_focus is False
    frame = run.apply(TabCycle(1))                          # simulates a left/right press: Grader
    assert frame.overlay.active == 2


def test_left_right_cycle_the_sub_tab_when_the_sub_tab_row_is_focused():
    run = _pilot_game(pet_species="none")
    run.apply(Inventory())
    run.apply(TabCycle(1))                                  # Scoring
    run.apply(FocusRow(1))                                   # focus: sub
    frame = run.apply(SubTabCycle(1))                        # simulates a left/right press
    assert frame.overlay.active == 1                         # still on Scoring
    assert frame.overlay.active_sub == 1                     # Rooms


def test_up_down_keys_map_to_focus_row():
    view = InfoView(tabs=[], active=0, body=[])
    assert keys.panel_command(keys.curses.KEY_UP, view) == FocusRow(-1)
    assert keys.panel_command(keys.curses.KEY_DOWN, view) == FocusRow(1)


def test_tab_and_arrows_route_to_the_focused_row():
    subtabs_view = InfoView(tabs=[], active=0, body=[], subtabs=[InfoTab("now", "Now")],
                            active_sub=0, sub_focus=True)
    assert keys.panel_command(ord("\t"), subtabs_view) == SubTabCycle(1)
    assert keys.panel_command(keys.curses.KEY_BTAB, subtabs_view) == SubTabCycle(-1)
    assert keys.panel_command(keys.curses.KEY_RIGHT, subtabs_view) == SubTabCycle(1)
    assert keys.panel_command(keys.curses.KEY_LEFT, subtabs_view) == SubTabCycle(-1)

    primary_view = InfoView(tabs=[], active=0, body=[], subtabs=[InfoTab("now", "Now")],
                            active_sub=0, sub_focus=False)
    assert keys.panel_command(ord("\t"), primary_view) == TabCycle(1)
    assert keys.panel_command(keys.curses.KEY_RIGHT, primary_view) == TabCycle(1)


def test_scoring_hint_carries_the_row_focus_chord_only_on_scoring():
    run = _pilot_game(pet_species="none")
    run.apply(Inventory())                                 # Pack
    assert run.frame().hint == run.strings("hint.inventory")
    frame = run.apply(TabCycle(1))                          # Scoring
    assert frame.hint == run.strings("hint.inventory_sub")
    frame = run.apply(TabCycle(1))                          # Grader: no sub-tabs
    assert frame.hint == run.strings("hint.inventory")


# -- the Status tab (DELVE-0044) -------------------------------------------------------------


def test_status_body_shows_version_pack_and_locale_and_omits_grader_by_default():
    import delve

    run = _pilot_game(pet_species="none")
    body = run._status_body()
    texts = [b.text for b in body]
    assert any(delve.__version__ in t for t in texts)
    assert any(run.pack.title in t for t in texts)
    assert any(run.strings.lang in t for t in texts)
    assert not any("Grader" in t or "Nakijker" in t for t in texts)


def test_status_body_includes_the_grader_model_and_host_when_one_is_configured():
    from delve.assess.grader import LLMGrader
    from delve.session.grading import ThreadedGrader

    class FakeClient:
        model = "qwen2.5:3b"
        host = "http://localhost:11434"

    run = _pilot_game(pet_species="none", grader_runner=ThreadedGrader(LLMGrader(FakeClient())))
    body = run._status_body()
    assert any("qwen2.5:3b" in b.text and "localhost:11434" in b.text for b in body)


def test_status_body_terminal_row_carries_only_a_label_for_ui_to_fill_in():
    # session never reads stdscr (rule 2): the last line is a bare label until ui fills in the
    # live size (`_fill_status_size` splices it into the sole body block's last line now, a
    # playtesting fix that closed the tab's last remaining gap).
    run = _pilot_game(pet_species="none")
    body = run._status_body()
    assert len(body) == 1
    last_line = body[0].text.split("\n")[-1]
    assert last_line == run.strings("item.status_size")
    assert "x" not in last_line                  # no digits x digits baked in yet


def test_status_body_condenses_every_row_including_the_size_one():
    """Every Status row, including the terminal-size one, folds into a single block via
    `_condensed`: no gap anywhere in the tab any more. `ui/windows.py:_fill_status_size` splices
    the live size into that block's last line at paint time instead of swapping a whole block."""
    run = _pilot_game(pet_species="none")
    body = run._status_body()
    assert len(body) == 1
    assert body[0].kind == "plain" and body[0].spans
    lines = body[0].text.split("\n")
    assert lines[-1] == run.strings("item.status_size")  # the size row stays last


def test_info_panel_status_tab_renders_the_body():
    run = _pilot_game(pet_species="none")
    run.apply(Inventory())
    frame = run.apply(TabCycle(3))                    # Status
    assert frame.overlay.active == 3
    assert frame.overlay.body == run._status_body()


# -- the Grader tab (DELVE-0054) ---------------------------------------------------------------


def test_grader_body_is_a_single_offline_line_with_no_model_configured():
    run = _pilot_game(pet_species="none")
    body = run._grader_body()
    assert len(body) == 1
    assert "no model configured" in body[0].text.lower()


def test_grader_body_shows_no_grade_yet_before_any_call():
    from delve.assess.grader import LLMGrader
    from delve.session.grading import ThreadedGrader

    class FakeClient:
        model = "qwen2.5:3b"
        host = "http://localhost:11434"

    run = _pilot_game(pet_species="none", grader_runner=ThreadedGrader(LLMGrader(FakeClient())))
    body = run._grader_body()
    texts = [b.text for b in body]
    assert any("qwen2.5:3b" in t and "localhost:11434" in t for t in texts)
    assert any("no grade yet" in t.lower() for t in texts)
    assert any("in 0" in t.lower() and "out 0" in t.lower() for t in texts)


def test_grader_body_reports_tokens_and_warm_latency_after_a_confident_call():
    from delve.assess.grader import LLMGrader
    from delve.assess.llm import ChatMetrics, ChatReply

    class FakeClient:
        model = "qwen2.5:3b"
        host = "http://localhost:11434"

        def chat(self, prompt):
            return ChatReply(
                text='{"verdict": "ACCEPT", "confidence": 0.9}',
                metrics=ChatMetrics(total_duration_ms=520, load_duration_ms=0,
                                     prompt_tokens=180, completion_tokens=40))

    grader = LLMGrader(FakeClient())
    from delve.assess.question import Question
    grader.grade_text(Question(prompt="p", explanation="e", accept=("x",)), "x")

    run = _pilot_game(pet_species="none")
    run._grader_runner = type("R", (), {"grader": grader})()
    body = run._grader_body()
    texts = [b.text for b in body]
    assert any("520" in t and "warm" in t.lower() for t in texts)
    assert any("in 180" in t.lower() and "out 40" in t.lower() and "llm 1" in t.lower()
               for t in texts)


def test_info_panel_grader_tab_renders_the_body():
    run = _pilot_game(pet_species="none")
    run.apply(Inventory())
    frame = run.apply(TabCycle(2))                    # Grader
    assert frame.overlay.active == 2
    assert frame.overlay.body == run._grader_body()


# -- the Grader tab's latency sparkline (DELVE-0077) ---------------------------------------------


def test_grader_body_omits_the_latency_line_below_two_calls():
    from delve.assess.grader import LLMGrader
    from delve.assess.llm import ChatMetrics, ChatReply

    class FakeClient:
        model = "qwen2.5:3b"
        host = "http://localhost:11434"

        def chat(self, prompt):
            return ChatReply(
                text='{"verdict": "ACCEPT", "confidence": 0.9}',
                metrics=ChatMetrics(total_duration_ms=520, load_duration_ms=0,
                                     prompt_tokens=180, completion_tokens=40))

    grader = LLMGrader(FakeClient())
    from delve.assess.question import Question
    grader.grade_text(Question(prompt="p", explanation="e", accept=("x",)), "x")

    run = _pilot_game(pet_species="none")
    run._grader_runner = type("R", (), {"grader": grader})()
    body = run._grader_body()
    texts = [b.text for b in body]
    assert not any("latency" in t.lower() and "(calls)" in t.lower() for t in texts)


def test_grader_body_shows_the_latency_line_from_two_calls_on():
    from delve.assess.grader import LLMGrader
    from delve.assess.llm import ChatMetrics, ChatReply

    class FakeClient:
        model = "qwen2.5:3b"
        host = "http://localhost:11434"

        def __init__(self):
            self.ms = 100

        def chat(self, prompt):
            self.ms += 100
            return ChatReply(
                text='{"verdict": "ACCEPT", "confidence": 0.9}',
                metrics=ChatMetrics(total_duration_ms=self.ms, load_duration_ms=0,
                                     prompt_tokens=10, completion_tokens=5))

    grader = LLMGrader(FakeClient())
    from delve.assess.question import Question
    q = Question(prompt="p", explanation="e", accept=("x",))
    grader.grade_text(q, "x")
    grader.grade_text(q, "x")

    run = _pilot_game(pet_species="none")
    run._grader_runner = type("R", (), {"grader": grader})()
    body = run._grader_body()
    texts = [b.text for b in body]
    assert any("(calls)" in t.lower() for t in texts)


def test_mcq_is_answered_by_number_not_letter():
    from delve.session.views import MenuItem

    menu = MenuView(prompt="?", items=[MenuItem("1", "a"), MenuItem("2", "b"), MenuItem("3", "c")])
    assert keys.panel_command(ord("1"), menu) == Answer(0)
    assert keys.panel_command(ord("3"), menu) == Answer(2)
    assert keys.panel_command(ord("a"), menu) is None        # letters no longer answer


def test_amount_field_keys():
    view = AmountView(prompt="Drop how many?", typed="5", maximum=10)
    assert keys.panel_command(ord("3"), view) == Digit(3)
    assert keys.panel_command(ord("\n"), view) == Confirm(True)
    assert keys.panel_command(127, view) == Backspace()
    assert keys.panel_command(27, view) == Dismiss()
    assert keys.panel_command(ord("l"), view) is None        # letters do not type into the field
