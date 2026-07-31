"""The M2 vertical slice, driven end to end as Commands against `session` with no terminal.

Walk to Ada, read the lesson, sit the examination, and watch the sealed wall become a door;
then walk through it into room 2. This is the go/no-go moment (PLAN.md section 11), and its
whole point is to be replayable: everything here is a list of commands and assertions on frames.
"""

from collections import deque

import pytest

from delve.assess.examination import DIFFICULTIES
from delve.engine.world import Direction, Point, TileKind
from delve.session.commands import Answer, Confirm, Dismiss, Move, Talk
from delve.session.run import new_run
from delve.session.views import MenuView, PromptView, TextView

_CARD = {
    Point(0, -1): Direction.N,
    Point(0, 1): Direction.S,
    Point(1, 0): Direction.E,
    Point(-1, 0): Direction.W,
}


def _path(grid, start, goal, blocked=frozenset()):
    prev = {start: None}
    q = deque([start])
    while q:
        cur = q.popleft()
        if cur == goal:
            break
        for d in _CARD:
            nxt = Point(cur.x + d.x, cur.y + d.y)
            if nxt not in prev and nxt not in blocked and grid.walkable(nxt.x, nxt.y):
                prev[nxt] = cur
                q.append(nxt)
    if goal not in prev:
        return None
    out, cur = [], goal
    while cur is not None:
        out.append(cur)
        cur = prev[cur]
    return out[::-1]


def _walk(run, path):
    for a, b in zip(path, path[1:], strict=False):
        run.apply(Move(_CARD[Point(b.x - a.x, b.y - a.y)]))


def _approach_ada(run):
    """Walk from the start to a floor tile next to the keeper, then face her."""
    keeper = run.gates["phishing"].keeper.pos
    blocked = set(run.keepers)
    targets = [
        Point(keeper.x + dx, keeper.y + dy)
        for dx in (-1, 0, 1)
        for dy in (-1, 0, 1)
        if (dx or dy) and run.chapter.grid.walkable(keeper.x + dx, keeper.y + dy)
        and Point(keeper.x + dx, keeper.y + dy) not in blocked
    ]
    best = None
    for t in targets:
        p = _path(run.chapter.grid, run.player.pos, t, blocked)
        if p and (best is None or len(p) < len(best)):
            best = p
    assert best is not None, "cannot reach Ada"
    _walk(run, best)


def _correct_index(gate):
    q = gate.current_question()
    correct = q.options[q.answer_index].text
    return gate.display_options().index(correct)


def _wrong_index(gate):
    q = gate.current_question()
    wrong = next(i for i, o in enumerate(q.options) if not o.correct)
    return gate.display_options().index(q.options[wrong].text)


def _sit_exam(run, pick):
    """From an open lesson panel: begin the exam and answer each question via `pick(gate)`."""
    frame = run.apply(Confirm(True))          # finish reading -> examination
    while isinstance(frame.overlay, (MenuView, PromptView)):
        frame = run.apply(Answer(pick(run.active)))   # -> explanation
        assert isinstance(frame.overlay, TextView)
        frame = run.apply(Confirm(True))              # -> next question, or finish
    return frame


# -- the slice ------------------------------------------------------------------------------


def test_walk_read_examine_and_the_door_appears():
    run = new_run(seed=99, cols=100, rows=30, name="Ada")

    _approach_ada(run)
    frame = run.apply(Talk())
    assert isinstance(frame.overlay, TextView)
    assert frame.overlay.title == "🎣 Recognising a Phish"

    door = run.chapter.exits["phishing"]
    assert run.chapter.grid.at(door.x, door.y).kind is TileKind.SEALED

    frame = _sit_exam(run, _correct_index)

    # Passing changes exactly one tile: the sealed wall becomes a door (SCREENS 8.1).
    assert run.gates["phishing"].passed
    assert run.chapter.grid.at(door.x, door.y).kind is TileKind.DOOR
    assert frame.overlay is None
    assert frame.messages[-1].startswith("The wall grinds")
    assert frame.status.rooms_done == 1

    # And now the corridor to room 2 is walkable.
    room2 = run.chapter.rooms[1].center
    path = _path(run.chapter.grid, run.player.pos, room2, blocked=set(run.keepers))
    assert path is not None, "the earned door did not open the way to room 2"
    _walk(run, path)
    assert run.player.pos == room2


def test_bumping_into_the_keeper_opens_the_conversation():
    # Walking into a keeper is NetHack's bump-to-act: it opens the lesson instead of the "you
    # can't go that way" a wall gives, and the player stays put (the keeper still blocks the tile).
    # Soloist so a roaming pet never drifts onto the deterministic path to the keeper.
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    keeper = run.gates["phishing"].keeper.pos
    blocked = set(run.keepers)
    ortho = [Point(keeper.x + dx, keeper.y + dy)
             for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
             if run.chapter.grid.walkable(keeper.x + dx, keeper.y + dy)
             and Point(keeper.x + dx, keeper.y + dy) not in blocked]
    best = None
    for t in ortho:
        p = _path(run.chapter.grid, run.player.pos, t, blocked)
        if p and (best is None or len(p) < len(best)):
            best = p
    assert best is not None, "no orthogonal tile next to the keeper"
    _walk(run, best)

    stood, turns = run.player.pos, run.turn
    frame = run.apply(Move(_CARD[Point(keeper.x - stood.x, keeper.y - stood.y)]))

    assert run.player.pos == stood, "the player should not step onto the keeper"
    assert isinstance(frame.overlay, TextView), "bumping the keeper should open the lesson"
    assert run.active is run.gates["phishing"]
    assert run.turn == turns + 1, "a bump costs a turn like an attack"


