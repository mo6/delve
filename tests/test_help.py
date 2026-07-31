"""The `?` help overlay (DELVE-0028): a Keys tab (the context command catalogue) and an
Objectives tab (static pack/chapter/room/progress facts only, since DELVE-0060 moved the optional
LLM passage off this tab and onto a room-entry toast, tested in test_room_toast.py), opened and
closed free of any turn cost, stacking over whatever was already open and handing it back
unchanged. Driven headless as Commands against `session`, the same way test_dungeon.py plays a
whole run.
"""

from test_dungeon import _approach, _pass_room

from delve.session.commands import Confirm, Consult, Dismiss, Drop, Help, Inventory, TabCycle, Talk
from delve.session.run import new_run
from delve.session.views import HelpView, InfoView, MenuView, PromptView, TextView
from delve.strings import load as load_strings
from delve.ui import keys

# -- opening and closing -------------------------------------------------------------------------


def test_help_opens_from_walking_and_lists_keys_free_of_turn_cost():
    run = new_run(seed=1, cols=100, rows=30)
    turn = run.turn
    frame = run.apply(Help())
    assert isinstance(frame.overlay, HelpView)
    assert frame.overlay.tabs[frame.overlay.active].key == "keys"
    assert any("i:" in b.text for b in frame.overlay.body)
    # 'p' is retired (a playtesting request): the message log lives in the Info panel now.
    assert not any("p:" in b.text for b in frame.overlay.body)
    assert run.turn == turn


def test_second_question_mark_or_esc_closes_help_with_no_turn_cost():
    run = new_run(seed=1, cols=100, rows=30)
    run.apply(Help())
    turn = run.turn
    frame = run.apply(Help())
    assert frame.overlay is None
    assert run.turn == turn

    run.apply(Help())
    frame = run.apply(Dismiss())
    assert frame.overlay is None


def test_help_stacks_over_a_lesson_and_dismiss_returns_to_it():
    run = new_run(seed=1, cols=100, rows=30)
    gate = run.gates["phishing"]
    _approach(run, gate.keeper.pos)
    lesson = run.apply(Talk())
    assert isinstance(lesson.overlay, TextView)
    frame = run.apply(Help())
    assert isinstance(frame.overlay, HelpView)
    frame = run.apply(Dismiss())
    assert isinstance(frame.overlay, TextView)   # back to exactly the lesson, not dismissed
    assert run.active is gate                    # the lesson's own state was never touched


def test_help_stacks_over_the_backpack_and_esc_returns_to_it():
    run = new_run(seed=1, cols=100, rows=30)
    inv = run.apply(Inventory())
    assert isinstance(inv.overlay, InfoView)
    run.apply(TabCycle(1))                       # move off the default tab
    frame = run.apply(Help())
    assert isinstance(frame.overlay, HelpView)
    frame = run.apply(Dismiss())
    assert isinstance(frame.overlay, InfoView)
    assert frame.overlay.tabs[frame.overlay.active].key != "pack"   # the tab move survived


# -- Keys matches context -------------------------------------------------------------------------


def test_keys_tab_lists_lesson_keys_not_walking_keys_over_a_lesson():
    run = new_run(seed=1, cols=100, rows=30)
    _approach(run, run.gates["phishing"].keeper.pos)
    run.apply(Talk())
    frame = run.apply(Help())
    joined = "\n".join(b.text for b in frame.overlay.body)
    assert "Space:" in joined
    assert "t:" not in joined        # walking-only (talk) must not leak into the lesson context


def test_keys_tab_lists_question_keys_over_an_examination():
    run = new_run(seed=1, cols=100, rows=30)
    gate = run.gates["phishing"]
    _approach(run, gate.keeper.pos)
    run.apply(Talk())
    run.apply(Confirm(True))                     # -> the examination
    assert isinstance(run._overlay, (MenuView, PromptView))
    frame = run.apply(Help())
    joined = "\n".join(b.text for b in frame.overlay.body)
    assert "@:" in joined                        # the pet consult, reachable from a question
    assert "t:" not in joined


def test_keys_tab_lists_backpack_keys_over_the_info_panel():
    run = new_run(seed=1, cols=100, rows=30)
    run.apply(Inventory())
    frame = run.apply(Help())
    joined = "\n".join(b.text for b in frame.overlay.body)
    assert "Tab" in joined
    assert ",:" not in joined                    # pickup is a walking key, not an info-panel one


# -- tab cycling ----------------------------------------------------------------------------------


def test_tab_cycle_switches_between_keys_and_objectives():
    run = new_run(seed=1, cols=100, rows=30)
    frame = run.apply(Help())
    assert frame.overlay.tabs[frame.overlay.active].key == "keys"
    frame = run.apply(TabCycle(1))
    assert frame.overlay.tabs[frame.overlay.active].key == "objectives"
    frame = run.apply(TabCycle(1))
    assert frame.overlay.tabs[frame.overlay.active].key == "keys"   # wraps


# -- Objectives: static facts ----------------------------------------------------------------------


