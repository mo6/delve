---
id: DELVE-0053
title: Stop discarding Ollama's timing and token fields on every grader chat call
status: implemented
area: [assess, docs]
type: story
epic: DELVE-0035
effort: medium
milestone:
version: 1.19.0
version_span:
created: 2026-07-29
updated: 2026-07-29
accepted_by: George Moses
accepted_at: 2026-07-29
commits: [4569757]
related: [DELVE-0040, DELVE-0054]
supersedes: []
docs: [docs/INFOSCREEN.md]
changelog: "1.19.0"
reason:
---

# Stop discarding Ollama's timing and token fields on every grader chat call

## Summary

`assess/llm.py:OllamaClient.chat` sends one request to Ollama's `/api/chat` and returns only `body["message"]["content"]`, throwing away everything else in the reply: `total_duration`, `load_duration`, `prompt_eval_count`, `eval_count`, and the phase-timing fields. This story keeps that data instead of discarding it, accumulated onto `LLMGrader` across a run's grade calls, so a later story can surface it on the Grader tab (DELVE-0035 §7) without redoing the client seam. It ships no UI; the Grader tab's `Live`/`Run` sub-tabs stay `item.tab_soon` after this lands, same as today.

## Motivation / problem

[docs/INFOSCREEN.md](../docs/INFOSCREEN.md) §7 sketches a Grader tab (model, warm/cold, this run's token and fallback counts, a latency sparkline) and names its one blocker explicitly: the metrics it would show do not exist anywhere yet, because `chat` throws them away at the point they are cheapest to keep. `delve doctor` never needed them (it only checks reachability and a canned warm-up grade), so nobody has had a reason to plumb them through until now. Capturing them where the HTTP call already happens is far cheaper than trying to reconstruct them later.

## Stories

### As a maintainer, I want `OllamaClient.chat` to return the reply's timing and token fields alongside its text, so that a caller can record them without a second request.

- Given a successful `/api/chat` response containing `message.content`, `total_duration`, `load_duration`, `prompt_eval_count`, and `eval_count`, when `chat` is called, then it returns a small typed result (e.g. `ChatReply(text, metrics)`) carrying the parsed text plus each of those fields (durations converted from Ollama's nanoseconds to milliseconds; a missing field lands as `None`, never `0`, so "unknown" is never confused with "instant" or "zero tokens").
- Given a response missing one or more of the optional fields (older Ollama versions, or a non-Ollama-compatible endpoint), when `chat` is called, then the call still succeeds and only the missing fields are `None`; only a missing/unparseable `message.content` (today's existing failure mode) raises `LLMUnavailable`.
- Given the existing callers of `chat` (`LLMGrader.grade_text`, `delve doctor`'s warm-up check), when this story lands, then both are updated for the new return shape; `chat`'s return type changes (no back-compat string alias), since every caller is internal to this repo and both are touched in this same story.

### As a maintainer, I want `LLMGrader` to accumulate this run's grading metrics, so that a later Grader-tab story can read a run-scoped summary without touching `assess/llm` again.

- Given `LLMGrader.grade_text` is called and the model call succeeds, when it records the result, then a `GraderMetrics` accumulator on the grader instance updates: total prompt/completion tokens summed, the last call's latency (`total_duration` ms) and a running max, whether the last call was cold (`load_duration` non-zero) or warm, and a count of verdicts sourced `"llm"` vs. `"keyword"` (the fallback already distinguishes these via `Verdict.source`).
- Given the model call raises `LLMUnavailable` (never reached the model), when the accumulator updates, then the keyword-fallback count increments and no token/latency numbers are recorded, since none exist for that call.
- Given the model call succeeds but its parsed confidence falls below the floor, when the grader falls back to `KeywordGrader`, then the keyword-fallback count increments, but the call's real token and latency numbers are still recorded (the model did answer; only its confidence, not its cost, is why the verdict is discarded).
- Given a fresh `LLMGrader` instance (one per run, built by `make_grader_runner`), when no grade has happened yet, then its `GraderMetrics` reads as the empty/offline state (`docs/INFOSCREEN.md` §7's "Keyword floor Â· model not configured" case for a Grader tab to render later), not a crash or `None` attribute access.
- Given `ThreadedGrader` wraps an `LLMGrader`, when a later caller wants this run's metrics, then they are reachable through the existing `self.grader` reference (`ThreadedGrader.grader.metrics`); no new method is added to `ThreadedGrader` or `InlineGrader` in this story.

## Non-goals

- No Grader tab UI, no `InfoView`/`Frame` change, no new `Strings` entries; this story is the `assess`/`session` plumbing only, per INFOSCREEN.md §7's own instruction to extend the seam before the chart. The Grader > Live and Grader > Run mock-ups in DELVE-0035 stay unbuilt.
- No change to grading behaviour: verdicts, the confidence floor, and the fallback rule are untouched; this story only records numbers alongside a decision already made.
- No new `delve doctor` diagnostics beyond keeping its existing warm-up check working against the new return shape.
- No persistence: metrics are in-memory, run-scoped, and reset when the process exits, matching INFOSCREEN.md §7's "run-scoped accumulator", not a new `progress/` table.
- No refresh/poll cost: nothing here adds a new HTTP call; the metrics are a side effect of calls `LLMGrader` already makes.

## Design notes / links

- [docs/INFOSCREEN.md](../docs/INFOSCREEN.md) §7 is the design note this story implements the first half of; its field table (`model`, `total_duration`, `load_duration`, `prompt_eval_count`, `eval_count`, phase-timing fields) is the exact set to keep.
- `delve/assess/llm.py:OllamaClient.chat` is the only place the HTTP body is parsed; keep the "the one core module that opens a socket" property from `CLAUDE.md`'s module list unchanged, and keep `assess` free of any `ui`/`session` import (rule 1).
- `delve/assess/grader.py:LLMGrader` and `delve/session/grading.py` (`ThreadedGrader`, `InlineGrader`, `make_grader_runner`) are the only other files expected to change; `ui` and `session/views.py` should need no edit for this story, since it ships no view-model field yet.
- Keep `Verdict.source` (`"llm"` / `"keyword"`) as the existing signal for which count to increment; do not add a second, parallel way to tell the two apart.

## Acceptance / verification

- `tests/test_llm_grader.py`'s `FakeClient` is updated to return a `ChatReply`-shaped result (with a way to set canned metrics per test), and existing verdict/floor/fallback tests keep passing against the new shape.
- A new test asserts `LLMGrader.grade_text` accumulates tokens and latency into `.metrics` on an LLM-sourced verdict, and increments the keyword-fallback counter (with no token/latency change) on a fallback verdict, across a short sequence of calls.
- A new test asserts a fresh `LLMGrader`'s `.metrics` reads as the empty/offline state before any call.
- `tests/test_doctor.py`'s warm-up check is updated for the new `chat` return shape and stays green.
- `./run-tests.sh` is green, including `ruff` and `pip-audit` (no new third-party dependency; the parsing stays stdlib `json`).
