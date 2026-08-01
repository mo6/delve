"""DELVE-0018: spend gold to eliminate a wrong MCQ option, priced against the room reward.

Mirrors the pet-consult tests in test_stakes.py, but the coin is the price and the score is kept.
The acceptance criteria (pricing 33 then 50, cost invariant, affordability, presentation, scoring
vs pet, availability, determinism) are all driven headlessly as Commands against `session`.
"""

from dataclasses import replace

from test_freetext import _freetext_run, _walk_beside_keeper
from test_stakes import _approach, _correct, _sit

from delve.content.pilot import PHISHING_ROOM
from delve.session.commands import Answer, BuyRemoval, Confirm, Consult, Dismiss, Talk
from delve.session.run import new_run
from delve.session.views import FreeTextView, MenuView, PromptView
from delve.ui import keys


def _exam_run(*, reward: int = 100, gold: int = 200, seed: int = 7, pet_species: str = "none"):
    """The M2 phishing slice with an explicit room reward (new_run has no pack, so R would be 0)
    and enough gold to buy. pet_species=none so a dog never competes for floor coins."""
    run = new_run(seed=seed, cols=100, rows=30, pet_species=pet_species)
    gate = run.gates["phishing"]
    gate.content = replace(PHISHING_ROOM, reward=reward)
    run.player.gold = gold
    return run


def _open_mcq(run):
    """Walk to Ada, open the lesson, and enter the first (four-option) MCQ."""
    _approach(run)
    run.apply(Talk())
    frame = run.apply(Confirm(True))
    assert isinstance(frame.overlay, MenuView)
    assert len(frame.overlay.items) == 4
    return frame


# -- pricing (the worked four-option example) ----------------------------------------------------


def test_four_option_removal_charges_thirty_three_then_fifty():
    run = _exam_run(reward=100, gold=200)
    _open_mcq(run)
    assert run._removal_price(run.active) == 33

    frame = run.apply(BuyRemoval())
    assert run.player.gold == 200 - 33
    elim = [it for it in frame.overlay.items if it.eliminated]
    assert len(elim) == 1
    correct = run.active.current_question()
    assert elim[0].text != correct.options[correct.answer_index].text
    assert "falls away" in frame.messages[-1]
    assert run._removal_price(run.active) == 50

    frame = run.apply(BuyRemoval())
    assert run.player.gold == 200 - 33 - 50
    assert sum(1 for it in frame.overlay.items if it.eliminated) == 2
    assert run.active.standing_count() == 2
    assert run._removal_price(run.active) is None          # n == 2: no further buy

    gold_before = run.player.gold
    frame = run.apply(BuyRemoval())                        # refused at two options left
    assert run.player.gold == gold_before
    assert "nothing here to buy" in frame.messages[-1]


# -- cost invariant (addendum) -------------------------------------------------------------------


def test_any_helpline_path_costs_more_than_answering_straight():
    """For R=100, every available removal sequence on a 3/4/5-option question leaves a strictly
    lower player gain than answering unaided; two removals on four cost 83 (gain 17); three on
    five cost 108 (gain -8); a buy is refused on a 2-option assertion and at n==2."""
    # Pure arithmetic of the formula, independent of a live sitting.
    def spend(n_start: int, removals: int, R: int = 100) -> int:
        total, n = 0, n_start
        for _ in range(removals):
            assert n >= 3
            total += round(R / (n - 1))
            n -= 1
        return total

    assert spend(3, 1) == 50
    assert spend(4, 1) == 33
    assert spend(4, 2) == 83
    assert spend(5, 1) == 25
    assert spend(5, 2) == 58
    assert spend(5, 3) == 108

    for n_start, max_removals in ((3, 1), (4, 2), (5, 3)):
        for k in range(1, max_removals + 1):
            assert 100 - spend(n_start, k) < 100          # earn identical, spend positive

    assert 100 - 83 == 17
    assert 100 - 108 == -8

    # Live: assertion never offers a buy; two options remaining refuses.
    run = _exam_run()
    _approach(run)
    run.apply(Talk())
    run.apply(Confirm(True))
    # Skip Q1 (MCQ) with the correct answer to reach Q2 (assertion).
    run.apply(Answer(_correct(run)))
    frame = run.apply(Confirm(True))
    assert isinstance(frame.overlay, PromptView)
    assert run._removal_price(run.active) is None
    gold = run.player.gold
    frame = run.apply(BuyRemoval())
    assert run.player.gold == gold
    assert "nothing here to buy" in frame.messages[-1]


# -- affordability -------------------------------------------------------------------------------


def test_insufficient_gold_refuses_and_spends_nothing():
    run = _exam_run(reward=100, gold=10)                   # price is 33
    _open_mcq(run)
    frame = run.apply(BuyRemoval())
    assert run.player.gold == 10
    assert not any(it.eliminated for it in frame.overlay.items)
    assert "haven't enough gold" in frame.messages[-1]
    assert "33 coins" in frame.messages[-1]


# -- presentation / selection --------------------------------------------------------------------


