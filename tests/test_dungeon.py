"""The full multi-chapter run, driven end to end as Commands against `session` with no terminal.

Load the real pilot pack, then walk every floor: read each keeper, sit the examination, watch
the last keeper of a chapter open the stairs, descend, and at the very bottom lift the scroll
from its pedestal. This is the M5 counterpart of the M2 slice test, and it is replayable for the
same reason: everything is a list of commands and assertions on frames.
"""

from collections import deque
from pathlib import Path

import pytest

from delve.content.parser import load_pack
from delve.engine import actions
from delve.engine.world import Direction, Point, TileKind
from delve.session.commands import Answer, AnswerText, Ascend, Confirm, Descend, Move, Talk
from delve.session.run import new_game, new_run
from delve.session.views import FreeTextView, MenuView, PromptView, TextView

PILOT = Path(__file__).resolve().parent.parent / "packs" / "security-onboarding"

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


def _approach(run, keeper_pos):
    blocked = set(run.keepers)
    targets = [
        Point(keeper_pos.x + dx, keeper_pos.y + dy)
        for dx in (-1, 0, 1) for dy in (-1, 0, 1)
        if (dx or dy) and run.chapter.grid.walkable(keeper_pos.x + dx, keeper_pos.y + dy)
        and Point(keeper_pos.x + dx, keeper_pos.y + dy) not in blocked
    ]
    best = None
    for t in targets:
        p = _path(run.chapter.grid, run.player.pos, t, blocked)
        if p and (best is None or len(p) < len(best)):
            best = p
    assert best is not None, f"cannot reach keeper at {keeper_pos}"
    _walk(run, best)


def _correct_index(gate):
    q = gate.current_question()
    return gate.display_options().index(q.options[q.answer_index].text)


def _pass_room(run, gate):
    _approach(run, gate.keeper.pos)
    frame = run.apply(Talk())
    assert isinstance(frame.overlay, TextView)
    frame = run.apply(Confirm(True))                     # finish reading -> examination
    while isinstance(frame.overlay, (MenuView, PromptView, FreeTextView)):
        if isinstance(frame.overlay, FreeTextView):
            # a free-text question: submit an accepted phrase, which the keyword floor passes
            run.apply(AnswerText(run.active.current_question().accept[0]))
        else:
            run.apply(Answer(_correct_index(run.active)))       # -> explanation
        frame = run.apply(Confirm(True))                        # -> next, or finish
    assert gate.passed, "answering everything correctly did not pass the room"
    return frame


def _clear_chapter(run):
    """Pass every room of the current chapter, in room order."""
    for gate in list(run.gates.values()):
        if not gate.passed:
            _pass_room(run, gate)


def _stand_on(run, kind):
    tile = next(p for p in _all_points(run.chapter.grid)
                if run.chapter.grid.at(p.x, p.y).kind is kind)
    path = _path(run.chapter.grid, run.player.pos, tile, blocked=set(run.keepers))
    assert path is not None, f"cannot reach {kind}"
    _walk(run, path)
    return tile


def _all_points(grid):
    return [Point(x, y) for y in range(grid.height) for x in range(grid.width)]


# -- the run --------------------------------------------------------------------------------


def test_full_pack_played_to_the_scroll():
    pack = load_pack(PILOT, "en")
    run = new_game(pack, seed=99, cols=100, rows=30, name="Ada")
    assert len(run.chapters) == len(pack.chapters) == 4

    for i in range(len(pack.chapters)):
        assert run.chapter.dlvl == i + 1
        _clear_chapter(run)
        if i < len(pack.chapters) - 1:
            # The last keeper opened the stairs down; descend to the next floor.
            _stand_on(run, TileKind.STAIRS_DOWN)
            frame = run.apply(Descend())
            assert run.idx == i + 1
            assert frame.status.dlvl == i + 2

    # The final chapter's last keeper revealed the pedestal; stepping onto it takes the scroll.
    pedestal = _stand_on(run, TileKind.PEDESTAL)  # walking onto it fires the award mid-path
    assert run.finished
    frame = run.frame()
    assert isinstance(frame.overlay, TextView)
    text = " ".join(b.text for b in frame.overlay.body)
    assert "Ada" in text
    assert pack.title in text
    assert "100.0%" in text                # every question answered correctly
    assert run.chapter.grid.at(pedestal.x, pedestal.y).kind is TileKind.PEDESTAL


def test_stairs_do_not_exist_until_the_last_keeper_is_passed():
    pack = load_pack(PILOT, "en")
    run = new_game(pack, seed=7, cols=100, rows=30)
    grid = run.chapter.grid
    assert not any(grid.at(p.x, p.y).kind is TileKind.STAIRS_DOWN for p in _all_points(grid))
    _clear_chapter(run)
    assert any(grid.at(p.x, p.y).kind is TileKind.STAIRS_DOWN for p in _all_points(grid))


