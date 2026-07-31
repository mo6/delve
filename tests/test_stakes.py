"""M4: stakes and the companion, driven headlessly as Commands against `session`.

Two guardrails are load-bearing and both are asserted here. First, the unit of stakes is the
*sitting*: a failed room costs one penalty no matter how many answers were wrong, and the bleed
per room is capped below starting HP so REPELLED always lands before HP:0 (PLAN.md section 6,
SCREENS.md 8.10). Second, none of it is punishment: REPELLED keeps every earned door, HP:0
respawns at the entrance whole, and rest returns the HP a struggling floor drains.

The pet is the other half: it follows the learner and, consulted, rules out a wrong option at
the cost of that question's score, never the learner's health.
"""

from collections import deque

from delve.assess.examination import DIFFICULTIES, Examination, Stakes
from delve.content.pilot import PHISHING_ROOM
from delve.engine.entities import Pet
from delve.engine.world import Direction, Point, TileKind
from delve.session.commands import Answer, Confirm, Consult, Move, Rest, Talk
from delve.session.run import new_run
from delve.session.views import MenuView, PromptView, TextView

_CARD = {Point(0, -1): Direction.N, Point(0, 1): Direction.S,
         Point(1, 0): Direction.E, Point(-1, 0): Direction.W}


# -- driving the slice -------------------------------------------------------------------------


def _path(grid, start, goal, blocked):
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


def _approach(run):
    """Walk from the start to a tile beside Ada, so the next Talk opens her lesson."""
    keeper = run.gates["phishing"].keeper.pos
    blocked = set(run.keepers)
    targets = [Point(keeper.x + dx, keeper.y + dy)
               for dx in (-1, 0, 1) for dy in (-1, 0, 1)
               if (dx or dy) and run.chapter.grid.walkable(keeper.x + dx, keeper.y + dy)
               and Point(keeper.x + dx, keeper.y + dy) not in blocked]
    best = min((p for t in targets if (p := _path(run.chapter.grid, run.player.pos, t, blocked))),
               key=len)
    for a, b in zip(best, best[1:], strict=False):
        run.apply(Move(_CARD[Point(b.x - a.x, b.y - a.y)]))


def _correct(run) -> int:
    g = run.active
    q = g.current_question()
    return g.display_options().index(q.options[q.answer_index].text)


def _wrong(run) -> int:
    g = run.active
    q = g.current_question()
    wrong = next(o for o in q.options if not o.correct)
    return g.display_options().index(wrong.text)


def _sit(run, choose):
    """From an open lesson panel: begin the exam and answer each question via choose(run), which
    may itself consult the pet before returning the display index to answer."""
    frame = run.apply(Confirm(True))
    while isinstance(frame.overlay, (MenuView, PromptView)):
        frame = run.apply(Answer(choose(run)))    # choose() may consult before deciding
        frame = run.apply(Confirm(True))
    return frame


def _fail_sittings(run, n):
    """Talk, then fail the whole room, n times over. Returns the final frame."""
    frame = None
    for _ in range(n):
        run.apply(Talk())
        frame = _sit(run, _wrong)
    return frame


# -- the difficulty table ----------------------------------------------------------------------


def test_the_bleed_is_capped_below_starting_hp_so_repelled_lands_first():
    # penalty x attempts < 12 at every finite difficulty: REPELLED before HP:0 (SCREENS 8.10).
    for stakes in DIFFICULTIES.values():
        if stakes.attempts is not None:
            assert stakes.penalty * stakes.attempts < 12
    assert DIFFICULTIES["relaxed"].attempts is None and DIFFICULTIES["relaxed"].penalty == 0
    assert (DIFFICULTIES["standard"].penalty, DIFFICULTIES["standard"].attempts) == (3, 3)
    assert (DIFFICULTIES["strict"].penalty, DIFFICULTIES["strict"].attempts) == (5, 2)