def test_eliminated_option_is_marked_and_cannot_be_selected():
    run = _exam_run()
    frame = _open_mcq(run)
    run.apply(BuyRemoval())
    gate = run.active
    elim_idx = next(i for i in range(4) if i in gate.eliminated)
    # Digit key for an eliminated option produces no Answer.
    assert keys.panel_command(ord(str(elim_idx + 1)), run._overlay) is None
    # Answering that index is a no-op: still on the question, gold unchanged by the attempt.
    gold = run.player.gold
    frame = run.apply(Answer(elim_idx))
    assert isinstance(frame.overlay, MenuView)
    assert run.player.gold == gold
    # A still-standing option answers and maps to the right grading path.
    standing = next(i for i in range(4) if i not in gate.eliminated)
    q = gate.current_question()
    correct_text = q.options[q.answer_index].text
    if gate.display_options()[standing] == correct_text:
        frame = run.apply(Answer(standing))
        assert "Correct" in frame.messages[-1]
    else:
        # Pick the correct standing index explicitly.
        correct_display = gate.display_options().index(correct_text)
        assert correct_display not in gate.eliminated
        frame = run.apply(Answer(correct_display))
        assert "Correct" in frame.messages[-1]


# -- scoring: gold keeps marks; pet still forfeits -----------------------------------------------


def test_paid_removal_keeps_the_score_pet_consult_still_forfeits():
    # Untouched perfect sitting passes.
    clean = _exam_run(seed=7)
    _approach(clean)
    clean.apply(Talk())
    _sit(clean, _correct)
    assert clean.gates["phishing"].passed
    clean_score = clean.gates["phishing"].passed_score

    # One paid removal on Q1, then answer everything correctly: still passes at the same score.
    paid = _exam_run(seed=7)
    _approach(paid)
    paid.apply(Talk())

    def buy_then_correct(run):
        if run.active.progress()[0] == 1 and run.active.standing_count() == 4:
            run.apply(BuyRemoval())
        return _correct(run)

    _sit(paid, buy_then_correct)
    assert paid.gates["phishing"].passed
    assert paid.gates["phishing"].passed_score == clean_score
    assert paid.gates["phishing"].hints_used == 0          # eliminate never calls assist

    # Pet consult on the same question still forfeits that question's score.
    both = _exam_run(seed=7, pet_species="dog")
    _approach(both)
    both.apply(Talk())

    def buy_and_consult(run):
        if run.active.progress()[0] == 1:
            if run.active.standing_count() == 4:
                run.apply(BuyRemoval())
            if not run.active.assisted_here:
                run.apply(Consult())
        return _correct(run)

    _sit(both, buy_and_consult)
    # One assisted question of four drops below the 0.75 pass mark when only three credit.
    assert both.gates["phishing"].hints_used == 1
    assert both.gates["phishing"].passed_score < clean_score or not both.gates["phishing"].passed


# -- availability --------------------------------------------------------------------------------


def test_lifeline_absent_when_reward_is_zero():
    run = _exam_run(reward=0, gold=200)
    _open_mcq(run)
    assert run._removal_price(run.active) is None
    assert "Eliminate" not in run.frame().hint
    gold = run.player.gold
    frame = run.apply(BuyRemoval())
    assert run.player.gold == gold
    assert "nothing here to buy" in frame.messages[-1]


def test_lifeline_absent_on_unscored_tutorial_floor():
    # new_run's single chapter is scored; force the chapter unscored to mirror the tutorial.
    run = _exam_run(reward=100, gold=200)
    run.cur.scored = False
    _open_mcq(run)
    assert run._removal_price(run.active) is None
    gold = run.player.gold
    frame = run.apply(BuyRemoval())
    assert run.player.gold == gold
    assert "nothing here to buy" in frame.messages[-1]


def test_lifeline_absent_on_freetext_question():
    # A free-text question has no options to eliminate; the pet's hint gets the same shrug.
    run = _freetext_run()
    _walk_beside_keeper(run)
    run.apply(Talk())
    frame = run.apply(Confirm(True))
    assert isinstance(frame.overlay, FreeTextView)
    assert run._removal_price(run.active) is None
    gold = run.player.gold
    frame = run.apply(BuyRemoval())
    assert run.player.gold == gold
    assert "nothing here to buy" in frame.messages[-1]


# -- determinism / re-sit / no refund ------------------------------------------------------------


def test_same_command_stream_removes_the_same_option():
    def once():
        run = _exam_run(seed=11, gold=200)
        _open_mcq(run)
        run.apply(BuyRemoval())
        elim = [it.text for it in run._overlay.items if it.eliminated]
        return elim, run.player.gold

    a, b = once(), once()
    assert a == b


def test_resit_shows_all_options_again_and_spent_gold_is_not_refunded():
    run = _exam_run(gold=200)
    _open_mcq(run)
    run.apply(BuyRemoval())
    assert run.player.gold == 200 - 33
    # Abandon the sitting with Esc; gold stays spent, and a fresh sit shows every option.
    run.apply(Dismiss())
    assert run.player.gold == 167
    run.apply(Talk())
    frame = run.apply(Confirm(True))
    assert isinstance(frame.overlay, MenuView)
    assert not any(it.eliminated for it in frame.overlay.items)
    assert len(frame.overlay.items) == 4
