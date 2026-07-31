"""Phase 2 step 1: free-text questions, the deterministic keyword grader, and the session flow,
with no model (PHASE2.md sections 4, 5.2, 9, 11). The format and the keyword floor are unit-level;
the answering loop is driven headless against `session` as a list of Commands, exactly like the
other slice tests, so a free-text room plays, scores and passes with no LLM present.

The LLM grader, its `assess.llm` seam and the non-blocking pending-grade state are Phase 2 step 2
and deliberately out of scope here; the grader injected in step 1 is the synchronous KeywordGrader.
"""

from collections import deque
from pathlib import Path

import pytest

from delve.assess.examination import Examination
from delve.assess.grader import KeywordGrader, Verdict
from delve.assess.question import Question
from delve.content.errors import PackError
from delve.content.markup import tokenize
from delve.content.parser import parse_room
from delve.content.schema import validate_pack
from delve.engine import layout
from delve.engine.entities import Player
from delve.engine.rng import Rng
from delve.engine.world import Direction, Point
from delve.gate import install_gates
from delve.session.commands import AnswerText, Backspace, Confirm, Move, Talk, Type
from delve.session.run import RunState
from delve.session.views import FreeTextView, TextView

FREETEXT_ROOM = (
    "---\n"
    "id: phishing\n"
    "keeper: wizard\n"
    "name: Ada\n"
    "pass: 1.0\n"
    "---\n"
    "# Phishing\n\n"
    "A message that hurries you is the thing to distrust.\n\n"
    "## Questions\n\n"
    "### In one word, name the feeling a phishing email manufactures to stop you thinking.\n\n"
    "- ?answer: urgency, time pressure, being rushed, panic\n"
    "- ?reject: fear of the boss, curiosity\n\n"
    "> Urgency is the lever. Thinking is what kills the attack.\n"
)


# -- the format: markup + parser -----------------------------------------------------------------


def test_answer_and_reject_lines_tokenize():
    tokens = tokenize("- ?answer: a, b\n- ?reject: c")
    kinds = [(t.kind, t.text) for t in tokens]
    assert ("freetext", "a, b") in kinds
    assert ("reject", "c") in kinds


def test_parse_builds_a_freetext_question():
    room = parse_room("r.md", FREETEXT_ROOM)
    q = room.questions[0]
    assert q.kind == "freetext"
    assert q.options == ()
    assert q.accept == ("urgency", "time pressure", "being rushed", "panic")
    assert q.reject == ("fear of the boss", "curiosity")
    assert "Urgency is the lever" in q.explanation


def test_reject_is_optional():
    text = FREETEXT_ROOM.replace("- ?reject: fear of the boss, curiosity\n", "")
    q = parse_room("r.md", text).questions[0]
    assert q.kind == "freetext" and q.reject == ()


def test_a_bare_answer_line_still_needs_an_explanation():
    text = FREETEXT_ROOM.replace("> Urgency is the lever. Thinking is what kills the attack.\n", "")
    with pytest.raises(PackError) as e:
        parse_room("r.md", text)
    assert "needs a '>' explanation" in str(e.value)


# -- the keyword grader (the deterministic floor, PHASE2.md section 5.2) --------------------------


def _q(accept, reject=()):
    return Question(prompt="?", explanation="e", accept=accept, reject=reject)


@pytest.mark.parametrize("answer, expected", [
    ("urgency", True),                                  # a listed synonym, verbatim
    ("URGENCY!!", True),                                # casing and punctuation are normalised away
    ("a sense of urgency, really", True),               # answer contains a reference phrase
    ("panic", True),                                    # answer inside a longer... here equal
    ("the blue colour of the header", False),           # nothing matches
    ("", False),                                        # empty answer short-circuits to reject
    ("   ", False),                                     # whitespace-only likewise
])
def test_keyword_grader_accept_and_miss(answer, expected):
    v = KeywordGrader().grade_text(_q(("urgency", "time pressure", "panic")), answer)
    assert isinstance(v, Verdict)
    assert v.correct is expected
    assert v.source == "keyword" and v.confidence == 1.0


def test_reject_beats_accept():
    # An answer that matches both a reject phrase and an accept phrase fails: reject wins.
    v = KeywordGrader().grade_text(_q(("urgency",), reject=("fear of the boss",)),
                                   "urgency, mostly fear of the boss")
    assert v.correct is False


def test_short_answer_inside_a_longer_target_counts():
    # "provenance" is inside the reference "its provenance and supply chain": accept it.
    v = KeywordGrader().grade_text(_q(("its provenance and supply chain",)), "provenance")
    assert v.correct is True


# -- the examination scores a free-text answer ---------------------------------------------------


def test_examination_grade_text_scores():
    exam = Examination([_q(("urgency",))], pass_mark=1.0)
    assert exam.grade_text("a real sense of urgency") is True
    assert exam.correct == 1
    exam2 = Examination([_q(("urgency",))], pass_mark=1.0)
    assert exam2.grade_text("the header colour") is False
    assert exam2.correct == 0


def test_examination_uses_an_injected_text_grader():
    class AlwaysYes:
        def grade_text(self, question, answer):
            return Verdict(True, 0.9, "fake")

    exam = Examination([_q(("nope",))], pass_mark=1.0, text_grader=AlwaysYes())
    assert exam.grade_text("anything at all") is True


# -- the gate seam: a free-text sitting passes ---------------------------------------------------