def test_descend_then_ascend_returns_to_the_floor_above():
    pack = load_pack(PILOT, "en")
    run = new_game(pack, seed=3, cols=100, rows=30)
    _clear_chapter(run)
    _stand_on(run, TileKind.STAIRS_DOWN)
    run.apply(Descend())
    assert run.idx == 1
    # A '<' waits at the entrance; climbing it returns to Dlvl 1, doors still open.
    _stand_on(run, TileKind.STAIRS_UP)
    frame = run.apply(Ascend())
    assert run.idx == 0
    assert frame.status.dlvl == 1
    assert all(g.passed for g in run.gates.values())


def test_bumping_a_passed_keeper_is_a_brush_off_not_a_re_lesson():
    pack = load_pack(PILOT, "en")
    run = new_game(pack, seed=11, cols=100, rows=30)
    gate = next(iter(run.gates.values()))
    _pass_room(run, gate)
    # Standing beside the passed keeper, walk into them: no lesson reopens (that stays a `t`), just
    # a brush-off. `t` re-reading is covered by test_backtracking_never_re_examines.
    d = next(dd for dd in Direction
             if actions.step(run.chapter, run.player.pos, dd) == gate.keeper.pos)
    frame = run.apply(Move(d))
    assert frame.overlay is None
    assert run.player.pos != gate.keeper.pos            # the keeper still blocks the tile
    assert "turns back" in frame.messages[-1]           # the brush-off line, not the lesson


def test_the_message_line_ages_out():
    run = new_run(seed=99, cols=100, rows=30)
    run.messages.append("hello")
    run.turn = 5
    assert run.frame().messages == ["hello"]            # fresh: posted this turn
    run.turn = 6
    assert run.frame().messages == ["hello"]            # still within the two-turn window
    run.turn = 7
    assert run.frame().messages == []                   # aged out, so no stale news lingers
    run._overlay = object()
    run._overlay_kind = "lesson"                        # a keeper encounter freezes the clock
    assert run.frame().messages == ["hello"]            # so its own line stays up
    run._overlay_kind = "info"                          # but the backpack must not resurrect it
    assert run.frame().messages == []


def test_the_message_log_shows_recent_lines_and_closes():
    # Lives in the Info panel as its own tab, index 3 (a playtesting request; the standalone 'p'
    # shortcut is retired). Status moved to the last position at DELVE-0097's addendum, so
    # Messages sits one earlier than it used to.
    from delve.session.commands import Dismiss, Inventory, TabCycle
    from delve.session.views import InfoView
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    run.messages.extend(["first thing", "", "second thing", "first thing"])   # first repeats
    run.apply(Inventory())
    frame = run.apply(TabCycle(3))
    assert isinstance(frame.overlay, InfoView)
    assert frame.overlay.tabs[frame.overlay.active].key == "messages"
    # Condensed into one block (DELVE-0059 generalised): its own lines are its `spans`, each
    # prefixed with a literal "\n" but the first, so splitting on "\n" recovers each entry.
    lines = frame.overlay.body[0].text.split("\n")
    assert lines[0] == "1. first thing"                 # newest first, numbered
    assert lines[1] == "2. second thing"                # blanks skipped
    assert sum(t.endswith("first thing") for t in lines) == 1   # a repeat is listed only once
    assert run.apply(Dismiss()).overlay is None         # Esc puts the log away


def test_the_message_log_holds_ten_recent_lines_not_five():
    # A playtesting request (DELVE-0068): five felt cramped once Messages became its own Info tab.
    from delve.session.commands import Inventory, TabCycle
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    run.messages.extend(f"line {i}" for i in range(12))
    run.apply(Inventory())
    frame = run.apply(TabCycle(3))
    lines = frame.overlay.body[0].text.split("\n")
    assert len(lines) == 10
    assert lines[0] == "1. line 11"                     # newest first
    assert lines[-1] == "10. line 2"                    # capped at ten, not five


def test_keeper_ref_keeps_a_first_name_but_a_whole_title():
    from delve.session.run import _keeper_ref
    assert _keeper_ref("Ada the Suspicious") == "Ada"        # first name only
    assert _keeper_ref("Grigor, wiens naam geleend werd") == "Grigor"   # trailing comma dropped
    assert _keeper_ref("De Marskramer") == "De Marskramer"   # a role-title stays whole
    assert _keeper_ref("The Peddler") == "The Peddler"


def test_backtracking_never_re_examines():
    pack = load_pack(PILOT, "en")
    run = new_game(pack, seed=11, cols=100, rows=30)
    first = next(iter(run.gates.values()))
    _pass_room(run, first)
    # Talk again after passing: the lesson opens, proceeding closes it, no examination.
    _approach(run, first.keeper.pos)
    frame = run.apply(Talk())
    assert isinstance(frame.overlay, TextView)
    frame = run.apply(Confirm(True))
    assert frame.overlay is None
    assert first.passed


@pytest.mark.parametrize("seed", [1, 7, 42])
def test_every_seed_reaches_the_scroll(seed):
    pack = load_pack(PILOT, "en")
    run = new_game(pack, seed=seed, cols=100, rows=30)
    for i in range(len(pack.chapters)):
        _clear_chapter(run)
        if i < len(pack.chapters) - 1:
            _stand_on(run, TileKind.STAIRS_DOWN)
            run.apply(Descend())
    _stand_on(run, TileKind.PEDESTAL)
    assert run.finished
