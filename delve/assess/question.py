"""A question and its options. Type is inferred, never declared (CLAUDE.md 'Question format'):
a `- ?answer:` reference set with no checkboxes is free text (Phase 2); otherwise exactly two
options is an assertion, three or more is multiple choice. Labels and reference answers are
content, so the engine has no opinion about language.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Option:
    text: str
    correct: bool


@dataclass(frozen=True)
class Question:
    prompt: str
    options: tuple[Option, ...] = ()
    explanation: str = ""
    # Free text (Phase 2, PHASE2.md section 4): `accept` is the reference answers, any of which is
    # fully correct (the first is canonical); `reject` is common wrong answers to fail explicitly.
    # Both feed the LLM prompt *and* the deterministic keyword fallback, so the two paths agree on
    # what "right" means. A question with a non-empty accept set is free text and has no options.
    accept: tuple[str, ...] = ()
    reject: tuple[str, ...] = ()

    @property
    def kind(self) -> str:
        if self.accept:
            return "freetext"
        return "assertion" if len(self.options) == 2 else "mcq"

    @property
    def answer_index(self) -> int:
        for i, opt in enumerate(self.options):
            if opt.correct:
                return i
        raise ValueError("question has no correct option")