def test_room_frontmatter_overrides_the_pack_difficulty():
    base = Stakes(attempts=3, penalty=3)
    assert base.resolve(None, None) == base
    assert base.resolve(5, None) == Stakes(attempts=5, penalty=3)
    assert base.resolve(None, 1) == Stakes(attempts=3, penalty=1)


# -- assisted scoring (the pet's price) --------------------------------------------------------


def test_an_assisted_question_never_counts_toward_the_score():
    exam = Examination(list(PHISHING_ROOM.questions), 0.75)
    for i in range(exam.total):
        if i < 2:
            exam.assist()                 # consult the first two
        exam.grade(exam.current().answer_index)   # then answer every question correctly
        exam.advance()
    assert exam.correct == 2              # the two assisted answers earned no credit
    assert not exam.passed()              # 2 of 4 is below pass, though all four were right


def test_a_repeat_consult_on_one_question_is_free():
    exam = Examination(list(PHISHING_ROOM.questions), 0.75)
    assert exam.assist() is True
    assert exam.assist() is False         # the gate counts a hint only on the first


def test_the_pet_rules_out_a_wrong_option():
    pet = Pet(pos=Point(0, 0))
    i = pet.hint_for(PHISHING_ROOM.questions[0])
    assert not PHISHING_ROOM.questions[0].options[i].correct


# -- a failed sitting costs one penalty --------------------------------------------------------


def test_one_failed_sitting_costs_one_penalty_not_one_per_wrong_answer():
    run = new_run(seed=99, cols=100, rows=30)          # standard: penalty 3
    _approach(run)
    _fail_sittings(run, 1)                              # every one of the four answers wrong
    assert run.player.hp == 12 - 3                      # charged once, not four times


def test_relaxed_never_costs_hp_and_never_repels():
    run = new_run(seed=99, cols=100, rows=30, difficulty="relaxed")
    _approach(run)
    frame = _fail_sittings(run, 4)
    assert run.player.hp == run.player.max_hp
    assert frame.overlay is None                        # closed to re-sit, never a REPELLED panel
    assert frame.messages[-1].startswith("Not yet")


# -- REPELLED ----------------------------------------------------------------------------------


def test_standard_repels_on_the_third_failed_sitting_at_hp_three():
    run = new_run(seed=99, cols=100, rows=30)
    _approach(run)
    frame = _fail_sittings(run, 3)
    assert isinstance(frame.overlay, TextView) and frame.overlay.title == "REPELLED"
    assert run.player.hp == 3                            # 12 - 3x3, still on your feet
    assert frame.status.rooms_done == 0                  # nothing earned was lost
    assert not run.gates["phishing"].passed
    assert run.chapter.grid.at(*run.chapter.exits["phishing"]).kind is TileKind.SEALED
    assert "pushed back" in frame.messages[-1]


def test_strict_repels_on_the_second_failed_sitting_at_hp_two():
    run = new_run(seed=99, cols=100, rows=30, difficulty="strict")   # penalty 5, attempts 2
    _approach(run)
    frame = _fail_sittings(run, 2)
    assert frame.overlay.title == "REPELLED"
    assert run.player.hp == 2


def test_repelled_resets_the_budget_and_the_room_stays_re_sittable():
    run = new_run(seed=99, cols=100, rows=30)
    _approach(run)
    _fail_sittings(run, 3)                               # -> REPELLED
    assert run.gates["phishing"].attempts_used == 0      # a fresh budget after a re-read
    frame = run.apply(Confirm(True))                     # dismiss the push-back panel
    assert frame.overlay is None
    frame = run.apply(Talk())                            # and the lesson opens again
    assert isinstance(frame.overlay, TextView)
    assert frame.overlay.title == "🎣 Recognising a Phish"


# -- HP:0 respawn (not death) ------------------------------------------------------------------