def test_gate_answer_text_passes_and_unlocks():
    chapter = layout.generate(1, 100, 30, 3, room_ids=["phishing", "b", "c"])
    room = parse_room("r.md", FREETEXT_ROOM)
    gate = install_gates(chapter, [room])["phishing"]
    gate.begin_exam(Rng(1))
    assert gate.current_question().kind == "freetext"
    # An answer the deterministic floor can reach ("panic" is a listed synonym); a looser paraphrase
    # like "it makes you feel rushed" is exactly the LLM-only case the keyword floor cannot catch.
    assert gate.answer_text("a real sense of panic") is True
    result = gate.proceed(Rng(1), chapter.grid)
    assert result.outcome == "passed"
    assert gate.passed


# -- the session flow, headless (no model, KeywordGrader) ----------------------------------------


def _freetext_run(seed=5, grader_runner=None):
    """A RunState on a generated chapter whose only gated room asks the free-text question. Built
    directly (like new_run) rather than from disk, and soloist (no pet) so nothing roams.
    `grader_runner` defaults to the inline keyword floor (Phase 2)."""
    chapter = layout.generate(seed, 100, 30, 3, room_ids=["phishing", "b", "c"])
    room = parse_room("r.md", FREETEXT_ROOM)
    gates = install_gates(chapter, [room])
    from delve.session.run import ChapterRun
    cr = ChapterRun(chapter=chapter, gates=gates, content_chapter_id="c")
    player = Player(pos=chapter.start, name="Ada")
    return RunState([cr], player, Rng(seed), pet_species="none", grader_runner=grader_runner)


_CARD = {Point(0, -1): Direction.N, Point(0, 1): Direction.S,
         Point(1, 0): Direction.E, Point(-1, 0): Direction.W}


def _walk_beside_keeper(run):
    grid = run.chapter.grid
    keeper = run.gates["phishing"].keeper.pos
    blocked = set(run.keepers)
    targets = [Point(keeper.x + dx, keeper.y + dy)
               for dx in (-1, 0, 1) for dy in (-1, 0, 1)
               if (dx or dy) and grid.walkable(keeper.x + dx, keeper.y + dy)
               and Point(keeper.x + dx, keeper.y + dy) not in blocked]
    # BFS to the nearest tile adjacent to the keeper, then walk it a step at a time.
    prev = {run.player.pos: None}
    q = deque([run.player.pos])
    goal = None
    while q:
        cur = q.popleft()
        if cur in targets:
            goal = cur
            break
        for d, direction in _CARD.items():
            nxt = Point(cur.x + d.x, cur.y + d.y)
            if nxt not in prev and nxt not in blocked and grid.walkable(nxt.x, nxt.y):
                prev[nxt] = (cur, direction)
                q.append(nxt)
    assert goal is not None, "no path to the keeper"
    steps = []
    cur = goal
    while prev[cur] is not None:
        cur, direction = prev[cur]
        steps.append(direction)
    for direction in reversed(steps):
        run.apply(Move(direction))


def test_a_freetext_room_shows_a_text_field_and_passes():
    run = _freetext_run()
    _walk_beside_keeper(run)
    frame = run.apply(Talk())
    assert isinstance(frame.overlay, TextView)             # the lesson
    frame = run.apply(Confirm(True))                       # lesson -> the free-text question
    assert isinstance(frame.overlay, FreeTextView)
    assert frame.overlay.typed == ""
    frame = run.apply(AnswerText("it makes you feel rushed and panicked"))
    assert isinstance(frame.overlay, TextView)             # the explanation
    assert frame.messages == ["Correct."]
    frame = run.apply(Confirm(True))                       # explanation -> passed (one question)
    assert run.gates["phishing"].passed


def test_typing_builds_the_buffer_and_enter_submits():
    run = _freetext_run()
    _walk_beside_keeper(run)
    run.apply(Talk())
    run.apply(Confirm(True))
    for ch in "urgency":
        frame = run.apply(Type(ch))
    assert isinstance(frame.overlay, FreeTextView)
    assert frame.overlay.typed == "urgency"
    frame = run.apply(Backspace())
    assert frame.overlay.typed == "urgenc"
    run.apply(Type("y"))
    frame = run.apply(Confirm(True))                       # Enter submits the buffer
    assert isinstance(frame.overlay, TextView)
    assert run.apply(Confirm(True)) is not None
    assert run.gates["phishing"].passed


def test_a_wrong_freetext_answer_does_not_pass():
    run = _freetext_run()
    _walk_beside_keeper(run)
    run.apply(Talk())
    run.apply(Confirm(True))
    frame = run.apply(AnswerText("the colour of the header"))
    assert frame.messages == ["Not quite."]
    run.apply(Confirm(True))                               # a missed single-question sitting
    assert not run.gates["phishing"].passed


# -- schema warns (but never blocks) on free text ------------------------------------------------


def test_validate_warns_when_a_pack_uses_free_text(tmp_path):
    _write_freetext_pack(tmp_path)
    issues = validate_pack(tmp_path)
    assert not [i for i in issues if i.level == "error"]   # nothing blocks
    warnings = [i for i in issues if i.level == "warning"]
    assert any("free-text" in i.message and "delve setup" in i.message for i in warnings)


def _write_freetext_pack(root: Path) -> None:
    en = root / "en"
    (en / "01-office").mkdir(parents=True)
    (en / "pack.md").write_text(
        "---\nid: p\ntitle: P\ndifficulty: standard\nscroll: A Scroll\n---\nIntro.\n",
        encoding="utf-8")
    (en / "01-office" / "chapter.md").write_text(
        "---\nid: office\ntitle: The Office\n---\nCh.\n", encoding="utf-8")
    (en / "01-office" / "01-phishing.md").write_text(FREETEXT_ROOM, encoding="utf-8")
