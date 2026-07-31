"""A sitting: the learner takes the whole room's questions in order and ends with a score.

The unit of stakes is the sitting, not the answer (CLAUDE.md rule 4): a single wrong answer
costs nothing here, it just earns its explanation. What a *failed* sitting costs, and how many
a learner gets, is a `Stakes` value resolved from the pack difficulty (M4). This object grades
and scores one sitting and knows nothing about doors or HP; the gate turns a score into a world
effect, and the session spends the HP.

Consulting the pet marks a question `assisted`: it still tells the learner right or wrong (the
explanation is the teaching), but an assisted question no longer counts toward the score. That
is the pet's price, paid in score rather than health (PLAN.md section 5).
"""

from __future__ import annotations

from dataclasses import dataclass

from delve.assess.grader import KeywordGrader, TextGrader, grader_for
from delve.assess.question import Question


@dataclass(frozen=True)
class Stakes:
    """What a failed sitting costs, and how many sittings the learner gets before REPELLED.

    `attempts is None` means unlimited (relaxed): a sitting can always be re-sat and the learner
    is never repelled. `penalty` is HP, charged once per failed sitting (never per wrong answer).
    """

    attempts: int | None
    penalty: int

    def resolve(self, room_attempts: int | None, room_penalty: int | None) -> Stakes:
        """Fold in a room's frontmatter overrides; None inherits the pack difficulty."""
        return Stakes(
            attempts=self.attempts if room_attempts is None else room_attempts,
            penalty=self.penalty if room_penalty is None else room_penalty,
        )


# Pack difficulty -> stakes. The total a room can bleed is `penalty * attempts` (9 at standard,
# 10 at strict), held below starting HP (12) on purpose, so REPELLED always lands before HP:0
# rather than after (PLAN.md section 6, SCREENS.md 8.10). relaxed can neither cost HP nor repel.
DIFFICULTIES: dict[str, Stakes] = {
    "relaxed": Stakes(attempts=None, penalty=0),
    "standard": Stakes(attempts=3, penalty=3),
    "strict": Stakes(attempts=2, penalty=5),
}


class Examination:
    def __init__(self, questions: list[Question], pass_mark: float,
                 text_grader: TextGrader | None = None):
        if not questions:
            raise ValueError("an examination needs at least one question")
        self.questions = questions
        self.pass_mark = pass_mark
        # The grader for free-text answers. Defaults to the deterministic keyword floor, so a run
        # with no model still grades and scores free text (PHASE2.md section 9); the session injects
        # an LLM-backed grader when one is present (Phase 2 step 2). MCQ/assertion never use it.
        self.text_grader = text_grader or KeywordGrader()
        self.idx = 0
        self.correct = 0
        self.assisted: set[int] = set()
        # A free consult (the cat's first per room, OBJECTS.md section 8) still shows the struck
        # option and is remembered here so a repeat is a no-op, but it is NOT in `assisted`, so the
        # question still counts toward the score.
        self.freebies: set[int] = set()

    def current(self) -> Question:
        return self.questions[self.idx]

    def grade(self, choice: int) -> bool:
        """Grade `choice` (an index into the current question's own option order) and record it.
        An assisted question still returns its verdict, so the learner sees the explanation, but
        it does not count toward the score: the pet's help is paid for in score (PLAN section 5)."""
        q = self.current()
        verdict = grader_for(q).grade(q, choice)
        if verdict and self.idx not in self.assisted:
            self.correct += 1
        return verdict

    def grade_text(self, answer: str) -> bool:
        """Grade a free-text `answer` against the current question's rubric and record it, in one
        call: the synchronous path for a direct caller (and the keyword floor). The session's async
        LLM path splits these, grading off-thread and calling `record_text` with the verdict."""
        return self.record_text(self.text_grader.grade_text(self.current(), answer).correct)

    def record_text(self, correct: bool) -> bool:
        """Record a free-text verdict already computed (by the session's grader, sync or async).
        Like `grade`, an assisted question still returns its verdict, so the learner sees the
        explanation, but it does not count toward the score (PLAN.md section 5). The verdict's
        confidence and source are the grader's affair; the sitting only needs the boolean."""
        if correct and self.idx not in self.assisted:
            self.correct += 1
        return correct

    def assist(self, free: bool = False) -> bool:
        """Mark the current question consulted. Returns True the first time (so the gate counts a
        hint), False on a repeat of the same question (which costs nothing more). `free` records it
        as a freebie (no score cost) instead of a paid assist; either way a repeat is a no-op."""
        if self.idx in self.assisted or self.idx in self.freebies:
            return False
        (self.freebies if free else self.assisted).add(self.idx)
        return True

    @property
    def assisted_now(self) -> bool:
        return self.idx in self.assisted or self.idx in self.freebies

    def advance(self) -> None:
        self.idx += 1

    @property
    def finished(self) -> bool:
        return self.idx >= len(self.questions)

    @property
    def total(self) -> int:
        return len(self.questions)

    def score(self) -> float:
        return self.correct / len(self.questions)

    def passed(self) -> bool:
        return self.score() >= self.pass_mark