def test_accumulated_loss_respawns_at_the_entrance_whole():
    run = new_run(seed=99, cols=100, rows=30)
    start = run.chapter.start
    _approach(run)
    _fail_sittings(run, 3)                               # REPELLED at HP 3, budget reset
    run.apply(Confirm(True))                             # put the panel down
    frame = _fail_sittings(run, 1)                       # one more failed sitting: 3 -> 0
    assert run.player.hp == run.player.max_hp            # woke whole, not dead
    assert run.player.pos == start                       # back at the chapter entrance
    assert frame.overlay is None
    assert "entrance" in frame.messages[-1]


def test_respawn_keeps_every_earned_door_open():
    run = new_run(seed=99, cols=100, rows=30)
    _approach(run)
    run.apply(Talk())
    _sit(run, _correct)                                  # pass the room: the door is earned
    door = run.chapter.exits["phishing"]
    assert run.chapter.grid.at(*door).kind is TileKind.DOOR

    run._respawn()                                       # an HP:0 respawn from elsewhere
    assert run.chapter.grid.at(*door).kind is TileKind.DOOR    # still open
    assert run.gates["phishing"].passed
    assert run.player.pos == run.chapter.start
    assert run.player.hp == run.player.max_hp


# -- rest returns the HP a floor drains --------------------------------------------------------


def test_rest_heals_to_full():
    run = new_run(seed=99, cols=100, rows=30)
    _approach(run)
    _fail_sittings(run, 1)
    assert run.player.hp == 9
    frame = run.apply(Rest())
    assert run.player.hp == run.player.max_hp
    assert "rest" in frame.messages[-1].lower()


# -- the pet -----------------------------------------------------------------------------------


def test_the_pet_moves_for_itself_and_stays_near():
    run = new_run(seed=99, cols=100, rows=30)
    for d in (Direction.E, Direction.W, Direction.S, Direction.N):
        run.apply(Move(d))
    # It steps for itself now (PETS.md), not glued to the vacated tile: always on a walkable tile,
    # never on the player or a keeper, and on its loose leash it stays within a room of the player.
    assert run.pet.pos != run.player.pos
    assert run.pet.pos not in run.keepers
    assert run.chapter.grid.walkable(*run.pet.pos)
    assert max(abs(run.pet.pos.x - run.player.pos.x),
               abs(run.pet.pos.y - run.player.pos.y)) <= 8


def test_consulting_strikes_a_wrong_option_and_counts_a_hint():
    run = new_run(seed=7, cols=100, rows=30, pet_species="dog")   # a dog's consult always costs
    _approach(run)
    run.apply(Talk())
    run.apply(Confirm(True))              # into Q1, an MCQ
    frame = run.apply(Consult())
    struck = [it for it in frame.overlay.items if it.struck]
    assert len(struck) == 1
    correct = run.active.current_question()
    assert struck[0].text != correct.options[correct.answer_index].text   # never the answer
    assert run.gates["phishing"].hints_used == 1
    assert "no longer counts" in frame.messages[-1]

    frame = run.apply(Consult())          # asking twice about the same question is free
    assert run.gates["phishing"].hints_used == 1
    assert "already" in frame.messages[-1]


def test_consulting_costs_the_pass():
    run = new_run(seed=7, cols=100, rows=30, pet_species="dog")   # a dog's consult always costs
    _approach(run)
    run.apply(Talk())

    def choose(run):
        if run.active.progress()[0] <= 2:     # consult on the first two questions
            run.apply(Consult())
        return _correct(run)                   # then answer every question correctly

    _sit(run, choose)
    assert not run.gates["phishing"].passed   # two assisted answers dropped the score below pass
    assert run.gates["phishing"].hints_used == 2


def test_consulting_with_no_question_open_is_a_harmless_no_op():
    run = new_run(seed=99, cols=100, rows=30)
    frame = run.apply(Consult())
    assert frame.overlay is None
    assert "nothing here to ask" in frame.messages[-1]
