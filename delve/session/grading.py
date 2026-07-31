"""How a free-text grade is *run*: inline in the calling thread, or on a background worker.

The seam the pending-grade state hangs on (PHASE2.md section 5.3). The session talks to a runner
through `submit`/`poll`, so the two-step (show 'Checking...', then fold the verdict) has the same
shape whichever grader is behind it; only whether a verdict is ready *immediately* differs.

- `InlineGrader` grades in-line and hands the verdict straight back, so the two-step collapses to
  one: tests and the headless harness send `AnswerText` and see the explanation in the same
  `apply`. It wraps the deterministic `KeywordGrader` by default, so a run with no model still
  grades free text offline (PHASE2.md section 9).
- `ThreadedGrader` runs a *blocking* grader (the LLM, whose HTTP call is real latency) on a daemon
  thread, so `apply` returns at once with a 'grading' overlay and the session polls for the result.

The threading lives here, on the session side, not in `assess`: the grader itself
(`grade_text -> Verdict`) is pure and synchronous; running it off-thread is orchestration.
"""

from __future__ import annotations

import threading

from delve.assess.grader import KeywordGrader, TextGrader, Verdict
from delve.assess.question import Question


class InlineGrader:
    """Grade synchronously; `submit` returns the verdict now, `poll` never has anything pending."""

    def __init__(self, grader: TextGrader | None = None):
        self.grader = grader or KeywordGrader()

    def submit(self, question: Question, answer: str) -> Verdict | None:
        return self.grader.grade_text(question, answer)

    def poll(self) -> Verdict | None:
        return None

    def cancel(self) -> None:
        pass


class ThreadedGrader:
    """Run a blocking grader on a daemon thread so `apply` stays non-blocking (PHASE2.md section
    5.3). `submit` starts the worker and returns None (pending); `poll` returns the verdict once the
    worker has set it, None until then. One grade is in flight at a time (a new sitting question
    only opens after the current one's explanation), so one result slot suffices."""

    def __init__(self, grader: TextGrader):
        self.grader = grader
        self._result: Verdict | None = None
        self._thread: threading.Thread | None = None

    def submit(self, question: Question, answer: str) -> Verdict | None:
        self._result = None
        self._thread = threading.Thread(
            target=self._work, args=(question, answer), daemon=True)
        self._thread.start()
        return None

    def _work(self, question: Question, answer: str) -> None:
        # The grader itself catches an unreachable model and falls to the keyword floor, so the
        # worker always resolves to a verdict rather than dying (PHASE2.md section 8).
        self._result = self.grader.grade_text(question, answer)

    def poll(self) -> Verdict | None:
        return self._result

    def cancel(self) -> None:
        self._result = None
        self._thread = None


def make_grader_runner(model: str | None = None, host: str | None = None):
    """Build the free-text grader runner from config. No model -> the inline keyword floor (the
    default: offline, deterministic, no dependency). A model -> the LLM grader on a background
    thread, with the keyword floor beneath it (PHASE2.md section 5.2). The `assess.llm` import is
    deferred to here, so nothing loads the HTTP seam unless a model is actually asked for."""
    if not model:
        return InlineGrader()
    from delve.assess.grader import LLMGrader
    from delve.assess.llm import DEFAULT_HOST, OllamaClient
    client = OllamaClient(model=model, host=host or DEFAULT_HOST)
    return ThreadedGrader(LLMGrader(client))
