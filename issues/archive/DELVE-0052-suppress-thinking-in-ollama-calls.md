---
id: DELVE-0052
title: Suppress thinking traces on every Ollama chat call
status: implemented
area: [assess]
type: bug
epic:
effort: low
milestone:
version: 1.18.0
version_span:
created: 2026-07-29
updated: 2026-07-29
accepted_by: George Moses
accepted_at: 2026-07-29
commits: [7c8f02a]
related: [DELVE-0051]
supersedes: []
docs: []
changelog:
reason:
---

# Suppress thinking traces on every Ollama chat call

## Summary

`OllamaClient.chat` (`delve/assess/llm.py`) sends every grading request without disabling Ollama's
"thinking" mode. For a non-thinking model like the current default (`qwen2.5:3b`) this is a no-op,
but a thinking model spends its whole reasoning trace inside `DEFAULT_TIMEOUT` (60s) before
returning any usable content, so `chat` can time out and fall to the keyword floor even though the
model would have answered correctly given the time. Set `"think": false` unconditionally on the
request payload.

## Motivation / problem

Confirmed in a manual side-by-side (`poc/ambient-flavour/`, unrelated ambient-text spike, same
underlying `/api/chat` call shape): `qwen3.5:9b` timed out on essentially every call at a 120s
limit, spending the whole budget on its thinking trace before emitting any reply content. Passing
`"think": false` in the request payload fixed it there (the model then answered well within the
budget). `assess/llm.py:OllamaClient`, the seam the shipping grader actually uses, has the same gap
and the same fix applies: nothing here depends on thinking output, `LLMGrader` only reads
`message.content` as a JSON verdict, so a reasoning trace is pure overhead in both time and (should
a thinking model ever become the grader default, see [[DELVE-0051]]) reliability.

`"think": false` is ignored by models that don't support thinking (per Ollama's API), so this is
safe for the current default and any other non-thinking model; it only changes behaviour for a
thinking model, where it removes a real failure mode.

## MUST

1. `OllamaClient.chat`'s request payload MUST include `"think": false` unconditionally, alongside
   the existing `"format": "json"` and `"options": {"temperature": 0}`.
2. No other request behaviour changes: same endpoint, same timeout, same error handling.

## Design notes / links

Same fix already applied to the unrelated `poc/ambient-flavour/{ambient,story}.py` spike scripts
(commit 6d69ca9), which is what surfaced the problem. This issue is the shipping-engine equivalent;
`poc/` changes don't need an issue (throwaway spikes), `delve/assess/llm.py` does.

## Acceptance / verification

`./run-tests.sh` stays green (no test currently asserts the exact payload shape, so this is a
behavioural addition, not a test-breaking change).