def test_objectives_shows_pack_chapter_progress_and_next_keeper():
    run = new_run(seed=1, cols=100, rows=30)
    run.apply(Help())
    frame = run.apply(TabCycle(1))
    joined = "\n".join(b.text for b in frame.overlay.body)
    assert "The Sorting Office" in joined
    assert "0" in joined and str(len(run.chapter.rooms)) in joined
    assert run.gates["phishing"].keeper.name in joined


def test_objectives_omits_the_keeper_line_once_every_gate_in_the_chapter_is_passed():
    run = new_run(seed=1, cols=100, rows=30)
    _pass_room(run, run.gates["phishing"])
    run.apply(Help())
    frame = run.apply(TabCycle(1))
    joined = "\n".join(b.text for b in frame.overlay.body)
    assert run.gates["phishing"].keeper.name not in joined


# -- the ? / @ rebinding --------------------------------------------------------------------------


def test_question_mark_opens_help_on_a_question_and_at_sign_still_consults():
    run = new_run(seed=1, cols=100, rows=30, pet_species="dog")
    gate = run.gates["phishing"]
    _approach(run, gate.keeper.pos)
    run.apply(Talk())
    run.apply(Confirm(True))
    assert isinstance(run._overlay, (MenuView, PromptView))

    assert keys.panel_command(ord("?"), run._overlay) == Help()
    assert keys.panel_command(ord("@"), run._overlay) == Consult()

    run.apply(Consult())
    assert gate.hints_used == 1                  # consulting still costs the room a hint (0011)


def test_walk_command_binds_question_mark_to_help():
    assert keys.walk_command(ord("?")) == Help()


# -- locale ---------------------------------------------------------------------------------------


def test_help_renders_in_dutch_with_the_same_entry_set_as_english():
    en_run = new_run(seed=1, cols=100, rows=30, strings=load_strings("en"))
    nl_run = new_run(seed=1, cols=100, rows=30, strings=load_strings("nl"))
    en_frame = en_run.apply(Help())
    nl_frame = nl_run.apply(Help())
    assert len(en_frame.overlay.body) == len(nl_frame.overlay.body)
    assert en_frame.overlay.tabs[0].label != nl_frame.overlay.tabs[0].label
    joined_nl = "\n".join(b.text for b in nl_frame.overlay.body)
    assert "Beweeg door de kamer" in joined_nl        # the Dutch explanation, not the English one


# -- app.py's pagination-key routing (space/'-' page a HelpView like an InfoView) ------------------


def test_drop_menu_still_reachable_after_help_is_dismissed():
    """A regression guard for `_close_help`: dismissing help over the drop menu must hand back the
    exact same droppables list, not a cleared one (`_close_item` must never run for help)."""
    run = new_run(seed=1, cols=100, rows=30)
    run.player.gold = 5
    frame = run.apply(Drop())
    assert isinstance(frame.overlay, MenuView)
    run.apply(Help())
    frame = run.apply(Dismiss())
    assert isinstance(frame.overlay, MenuView)
    assert run._droppables


# -- ? over the scroll (win) screen ----------------------------------------------------------------


def test_help_opens_and_closes_over_the_scroll_screen():
    """Before this fix, `RunState.apply`'s early-return branch for the scroll overlay swallowed
    every command but Confirm/Dismiss, so `?` did nothing at all on the win screen even though the
    help catalogue claims that context is reachable."""
    run = new_run(seed=1, cols=100, rows=30)
    run._overlay = run._scroll_overlay()
    run._overlay_kind = "scroll"

    frame = run.apply(Help())
    assert isinstance(frame.overlay, HelpView)

    frame = run.apply(Dismiss())
    assert isinstance(frame.overlay, TextView)   # back to the scroll itself, not dismissed
    assert run._overlay_kind == "scroll"


def test_confirm_still_puts_the_scroll_down_when_help_is_not_open():
    run = new_run(seed=1, cols=100, rows=30)
    run._overlay = run._scroll_overlay()
    run._overlay_kind = "scroll"
    frame = run.apply(Confirm(True))
    assert frame.overlay is None


# -- the hint line advertises ? outside the bare walking default too -------------------------------


def test_hint_line_still_advertises_help_while_carrying_gold():
    run = new_run(seed=1, cols=100, rows=30)
    run.player.gold = 5
    frame = run.frame()
    assert frame.hint == run.strings("hint.carrying")
    assert "?" in frame.hint


def test_hint_line_advertises_help_beside_a_keeper():
    run = new_run(seed=1, cols=100, rows=30)
    _approach(run, run.gates["phishing"].keeper.pos)
    frame = run.frame()
    assert frame.hint == run.strings("hint.talk", first="Ada")
    assert "?" in frame.hint


def test_walking_hint_names_info_not_the_retired_messages_key():
    # DELVE-0068: 'p' was retired when the message log moved into the Info panel (DELVE-0063),
    # but the walking hint line still named it and never mentioned 'i'.
    run = new_run(seed=1, cols=100, rows=30)
    frame = run.frame()
    assert "Info: i" in frame.hint
    assert "Messages: p" not in frame.hint