def test_standing_on_a_stair_shows_the_stair_hint_even_beside_a_keeper():
    # A keeper almost always stands next to the stairs (the last one always does), and the tile
    # underfoot must win: standing on a down-stair, the hint names Descend, not Talk.
    run = new_run(seed=99, cols=100, rows=30)
    keeper = run.gates["phishing"].keeper.pos
    grid = run.chapter.grid
    spot = next(Point(keeper.x + dx, keeper.y + dy)
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                if grid.walkable(keeper.x + dx, keeper.y + dy)
                and Point(keeper.x + dx, keeper.y + dy) not in run.keepers)
    grid.at(spot.x, spot.y).kind = TileKind.STAIRS_DOWN
    run.player.pos = spot

    hint = run.frame().hint
    assert hint == run.strings("hint.descend")
    assert "Descend" in hint and "Talk" not in hint


def test_wrong_answers_do_not_open_the_door():
    run = new_run(seed=99, cols=100, rows=30)
    _approach_ada(run)
    run.apply(Talk())
    frame = _sit_exam(run, _wrong_index)

    assert not run.gates["phishing"].passed
    door = run.chapter.exits["phishing"]
    assert run.chapter.grid.at(door.x, door.y).kind is TileKind.SEALED
    assert frame.status.rooms_done == 0
    assert frame.messages[-1].startswith("Not yet")
    # One failed sitting costs one penalty at M4 (standard = 3), never per wrong answer, and the
    # door is still stone. The stakes proper live in test_stakes.py.
    assert run.player.hp == run.player.max_hp - DIFFICULTIES["standard"].penalty


def test_the_examination_is_a_real_sitting():
    run = new_run(seed=7, cols=100, rows=30)
    _approach_ada(run)
    frame = run.apply(Talk())
    frame = run.apply(Confirm(True))
    # First question is Ada's MCQ: a menu with four shuffled options and a progress footer.
    assert isinstance(frame.overlay, MenuView)
    assert len(frame.overlay.items) == 4
    assert frame.overlay.footer == "Question 1 of 4."
    # The menu never leaks which option is correct.
    assert all(isinstance(it.text, str) for it in frame.overlay.items)


def test_an_mcq_can_be_navigated_and_confirmed():
    from delve.session.commands import Select
    run = new_run(seed=7, cols=100, rows=30)
    _approach_ada(run)
    run.apply(Talk())
    frame = run.apply(Confirm(True))                  # the MCQ
    assert isinstance(frame.overlay, MenuView) and frame.overlay.selected == 0
    frame = run.apply(Select(1))
    assert frame.overlay.selected == 1                # the arrows move the focus
    correct = _correct_index(run.active)
    frame = run.apply(Select(correct - frame.overlay.selected))
    assert frame.overlay.selected == correct
    frame = run.apply(Confirm(True))                  # Enter answers the focused option
    assert frame.messages == ["Correct."]


def test_correct_and_wrong_answers_colour_the_message_and_it_clears():
    from delve.session.views import Colour
    run = new_run(seed=7, cols=100, rows=30)
    _approach_ada(run)
    run.apply(Talk())
    run.apply(Confirm(True))                             # into the exam, Q1

    frame = run.apply(Answer(_correct_index(run.active)))
    assert frame.messages == ["Correct."] and frame.message_bg is Colour.GREEN

    frame = run.apply(Confirm(True))                     # advance to the next question
    assert frame.messages == [""] and frame.message_bg is None   # the highlight does not linger

    frame = run.apply(Answer(_wrong_index(run.active)))
    assert frame.messages == ["Not quite."] and frame.message_bg is Colour.RED


def test_assertion_renders_as_a_two_way_prompt():
    run = new_run(seed=7, cols=100, rows=30)
    _approach_ada(run)
    run.apply(Talk())
    frame = run.apply(Confirm(True))         # Q1 (mcq)
    frame = run.apply(Answer(_correct_index(run.active)))
    frame = run.apply(Confirm(True))         # -> Q2, the True/False assertion
    assert isinstance(frame.overlay, PromptView)
    assert frame.overlay.choices == ["True", "False"]


def test_esc_abandons_a_sitting_without_passing():
    run = new_run(seed=99, cols=100, rows=30)
    _approach_ada(run)
    run.apply(Talk())
    run.apply(Confirm(True))                 # into the exam
    frame = run.apply(Dismiss())             # Esc out
    assert frame.overlay is None
    assert not run.gates["phishing"].passed
    # The room re-seals so it can be sat again from scratch.
    assert run.gates["phishing"].state.name == "SEALED"


def test_reread_after_passing_never_re_examines():
    run = new_run(seed=99, cols=100, rows=30)
    _approach_ada(run)
    run.apply(Talk())
    _sit_exam(run, _correct_index)
    assert run.gates["phishing"].passed

    # Talk again: the lesson opens, but proceeding past it closes the panel instead of
    # re-examining. Passing is final (CLAUDE.md rule 3).
    frame = run.apply(Talk())
    assert isinstance(frame.overlay, TextView)
    frame = run.apply(Confirm(True))
    assert frame.overlay is None
    assert run.gates["phishing"].passed


@pytest.mark.parametrize("seed", [1, 7, 42, 99, 2024])
def test_slice_completes_on_every_seed(seed):
    run = new_run(seed=seed, cols=100, rows=30)
    _approach_ada(run)
    run.apply(Talk())
    _sit_exam(run, _correct_index)
    assert run.gates["phishing"].passed
